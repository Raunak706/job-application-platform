from google.genai import errors

from src.resume_tailoring.contracts import (
    StructuredResumeContent,
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.gemini_content_generator import (
    GeminiResumeContentGenerator,
)


class FakeResponse:
    parsed = {
        "professional_summary": "Data engineer focused on reliable systems.",
        "experiences": [],
        "projects": [],
        "skills": [],
    }


class FakeModels:
    def __init__(self):
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def make_tailoring_input():
    return TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=100,
            title="Data Engineer",
            company="Example Employer",
            description="Build reliable Python data pipelines.",
            location="New York",
            country="US",
            workplace_type="hybrid",
            employment_type="full_time",
            department="Engineering",
        ),
        professional_headline="Data Engineer",
        professional_summary="Builds reliable data systems.",
        experiences=(),
        projects=(),
        skills=(),
        achievements=(),
    )


def test_gemini_generator_returns_structured_resume_content():
    client = FakeClient()
    generator = GeminiResumeContentGenerator(
        client=client,
        model="test-model",
    )

    result = generator.generate(make_tailoring_input())

    assert isinstance(result, StructuredResumeContent)
    assert result.professional_summary == (
        "Data engineer focused on reliable systems."
    )
    assert result.experiences == ()
    assert result.projects == ()
    assert result.skills == ()


def test_gemini_generator_uses_structured_json_output():
    client = FakeClient()
    generator = GeminiResumeContentGenerator(
        client=client,
        model="test-model",
    )

    generator.generate(make_tailoring_input())

    call = client.models.calls[0]

    assert call["model"] == "test-model"
    assert call["config"].response_mime_type == "application/json"
    assert call["config"].response_json_schema is not None


def test_gemini_generator_retries_503_then_succeeds():
    class RetryModels:
        def __init__(self):
            self.call_count = 0

        def generate_content(self, **kwargs):
            self.call_count += 1

            if self.call_count == 1:
                raise errors.ServerError(
                    503,
                    {"error": {"message": "Service unavailable"}},
                )

            return FakeResponse()

    class RetryClient:
        def __init__(self):
            self.models = RetryModels()

    sleep_calls = []

    generator = GeminiResumeContentGenerator(
        client=RetryClient(),
        model="test-model",
        sleep_fn=sleep_calls.append,
    )

    result = generator.generate(make_tailoring_input())

    assert isinstance(result, StructuredResumeContent)
    assert generator._client.models.call_count == 2
    assert sleep_calls == [1]


def test_gemini_generator_raises_after_repeated_503():
    class UnavailableModels:
        def __init__(self):
            self.call_count = 0

        def generate_content(self, **kwargs):
            self.call_count += 1
            raise errors.ServerError(
                503,
                {"error": {"message": "Service unavailable"}},
            )

    class UnavailableClient:
        def __init__(self):
            self.models = UnavailableModels()

    client = UnavailableClient()
    sleep_calls = []

    generator = GeminiResumeContentGenerator(
        client=client,
        model="test-model",
        sleep_fn=sleep_calls.append,
    )

    try:
        generator.generate(make_tailoring_input())
    except errors.ServerError as error:
        assert error.code == 503
    else:
        raise AssertionError(
            "Expected repeated Gemini 503 response to be raised."
        )

    assert client.models.call_count == 3
    assert sleep_calls == [1, 2]


def test_gemini_generator_rejects_malformed_response():
    class MalformedResponse:
        parsed = {
            "professional_summary": "Data engineer.",
            "experiences": [],
        }

    class MalformedModels:
        def generate_content(self, **kwargs):
            return MalformedResponse()

    class MalformedClient:
        def __init__(self):
            self.models = MalformedModels()

    generator = GeminiResumeContentGenerator(
        client=MalformedClient(),
        model="test-model",
    )

    try:
        generator.generate(make_tailoring_input())
    except ValueError as error:
        assert str(error) == (
            "Gemini returned malformed structured resume content."
        )
    else:
        raise AssertionError(
            "Expected malformed Gemini response to be rejected."
        )