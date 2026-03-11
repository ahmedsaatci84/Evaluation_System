#!/usr/bin/env python
"""
Convert all template files to use Django i18n translation tags.
"""
import os
import re

# Template file updates
TEMPLATE_UPDATES = {
    'professor_list.html': '''{% extends "evaluation_app/base.html" %}
{% load i18n %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>{% trans "Professor List" %}</h1>
    <a href="{% url 'professor_create' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> {% trans "Add Professor" %}
    </a>
</div>

{% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
{% endif %}

{% if professors %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead class="table-dark">
            <tr>
                <th>{% trans "ID" %}</th>
                <th>{% trans "Name" %}</th>
                <th>{% trans "Phone" %}</th>
                <th>{% trans "Actions" %}</th>
            </tr>
        </thead>
        <tbody>
            {% for professor in professors %}
            <tr>
                <td>{{ professor.profid }}</td>
                <td>{{ professor.profname|default:"N/A" }}</td>
                <td>{{ professor.prophone|default:"N/A" }}</td>
                <td>
                    <a href="{% url 'professor_update' professor.profid %}" class="btn btn-sm btn-warning">{% trans "Edit" %}</a>
                    <a href="{% url 'professor_delete' professor.profid %}" class="btn btn-sm btn-danger">{% trans "Delete" %}</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-warning" role="alert">
    {% trans "No professors found." %}
</div>
{% endif %}
{% endblock %}
''',

    'course_list.html': '''{% extends "evaluation_app/base.html" %}
{% load i18n %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>{% trans "Course List" %}</h1>
    <a href="{% url 'course_create' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> {% trans "Add Course" %}
    </a>
</div>

{% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
{% endif %}

{% if courses %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead class="table-dark">
            <tr>
                <th>{% trans "ID" %}</th>
                <th>{% trans "Course ID" %}</th>
                <th>{% trans "Course Name" %}</th>
                <th>{% trans "Professor" %}</th>
                <th>{% trans "Actions" %}</th>
            </tr>
        </thead>
        <tbody>
            {% for course in courses %}
            <tr>
                <td>{{ course.cid }}</td>
                <td>{{ course.courseid|default:"N/A" }}</td>
                <td>{{ course.coursename }}</td>
                <td>{{ course.prof.profname|default:"N/A" }}</td>
                <td>
                    <a href="{% url 'course_update' course.cid %}" class="btn btn-sm btn-warning">{% trans "Edit" %}</a>
                    <a href="{% url 'course_delete' course.cid %}" class="btn btn-sm btn-danger">{% trans "Delete" %}</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-warning" role="alert">
    {% trans "No courses found." %}
</div>
{% endif %}
{% endblock %}
''',

    'trainer_list.html': '''{% extends "evaluation_app/base.html" %}
{% load i18n %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>{% trans "Trainer List" %}</h1>
    <a href="{% url 'trainer_create' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> {% trans "Add Trainer" %}
    </a>
</div>

{% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
{% endif %}

{% if trainers %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead class="table-dark">
            <tr>
                <th>{% trans "ID" %}</th>
                <th>{% trans "Name" %}</th>
                <th>{% trans "Phone" %}</th>
                <th>{% trans "Email" %}</th>
                <th>{% trans "Actions" %}</th>
            </tr>
        </thead>
        <tbody>
            {% for trainer in trainers %}
            <tr>
                <td>{{ trainer.train_id }}</td>
                <td>{{ trainer.train_name }}</td>
                <td>{{ trainer.train_phone|default:"N/A" }}</td>
                <td>{{ trainer.train_email|default:"N/A" }}</td>
                <td>
                    <a href="{% url 'trainer_update' trainer.train_id %}" class="btn btn-sm btn-warning">{% trans "Edit" %}</a>
                    <a href="{% url 'trainer_delete' trainer.train_id %}" class="btn btn-sm btn-danger">{% trans "Delete" %}</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-warning" role="alert">
    {% trans "No trainers found." %}
</div>
{% endif %}
{% endblock %}
''',

    'location_list.html': '''{% extends "evaluation_app/base.html" %}
{% load i18n %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>{% trans "Location List" %}</h1>
    <a href="{% url 'location_create' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> {% trans "Add Location" %}
    </a>
</div>

{% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
{% endif %}

{% if locations %}
<div class="table-responsive">
    <table class="table table-striped table-hover">
        <thead class="table-dark">
            <tr>
                <th>{% trans "ID" %}</th>
                <th>{% trans "Location ID" %}</th>
                <th>{% trans "Location Name" %}</th>
                <th>{% trans "Actions" %}</th>
            </tr>
        </thead>
        <tbody>
            {% for location in locations %}
            <tr>
                <td>{{ location.id }}</td>
                <td>{{ location.locationid|default:"N/A" }}</td>
                <td>{{ location.locationname|default:"N/A" }}</td>
                <td>
                    <a href="{% url 'location_update' location.id %}" class="btn btn-sm btn-warning">{% trans "Edit" %}</a>
                    <a href="{% url 'location_delete' location.id %}" class="btn btn-sm btn-danger">{% trans "Delete" %}</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="alert alert-warning" role="alert">
    {% trans "No locations found." %}
</div>
{% endif %}
{% endblock %}
''',
}


def update_templates():
    """Update all template files with i18n translation tags."""
    template_dir = os.path.join('evaluation_app', 'templates', 'evaluation_app')
    
    if not os.path.exists(template_dir):
        print(f"Error: Template directory not found: {template_dir}")
        return False
    
    updated_count = 0
    
    for filename, content in TEMPLATE_UPDATES.items():
        filepath = os.path.join(template_dir, filename)
        
        if os.path.exists(filepath):
            # Backup original file
            backup_path = filepath + '.backup'
            if not os.path.exists(backup_path):
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                print(f"✓ Created backup: {filename}.backup")
            
            # Write new content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Updated: {filename}")
            updated_count += 1
        else:
            print(f"✗ Not found: {filename}")
    
    return updated_count > 0


def main():
    print("="*60)
    print("Updating Templates with i18n Translation Tags")
    print("="*60 + "\n")
    
    if update_templates():
        print("\n" + "="*60)
        print("✓ Templates updated successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Restart the Django development server")
        print("2. Use the language switcher to test all languages")
    else:
        print("\n" + "="*60)
        print("✗ Template update failed")
        print("="*60)


if __name__ == '__main__':
    main()
