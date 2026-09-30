from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    StructuredResumeContent,
)
from src.resume_tailoring.content_generator import ResumeContentGenerator


class FakeResumeContentGenerator:
    def generate(
        self,
        generation_input: ResumeGenerationInput,
    ) -> StructuredResumeContent:
        return StructuredResumeContent(
            professional_summary=None,
            experiences=(),
            projects=(),
            skills=(),
        )


def test_fake_generator_satisfies_provider_neutral_boundary():
    generator: ResumeContentGenerator = FakeResumeContentGenerator()

    assert isinstance(generator, FakeResumeContentGenerator)