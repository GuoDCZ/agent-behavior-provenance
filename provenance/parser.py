"""Conservative adapters for OpenCode JSON stream/native messages and Pi JSON.

Native layouts are tested against synthetic contract fixtures, NOT live exports.
Explicit `model_request` is an optional instrumentation envelope, not a claim
that OpenCode/Pi exports include requests. Tool results alone do not prove delivery.
"""
import json
from pathlib import Path
from .schema import Event


def text_content(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '\n'.join(text_content(v) for v in value)
    if isinstance(value, dict):
        return text_content(value.get('text', value.get('content', '')))
    return ''


def parse(run, snapshot_only=False):
    run = Path(run)
    events, warnings = [], []
    def emit(kind, ref, **fields):
        events.append(Event(f'e{len(events)+1:05d}', len(events)+1, kind, ref, **fields))
    def tool(part, ref, turn=''):
        state = part.get('state') or {}
        if not isinstance(state, dict):
            raise ValueError('tool state must be an object')
        args = state.get('input', part.get('arguments', part.get('input', {}))) or {}
        if not isinstance(args, dict):
            warnings.append(f'{ref}: tool arguments are opaque')
            args = {}
        common = dict(tool_name=str(part.get('tool', part.get('name', ''))),
                      call_id=str(part.get('callID', part.get('id', ''))), turn_id=turn,
                      path=str(args.get('filePath', args.get('path', args.get('file_path', '')))),
                      command=str(args.get('command', '')))
        emit('tool_call', ref, text=json.dumps(args, sort_keys=True), status=str(state.get('status', 'recorded')), **common)
        if 'output' in state or state.get('status') == 'error':
            meta = state.get('metadata') or {}
            emit('tool_result', ref, text=text_content(state.get('output', state.get('error', ''))),
                 status=str(state.get('status', 'recorded')),
                 exit_code=meta.get('exitCode') if isinstance(meta, dict) else None, **common)

    def message(msg, parts, ref):
        role = msg.get('role', '')
        turn = str(msg.get('id', msg.get('messageID', '')))
        if role == 'assistant':
            emit('model_turn', ref, turn_id=turn)
        if role == 'toolResult':
            emit('tool_result', ref, text=text_content(msg.get('content', '')),
                 tool_name=str(msg.get('toolName', '')), call_id=str(msg.get('toolCallId', '')),
                 status='error' if msg.get('isError') else 'recorded')
            return
        for i, p in enumerate(parts):
            if not isinstance(p, dict):
                warnings.append(f'{ref}: non-object message part'); continue
            pref = f'{ref}/parts/{i}'
            if p.get('type') in ('tool', 'toolCall'):
                tool(p, pref, turn)
            elif p.get('type') == 'text':
                emit('assistant_text' if role == 'assistant' else 'user_message', pref,
                     turn_id=turn, text=text_content(p))

    # Prefer one source to avoid double-counting stream and native session events.
    native = run / 'session.json'
    data = None
    if native.is_file():
        try:
            data = json.loads(native.read_text())
        except (ValueError, UnicodeError):
            warnings.append('session.json: invalid JSON; falling back to events.jsonl')
    if isinstance(data, dict) and isinstance(data.get('messages'), list) and data['messages']:
        for i, m in enumerate(data['messages']):
            ref = f'session.json:/messages/{i}'
            try:
                message(m.get('info', m), m.get('parts', []), ref)
            except (ValueError, TypeError, AttributeError) as err:
                warnings.append(f'{ref}: {err}')
        source = 'opencode_native_contract'
    else:
        stream = run / 'events.jsonl'
        if not stream.is_file():
            if not snapshot_only:
                raise ValueError('Missing events.jsonl and usable session.json; collect a real run or use --snapshot-only for integrity analysis without trajectories')
            return [], ['No trajectory: explicit snapshot-only analysis; no agent behavior or exposure observed.'], 'snapshot_only'
        source = 'jsonl_stream_contract'
        seen_turns=set()
        for line, raw in enumerate(stream.read_bytes().splitlines(), 1):
            if not raw.strip(): continue
            ref = f'events.jsonl:line-{line}'
            try:
                obj = json.loads(raw)
                if not isinstance(obj, dict): raise ValueError('event must be an object')
                typ = obj.get('type')
                start=len(events)
                part=obj.get('part')
                mid=str(part.get('messageID', '')) if isinstance(part,dict) else ''
                if typ in ('tool_use','text') and mid and mid not in seen_turns:
                    emit('model_turn',ref,turn_id=mid,text='Export message grouping only; no model request observed')
                    seen_turns.add(mid)
                if typ == 'tool_use':
                    part = obj.get('part', {})
                    tool(part, ref, str(part.get('messageID', '')))
                elif typ == 'text':
                    emit('assistant_text', ref, text=text_content(obj.get('part', {})), turn_id=str(obj.get('part', {}).get('messageID', '')))
                elif typ == 'message_end':
                    m = obj.get('message', {})
                    message(m, m.get('content', []), ref)
                elif typ == 'tool_execution_start':
                    # Prefer completed Pi messages when present; start/end fallback
                    # is intentionally not merged with message_end without an ID.
                    emit('tool_start', ref, call_id=str(obj.get('toolCallId', '')), tool_name=str(obj.get('toolName', '')))
                elif typ == 'tool_execution_end':
                    emit('tool_end', ref, call_id=str(obj.get('toolCallId', '')), tool_name=str(obj.get('toolName', '')), text=text_content(obj.get('result', {})))
                elif typ == 'model_request' and isinstance(obj.get('messages'), list):
                    emit('model_request', ref, text='\n'.join(text_content(m.get('content', '')) for m in obj['messages'] if isinstance(m, dict)), turn_id=str(obj.get('id', '')))
                elif typ == 'error':
                    emit('execution_error', ref, text=json.dumps(obj, sort_keys=True))
                elif typ not in ('step_start','step_finish','start','agent_start','agent_end','turn_start','turn_end','message_start','message_update'):
                    warnings.append(f'{ref}: unsupported event type {typ!r}')
                for e in events[start:]:
                    e.timestamp=str(obj.get('timestamp', ''))
            except (ValueError, TypeError, AttributeError, UnicodeError) as err:
                warnings.append(f'{ref}: malformed/partial record: {err}')
    if not events:
        warnings.append('No supported behavioral events parsed')
    # Only the last assistant text without a later call is a final response candidate.
    texts = [e for e in events if e.kind == 'assistant_text']
    if texts and not any(e.kind == 'tool_call' and e.order > texts[-1].order for e in events):
        texts[-1].kind = 'final_response'
    warnings.append('Shell internals, exact model requests, and per-tool file snapshots may be unobserved; native adapter not validated against a live export in this environment.')
    return events, warnings, source
