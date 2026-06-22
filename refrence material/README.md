# Kaggle Agent Reference Library

This is the entry point for humans and LLMs. For implementation work, start with the [`implementation_specs` index](reference_texts/implementation_specs/README.md). For broader research, use [`reference_texts/SUMMARY_INDEX.md`](reference_texts/SUMMARY_INDEX.md).

## Directory map

```text
refrence material/
├── README.md                 # Start here
├── reference_texts/          # Searchable, low-token source material
│   ├── SUMMARY_INDEX.md      # Topic router and canonical knowledge index
│   ├── implementation_specs/ # Primary code-and-logic documents
│   ├── capstone/             # Rules, requirements, and project notes
│   ├── whitepapers/          # Course concepts and architecture
│   └── codelabs/             # Extracted step-by-step lab instructions
├── codelabs/                 # Runnable lab projects, specs, and lab originals
│   └── README.md             # Project and implementation-spec index
└── source_documents/         # PDFs and RTF/RTFD originals; use only when needed
    ├── capstone/
    └── whitepapers/
```

## LLM retrieval order

1. For code or architecture work, read `reference_texts/implementation_specs/README.md`.
2. Read the relevant implementation spec; these are the primary reusable documents.
3. Inspect only the source-code files named by that spec.
4. Use `reference_texts/SUMMARY_INDEX.md` to find supporting course material.
5. Read one or two targeted extracted-text files rather than the whole library.
6. Open a PDF or RTF/RTFD only when visual context matters.

## Search guidance

Prefer `reference_texts/` for conceptual searches and `codelabs/` for code searches. Exclude generated or dependency directories:

```bash
rg "search term" "refrence material/reference_texts"
rg "search term" "refrence material/codelabs" \
  -g '!**/.venv/**' -g '!**/__pycache__/**' \
  -g '!**/.pytest_cache/**' -g '!**/.ruff_cache/**'
```

The top-level folder retains its existing spelling (`refrence material`) to avoid breaking project and IDE paths.
