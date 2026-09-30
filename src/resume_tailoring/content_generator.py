from typing import Protocol

from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    StructuredResumeContent,
)


class ResumeContentGenerator(Protocol):
    def generate(
        self,
        generation_input: ResumeGenerationInput,
    ) -> StructuredResumeContent:
        ...
        