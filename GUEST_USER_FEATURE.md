# Guest User Feature - Add Evaluation Only

## Overview
Guest users can now add evaluations without having access to any other features in the system. Their participant name is automatically filled based on their registered user profile.

## Key Features

### 1. Automatic Participant Name Filling
- When a guest user creates an evaluation, their participant name is automatically filled from their profile
- The system uses: `First Name + Last Name` or `Username` if no name is set
- Participant email and phone are also auto-filled from the user profile

### 2. Access Restrictions for Guest Users
Guest users have **LIMITED ACCESS** - they can ONLY:
- ✅ Create new evaluations
- ✅ View the About page
- ✅ Access their Dashboard

Guest users **CANNOT**:
- ❌ View evaluation list
- ❌ Edit evaluations
- ❌ Delete evaluations
- ❌ Manage professors
- ❌ Manage courses
- ❌ Manage participants
- ❌ Manage locations
- ❌ View contact messages

### 3. Navigation Menu
The sidebar navigation is simplified for guest users:
- **Add Evaluation** - Primary action button
- **About** - Information page
- **Dashboard** - User profile and stats

All other menu items are hidden from guest users.

### 4. Evaluation Form Changes
When a guest user opens the evaluation form:
- The **Participant** field is replaced with a read-only text field
- The field displays their auto-filled name
- A helper text shows: "Your name is automatically filled"
- All other fields (Professor, Course, Location, Questions) work normally

## Implementation Details

### Modified Files
1. **views.py**
   - Updated `evaluation_create()` to detect guest users
   - Auto-creates or retrieves participant based on user's name
   - Added decorators to restrict access to other views

2. **decorators.py**
   - Added `guest_can_create_evaluation()` - Allows all logged-in users to create evaluations
   - Added `not_guest_required()` - Blocks guest users from certain views
   - Applied `can_delete_required()` - Ensures only admins can delete

3. **evaluation_form.html**
   - Shows read-only participant name field for guests
   - Shows dropdown selection for admin/user roles
   - Conditional rendering based on `is_guest` flag

4. **base.html**
   - Simplified navigation menu for guest users
   - Shows only: Add Evaluation, About
   - Hides all list views and management pages

### User Roles
The system supports three user roles:
- **admin** - Full access (create, edit, delete all resources)
- **user** - Can create and edit (cannot delete)
- **guest** - Can only create evaluations

## How to Use

### For Guest Users:
1. Register an account or have an admin create one with role "guest"
2. Log in to the system
3. Click "Add Evaluation" from the sidebar
4. Fill out the evaluation form
   - Your name is automatically filled in the Participant field
   - Select Professor, Course, Location
   - Rate all questions (1-10)
   - Add optional notes
5. Click "Save" to submit

### For Administrators:
To create a guest user:
1. Go to user registration
2. Fill in user details (ensure First Name and Last Name are provided)
3. Set Role to "Guest"
4. The guest user will only see the Add Evaluation option

## Database Behavior
- Participant records are created automatically if they don't exist
- Participant ID is auto-incremented
- Email and phone from user profile are stored with participant
- All evaluation data is saved normally

## Security
- All views are protected with `@login_required`
- Role-based decorators enforce access control
- Guest users attempting to access restricted pages receive error message
- They are redirected to home page with appropriate feedback

## Testing
To test the guest user feature:
1. Create a guest user account
2. Log in as the guest user
3. Verify you can only see "Add Evaluation" in the menu
4. Create an evaluation and verify your name is auto-filled
5. Attempt to access restricted URLs directly (should be blocked)
6. Verify the evaluation is saved with correct participant data

## Notes
- Guest users must have a properly configured profile with First/Last name for best experience
- If no name is set, the username will be used as participant name
- Guest users can still access the About page for system information
- Dashboard shows basic profile information for guest users
