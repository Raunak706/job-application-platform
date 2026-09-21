# Resume / Candidate Document Ingestion
## Architecture Handoff and Implementation Goals

## 1. Purpose

This document defines the architecture and implementation expectations for the future candidate document-ingestion pipeline.

It is written so another developer can work on document/resume ingestion independently without needing prior chat history.

The goal is to allow a candidate to upload one or more resumes or other source documents, extract structured candidate information, reconcile it safely with the existing canonical candidate profile, and preserve provenance.

The key architectural rule is:

```text
Uploaded Document
        ↓
Immutable Source Document
        ↓
Document Parsing
        ↓
Extracted Candidate Facts
        ↓
Deduplication / Reconciliation
        ↓
Conflict Detection / Review
        ↓
Approved Canonical Writes
        ↓
CanonicalCandidateProfile
```

The ingestion pipeline must not silently overwrite canonical candidate truth.

---

## 2. Current Project Context

The project already has a completed canonical candidate knowledge-base architecture.

The canonical candidate profile is not merely a resume.

It is intended to contain the candidate's complete reusable knowledge base, including information such as:

```text
identity
contact information
links
work experience
projects
education
coursework
skills
certifications
awards
publications
activities
achievements
preferences
application facts
reusable stories
generic candidate facts
tags
relationships
evidence
```

Downstream systems such as:

```text
matching
resume tailoring
application workflows
analytics
```

should consume the canonical candidate profile rather than reading arbitrary source documents directly.

---

## 3. Critical Separation of Data Types

The project intentionally separates five different concepts.

### 3.1 Source Truth

Original uploaded or imported material.

Examples:

```text
resume PDF
resume DOCX
manual JSON import
future LinkedIn export
portfolio document
certificate document
```

Source truth is evidence.

It is not automatically canonical truth.

---

### 3.2 Canonical Truth

The structured, accepted candidate profile.

This is represented through the existing candidate-profile architecture and exposed downstream as:

```python
CanonicalCandidateProfile
```

Canonical truth should contain only accepted candidate facts.

---

### 3.3 Derived Data

Information calculated from canonical truth.

Examples:

```text
candidate-job match scores
semantic embeddings
ranking signals
analytics
derived years of experience
```

Derived data should not become canonical truth automatically.

---

### 3.4 Generated Artifacts

Content generated for a particular task or application.

Examples:

```text
tailored resume
cover letter
generated application answer
generated professional summary
```

Generated content must not automatically modify canonical truth.

---

### 3.5 Application History

Information about what was actually submitted to an employer.

Examples:

```text
resume snapshot
cover-letter snapshot
application answers
submission timestamp
application status
```

Application history should remain separate from source documents and canonical profile truth.

---

## 4. Existing Candidate Profile Boundary

Canonical candidate operations already exist under:

```text
src/candidate_profile/
```

Important files include:

```text
src/candidate_profile/contracts.py
src/candidate_profile/repository.py
src/candidate_profile/service.py
src/candidate_profile/management.py
src/candidate_profile/population.py
src/candidate_profile/populate_from_json.py
```

These components already have defined responsibilities.

---

## 5. CandidateProfileRepository

File:

```text
src/candidate_profile/repository.py
```

Responsibility:

```text
database persistence
database retrieval
canonical candidate entity access
```

This layer should not be redesigned merely to make document ingestion easier.

Only modify it when a demonstrated canonical-profile requirement requires it.

---

## 6. CandidateProfileService

File:

```text
src/candidate_profile/service.py
```

Responsibility:

```text
normal canonical candidate-profile operations
stable downstream candidate-profile access
service-level transactions
returning CanonicalCandidateProfile
```

The primary downstream contract is:

```python
CanonicalCandidateProfile
```

Document ingestion must eventually write approved information into the same canonical profile.

Do not create a second competing candidate-profile system.

---

## 7. CandidateManagementService

File:

```text
src/candidate_profile/management.py
```

Class:

```python
CandidateManagementService
```

Responsibility:

```text
candidate lifecycle
candidate creation
initial CandidateProfile creation
```

Candidate creation is intentionally separate from normal profile operations.

Do not move lifecycle/bootstrap behavior into `CandidateProfileService`.

