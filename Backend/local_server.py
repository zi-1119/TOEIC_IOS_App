#!/usr/bin/env python3
"""Local cross-process TOEICPath HTTP service.

This server is intentionally dependency-free and uses SQLite for deterministic
local integration tests. Fixed OTP 246810 is available only with --test-mode.
It is not the public production deployment target.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import signal
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None) -> str | None:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z") if value else None


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def canonical_uuid(value: object) -> str:
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        raise APIError(400, "invalid_uuid", "A valid UUID is required")


class APIError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


SCHEMA = """
pragma journal_mode=WAL;
pragma foreign_keys=ON;
create table if not exists users(id text primary key, email text not null unique, display_name text not null, created_at text not null);
create table if not exists otp(email text primary key, code_hash text not null, expires_at text not null);
create table if not exists sessions(token_hash text primary key, user_id text not null references users(id), expires_at text not null);
create table if not exists operations(actor_id text not null, operation text not null, request_id text not null, primary key(actor_id,operation,request_id));
create table if not exists profiles(user_id text primary key references users(id), profile_json text not null, updated_at text not null);
create table if not exists invites(code_hash text primary key, code text not null, inviter_id text not null references users(id), expires_at text not null, accepted_by text);
create table if not exists friendships(id text primary key, low_id text not null, high_id text not null, status text not null, unique(low_id,high_id));
create table if not exists blocks(blocker_id text not null, blocked_id text not null, primary key(blocker_id,blocked_id));
create table if not exists conversations(id text primary key, friendship_id text not null unique references friendships(id), first_id text not null, second_id text not null);
create table if not exists messages(id text primary key, client_message_id text not null, conversation_id text not null references conversations(id), sender_id text not null, body text not null, created_at text not null, unique(sender_id,client_message_id));
create index if not exists messages_cursor on messages(conversation_id,created_at,id);
create table if not exists battle_catalog(content_version text not null, group_id text not null, item_id text not null, ordinal integer not null, correct_option_id text not null, purpose text not null, primary key(content_version,item_id));
create table if not exists battle_catalog_payload(content_version text not null, item_id text not null, payload_json text not null, asset_checksums_json text not null, primary key(content_version,item_id));
create table if not exists matches(id text primary key, request_id text not null, creator_id text not null, state text not null, content_version text not null, group_ids_json text not null, item_ids_json text not null, invitation_expires_at text not null, starts_at text, deadline text, winner_id text, is_review integer not null default 0, unique(creator_id,request_id));
create table if not exists participants(match_id text not null references matches(id), user_id text not null, state text not null, progress integer not null default 0, score integer, primary key(match_id,user_id));
create table if not exists answers(match_id text not null, user_id text not null, item_id text not null, option_id text not null, request_id text not null, primary key(match_id,user_id,item_id), unique(user_id,request_id));
create table if not exists match_questions(match_id text not null references matches(id), item_id text not null, ordinal integer not null, payload_json text not null, primary key(match_id,item_id));
create table if not exists match_assets(match_id text not null references matches(id), asset_id text not null, checksum text not null, primary key(match_id,asset_id));
create table if not exists issues(id text primary key, reporter_id text not null, request_id text not null, payload_json text not null, unique(reporter_id,request_id));
"""


class Store:
    def __init__(self, path: Path, catalog_path: Path | None, battle_seconds: int):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self.battle_seconds = battle_seconds
        with self.lock:
            self.db.executescript(SCHEMA)
            if catalog_path:
                entries = json.loads(catalog_path.read_text())
                for entry in entries:
                    if entry.get("purpose") != "battle":
                        raise ValueError("battle catalog may contain only purpose=battle")
                    prompt, options = entry.get("prompt"), entry.get("options")
                    if not isinstance(prompt, str) or not prompt.strip() or not isinstance(options, list) or len(options) < 2:
                        raise ValueError("battle catalog requires answer-free prompt and options")
                    if any(not isinstance(option, dict) or not isinstance(option.get("id"), str) or not isinstance(option.get("text"), str) for option in options):
                        raise ValueError("battle catalog options require string id/text")
                    asset_checksums = entry.get("assetChecksums", {})
                    if not isinstance(asset_checksums, dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in asset_checksums.items()):
                        raise ValueError("battle catalog assetChecksums must be a string map")
                    self.db.execute(
                        "insert or replace into battle_catalog values(?,?,?,?,?,?)",
                        (entry["contentVersion"], entry["groupID"], entry["itemID"], entry["ordinal"], entry["correctOptionID"], entry["purpose"]),
                    )
                    payload = {
                        "id": entry["itemID"], "groupID": entry["groupID"], "prompt": prompt,
                        "options": options, "assetChecksums": asset_checksums,
                    }
                    self.db.execute(
                        "insert or replace into battle_catalog_payload values(?,?,?,?)",
                        (entry["contentVersion"], entry["itemID"], json.dumps(payload, separators=(",", ":")), json.dumps(asset_checksums, separators=(",", ":"))),
                    )
                self.db.commit()

    def execute(self, sql: str, args=()):
        return self.db.execute(sql, args)

    def commit(self):
        self.db.commit()

    def user_for_token(self, token: str | None) -> str:
        if not token:
            raise APIError(401, "not_authenticated", "Missing bearer token")
        row = self.execute("select user_id,expires_at from sessions where token_hash=?", (token_hash(token),)).fetchone()
        if not row or parse_date(row["expires_at"]) <= now():
            raise APIError(401, "not_authenticated", "Session is missing or expired")
        return row["user_id"]

    def user(self, user_id: str):
        row = self.execute("select * from users where id=?", (user_id,)).fetchone()
        if not row:
            raise APIError(404, "user_not_found", "User does not exist")
        return row

    def friendship(self, a: str, b: str):
        low, high = sorted((a, b))
        return self.execute("select * from friendships where low_id=? and high_id=?", (low, high)).fetchone()

    def blocked(self, a: str, b: str) -> bool:
        return self.execute(
            "select 1 from blocks where (blocker_id=? and blocked_id=?) or (blocker_id=? and blocked_id=?)",
            (a, b, b, a),
        ).fetchone() is not None

    def require_friends(self, a: str, b: str, allow_removed=False):
        if self.blocked(a, b):
            raise APIError(403, "blocked", "A block is active")
        relation = self.friendship(a, b)
        if not relation or (relation["status"] != "accepted" and not (allow_removed and relation["status"] == "removed")):
            raise APIError(403, "not_friends", "Accepted friendship required")
        return relation

    def remember(self, actor: str, operation: str, request_id: str) -> bool:
        try:
            self.execute("insert into operations values(?,?,?)", (actor, operation, request_id))
            return True
        except sqlite3.IntegrityError:
            return False

    def sweep(self):
        with self.lock:
            stamp = iso(now())
            self.execute("update matches set state='expired' where state='invited' and invitation_expires_at<=?", (stamp,))
            due = self.execute("select id from matches where state='active' and deadline<=?", (stamp,)).fetchall()
            for row in due:
                self.settle(row["id"], timed_out=True)
            self.commit()

    def settle(self, match_id: str, timed_out=False):
        match = self.execute("select * from matches where id=?", (match_id,)).fetchone()
        if not match or match["state"] == "completed":
            return
        item_ids = json.loads(match["item_ids_json"])
        keys = {r["item_id"]: r["correct_option_id"] for r in self.execute(
            f"select item_id,correct_option_id from battle_catalog where content_version=? and item_id in ({','.join('?' for _ in item_ids)})",
            (match["content_version"], *item_ids),
        ).fetchall()}
        participants = self.execute("select * from participants where match_id=? order by user_id", (match_id,)).fetchall()
        scores = []
        for participant in participants:
            answers = self.execute("select item_id,option_id from answers where match_id=? and user_id=?", (match_id, participant["user_id"])).fetchall()
            score = sum(100 for answer in answers if keys.get(answer["item_id"]) == answer["option_id"])
            state = "timedOut" if timed_out and participant["state"] != "submitted" else "completed"
            self.execute("update participants set state=?,score=? where match_id=? and user_id=?", (state, score, match_id, participant["user_id"]))
            scores.append((participant["user_id"], score))
        winner = None
        if len(scores) == 2 and scores[0][1] != scores[1][1]:
            winner = max(scores, key=lambda value: value[1])[0]
        self.execute("update matches set state='completed',winner_id=? where id=?", (winner, match_id))

    def visible_match(self, match_id: str, actor: str):
        match = self.execute("select * from matches where id=?", (match_id,)).fetchone()
        if not match:
            raise APIError(404, "match_not_found", "Match does not exist")
        participants = self.execute("select * from participants where match_id=? order by user_id", (match_id,)).fetchall()
        if actor not in {row["user_id"] for row in participants}:
            raise APIError(403, "forbidden", "Not a participant")
        completed = match["state"] == "completed"
        return {
            "id": match["id"], "requestID": match["request_id"], "state": match["state"],
            "contentVersion": match["content_version"], "groupIDs": json.loads(match["group_ids_json"]),
            "orderedItemIDs": json.loads(match["item_ids_json"]), "invitationExpiresAt": match["invitation_expires_at"],
            "startsAt": match["starts_at"], "deadline": match["deadline"],
            "participants": [{"id": row["user_id"], "state": row["state"], "progress": row["progress"], "serverScore": row["score"] if completed else None} for row in participants],
            "winnerID": match["winner_id"] if completed else None, "isReviewRematch": bool(match["is_review"]),
        }


class Handler(BaseHTTPRequestHandler):
    server_version = "TOEICPathLocal/1.0"

    @property
    def app(self):
        return self.server.app

    def log_message(self, format, *args):
        if self.app.verbose:
            super().log_message(format, *args)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 2_000_000:
            raise APIError(413, "payload_too_large", "Payload exceeds local service limit")
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except Exception as error:
            raise APIError(400, "invalid_json", str(error))

    def respond(self, status=200, payload=None):
        data = json.dumps(payload if payload is not None else {}, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def actor(self):
        auth = self.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else None
        return self.app.store.user_for_token(token)

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def do_DELETE(self):
        self.dispatch("DELETE")

    def dispatch(self, method):
        try:
            if self.headers.get("X-Public-Client-ID") != self.app.public_client_id:
                raise APIError(401, "invalid_client", "Public client ID mismatch")
            parsed = urlparse(self.path)
            path, query = parsed.path, parse_qs(parsed.query)
            with self.app.store.lock:
                payload = self.route(method, path, query)
                self.app.store.commit()
            self.respond(200, payload)
        except APIError as error:
            self.app.store.db.rollback()
            self.respond(error.status, {"error": error.code, "message": error.message})
        except sqlite3.IntegrityError as error:
            self.app.store.db.rollback()
            self.respond(409, {"error": "conflict", "message": str(error)})
        except Exception as error:
            self.app.store.db.rollback()
            self.respond(500, {"error": "internal_error", "message": str(error) if self.app.verbose else "Internal server error"})

    def route(self, method, path, query):
        body = self.read_json() if method in {"POST", "DELETE"} else {}
        store = self.app.store

        if method == "POST" and path == "/v1/auth/request-code":
            email = str(body.get("email", "")).strip().lower()
            if "@" not in email:
                raise APIError(400, "invalid_email", "Valid email required")
            if not self.app.test_mode:
                raise APIError(503, "email_provider_not_configured", "Configure a production OTP delivery provider")
            store.execute("insert or replace into otp values(?,?,?)", (email, token_hash("246810"), iso(now() + timedelta(minutes=10))))
            return {}

        if method == "POST" and path == "/v1/auth/verify":
            email, code = str(body.get("email", "")).strip().lower(), str(body.get("code", ""))
            row = store.execute("select * from otp where email=?", (email,)).fetchone()
            if not row or parse_date(row["expires_at"]) <= now() or row["code_hash"] != token_hash(code):
                raise APIError(401, "invalid_code", "Invalid or expired code")
            user = store.execute("select * from users where email=?", (email,)).fetchone()
            if not user:
                user_id = str(uuid.uuid4())
                store.execute("insert into users values(?,?,?,?)", (user_id, email, email.split("@")[0][:80], iso(now())))
                user = store.user(user_id)
            token = secrets.token_urlsafe(32)
            store.execute("insert into sessions values(?,?,?)", (token_hash(token), user["id"], iso(now() + timedelta(days=30))))
            return {"identity": {"userID": user["id"], "email": user["email"], "displayName": user["display_name"]}, "accessToken": token}

        actor = self.actor()
        if method == "POST" and path == "/v1/auth/sign-out":
            auth = self.headers.get("Authorization", "")[7:]
            store.execute("delete from sessions where token_hash=?", (token_hash(auth),))
            return {}
        if method == "POST" and path == "/v1/profile/merge":
            request_id = str(body.get("requestID", ""))
            if store.remember(actor, "profile.merge", request_id):
                store.execute("insert or replace into profiles values(?,?,?)", (actor, json.dumps(body.get("profile", {})), iso(now())))
            return {}
        if method == "POST" and path == "/v1/friends/invites":
            request_id = str(body.get("requestID", ""))
            existing = store.execute("select code from invites where inviter_id=? and code_hash=?", (actor, token_hash(request_id))).fetchone()
            if existing:
                return {"url": f"toeicpath://invite/{existing['code']}"}
            code = secrets.token_urlsafe(18)
            store.execute("insert into invites values(?,?,?,?,null)", (token_hash(request_id), code, actor, iso(now() + timedelta(hours=24))))
            return {"url": f"toeicpath://invite/{code}"}
        if method == "POST" and path == "/v1/friends/accept":
            invite = store.execute("select * from invites where code=?", (body.get("code"),)).fetchone()
            if not invite or parse_date(invite["expires_at"]) <= now():
                raise APIError(404, "invite_invalid", "Invite missing or expired")
            other = invite["inviter_id"]
            if other == actor:
                raise APIError(400, "cannot_invite_self", "Cannot accept own invite")
            if store.blocked(actor, other):
                raise APIError(403, "blocked", "A block is active")
            low, high = sorted((actor, other))
            relation = store.friendship(actor, other)
            if relation:
                store.execute("update friendships set status='accepted' where id=?", (relation["id"],))
                friendship_id = relation["id"]
            else:
                friendship_id = str(uuid.uuid4())
                store.execute("insert into friendships values(?,?,?,'accepted')", (friendship_id, low, high))
                store.execute("insert into conversations values(?,?,?,?)", (str(uuid.uuid4()), friendship_id, low, high))
            store.execute("update invites set accepted_by=? where code=?", (actor, body.get("code")))
            return self.friend_summary(other, actor)
        if method == "GET" and path == "/v1/friends":
            relations = store.execute("select * from friendships where (low_id=? or high_id=?) and status='accepted'", (actor, actor)).fetchall()
            return [self.friend_summary(row["high_id"] if row["low_id"] == actor else row["low_id"], actor) for row in relations if not store.blocked(row["low_id"], row["high_id"])]
        if path.startswith("/v1/friends/"):
            parts = path.split("/")
            other = canonical_uuid(parts[3])
            store.user(other)
            if method == "POST" and len(parts) == 5 and parts[4] == "block":
                store.execute("delete from blocks where blocker_id=? and blocked_id=?", (actor, other))
                if body.get("blocked"):
                    store.execute("insert into blocks values(?,?)", (actor, other))
                return {}
            if method == "DELETE" and len(parts) == 4:
                relation = store.friendship(actor, other)
                if relation:
                    store.execute("update friendships set status='removed' where id=?", (relation["id"],))
                return {}
        if method == "GET" and path.startswith("/v1/conversations/with/"):
            other = canonical_uuid(path.rsplit("/", 1)[1])
            relation = store.require_friends(actor, other, allow_removed=True)
            conversation = store.execute("select id from conversations where friendship_id=?", (relation["id"],)).fetchone()
            return {"conversationID": conversation["id"]}
        if path.startswith("/v1/conversations/") and path.endswith("/messages"):
            conversation_id = canonical_uuid(path.split("/")[3])
            conversation = store.execute("select * from conversations where id=?", (conversation_id,)).fetchone()
            if not conversation or actor not in {conversation["first_id"], conversation["second_id"]}:
                raise APIError(403, "forbidden", "Conversation unavailable")
            other = conversation["second_id"] if conversation["first_id"] == actor else conversation["first_id"]
            if method == "POST":
                store.require_friends(actor, other)
                text = str(body.get("body", "")).strip()
                if not 1 <= len(text) <= 4000:
                    raise APIError(400, "invalid_message", "Message must contain 1-4000 characters")
                client_id = str(body.get("clientMessageID"))
                existing = store.execute("select * from messages where sender_id=? and client_message_id=?", (actor, client_id)).fetchone()
                if existing:
                    return self.message_json(existing)
                row_id = str(uuid.uuid4())
                store.execute("insert into messages values(?,?,?,?,?,?)", (row_id, client_id, conversation_id, actor, text, iso(now())))
                return self.message_json(store.execute("select * from messages where id=?", (row_id,)).fetchone())
            if method == "GET":
                if store.blocked(actor, other):
                    raise APIError(403, "blocked", "A block is active")
                limit = min(100, max(1, int(query.get("limit", ["100"])[0])))
                after = query.get("after", [None])[0]
                sql, args = "select * from messages where conversation_id=?", [conversation_id]
                if after:
                    sql, args = sql + " and created_at>?", args + [after]
                rows = store.execute(sql + " order by created_at,id limit ?", (*args, limit)).fetchall()
                return [self.message_json(row) for row in rows]
        if method == "POST" and path == "/v1/battles/catalog/check":
            for item in body.get("items", []):
                if item.get("purpose") != "battle":
                    raise APIError(400, "invalid_battle_content", "Only battle purpose is accepted")
                row = store.execute("select 1 from battle_catalog where content_version=? and group_id=? and item_id=?", (item.get("contentVersion"), item.get("groupID"), item.get("itemID"))).fetchone()
                if not row:
                    raise APIError(409, "catalog_mismatch", "Server battle catalog does not contain requested item")
            return {}
        if method == "POST" and path == "/v1/battles":
            opponent = canonical_uuid(body.get("opponentID"))
            store.require_friends(actor, opponent)
            request_id, group_ids = str(body.get("requestID")), body.get("groupIDs", [])
            existing = store.execute("select id from matches where creator_id=? and request_id=?", (actor, request_id)).fetchone()
            if existing:
                return store.visible_match(existing["id"], actor)
            if not group_ids:
                raise APIError(400, "invalid_battle_content", "At least one group is required")
            placeholders = ",".join("?" for _ in group_ids)
            rows = store.execute(f"select * from battle_catalog where group_id in ({placeholders}) order by ordinal", group_ids).fetchall()
            if not rows or {row["group_id"] for row in rows} != set(group_ids) or len({row["content_version"] for row in rows}) != 1:
                raise APIError(409, "invalid_battle_content", "Groups must resolve to one server catalog version")
            match_id = str(uuid.uuid4())
            store.execute("insert into matches values(?,?,?,?,?,?,?,?,?,?,?,0)", (match_id, request_id, actor, "invited", rows[0]["content_version"], json.dumps(group_ids), json.dumps([row["item_id"] for row in rows]), iso(now() + timedelta(hours=24)), None, None, None))
            store.execute("insert into participants values(?,?,?,0,null)", (match_id, actor, "accepted"))
            store.execute("insert into participants values(?,?,?,0,null)", (match_id, opponent, "invited"))
            frozen_assets = {}
            for ordinal, row in enumerate(rows):
                payload = store.execute(
                    "select payload_json,asset_checksums_json from battle_catalog_payload where content_version=? and item_id=?",
                    (row["content_version"], row["item_id"]),
                ).fetchone()
                if not payload:
                    raise APIError(409, "invalid_battle_content", "Server catalog is missing answer-free client payload")
                store.execute("insert into match_questions values(?,?,?,?)", (match_id, row["item_id"], ordinal, payload["payload_json"]))
                for asset_id, checksum in json.loads(payload["asset_checksums_json"]).items():
                    if asset_id in frozen_assets and frozen_assets[asset_id] != checksum:
                        raise APIError(409, "invalid_battle_content", "Server catalog has conflicting asset checksums")
                    frozen_assets[asset_id] = checksum
            for asset_id, checksum in frozen_assets.items():
                store.execute("insert into match_assets values(?,?,?)", (match_id, asset_id, checksum))
            return store.visible_match(match_id, actor)
        if method == "GET" and path == "/v1/battles":
            store.sweep()
            rows = store.execute("select match_id from participants where user_id=?", (actor,)).fetchall()
            return [store.visible_match(row["match_id"], actor) for row in rows]
        if path.startswith("/v1/battles/"):
            parts = path.split("/")
            match_id = canonical_uuid(parts[3])
            store.sweep()
            match = store.visible_match(match_id, actor)
            action = parts[4] if len(parts) > 4 else None
            if method == "GET" and action is None:
                return match
            if method == "GET" and action == "questions":
                rows = store.execute("select payload_json from match_questions where match_id=? order by ordinal", (match_id,)).fetchall()
                if len(rows) != len(match["orderedItemIDs"]):
                    raise APIError(409, "invalid_battle_content", "Frozen battle payload is incomplete")
                return [json.loads(row["payload_json"]) for row in rows]
            request_id = str(body.get("requestID", ""))
            if action in {"accept", "ready", "submit"} and not store.remember(actor, f"battle.{match_id}.{action}", request_id):
                return store.visible_match(match_id, actor)
            if method == "POST" and action == "accept":
                if match["state"] != "invited":
                    raise APIError(409, "invalid_transition", "Match is not invited")
                store.execute("update participants set state='accepted' where match_id=? and user_id=?", (match_id, actor))
                store.execute("update matches set state='accepted' where id=?", (match_id,))
                return store.visible_match(match_id, actor)
            if method == "POST" and action == "ready":
                if match["state"] not in {"accepted", "preparing"}:
                    raise APIError(409, "invalid_transition", "Match cannot become ready")
                required_assets = {row["asset_id"]: row["checksum"] for row in store.execute(
                    "select asset_id,checksum from match_assets where match_id=?", (match_id,)
                ).fetchall()}
                provided_assets = body.get("assetChecksums", {})
                if not isinstance(provided_assets, dict) or provided_assets != required_assets:
                    raise APIError(409, "asset_mismatch", "Required battle assets are missing or have different checksums")
                store.execute("update participants set state='ready' where match_id=? and user_id=?", (match_id, actor))
                store.execute("update matches set state='preparing' where id=?", (match_id,))
                remaining = store.execute("select count(*) n from participants where match_id=? and state!='ready'", (match_id,)).fetchone()["n"]
                if remaining == 0:
                    started = now()
                    store.execute("update matches set state='active',starts_at=?,deadline=? where id=?", (iso(started), iso(started + timedelta(seconds=store.battle_seconds)), match_id))
                    store.execute("update participants set state='active' where match_id=?", (match_id,))
                return store.visible_match(match_id, actor)
            if method == "POST" and action == "answers":
                item_id = str(body.get("itemID"))
                option_id = str(body.get("optionID"))
                accepted_replay = store.execute(
                    "select match_id,item_id,option_id from answers where user_id=? and request_id=?",
                    (actor, request_id),
                ).fetchone()
                if accepted_replay:
                    if accepted_replay["match_id"] == match_id and accepted_replay["item_id"] == item_id and accepted_replay["option_id"] == option_id:
                        return {}
                    raise APIError(409, "idempotency_conflict", "Request ID was already used for different answer data")
                current = store.visible_match(match_id, actor)
                if current["state"] != "active" or parse_date(current["deadline"]) <= now():
                    raise APIError(409, "answer_window_closed", "Answer deadline passed")
                participant = store.execute(
                    "select state from participants where match_id=? and user_id=?", (match_id, actor)
                ).fetchone()
                if not participant or participant["state"] != "active":
                    raise APIError(409, "participant_not_active", "Submitted or timed-out participants cannot add answers")
                if item_id not in current["orderedItemIDs"]:
                    raise APIError(400, "invalid_battle_content", "Item not in match")
                try:
                    store.execute("insert into answers values(?,?,?,?,?)", (match_id, actor, item_id, option_id, request_id))
                    store.execute("update participants set progress=progress+1 where match_id=? and user_id=?", (match_id, actor))
                except sqlite3.IntegrityError:
                    duplicate = store.execute("select 1 from answers where user_id=? and request_id=?", (actor, request_id)).fetchone()
                    if not duplicate:
                        raise APIError(409, "answer_already_accepted", "Item already has an accepted answer")
                return {}
            if method == "POST" and action == "submit":
                if match["state"] != "active":
                    raise APIError(409, "invalid_transition", "Match is not active")
                store.execute("update participants set state='submitted' where match_id=? and user_id=?", (match_id, actor))
                count = store.execute("select count(*) n from participants where match_id=? and state!='submitted'", (match_id,)).fetchone()["n"]
                if count == 0:
                    store.settle(match_id)
                return store.visible_match(match_id, actor)
        if method == "POST" and path == "/v1/content/issues":
            request_id = str(body.get("requestID"))
            store.execute("insert or ignore into issues values(?,?,?,?)", (str(uuid.uuid4()), actor, request_id, json.dumps(body)))
            return {}
        raise APIError(404, "not_found", "Unknown endpoint")

    def friend_summary(self, user_id, viewer_id):
        user = self.app.store.user(user_id)
        relation = self.app.store.friendship(user_id, viewer_id)
        conversation = self.app.store.execute("select id from conversations where friendship_id=?", (relation["id"],)).fetchone() if relation else None
        unread = self.app.store.execute("select count(*) n from messages where conversation_id=? and sender_id=?", (conversation["id"], user_id)).fetchone()["n"] if conversation else 0
        return {"id": user_id, "displayName": user["display_name"], "handle": "@" + user["email"].split("@")[0], "isBlocked": self.app.store.blocked(viewer_id, user_id), "unreadCount": unread}

    @staticmethod
    def message_json(row):
        return {"id": row["id"], "clientMessageID": row["client_message_id"], "conversationID": row["conversation_id"], "senderID": row["sender_id"], "body": row["body"], "createdAt": row["created_at"], "delivery": "sent"}


class App:
    def __init__(self, args):
        self.store = Store(Path(args.state), Path(args.catalog) if args.catalog else None, args.battle_seconds)
        self.public_client_id = args.public_client_id
        self.test_mode, self.verbose = args.test_mode, args.verbose
        self.stop = threading.Event()

    def worker(self):
        while not self.stop.wait(0.25):
            try:
                self.store.sweep()
            except Exception:
                if self.verbose:
                    import traceback
                    traceback.print_exc()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--state", required=True)
    parser.add_argument("--catalog")
    parser.add_argument("--public-client-id", default="toeicpath-local")
    parser.add_argument("--battle-seconds", type=int, default=600)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    app = App(args)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.app = app
    worker = threading.Thread(target=app.worker, daemon=True)
    worker.start()
    print(json.dumps({"event": "listening", "host": args.host, "port": server.server_address[1]}), flush=True)

    def stop(*_):
        app.stop.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        server.serve_forever()
    finally:
        app.stop.set()
        server.server_close()
        app.store.db.close()


if __name__ == "__main__":
    main()
