import pytest

from src.resume_tailoring.gemini_content_generator import (
    GeminiResumeContentGenerator,
)
from src.resume_tailoring.generator_factory import (
    create_resume_content_generator,
)


class FakeGeminiClient:
    pass


def install_fake_gemini_client(monkeypatch):
    created_clients = []

    def fake_client(*, api_key):
        created_clients.append(api_key)
        return FakeGeminiClient()

    monkeypatch.setattr(
        "src.resume_tailoring.generator_factory.genai.Client",
        fake_client,
    )

    return created_clients


def test_factory_creates_gemini_generator(monkeypatch):
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    created_clients = install_fake_gemini_client(monkeypatch)

    generator = create_resume_content_generator(
        provider="gemini",
        model="test-model",
    )

    assert isinstance(
        generator,
        GeminiResumeContentGenerator,
    )
    assert generator._client.__class__ is FakeGeminiClient
    assert generator._model == "test-model"
    assert created_clients == ["test-api-key"]


def test_factory_uses_environment_configuration(monkeypatch):
    monkeypatch.setenv(
        "RESUME_CONTENT_PROVIDER",
        "gemini",
    )
    monkeypatch.setenv(
        "RESUME_CONTENT_MODEL",
        "environment-model",
    )
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-api-key",
    )

    created_clients = install_fake_gemini_client(monkeypatch)

    generator = create_resume_content_generator()

    assert isinstance(
        generator,
        GeminiResumeContentGenerator,
    )
    assert generator._model == "environment-model"
    assert created_clients == ["test-api-key"]


def test_factory_rejects_unsupported_provider():
    with pytest.raises(
        ValueError,
        match="Unsupported resume content provider: unknown",
    ):
        create_resume_content_generator(
            provider="unknown",
            model="test-model",
        )