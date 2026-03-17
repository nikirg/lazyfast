"""
BTC Price example.

Standalone:
    uv run --with uvicorn --with aiohttp -m examples.btc
    open http://localhost:8000/btc
"""

import asyncio

from fastapi import BackgroundTasks, Depends, FastAPI

from lazyfast import LazyFastRouter, BaseState, Component, tags
from example.apps.shared import common_head, render_nav


async def get_btc_price() -> float:
    import aiohttp  # lazy: installed via --with aiohttp

    url = "https://api.binance.com/api/v3/avgPrice"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"symbol": "BTCUSDT"}) as resp:
            data = await resp.json()
    return float(data["price"])


INTERVALS = [0.5, 1, 2, 5, 10]


class State(BaseState):
    btc_price: float | None = None
    interval: float = 1.0


router = LazyFastRouter(state_schema=State, loader_route_prefix="/__lf_btc__")


@router.component(id="btc_currency", reload_on=[State.btc_price])
class Currency(Component):
    async def view(self, state: State = Depends(State)):
        with tags.div(class_="box"):
            tags.h1(
                f"BTC: ${state.btc_price:,.2f}" if state.btc_price else "Loading…",
                class_="title is-2",
            )


@router.component(id="btc_controls", reload_on=[State.interval])
class Controls(Component):
    async def view(self, state: State = Depends(State)):
        with tags.div(class_="box"):
            tags.p("Update interval (sec):", class_="label")
            with tags.div(class_="buttons"):
                for value in INTERVALS:
                    is_active = state.interval == value
                    cls = "button is-small is-info" + ("" if is_active else " is-light")
                    btn = tags.button(str(value), id=f"btc_iv_{value}", class_=cls)
                    if btn.trigger:
                        async with state:
                            state.interval = value


@router.page("/btc", head_renderer=lambda: common_head("BTC Price"))
def page(
    background_tasks: BackgroundTasks,
    state: State = Depends(State),
):
    render_nav("/btc")
    with tags.div(class_="container mt-5"):
        Currency()
        Controls()

    async def price_monitoring():
        while state.is_connection_alive():
            try:
                price = await get_btc_price()
                async with state:
                    state.btc_price = price
                    interval = state.interval
                await asyncio.sleep(interval)
            except Exception:
                await asyncio.sleep(5)

    background_tasks.add_task(price_monitoring)


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
