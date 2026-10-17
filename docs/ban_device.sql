-- Bans that stick to the device and the network: a banned player can't make a new account or sign in
-- from the same browser/device or the same internet connection (IP). Safe to run more than once.

alter table public.players add column if not exists last_ip text;
alter table public.players add column if not exists dev text;

create table if not exists public.ban_marks (
  kind text not null check (kind in ('ip', 'dev')), val text not null,
  player uuid, created_at timestamptz not null default now(),
  primary key (kind, val)
);
alter table public.ban_marks enable row level security;
revoke all on public.ban_marks from anon, authenticated;

-- the caller's IP, from the headers Supabase passes through
create or replace function public.req_ip() returns text
language sql stable set search_path = public as $$
  select nullif(trim(coalesce(
    current_setting('request.headers', true)::json->>'cf-connecting-ip',
    split_part(current_setting('request.headers', true)::json->>'x-forwarded-for', ',', 1),
    current_setting('request.headers', true)::json->>'x-real-ip', '')), '');
$$;

create or replace function public.marked(p_dev text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from ban_marks where (kind = 'ip' and val = req_ip()) or (kind = 'dev' and val = nullif(p_dev, '')));
$$;

create or replace function public.signup_v2(p_user text, p_pass text, p_dev text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare t text := encode(gen_random_bytes(24), 'hex'); adm boolean := lower(p_user) = 'pizzarobber9';
begin
  if marked(p_dev) then raise exception 'BANNED:This device is banned'; end if;
  if p_user !~ '^[A-Za-z0-9_]{3,20}$' then raise exception 'Username: 3-20 letters, numbers or _'; end if;
  if length(coalesce(p_pass,'')) < 6 then raise exception 'Password: at least 6 characters'; end if;
  if exists (select 1 from players where lower(username) = lower(p_user)) then raise exception 'That username is taken'; end if;
  insert into players (username, pass_hash, token, is_admin, last_ip, dev) values (p_user, crypt(p_pass, gen_salt('bf')), t, adm, req_ip(), nullif(p_dev, ''));
  return json_build_object('token', t, 'username', p_user, 'admin', adm, 'save', '{}'::json);
end $$;

create or replace function public.login_v2(p_user text, p_pass text, p_dev text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare r players;
begin
  select * into r from players where lower(username) = lower(p_user);
  if not found or r.pass_hash <> crypt(p_pass, r.pass_hash) then raise exception 'Wrong username or password'; end if;
  if r.banned then raise exception 'BANNED:%', coalesce(r.ban_reason, ''); end if;
  if not r.is_admin and marked(p_dev) then raise exception 'BANNED:This device is banned'; end if;
  if r.token is null then r.token := encode(gen_random_bytes(24), 'hex'); end if;
  update players set token = r.token, last_seen = now(), last_ip = req_ip(), dev = coalesce(nullif(p_dev, ''), dev) where id = r.id;
  return json_build_object('token', r.token, 'username', r.username, 'admin', r.is_admin, 'save', r.save);
end $$;

create or replace function public.me_v2(p_token text, p_dev text) returns json
language plpgsql security definer set search_path = public as $$
declare r players;
begin
  select * into r from players where token = p_token;
  if not found then raise exception 'Signed out'; end if;
  if r.banned then raise exception 'BANNED:%', coalesce(r.ban_reason, ''); end if;
  if not r.is_admin and marked(p_dev) then raise exception 'BANNED:This device is banned'; end if;
  update players set last_seen = now(), last_ip = req_ip(), dev = coalesce(nullif(p_dev, ''), dev) where id = r.id;
  return json_build_object('username', r.username, 'admin', r.is_admin, 'save', r.save);
end $$;

-- the old sign-up and sign-in check the network too (for copies of the game that haven't updated yet)
create or replace function public.signup(p_user text, p_pass text) returns json
language plpgsql security definer set search_path = public, extensions as $$
begin
  if marked(null) then raise exception 'BANNED:This device is banned'; end if;
  return signup_v2(p_user, p_pass, null);
end $$;

-- banning marks the player's device and network; unbanning clears them
create or replace function public.admin_ban(p_token text, p_id uuid, p_ban boolean, p_reason text) returns json
language plpgsql security definer set search_path = public as $$
declare r players;
begin
  if not exists (select 1 from players where token = p_token and is_admin and not banned) then raise exception 'Not an admin'; end if;
  select * into r from players where id = p_id;
  if not found then raise exception 'No such player'; end if;
  if r.is_admin then raise exception 'You can''t ban an admin'; end if;
  update players set banned = p_ban, ban_reason = case when p_ban then p_reason else null end where id = p_id;
  if p_ban then
    if r.last_ip is not null then insert into ban_marks (kind, val, player) values ('ip', r.last_ip, p_id) on conflict do nothing; end if;
    if r.dev is not null then insert into ban_marks (kind, val, player) values ('dev', r.dev, p_id) on conflict do nothing; end if;
  else
    delete from ban_marks where player = p_id;
  end if;
  return json_build_object('ok', true);
end $$;

revoke all on function public.req_ip, public.marked, public.signup_v2, public.login_v2, public.me_v2 from public;
grant execute on function public.signup_v2, public.login_v2, public.me_v2 to anon, authenticated;
grant execute on function public.signup, public.admin_ban to anon, authenticated;
