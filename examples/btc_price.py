import asyncio, requests
from fastapi import BackgroundTasks, Depends, FastAPI
from lazyfast import LazyFastRouter, Component, tags, BaseState


def get_btc_price() -> float:
    url = "https://api.binance.com/api/v3/avgPrice"
    params = {"symbol": "BTCUSDT"}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data["price"])


class State(BaseState):
    btc_price: float | None = None


router = LazyFastRouter(state_schema=State)


@router.component(id="currency", reload_on=[State.btc_price])
class Currency(Component):
    async def view(self, state: State = Depends(State.load)):
        with tags.div(class_="box"):
            with tags.div(class_="content"):
                tags.h1(f"BTC: ${state.btc_price}")


def head_renderer():
    tags.title("Currency")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head_renderer=head_renderer)
def root(background_tasks: BackgroundTasks, state: State = Depends(State.load)):
    with tags.div(class_="container mt-6"):
        Currency()

    async def price_monitoring():
        while True:
            async with state:
                state.btc_price = get_btc_price()
            await asyncio.sleep(1)

    background_tasks.add_task(price_monitoring)


app = FastAPI()
app.include_router(router)
