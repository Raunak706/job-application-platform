# Candidate ↔ Job Matching
## V1 Handoff and V2 Design Goals

## 1. Purpose

This document explains the current Candidate ↔ Job Matching implementation and the intended direction for a future Matching v2.

It is written so another developer can work on matching independently without needing prior chat history.

The main architectural requirement is:

```text
CanonicalCandidateProfile
        +
Normalized Job
        ↓
MatchingService
        ↓
CandidateJobMatchResult
        ↓
Resume Tailoring
Application Selection
Analytics
```

Downstream code must depend on the stable matching result contract, not on the internal implementation of Matching v1.

This allows Matching v1 to be replaced or enhanced later without redesigning downstream resume or application workflows.

---

## 2. Current Status

Matching v1 is a deterministic, explainable baseline.

It currently includes:

- candidate feature extraction
- job feature extraction
- skill matching
- experience/project evidence matching
- title relevance matching
- location/workplace/employment compatibility
- stable `CandidateJobMatchResult`
- thin `MatchingService`
- deterministic scoring
- human-readable reasons
- generic multi-candidate behavior

The current matcher is intentionally simple.

It is not intended to be the final intelligent matcher.

Its purpose is to provide:

- a working baseline
- transparent logic
- testable behavior
- stable downstream interfaces
- something future matching versions can be compared against

---

## 3. Public Matching Boundary

The main public service is:

```python
from src.matching.service import MatchingService
```

Usage:

```python
result = MatchingService().match(
    candidate_profile,
    job,
)
```

Inputs:

```text
CanonicalCandidateProfile
Job
```

Output:

```text
CandidateJobMatchResult
```

Downstream systems should consume this boundary.

They should not directly call low-level scorer functions unless they are part of matching internals.

---

## 4. Candidate Contract

Matching consumes:

```python
CanonicalCandidateProfile
```

from:

```text
src/candidate_profile/contracts.py
```

The matcher does not query candidate tables directly.

Candidate profile loading remains the responsibility of:

```python
CandidateProfileService
```

Example:

```python
profile = CandidateProfileService().get_profile(candidate_id)
```

This boundary must remain intact.

Do not add candidate-specific matching logic.

Never write logic such as:

```python
if candidate_id == 1:
    ...
```

The matcher must work for all candidates through the same path.

---

## 5. Job Contract

Matching consumes the normalized SQLAlchemy `Job` model from:

```text
src/database/models.py
```

Important normalized fields include:

```text
id
title
company
location
country
workplace_type
employment_type
department
description
source
source_job_id
source_url
apply_url
```

Matching must not modify job normalization.

The normalized `jobs` table is the job-side source for matching.

---

## 6. Matching Package

Current package:

```text
src/matching/
```

Current important files:

```text
src/matching/contracts.py
src/matching/candidate_features.py
src/matching/job_features.py
src/matching/scorer.py
src/matching/service.py
```

---

## 7. CandidateJobMatchResult

Current result contract:

```text
candidate_id
job_id
matcher_version

overall_score

skill_score
title_relevance_score
evidence_score
compatibility_score

matched_skills
missing_skills

supporting_experience_ids
supporting_project_ids

compatibility
reasons
```

This contract is the stable downstream boundary.

Future matcher versions should preserve the overall purpose of this result.

If the result contract needs to evolve, changes should be additive where possible.

Do not force downstream systems to understand matcher internals.

---

## 8. Matcher Versioning

Current matcher version:

```text
v1
```

The result includes:

```python
matcher_version = "v1"
```

This field exists for traceability.

Downstream code should normally not branch on matcher version.

Bad:

```python
if result.matcher_version == "v1":
    ...
```

Preferred:

```text
consume CandidateJobMatchResult consistently
```

Future Matching v2 should ideally return the same general result shape.

---

## 9. Candidate Feature Extraction

File:

```text
src/matching/candidate_features.py
```

Current candidate features include:

```text
candidate_id
skills
experiences
projects
current_location
current_country
active preferences
```

Skills use the canonical normalized skill names already stored in the candidate profile.

Experiences expose:

```text
experience_id
title
description
```

