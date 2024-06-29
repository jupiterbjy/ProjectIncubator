"""
A cross-platform script for the automatic llama 3B setup cpu-only, single user setup for my laziness.

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

import json
import pathlib
import logging
import argparse
from typing import List, TypedDict, Tuple
from urllib.parse import urlparse
from contextlib import contextmanager

import httpx
from llama_cpp import Llama, LlamaCache
from psutil import cpu_count


# --- DEFAULT CONFIG ---
# Change default config here.
# Some of these can be overridden by arguments.

MODEL_URL = """
https://huggingface.co/MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF/resolve/main/Llama-3-8B-Instruct-32k-v0.1.Q6_K.gguf
""".strip()

# Initial prompt added to start of chat
DEFAULT_PROMPT = "You are an assistant who proficiently answers to questions."

# Subdirectory used for saving downloaded model files
SUBDIR_PATH = "_llm"

DEFAULT_TOKENS = 4096

DEFAULT_CONTEXT_LENGTH = 32768

DEFAULT_SEED = -1

DEFAULT_TEMPERATURE = 0.7

LLM_VERBOSE = False

SERVER_MODE = False

# STOP_AT = ["\n"]


# --- GLOBAL SETUP ---

MODEL_PATH = pathlib.Path(__file__).parent / SUBDIR_PATH
MODEL_PATH.mkdir(exist_ok=True)
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

    def create_chat_completion(
        self, messages: List[dict], **kwargs
    ) -> Tuple[str, Message]:
        """Creates chat completion. This just wraps the original function for type hinting."""

        return extract_message(self.llm.create_chat_completion(messages, **kwargs))

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
        llm: LLMWrapper,
        uuid: str,
        init_prompt="",
        output_json=False,
        max_tokens=DEFAULT_TOKENS,
        enable_cache=True,
    ):
        self.uuid = uuid
        self.llm = llm

        self.preprocessor = lambda x: x
        self.prompt = f"{DEFAULT_PROMPT} {init_prompt}".strip()
        self.resp_format = None

        if output_json:
            self.preprocessor = json.loads
            self.prompt += " You outputs in JSON."
            self.resp_format = {"type": "json_object"}

        self.temperature = 0.7
        self.max_tokens = max_tokens

        self.messages: List[Message] = [
            {
                "role": "system",
                "content": self.prompt,
            }
        ]

        self.cache = LlamaCache() if enable_cache else None

    def __str__(self):
        return f"ChatSession({self.uuid})"

    def clear(self):
        """Clears session history excluding first system prompt."""

        first_msg = self.messages[0]
        self.messages.clear()
        self.messages.append(first_msg)

    def send(self, content: str, role="user") -> Tuple[str, str | dict]:
        """Send message to llm and get reply. Returns (stop reason, content)"""

        self.messages.append({"role": role, "content": content})

        # generate message and append back to message list
        reason, msg = self.llm.create_chat_completion(
            self.messages,
            temperature=self.temperature,
            response_format=self.resp_format,
            max_tokens=self.max_tokens,
        )
        self.messages.append(msg)

        return reason, self.preprocessor(msg["content"])


def standalone_mode():
    """Some boilerplates setting up models and getting input"""

    llm = LLMWrapper(MODEL_URL)
    session = ChatSession(llm, "1")
    llm.set_cache(session.cache)

    while True:
        print("----------------------------")
        prompt = input("You >> ")

        # assume that if prompt is short, check if it's command.
        # TODO: replace with regex
        if len(prompt) < 10:
            match prompt:
                case "exit()":
                    break

                case "clear()":
                    session.clear()
                    LOGGER.info(f"Session cleared")
                    continue

                case str(x) if x.startswith("temp(") and x.endswith(")"):
                    try:
                        session.temperature = float(x[len("temp(") : -len(")")])
                    except ValueError:
                        pass
                    else:
                        LOGGER.info(f"Temp: {session.temperature}")

                    continue

        if prompt == "exit()":
            LOGGER.info("Stopping")
            break

        print("----------------------------")

        reason, output = session.send(prompt)
        LOGGER.info(f"[Stop reason: {reason}]")

        print(f"Bot: {output}\n")


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
        standalone_mode()
