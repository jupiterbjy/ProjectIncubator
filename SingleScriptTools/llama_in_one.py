"""
A cross-platform script for the automatic llama 3 8B setup cpu-only, single user setup for my laziness.

This is intended to be used for Godot plugin.

Dependency installation:
```
py -m pip install psutil llama-cpp-python httpx --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```


:Author: jupiterbjy@gmail.com

: MIT License
:
: Copyright (c) 2024 jupiterbjy@gmail.com
:
: Permission is hereby granted, free of charge, to any person obtaining a copy
: of this software and associated documentation files (the "Software"), to deal
: in the Software without restriction, including without limitation the rights
: to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
: copies of the Software, and to permit persons to whom the Software is
: furnished to do so, subject to the following conditions:
:
: The above copyright notice and this permission notice shall be included in all
: copies or substantial portions of the Software.
:
: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
: IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
: FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
: AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
: LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
: OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
: SOFTWARE.
"""

import base64
import json
import pathlib
import logging
import argparse
import zlib
from typing import List, TypedDict, Tuple, Callable, Any
from collections.abc import Generator, Iterator
from urllib.parse import urlparse
from contextlib import contextmanager

import httpx
from llama_cpp import Llama, LlamaCache
from psutil import cpu_count


# --- DEFAULT CONFIG ---
# Change default config here.
# Some of these can be overridden by arguments.

MODEL_URL = r"""
https://huggingface.co/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF/resolve/main/Llama-3-8B-Instruct-32k-v0.1.Q6_K.gguf
""".strip()

# Initial prompt added to start of chat
DEFAULT_PROMPT = "You are an assistant who proficiently answers to questions."

# Subdirectory used for saving downloaded model files
LLM_SUBDIR = "_llm"

# Subdirectory used for saved sessions
SESSION_SUBDIR = "_session"

DEFAULT_TOKENS = 4096

DEFAULT_CONTEXT_LENGTH = 32000

DEFAULT_SEED = -1

DEFAULT_TEMPERATURE = 0.7

LLM_VERBOSE = False

SERVER_MODE = False

COMMAND_PREFIX = ":"
# STOP_AT = ["\n"]


# --- GLOBAL SETUP ---

MODEL_PATH = pathlib.Path(__file__).parent / LLM_SUBDIR
MODEL_PATH.mkdir(exist_ok=True)

SESSION_PATH = MODEL_PATH.parent / SESSION_SUBDIR
SESSION_PATH.mkdir(exist_ok=True)

THREAD_COUNT = cpu_count(logical=False)


# --- LOGGER CONFIG ---

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] <%(funcName)s> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


# --- UTILITIES ---


@contextmanager
def progress_manager(size: int):
    """Prints progress. Execute manager with incremental.
    Written to skip TQDM requirement."""

    digits = len(str(size))
    accumulated = 0

    def progress(amount):
        nonlocal accumulated
        accumulated += amount
        print(
            f"{int(100 * accumulated / size):>3}% | {accumulated:{digits}}/{size}",
            end="\r",
        )

    progress(0)

    try:
        yield progress
    finally:
        print()


class Message(TypedDict):
    role: str
    content: str


def extract_message(response: dict) -> Tuple[str, Message]:
    """Extracts message from output and returns (stop reason, message)"""

    return response["choices"][0]["finish_reason"], response["choices"][0]["message"]


class StreamWrap:
    """Makes return reason available"""

    def __init__(self, gen: Generator):
        self._gen = gen
        self.value = None

    def __iter__(self):
        self.value = yield from self._gen
        return self.value


# --- WRAPPER ---


class LLMWrapper:
    """Wraps Llama for easier access"""

    def __init__(
        self,
        model_url,
        seed=DEFAULT_SEED,
        context_length=DEFAULT_CONTEXT_LENGTH,
        *args,
        **kwargs,
    ):
        self.model_url = model_url

        file_name = pathlib.Path(urlparse(model_url).path).name
        self.model_path = MODEL_PATH / file_name
        self.model_name = self.model_path.stem

        self._ensure_downloaded()

        self.llm = Llama(
            self.model_path.as_posix(),
            seed=seed,
            n_ctx=context_length,
            verbose=LLM_VERBOSE,
            n_threads=THREAD_COUNT,
            *args,
            **kwargs,
        )

    def __str__(self):
        return f"LLMWrapper({self.model_name})"

    def _ensure_downloaded(self):
        """Make sure file exists, if not download from self.model_url.
        This is to strip huggingface module dependency."""

        # if exists then return, no hash check cause lazy
        if self.model_path.exists():
            LOGGER.info(f"Found model {self.model_name}")
            return

        LOGGER.info(f"Downloading from {self.model_url}")

        # write with different extension
        temp = self.model_path.with_suffix(".temp")

        with (
            httpx.stream("GET", self.model_url, follow_redirects=True) as stream,
            temp.open("wb") as fp,
        ):
            length = int(stream.headers["content-length"])

            with progress_manager(length) as progress:
                for data in stream.iter_bytes():
                    fp.write(data)
                    progress(len(data))

        # rename back, we succeeded.
        temp.rename(self.model_path)
        LOGGER.info("Download complete")

    def create_chat_completion(self, messages: List[dict], **kwargs) -> Iterator:
        """Creates chat completion. This just wraps the original function for type hinting."""

        return self.llm.create_chat_completion(messages, **kwargs)

    def create_chat_completion_stream(self, messages: List[dict], **kwargs):
        """Creates stream chat completion."""

        return self.llm.create_chat_completion(messages, **kwargs)

    def set_cache(self, cache: LlamaCache):
        """
        # Uses cache for faster digest by keeping the state
        # https://github.com/abetlen/llama-cpp-python/issues/44#issuecomment-1509882229
        """
        self.llm.set_cache(cache)


