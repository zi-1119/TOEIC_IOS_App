import collections
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path('/Users/ziii/Desktop/TOEIC_IOS_App')
validator = Draft202012Validator(json.loads((root / 'specs/group.schema.json').read_text()))
for n in range(1, 11):
    batch = f'batch-ag-{n:04}'
    groups = [json.loads(line) for line in (root / 'exports' / batch / 'groups.jsonl').read_text().splitlines()]
    errors = [(g['group_id'], e) for g in groups for e in validator.iter_errors(g)]
    counts = collections.Counter(e.message for _, e in errors)
    missing_evidence_items = sum(any('reasoning_zh' not in ev for ev in item['evidence']) for g in groups for item in g['items'])
    print(json.dumps({'batch': batch, 'groups': len(groups), 'invalid_groups': len({gid for gid, _ in errors}), 'schema_errors': len(errors), 'missing_evidence_reason_items': missing_evidence_items, 'error_categories': counts}, ensure_ascii=False))
