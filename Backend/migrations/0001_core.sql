-- PostgreSQL 16 reference schema. The API layer must set app.actor_id as a
-- transaction-local value only after verifying the auth token. Do not expose
-- the database directly until equivalent row policies are enabled and tested.
create extension if not exists pgcrypto;

create type friendship_status as enum ('pending', 'accepted', 'removed');
create type message_status as enum ('accepted', 'redacted');
create type match_state as enum (
  'invited', 'accepted', 'preparing', 'active', 'settling', 'completed',
  'expired', 'declined', 'cancelled', 'invalid', 'forfeited'
);
create type participant_state as enum (
  'invited', 'accepted', 'ready', 'active', 'submitted', 'timed_out', 'forfeited', 'completed'
);

create table app_user (
  id uuid primary key,
  email_normalized text not null unique,
  display_name text not null check (char_length(display_name) between 1 and 80),
  created_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table idempotency_record (
  actor_id uuid not null references app_user(id),
  operation text not null,
  request_id uuid not null,
  request_hash text not null,
  response_status integer,
  response_body jsonb,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  primary key (actor_id, operation, request_id)
);

create table friendship (
  id uuid primary key default gen_random_uuid(),
  requester_id uuid not null references app_user(id),
  addressee_id uuid not null references app_user(id),
  low_user_id uuid generated always as (least(requester_id, addressee_id)) stored,
  high_user_id uuid generated always as (greatest(requester_id, addressee_id)) stored,
  status friendship_status not null default 'pending',
  created_at timestamptz not null default now(),
  accepted_at timestamptz,
  removed_at timestamptz,
  check (requester_id <> addressee_id),
  unique (low_user_id, high_user_id)
);

create table user_block (
  blocker_id uuid not null references app_user(id),
  blocked_id uuid not null references app_user(id),
  created_at timestamptz not null default now(),
  check (blocker_id <> blocked_id),
  primary key (blocker_id, blocked_id)
);

create table friend_invite (
  id uuid primary key default gen_random_uuid(),
  inviter_id uuid not null references app_user(id),
  code_hash text not null unique,
  expires_at timestamptz not null,
  accepted_by uuid references app_user(id),
  accepted_at timestamptz,
  cancelled_at timestamptz,
  created_at timestamptz not null default now()
);

create table conversation (
  id uuid primary key default gen_random_uuid(),
  friendship_id uuid not null unique references friendship(id),
  created_at timestamptz not null default now()
);

create table conversation_hidden (
  conversation_id uuid not null references conversation(id),
  user_id uuid not null references app_user(id),
  hidden_before timestamptz not null default now(),
  primary key (conversation_id, user_id)
);

create table chat_message (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversation(id),
  sender_id uuid not null references app_user(id),
  client_message_id uuid not null,
  body text not null check (char_length(body) between 1 and 4000),
  status message_status not null default 'accepted',
  created_at timestamptz not null default now(),
  unique (sender_id, client_message_id)
);
create index chat_message_cursor_idx on chat_message (conversation_id, created_at, id);

create table learning_session (
  id uuid primary key,
  user_id uuid not null references app_user(id),
  mode text not null check (mode in ('practice', 'diagnostic', 'mockExam', 'review', 'battle')),
  content_version text not null,
  rule_version text,
  started_at timestamptz not null,
  completed_at timestamptz,
  selection_reasons jsonb not null default '{}',
  client_updated_at timestamptz not null,
  server_received_at timestamptz not null default now()
);

create table item_response (
  id uuid primary key,
  session_id uuid not null references learning_session(id) on delete cascade,
  user_id uuid not null references app_user(id),
  group_id text not null,
  item_id text not null,
  family_id text not null,
  part smallint not null check (part between 1 and 7),
  difficulty smallint not null check (difficulty between 1 and 5),
  selected_option_id text,
  is_correct boolean not null,
  elapsed_milliseconds integer not null check (elapsed_milliseconds >= 0),
  answer_condition jsonb not null,
  answered_at timestamptz not null,
  unique (session_id, item_id)
);
create index item_response_exposure_idx on item_response (user_id, family_id, answered_at);

create table battle_match (
  id uuid primary key default gen_random_uuid(),
  creator_id uuid not null references app_user(id),
  request_id uuid not null,
  state match_state not null default 'invited',
  content_version text not null,
  ordered_group_ids text[] not null,
  ordered_item_ids text[] not null,
  asset_checksums jsonb not null,
  invitation_expires_at timestamptz not null,
  starts_at timestamptz,
  deadline timestamptz,
  time_allowance_seconds integer not null check (time_allowance_seconds > 0),
  is_review_rematch boolean not null default false,
  winner_id uuid references app_user(id),
  settled_at timestamptz,
  settlement_version integer not null default 0,
  created_at timestamptz not null default now(),
  unique (creator_id, request_id),
  check (cardinality(ordered_item_ids) > 0)
);
create index battle_match_deadline_idx on battle_match (state, deadline);
create index battle_match_invite_expiry_idx on battle_match (state, invitation_expires_at);

-- Correct answers are deliberately separated from participant-readable match rows.
create table battle_match_item (
  match_id uuid not null references battle_match(id) on delete cascade,
  ordinal integer not null check (ordinal >= 0),
  item_id text not null,
  correct_option_id text not null,
  primary key (match_id, ordinal),
  unique (match_id, item_id)
);

create table battle_participant (
  match_id uuid not null references battle_match(id) on delete cascade,
  user_id uuid not null references app_user(id),
  state participant_state not null,
  progress integer not null default 0 check (progress >= 0),
  score integer check (score >= 0),
  ready_at timestamptz,
  submitted_at timestamptz,
  last_seen_at timestamptz,
  primary key (match_id, user_id)
);

create table battle_answer (
  match_id uuid not null,
  user_id uuid not null,
  item_id text not null,
  request_id uuid not null,
  selected_option_id text,
  received_at timestamptz not null default now(),
  elapsed_milliseconds integer not null check (elapsed_milliseconds >= 0),
  interruption_flags jsonb not null default '{}',
  primary key (match_id, user_id, item_id),
  unique (user_id, request_id),
  foreign key (match_id, user_id) references battle_participant(match_id, user_id)
);

create table content_issue (
  id uuid primary key default gen_random_uuid(),
  reporter_id uuid not null references app_user(id),
  request_id uuid not null,
  content_version text not null,
  group_id text not null,
  item_id text,
  category text not null,
  details text not null check (char_length(details) between 1 and 4000),
  created_at timestamptz not null default now(),
  unique (reporter_id, request_id)
);

create function match_transition_allowed(old_state match_state, new_state match_state)
returns boolean language sql immutable as $$
  select case old_state
    when 'invited' then new_state in ('accepted', 'declined', 'cancelled', 'expired')
    when 'accepted' then new_state in ('preparing', 'cancelled', 'invalid')
    when 'preparing' then new_state in ('active', 'cancelled', 'invalid')
    when 'active' then new_state in ('settling', 'forfeited', 'invalid')
    when 'settling' then new_state in ('completed', 'invalid')
    else false
  end;
$$;

create function enforce_match_transition() returns trigger language plpgsql as $$
begin
  if new.state <> old.state and not match_transition_allowed(old.state, new.state) then
    raise exception 'illegal match transition: % -> %', old.state, new.state;
  end if;
  if old.winner_id is not null and new.winner_id is distinct from old.winner_id then
    raise exception 'winner is immutable after settlement';
  end if;
  return new;
end;
$$;
create trigger battle_match_transition_guard before update on battle_match
for each row execute function enforce_match_transition();

-- Called by a durable scheduled worker. Settlement itself belongs in a single
-- transaction that locks match + participants and increments settlement_version.
create function sweep_match_deadlines(scan_time timestamptz default now())
returns table (match_id uuid, action text) language plpgsql as $$
begin
  return query
  with expired as (
    update battle_match
       set state = 'expired'
     where state = 'invited' and invitation_expires_at <= scan_time
     returning id
  ) select id, 'expired'::text from expired;

  return query
  with due as (
    update battle_match
       set state = 'settling'
     where state = 'active' and deadline <= scan_time
     returning id
  ) select id, 'settle'::text from due;
end;
$$;

-- Direct execution should be granted only to the trusted API/worker roles.
revoke all on function sweep_match_deadlines(timestamptz) from public;
