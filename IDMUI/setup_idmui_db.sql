-- Create IDMUI Application Database
CREATE DATABASE IF NOT EXISTS idmui_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create Dedicated User
CREATE USER 'idmui_user'@'localhost' 
    IDENTIFIED BY 'SecureIDMUIPass123!';

-- Grant Privileges
GRANT ALL PRIVILEGES ON idmui_db.* 
    TO 'idmui_user'@'localhost' 
    WITH GRANT OPTION;

-- Optional: Remote Access from Keystone VM
CREATE USER 'idmui_user'@'192.168.56.101' 
    IDENTIFIED BY 'SecureIDMUIPass123!';
    
GRANT SELECT, INSERT, UPDATE, DELETE ON idmui_db.* 
    TO 'idmui_user'@'192.168.56.101';

FLUSH PRIVILEGES;