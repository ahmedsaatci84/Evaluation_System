-- Connect to SQL Server and run these commands as an administrator:
-- (Run this in SSMS or sqlcmd as sa / sysadmin)

USE evaluation_db;
GO

-- Grant backup permissions to user 'ali'
GRANT BACKUP DATABASE TO [ali];
GRANT BACKUP LOG TO [ali];
GO

-- Grant db_owner role for restore capability
ALTER ROLE db_owner ADD MEMBER [ali];
GO

-- Grant dbcreator server role (needed for RESTORE DATABASE)
USE master;
GO
ALTER SERVER ROLE dbcreator ADD MEMBER [ali];
GO

-- Verify permissions
USE evaluation_db;
GO
SELECT 
    USER_NAME() as CurrentUser,
    HAS_PERMS_BY_NAME(NULL, NULL, 'BACKUP DATABASE') as HasBackupPermission,
    IS_SRVROLEMEMBER('dbcreator') as HasDbCreatorRole,
    IS_MEMBER('db_owner') as HasDbOwnerRole;
GO
