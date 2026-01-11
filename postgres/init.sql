-- postgres/init.sql
-- Create additional database for testing if needed
CREATE DATABASE property_test_db;
GRANT ALL PRIVILEGES ON DATABASE property_test_db TO property_user;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create function for audit logging (optional)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
