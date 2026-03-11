# AI Assistant Integration Examples

## Quick Integration Examples

### Example 1: Add AI Button to Professor Detail Page

Add this to `professor_detail.html`:

```html
<!-- AI Report Button -->
<div class="card mt-3">
    <div class="card-header bg-gradient-purple text-white">
        <h5><i class="fas fa-robot"></i> AI Insights</h5>
    </div>
    <div class="card-body">
        <button class="btn btn-primary" onclick="generateAIReport()">
            <i class="fas fa-magic"></i> Generate AI Performance Report
        </button>
        <div id="ai-report-container" class="mt-3"></div>
    </div>
</div>

<script>
function generateAIReport() {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    
    fetch(`/ai/professor/{{ professor.profid }}/report/`)
        .then(response => response.json())
        .then(data => {
            if (data.report) {
                document.getElementById('ai-report-container').innerHTML = `
                    <div class="alert alert-info">
                        <h6>AI Analysis:</h6>
                        <pre style="white-space: pre-wrap;">${data.report}</pre>
                    </div>
                `;
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Performance Report';
        })
        .catch(error => {
            alert('Error generating report: ' + error);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Performance Report';
        });
}
</script>
```

### Example 2: Add AI Insights to Dashboard

Add this to `dashboard.html`:

```html
<!-- AI Insights Card -->
<div class="col-md-12 mb-4">
    <div class="card">
        <div class="card-header bg-gradient-purple text-white">
            <h5><i class="fas fa-brain"></i> AI Insights</h5>
        </div>
        <div class="card-body">
            <div id="ai-insights-container">
                <button class="btn btn-primary" onclick="loadAIInsights()">
                    <i class="fas fa-lightbulb"></i> Generate Smart Insights
                </button>
            </div>
        </div>
    </div>
</div>

<script>
function loadAIInsights() {
    const container = document.getElementById('ai-insights-container');
    container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Analyzing data...</p></div>';
    
    fetch('/ai/dashboard/insights/')
        .then(response => response.json())
        .then(data => {
            if (data.insights) {
                container.innerHTML = `
                    <div class="alert alert-success">
                        <h6><i class="fas fa-robot"></i> AI Analysis:</h6>
                        <div style="white-space: pre-wrap;">${data.insights}</div>
                    </div>
                    <button class="btn btn-sm btn-secondary" onclick="loadAIInsights()">
                        <i class="fas fa-redo"></i> Refresh Insights
                    </button>
                `;
            } else {
                container.innerHTML = `
                    <div class="alert alert-warning">${data.insights || 'AI not available'}</div>
                `;
            }
        });
}

// Auto-load on page load
document.addEventListener('DOMContentLoaded', function() {
    // Uncomment to auto-load insights
    // loadAIInsights();
});
</script>
```

### Example 3: Analyze Evaluation Notes in Evaluation List

Add this to `evaluation_list.html`:

```html
<!-- Add this button above the table -->
<div class="mb-3">
    <button class="btn btn-info" onclick="analyzeSelectedNotes()">
        <i class="fas fa-chart-line"></i> Analyze Selected Evaluations with AI
    </button>
</div>

<!-- Add checkboxes to each row in your table -->
<td>
    <input type="checkbox" class="eval-checkbox" value="{{ evaluation.id }}">
</td>

<script>
function analyzeSelectedNotes() {
    const checkboxes = document.querySelectorAll('.eval-checkbox:checked');
    const ids = Array.from(checkboxes).map(cb => cb.value);
    
    if (ids.length === 0) {
        alert('Please select at least one evaluation');
        return;
    }
    
    fetch('/ai/analyze-notes/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ evaluation_ids: ids })
    })
    .then(response => response.json())
    .then(data => {
        if (data.analysis) {
            alert(`AI Analysis:\\n\\n` +
                  `Sentiment: ${data.analysis.sentiment}\\n` +
                  `Themes: ${data.analysis.themes.join(', ')}\\n\\n` +
                  `Summary: ${data.analysis.summary}`);
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
```

### Example 4: Smart Contact Message Categorization

Add this to `contact_list.html` or `contact_detail.html`:

