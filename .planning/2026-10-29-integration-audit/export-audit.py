"""Read-only integrity and media probe for ten producer batches."""
import collections
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess

root = Path('/Users/ziii/Desktop/TOEIC_IOS_App')
latest = {}
file_count = 0
for n in range(1, 11):
    folder = root / 'exports' / f'batch-ag-{n:04}'
    manifest = json.loads((folder / 'manifest.json').read_text())
    for entry in manifest['files']:
        assert hashlib.sha256((folder / entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
        file_count += 1
    for line in (folder / 'groups.jsonl').read_text().splitlines():
        group = json.loads(line)
        if group['version'] >= latest.get(group['group_id'], ({'version': 0}, None))[0]['version']:
            latest[group['group_id']] = (group, folder)

pools = collections.Counter()
statuses = collections.Counter()
families = collections.defaultdict(set)
audio = []
photos = 0
for group, folder in latest.values():
    pools[group['pool']] += len(group['items'])
    statuses[group['content_status']] += len(group['items'])
    families[group['family_id']].add(group['pool'])
    for asset in group['assets']:
        assert asset['status'] == 'ready', asset['asset_id']
        path = folder / asset['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256']
        if asset['kind'] == 'audio':
            assert {s['segment_id'] for s in asset['segment_times']} == {s['segment_id'] for s in group['stimulus']['audio_script']}
            audio.append(path)
        else:
            photos += 1
assert all(len(p) == 1 for p in families.values())

def probe(path):
    data = json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'json', str(path)]))
    assert float(data['format']['duration']) > 0
    assert any(s['codec_type'] == 'audio' for s in data['streams'])
    return path.name

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    checked = list(pool.map(probe, audio))
print(json.dumps({'manifest_files': file_count, 'groups': len(latest), 'items_by_pool': pools, 'content_status': statuses, 'audio_probed': len(checked), 'photos': photos, 'cross_pool_family_conflicts': 0}, ensure_ascii=False, indent=2))
