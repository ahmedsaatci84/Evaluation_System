import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EvaluationProject.settings')
django.setup()

from django.db import connection
from evaluation_app.models import (
    ProfessorTbl, ParticipantTbl, LocationTbl, CourseTbl,
    TrainTbl, TrainParticipantTbl, EvaluationTab,
    ContactMessage, UserProfile, SystemSettings
)

print("=" * 70)
print("DJANGO PROJECT HEALTH CHECK")
print("=" * 70)

# Test database connection
print("\n1. Testing Database Connection...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"   ✓ Connected to: {version.split('-')[0].strip()}")
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")

# Test table existence
print("\n2. Verifying All Tables Exist...")
models = [
    ('Professor_tbl', ProfessorTbl),
    ('Participant_tbl', ParticipantTbl),
    ('Location_tbl', LocationTbl),
    ('Course_tbl', CourseTbl),
    ('Train_tbl', TrainTbl),
    ('Train_Participant_tbl', TrainParticipantTbl),
    ('Evaluation_TAB', EvaluationTab),
    ('contact_messages', ContactMessage),
    ('user_profiles', UserProfile),
    ('system_settings', SystemSettings),
]

all_good = True
for table_name, model in models:
    try:
        count = model.objects.count()
        print(f"   ✓ {table_name:<25} - {count} records")
    except Exception as e:
        print(f"   ✗ {table_name:<25} - ERROR: {e}")
        all_good = False

# Test model relationships
print("\n3. Testing Model Relationships...")
try:
    # Test foreign key relationships
    courses = CourseTbl.objects.select_related('prof').all()
    trains = TrainTbl.objects.select_related('course', 'professor', 'location').all()
    evals = EvaluationTab.objects.select_related('participant', 'train').all()
    print(f"   ✓ Foreign key relationships working")
except Exception as e:
    print(f"   ✗ Relationship error: {e}")
    all_good = False

# Summary
print("\n" + "=" * 70)
if all_good:
    print("✅ ALL SYSTEMS OPERATIONAL - NO PROBLEMS DETECTED!")
else:
    print("⚠️  SOME ISSUES DETECTED - See details above")
print("=" * 70)
