from src.resume_tailoring.prompt import (
    PROMPT_VERSION,
    build_generation_instructions,
)


def test_prompt_version_is_v6():
    assert PROMPT_VERSION == "v6"


def test_prompt_defines_candidate_facts_as_only_factual_source():
    prompt = build_generation_instructions()

    assert "approved_candidate_facts" in prompt
    assert "ONLY factual source" in prompt


def test_prompt_defines_three_input_sections():
    prompt = build_generation_instructions()

    assert "job_context" in prompt
    assert "approved_candidate_facts" in prompt
    assert "composition_guidance" in prompt
    assert "three sections" in prompt


def test_prompt_keeps_job_context_as_context_not_evidence():
    prompt = build_generation_instructions()

    assert (
        "Never use job_context or composition_guidance "
        "as candidate evidence"
        in prompt
    )
    assert (
        "Never turn a job requirement into a "
        "candidate qualification"
        in prompt
    )


def test_prompt_forbids_unsupported_candidate_claims():
    prompt = build_generation_instructions()

    assert "Never invent or infer unsupported:" in prompt
    assert "skills" in prompt
    assert "technologies" in prompt
    assert "achievements" in prompt
    assert "metrics" in prompt
    assert "outcomes" in prompt
    assert "business impact" in prompt
    assert "qualifications" in prompt


def test_prompt_prefers_omission_over_fabrication():
    prompt = build_generation_instructions()

    assert (
        "If information is missing, omit the unsupported claim"
        in prompt
    )
    assert (
        "A factual bullet without a number is always better "
        "than an invented number"
        in prompt
    )


def test_prompt_allows_supported_semantic_abstraction():
    prompt = " ".join(build_generation_instructions().split())

    assert "SEMANTIC ABSTRACTION" in prompt
    assert "restate approved facts" in prompt
    assert "normal technical terminology" in prompt


def test_prompt_prevents_semantic_abstraction_from_adding_facts():
    prompt = build_generation_instructions()

    assert (
        "Semantic abstraction must never introduce a new:"
        in prompt
    )
    assert "technology" in prompt
    assert "metric" in prompt
    assert "responsibility" in prompt
    assert "outcome" in prompt
    assert "qualification" in prompt


def test_prompt_preserves_upstream_selection_boundary():
    prompt = build_generation_instructions()

    assert (
        "The upstream system has already selected "
        "the experiences and projects"
        in prompt
    )
    assert (
        "Do not add, remove, replace, merge, or invent records"
        in prompt
    )


def test_prompt_requires_preserving_record_ids():
    prompt = build_generation_instructions()

    assert (
        "Preserve every supplied experience_id and project_id exactly"
        in prompt
    )
    assert "Every experience_id must be supplied" in prompt
    assert "Every project_id must be supplied" in prompt


def test_prompt_requires_exact_composition_allocations():
    prompt = " ".join(build_generation_instructions().split())

    assert (
        "Generate exactly target_bullets for every supplied record"
        in prompt
    )
    assert "Do not redistribute bullets between records" in prompt


def test_prompt_requires_at_least_two_project_bullets():
    prompt = build_generation_instructions()

    assert (
        "Every selected project must have at least 2 bullets"
        in prompt
    )
    assert "generate at least 2 bullets" in prompt


def test_prompt_prevents_inventing_content_for_bullet_counts():
    prompt = build_generation_instructions()

    assert "If evidence is limited" in prompt
    assert (
        "Never invent content just to satisfy "
        "the requested bullet count"
        in prompt
    )


def test_prompt_requires_quantification_when_supported():
    prompt = " ".join(build_generation_instructions().split())

    assert "QUANTIFICATION" in prompt
    assert "For EVERY selected experience or project:" in prompt
    assert (
        "at least ONE bullet containing a supported number"
        in prompt
    )
    assert (
        "Treat this as an important requirement, "
        "not a casual preference"
        in prompt
    )


def test_prompt_maximizes_supported_quantified_bullets():
    prompt = build_generation_instructions()

    assert (
        "maximize meaningful quantified bullets"
        in prompt
    )
    assert "ONLY" in prompt
    assert "approved_candidate_facts" in prompt


