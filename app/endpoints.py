from fastapi import APIRouter
from app.settings import config
from app.models import AddChannelBody


router = APIRouter()

@router.get("/health")
async def health():
    return {"ok": True}

@router.get("/channels")
async def get_channels():
    return {
        "channels": router.state.channels,
        "last_seen": router.state.last_seen,
        "serial_open": bool(router.state.serial and router.state.serial.is_open),
        "poll_seconds": config.OLL_SECONDS,
    }

@router.post("/channels")
async def add_channel(body: AddChannelBody):
    cid = body.channel_id.strip()
    if cid and cid not in router.state.channels:
        router.state.channels.append(cid)
        router.state.last_seen[cid] = None
    return {"channels": router.state.channels}