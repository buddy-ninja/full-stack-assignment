"""Checks that the starter pieces work. Keep or replace them."""

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai_service.knowledge import load_articles
from ai_service.llm import FakeLLMProvider, Message, ProviderUnavailableError
from ai_service.main import app

KNOWLEDGE = Path(__file__).resolve().parents[2] / "knowledge"


def test_knowledge_pack_loads():
    articles = load_articles(KNOWLEDGE)
    assert len(articles) == 20
    assert {a.id for a in articles} >= {"toxin-ingestion", "breathing-difficulty", "seizures"}


def test_fake_cites_tagged_sources_in_order():
    messages = [
        Message("system", "Context:\n[source:vomiting] ...\n[source:diarrhoea] ...\n[source:vomiting] again"),
        Message("user", "My dog threw up once"),
    ]
    answer = asyncio.run(FakeLLMProvider().complete(messages))
    assert "based on vomiting, diarrhoea," in answer


def test_fake_is_deterministic():
    messages = [Message("user", "Is my cat ok?")]
    fake = FakeLLMProvider()
    assert asyncio.run(fake.complete(messages)) == asyncio.run(fake.complete(messages))


def test_fake_error_switch():
    with pytest.raises(ProviderUnavailableError):
        asyncio.run(FakeLLMProvider().complete([Message("user", "hi [[fake:error]]")]))


def test_health(monkeypatch):
    monkeypatch.setenv("KNOWLEDGE_DIR", str(KNOWLEDGE))
    assert TestClient(app).get("/health").json() == {"status": "ok", "articles": 20}