def test_prompt_preserves_supported_metrics():
    prompt = " ".join(build_generation_instructions().split())

    assert (
        "Preserve useful approved metrics instead of replacing "
        "them with generic statements"
        in prompt
    )
    assert (
        "Keep each metric with the contribution it actually supports"
        in prompt
    )


def test_prompt_allows_multiple_distinct_quantified_bullets():
    prompt = " ".join(build_generation_instructions().split())

    assert "If multiple independent useful metrics exist" in prompt
    assert "use them across separate bullets" in prompt


def test_prompt_forbids_fabricated_quantification():
    prompt = build_generation_instructions()

    assert "invent a number" in prompt
    assert "estimate a missing number" in prompt
    assert "extrapolate a number" in prompt
    assert "manufacture a metric" in prompt
    assert (
        "force a number into a record with no supported "
        "quantitative evidence"
        in prompt
    )


def test_prompt_allows_non_quantified_bullets_without_evidence():
    prompt = " ".join(build_generation_instructions().split())

    assert (
        "If no useful supported number exists for a record"
        in prompt
    )
    assert "non-quantified bullets instead" in prompt


def test_prompt_requires_natural_concise_resume_writing():
    prompt = build_generation_instructions()

    assert "strong human technical resume writer" in prompt
    assert "concise" in prompt
    assert "natural" in prompt
    assert "specific" in prompt
    assert "technically credible" in prompt
    assert "information-dense" in prompt
    assert "easy to scan" in prompt


def test_prompt_discourages_generic_ai_style_language():
    prompt = build_generation_instructions()

    assert "results-driven" in prompt
    assert "highly motivated" in prompt
    assert "passionate about" in prompt
    assert "proven track record" in prompt
    assert "keyword-stuff" in prompt


def test_prompt_requires_action_verb_diversity():
    prompt = build_generation_instructions()

    assert "ACTION VERBS" in prompt
    assert (
        "Vary opening action verbs across the full resume"
        in prompt
    )
    assert (
        'Do not repeatedly default to "Built" or "Designed"'
        in prompt
    )


def test_prompt_limits_repeated_opening_verbs():
    prompt = build_generation_instructions()

    assert (
        "Avoid starting two bullets in the same record "
        "with the same verb"
        in prompt
    )
    assert (
        "Avoid using the same opening verb more than twice "
        "across the full resume"
        in prompt
    )


def test_prompt_does_not_sacrifice_accuracy_for_verb_variety():
    prompt = build_generation_instructions()

    assert (
        "Never change factual meaning just to avoid repetition"
        in prompt
    )
    assert (
        "Factual precision is more important than verb variety"
        in prompt
    )


def test_prompt_sets_bullet_density_guidance():
    prompt = build_generation_instructions()

    assert "15-30 words per bullet" in prompt
    assert "downstream page fitter" in prompt
    assert "one clear contribution or technical aspect" in prompt


def test_prompt_requires_strongest_bullets_first():
    prompt = " ".join(build_generation_instructions().split())

    assert (
        "order bullets from strongest and most job-relevant "
        "to least important"
        in prompt
    )
    assert (
        "Later bullets should contain more expendable supporting detail"
        in prompt
    )


def test_prompt_requires_distinct_supported_bullets():
    prompt = build_generation_instructions()

    assert "Use distinct supported aspects across bullets" in prompt
    assert (
        "Do not artificially split one idea just to satisfy bullet count"
        in prompt
    )
    assert (
        "Remove redundant wording before removing strong evidence"
        in prompt
    )


def test_prompt_requires_exact_experience_generation():
    prompt = build_generation_instructions()

    assert "For each selected experience:" in prompt
    assert "preserve experience_id" in prompt
    assert "generate exactly target_bullets" in prompt
    assert "keep bullets distinct and useful" in prompt


def test_prompt_requires_experience_quantification_when_supported():
    prompt = " ".join(build_generation_instructions().split())

    assert (
        "If useful supported quantitative evidence exists, "
        "include at least one quantified bullet whenever practical"
        in prompt
    )