class ChatSession:
    """Represents single chat session"""

    def __init__(
        self,
        uuid: str,
        llm: LLMWrapper,
        init_prompt="",
        output_json=False,
        max_tokens=DEFAULT_TOKENS,
        enable_cache=True,
    ):
        self.uuid = uuid
        self.llm = llm

        self.preprocessor = lambda x: x
        prompt = f"{DEFAULT_PROMPT} {init_prompt}".strip()
        self.resp_format = None

        if output_json:
            self.preprocessor = json.loads
            prompt += " You outputs in JSON."
            self.resp_format = {"type": "json_object"}

        self.temperature = 0.7
        self.max_tokens = max_tokens

        self.messages: List[Message] = []
        self.system_send(prompt)

        self.cache = LlamaCache() if enable_cache else None

    def __str__(self):
        return f"ChatSession({self.uuid})"

    def serialize(self) -> bytes:
        """Serializes and compress session into plain text"""

        raw = json.dumps(
            {
                "uuid": self.uuid,
                "messages": json.dumps(self.messages),
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "resp_format": self.resp_format,
                "enable_cache": self.cache is not None,
                "output_json": self.preprocessor == json.loads,
            }
        )
        # https://stackoverflow.com/a/4845324/10909029
        compressed = zlib.compress(raw.encode("utf8"))
        return compressed

    @classmethod
    def deserialize(cls, compressed: bytes, llm: LLMWrapper):
        """Deserializes session"""

        serialized = zlib.decompress(base64.b64decode(compressed))

        data = json.loads(serialized)

        session = cls(
            llm,
            data["uuid"],
            "",
            data["output_json"],
            data["max_tokens"],
            data["enable_cache"],
        )
        session.messages = json.loads(data["messages"])
        session.temperature = data["temperature"]
        session.max_tokens = data["max_tokens"]
        session.resp_format = data["resp_format"]

        return session

    def save_session(self):
        """Saves session in SESSION_SUBDIR."""

        with open(SESSION_PATH / f"{self.uuid}", "wb") as fp:
            fp.write(self.serialize())

    @classmethod
    def load_session(cls, uuid: str, llm: LLMWrapper) -> "ChatSession":
        """Opens session from SESSION_SUBDIR.

        Raises:
            FileNotFoundError: When session file for given UUID is missing.
        """

        with open(SESSION_PATH / f"{uuid}", "rb") as fp:
            return ChatSession.deserialize(fp.read(), llm)

    def clear(self, new_init_prompt):
        """Clears session history excluding first system prompt.
        Sets new first system prompt if provided."""

        first_msg = self.messages[0]
        self.messages.clear()

        if new_init_prompt is not None:
            first_msg["content"] = new_init_prompt

        self.messages.append(first_msg)

    def system_send(self, prompt: str):
        """Sends system prompt(system role message)."""

        self.messages.append(
            {
                "role": "system",
                "content": prompt,
            }
        )

    def get_reply_stream(self, content: str, role="user") -> Generator[str]:
        """get_reply with streaming. Does not support json output mode.
        Returns finish reason."""

        # append user message
        self.messages.append({"role": role, "content": content})

        # generate message and append back to message list
        output = self.llm.create_chat_completion_stream(
            messages=self.messages,
            temperature=self.temperature,
            response_format=self.resp_format,
            max_tokens=self.max_tokens,
            stream=True,
        )

        # type hint to satisfy linter
        current_role: str = ""
        current_role_output = ""
        finish_reason = "None"

        for chunk in output:
            delta = chunk["choices"][0]["delta"]

            # if there's finish reason update it.
            if chunk["choices"][0]["finish_reason"] is not None:
                finish_reason = chunk["choices"][0]["finish_reason"]

            if "role" in delta:
                current_role = delta["role"]

            elif "content" in delta:
                current_role_output += delta["content"]
                yield delta["content"]

        self.messages.append({"role": current_role, "content": current_role_output})
        return finish_reason

    def get_reply(self, content: str, role="user") -> Tuple[str, str | dict]:
        """Send message to llm and get reply iterator. Returns (stop reason, content).
        Can return dictionary if json output is enabled."""

        # append user message
        self.messages.append({"role": role, "content": content})

        # generate message and append back to message list
        reason, msg = self.llm.create_chat_completion(
            messages=self.messages,
            temperature=self.temperature,
            response_format=self.resp_format,
            max_tokens=self.max_tokens,
        )
        self.messages.append(msg)

        return reason, self.preprocessor(msg["content"])


