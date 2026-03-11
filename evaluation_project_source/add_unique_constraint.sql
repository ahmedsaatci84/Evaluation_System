-- SQL Script to add unique constraint to Evaluation_TAB
-- This prevents duplicate evaluations from the same participant on the same training session

USE [EvaluationDB]
GO

-- Check if constraint already exists and drop it if needed
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'unique_participant_train_evaluation' AND object_id = OBJECT_ID('dbo.Evaluation_TAB'))
BEGIN
    ALTER TABLE [dbo].[Evaluation_TAB] DROP CONSTRAINT [unique_participant_train_evaluation]
    PRINT 'Existing constraint dropped.'
END
GO

-- Add the unique constraint
ALTER TABLE [dbo].[Evaluation_TAB]
ADD CONSTRAINT [unique_participant_train_evaluation] 
UNIQUE (ParticipantID, TrainID);
GO

PRINT 'Unique constraint added successfully!'
PRINT 'Each participant can now only submit one evaluation per training session.'
GO