---

## 8. CandidatePopulationService

File:

```text
src/candidate_profile/population.py
```

Class:

```python
CandidatePopulationService
```

Purpose:

```text
bulk population of an existing candidate profile
from manually reviewed structured data
```

The current population layer is already:

```text
generic
multi-user
stable-reference based
transactional
rerun-safe
```

It is not the document-ingestion pipeline.

However, some concepts from it may be useful when approved extracted facts eventually need to be written canonically.

---

## 9. Existing Manual JSON Population

Generic CLI:

```text
src/candidate_profile/populate_from_json.py
```

Usage:

```bash
python -m src.candidate_profile.populate_from_json \
  --candidate-id <ID> \
  --file <PATH>
```

This flow assumes the JSON is already reviewed and trusted.

That makes it fundamentally different from automated document ingestion.

Do not send raw machine-extracted resume information directly through the manual population flow without reconciliation.

---

## 10. Existing Stable References

Manual candidate JSON intentionally avoids database IDs.

Example:

```json
{
  "projects": [
    {
      "ref": "job_application_platform",
      "name": "Job Application Platform"
    }
  ]
}
```

Relationships can then use:

```json
{
  "project_ref": "job_application_platform"
}
```

Similar stable references exist for concepts such as:

```text
experience_ref
project_ref
education_ref
skill_ref
entity_ref
tag_ref
from_entity_ref
to_entity_ref
```

Do not introduce portable candidate data formats that depend directly on database primary keys.

---

## 11. Existing Candidate Document Schema

The database already contains document-ingestion-oriented structures.

Relevant models exist in:

```text
src/database/models.py
```

Important models include:

```text
CandidateSourceDocument
CandidateDocumentParse
CandidateExtractedFact
CandidateProfileConflict
CandidateEvidence
```

These structures were intentionally created to support a future ingestion pipeline.

Do not create duplicate tables before examining these existing models.

---

## 12. CandidateSourceDocument

Purpose:

```text
represent an immutable uploaded candidate source document
```

Important concepts include:

```text
candidate_id
document_type
label
original_filename
storage_uri
mime_type
size_bytes
content_hash
status
metadata_json
uploaded_at
```

There is a uniqueness rule involving:

```text
candidate_id
content_hash
```

This supports duplicate-document detection.

---

## 13. Source Documents Must Be Immutable Evidence

Once a document is accepted into the source-document layer, treat the original source as immutable evidence.

Do not silently replace the original document contents.

If a candidate uploads a new version of a resume:

```text
old resume
new resume
```

these should normally be represented as separate source documents.

This preserves provenance.

---

## 14. Document Hashing

Uploaded documents should have a stable content hash.

The existing source-document model includes:

```text
content_hash
```

Expected behavior:

```text
same candidate
+
same document content
        ↓
detect duplicate upload
```

Do not rely only on filenames.

Two different documents may have the same filename.

Two identical documents may have different filenames.

---

## 15. Document Storage

The database should store metadata and a storage reference.

The source-document model uses:

```text
storage_uri
```

Do not store large binary resume files directly inside normal candidate-profile rows.

The exact storage mechanism can be chosen later.

Possible local development storage could be:

```text
local filesystem
```

Future deployment may use:

```text
object storage
cloud blob storage
```

The candidate-ingestion architecture should not depend tightly on one storage provider.

---

## 16. CandidateDocumentParse

Purpose:

```text
represent one parser execution against a source document
```

Important concepts include:

```text
source_document_id
parser_name
parser_version
extracted_text
structured_payload
parsed_at
```

The schema supports parser versioning.

This is important because parsing logic can evolve.

---

## 17. Parser Versioning

A source document may be parsed again by a newer parser.

Conceptually:

```text
resume.pdf
    ↓
parser v1
    ↓
parse result v1

resume.pdf
    ↓
parser v2
    ↓
parse result v2
```

Do not overwrite old parse results when parser behavior changes.

Parser versioning supports reproducibility and debugging.

---

## 18. CandidateExtractedFact

Purpose:

```text
store candidate information extracted from a document
before it becomes canonical truth
```

Important concepts include:

