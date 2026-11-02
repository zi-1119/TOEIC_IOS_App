"""Read-only audit of exported manifests, active metadata and actual media."""
import collections
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess

root = Path('/Users/ziii/Desktop/TOEIC_IOS_App')
latest = {}
file_count = 0
for number in range(1, 8):
    batch = root / 'exports' / f'batch-ag-{number:04}'
    manifest = json.loads((batch / 'manifest.json').read_text())
    for entry in manifest['files']:
        path = batch / entry['path']
        assert path.is_file(), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
        file_count += 1
    for line in (batch / 'groups.jsonl').read_text().splitlines():
        group = json.loads(line)
        if group['version'] >= latest.get(group['group_id'], ({'version': 0}, None))[0]['version']:
            latest[group['group_id']] = (group, batch)

audio = []
images = []
blind_matches = 0
statuses = collections.Counter()
pools = collections.Counter()
difficulties = collections.Counter()
for group, batch in latest.values():
    n = len(group['items'])
    statuses[group['content_status']] += n
    pools[group['pool']] += n
    difficulties[group['difficulty']['level']] += n
    blind = {x['item_id']: x for x in json.loads((batch / 'reports/blind-solve.json').read_text())['items']}
    for item in group['items']:
        assert blind[item['item_id']]['selected_choice_id'] == item['answer_choice_id']
        blind_matches += 1
    for asset in group['assets']:
        assert asset['status'] == 'ready', asset['asset_id']
        path = batch / asset['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256'], path
        if asset['kind'] == 'audio':
            audio.append((group, asset, path))
        else:
            images.append(str(path))

def check_audio(entry):
    group, asset, path = entry
    actual = json.loads(subprocess.check_output([
        '/opt/homebrew/bin/ffprobe', '-v', 'error', '-show_entries',
        'format=duration:stream=codec_name,codec_type', '-of', 'json', str(path)
    ]))
    duration = float(actual['format']['duration']) * 1000
    delta = abs(duration - asset['duration_ms'])
    # Record container duration differences; the 100 ms mock-form rule is not
    # a group-audio acceptance rule. AAC padding may explain this discrepancy.
    assert any(x['codec_type'] == 'audio' for x in actual['streams'])
    timings = asset['segment_times']
    assert {x['segment_id'] for x in timings} == {x['segment_id'] for x in group['stimulus']['audio_script']}
    previous = 0
    for segment in timings:
        assert previous <= segment['start_ms'] < segment['end_ms'] <= asset['duration_ms']
        previous = segment['end_ms']
    return {'file': path.name, 'duration_ms': round(duration), 'delta_ms': round(delta, 3)}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    audio_checks = list(executor.map(check_audio, audio))

print(json.dumps({
    'manifest_file_hashes_checked': file_count,
    'active_groups': len(latest), 'active_item_status': statuses, 'active_pools': pools,
    'editorial_difficulty': difficulties, 'blind_record_matches': blind_matches,
    'audio_checked': len(audio_checks),
    'maximum_duration_error_ms': max(x['delta_ms'] for x in audio_checks),
    'container_differences_above_100ms': [x for x in audio_checks if x['delta_ms'] > 100],
    'photos': images,
    'notes': 'Matching blind records do not independently prove isolated contexts or audio listening QA.'
}, ensure_ascii=False, indent=2))
