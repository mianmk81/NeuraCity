-- =====================================================
-- Seed Data: Contractors
-- Insert diverse contractors with various specialties
-- =====================================================

-- Clear existing data (optional - comment out for production)
-- TRUNCATE TABLE contractors CASCADE;

-- Pothole and Road Repair Specialists
INSERT INTO contractors (name, specialty, contact_email, has_city_contract) VALUES
('QuickFix Paving Co.', 'pothole_repair', 'dispatch@quickfixpaving.com', TRUE),
('Metro Road Solutions', 'pothole_repair', 'contact@metroroads.com', TRUE),
('Urban Asphalt Services', 'asphalt_repair', 'info@urbanasphalt.com', TRUE),
('RapidPatch Road Repair', 'pothole_repair', 'service@rapidpatch.com', TRUE);

-- Traffic Signal and Electrical Specialists
INSERT INTO contractors (name, specialty, contact_email, has_city_contract) VALUES
('SignalTech Systems', 'traffic_signals', 'ops@signaltech.com', TRUE),
('City Light & Signal', 'electrical', 'admin@citylightsignal.com', TRUE),
('TrafficFlow Technologies', 'traffic_signals', 'support@trafficflow.tech', TRUE),
('ElectraCity Solutions', 'electrical', 'contact@electracity.com', TRUE);

-- General Infrastructure and Construction
INSERT INTO contractors (name, specialty, contact_email, has_city_contract) VALUES
('BuildRight Infrastructure', 'general_construction', 'projects@buildright.com', TRUE),
('Municipal Maintenance Corp', 'general_maintenance', 'service@municorp.com', TRUE),
('CityWorks Construction', 'general_construction', 'hello@cityworks.build', TRUE);

-- Specialized Services
INSERT INTO contractors (name, specialty, contact_email, has_city_contract) VALUES
('EmergencyFix 24/7', 'emergency_repair', 'dispatch@emergencyfix.com', TRUE),
('GreenCity Landscaping', 'landscaping', 'info@greencity.land', TRUE),
('DrainFlow Systems', 'drainage', 'contact@drainflow.com', TRUE),
('SafeWalk Sidewalk Repair', 'sidewalk_repair', 'admin@safewalk.repair', TRUE);

-- Additional contractors (some without active contracts)
INSERT INTO contractors (name, specialty, contact_email, has_city_contract) VALUES
('BudgetPave Inc.', 'pothole_repair', 'info@budgetpave.com', FALSE),
('Premium Signal Solutions', 'traffic_signals', 'sales@premiumsignal.com', FALSE),
('FastLane Repairs', 'general_maintenance', 'contact@fastlanerepairs.com', TRUE),
('EcoFriendly Infrastructure', 'sustainable_construction', 'hello@ecofriendly.build', TRUE);

-- Insert a summary message
DO $$
DECLARE
    contractor_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO contractor_count FROM contractors;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Contractors seeded successfully';
    RAISE NOTICE 'Total contractors: %', contractor_count;
    RAISE NOTICE '========================================';
END $$;
