-- Assumes risk.fire_zones(zone_id text, risk_score numeric, geom geometry(Polygon,4326))

-- Materialized view for analytics
create materialized view if not exists mart.poles_fire_risk as
select
  p.id,
  r.zone_id,
  r.risk_score,
  p.install_year
from core.poles p
join risk.fire_zones r
  on st_intersects(p.geom, r.geom);

-- Indexes for mv
create index if not exists idx_m_pfr_zone on mart.poles_fire_risk(zone_id);
create index if not exists idx_m_pfr_install_year on mart.poles_fire_risk(install_year);

-- Refresh helper
-- Use CONCURRENTLY if you add a unique index later
refresh materialized view mart.poles_fire_risk;
