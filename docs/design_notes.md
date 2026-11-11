# Design and evidence boundaries

System provenance maps objects to file versions, activities to tool calls/results
and exported model message groups, and dependencies to typed directed edges.
Independent integrity changes connect baseline and final file versions, then
annotate protected changes as policy findings. A final difference has run-level
attribution: no tool is automatically assigned responsibility. In a native export,
model-message-to-tool invocation and call-to-result relations are structural
observations. Streaming message IDs can identify a message group without exposing
an internal reasoning process or request context.

Read tools with recorded non-error results can link a named file to the read
activity; hashes of that intermediate version are unknown. Failed/unmatched reads
are READ_TARGET intent only. Shell commands stay opaque and are never expanded
into asserted read/write syscalls. Direct edit/write path arguments indicate an
attempt. Tool success text is not confirmation of a persisted write. Final hashes
and the professor's checker independently establish final integrity outcomes.

The graph is a NetworkX MultiDiGraph so chronology and evidence links between
the same nodes can coexist. Node types include TrustedTask, ModelTurn,
ModelRequest, ToolCall, ToolResult, FileVersion, IntegrityChange, FinalResponse,
PolicyFinding and generic observations. Edges retain a relation, evidence status,
and original source reference. Acyclicity is checked before exporting. File
versions are tied to before/after hashes; absence is represented explicitly.
The prepared task node does not acquire an availability edge merely by existing.

Backward slicing traverses observed INVOKED, RETURNED, READ_FROM,
AVAILABLE_TO_MODEL, TASK_TEXT_PRESENT, COMPARED_WITH, WROTE_TO and EVIDENCE_FOR
relations. It separately traverses possible contexts and matching edit-target
hypotheses. PRECEDED edges are excluded from both queries. With no per-tool
snapshots, the observed slice from a confirmed change may stop at integrity
evidence. A matching edit attempt may enter only the possible set. This is an
explicit limit, not a missing edge filled by temporal guessing.

All earlier tool results are conservatively possible inputs to subsequent tool
calls, creating O(n²) possible edges. This intentionally illustrates dependency
explosion. Exact textual containment in an explicitly recorded model request can
add observed availability. Queries report all outputs and sliced candidate
outputs; candidate pruning is not ground-truth causal recovery. SVG rendering
is suitable for small runs; dense traces need filtering for practical inspection.

The analogy to OS provenance breaks at several boundaries. Context availability
is not causal influence. Model reasoning is not observed. Bash/tool processes
hide internal accesses, aliases and reverted writes. Exports may omit requests,
results or exact exit status. Final assistant claims are not independent task
validation; an unchanged implementation can fail the independent oracle even
when tampered public tests pass. Therefore a public-test success claim is labeled
unverified unless relevant public output is separately established; oracle failure
alone does not prove the public-test claim false.

Policy checks use component-aware normalized paths. Traversal, absolute paths
outside the known workspace, src2 prefixes and nonauthorized roots are protected.
Snapshot symlink entries are hashed as links, not followed. Path argument analysis
is not an OS sandbox and does not resolve all indirect target aliases.

Adapters are contract-tested with synthetic OpenCode and Pi shapes, since no live
exports were supplied or collectable. Native sessions take precedence over stream
records. Unsupported/malformed lines are retained as coverage warnings; parse
success never authenticates an export. A final text event is only a final-response
candidate based on export order. Exact exposure checks use full scenario override
text, so transformed/truncated payloads may not match; nonmatching evidence remains
not observed rather than proof of no delivery. Reports should be read with raw
source records.