Projects expose:

```text
project_id
name
description
```

Preferences are included only when active.

Missing candidate fields are valid and must not cause matching failures.

---

## 10. Job Feature Extraction

File:

```text
src/matching/job_features.py
```

Current job features include:

```text
job_id
title
company
location
country
workplace_type
employment_type
department
description
```

Text fields are normalized deterministically.

Missing optional fields remain `None`.

The matcher must remain safe when job descriptions, locations, workplace types, or other optional fields are missing.

---

## 11. Skill Matching V1

File:

```text
src/matching/scorer.py
```

Matching v1 uses a hardcoded known-skill vocabulary.

Examples include:

```text
Python
SQL
PostgreSQL
Databricks
PySpark
Pandas
NumPy
Machine Learning
Natural Language Processing
Docker
Git
REST APIs
Data Pipelines
ETL
XGBoost
```

The current implementation uses deterministic boundary-aware text matching.

It does not use embeddings or LLMs.

The current skill result includes:

```text
matched_skills
missing_skills
skill_score
```

Skill score is:

```text
matched detected job skills
/
all detected job skills
```

If no recognized job skills are detected:

```text
skill_score = 0.0
```

---

## 12. Important V1 Skill Limitation

The known skill vocabulary is hardcoded.

This means v1 can miss:

- aliases
- abbreviations
- related technologies
- semantically equivalent skills
- skills not included in the vocabulary

Examples:

```text
Spark vs Apache Spark
Postgres vs PostgreSQL
ML vs Machine Learning
BI vs Business Intelligence
```

Do not overcomplicate v1 to solve this.

This is a v2 concern.

---

## 13. Evidence Matching V1

Evidence matching links matched skills back to canonical candidate evidence.

Current evidence sources:

```text
candidate experiences
candidate projects
```

The scorer only treats a skill as evidence-supported when:

1. the job mentions the skill
2. the candidate profile contains the skill
3. an experience or project description explicitly supports it

This prevents the matcher from inventing evidence.

Example:

If a job requires:

```text
Spark
```

and the candidate only has:

```text
Databricks
```

the matcher must not automatically claim Spark evidence.

Related technologies are not proof.

This integrity rule must be preserved in future versions.

---

## 14. Title Relevance V1

Title relevance currently uses deterministic hardcoded role families.

Examples:

```text
Data Scientist
Machine Learning Engineer
ML Engineer
Applied Scientist
```

and:

```text
Data Analyst
Analytics Engineer
Business Intelligence Analyst
```

and:

```text
Data Engineer
Analytics Engineer
```

and:

```text
AI Engineer
Artificial Intelligence Engineer
Machine Learning Engineer
ML Engineer
```

This is intentionally simple.

It does not attempt semantic title similarity.

Known limitation:

A candidate with title:

```text
Machine Learning Engineer
```

may still receive:

```text
title_relevance_score = 0
```

for some related roles not represented in the current role groups.

This is acceptable for v1.

---

## 15. Compatibility V1

Compatibility considers:

```text
location
workplace type
employment type
```

Current statuses include:

```text
location:compatible
location:mismatch
location:unknown

workplace:compatible
workplace:mismatch
workplace:unknown

employment_type:compatible
employment_type:mismatch
employment_type:unknown
```

Unknown data must remain unknown.

Do not treat missing data as a mismatch.

---

## 16. Location Compatibility V1

Current location compatibility is country-level only.

If:

```text
candidate.current_country == job.country
```

then:

```text
location:compatible
```

If both countries exist and differ:

```text
location:mismatch
```

If either side is missing:

```text
location:unknown
```

The current matcher does not calculate:

- commuting distance
- state-level compatibility
- relocation
- visa implications
- remote geographic restrictions

These belong in later versions.

---

## 17. Workplace Compatibility V1

The matcher checks active candidate preferences such as:

```text
category = workplace
preference_key = workplace_types
```

Example values:

```json
{
  "values": [
    "remote",
    "hybrid"
  ]
}
```

A hybrid job would be compatible.

An onsite job would be a mismatch.

If no candidate workplace preference exists:

```text
workplace:unknown
```

