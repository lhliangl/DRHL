# test_extract

This directory is an isolated harness for testing DRHL access-control source
extraction. It calls the same `_analyze_source` entry point used by the DRHL
`analyze-source` command, including `llm_snippets.json` compaction, but replaces
the configured formal `run_dir` with `test_extract/runs/<app>`.

Run it from the repository root:

```powershell
python test_extract\extract.py --config configs\jsforum.json
```

To force CST output:

```powershell
python test_extract\extract.py --config configs\jsforum.json --save-cst
```

Artifacts are written only below `test_extract/runs/<app>`:

- `config.json`
- `database/baseline.sql`, when the formal run already contains one; it is
  copied read-only as input to source analysis
- `source/candidate_parameters.json`
- `source/candidate_functions.json`
- `source/parameters.json`
- `source/functions.json`
- `source/snippets.json`
- `source/llm_snippets.json`
- `source/cst.json`, when CST output is enabled
- `summary.json`

The harness does not crawl the application, connect to or modify its database,
run vulnerability detection, invoke an LLM, or run repair. It does not write to
the configured formal `runs/<app>` directory.

Every extraction, including `evaluate.py --no-extract`, asserts the complete
artifact chain: every validated parameter/function ID must be referenced by
`snippets.json`; every snippet must reference only validated IDs; and
`llm_snippets.json` must retain every distinct `(path, selected code)` context
using only `path` plus `if_framework` (preferred) or `code`. Provenance IDs stay
in `snippets.json` and are intentionally omitted from the LLM input. Evaluation
stops immediately if any stage is inconsistent.

## Batch evaluation

The following command extracts every configured application and evaluates the
validated parameters and functions against the manually reviewed files in
`test_extract/ground_truth`:

```powershell
D:\Anaconda3\envs\drhl\python.exe test_extract\evaluate.py
```

It writes `extraction_metrics.md`, `evaluation.json`, and all per-application
artifacts only inside `test_extract`.

To recalculate only the metrics from existing isolated outputs:

```powershell
D:\Anaconda3\envs\drhl\python.exe test_extract\evaluate.py --no-extract
```
