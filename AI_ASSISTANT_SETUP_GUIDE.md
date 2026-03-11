# AI Assistant Setup Guide

The AI Assistant has been successfully integrated into your Evaluation System! This guide will help you install and configure it.

## 🎯 Features Added

### 1. **AI Chatbot Widget**
- Floating chatbot button on every authenticated page
- Real-time conversation with AI
- Quick action buttons for common queries
- Beautiful, responsive UI

### 2. **Intelligent Analysis**
- **Evaluation Analysis**: Analyze evaluation notes to extract themes and sentiments
- **Professor Reports**: Generate comprehensive AI-powered performance reports
- **Dashboard Insights**: Get natural language insights from your dashboard statistics
- **Contact Categorization**: Auto-categorize and prioritize contact messages

### 3. **API Endpoints**
- `/ai/chatbot/` - Chat with AI assistant
- `/ai/professor/<id>/report/` - Generate professor report
- `/ai/dashboard/insights/` - Get dashboard insights
- `/ai/analyze-notes/` - Analyze evaluation notes
- `/ai/contact/<id>/categorize/` - Categorize contact messages
- `/ai/status/` - Check AI availability

## 📦 Installation Steps

### Step 1: Install Ollama (AI Runtime)

#### **For Windows:**
1. Download Ollama from: https://ollama.com/download/windows
2. Run the installer (OllamaSetup.exe)
3. Ollama will automatically start in the background
4. Verify installation by opening PowerShell and running:
   ```powershell
   ollama --version
   ```

#### **For Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### **For macOS:**
```bash
brew install ollama
```

### Step 2: Download AI Model

Choose one of these models (recommended: llama3.2):

```bash
# Llama 3.2 - Best balance (recommended, ~2GB)
ollama pull llama3.2

# OR Mistral - Great for analysis (~4GB)
ollama pull mistral

# OR Phi-3 - Smallest/fastest (~1.5GB)
ollama pull phi3

# OR Gemma 2 - Google's model (~5GB)
ollama pull gemma2
```

### Step 3: Install Python Package

```powershell
# Make sure you're in your project directory
cd D:\evaluation_project_source

# Install the ollama Python package
pip install ollama
```

### Step 4: Test Installation

```powershell
# Test Ollama is running
ollama list

# Test in Python
python -c "import ollama; print('Ollama is ready!')"
```

### Step 5: Run Your Django Server

```powershell
python manage.py runserver
```

Visit your site and look for the **purple robot button** in the bottom-right corner! 🤖

## 🎨 How to Use

### **1. Chatbot Widget**
- Click the purple robot button (bottom-right)
- Type questions like:
  - "What are the average evaluation scores?"
  - "Which professors have the highest ratings?"
  - "Show me recent feedback"
  - "How can I improve my courses?"

### **2. Quick Actions**
Use the quick action buttons for instant insights:
- **Average Scores** - Get overall evaluation statistics
- **Recent Activity** - See recent evaluations
- **Issues** - Identify professors or courses needing attention

### **3. Professor Reports (API)**
```javascript
// Call from your JavaScript
fetch('/ai/professor/1/report/')
    .then(response => response.json())
    .then(data => {
        console.log(data.report);
    });
```

### **4. Dashboard Insights (API)**
```javascript
fetch('/ai/dashboard/insights/')
    .then(response => response.json())
    .then(data => {
        console.log(data.insights);
    });
```

## ⚙️ Configuration

