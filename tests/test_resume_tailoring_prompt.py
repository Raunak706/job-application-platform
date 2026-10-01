from src.resume_tailoring.prompt import (
    PROMPT_VERSION,
    build_generation_instructions,
)


def test_prompt_version_is_v4():
    assert PROMPT_VERSION == "v4"


def test_prompt_defines_candidate_facts_as_only_factual_source():
    prompt = build_generation_instructions()

    assert "approved_candidate_facts" in prompt
    assert "ONLY factual source" in prompt


def test_prompt_defines_three_input_sections():
    prompt = build_generation_instructions()

    assert "job_context" in prompt
    assert "approved_candidate_facts" in prompt
    assert "composition_guidance" in prompt
    assert "three distinct sections" in prompt


def test_prompt_treats_job_context_as_context_not_evidence():
    prompt = build_generation_instructions()

    assert "job_context" in prompt
    assert "Never treat job_context as evidence" in prompt
    assert (
        "Never turn a job requirement into a candidate qualification"
        in prompt
    )


def test_prompt_treats_composition_guidance_as_instruction_not_evidence():
    prompt = build_generation_instructions()

    assert "composition_guidance" in prompt
    assert (
        "Never treat composition_guidance as evidence about the candidate"
        in prompt
    )
    assert "It is NOT evidence about the candidate" in prompt


def test_prompt_forbids_inventing_candidate_facts():
    prompt = build_generation_instructions()

    assert (
        "Do not invent skills, technologies, experience, projects, "
        "responsibilities,"
        in prompt
    )
    assert "achievements, metrics, outcomes" in prompt


def test_prompt_allows_faithful_semantic_abstraction():
    prompt = build_generation_instructions()

    assert "faithful semantic abstraction" in prompt
    assert "standard technical terminology" in prompt
    assert "directly supported by approved candidate facts" in prompt


def test_prompt_distinguishes_abstraction_from_extrapolation():
    prompt = build_generation_instructions()

    assert (
        "A faithful abstraction restates or generalizes supported facts"
        in prompt
    )
    assert (
        "It does not introduce a new tool, technique, metric, "
        "responsibility,"
        in prompt
    )
    assert "outcome, qualification, or accomplishment" in prompt


def test_prompt_allows_supported_relationship_wording():
    prompt = build_generation_instructions()

    assert "Whisper ASR" in prompt
    assert "speech recognition" in prompt
    assert "MarianMT" in prompt
    assert "machine translation" in prompt


def test_prompt_forbids_fabricated_metrics():
    prompt = build_generation_instructions()

    assert (
        "A factual bullet without a metric is better than an invented metric"
        in prompt
    )
    assert (
        "Do not force a result or metric when none is supplied"
        in prompt
    )


def test_prompt_preserves_upstream_selection_boundary():
    prompt = build_generation_instructions()

    assert "already selected" in prompt
    assert (
        "Do not add, replace, merge, omit, or invent experiences or projects"
        in prompt
    )
    assert "Do not perform a second independent selection process" in prompt


def test_prompt_requires_preserving_record_ids():
    prompt = build_generation_instructions()

    assert (
        "Preserve every supplied experience_id and project_id exactly"
        in prompt
    )
    assert "Every experience_id must be a supplied experience_id" in prompt
    assert "Every project_id must be a supplied project_id" in prompt


def test_prompt_requires_exact_composition_allocations():
    prompt = build_generation_instructions()

    assert (
        "Generate exactly target_bullets for every experience"
        in prompt
    )
    assert (
        "Generate exactly target_bullets for every project"
        in prompt
    )
    assert "Do not independently increase or decrease these counts" in prompt
    assert "Do not redistribute bullets between records" in prompt


def test_prompt_requires_at_least_two_bullets_for_selected_projects():
    prompt = build_generation_instructions()

    assert (
        "Every selected project will have a target of at least 2 bullets"
        in prompt
    )
    assert "Never collapse a selected project into a single bullet" in prompt
    assert "no selected project has fewer than 2 bullets" in prompt


def test_prompt_requires_natural_concise_resume_writing():
    prompt = build_generation_instructions()

    assert "strong human technical resume writer" in prompt
    assert "concise" in prompt
    assert "natural" in prompt
    assert "specific" in prompt
    assert "technically credible" in prompt
    assert "information-dense" in prompt


