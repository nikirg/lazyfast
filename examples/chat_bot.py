from typing import Any, Literal
import requests
from dataclasses import dataclass

from fastapi import FastAPI, Depends, Request
from renderable import RenderableRouter, tags, State as BaseState
from renderable.component import Component


STYLE = """
body { height: 100vh; }

.chat-container {
    height: 400px;
    overflow-y: auto;
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
}

.chat-message {
    padding: 15px;
    margin: 10px 0;
    word-wrap: break-word;
}
.chat-message.assistant {
    text-align: left;
}
.chat-message.user {
    border: 1px solid #ddd;
    border-radius: 10px;
    background-color: #f5f5f5;
    text-align: right;
}
"""


@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str


def get_chat_completion(api_key: str, messages: list[Message]) -> dict[str, Any] | None:
    msgs = [{"role": msg.role, "content": msg.content} for msg in messages]

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"model": "gpt-4o", "messages": msgs}

    response = requests.post(url, headers=headers, json=data)

    if response.ok:
        return response.json()

    print(response.text)


class State(BaseState):
    api_token: str | None = None
    messages: list[Message] = []


router = RenderableRouter(state_schema=State)


@router.component()
class ChatConfig(Component):
    async def view(self, state: State = Depends(State.load)):
        with tags.div(class_="box"):
            with tags.div(class_="field"):
                tags.label("OpenAI API token", class_="label", for_="api_token")
                api_token_inp = tags.input(
                    class_="input",
                    id="api_token",
                    name="api_token",
                    type_="text",
                )

                if not api_token_inp.value and not api_token_inp.trigger:
                    api_token_inp.value = state.api_token

        if api_token_inp.trigger:
            async with state:
                state.api_token = api_token_inp.value


@router.component(id="MessagesContainer", reload_on=[State.messages])
class ChatMessages(Component):
    async def view(self, state: State = Depends(State.load)):
        with tags.div(class_="chat-container", id="chat-container"):
            for message in state.messages:
                with tags.div(class_=f"chat-message {message.role}"):
                    tags.p(message.content)

        tags.script(
            'document.getElementById("chat-container").scrollTop = document.getElementById("chat-container").scrollHeight;'
        )


@router.component()
class ChatInput(Component):
    async def view(self, state: State = Depends(State.load)):
        with tags.div(class_="box"):
            with tags.div(class_="field"):
                inp = tags.input(
                    class_="input",
                    id="utterance",
                    name="utterance",
                    type_="text",
                    placeholder="Chat with me",
                )
                tags.span("Press Enter to send message", class_="help")

        if inp.value:
            async with state:
                state.messages.append(Message("user", inp.value))
                result = get_chat_completion(state.api_token, state.messages)
                ai_response = result["choices"][0]["message"]["content"]
                state.messages.append(Message("assistant", ai_response))
                inp.value = None


def extra_head():
    tags.title("Live Search")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )
    tags.style(STYLE)


@router.page("/", head=extra_head)
def root():
    with tags.div(class_="container hero is-fullheight p-6"):
        with tags.header():
            ChatConfig()

        with tags.div():
            ChatMessages()

        with tags.footer(class_="is-flex-align-items-flex-end mt-auto"):
            ChatInput()


app = FastAPI()
app.include_router(router)