# --- COMMANDS ---


class CommandMap:
    """Class that acts like a command map. Each method is single command in chat session.
    Commands can either return False to stop the session, or True to continue.

    Originally was `Dict[str, Callable[[ChatSession, Any], ...]]` like this:

    COMMAND_MAP: Dict[str, Callable[[ChatSession, Any], bool]] = {
        "exit": lambda _session, param: exit(),
        "clear": lambda _session, param: _session.clear(),
        "temp": lambda _session, param:
    }

    ... but changed to class to make type hint work and better readability.
    You can still add new methods to class in runtime anyway!

    Notes:
        This is to be instanced so new command can be added in runtime if needed.
    """

    def command(self, session: ChatSession, name: str, arg=None) -> bool:
        """Search command via getattr and executes it.

        Raises:
            NameError: When given command doesn't exist.
            ValueError: When given argument for command is invalid.

        Returns:
            True if chat should continue, else False.
        """

        try:
            func: Callable[[ChatSession, Any], bool] = getattr(self, name)
        except AttributeError as err:
            raise NameError("No such command exists.") from err

        return func(session, arg)

    @staticmethod
    def exit(_session, _) -> bool:
        """Exits the session."""
        print("Exiting!")
        return False

    @staticmethod
    def clear(session: ChatSession, new_init_prompt) -> bool:
        """Clears chat histories and set new initial prompt if any.
        Otherwise, will fall back to previous initial prompt."""

        session.clear(new_init_prompt)
        print("Session cleared.")
        return True

    @staticmethod
    def temperature(session: ChatSession, amount_str: str) -> bool:
        """Set model temperature to given value.

        Raises:
            ValueError: On invalid amount string
        """

        session.temperature = float(amount_str)
        print(f"Temperature set to {session.temperature}.")
        return True

    @staticmethod
    def system(session: ChatSession, prompt: str) -> bool:
        """Give system prompt (system role message) to llm."""

        session.system_send(prompt)
        print(f"System prompt sent.")
        return True

    @staticmethod
    def save(session: ChatSession, prompt: str) -> bool:
        """Save the chat session."""

        session.save_session()
        print(f"Session saved as '{session.uuid}'.")
        return True


# --- STANDALONE MODE RUNNER ---


class StandaloneMode:
    def __init__(self):
        self.llm = LLMWrapper(MODEL_URL)
        self.session: ChatSession | None = None

    def menu(self):
        """Show menu"""

        menus = ["Create new session", "Load session"]

        print("\n".join(f"{idx}. {line}" for idx, line in enumerate(menus, start=1)))

        while True:

            # validate choice
            try:
                choice = int(input(">> "))
                assert 0 < choice <= len(menus)

            except (ValueError, AssertionError):
                continue

            match choice:
                case 1:
                    self.session = ChatSession("not_set", self.llm)
                    return
                case 2:
                    # validate uuid
                    try:
                        self.session = ChatSession.load_session(
                            input("uuid >> "), self.llm
                        )
                    except FileNotFoundError:
                        continue

    def run(self):
        """Runs standalone mode"""

        self.menu()

        command_map = CommandMap()
        run = True

        while run:
            print("----------------------------")
            user_input = input("[You]\n>> ")

            print("\n----------------------------")
            if user_input.startswith(COMMAND_PREFIX):
                # it's some sort of command. cut at first whitespace if any.
                sections = user_input[1:].split(" ", maxsplit=1)

                try:
                    run = command_map.command(
                        self.session,
                        sections[0],
                        None if len(sections) == 1 else sections[1],
                    )
                except Exception as err:
                    print(err)

            else:
                print("[Bot]")
                gen = StreamWrap(self.session.get_reply_stream(user_input))

                # flush token by token, so it doesn't group up and print at once
                # people willingly wait some extra overhead to complete the sentence to see the progress
                for token in gen:
                    print(token, end="", flush=True)

                print(f"\n\n[Stop reason: {gen.value}]")


# --- MAIN ---

if __name__ == "__main__":
    _parser = argparse.ArgumentParser()
    _parser.add_argument(
        "-s",
        "--server-mode",
        action="store_true",
        default=SERVER_MODE,
    )
    _parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=LLM_VERBOSE,
    )

    _args = _parser.parse_args()
    LLM_VERBOSE = _args.verbose

    if _args.server_mode:
        # I think we could just use llama.cpp's own server mod...
        raise NotImplementedError("Server mode Not implemented yet")
    else:
        _runner = StandaloneMode()
        _runner.run()
