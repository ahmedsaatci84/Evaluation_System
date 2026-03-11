# Quick Reference: Model Changes

## Summary
The evaluation project has been reorganized to match the SQL Server database schema by introducing Training Sessions as a central concept.

## Key Changes

### 1. New Models
- **TrainTbl** - Represents training sessions (links Course + Professor + Location)
- **TrainParticipantTbl** - Junction table linking trainings with participants

### 2. Modified Models
- **EvaluationTab** - Now references TrainTbl instead of direct Course/Professor/Location

### 3. Removed Fields from Evaluation
- ❌ `ev_date` field
- ❌ `prof` foreign key
- ❌ `course` foreign key
- ❌ `location` foreign key

### 4. Added to Evaluation
- ✅ `train` foreign key to TrainTbl
- ✅ `get_course()` method
- ✅ `get_professor()` method
- ✅ `get_location()` method

## New URLs Available

### Training Sessions
- `/training/` - List all training sessions
- `/training/create/` - Create new training session
- `/training/<id>/update/` - Edit training session
- `/training/<id>/delete/` - Delete training session

### Training Participants
- `/training-participants/` - List all training participants
- `/training-participants/create/` - Create new training participant
- `/training-participants/<id>/update/` - Edit training participant
- `/training-participants/<id>/delete/` - Delete training participant

## Admin Interface
New sections added:
- Training Sessions
- Training Participants

Both include search, filtering, and CRUD operations.

## How to Access Related Data

### From Evaluation to Course/Professor/Location
```python
# Old way (REMOVED)
evaluation.course
evaluation.prof
evaluation.location
evaluation.ev_date

# New way
evaluation.train.course
evaluation.train.professor
evaluation.train.location
evaluation.train.train_date

# Or use helper methods
evaluation.get_course()
evaluation.get_professor()
evaluation.get_location()
```

### From Course to Evaluations
```python
# Old way (REMOVED)
course.evaluationtab_set.all()

# New way (through training sessions)
course.training_sessions.all()  # Get all training sessions for this course

# Get all evaluations for a specific course
evaluations = []
for train in course.training_sessions.all():
    evaluations.extend(train.evaluations.all())
```

### From Training Session
```python
train = TrainTbl.objects.get(trainid=1)

# Access related objects
train.course  # Course for this training
train.professor  # Professor conducting training
train.location  # Training location
train.evaluations.all()  # All evaluations for this training
train.participants.all()  # All participants enrolled
```

## Database Constraints
- Deleting a Training Session will **CASCADE DELETE** all related:
  - Evaluations
  - Training Participants
  
- Deleting a Participant will **CASCADE DELETE** all related:
  - Evaluations
  - Training Participants

## Migration Status
Migration file created: `0009_add_train_models.py`

**Note**: Since models use `managed=False`, the migration doesn't alter the database schema. The tables should already exist in SQL Server.

## Files Modified
1. ✅ `models.py` - Added TrainTbl and TrainParticipantTbl, modified EvaluationTab
2. ✅ `admin.py` - Registered new models with admin classes
3. ✅ `views.py` - Added CRUD views for new models, updated evaluation views
4. ✅ `urls.py` - Added URL patterns for new views
5. ✅ `migrations/0009_add_train_models.py` - Migration file created

## Templates Required (Next Step)
Create these templates:
- `train_list.html`
- `train_form.html`
- `train_confirm_delete.html`
- `train_participant_list.html`
- `train_participant_form.html`
- `train_participant_confirm_delete.html`

Update these templates:
- `evaluation_form.html` - Replace course/professor/location dropdowns with training session dropdown
- `evaluation_list.html` - Update to show training session info
