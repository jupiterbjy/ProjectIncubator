"""
A cross-platform script for the automatic llama 3 setup excluding 2 libraries - Because I'm lazy!

Dependency installation:
```
py -m pip install psutil llama-cpp-python httpx --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

WORK IN PROGRESS

:Author: jupiterbjy@gmail.com
"""

import json
import pathlib
import logging
import argparse
from typing import List, TypedDict, Tuple
from urllib.parse import urlparse
from contextlib import contextmanager

import httpx
from llama_cpp import Llama
from psutil import cpu_count

# --- CONFIG ---

MODEL_URL = """
https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q6_K.gguf
""".strip()

# Initial prompt added to start of chat
DEFAULT_PROMPT = "You are an assistant who proficiently answers to questions."

# Subdirectory used for saving downloaded model files
SUBDIR_PATH = "_llm"

DEFAULT_TOKENS = 512

DEFAULT_CONTEXT_LENGTH = 4096

DEFAULT_SEED = -1

DEFAULT_TEMPERATURE = 0.7

LLM_VERBOSE = True

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
            context_length=context_length,
            *args,
            **kwargs,
            verbose=LLM_VERBOSE,
            n_threads=THREAD_COUNT,
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


class ChatSession:
    """Represents single chat session"""

    def __init__(
        self,
        llm: LLMWrapper,
        uuid: str,
        init_prompt="",
        output_json=False,
        max_tokens=DEFAULT_TOKENS,
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


def main():
    """Some boilerplates setting up models and getting input"""

    llm = LLMWrapper(MODEL_URL)
    session = ChatSession(llm, "1")

    while True:
        print("----------------------------")
        prompt = input("You >>")

        # assume that if prompt is short, check if it's command.
        # TODO: replace with regex
        if len(prompt) < 10:
            match prompt:
                case "exit()":
                    break

                case "clear()":
                    session.clear()

                case str(x) if x.startswith("temp(") and x.endswith(")"):
                    try:
                        session.temperature = float(
                            x.removeprefix("temp(").removesuffix(")")
                        )
                    except ValueError:
                        pass
                    else:
                        LOGGER.info(f"Temp: {session.temperature}")

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
        "-v",
        "--verbose",
        type=bool,
        action="store_const",
        default=False,
    )

    main()