### Change AI Model
Edit [ai_service.py](evaluation_app/ai_service.py#L18):

```python
def __init__(self, model_name: str = "llama3.2"):  # Change to "mistral", "phi3", etc.
```

### Customize Chatbot Behavior
Edit the `chatbot_response` method in [ai_service.py](evaluation_app/ai_service.py#L146) to change:
- System instructions
- Response style
- Available features

## 🔧 Troubleshooting

### Issue: "AI Assistant is not available"
**Solution:**
1. Check if Ollama is running:
   ```powershell
   ollama list
   ```
2. If not running, start it:
   ```powershell
   # Windows: Start from Start Menu or
   & "C:\Users\YOUR_USERNAME\AppData\Local\Programs\Ollama\ollama.exe" serve
   ```

### Issue: "Model not found"
**Solution:**
```bash
ollama pull llama3.2
```

### Issue: Badge shows red (offline)
**Solution:**
- Restart Ollama service
- Check if model is downloaded: `ollama list`
- Check network connection

### Issue: Slow responses
**Solution:**
- Use a smaller model (phi3 instead of mistral)
- Increase your system RAM
- Close unnecessary applications

## 🚀 Advanced Features

### Add Custom AI Functions

Edit [ai_service.py](evaluation_app/ai_service.py) and add new methods:

```python
def predict_course_popularity(self, course_data: Dict) -> Dict:
    """Predict which courses will be most popular"""
    prompt = f"Based on this data: {course_data}, predict..."
    return self._generate_response(prompt)
```

Then create a view in [ai_views.py](evaluation_app/ai_views.py):

```python
@login_required
def ai_predict_popularity(request, course_id):
    # Your implementation
    pass
```

### Integrate with Evaluation Detail Pages

Add AI insights to specific professor or course pages:

```html
<!-- In professor_detail.html -->
<button onclick="generateAIReport({{ professor.pk }})">
    <i class="fas fa-robot"></i> Generate AI Report
</button>

<script>
function generateAIReport(professorId) {
    fetch(`/ai/professor/${professorId}/report/`)
        .then(response => response.json())
        .then(data => {
            alert(data.report);
        });
}
</script>
```

## 📊 Example Use Cases

### 1. Automated Insights for Administrators
```python
# Get insights every morning
stats = AIAssistantHelper.get_dashboard_stats()
ai = EvaluationAI()
insights = ai.generate_insights_dashboard(stats)
# Email insights to admin
```

### 2. Real-time Evaluation Analysis
```python
# When new evaluation is submitted
notes = ["Great course!", "Needs improvement"]
ai = EvaluationAI()
analysis = ai.analyze_evaluation_notes(notes)
# Display themes to professor
```

### 3. Smart Contact Message Routing
```python
# When contact message arrives
ai = EvaluationAI()
category = ai.categorize_contact_message(message, subject)
if category['priority'] == 'urgent':
    # Send immediate notification
```

## 💡 Best Practices

1. **Start with llama3.2** - Best balance of speed and quality
2. **Monitor resource usage** - AI models use RAM, especially larger ones
3. **Cache responses** - Store common queries to reduce AI calls
4. **Set timeouts** - Prevent long waits for users
5. **Provide fallbacks** - Always have manual options when AI is unavailable

## 🔒 Privacy & Security

- ✅ **100% Local** - All AI runs on your server, no data sent to external APIs
- ✅ **No API Costs** - Completely free, unlimited usage
- ✅ **Private Data** - Evaluation data never leaves your infrastructure
- ✅ **Offline Capable** - Works without internet connection

## 📈 Performance

### Model Comparison:

| Model      | Size  | Speed     | Quality | RAM Required |
|------------|-------|-----------|---------|--------------|
| llama3.2   | 2GB   | Fast      | High    | 4GB          |
| mistral    | 4GB   | Medium    | Highest | 8GB          |
| phi3       | 1.5GB | Fastest   | Good    | 3GB          |
| gemma2     | 5GB   | Slower    | High    | 10GB         |

## 🎓 Learning Resources

- Ollama Documentation: https://github.com/ollama/ollama
- Model Library: https://ollama.com/library
- Python SDK: https://github.com/ollama/ollama-python

## 🆘 Support

If you encounter issues:
1. Check Ollama service is running
2. Verify model is downloaded
3. Check browser console for errors
4. Review Django logs for API errors

## 🎉 You're All Set!

Your AI Assistant is ready to help improve your evaluation system. Start by clicking the robot button and asking questions!

**Happy Evaluating! 🚀**
