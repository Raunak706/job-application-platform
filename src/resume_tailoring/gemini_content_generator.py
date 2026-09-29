import json
from typing import Any

from google.genai import types

from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
    TailoringInput,
)
from src.resume_tailoring.prompt import build_generation_instructions
from src.resume_tailoring.serialization import serialize_tailoring_input


_RESPONSE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "professional_summary": {
            "type": ["string", "null"],
        },
        "experiences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "experience_id": {
                        "type": "integer",
                    },
                    "bullets": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "experience_id",
                    "bullets",
                ],
                "additionalProperties": False,
            },
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                    },
                    "bullets": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "project_id",
                    "bullets",
                ],
                "additionalProperties": False,
            },
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "professional_summary",
        "experiences",
        "projects",
        "skills",
    ],
    "additionalProperties": False,
}


class GeminiResumeContentGenerator:
    def __init__(
        self,
        *,
        client: Any,
        model: str,
    ):
        self._client = client
        self._model = model

    def generate(
        self,
        tailoring_input: TailoringInput,
    ) -> StructuredResumeContent:
        response = self._client.models.generate_content(
            model=self._model,
            contents=json.dumps(
                serialize_tailoring_input(tailoring_input),
            ),
            config=types.GenerateContentConfig(
                system_instruction=build_generation_instructions(),
                response_mime_type="application/json",
                response_json_schema=_RESPONSE_JSON_SCHEMA,
            ),
        )

        return _parse_response(response.parsed)


def _parse_response(
    parsed: Any,
) -> StructuredResumeContent:
    if not isinstance(parsed, dict):
        raise ValueError(
            "Gemini returned malformed structured resume content."
        )

    try:
        return StructuredResumeContent(
            professional_summary=parsed["professional_summary"],
            experiences=tuple(
                GeneratedExperienceContent(
                    experience_id=item["experience_id"],
                    bullets=tuple(item["bullets"]),
                )
                for item in parsed["experiences"]
            ),
            projects=tuple(
                GeneratedProjectContent(
                    project_id=item["project_id"],
                    bullets=tuple(item["bullets"]),
                )
                for item in parsed["projects"]
            ),
            skills=tuple(parsed["skills"]),
        )
    except (KeyError, TypeError):
        raise ValueError(
            "Gemini returned malformed structured resume content."
        ) from None