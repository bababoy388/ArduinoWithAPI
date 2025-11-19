from unidecode import unidecode
import feedparser
from fastapi import FastAPI
import httpx
from app.settings import config
from typing import Dict, List, Optional
import asyncio
from contextlib import asynccontextmanager
import serial

def lcd_formatting(text: str, width: int = 16) -> str:
    if not text:
        text = ""

    text = text.replace("|", "/")
    text = unidecode(text)
    text = " ".join(text.split())

    return text[:width]

def build_msg(line1: str, line2: str) -> bytes:
    # Протокол: L|<line1>|<line2>\n
    l1 = lcd_formatting(line1)
    l2 = lcd_formatting(line2)

    return f"L|{l1}|{l2}\n".encode("utf-8")

def parse_latest(feed_text: str):
    feed = feedparser.parse(feed_text)

    if not feed.entries:
        return None
    e = feed.entries[0]

    title = e.get("title", "")

    video_id = e.get("yt_videoid")
    if not video_id:
        entry_id = e.get("id", "")
        if entry_id.startswith("yt:video:"):
            video_id = entry_id.split(":")[-1]

    link = e.get("link", "")

    channel_title = feed.feed.get("title", "")

    return {
        "video_id": video_id,
        "title": title,
        "link": link,
        "channel_title": channel_title,
    }

async def poller_worker(app: FastAPI):
    print("[Worker] started")
    while not app.state.stop.is_set():
        try:
            for cid in list(app.state.channels):
                url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
                try:
                    resp = await app.state.http.get(url)
                    if resp.status_code != 200:
                        print(f"[RSS] {cid} HTTP {resp.status_code}")
                        continue
                    latest = parse_latest(resp.text)
                    if not latest or not latest.get("video_id"):
                        continue
                    last = app.state.last_seen.get(cid)
                    if last != latest["video_id"]:
                        # обновление
                        app.state.last_seen[cid] = latest["video_id"]
                        # отправка на Arduino
                        line1 = latest.get("channel_title") or "New video"
                        line2 = latest.get("title") or "Untitled"
                        payload = build_msg(line1, line2)
                        if app.state.serial and app.state.serial.is_open:
                            try:
                                app.state.serial.write(payload)
                                app.state.serial.flush()
                                print(f"[Serial] Sent: {payload!r}")
                            except Exception as se:
                                print(f"[Serial] write error: {se}")
                        else:
                            print("[Serial] not open; msg skipped")
                except Exception as e:
                    print(f"[Worker] error for {cid}: {e}")
            # пауза
            await asyncio.wait_for(app.state.stop.wait(), timeout=config.POLL_SECONDS)
        except asyncio.TimeoutError:
            # нормальный цикл
            pass
        except Exception as e:
            print(f"[Worker] loop error: {e}")
    print("[Worker] stopped")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.serial = None
    try:
        app.state.serial = serial.Serial(config.SERIAL_PORT, config.BAUDRATE, timeout=1)
        print(f"[Serial] Opened {config.SERIAL_PORT} @ {config.BAUDRATE}")
    except Exception as e:
        print(f"[Serial] Failed to open {config.SERIAL_PORT}: {e}")

    app.state.http = httpx.AsyncClient(timeout=httpx.Timeout(10.0))
    app.state.last_seen: Dict[str, Optional[str]] = {cid: None for cid in config.CHANNEL_IDS}
    app.state.channels: List[str] = list(app.state.last_seen.keys())

    app.state.stop = asyncio.Event()
    app.state.worker_task = asyncio.create_task(poller_worker(app))

    yield

    # Shutdown
    app.state.stop.set()
    try:
        await app.state.worker_task
    except Exception:
        pass
    await app.state.http.aclose()
    if app.state.serial and app.state.serial.is_open:
        app.state.serial.close()
        print("[Serial] Closed")