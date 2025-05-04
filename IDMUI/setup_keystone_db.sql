-- Create Keystone Database
CREATE DATABASE IF NOT EXISTS keystone 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create Dedicated User
CREATE USER 'keystone_user'@'localhost' 
    IDENTIFIED BY 'SecureKeystonePass456!';

-- Grant Privileges
GRANT ALL PRIVILEGES ON keystone.* 
    TO 'keystone_user'@'localhost';

-- Optional: Remote Access from IDMUI VM
CREATE USER 'keystone_user'@'192.168.56.102' 
    IDENTIFIED BY 'SecureKeystonePass456!';
    
GRANT SELECT, INSERT, UPDATE, DELETE ON keystone.* 
    TO 'keystone_user'@'192.168.56.102';

FLUSH PRIVILEGES;