```text
candidate_id
source_document_id
document_parse_id
proposed_entity_type
proposed_field
value_text
value_json
confidence
review_status
resolved_entity_type
resolved_entity_id
created_at
reviewed_at
```

This layer is deliberately separate from canonical candidate entities.

---

## 19. Extracted Facts Are Proposals

This rule is critical:

```text
CandidateExtractedFact != canonical candidate truth
```

An extracted fact represents something the parser/extractor believes the source document contains.

Examples:

```text
proposed_entity_type = experience
proposed_field = company
value_text = Tech Mahindra
```

or:

```text
proposed_entity_type = skill
proposed_field = canonical_name
value_text = Python
```

These are proposals until reconciliation/approval occurs.

---

## 20. Confidence

Extracted facts may include:

```text
confidence
```

Confidence may help determine:

```text
automatic acceptance thresholds
manual review priority
conflict severity
```

However:

```text
high confidence != guaranteed truth
```

Confidence should never bypass important conflict handling blindly.

---

## 21. Review Status

Extracted facts include a review lifecycle.

The exact allowed statuses should be inspected before implementation, but conceptually this layer may represent states such as:

```text
pending
accepted
rejected
resolved
```

Do not invent status values without confirming the existing project conventions.

---

## 22. CandidateProfileConflict

Purpose:

```text
represent a conflict between incoming extracted information
and existing canonical candidate truth
```

Important concepts include:

```text
candidate_id
conflict_type
existing_entity_type
existing_entity_id
field_name
incoming_extracted_fact_id
status
resolution_note
resolution_json
created_at
resolved_at
```

Conflicts must be explicit.

---

## 23. No Silent Overwrite

This is one of the most important permanent rules.

Example:

Existing canonical profile:

```text
University GPA = 3.3
```

New resume extraction:

```text
University GPA = 3.5
```

The ingestion system must not silently replace `3.3` with `3.5`.

Instead:

```text
incoming extracted fact
        ↓
comparison
        ↓
conflict detected
        ↓
CandidateProfileConflict
        ↓
review / resolution
        ↓
approved canonical write if appropriate
```

---

## 24. Deduplication vs Conflict Detection

These are different concepts.

### Duplicate

Example:

```text
Existing skill: Python
Incoming skill: Python
```

Likely result:

```text
same fact
no duplicate canonical row required
```

---

### Conflict

Example:

```text
Existing employment end date: Aug 2024
Incoming employment end date: Sep 2024
```

Likely result:

```text
conflict requiring reconciliation
```

Do not treat conflict handling as simple idempotency.

---

## 25. Exact-Match Rerun Safety

The existing manual population workflow is rerun-safe.

Document ingestion should also avoid creating repeated extracted facts or canonical rows unnecessarily.

However:

```text
rerun safety
```

and:

```text
conflict reconciliation
```

are different requirements.

Do not collapse them into one mechanism.

---

## 26. CandidateEvidence

Purpose:

```text
link canonical candidate truth back to supporting source evidence
```

Important concepts include:

```text
candidate_id
source_kind
source_document_id
extracted_fact_id
target_entity_type
target_entity_id
excerpt
locator_json
confidence
verification_status
created_at
```

This is the provenance layer.

---

## 27. Evidence Example

Suppose a resume contains:

```text
Built and maintained data pipelines in Azure Databricks.
```

The final canonical profile might contain:

```text
Skill: Databricks
```

Evidence could link:

```text
source document
        ↓
extracted fact
        ↓
canonical CandidateSkill
```

with an excerpt such as:

```text
Built and maintained data pipelines in Azure Databricks.
```

This allows downstream systems to distinguish:

```text
candidate claims skill
```

from:

```text
candidate has source-backed evidence for skill
```

---

## 28. Evidence Must Survive Reconciliation

When an extracted fact is accepted into canonical truth, preserve its evidence relationship.

Do not copy the value into the canonical profile and discard where it came from.

Provenance is important for:

```text
resume tailoring
matching
conflict review
auditability
future profile updates
```

---

## 29. Recommended Ingestion Pipeline

The target pipeline should look like:

