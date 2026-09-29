from src.resume_tailoring.contracts import (
    StructuredResumeContent,
    TailoringInput,
)
from src.resume_tailoring.content_generator import ResumeContentGenerator


class FakeResumeContentGenerator:
    def generate(
        self,
        tailoring_input: TailoringInput,
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