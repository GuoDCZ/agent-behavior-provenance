# Remaining limitations

Live collection is blocked: OpenCode and Pi are absent from PATH, and environment
status reports no credential bindings. No model/version, trajectory, live attack
outcome or matched trial is claimed. Installing a CLI alone would not supply a
configured model. Real validation must use the commands in README with provider
credentials configured outside the repository. The missing course PDFs and
brainstorming document should be checked by the team before formal submission.

The analyzer's parser contracts are synthetic-tested, not validated against real
agent versions. Pi start/end-only tool events are retained as opaque observations;
full call arguments are obtained from assistant message-end records when present.
No requests are invented. Timestamps from JSONL top-level records are retained
when present, but export order is the analysis ordering; nested timestamps are
not reconstructed. Multiple native schemas and partial streamed arguments may
need additional adapters once a real sample exists. A final text event after
calls is a completion-report candidate, not proof that execution finished.

No OS instrumentation or per-tool file snapshots are installed. Consequently
shell edits, patch payload paths, multiedit targets, symlink aliases, transient
edits, exact write attribution and hidden accesses may escape activity analysis.
Final snapshot comparisons still detect persisted protected changes visible in
the workspace. A stale check.json is retained independently, not overwritten;
its integrity findings are unioned with current snapshot findings, so users must
inspect timestamps/raw checks before interpreting disagreements. The analyzer
cannot authenticate logs or snapshots. It is an evidence organizer, not a monitor
that enforces permissions.

Exact payload matching can miss transformations and truncations. Existing native
result records do not by themselves prove model visibility. Public-test claim
assessment remains conservative: the independent oracle tests correctness but
cannot establish whether the separate public tests really passed.

All possible earlier outputs are retained as uncertain candidates. Large runs
will encounter quadratic possible-edge growth and crowded SVGs. Additional
instrumentation, paged views and explicit request/result correlation would help.
No empirical investigation-burden reduction or detection accuracy is established.

Counterfactual ablation is deferred because no actual model replay is available.
There is no mock replay oracle. Future real ablations should replace only runner
notes, preserve prompt/workload/test semantics, use matched initial states and
settings, retain real events and repeat to measure variability. Any difference
would support an influence hypothesis, not identify a sole cause mathematically.

Students must write their own required non-AI executive summary and truthful
individual contribution statements. This repository provides factual implementation
and test evidence only.