```text
Upload
  ↓
CandidateSourceDocument
  ↓
Document Parser
  ↓
CandidateDocumentParse
  ↓
Structured Fact Extractor
  ↓
CandidateExtractedFact
  ↓
Deduplication
  ↓
Canonical Comparison
  ↓
Conflict Detection
  ↓
CandidateProfileConflict when needed
  ↓
Approval / Reconciliation
  ↓
Canonical Candidate Writes
  ↓
CandidateEvidence
```

---

## 30. Upload Layer

The upload layer should:

```text
accept a candidate_id
accept a document
compute content hash
detect duplicate document upload
store the document
create CandidateSourceDocument
```

The upload layer should not directly modify canonical candidate data.

---

## 31. Parser Layer

The parser should be responsible for:

```text
extracting text
extracting basic document structure where possible
producing a parser-versioned parse result
```

The parser should not decide canonical truth.

Potential future parser support may include:

```text
PDF
DOCX
plain text
```

Start with the minimum useful format rather than implementing every format immediately.

---

## 32. Extraction Layer

The extractor converts parsed resume content into structured candidate fact proposals.

Potential extracted domains include:

```text
identity
contact information
links
experience
projects
education
skills
certifications
awards
publications
activities
achievements
coursework
preferences
application facts
generic facts
```

Do not require all documents to contain all domains.

Missing sections are normal.

---

## 33. Extraction Output Should Be Structured

Avoid returning only free-form text.

Preferred:

```json
{
  "entity_type": "experience",
  "fields": {
    "company": "Example Company",
    "title": "Data Engineer"
  }
}
```

rather than:

```text
Candidate worked as a Data Engineer at Example Company.
```

Structured output makes reconciliation testable.

---

## 34. LLM Usage

An LLM may eventually be useful for extracting structured facts from resumes.

Recommended architecture:

```text
parsed resume text
        ↓
LLM structured extraction
        ↓
validated structured output
        ↓
CandidateExtractedFact
```

The LLM must not write canonical truth directly.

---

## 35. LLM Output Validation

LLM output must be validated before being accepted into the extraction layer.

Possible validation includes:

```text
schema validation
required field validation
date validation
enum validation
candidate/domain validation
```

Malformed model output should fail safely.

---

## 36. Date Integrity

The existing candidate architecture deliberately avoids inventing exact dates.

Example source:

```text
May 2025 – Aug 2025
```

Do not automatically invent:

```text
2025-05-01
2025-08-31
```

unless the source explicitly supports those dates.

Preserve uncertain or partial date precision honestly.

---

## 37. Missing Data

The ingestion pipeline must tolerate incomplete resumes.

Examples:

```text
no GitHub
no LinkedIn
no GPA
no project dates
no employment type
no certification expiry
```

Missing fields must not crash ingestion.

Do not invent values merely to fill schema fields.

---

## 38. Entity Matching

Before creating a new canonical entity, the reconciliation layer should determine whether the entity already exists.

Examples:

```text
same experience
same project
same education
same skill
same certification
```

Matching should use stable domain logic.

Do not deduplicate only by raw database ID.

---

## 39. Skill Reconciliation

The project already has a shared skill taxonomy table.

Relevant models include:

```text
Skill
SkillAlias
CandidateSkill
```

Canonical skill normalization already exists.

Do not create a second unrelated skill-normalization system inside document ingestion.

Reuse the existing taxonomy boundary where appropriate.

---

## 40. Experience Reconciliation

Incoming experience records may need comparison using signals such as:

```text
company
title
date range
location
description
```

Do not rely on one field alone.

Example:

```text
Machine Learning Engineer
Tech Mahindra
```

appearing on two resumes should usually refer to the same experience rather than creating two canonical experience rows.

---

## 41. Project Reconciliation

Incoming projects may need matching based on:

```text
project name
description
organization
technologies
dates
```

Again, avoid duplicate canonical projects across multiple resumes.

---

## 42. Education Reconciliation

Incoming education information may vary between documents.

Example:

```text
Master of Science in Data Science
```

versus:

```text
M.S. Data Science
```

The system should eventually recognize likely equivalence without creating duplicate education rows.

However, uncertain equivalence should not silently merge unrelated entities.

---

## 43. Conflict Review

Conflicts should be reviewable.

