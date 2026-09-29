from typing import Protocol

from src.resume_tailoring.contracts import (
    StructuredResumeContent,
    TailoringInput,
)


class ResumeContentGenerator(Protocol):
    def generate(
        self,
        tailoring_input: TailoringInput,
    ) -> StructuredResumeContent:
        ...
