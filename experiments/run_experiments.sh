#!/usr/bin/env bash
# Real collection only. No fallback to fixtures. Run from project root.
set -euo pipefail
: "${DEMO_MODEL:?Set DEMO_MODEL to a model actually listed by your configured agent}"
AGENT="${DEMO_AGENT:-opencode}"
if [[ "$AGENT" != opencode && "$AGENT" != pi ]]; then
  echo 'DEMO_AGENT must be opencode or pi' >&2; exit 2
fi
command -v "$AGENT" >/dev/null || { echo "$AGENT not installed; live collection blocked" >&2; exit 3; }
PYTHON="${PROVENANCE_PYTHON:-.venv/bin/python}"
TRIAL="${1:?Supply a fresh trial name, e.g. trial-001}"
if [[ ! "$TRIAL" =~ ^[A-Za-z0-9_-]+$ ]]; then echo 'Use a plain trial name' >&2; exit 2; fi
BASE="artifact/runs/$TRIAL"
mkdir "$BASE"
RESULTS="results/$TRIAL"
mkdir "$RESULTS"
for SCENARIO in normal tool-output-injection; do
  RUN="$BASE/$SCENARIO"
  "$PYTHON" artifact/scripts/prepare.py "$SCENARIO" --output "$RUN"
  set +e
  "$PYTHON" artifact/scripts/collect.py "$AGENT" "$RUN" --model "$DEMO_MODEL"
  COLLECT_STATUS=$?
  "$PYTHON" artifact/scripts/check.py "$RUN"
  CHECK_STATUS=$?
  set -e
  echo "collector=$COLLECT_STATUS independent_check=$CHECK_STATUS" > "$RESULTS/$SCENARIO-status.txt"
  if [[ -f "$RUN/events.jsonl" ]]; then
    "$PYTHON" -m provenance.cli analyze --run "$RUN" --output "$RESULTS/$SCENARIO"
  else
    echo 'No trajectory; collector preflight failed. No analysis substituted.' >&2
  fi
done
if [[ -f "$RESULTS/normal/analysis.json" && -f "$RESULTS/tool-output-injection/analysis.json" ]]; then
  "$PYTHON" -m provenance.cli compare --baseline "$RESULTS/normal/analysis.json" --injected "$RESULTS/tool-output-injection/analysis.json" --output "$RESULTS/comparison.md"
fi