```html
<button class="btn btn-sm btn-info" onclick="categorizeMessage({{ contact.id }})">
    <i class="fas fa-tags"></i> Auto-Categorize
</button>

<script>
function categorizeMessage(contactId) {
    fetch(`/ai/contact/${contactId}/categorize/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.categorization) {
            const cat = data.categorization;
            alert(`Category: ${cat.category}\\n` +
                  `Priority: ${cat.priority}\\n\\n` +
                  `Suggested Response:\\n${cat.suggested_response}`);
        }
    });
}
</script>
```

### Example 5: Backend Integration in Views

Add AI analysis to your existing views:

```python
# In views.py

from .ai_service import EvaluationAI, AIAssistantHelper

def professor_detail(request, pk):
    professor = get_object_or_404(ProfessorTbl, pk=pk)
    
    # Get AI analysis
    ai = EvaluationAI()
    ai_available = ai.is_available()
    ai_report = None
    
    if ai_available:
        professor_data = AIAssistantHelper.get_professor_ai_data(professor)
        ai_report = ai.generate_professor_report(professor_data)
    
    context = {
        'professor': professor,
        'ai_available': ai_available,
        'ai_report': ai_report,
        # ... other context
    }
    return render(request, 'evaluation_app/professor_detail.html', context)
```

Then in template:

```html
{% if ai_available and ai_report %}
<div class="alert alert-info">
    <h6><i class="fas fa-robot"></i> AI Analysis</h6>
    <pre>{{ ai_report }}</pre>
</div>
{% endif %}
```

## Custom AI Functions

### Create New AI Function

1. Add method to `EvaluationAI` class in `ai_service.py`:

```python
def suggest_course_improvements(self, course_data: Dict) -> List[str]:
    """Suggest improvements for a course"""
    prompt = f"""Based on this course data:
    Name: {course_data['name']}
    Average Rating: {course_data['avg_rating']}
    Common Issues: {course_data['issues']}
    
    Suggest 5 specific improvements.
    Return as JSON array of strings.
    """
    
    response = self._generate_response(prompt)
    try:
        return json.loads(response)
    except:
        return []
```

2. Add view in `ai_views.py`:

```python
@login_required
@require_http_methods(["GET"])
def ai_course_improvements(request, course_id):
    try:
        course = CourseTbl.objects.get(pk=course_id)
        ai = EvaluationAI()
        
        if not ai.is_available():
            return JsonResponse({'error': 'AI not available'}, status=503)
        
        # Prepare course data
        course_data = {
            'name': course.coursename,
            'avg_rating': 4.2,  # Calculate from evaluations
            'issues': ['time management', 'materials']
        }
        
        improvements = ai.suggest_course_improvements(course_data)
        
        return JsonResponse({
            'improvements': improvements
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

3. Add URL in `urls.py`:

```python
path('ai/course/<int:course_id>/improvements/', ai_views.ai_course_improvements, name='ai_course_improvements'),
```

4. Use in template:

```html
<button onclick="getCourseImprovements({{ course.cid }})">
    Get AI Suggestions
</button>

<script>
function getCourseImprovements(courseId) {
    fetch(`/ai/course/${courseId}/improvements/`)
        .then(response => response.json())
        .then(data => {
            const list = data.improvements.map(i => `<li>${i}</li>`).join('');
            alert('Suggested Improvements:\n' + data.improvements.join('\n'));
        });
}
</script>
```

## Tips

1. **Always check AI availability** before calling AI functions
2. **Show loading states** - AI responses can take 2-10 seconds
3. **Provide fallbacks** - Have manual options when AI is unavailable
4. **Cache results** - Store common queries to reduce API calls
5. **Handle errors gracefully** - AI might fail, always have error handling

## Testing AI Features

```python
# In Django shell
python manage.py shell

from evaluation_app.ai_service import EvaluationAI, AIAssistantHelper

# Test chatbot
ai = EvaluationAI()
print(ai.is_available())
response = ai.chatbot_response("What is this system for?")
print(response)

# Test note analysis
notes = ["Great course", "Needs improvement", "Excellent professor"]
analysis = ai.analyze_evaluation_notes(notes)
print(analysis)
```

These examples show you exactly how to integrate AI features into your existing pages!