def test_prompt_discourages_generic_ai_style_language():
    prompt = build_generation_instructions()

    assert "results-driven" in prompt
    assert "highly motivated" in prompt
    assert "passionate about" in prompt
    assert "proven track record" in prompt
    assert "keyword-stuff" in prompt


def test_prompt_sets_bullet_density_guidance():
    prompt = build_generation_instructions()

    assert "15-30 words per bullet" in prompt
    assert "dense one-page technical resume" in prompt
    assert (
        "upstream composition guidance determines how much space"
        in prompt
    )


def test_prompt_prevents_filler_for_allocated_bullets():
    prompt = build_generation_instructions()

    assert "If evidence is limited" in prompt
    assert "Never invent information merely" in prompt
    assert "to satisfy the requested count" in prompt
    assert "Avoid splitting one idea artificially" in prompt
    assert "Use distinct supported aspects" in prompt


def test_prompt_requires_exact_experience_allocation():
    prompt = build_generation_instructions()

    assert "For each supplied experience:" in prompt
    assert "generate exactly the allocated target_bullets" in prompt
    assert "keep each bullet distinct and useful" in prompt


def test_prompt_requires_exact_project_allocation():
    prompt = build_generation_instructions()

    assert "The supplied projects were already selected upstream" in prompt
    assert (
        "generate at least 2 bullets because selected projects must be "
        "meaningfully"
        in prompt
    )
    assert "generate exactly the allocated target_bullets" in prompt


def test_prompt_restricts_skills_to_approved_input():
    prompt = build_generation_instructions()

    assert "Return only supplied approved skills" in prompt
    assert "Do not derive new skills from job_context" in prompt
    assert "Every skill must be a supplied approved skill" in prompt


def test_prompt_keeps_professional_summary_compact():
    prompt = build_generation_instructions()

    assert "preferably 1-2 short sentences" in prompt
    assert "Do not write a generic objective statement" in prompt
    assert "Do not repeat the entire skills section" in prompt


def test_prompt_prioritizes_relevant_content_without_changing_selection():
    prompt = build_generation_instructions()

    assert "work directly related to the target role" in prompt
    assert "relevant approved technologies and skills" in prompt
    assert "controls emphasis and wording only" in prompt


def test_prompt_requires_information_compression():
    prompt = build_generation_instructions()

    assert "Compress overlapping information intelligently" in prompt
    assert (
        "Do not repeat the same skill across many bullets solely for "
        "keyword matching"
        in prompt
    )
    assert "weak filler and redundant content have been removed" in prompt


def test_prompt_forbids_document_format_generation():
    prompt = build_generation_instructions()

    assert "Do not generate LaTeX" in prompt
    assert "HTML" in prompt
    assert "Markdown" in prompt
    assert "complete resume document" in prompt


def test_prompt_requires_structured_resume_content_only():
    prompt = build_generation_instructions()

    assert "Return structured content containing only" in prompt
    assert "professional_summary" in prompt
    assert "experiences:" in prompt
    assert "experience_id" in prompt
    assert "projects:" in prompt
    assert "project_id" in prompt
    assert "skills" in prompt


def test_prompt_requires_non_empty_bullets():
    prompt = build_generation_instructions()

    assert "Every bullet must be a non-empty string" in prompt


def test_prompt_requires_all_selected_ids_exactly_once():
    prompt = build_generation_instructions()

    assert (
        "all supplied experience and project IDs are present exactly once"
        in prompt
    )


def test_prompt_defines_final_priority_rules():
    prompt = build_generation_instructions()

    assert "When accuracy conflicts with style, choose accuracy" in prompt
    assert (
        "When job alignment conflicts with candidate evidence, "
        "choose candidate evidence"
    ) in prompt
    assert (
        "When impressive wording conflicts with precise wording, "
        "choose precise wording"
    ) in prompt

def test_prompt_requires_bullets_in_descending_resume_value_order():
    prompt = build_generation_instructions()

    assert (
        "Order bullets from most job-relevant and important to least"
        in prompt
    )
    assert (
        "Later bullets should contain the most expendable supporting detail"
        in prompt
    )

def test_prompt_requires_job_specific_professional_summary():
    prompt = build_generation_instructions()

    assert (
        "Tailor the summary specifically to the target role described "
        "in job_context"
        in prompt
    )
    assert (
        "Use job_context to decide which approved candidate facts "
        "to emphasize"
        in prompt
    )
    assert (
        "Do not copy job requirements into the summary as candidate claims"
        in prompt
    )