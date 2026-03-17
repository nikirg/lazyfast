"""
Chat Bot example.

Standalone:
    uv run --with uvicorn --with openai --with markdown -m examples.chat
    open http://localhost:8000/chat
"""

from dataclasses import dataclass
from typing import Literal

from fastapi import BackgroundTasks, Depends, FastAPI

from lazyfast import LazyFastRouter, BaseState, Component, tags
from example.apps.shared import common_head, render_nav


CHAT_STYLE = """
.chat-wrap { display: flex; flex-direction: column; height: calc(100vh - 52px); }
.chat-messages { flex: 1; overflow-y: auto; padding: 1rem; }
.user-msg { text-align: right; margin: .4rem 0; }
.user-bubble { display: inline-block; background: #f5f5f5; border: 1px solid #ddd;
               border-radius: 10px; padding: .5rem 1rem; }
.assistant-msg { margin: .4rem 0; padding: .25rem 0; }
.dots::after { content: ''; animation: dots 1s steps(4,end) infinite; display: inline-block; }
@keyframes dots { 0%,100%{content:''} 25%{content:'.'} 50%{content:'..'} 75%{content:'...'} }
"""


@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str


async def get_chat_completion(api_key: str, messages: list[Message]) -> str | None:
    from openai import AsyncOpenAI  # lazy: installed via --with openai

    try:
        client = AsyncOpenAI(api_key=api_key)
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        resp = await client.chat.completions.create(model="gpt-4o", messages=msgs)
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[chat] {e}")


class State(BaseState):
    api_token: str | None = None
    messages: list[Message] = []
    is_awaiting_response: bool = False


router = LazyFastRouter(state_schema=State, loader_route_prefix="/__lf_chat__")


@router.component()
class ChatConfig(Component):
    async def view(self, state: State = Depends(State)):
        with tags.div(class_="box py-3"):
            with tags.div(class_="field"):
                tags.label("OpenAI API token", class_="label", for_="chat_api_token")
                token_inp = tags.input(
                    class_="input",
                    id="chat_api_token",
                    name="chat_api_token",
                    type_="text",
                    placeholder="sk-…",
                    reload_on=["change"],
                )
                if token_inp.trigger:
                    if token_inp.value:
                        async with state:
                            state.api_token = token_inp.value
                    else:
                        tags.p("Token cannot be empty", class_="help is-danger")

                if state.api_token:
                    tags.p("Token saved ✓", class_="help is-success")
                    token_inp.value = state.api_token
                    token_inp.type_ = "password"
                    token_inp.disabled = True
                else:
                    tags.p("Press Enter to save", class_="help")


@router.component(id="ChatMessages", reload_on=[State.messages])
class ChatMessages(Component):
    async def view(self, state: State = Depends(State)):
        import markdown as md  # lazy: installed via --with markdown

        for msg in state.messages:
            if msg.role == "user":
                with tags.div(class_="user-msg"):
                    tags.div(msg.content, class_="user-bubble")
            else:
                content = md.markdown(msg.content)
                tags.div(content, class_="assistant-msg", allow_unsafe_html=True)

        if state.is_awaiting_response:
            with tags.div(class_="has-text-grey"):
                tags.span("Thinking")
                tags.span(class_="dots")

        tags.script(
            'var m=document.getElementById("chat-messages");'
            'if(m) m.scrollTop=m.scrollHeight;'
        )


@router.component()
class ChatInput(Component):
    async def view(
        self,
        background_tasks: BackgroundTasks,
        state: State = Depends(State),
    ):
        with tags.div(class_="box py-3"):
            inp = tags.input(
                class_="input",
                id="chat_utterance",
                name="chat_utterance",
                type_="text",
                placeholder="Type a message and press Enter…",
            )
            tags.p("Press Enter to send", class_="help")

        if inp.value:
            async def _generate():
                async with state:
                    if state.api_token and (
                        reply := await get_chat_completion(state.api_token, state.messages)
                    ):
                        state.messages.append(Message("assistant", reply))
                    state.is_awaiting_response = False

            await state.open()
            state.messages.append(Message("user", inp.value))
            inp.value = None
            state.is_awaiting_response = True
            background_tasks.add_task(_generate)
            await state.commit()


def _head():
    common_head("Chat Bot")
    tags.style(CHAT_STYLE)


@router.page("/chat", head_renderer=_head)
def page():
    render_nav("/chat")
    with tags.div(class_="chat-wrap"):
        with tags.div(class_="px-4 pt-3"):
            ChatConfig()
        with tags.div(class_="chat-messages", id="chat-messages"):
            ChatMessages()
        with tags.div(class_="px-4 pb-3"):
            ChatInput()


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
