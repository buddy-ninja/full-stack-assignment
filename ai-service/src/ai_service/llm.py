"""LLM provider interface and a deterministic fake for local work and tests.

The fake never calls a network. Its output depends only on its input, so tests
can assert on it. Control phrases in the last user message let you exercise
failure paths without mocking:

    [[fake:error]]    raise ProviderUnavailableError (as if the provider were down)
    [[fake:slow]]     wait FAKE_SLOW_SECONDS (default 12) before answering
    [[fake:refuse]]   return an answer that names a medication, so it should be flagged
"""

from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


class ProviderUnavailableError(RuntimeError):
    """The model provider could not be reached or returned a server error."""


class LLMProvider(Protocol):
    async def complete(self, messages: Sequence[Message]) -> str: ...

    def stream(self, messages: Sequence[Message]) -> AsyncIterator[str]: ...


_SOURCE_TAG = re.compile(r"\[source:([a-z0-9-]+)\]")


class FakeLLMProvider:
    """Builds a canned answer from the prompt.

    It cites every `[source:<article-id>]` tag it finds in the messages, in the
    order they first appear. Put those tags in your prompt next to each article
    you retrieved, and the fake will "use" them.
    """

    def __init__(self, chunk_delay_s: float = 0.0, slow_s: float | None = None) -> None:
        self.chunk_delay_s = chunk_delay_s
        self.slow_s = slow_s if slow_s is not None else float(os.getenv("FAKE_SLOW_SECONDS", "12"))

    async def complete(self, messages: Sequence[Message]) -> str:
        return "".join([chunk async for chunk in self.stream(messages)])

    async def stream(self, messages: Sequence[Message]) -> AsyncIterator[str]:
        question = next((m.content for m in reversed(messages) if m.role == "user"), "")
        if "[[fake:error]]" in question:
            raise ProviderUnavailableError("fake provider: simulated outage")
        if "[[fake:slow]]" in question:
            await asyncio.sleep(self.slow_s)

        answer = self._answer(messages, question)
        for word in answer.split(" "):
            if self.chunk_delay_s:
                await asyncio.sleep(self.chunk_delay_s)
            yield word + " "

    @staticmethod
    def _answer(messages: Sequence[Message], question: str) -> str:
        sources: list[str] = []
        for m in messages:
            for sid in _SOURCE_TAG.findall(m.content):
                if sid not in sources:
                    sources.append(sid)
        topic = question.replace("[[fake:refuse]]", "").strip()[:120] or "your question"
        parts = [f"(fake answer) About \"{topic}\":"]
        if sources:
            parts.append("based on " + ", ".join(sources) + ", keep an eye on your pet and contact a vet if things get worse.")
        else:
            parts.append("I could not find a relevant article, so please ask your vet.")
        if "[[fake:refuse]]" in question:
            parts.append("You could give half an ibuprofen tablet for the pain.")
        return " ".join(parts).strip()


def get_provider() -> LLMProvider:
    """Pick the provider from LLM_PROVIDER. Add real providers here."""
    name = os.getenv("LLM_PROVIDER", "fake")
    if name == "fake":
        return FakeLLMProvider(chunk_delay_s=float(os.getenv("FAKE_CHUNK_DELAY_SECONDS", "0.02")))
    raise ValueError(f"Unknown LLM_PROVIDER: {name!r}")
