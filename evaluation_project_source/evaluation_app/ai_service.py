"""
AI Assistant Service for Evaluation System
Uses Ollama (free, local LLM) for intelligent features
"""
import json
from typing import List, Dict, Optional
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class EvaluationAI:
    """AI Assistant for Evaluation System using Ollama"""
    
    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize AI service
        Args:
            model_name: Ollama model to use (llama3.2, mistral, gemma2, etc.)
        """
        self.model_name = model_name
        self.available = OLLAMA_AVAILABLE
        
    def is_available(self) -> bool:
        """Check if Ollama is installed and running"""
        if not self.available:
            return False
        try:
            # Try to list models - this checks if Ollama service is running
            models = ollama.list()
            # Check if we have the required model
            if hasattr(models, 'models'):
                model_names = [m.model for m in models.models]
                # Check if our model exists (with or without :latest tag)
                has_model = any(
                    self.model_name in name 
                    for name in model_names
                )
                return has_model
            return False
        except Exception as e:
            # Check if it's a connection error (service not running)
            # vs import error (module not installed)
            return False
    
    def _generate_response(self, prompt: str, context: str = "") -> str:
        """Generate AI response using Ollama"""
        if not self.is_available():
            return "AI Assistant is not available. Please make sure Ollama is running (run 'ollama serve' in terminal)."
        
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Try chat API first (preferred for conversational models)
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {
                            'role': 'user',
                            'content': full_prompt
                        }
                    ]
                )
                return response['message']['content']
            except:
                # Fallback to generate API
                response = ollama.generate(
                    model=self.model_name,
                    prompt=full_prompt,
                    stream=False
                )
                return response['response']
        except Exception as e:
            error_msg = str(e)
            if 'connection' in error_msg.lower():
                return "AI Error: Cannot connect to Ollama. Please make sure Ollama is running (run 'ollama serve' in a terminal)."
            elif 'model' in error_msg.lower() or 'not found' in error_msg.lower():
                return f"AI Error: Model '{self.model_name}' not found. Please run 'ollama pull {self.model_name}' first."
            else:
                return f"AI Error: {error_msg}"
    
    def analyze_evaluation_notes(self, notes_list: List[str]) -> Dict:
        """
        Analyze evaluation notes to extract common themes and sentiments
        
        Args:
            notes_list: List of evaluation notes
            
        Returns:
            Dict with themes, sentiment, and summary
        """
        if not notes_list:
            return {
                'summary': 'No notes to analyze',
                'themes': [],
                'sentiment': 'neutral'
            }
        
        combined_notes = "\n".join([f"- {note}" for note in notes_list if note])
        
        prompt = f"""Analyze these evaluation feedback notes and provide:
1. Main themes (list 3-5 key themes)
2. Overall sentiment (positive/neutral/negative)
3. Brief summary (2-3 sentences)

Evaluation Notes:
{combined_notes}

Respond in JSON format:
{{
    "themes": ["theme1", "theme2", ...],
    "sentiment": "positive/neutral/negative",
    "summary": "brief summary text"
}}
"""
        
        response = self._generate_response(prompt)
        
        try:
            # Try to parse JSON response
            result = json.loads(response)
            return result
        except:
            # If not JSON, return raw response
            return {
                'summary': response,
                'themes': [],
                'sentiment': 'neutral'
            }
    
    def generate_professor_report(self, professor_data: Dict) -> str:
        """
        Generate comprehensive AI report for a professor
        
        Args:
            professor_data: Dict containing professor info and evaluation stats
            
        Returns:
            Formatted report text
        """
        prompt = f"""Generate a comprehensive performance report for this professor:

Professor: {professor_data.get('name', 'Unknown')}
Total Evaluations: {professor_data.get('total_evaluations', 0)}
Average Rating: {professor_data.get('avg_rating', 0)}/5
Courses Taught: {professor_data.get('courses_count', 0)}

Question Averages:
{json.dumps(professor_data.get('question_averages', {}), indent=2)}

Recent Feedback:
{chr(10).join(professor_data.get('recent_notes', []))}

Provide:
1. Overall Performance Summary
2. Strengths (based on high-scoring questions)
3. Areas for Improvement (based on low-scoring questions)
4. Actionable Recommendations
5. Trend Analysis

Keep it professional and constructive.
"""
        
        return self._generate_response(prompt)
    
    def chatbot_response(self, user_question: str, context_data: Dict = None) -> str:
        """
        Answer user questions about the evaluation system
        
        Args:
            user_question: User's question
            context_data: Optional context (user role, recent data, etc.)
            
        Returns:
            AI response
        """
        system_context = """You are a helpful AI assistant for an Evaluation Management System.
This system manages:
- Professors and their courses
- Training sessions at different locations
- Participants who attend training
- Evaluations with 15 rating questions (1-5 scale) plus notes
- Contact messages

You help users navigate the system, understand their data, and make decisions.
Be concise, helpful, and professional.
"""
        
        if context_data:
            system_context += f"\n\nContext: {json.dumps(context_data)}"
        
        return self._generate_response(user_question, system_context)
    
    def categorize_contact_message(self, message: str, subject: str = "") -> Dict:
        """
        Auto-categorize contact messages
        
        Args:
            message: Message content
            subject: Message subject
            
        Returns:
            Dict with category, priority, and suggested response
        """
        prompt = f"""Categorize this contact message:

Subject: {subject}
Message: {message}

Provide:
1. Category (general_inquiry, technical_support, complaint, suggestion, evaluation_question)
2. Priority (low, medium, high, urgent)
3. Suggested response template (brief)

