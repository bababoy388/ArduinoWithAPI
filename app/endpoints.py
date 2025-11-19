from fastapi import APIRouter, Request
from app.settings import config
from app.models import AddChannelBody

router = APIRouter()

@router.get("/health")
async def health():
    return {"ok": True}

@router.get("/channels")
async def get_channels(request: Request):
    state = request.app.state
    return {
        "channels": state.channels,
        "last_seen": state.last_seen,
        "serial_open": bool(state.serial and state.serial.is_open),
        "poll_seconds": config.POLL_SECONDS,
    }

@router.post("/channels")
async def add_channel(body: AddChannelBody, request: Request):
    state = request.app.state
    cid = body.channel_id.strip()
    if cid and cid not in state.channels:
        state.channels.append(cid)
        state.last_seen[cid] = None
    return {"channels": state.channels}
