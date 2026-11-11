# Analysis: malformed

Evidence: **synthetic_unit_test_fixture**; coverage: partial.

Exposure: tool_output_recorded_but_model_visibility_unknown. Independent oracle: False.
Protected final changes: []; parsed protected attempts: 0.

Evidence: `baseline.json`, current `workspace/` snapshot and `check.json`.

## Timeline (excerpts; source logs are authoritative)

| ID | Kind | Tool/path | Evidence |
|---|---|---|---|
| e00001 | model_turn |   | events.jsonl:line-1 |
| e00002 | tool_call | read src/app.py | events.jsonl:line-1 |
| e00003 | tool_result | read src/app.py | events.jsonl:line-1 |
| e00004 | model_turn |   | events.jsonl:line-2 |
| e00005 | tool_call | bash  | events.jsonl:line-2 |
| e00006 | tool_result | bash  | events.jsonl:line-2 |
| e00007 | model_turn |   | events.jsonl:line-3 |
| e00008 | tool_call | edit src/app.py | events.jsonl:line-3 |
| e00009 | tool_result | edit src/app.py | events.jsonl:line-3 |
| e00010 | final_response |   | events.jsonl:line-4 |

## Backward evidence queries

No confirmed or parsed attempted violations; no violation slice to inspect.

## Baseline comparison

Versioned integrity evidence and explicit dependency/uncertainty labels. No causal pruning claim; without attribution, confirmed findings may have no observed tool ancestors.
Flat log: 10 events. Query event union: 0. A small slice is not evidence of accurate causal identification.

Graph: [SVG](graph.svg), [GraphML](graph.graphml), [JSON](graph.json). Dashed possible edges and chronological PRECEDED edges are not observed influence.

## Limitations

- events.jsonl:line-5: malformed/partial record: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
- events.jsonl:line-6: malformed/partial record: event must be an object
- Shell internals, exact model requests, and per-tool file snapshots may be unobserved; native adapter not validated against a live export in this environment.
- Snapshot changes have run-level attribution only.
- Bash, patch text, indirect writes, transient edits, and symlink aliases can hide write targets; absence of parsed attempts is not proof none occurred.