Respond in JSON format:
{{
    "category": "category_name",
    "priority": "priority_level",
    "suggested_response": "template text"
}}
"""
        
        response = self._generate_response(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                'category': 'general_inquiry',
                'priority': 'medium',
                'suggested_response': response
            }
    
    def predict_evaluation_issues(self, evaluation_data: Dict) -> Dict:
        """
        Predict potential issues based on evaluation patterns
        
        Args:
            evaluation_data: Recent evaluation statistics
            
        Returns:
            Dict with predictions and recommendations
        """
        prompt = f"""Analyze this evaluation data and predict potential issues:

Recent Evaluation Stats:
{json.dumps(evaluation_data, indent=2)}

Identify:
1. Warning signs (declining trends, low scores)
2. Predicted issues within next 30 days
3. Preventive recommendations

Respond in JSON format:
{{
    "warnings": ["warning1", "warning2"],
    "predictions": ["prediction1", "prediction2"],
    "recommendations": ["rec1", "rec2"]
}}
"""
        
        response = self._generate_response(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                'warnings': [],
                'predictions': [],
                'recommendations': [response]
            }
    
    def suggest_evaluation_questions(self, course_type: str, context: str = "") -> List[str]:
        """
        Generate relevant evaluation questions for specific course types
        
        Args:
            course_type: Type of course
            context: Additional context
            
        Returns:
            List of suggested questions
        """
        prompt = f"""Generate 5 relevant evaluation questions for:

Course Type: {course_type}
Context: {context}

Questions should be:
- Specific to the course type
- Use 1-5 scale
- Focus on different aspects (content, delivery, materials, etc.)

Return as JSON array of strings.
"""
        
        response = self._generate_response(prompt)
        
        try:
            return json.loads(response)
        except:
            return [
                "How would you rate the overall course quality?",
                "How effective was the professor's teaching method?",
                "How relevant was the course content to your needs?",
                "How would you rate the course materials?",
                "How likely are you to recommend this course?"
            ]
    
    def auto_complete_data(self, partial_data: str, field_type: str) -> List[str]:
        """
        Provide auto-completion suggestions for data entry
        
        Args:
            partial_data: Partial input from user
            field_type: Type of field (name, email, phone, etc.)
            
        Returns:
            List of suggestions
        """
        # This would typically use a fine-tuned model with your data
        # For now, it provides intelligent formatting suggestions
        
        prompt = f"""Given partial input "{partial_data}" for a {field_type} field,
suggest 3-5 properly formatted completions.

Return as JSON array of strings.
"""
        
        response = self._generate_response(prompt)
        
        try:
            return json.loads(response)
        except:
            return []
    
    def translate_content(self, text: str, target_language: str) -> str:
        """
        Translate content to target language
        
        Args:
            text: Text to translate
            target_language: Target language (ar, tr, ckb, ku)
            
        Returns:
            Translated text
        """
        language_names = {
            'ar': 'Arabic',
            'tr': 'Turkish',
            'ckb': 'Central Kurdish (Sorani)',
            'ku': 'Kurdish'
        }
        
        prompt = f"""Translate this text to {language_names.get(target_language, target_language)}:

{text}

Provide only the translation, no explanations.
"""
        
        return self._generate_response(prompt)
    
    def generate_insights_dashboard(self, stats: Dict) -> str:
        """
        Generate natural language insights for dashboard
        
        Args:
            stats: Dashboard statistics
            
        Returns:
            Human-readable insights
        """
        prompt = f"""Based on these evaluation system statistics, generate 3-5 key insights:

Statistics:
{json.dumps(stats, indent=2)}

Provide actionable insights that help administrators make decisions.
Be specific and mention numbers where relevant.
"""
        
        return self._generate_response(prompt)


class AIAssistantHelper:
    """Helper functions for integrating AI into Django views"""
    
    @staticmethod
    def get_professor_ai_data(professor_obj):
        """Prepare professor data for AI analysis"""
        from .models import EvaluationTab
        from django.db.models import Avg
        
        evaluations = EvaluationTab.objects.filter(
            train__professor=professor_obj
        )
        
        question_averages = {}
        for i in range(1, 16):
            field_name = f'ev_q_{i}'
            avg = evaluations.aggregate(avg=Avg(field_name))['avg']
            question_averages[f'Q{i}'] = round(avg, 2) if avg else 0
        
        recent_notes = list(
            evaluations.exclude(ev_q_notes__isnull=True)
            .exclude(ev_q_notes='')
            .values_list('ev_q_notes', flat=True)[:10]
        )
        
        return {
            'name': professor_obj.profname,
            'total_evaluations': evaluations.count(),
            'avg_rating': round(sum(question_averages.values()) / 15, 2) if question_averages else 0,
            'courses_count': professor_obj.course_set.count(),
            'question_averages': question_averages,
            'recent_notes': recent_notes
        }
    
    @staticmethod
    def get_dashboard_stats():
        """Get stats for AI dashboard insights"""
        from .models import (
            EvaluationTab, ProfessorTbl, CourseTbl, 
            ParticipantTbl, ContactMessage
        )
        from django.db.models import Avg, Count
        from datetime import datetime, timedelta
        
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        
        return {
            'total_evaluations': EvaluationTab.objects.count(),
            'recent_evaluations': EvaluationTab.objects.filter(
                train__train_date__gte=thirty_days_ago
            ).count(),
            'total_professors': ProfessorTbl.objects.count(),
            'total_courses': CourseTbl.objects.count(),
            'total_participants': ParticipantTbl.objects.count(),
            'avg_overall_rating': EvaluationTab.objects.aggregate(
                avg=Avg('ev_q_1')  # You can calculate overall average
            )['avg'],
            'unread_messages': ContactMessage.get_unread_count(),
        }
