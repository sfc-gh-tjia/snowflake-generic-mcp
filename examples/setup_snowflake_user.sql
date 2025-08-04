-- Snowflake User Setup for MCP Server
-- This script creates a dedicated user with minimal required permissions
-- Run this as a Snowflake administrator
--
-- ⚠️ SECURITY NOTICE: The MCP server executes raw SQL queries from AI assistants.
-- Follow the principle of least privilege - only grant permissions actually needed.
-- Consider using read-only access for sensitive production environments.

-- Variables (replace with your actual values)
SET mcp_username = 'mcp_user'; # example username for the mcp user: mcp_user
SET mcp_password = 'change_me_secure_password!'; # example password for the mcp user: change_me_secure_password!
SET target_database = 'your_database'; # example database for the mcp user: your_database
SET target_schema = 'your_schema'; # example schema for the mcp user: your_schema
SET target_warehouse = 'your_warehouse';

-- 1. Create the MCP user
CREATE USER IDENTIFIER($mcp_username)
    PASSWORD = $mcp_password
    DEFAULT_WAREHOUSE = $target_warehouse
    DEFAULT_DATABASE = $target_database
    DEFAULT_SCHEMA = $target_schema
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT = 'Dedicated user for MCP Snowflake server';

-- 2. Create a custom role for MCP operations (optional, for better security)
CREATE ROLE IF NOT EXISTS mcp_role
    COMMENT = 'Role for MCP server operations';

-- 3. Grant the role to the user
GRANT ROLE mcp_role TO USER IDENTIFIER($mcp_username);

-- 4. Set the role as default for the user
ALTER USER IDENTIFIER($mcp_username) SET DEFAULT_ROLE = 'mcp_role';

-- 5. Grant necessary privileges to the role

-- Warehouse usage (required for running queries)
GRANT USAGE ON WAREHOUSE IDENTIFIER($target_warehouse) TO ROLE mcp_role;

-- Database and schema access
GRANT USAGE ON DATABASE IDENTIFIER($target_database) TO ROLE mcp_role;
GRANT USAGE ON SCHEMA IDENTIFIER($target_database).IDENTIFIER($target_schema) TO ROLE mcp_role;

-- Table permissions (adjust based on your needs)
-- Option A: Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA IDENTIFIER($target_database).IDENTIFIER($target_schema) TO ROLE mcp_role;

-- Option B: Grant SELECT on specific tables (replace with your table names)
-- GRANT SELECT ON TABLE your_database.public.customers TO ROLE mcp_role;
-- GRANT SELECT ON TABLE your_database.public.orders TO ROLE mcp_role;

-- Option C: Grant broader permissions if needed (be careful with this)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA IDENTIFIER($target_database).IDENTIFIER($target_schema) TO ROLE mcp_role;

-- Future tables (optional - grants permissions on tables created in the future)
GRANT SELECT ON FUTURE TABLES IN SCHEMA IDENTIFIER($target_database).IDENTIFIER($target_schema) TO ROLE mcp_role;

-- View permissions (if you have views)
GRANT SELECT ON ALL VIEWS IN SCHEMA IDENTIFIER($target_database).IDENTIFIER($target_schema) TO ROLE mcp_role;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA IDENTIFIER($target_database).IDENTIFIER($target_schema) TO ROLE mcp_role;

-- 6. For private key authentication, set the public key
-- First, generate the key pair locally:
-- openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
-- openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

-- Then copy the public key content (without BEGIN/END lines) and run:
-- ALTER USER IDENTIFIER($mcp_username) SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...';

-- 7. Verify the setup
SHOW USERS LIKE '%mcp_user%';
SHOW GRANTS TO ROLE mcp_role;
SHOW GRANTS TO USER IDENTIFIER($mcp_username);

-- 8. Test connection (optional - run these as the mcp_user)
-- SELECT CURRENT_USER();
-- SELECT CURRENT_ROLE();
-- SELECT CURRENT_DATABASE();
-- SELECT CURRENT_SCHEMA();
-- SELECT CURRENT_WAREHOUSE(); 