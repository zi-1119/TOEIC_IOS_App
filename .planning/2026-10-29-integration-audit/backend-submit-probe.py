"""Local-only regression probe with synthetic accounts and temporary SQLite."""
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import uuid

spec = importlib.util.spec_from_file_location('audit_local_server', '/Users/ziii/Desktop/TOEIC_IOS_App/Backend/local_server.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='TOEIC-submit-probe-') as folder:
    app = module.App(SimpleNamespace(state=str(Path(folder) / 'state.sqlite'), catalog=None, battle_seconds=600, public_client_id='audit', test_mode=True, verbose=False))
    for n in (1, 2):
        app.store.execute('insert into battle_catalog values(?,?,?,?,?,?)', ('audit-version', 'audit-group', f'audit-item-{n}', n, 'B', 'battle'))
    app.store.commit()
    server = module.ThreadingHTTPServer(('127.0.0.1', 0), module.Handler)
    server.app = app
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_address[1]}'
    def post(path, body=None, token=None):
        body = {'requestID': str(uuid.uuid4()), **(body or {})}
        headers = {'Content-Type': 'application/json', 'X-Public-Client-ID': 'audit'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        req = Request(base + path, data=json.dumps(body).encode(), headers=headers, method='POST')
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)
    def login(email):
        assert post('/v1/auth/request-code', {'email': email})[0] == 200
        status, result = post('/v1/auth/verify', {'email': email, 'code': '246810'})
        assert status == 200
        return result['accessToken'], result['identity']['userID']
    try:
        alice, alice_id = login('audit-a@example.test')
        bob, bob_id = login('audit-b@example.test')
        _, invite = post('/v1/friends/invites', token=alice)
        assert post('/v1/friends/accept', {'code': invite['url'].rsplit('/', 1)[1]}, bob)[0] == 200
        status, match = post('/v1/battles', {'opponentID': bob_id, 'groupIDs': ['audit-group']}, alice)
        assert status == 200
        path = '/v1/battles/' + match['id']
        assert post(path + '/accept', token=bob)[0] == 200
        assert post(path + '/ready', {'assetChecksums': {}}, alice)[0] == 200
        assert post(path + '/ready', {'assetChecksums': {}}, bob)[0] == 200
        assert post(path + '/answers', {'itemID': 'audit-item-1', 'optionID': 'B'}, alice)[0] == 200
        status, submitted = post(path + '/submit', token=alice)
        alice_state = next(p['state'] for p in submitted['participants'] if p['id'] == alice_id)
        status, result = post(path + '/answers', {'itemID': 'audit-item-2', 'optionID': 'B'}, alice)
        print(json.dumps({'alice_state_before_late_answer': alice_state, 'late_answer_http_status': status, 'late_answer_response': result, 'expected': 'reject new answer after this participant submitted'}))
        _, final = post(path + '/submit', token=bob)
        print(json.dumps({'final_state': final['state'], 'alice_score': next(p['serverScore'] for p in final['participants'] if p['id'] == alice_id)}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        app.store.db.close()
