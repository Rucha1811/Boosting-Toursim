from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...services.ws import hub
from ..deps import authenticate_ws

router = APIRouter()

AUTHORITY_ROLES = ("authority_admin", "authority_officer")
BUSINESS_ROLES = ("business", "artisan")


@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    token = websocket.query_params.get("token")
    payload = await authenticate_ws(websocket) if token else None
    role = (payload or {}).get("role")

    valid = channel in ("public", "authority", "business")
    if not valid:
        await websocket.close(code=1008, reason="unknown channel")
        return

    # authority channel requires an authority role
    if channel == "authority" and role not in AUTHORITY_ROLES:
        await websocket.close(code=1008, reason="authority token required")
        return

    # business channel requires a business/artisan role
    if channel == "business" and role not in BUSINESS_ROLES:
        await websocket.close(code=1008, reason="business token required")
        return

    await hub.connect(channel, websocket)
    try:
        await websocket.send_text('{"event":"connected","data":{"channel":"%s"}}' % channel)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(channel, websocket)
    except Exception:
        hub.disconnect(channel, websocket)