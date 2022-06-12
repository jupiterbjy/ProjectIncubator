"""
Nursery cancellation demo
"""
import itertools
from typing import Dict, Tuple

import trio
import fastapi
import hypercorn
from hypercorn.trio import serve


NURSERY = trio.open_nursery()
GLOBAL_NURSERY_STORAGE: Dict[str, Tuple[trio.CancelScope, trio.Event]] = {}
TIMEOUT = 5

router = fastapi.APIRouter()


@router.websocket('/stream')
async def run_task(websocket: fastapi.WebSocket):
    # accept and receive UUID
    # Replace UUID with anything client-specific
    await websocket.accept()
    uuid_ = await websocket.receive_text()

    print(f"[{uuid_}] CONNECTED")

    # check if nursery exist in session, if exists, cancel it and wait for it to end.
    if uuid_ in GLOBAL_NURSERY_STORAGE:
        print(f"[{uuid_}] STOPPING NURSERY")
        cancel_scope, event = GLOBAL_NURSERY_STORAGE[uuid_]
        cancel_scope.cancel()
        await event.wait()

    # create new event, and start new nursery.
    cancel_done_event = trio.Event()

    async with trio.open_nursery() as nursery:
        # save ref
        GLOBAL_NURSERY_STORAGE[uuid_] = nursery.cancel_scope, cancel_done_event

        try:
            for n in itertools.count(0, 1):
                nursery.start_soon(task, n, uuid_, websocket)
                await trio.sleep(1)

                # wait for client response
                with trio.fail_after(TIMEOUT):
                    recv = await websocket.receive_text()
                    print(f"[{uuid_}] RECEIVED {recv}")

        except trio.TooSlowError:
            # client possibly left without proper disconnection, due to network issue
            print(f"[{uuid_}] CLIENT TIMEOUT")

        except fastapi.websockets.WebSocketDisconnect:
            # client performed proper disconnection
            print(f"[{uuid_}] CLIENT DISCONNECTED")

    # fire event, and pop reference if any.
    cancel_done_event.set()
    GLOBAL_NURSERY_STORAGE.pop(uuid_, None)
    print(f"[{uuid_}] NURSERY STOPPED & REFERENCE DROPPED")


async def task(text, uuid_, websocket: fastapi.WebSocket):
    await websocket.send_text(str(text))
    print(f"[{uuid_}] SENT {text}")


if __name__ == '__main__':
    cornfig = hypercorn.Config()
    # cornfig.bind = "ws://127.0.0.1:8000"
    trio.run(serve, router, cornfig)