---

## 18. Employment Compatibility V1

The matcher checks active candidate preferences such as:

```text
category = employment
preference_key = employment_types
```

Example:

```json
{
  "values": [
    "full_time"
  ]
}
```

If either side does not provide enough information:

```text
employment_type:unknown
```

---

## 19. Overall Score V1

Current formula:

```text
45% skill match
25% title relevance
20% evidence
10% compatibility
```

Equivalent:

```python
overall_score = (
    skill_score * 0.45
    + title_relevance_score * 0.25
    + evidence_score * 0.20
    + compatibility_score * 0.10
)
```

These weights are intentionally simple.

They are not claimed to be statistically optimal.

They exist to provide:

- predictable behavior
- interpretability
- a baseline for future comparison

Future versions may replace them.

Downstream systems must not depend on these exact weights.

---

## 20. Explainability

The matcher returns human-readable reasons.

Examples:

```text
Matched skills: python, sql.
```

```text
Job skills without direct candidate evidence: spark.
```

```text
Candidate experience includes a related role family.
```

```text
Canonical experience or project evidence supports matched job skills.
```

```text
Compatibility: location:compatible, workplace:unknown, employment_type:unknown.
```

The final match must remain explainable.

Future v2 improvements should not replace this with only an opaque score.

---

## 21. Verified Multi-Candidate Behavior

Matching v1 was manually tested through the same path for:

```text
Candidate 1
Candidate 746
```

The same:

```python
MatchingService().match(...)
```

path was used.

No candidate-specific matching logic exists.

This requirement must remain true.

---

## 22. Real Job Validation

Matching v1 was validated against real normalized jobs.

Observed examples included:

```text
Data Engineer II - Life Sciences
Data Engineer (in person)
Experienced Software Engineer
Software Engineer
Software Engineering Intern
```

Data-engineering roles scored significantly higher than unrelated software-engineering examples.

The baseline therefore behaves reasonably enough to use as Matching v1.

---

## 23. Known V1 Limitations

Known limitations include:

- hardcoded skill vocabulary
- limited skill aliases
- no structured required/preferred requirement distinction
- title relevance based on hardcoded role groups
- no semantic similarity
- no embeddings
- no LLM requirement extraction
- no experience-duration reasoning
- no education-requirement reasoning
- no certification matching
- simple location compatibility
- preferences may be missing
- unverified candidate skills are currently treated like other candidate skills
- no confidence scoring per requirement
- no historical persisted match records
- no requirement-level evidence graph

These limitations are accepted for v1.

Do not turn v1 into v2 incrementally inside downstream work.

---

## 24. V2 Goal

Matching v2 should improve intelligence without breaking downstream consumers.

Target architecture:

```text
CanonicalCandidateProfile
        +
Normalized Job
        ↓
Structured Job Requirement Extraction
        ↓
Requirement Classification
        ↓
Skill Taxonomy / Alias Resolution
        ↓
Semantic Candidate ↔ Requirement Matching
        ↓
Canonical Evidence Linking
        ↓
Compatibility / Hard Constraints
        ↓
Scoring / Explanation
        ↓
CandidateJobMatchResult
```

---

## 25. Structured Job Requirement Extraction

V2 should parse job descriptions into explicit structured requirements.

Example output:

```text
Python
    type: required
    confidence: high

SQL
    type: required
    confidence: high

Spark
    type: preferred
    confidence: medium

3+ years experience
    type: required

Bachelor's degree
    type: required
```

The matcher should distinguish:

```text
required
preferred
optional
unknown
```

Do not treat every technology appearing in a job description as a hard requirement.

---

## 26. Skill Taxonomy and Alias Layer

V2 should resolve aliases and related forms.

Examples:

```text
postgres
postgresql

spark
apache spark

ml
machine learning

nlp
natural language processing

sklearn
scikit-learn
```

This should be implemented as a reusable taxonomy layer.

Avoid hiding aliases inside random scorer logic.

---

## 27. Semantic Matching

V2 may add semantic similarity using embeddings.

Potential uses:

- candidate experience ↔ job responsibility similarity
- project ↔ job responsibility similarity
- role title similarity
- requirement ↔ evidence similarity