A useful future review workflow should show:

```text
existing canonical value
incoming extracted value
source document
source excerpt
confidence
proposed action
```

Possible decisions:

```text
keep existing
accept incoming
merge
reject incoming
defer
```

The exact user interface is a later concern.

The backend should support these decisions cleanly.

---

## 44. Canonical Write Boundary

Only approved/reconciled information should cross into canonical truth.

Recommended conceptual boundary:

```text
approved extracted facts
        ↓
canonical write service
        ↓
CandidateProfileRepository / canonical profile layer
```

Do not let the parser or extractor write directly into canonical candidate tables.

---

## 45. Transaction Strategy

Canonical reconciliation should use explicit transaction boundaries.

A failed approval/import should not leave a partially updated candidate profile.

The existing population layer already follows an atomic bulk-transaction philosophy.

Document-ingestion writes should preserve the same safety principle.

---

## 46. Auditability

Candidate-profile architecture already contains audit/version-oriented structures such as:

```text
CandidateProfileVersion
CandidateAuditLog
```

Before implementing new audit systems, inspect the existing models.

The document-ingestion pipeline should integrate with existing audit concepts rather than creating parallel history systems unnecessarily.

---

## 47. Multi-Candidate Requirement

All ingestion logic must remain generic.

Never write:

```python
if candidate_id == 1:
    ...
```

Never hardcode:

```text
Raunak
```

The ingestion pipeline must support:

```text
Candidate 1
Candidate 746
future candidates
```

through the same code path.

---

## 48. Candidate Isolation

A source document uploaded for Candidate A must never:

```text
create facts for Candidate B
resolve entities belonging to Candidate B
attach evidence to Candidate B
create conflicts against Candidate B
```

Candidate isolation must be tested explicitly.

---

## 49. Privacy

Candidate documents may contain:

```text
phone numbers
email addresses
addresses
employment information
education information
work authorization
other sensitive application facts
```

Do not expose private candidate documents in Git.

Private real candidate data must remain local or in appropriate secure storage.

---

## 50. Git Rules

Current private candidate JSON convention:

```text
data/candidates/*.json
```

is ignored except:

```text
data/candidates/example_candidate.json
```

Do not commit real candidate resumes, private JSON, or personal source documents.

Version-controlled test fixtures must contain fake data only.

---

## 51. Safe Test Fixtures

Document-ingestion tests should use synthetic candidate documents.

Examples:

```text
fake_resume.pdf
fake_resume.txt
fake extracted payload
```

Do not copy real candidate personal information into committed test fixtures.

---

## 52. Recommended Package Boundary

A future package could live under something such as:

```text
src/candidate_ingestion/
```

Possible future modules may include:

```text
upload.py
storage.py
parsers/
extractor.py
reconciliation.py
conflicts.py
approval.py
service.py
contracts.py
```

Do not create all of these blindly.

Start with the smallest structure that supports the workflow.

---

## 53. Recommended Public Ingestion Service

A future stable service might conceptually look like:

```python
CandidateDocumentIngestionService
```

Potential operations might include:

```text
upload_document(...)
parse_document(...)
extract_facts(...)
reconcile(...)
approve(...)
```

Exact method signatures should be designed after inspecting existing code.

Do not treat these names as mandatory.

---

## 54. Important Architectural Boundary

Downstream code should not need to understand:

```text
PDF parser internals
LLM prompts
OCR
document storage provider
reconciliation algorithm
conflict-resolution implementation
```

Downstream systems should continue consuming:

```text
CanonicalCandidateProfile
```

This keeps document ingestion replaceable and independently improvable.

---

## 55. Resume Tailoring Relationship

Resume ingestion and resume tailoring are separate systems.

Resume ingestion:

```text
source documents
        ↓
candidate facts
        ↓
canonical truth
```

Resume tailoring:

```text
canonical truth
        +
job
        +
matching result
        ↓
selected approved candidate facts
        ↓
generated tailored resume
```

Do not merge these responsibilities.

---

## 56. Generated Resume Must Not Become Source Truth Automatically

A tailored resume may contain generated wording.

That wording must not automatically become canonical candidate truth.

Example:

```text
canonical achievement
        ↓
OpenAI rewrites wording
        ↓
tailored resume bullet
```

The rewritten bullet is a generated artifact.

It is not automatically a new canonical fact.

---

## 57. Future Resume Tailoring Architecture

The planned downstream tailoring architecture is:

```text
CanonicalCandidateProfile
        +
Normalized Job
        +
CandidateJobMatchResult
        ↓
select relevant approved candidate facts
        ↓
OpenAI API generates structured resume content
        ↓
local Python renderer
        ↓
stable LaTeX template
        ↓
locally compiled PDF
```

Formatting should remain deterministic and local.

The model should not freely rewrite the entire LaTeX document.

---

## 58. Application Snapshot Requirement

A working tailored resume may be overwritten while experimenting.

Once an application is submitted:

```text
resume used for application
cover letter used
application answers
```

should be saved as immutable application artifacts.

Do not rely only on the current working resume file.

---

## 59. Recommended Development Stages

A practical implementation sequence is:

### Stage A — Upload

Implement:

```text
document validation
content hashing
storage
CandidateSourceDocument creation
duplicate detection
```

---

### Stage B — Parsing

Implement:

```text
parser interface
first supported document type
CandidateDocumentParse
parser versioning
```

---

### Stage C — Structured Extraction

Implement:

```text
structured candidate extraction schema
validation
CandidateExtractedFact writes
confidence
review status
```

---

### Stage D — Deduplication

Implement:

```text
detect exact duplicate facts
identify likely existing canonical entities
avoid duplicate candidate rows
```

---

### Stage E — Conflict Detection

Implement:

```text
compare incoming facts with canonical truth
create CandidateProfileConflict
preserve both existing and incoming values
```

---

### Stage F — Review / Approval

Implement:

```text
accept
reject
merge
keep existing
```

---

### Stage G — Canonical Writes

Implement:

```text
approved fact → canonical entity
atomic transaction
evidence creation
audit/version integration
```

---

### Stage H — Real Resume Validation

Test with multiple resumes for one candidate.

Verify:

```text
no duplicate experiences
no duplicate skills
no silent overwrites
conflicts generated where appropriate
provenance preserved
```

---

## 60. Initial Scope Recommendation

Do not implement every candidate domain in the first iteration.

A reasonable first end-to-end slice could support:

```text
skills
experience
education
projects
```

Once the reconciliation architecture is proven, expand to:

```text
certifications
awards
publications
activities
achievements
contacts
links
facts
```

Architecture should still allow all canonical domains eventually.

---

## 61. Parser Independence

Document parsing should be independent of candidate reconciliation.

Example:

```text
PDF parser
        ↓
text / structure

DOCX parser
        ↓
text / structure

both
        ↓
same extraction layer
```

Do not put canonical database logic inside file parsers.

---

## 62. Extraction Independence

The extractor should not depend on one exact parser.

Preferred:

```text
ParsedCandidateDocument
        ↓
Extractor
```

rather than:

```text
PDF-specific extraction logic
mixed directly with canonical database writes
```

This makes adding DOCX or other formats easier later.

---

## 63. Reconciliation Independence

Reconciliation should operate on structured extracted facts.

It should not need to know whether the source was:

```text
PDF
DOCX
JSON
future API import
```

That keeps the ingestion architecture extensible.

---

## 64. Idempotency Expectations

Repeated processing of the same source should not create uncontrolled duplicates.

Examples:

```text
same document uploaded twice
same parse retried
same extraction rerun
same approval operation retried
```

Each layer should define its own idempotency rule.

---

## 65. Error Isolation

Failures should be attributable to a specific stage.

Examples:

```text
upload failure
storage failure
parse failure
extraction failure
validation failure
reconciliation failure
canonical-write failure
```

Avoid one giant ingestion function where failure location is unclear.

---

## 66. Observability

Useful future metadata may include:

```text
parser version
extractor version
model name/version
processing timestamp
confidence
review status
source document ID
```

This helps explain how canonical data was produced.

---

## 67. LLM Prompt Versioning

If an LLM extractor is introduced, prompt/schema behavior should be versionable.

Conceptually:

```text
extractor_name
extractor_version
model
schema_version
```