def test_prompt_requires_exact_project_generation():
    prompt = build_generation_instructions()

    assert "For each selected project:" in prompt
    assert "preserve project_id" in prompt
    assert "generate exactly target_bullets" in prompt
    assert "generate at least 2 bullets" in prompt
    assert "keep bullets distinct and useful" in prompt


def test_prompt_prioritizes_project_implementation_and_impact():
    prompt = build_generation_instructions()

    assert (
        "prioritize implementation, technical approach, "
        "scale, and outcomes"
        in prompt
    )


def test_prompt_restricts_skills_to_approved_input():
    prompt = build_generation_instructions()

    assert "Return only supplied approved skills" in prompt
    assert "Do not derive skills from job_context" in prompt
    assert (
        "Do not invent skill synonyms for keyword matching"
        in prompt
    )
    assert "Every skill must be supplied and approved" in prompt


def test_prompt_keeps_professional_summary_compact():
    prompt = build_generation_instructions()

    assert "preferably 1-2 short sentences" in prompt
    assert (
        "Use job_context only to decide which approved "
        "facts deserve emphasis"
        in prompt
    )
    assert "Do not:" in prompt
    assert "write a generic objective" in prompt
    assert "repeat the entire skills section" in prompt


def test_prompt_forbids_unsupported_summary_claims():
    prompt = build_generation_instructions()

    assert "claim unsupported years of experience" in prompt
    assert "claim unsupported expertise" in prompt
    assert "claim unsupported specialization" in prompt
    assert "claim unsupported leadership" in prompt
    assert "claim unsupported seniority" in prompt


def test_prompt_forbids_document_format_generation():
    prompt = build_generation_instructions()

    assert "Do not generate:" in prompt
    assert "LaTeX" in prompt
    assert "HTML" in prompt
    assert "Markdown" in prompt
    assert "complete resume document" in prompt


def test_prompt_requires_structured_resume_content_only():
    prompt = build_generation_instructions()

    assert "Return structured content containing only:" in prompt
    assert "professional_summary" in prompt
    assert "experiences:" in prompt
    assert "experience_id" in prompt
    assert "projects:" in prompt
    assert "project_id" in prompt
    assert "skills" in prompt


def test_prompt_requires_non_empty_bullets():
    prompt = build_generation_instructions()

    assert "Every bullet must be a non-empty string" in prompt


def test_prompt_requires_exact_final_structure():
    prompt = build_generation_instructions()

    assert (
        "Every record must contain exactly its allocated target_bullets"
        in prompt
    )
    assert "Every experience_id must be supplied" in prompt
    assert "Every project_id must be supplied" in prompt
    assert "Every skill must be supplied and approved" in prompt


def test_prompt_final_check_protects_factual_integrity():
    prompt = build_generation_instructions()

    assert "FINAL CHECK" in prompt
    assert (
        "every candidate claim is supported by "
        "approved_candidate_facts"
        in prompt
    )
    assert (
        "no fact, technology, skill, metric, or outcome was invented"
        in prompt
    )


def test_prompt_final_check_protects_metric_provenance():
    prompt = build_generation_instructions()

    assert (
        "every numerical claim belongs to that same "
        "experience or project"
        in prompt
    )
    assert (
        "no unsupported number was added for quantification"
        in prompt
    )


def test_prompt_final_check_requires_quantified_records_when_supported():
    prompt = build_generation_instructions()

    assert (
        "records containing useful supported numbers preserve "
        "at least one"
        in prompt
    )
    assert "quantified bullet whenever practical" in prompt


def test_prompt_final_check_requires_verb_review():
    prompt = build_generation_instructions()

    assert (
        "opening action verbs are varied where accurate alternatives exist"
        in prompt
    )
    assert (
        '"Built" and "Designed" are not unnecessarily repeated'
        in prompt
    )


def test_prompt_defines_final_priority_rules():
    prompt = build_generation_instructions()

    assert "When accuracy conflicts with style, choose accuracy" in prompt
    assert (
        "When quantification conflicts with evidence, choose evidence"
        in prompt
    )
    assert (
        "When verb variety conflicts with factual precision, "
        "choose factual precision"
        in prompt
    )
    assert (
        "When job alignment conflicts with candidate evidence, "
        "choose candidate evidence"
        in prompt
    )