Semantic matching should supplement canonical evidence.

It must not invent candidate facts.

---

## 28. LLM-Assisted Requirement Interpretation

A future OpenAI-assisted layer may interpret complex job descriptions.

Recommended use:

```text
job description
    ↓
structured JSON requirement extraction
```

The LLM should not directly return the final opaque match score.

Preferred architecture:

```text
LLM interpretation
        ↓
structured requirements
        ↓
deterministic / explainable scoring
```

---

## 29. Verification Status in V2

Candidate skills have verification statuses.

V2 should consider them.

Possible categories include:

```text
verified
source_document
manual
unverified
```

Example future behavior:

```text
verified evidence
    > source_document evidence
    > manual evidence
    > unverified/planned skill
```

Do not silently treat planned skills as equal to demonstrated experience.

---

## 30. Evidence Integrity

This rule must remain permanent:

```text
Matching must never fabricate candidate evidence.
```

The system may say:

```text
Skill appears related.
```

But must distinguish that from:

```text
Candidate has direct canonical evidence.
```

Resume tailoring depends on this distinction.

---

## 31. Hard Requirements vs Soft Relevance

V2 should separate:

```text
hard incompatibilities
```

from:

```text
soft relevance
```

Examples of possible hard constraints:

```text
work authorization
required location
required degree
required certification
mandatory technology
minimum years of experience
```

These should not simply disappear inside a weighted average.

---

## 32. Future Persistence

Matching currently runs in memory.

Do not create match persistence unless there is a demonstrated workflow need.

A future persisted match record may include:

```text
candidate_id
job_id
matcher_version
overall_score
component_scores
matched_requirements
missing_requirements
evidence references
created_at
```

If persistence is introduced, historical matcher versions should remain interpretable.

---

## 33. Downstream Compatibility Requirement

This is one of the most important design rules.

Resume tailoring should consume:

```text
CandidateJobMatchResult
```

It should not know:

- how skills were detected
- which regex was used
- which weights were used
- whether embeddings exist
- whether an LLM was used
- how title similarity was calculated

This allows v2 to replace v1 internally.

---

## 34. Tests Required for V2

V2 should include tests for:

```text
strong match
weak match
unrelated match
required skill missing
preferred skill missing
skill aliases
semantic evidence
candidate missing optional fields
job missing optional fields
location compatibility
workplace compatibility
employment compatibility
hard incompatibility
verified vs unverified evidence
deterministic structured output
multiple candidates
no cross-candidate leakage
no fabricated evidence
```

---

## 35. Merge Safety

A developer working on Matching v2 should avoid modifying unrelated completed systems.

Do not redesign:

```text
job ingestion
job normalization
CandidateProfileRepository
CandidateProfileService
CandidateManagementService
CandidatePopulationService
```

Matching should remain downstream.

Prefer changes inside:

```text
src/matching/
tests/test_matching_*.py
```

Only change shared contracts when there is a demonstrated requirement.

---

## 36. Branch Recommendation

A separate development branch is recommended.

Example:

```bash
git checkout -b matching-v2
```

The branch can evolve independently.

When ready:

```text
run focused tests
run full tests
inspect diff
merge or open pull request
```

The main branch can continue downstream using Matching v1 in the meantime.

---

## 37. Definition of Done for V2

Matching v2 should not be considered complete until:

- structured requirements exist
- required/preferred distinction exists
- skill aliases are supported
- semantic matching is explainable
- candidate evidence remains canonical
- unverified skills are handled appropriately
- hard constraints are explicit
- multiple candidates work through the same path
- downstream `CandidateJobMatchResult` consumption still works
- real normalized jobs have been evaluated
- focused tests pass
- full test suite passes
- no unrelated architecture is redesigned

---

## 38. Current Decision

The current project decision is:

```text
Finish and freeze Matching v1.
Continue downstream into resume tailoring and application workflows.
Build Matching v2 later as a separate enhancement phase.
```

Matching v1 exists as the stable baseline.

Matching v2 should improve the implementation behind the same public matching boundary rather than forcing downstream redesign.