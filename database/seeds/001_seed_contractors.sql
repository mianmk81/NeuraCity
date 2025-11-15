-- NeuraCity Contractor Seed Data
-- Populates the contractors table with city-approved contractors
-- These contractors are matched with work orders based on specialty

-- Clear existing data (for re-running seed)
TRUNCATE TABLE contractors CASCADE;

-- ============================================================================
-- Contractor Seed Data
-- ============================================================================

INSERT INTO contractors (name, specialty, contact_email, has_city_contract) VALUES
  -- Road and Infrastructure Specialists
  ('Apex Road Solutions', 'road_repair', 'dispatch@apexroad.com', true),
  ('Metro Asphalt Group', 'pothole_repair', 'service@metroasphalt.com', true),
  ('Urban Pavement Systems', 'road_repair', 'info@urbanpavement.com', true),

  -- Electrical and Traffic Engineering
  ('City Electrical Services', 'electrical', 'contact@cityelectrical.com', true),
  ('TrafficTech Engineering', 'traffic_engineering', 'support@traffictech.com', true),
  ('SignalWorks Inc.', 'traffic_light_repair', 'dispatch@signalworks.com', true),
  ('Municipal Lighting Solutions', 'electrical', 'service@munilighting.com', true),

  -- Specialized Infrastructure
  ('Bridge & Structural Co.', 'structural_engineering', 'info@bridgestructural.com', true),
  ('Underground Utilities LLC', 'utility_repair', 'contact@undergroundutil.com', true),
  ('Storm Drain Experts', 'drainage', 'service@stormdrain.com', true),

  -- Multi-Specialty Contractors
  ('General Infrastructure Partners', 'general_infrastructure', 'dispatch@geninfra.com', true),
  ('Emergency Response Contractors', 'emergency_repair', 'emergency@ercteam.com', true),

  -- Sidewalk and Pedestrian Infrastructure
  ('Sidewalk Solutions Inc.', 'sidewalk_repair', 'info@sidewalksolutions.com', true),
  ('Accessible Pathways Group', 'accessibility', 'contact@accessiblepaths.com', true),

  -- Environmental and Landscaping
  ('Green City Landscaping', 'landscaping', 'service@greencity.com', true);

-- ============================================================================
-- Verification Query
-- ============================================================================

-- Count contractors by specialty
-- SELECT specialty, COUNT(*) as contractor_count
-- FROM contractors
-- WHERE has_city_contract = true
-- GROUP BY specialty
-- ORDER BY specialty;

-- ============================================================================
-- Specialty Reference Guide
-- ============================================================================

-- The following specialties are available in the system:
--
-- - road_repair: General road maintenance and repairs
-- - pothole_repair: Specialized pothole filling and road surface repair
-- - electrical: Electrical work including power systems
-- - traffic_engineering: Traffic system design and optimization
-- - traffic_light_repair: Traffic signal installation and repair
-- - structural_engineering: Bridges, overpasses, structural work
-- - utility_repair: Underground utilities (water, gas, electric)
-- - drainage: Storm drains and water management
-- - general_infrastructure: Multi-purpose infrastructure work
-- - emergency_repair: 24/7 emergency response services
-- - sidewalk_repair: Sidewalk and pedestrian path repair
-- - accessibility: ADA compliance and accessibility improvements
-- - landscaping: Green infrastructure and landscaping

-- ============================================================================
-- Seed complete
-- ============================================================================