Do not make historical extracted facts impossible to interpret after changing prompts.

---

## 68. Human Review

The architecture should support human review even if an initial version automatically approves very safe cases.

Potential automatic cases:

```text
exact duplicate skill
exact duplicate link
same confirmed candidate name
```

Potential review-required cases:

```text
different dates
different employer/title combinations
different GPA
different contact details
conflicting work authorization
ambiguous project match
```

---

## 69. Exact Duplicate Example

Existing canonical skill:

```text
Python
```

Resume extraction:

```text
Python
```

Likely action:

```text
reuse canonical Skill
reuse CandidateSkill
attach additional evidence
```

Do not create another Python candidate skill row.

---

## 70. Conflict Example

Canonical:

```text
Tech Mahindra
Machine Learning Engineer
Sep 2023 – Aug 2024
```

Incoming extraction:

```text
Tech Mahindra
Machine Learning Engineer
Sep 2023 – Oct 2024
```

Potential result:

```text
identify likely same experience
detect end-date disagreement
create CandidateProfileConflict
do not silently overwrite
```

---

## 71. Additional Evidence Example

Canonical:

```text
Databricks skill already exists
```

New resume also mentions:

```text
Built Azure Databricks pipelines.
```

Likely behavior:

```text
do not duplicate canonical skill
create additional source evidence
```

Multiple documents may support the same canonical fact.

---

## 72. Source Deletion

If source deletion is implemented later, think carefully before deleting provenance used by canonical evidence.

Do not casually delete:

```text
source document
parse
extracted facts
evidence
```

if canonical facts depend on them.

Retention behavior should be designed explicitly.

---

## 73. Candidate Profile Versioning

The schema includes:

```text
CandidateProfileVersion
```

A future ingestion approval may optionally create a new profile version.

Before implementing this, inspect the existing intended version semantics.

Do not add parallel profile-versioning infrastructure unnecessarily.

---

## 74. Candidate Audit Log

The schema includes:

```text
CandidateAuditLog
```

Approved ingestion changes may eventually be recorded there.

Possible audit concepts include:

```text
entity created
entity updated
conflict resolved
fact rejected
source document linked
```

Inspect existing conventions before integrating.

---

## 75. Tests — Upload Layer

Tests should eventually verify:

```text
new document accepted
duplicate content detected
same filename with different content allowed
different filename with same content deduplicated appropriately
candidate isolation
invalid file rejected safely
```

---

## 76. Tests — Parsing Layer

Tests should verify:

```text
supported file parses
parser version stored
parse text preserved
structured payload preserved
parse failure does not modify canonical profile
```

---

## 77. Tests — Extraction Layer

Tests should verify:

```text
structured facts created
candidate_id correct
source_document_id correct
document_parse_id correct
confidence retained
invalid extraction rejected
missing optional fields safe
```

---

## 78. Tests — Reconciliation Layer

Tests should verify:

```text
exact duplicate detected
likely same entity detected
new entity detected
conflicting field detected
ambiguous match handled safely
```

---

## 79. Tests — Conflict Layer

Tests should verify:

```text
conflict row created
existing canonical value preserved
incoming extracted value preserved
resolution status tracked
resolution note supported
```

---

## 80. Tests — Approval Layer

Tests should verify:

```text
approved new fact creates canonical data
rejected fact does not modify canonical data
accepted duplicate does not create duplicate row
accepted conflict updates only after explicit resolution
evidence created
transaction rollback works
```

---

## 81. Tests — Multi-Resume Behavior

This is especially important.

Upload two different resumes for the same candidate.

Verify:

```text
same experience is reconciled
same skills are deduplicated
new skills are added
conflicting facts are flagged
evidence from both documents is retained
```

---

## 82. Tests — Multi-Candidate Isolation

Use at least two candidates.

Verify:

```text
Candidate A document cannot modify Candidate B
Candidate A facts cannot attach to Candidate B entities
Candidate A conflicts cannot reference Candidate B canonical data
Candidate A evidence cannot point to Candidate B canonical data
```

---

## 83. PostgreSQL Testing Requirement

The project uses PostgreSQL-specific features including:

