"""In-process WebSocket broadcast hubs.

Events flow:  authority action -> hub.publish("public"/"authority"/"business", payload)
Every connected client on that channel receives real-time updates, which powers
the two-way data flow between authorities and the public app.
"""

import asyncio
import json
from typing import Any, Dict, List, Set

from fastapi import WebSocket


class Hub:
    def __init__(self) -> None:
        self.channels: Dict[str, Set[WebSocket]] = {
            "public": set(),
            "authority": set(),
            "business": set(),
        }

    async def connect(self, channel: str, ws: WebSocket) -> None:
        await ws.accept()
        self.channels.setdefault(channel, set()).add(ws)

    def disconnect(self, channel: str, ws: WebSocket) -> None:
        self.channels.setdefault(channel, set()).discard(ws)

    async def publish(self, channel: str, event: str, data: Any) -> None:
        message = json.dumps({"event": event, "data": data}, default=str)
        dead = []
        for ws in list(self.channels.get(channel, set())):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.channels[channel].discard(ws)

    async def publish_all(self, event: str, data: Any) -> None:
        for channel in self.channels:
            await self.publish(channel, event, data)


hub = Hub()


async def broadcast_public(event: str, data: Any) -> None:
    await hub.publish("public", event, data)


async def broadcast_authority(event: str, data: Any) -> None:
    await hub.publish("authority", event, data)


async def broadcast_business(event: str, data: Any) -> None:
    await hub.publish("business", event, data)


# A very lightweight event bus to wake the simulator tick.
_sim_event = asyncio.Event()


def wake_simulator() -> None:
    _sim_event.set()


async def wait_sim_tick() -> None:
    try:
        await asyncio.wait_for(_sim_event.wait(), timeout=2.0)
    except asyncio.TimeoutError:
        pass
    finally:
        _sim_event.clear()