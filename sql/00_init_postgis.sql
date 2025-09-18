-- Create DB objects and enable PostGIS
create extension if not exists postgis;

-- Schemas
create schema if not exists staging;
create schema if not exists core;
create schema if not exists risk;
create schema if not exists mart;
create schema if not exists ops;

-- Simple run log
create table if not exists ops.run_log(
  id bigserial primary key,
  pipeline text not null,
  step text not null,
  status text not null check (status in ('START','OK','FAIL')),
  row_count bigint,
  duration_sec numeric,
  ts timestamptz default now()
);

-- Staging raw assets
create table if not exists staging.poles_raw(
  id integer primary key,
  install_year integer,
  status text,
  lon double precision,
  lat double precision
);

-- Core normalized poles
create table if not exists core.poles(
  id integer primary key,
  install_year integer,
  status text,
  geom geometry(Point,4326)
);
create index if not exists core_poles_geom_gix on core.poles using gist(geom);

-- Risk zones
create table if not exists risk.fire_zones(
  zone_id integer primary key,
  risk_score double precision,
  geom geometry(Polygon,4326)
);
create index if not exists risk_fire_zones_geom_gix on risk.fire_zones using gist(geom);

-- Materialized view for joined analysis (refreshed after loads)
create materialized view if not exists mart.poles_fire_risk as
select p.id,
       z.zone_id,
       z.risk_score,
       p.install_year,
       p.geom
from core.poles p
left join risk.fire_zones z on st_intersects(p.geom, z.geom);

comment on materialized view mart.poles_fire_risk is 'Join of poles with fire risk zones';

-- Helper function to refresh materialized view
create or replace function mart.refresh_poles_fire_risk() returns void language plpgsql as $$
begin
  refresh materialized view concurrently mart.poles_fire_risk;
end;$$;
