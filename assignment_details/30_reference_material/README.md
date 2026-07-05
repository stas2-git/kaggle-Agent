# Reference Material

This is the course and codelab reference pyramid. Start with the extracted guides for a high-level view, then drill into searchable source text or runnable codelab projects only when needed.

## Start Here

1. [`10_extracted_guides/README.md`](10_extracted_guides/README.md) - read order for the high-level guide layer.
2. [`10_extracted_guides/00_capstone_baseline_expectations.md`](10_extracted_guides/00_capstone_baseline_expectations.md) - minimum expected capstone quality bar.
3. [`10_extracted_guides/01_course_concepts.md`](10_extracted_guides/01_course_concepts.md) - what the course covered.
4. [`10_extracted_guides/02_codelab_lessons.md`](10_extracted_guides/02_codelab_lessons.md) - what the codelabs taught and what this project reused.
5. [`10_extracted_guides/03_submission_requirements.md`](10_extracted_guides/03_submission_requirements.md) - what Kaggle expects for the final submission.
6. [`20_searchable_reference_texts/SUMMARY_INDEX.md`](20_searchable_reference_texts/SUMMARY_INDEX.md) - router into extracted source material.
7. [`30_runnable_codelab_projects/README.md`](30_runnable_codelab_projects/README.md) - runnable codelab copies and implementation specs.

## Directory Map

```text
assignment/30_reference_material/
├── 10_extracted_guides/          # Human-readable course and submission summaries
├── 20_searchable_reference_texts/# Searchable extracted text for LLM retrieval
├── 30_runnable_codelab_projects/ # Runnable codelab workspaces and lab originals
└── 90_source_documents/          # PDF and rich-text originals
```

## LLM Retrieval Order

1. Start with `10_extracted_guides/00_capstone_baseline_expectations.md`.
2. Read the other guides in `10_extracted_guides/` for course, codelab, and submission expectations.
3. For code or architecture work, read `20_searchable_reference_texts/implementation_specs/README.md`.
4. Read the relevant implementation spec.
5. Inspect only the source files named by that spec.
6. Use `20_searchable_reference_texts/SUMMARY_INDEX.md` for supporting course material.
7. Open originals in `90_source_documents/` only when formatting or images matter.

## Search Guidance

Prefer `20_searchable_reference_texts/` for conceptual searches and `30_runnable_codelab_projects/` for code searches. Exclude generated or dependency directories:

```bash
rg "search term" "assignment/30_reference_material/20_searchable_reference_texts"
rg "search term" "assignment/30_reference_material/30_runnable_codelab_projects" \
  -g '!**/.venv/**' -g '!**/__pycache__/**' \
  -g '!**/.pytest_cache/**' -g '!**/.ruff_cache/**'
```
