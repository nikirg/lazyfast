import asyncio
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI()

html = """
<script src="https://unpkg.com/htmx.org"></script>
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>

<div hx-ext="sse" sse-connect="/event_stream">
    <div hx-get="/chatroom" hx-trigger="load, sse:chatter"></div>
</div>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    return html


@app.get("/event_stream", response_class=StreamingResponse)
async def stream(request: Request):
    async def event_stream():
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(1)
            yield "event: chatter\ndata: <none>\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/chatroom", response_class=HTMLResponse)
def chatroom(request: Request):
    return f"<span>{random.randint(0, 1000)}</span>"