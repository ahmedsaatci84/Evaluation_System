-- Create missing tables for evaluation_app

-- Create Professor_tbl
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Professor_tbl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Professor_tbl] (
        [ProfID] bigint NOT NULL PRIMARY KEY,
        [ProFName] nvarchar(50) NULL,
        [ProPhone] bigint NULL
    );
    PRINT '✓ Created Professor_tbl';
END
ELSE
    PRINT '- Professor_tbl already exists';

-- Create Participant_tbl
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Participant_tbl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Participant_tbl] (
        [Participant_ID] bigint NOT NULL PRIMARY KEY,
        [Participant_name] nvarchar(35) NOT NULL,
        [Participant_phone] bigint NULL,
        [Participant_Email] nvarchar(50) NULL
    );
    PRINT '✓ Created Participant_tbl';
END
ELSE
    PRINT '- Participant_tbl already exists';

-- Create Location_tbl
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Location_tbl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Location_tbl] (
        [id] bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [LocationName] nvarchar(50) NULL
    );
    PRINT '✓ Created Location_tbl';
END
ELSE
    PRINT '- Location_tbl already exists';

-- Create Course_tbl  
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Course_tbl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Course_tbl] (
        [cid] bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [CourseID] nvarchar(50) NULL,
        [CourseName] nvarchar(50) NULL,
        [ProfID] bigint NULL,
        FOREIGN KEY ([ProfID]) REFERENCES [Professor_tbl]([ProfID])
    );
    PRINT '✓ Created Course_tbl';
END
ELSE
    PRINT '- Course_tbl already exists';

-- Create Train_tbl
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Train_tbl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Train_tbl] (
        [TrainID] bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [Train_Date] date NULL,
        [IS_Active] bit NULL DEFAULT 1,
        [CourseID] bigint NULL,
        [ProfessorID] bigint NULL,
        [LocationID] bigint NULL,
        FOREIGN KEY ([CourseID]) REFERENCES [Course_tbl]([cid]) ON DELETE CASCADE,
        FOREIGN KEY ([ProfessorID]) REFERENCES [Professor_tbl]([ProfID]) ON DELETE CASCADE,
        FOREIGN KEY ([LocationID]) REFERENCES [Location_tbl]([id]) ON DELETE CASCADE
    );
    PRINT '✓ Created Train_tbl';
END
ELSE
    PRINT '- Train_tbl already exists';

-- Create Train_Participant_tbl
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Train_Participant_tbl]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Train_Participant_tbl] (
        [Train_Paticipant_id] bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [Evaluation_Date] date NULL,
        [IS_Active] bit NULL DEFAULT 1,
        [TrainID] bigint NULL,
        [ParticipantID] bigint NULL,
        FOREIGN KEY ([TrainID]) REFERENCES [Train_tbl]([TrainID]) ON DELETE CASCADE,
        FOREIGN KEY ([ParticipantID]) REFERENCES [Participant_tbl]([Participant_ID]) ON DELETE CASCADE
    );
    PRINT '✓ Created Train_Participant_tbl';
END
ELSE
    PRINT '- Train_Participant_tbl already exists';

-- Create Evaluation_TAB
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Evaluation_TAB]') AND type in (N'U'))
BEGIN
    CREATE TABLE [Evaluation_TAB] (
        [id] bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [Ev_Q_1] int NULL,
        [Ev_Q_2] int NULL,
        [Ev_Q_3] int NULL,
        [Ev_Q_4] int NULL,
        [Ev_Q_5] int NULL,
        [Ev_Q_6] int NULL,
        [Ev_Q_7] int NULL,
        [Ev_Q_8] int NULL,
        [Ev_Q_9] int NULL,
        [Ev_Q_10] int NULL,
        [Ev_Q_11] int NULL,
        [Ev_Q_12] int NULL,
        [Ev_Q_13] int NULL,
        [Ev_Q_14] int NULL,
        [Ev_Q_15] int NULL,
        [Ev_Q_Notes] nvarchar(max) NULL,
        [ParticipantID] bigint NULL,
        [TrainID] bigint NULL,
        FOREIGN KEY ([ParticipantID]) REFERENCES [Participant_tbl]([Participant_ID]) ON DELETE CASCADE,
        FOREIGN KEY ([TrainID]) REFERENCES [Train_tbl]([TrainID]) ON DELETE CASCADE
    );
    PRINT '✓ Created Evaluation_TAB';
END
ELSE
    PRINT '- Evaluation_TAB already exists';

PRINT '';
PRINT '=== Table Creation Complete ===';
