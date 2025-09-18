-- Normalize raw poles to core
-- Assumes staging.poles_raw(id text, lon double precision, lat double precision, install_year int, status text)
create table if not exists core.poles as
select
  id,
  install_year,
  status,
  st_setsrid(st_makepoint(lon, lat), 4326) as geom
from staging.poles_raw
where status in ('active','planned');

-- Indexes
create index if not exists idx_poles_geom on core.poles using gist(geom);
create index if not exists idx_poles_status on core.poles(status);

-- Optional QA
-- Fail if null geometries slipped through
do $$
begin
  if exists (select 1 from core.poles where geom is null) then
    raise exception 'Null geometry found in core.poles';
  end if;
end$$;