```text
JSONB
PostgreSQL constraints
PostgreSQL transaction behavior
```

Integration tests must use PostgreSQL.

Do not substitute SQLite for database integration tests.

Pure parsing/extraction utilities may use normal unit tests without DB access.

---

## 84. Transaction Testing

The existing project has already used PostgreSQL transaction fixtures with SAVEPOINT-compatible behavior.

Where nested transaction behavior is required, inspect existing patterns such as:

```python
join_transaction_mode="create_savepoint"
```

Do not invent a different testing transaction strategy without need.

---

## 85. Do Not Redesign Completed Architecture

A developer working on document ingestion should not redesign:

```text
job ingestion
job normalization
matching
CandidateProfileRepository
CandidateProfileService
CandidateManagementService
CandidatePopulationService
```

The document pipeline sits upstream of canonical candidate truth.

---

## 86. Merge Safety

Prefer implementation in a dedicated package such as:

```text
src/candidate_ingestion/
```

and focused tests such as:

```text
tests/test_candidate_ingestion_*.py
```

Database migrations should only be added if the existing schema is genuinely insufficient.

Inspect existing document-ingestion models first.

---

## 87. Branch Recommendation

A separate branch is recommended.

Example:

```bash
git checkout -b resume-ingestion
```

The main branch can continue downstream development independently.

When implementation is ready:

```text
run focused tests
run full tests
run git diff --check
inspect git status/diff
open pull request or merge
```

---

## 88. Merge Expectations

A resume-ingestion branch should ideally integrate without requiring downstream changes.

The final result of successful ingestion should still be:

```text
CanonicalCandidateProfile
```

Therefore:

```text
MatchingService
Resume Tailoring
Application Workflow
```

should not need to know how the candidate facts entered the profile.

---

## 89. Definition of Done — Initial Resume Ingestion

The first production-worthy version should not be considered complete until:

- source documents are immutable
- duplicate uploads are detected
- parsing is versioned
- structured facts are extracted
- extracted facts remain separate from canonical truth
- canonical comparison exists
- duplicate facts are reconciled
- conflicts are explicit
- silent overwrites are impossible
- approved facts can reach canonical truth
- evidence/provenance is preserved
- failed writes rollback atomically
- missing resume fields are safe
- multiple resumes per candidate work
- multiple candidates work
- candidate isolation is tested
- PostgreSQL integration tests pass
- full repository tests pass
- no private candidate documents are committed
- completed architecture is not unnecessarily redesigned

---

## 90. Definition of Done — Mature Resume Ingestion

A later mature version may additionally support:

- multiple document formats
- LLM structured extraction
- extraction confidence
- automatic safe reconciliation
- human conflict-review workflow
- parser versioning
- extractor versioning
- prompt/model versioning
- candidate-profile version snapshots
- audit-log integration
- richer evidence locators
- source-document lifecycle management
- batch document processing

These are enhancements beyond the first usable ingestion pipeline.

---

## 91. Permanent Rules

The following rules should remain true even as implementation evolves.

```text
Source documents are evidence, not canonical truth.

Extracted facts are proposals, not canonical truth.

Conflicts must never be silently overwritten.

Generated resume content must never automatically become canonical truth.

Canonical writes must preserve provenance.

Downstream systems consume CanonicalCandidateProfile.

Document ingestion must remain candidate-agnostic.

Private candidate documents must not be committed.

Missing fields must not break ingestion.

Do not invent candidate facts or false date precision.
```

---

## 92. Current Project Decision

The current project is not implementing resume/document ingestion immediately.

The main branch will continue downstream using the already populated canonical candidate profiles.

Document ingestion is intentionally being separated into an independent enhancement track.

The intended future flow is:

```text
Multiple Candidate Documents
        ↓
Immutable Sources
        ↓
Parsing
        ↓
Structured Extraction
        ↓
Deduplication / Reconciliation
        ↓
Conflict Review
        ↓
Approved Canonical Writes
        ↓
Evidence
        ↓
CanonicalCandidateProfile
```

A developer can implement this pipeline independently as long as the canonical candidate-profile boundary remains intact.

The main branch should then be able to merge the completed ingestion work without redesigning matching, resume tailoring, or other downstream systems.