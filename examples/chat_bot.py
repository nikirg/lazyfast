import aiohttp
from typing import Any, Literal
import markdown
from dataclasses import dataclass

from fastapi import BackgroundTasks, FastAPI, Depends
from lazyfast import LazyFastRouter, tags, BaseState, Component


STYLE = """
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
}

.key-input-container {
  padding: 10px;
}

.messages-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.message-input-container {
  padding: 10px;
}

.message-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.message {
  margin: 5px 0;
  padding: 15px;

}

.user-message {
    text-align: right;
    padding: 10px;
}

.user-content {
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    display: inline-block;
    border: 1px solid #ddd;
    background-color: #f5f5f5;
    float: right;   
}

.assistant-message {
  text-align: left;
  padding-left: 20px;
  padding-top: 25px;
}

.typing {
  display: inline-block;
}

.dots::after {
  content: '';
  display: inline-block;
  width: 1em;
  text-align: left;
  animation: dots 1s steps(4, end) infinite;
}

@keyframes dots {
  0%, 100% {
    content: '';
  }
  25% {
    content: '.';
  }
  50% {
    content: '..';
  }
  75% {
    content: '...';
  }
}

"""


@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str


async def get_chat_completion(
    api_key: str, messages: list[Message]
) -> dict[str, Any] | None:
    msgs = [{"role": msg.role, "content": msg.content} for msg in messages]

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"model": "gpt-4o", "messages": msgs}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(await response.text())


class State(BaseState):
    api_token: str | None = None
    messages: list[Message] = []
    is_awaiting_response: bool = False


router = LazyFastRouter(state_schema=State)


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
                    placeholder="Enter your OpenAI API token",
                    reload_on=["change"],
                )

                if api_token_inp.trigger:
                    if token := api_token_inp.value:
                        state.api_token = token
                    else:
                        tags.div("Token cannot be empty", class_="help is-danger")

                if state.api_token:
                    edit_btn = tags.span(
                        "Click to edit",
                        id="edit_api_token",
                        class_="help is-primary",
                        style="cursor: pointer;",
                        reload_on=["click"],
                    )

                    api_token_inp.value = state.api_token

                    if edit_btn.trigger:
                        state.api_token = None
                        await self.reload()

                    else:
                        api_token_inp.type_ = "password"
                        api_token_inp.disabled = True

                else:
                    tags.div("Press Enter to save", class_="help")


@router.component(id="MessagesContainer", reload_on=[State.messages])
class ChatMessages(Component):
    async def view(self, state: State = Depends(State.load)):
        for message in state.messages:
            with tags.div(class_=f"message {message.role}-message"):
                content = markdown.markdown(message.content)

                if message.role == "user":
                    with tags.p():
                        tags.div(content, class_="user-content", allow_unsafe_html=True)
                else:
                    tags.p(content, allow_unsafe_html=True)

            if state.is_awaiting_response:
                with tags.div(class_="typing"):
                    tags.span("Loading")
                    tags.span(class_="dots")

        tags.script(
            'document.getElementById("messages").scrollTop = document.getElementById("messages").scrollHeight;'
        )


@router.component()
class ChatInput(Component):
    async def view(
        self, background_tasks: BackgroundTasks, state: State = Depends(State.load)
    ):
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

            async def generate_response():
                async with state:
                    result = await get_chat_completion(state.api_token, state.messages)
                    ai_response = result["choices"][0]["message"]["content"]
                    state.messages.append(Message("assistant", ai_response))
                    state.is_awaiting_response = False

            state.open()

            state.messages.append(Message("user", inp.value))
            inp.value = None
            background_tasks.add_task(generate_response)
            state.is_awaiting_response = True

            await state.commit()


def head_renderer():
    tags.title("Chat Bot")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )
    tags.style(STYLE)


@router.page("/", head_renderer=head_renderer)
def root():
    with tags.div(class_="container "):
        with tags.div(class_="chat-container"):
            with tags.div(class_="key-input-container"):
                ChatConfig()

            with tags.div(class_="messages-container", id="messages"):
                ChatMessages()

            with tags.div(class_="message-input-container"):
                ChatInput()


app = FastAPI()
app.include_router(router)
