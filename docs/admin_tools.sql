-- Mission Strata admin tools: message to all players, events (double cash, free gas, car sale), player reports, stats.
-- Safe to run more than once.

create table if not exists public.live (
  id int primary key default 1 check (id = 1),
  msg text, msg_until timestamptz,
  ev jsonb not null default '{}'::jsonb, ev_until timestamptz
);
insert into public.live (id) values (1) on conflict (id) do nothing;
alter table public.live enable row level security;
revoke all on public.live from anon, authenticated;

create table if not exists public.reports (
  id bigserial primary key,
  reporter text not null, target text not null, reason text,
  created_at timestamptz not null default now(), resolved boolean not null default false
);
alter table public.reports enable row level security;
revoke all on public.reports from anon, authenticated;

-- everyone (signed in or not): the current message and events
create or replace function public.get_live() returns json
language sql security definer set search_path = public as $$
  select json_build_object(
    'msg', case when msg_until > now() then msg end, 'msg_until', case when msg_until > now() then msg_until end,
    'ev', case when ev_until > now() then ev else '{}'::jsonb end, 'ev_until', case when ev_until > now() then ev_until end)
  from live where id = 1;
$$;

-- admin: send a message to everyone for some minutes (empty message clears it)
create or replace function public.admin_live(p_token text, p_msg text, p_minutes int) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from players where token = p_token and is_admin and not banned) then raise exception 'Not an admin'; end if;
  update live set msg = nullif(trim(p_msg), ''), msg_until = now() + make_interval(mins => greatest(1, least(coalesce(p_minutes, 60), 10080))) where id = 1;
  return json_build_object('ok', true);
end $$;

-- admin: events, e.g. {"cash": 2, "gas": true, "sale": 20} for some hours ({} ends them)
create or replace function public.admin_events(p_token text, p_ev jsonb, p_hours numeric) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from players where token = p_token and is_admin and not banned) then raise exception 'Not an admin'; end if;
  update live set ev = coalesce(p_ev, '{}'::jsonb), ev_until = now() + make_interval(secs => greatest(60, least(coalesce(p_hours, 1), 168)) * 3600) where id = 1;
  return json_build_object('ok', true);
end $$;

-- a signed-in player reports someone (at most 5 reports an hour)
create or replace function public.report_player(p_token text, p_target text, p_reason text) returns json
language plpgsql security definer set search_path = public as $$
declare me text;
begin
  select username into me from players where token = p_token and not banned;
  if me is null then raise exception 'Sign in to report a player'; end if;
  if (select count(*) from reports where reporter = me and created_at > now() - interval '1 hour') >= 5 then raise exception 'Too many reports. Try again later'; end if;
  insert into reports (reporter, target, reason) values (me, left(trim(p_target), 40), left(trim(coalesce(p_reason, '')), 300));
  return json_build_object('ok', true);
end $$;

create or replace function public.admin_reports(p_token text) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from players where token = p_token and is_admin and not banned) then raise exception 'Not an admin'; end if;
  return coalesce((select json_agg(json_build_object('id', r.id, 'reporter', r.reporter, 'target', r.target, 'reason', r.reason, 'at', r.created_at,
    'pid', p.id, 'banned', p.banned) order by r.created_at desc)
    from (select * from reports where not resolved order by created_at desc limit 200) r left join players p on lower(p.username) = lower(r.target)), '[]'::json);
end $$;

create or replace function public.admin_report_done(p_token text, p_id bigint) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from players where token = p_token and is_admin and not banned) then raise exception 'Not an admin'; end if;
  update reports set resolved = true where id = p_id;
  return json_build_object('ok', true);
end $$;

-- admin: numbers at a glance
create or replace function public.admin_stats(p_token text) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from players where token = p_token and is_admin and not banned) then raise exception 'Not an admin'; end if;
  return json_build_object(
    'total', (select count(*) from players),
    'online', (select count(*) from players where last_seen > now() - interval '5 minutes'),
    'today', (select count(*) from players where last_seen > now() - interval '24 hours'),
    'week', (select count(*) from players where last_seen > now() - interval '7 days'),
    'new_today', (select count(*) from players where created_at > now() - interval '24 hours'),
    'banned', (select count(*) from players where banned),
    'reports', (select count(*) from reports where not resolved),
    'cash', (select coalesce(sum((save->>'cash')::numeric), 0) from players where save ? 'cash'),
    'top_cars', coalesce((select json_agg(json_build_object('car', car, 'n', n)) from (
       select c.car, count(*) n from players, jsonb_array_elements_text(case when jsonb_typeof(save->'cars') = 'array' then save->'cars' else '[]'::jsonb end) as c(car)
       group by c.car order by n desc limit 10) t), '[]'::json));
end $$;

revoke all on function public.get_live, public.admin_live, public.admin_events, public.report_player, public.admin_reports, public.admin_report_done, public.admin_stats from public;
grant execute on function public.get_live, public.admin_live, public.admin_events, public.report_player, public.admin_reports, public.admin_report_done, public.admin_stats to anon, authenticated;
