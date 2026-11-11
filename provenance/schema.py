"""Normalized evidence records; raw content stays out of public reports."""
from dataclasses import dataclass, asdict

@dataclass
class Event:
    event_id: str
    order: int
    kind: str
    source_ref: str
    text: str = ''
    tool_name: str = ''
    call_id: str = ''
    turn_id: str = ''
    path: str = ''
    command: str = ''
    status: str = 'recorded'
    exit_code: int | None = None
    timestamp: str = ''

    def public(self):
        record = asdict(self)
        record['content_excerpt'] = record.pop('text')[:240]
        return record
