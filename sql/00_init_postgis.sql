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
