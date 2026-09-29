import os

from google import genai

from src.resume_tailoring.content_generator import ResumeContentGenerator
from src.resume_tailoring.gemini_content_generator import (
    GeminiResumeContentGenerator,
)


def create_resume_content_generator(
    *,
    provider: str | None = None,
    model: str | None = None,
) -> ResumeContentGenerator:
    selected_provider = provider or os.environ["RESUME_CONTENT_PROVIDER"]
    selected_model = model or os.environ["RESUME_CONTENT_MODEL"]

    if selected_provider == "gemini":
        api_key = os.environ["GEMINI_API_KEY"]

        client = genai.Client(
            api_key=api_key,
        )

        return GeminiResumeContentGenerator(
            client=client,
            model=selected_model,
        )

    raise ValueError(
        f"Unsupported resume content provider: {selected_provider}"
    )