-- Mission Strata traffic brain, part 2 (v362): trouble spots, weather/night following gaps, the driving-style mix and zipper merging,
-- shared between every game whose player opted in. Run this once in the Supabase SQL editor after ai_brain.sql. Safe to run more than once.
-- Nothing personal is stored: a random device id (for rate limiting), 80 m map-grid cells with counts, and a few averaged numbers.
-- "How you drive" (your reputation with other drivers) never leaves the player's device.

create table if not exists public.brain2 (
  id int primary key default 1 check (id = 1),
  w double precision not null default 0,                   -- how much learning is behind the shared values (capped so it keeps adapting)
  rain double precision not null default 1.12,             -- extra following room in the rain (1.12 = 12% more)
  snow double precision not null default 1.3,
  night double precision not null default 1.06,
  zip double precision not null default 1,                 -- how readily drivers let merging cars in at work zones
  mix double precision[] not null default array[0.08,0.19,0.37,0.10,0.12,0.09,0.05],   -- eco, calm, normal, sport, brisk, pushy, reckless
  updated_at timestamptz not null default now()
);
insert into public.brain2 (id) values (1) on conflict (id) do nothing;
alter table public.brain2 enable row level security;
revoke all on public.brain2 from anon, authenticated;

-- one row per 80 m map cell that has seen trouble: close calls, crashes, hard braking, seconds of freeway jam
create table if not exists public.brain_cell (
  k text primary key check (k ~ '^-?[0-9]{1,4},-?[0-9]{1,4}$'),
  nm double precision not null default 0, cr double precision not null default 0, hb double precision not null default 0, jam double precision not null default 0,
  updated_at timestamptz not null default now()
);
alter table public.brain_cell enable row level security;
revoke all on public.brain_cell from anon, authenticated;

create table if not exists public.brain2_dev (dev text primary key, last_at timestamptz not null);
alter table public.brain2_dev enable row level security;
revoke all on public.brain2_dev from anon, authenticated;

-- everyone's result: the averaged numbers and the 400 worst cells, as 0..1 risk. A cell fades over about two weeks unless it keeps happening
create or replace function public.brain2_get() returns json
language sql security definer set search_path = public as $$
  select json_build_object('w', b.w, 'cond', json_build_object('rain', b.rain, 'snow', b.snow, 'night', b.night), 'zip', b.zip, 'mix', b.mix,
    'cells', coalesce((select json_agg(json_build_array(c.k, c.r)) from (
       select k, least(1.0, (nm*3 + cr*6 + hb*0.4 + jam/90.0) * exp(-extract(epoch from now() - updated_at) / 1209600.0) / 60.0) as r
       from brain_cell order by (nm*3 + cr*6 + hb*0.4 + jam/90.0) * exp(-extract(epoch from now() - updated_at) / 1209600.0) desc limit 400) c
     where c.r > 0.02), '[]'::json))
  from brain2 b where b.id = 1;
$$;

-- one device adds what its traffic learned: at most once every 4 minutes, at most 40 cells, every count and value clamped to the
-- game's own safe ranges, so no single player can push the traffic into doing something silly
create or replace function public.brain2_contribute(p_dev text, p_rain float8, p_snow float8, p_night float8, p_zip float8, p_mix float8[], p_cells json)
returns json language plpgsql security definer set search_path = public as $$
declare d public.brain2_dev; b public.brain2; n float8 := 20; r record; m float8[]; s float8; i int; dflt float8[] := array[0.08,0.19,0.37,0.10,0.12,0.09,0.05];
begin
  if p_dev is null or p_dev !~ '^[a-z0-9]{16,40}$' then raise exception 'bad device'; end if;
  select * into d from brain2_dev where dev = p_dev;
  if found and d.last_at > now() - interval '4 minutes' then return brain2_get(); end if;
  insert into brain2_dev (dev, last_at) values (p_dev, now()) on conflict (dev) do update set last_at = now();
  -- the style mix: each share kept within half and 1.7x its starting value, then normalised
  m := dflt;
  if p_mix is not null and array_length(p_mix, 1) = 7 then
    for i in 1..7 loop m[i] := least(dflt[i]*1.7, greatest(dflt[i]*0.5, coalesce(p_mix[i], dflt[i]))); end loop;
  end if;
  select * into b from brain2 where id = 1 for update;
  for i in 1..7 loop m[i] := (b.mix[i] * b.w + m[i] * n) / (b.w + n); end loop;
  s := 0; for i in 1..7 loop s := s + m[i]; end loop; for i in 1..7 loop m[i] := m[i] / s; end loop;
  update brain2 set
    rain  = (b.rain  * b.w + least(1.6,  greatest(1, coalesce(p_rain, 1.12)))  * n) / (b.w + n),
    snow  = (b.snow  * b.w + least(2.0,  greatest(1, coalesce(p_snow, 1.3)))   * n) / (b.w + n),
    night = (b.night * b.w + least(1.35, greatest(1, coalesce(p_night, 1.06)))  * n) / (b.w + n),
    zip   = (b.zip   * b.w + least(1.5,  greatest(0.8, coalesce(p_zip, 1)))     * n) / (b.w + n),
    mix = m, w = least(b.w + n, 20000), updated_at = now()
  where id = 1;
  -- the cells (older counts fade before the new ones are added)
  if p_cells is not null then
    for r in select key, value from json_each(p_cells) limit 40 loop
      if r.key ~ '^-?[0-9]{1,4},-?[0-9]{1,4}$' then
        insert into brain_cell as c (k, nm, cr, hb, jam, updated_at) values (r.key,
            least(5, greatest(0, coalesce((r.value->>'nm')::float8, 0))), least(3, greatest(0, coalesce((r.value->>'cr')::float8, 0))),
            least(20, greatest(0, coalesce((r.value->>'hb')::float8, 0))), least(600, greatest(0, coalesce((r.value->>'jam')::float8, 0))), now())
          on conflict (k) do update set
            nm  = c.nm  * exp(-extract(epoch from now() - c.updated_at) / 1209600.0) + excluded.nm,
            cr  = c.cr  * exp(-extract(epoch from now() - c.updated_at) / 1209600.0) + excluded.cr,
            hb  = c.hb  * exp(-extract(epoch from now() - c.updated_at) / 1209600.0) + excluded.hb,
            jam = c.jam * exp(-extract(epoch from now() - c.updated_at) / 1209600.0) + excluded.jam,
            updated_at = now();
      end if;
    end loop;
  end if;
  delete from brain_cell where updated_at < now() - interval '60 days';
  return brain2_get();
end $$;

grant execute on function public.brain2_get() to anon, authenticated;
grant execute on function public.brain2_contribute(text, float8, float8, float8, float8, float8[], json) to anon, authenticated;
