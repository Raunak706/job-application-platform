from src.resume_tailoring.prompt import build_generation_instructions


def test_generation_instructions_enforce_candidate_fact_boundary():
    instructions = build_generation_instructions().casefold()

    assert "approved_candidate_facts" in instructions
    assert "job_context" in instructions

    assert (
        "only factual source for claims about the candidate"
        in instructions
    )
    assert (
        "do not infer candidate skills from the job description"
        in instructions
    )
    assert "do not invent metrics" in instructions


def test_generation_instructions_require_structured_output():
    instructions = build_generation_instructions().casefold()

    assert "professional_summary" in instructions
    assert "experience_id" in instructions
    assert "project_id" in instructions
    assert "skills" in instructions

    assert "do not generate latex" in instructions