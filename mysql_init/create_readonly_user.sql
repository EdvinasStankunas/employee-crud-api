-- Create a read-only user (adjust password as needed)
CREATE USER 'readonly_user'@'%' IDENTIFIED BY 'readonly_password';

-- Grant only SELECT privileges on the specific database to this user
GRANT SELECT ON company_db.* TO 'readonly_user'@'%';

-- Apply the changes
FLUSH PRIVILEGES;

-- You can verify by connecting with this user and trying an INSERT/UPDATE/DELETE
