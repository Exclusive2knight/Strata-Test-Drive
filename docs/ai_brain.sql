-- Mission Strata shared traffic brain: games whose players opted in send anonymous traffic-learning stats every few minutes,
-- and every game downloads the combined result. Run this once in the Supabase SQL editor. Safe to run more than once.

create table if not exists public.brain (
  id int primary key default 1 check (id = 1),
  w double precision not null default 0,                 -- how much learning is behind the shared values (capped so it keeps adapting)
  stop_wait double precision not null default 6,         -- seconds a driver waits for their turn at an all-way stop
  gap_k double precision not null default 1,             -- how big a gap drivers want before pulling out (1 = normal)
  ped_pat double precision not null default 45,          -- seconds a pedestrian waits before crossing anyway
  ped_gap_k double precision not null default 1,         -- how far away cars must be before a fed-up pedestrian goes
  stops bigint not null default 0, crossings bigint not null default 0, scares bigint not null default 0, crashes bigint not null default 0,
  devices int not null default 0, updated_at timestamptz not null default now()
);
insert into public.brain (id) values (1) on conflict (id) do nothing;
alter table public.brain enable row level security;
revoke all on public.brain from anon, authenticated;

create table if not exists public.brain_dev (dev text primary key, last_at timestamptz not null, total bigint not null default 0);
alter table public.brain_dev enable row level security;
revoke all on public.brain_dev from anon, authenticated;

create or replace function public.brain_get() returns json
language sql security definer set search_path = public as $$
  select json_build_object('stopWait', stop_wait, 'gapK', gap_k, 'pedPat', ped_pat, 'pedGapK', ped_gap_k,
    'stops', stops, 'cross', crossings, 'scares', scares, 'crashes', crashes, 'devices', devices, 'w', w, 'at', updated_at)
  from brain where id = 1;
$$;

-- one device adds what its traffic learned. At most once every 4 minutes per device, at most 200 learning events per upload,
-- and every value is clamped to the same safe range the game uses, so nobody can push the traffic into doing something silly
create or replace function public.brain_contribute(p_dev text, p_n int, p_stop_wait float8, p_gap_k float8, p_ped_pat float8, p_ped_gap_k float8,
  p_stops int, p_cross int, p_scares int, p_crashes int) returns json
language plpgsql security definer set search_path = public as $$
declare d public.brain_dev; b public.brain; n float8; isnew boolean := false;
begin
  if p_dev is null or p_dev !~ '^[a-z0-9]{16,40}$' then raise exception 'bad device'; end if;
  select * into d from brain_dev where dev = p_dev;
  if found and d.last_at > now() - interval '4 minutes' then return brain_get(); end if;
  isnew := not found;
  n := greatest(0, least(coalesce(p_n, 0), 200));
  insert into brain_dev (dev, last_at, total) values (p_dev, now(), n)
    on conflict (dev) do update set last_at = now(), total = brain_dev.total + n;
  if n > 0 then
    select * into b from brain where id = 1 for update;
    update brain set
      stop_wait = (b.stop_wait * b.w + least(9, greatest(2.5, coalesce(p_stop_wait, 6))) * n) / (b.w + n),
      gap_k     = (b.gap_k * b.w + least(1.5, greatest(0.72, coalesce(p_gap_k, 1))) * n) / (b.w + n),
      ped_pat   = (b.ped_pat * b.w + least(70, greatest(12, coalesce(p_ped_pat, 45))) * n) / (b.w + n),
      ped_gap_k = (b.ped_gap_k * b.w + least(1.6, greatest(1, coalesce(p_ped_gap_k, 1))) * n) / (b.w + n),
      w = least(b.w + n, 20000),
      stops = b.stops + greatest(0, least(coalesce(p_stops, 0), 500)),
      crossings = b.crossings + greatest(0, least(coalesce(p_cross, 0), 500)),
      scares = b.scares + greatest(0, least(coalesce(p_scares, 0), 100)),
      crashes = b.crashes + greatest(0, least(coalesce(p_crashes, 0), 100)),
      devices = b.devices + case when isnew then 1 else 0 end,
      updated_at = now()
    where id = 1;
  end if;
  return brain_get();
end $$;

grant execute on function public.brain_get() to anon, authenticated;
grant execute on function public.brain_contribute(text, int, float8, float8, float8, float8, int, int, int, int) to anon, authenticated;
