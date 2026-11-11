# Implementation execution record

Implemented in `/workspace/work/project` using the uploaded professor artifact.
This is a factual implementation record, not the team's required executive summary.

## Completed and blocked phases

| Phase | Status | Evidence |
|---|---|---|
| 1: Inspect/validate | Complete for supplied materials | README/task/scripts/scenarios/workload/debugging skill inspected; original helper and workload tests run; archive source hashes verified; prepare isolation verified |
| 2: Real matched collection | Blocked | Python 3.12.14 available; `opencode` and `pi` absent from PATH; managed environment reports zero credential bindings; no model/version or trajectory claimed |
| 3: Parser | Implemented; live schema validation pending | OpenCode JSONL/native and Pi message-end contract fixtures, malformed coverage warnings, refs/order, recorded timestamps when available |
| 4: Graph/query | Implemented and locally tested | NetworkX DAG assertion, typed edges with evidence status, JSON/GraphML/SVG, observed/possible backward queries, chronology excluded |
| 5: Policy | Implemented and locally tested | Hash snapshots, checker findings, protected edit attempts, independent correctness and conservative completion-claim assessment |
| 6: Evaluation | Local infrastructure complete; live comparison blocked | Two unexecuted snapshot reports; comparison explicitly states no agent experiments; separately labeled synthetic examples |
| 7: Ablation | Deferred | No real model replay; no mock causal results |
| 8: Documentation | Complete for implementation | README, protocol, design notes, limitations, this record, actual test logs |

## Actual verification results

Final reproduction command:

```bash
.venv/bin/python experiments/run_local.py \
  --runs artifact/runs/release-validation --results results/release-validation
```

- Professor helper suite: **18/18 passed**, exit 0.
- Analyzer suite: **19/19 passed**, exit 0.
- Original public workload: **3/5 passed, 2 expected failures**, exit 1.
- Each fresh, unexecuted normal/injection workspace: **no final protected changes**;
  independent oracle **failed** (mixed, refund-only and cents fail; six other
  independent cases pass). Checker exit 1 is verified as expected initial behavior.
- Professor source files are unchanged from the provided archive. Local preparation
  and checks do not mutate source workload/skill templates.
- GraphML reload and DAG checks, SVG XML validation, CLI invalid-input/help,
  observed/possible query behavior and byte-identical repeated export tests pass.

The application adds amounts regardless of charge/refund kind. Public tests
correctly expect 120 minus 20 = 100 and refund-only balance -5.50. This prototype
does not pre-repair the original workload, because real coding-agent trials must
start with that bug. No protected tests were changed to produce an apparent attack.

## Files and outputs

New source: `provenance/{schema,parser,policy,graph,slice,report,visualize,cli}.py`.
Tests: `tests/test_provenance.py`, synthetic fixture generator and fixture README.
Experiments: offline reproduction command and real-collection shell driver.
Docs: root README, protocol, Module 2 design notes and limitations.

Authoritative generated outputs are in `results/release-validation/`: test logs,
environment metadata, independent-check logs, before/after source integrity,
snapshot-only `normal-001/` and `tool-output-001/` analyses, comparison, CLI help,
and a query example. Synthetic demonstrations occupy their own named subdirectory;
raw synthetic inputs remain under `artifact/runs/release-validation/synthetic-fixtures/`.
Earlier local-validation directories are development runs, not additional trials.

Each analysis emits `analysis.json`, `analysis.md`, `graph.graphml`, `graph.json`
and `graph.svg`. Missing real logs are never replaced automatically by fixtures.
Snapshot reports have `run_status=uncollected` and zero trajectory events. No
experimental success rate, exposure rate, causal verification, or burden reduction
has been measured.

## Remaining work and limits

Install/authenticate a supported OpenCode or Pi agent externally, confirm a real
model, then run `experiments/run_experiments.sh` with a fresh trial name. Validate
the adapters against that actual export before drawing behavioral conclusions.
Review the missing `Project.pdf`, `project-guide.pdf` and `project_a.md` independently.

Without per-tool snapshots or OS tracing, final changes cannot be uniquely assigned
to an edit call. Shell internals, indirect edits and transient changes remain opaque.
Model message groups are not request contexts, and context availability does not
prove influence. Full payload matching may miss truncated/transformed text.
Public-test success claims are not established merely by oracle correctness.
See `docs/limitations_and_future_work.md` for all supported boundaries.

The prescribed chat output location `/codex/browser/projectless/0001-files-mentioned-by-the-user-uploaded-file-pointe/output`
is absent in the attached runtime; creating it returns `Read-only file system`.
The complete project and a portable archive are retained in the shared workspace
instead. This affects download presentation, not execution or local results.
