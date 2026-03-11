"""
AI Assistant Service for Evaluation System
Uses Ollama (free, local LLM) for intelligent features
Supports multiple languages: English and Arabic
"""
import json
from typing import List, Dict, Optional
from django.db.models import Avg, Count, Q
from django.utils.translation import get_language, gettext_lazy as _
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
        self.current_language = get_language() or 'en'
        
    def _get_language_instruction(self) -> str:
        """Get language instruction for AI based on current Django language"""
        if self.current_language in ['ar']:
            return "Respond in Arabic (العربية)."
        else:
            return "Respond in English."
        
    def is_available(self) -> bool:
        """Check if Ollama is installed and running"""
        if not self.available:
            return False
        try:
            ollama.list()
            return True
        except:
            return False
    
    def _generate_response(self, prompt: str, context: str = "") -> str:
        """Generate AI response using Ollama"""
        if not self.is_available():
            if self.current_language in ['ar']:
                return "مساعد AI غير متاح حالياً. يرجى تثبيت Ollama وتحميل نموذج."
            else:
                return "AI Assistant is not available. Please install Ollama and download a model."
        
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            if self.current_language in ['ar']:
                return f"خطأ في الذكاء الاصطناعي: {str(e)}"
            else:
                return f"AI Error: {str(e)}"
    
    def analyze_evaluation_notes(self, notes_list: List[str]) -> Dict:
        """
        Analyze evaluation notes to extract common themes and sentiments
        
        Args:
            notes_list: List of evaluation notes
            
        Returns:
            Dict with themes, sentiment, and summary
        """
        if not notes_list:
            if self.current_language in ['ar']:
                return {
                    'summary': 'لا توجد ملاحظات للتحليل',
                    'themes': [],
                    'sentiment': 'neutral'
                }
            else:
                return {
                    'summary': 'No notes to analyze',
                    'themes': [],
                    'sentiment': 'neutral'
                }
        
        combined_notes = "\n".join([f"- {note}" for note in notes_list if note])
        
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""قم بتحليل ملاحظات تقييم المدرس التالية وقدم:
1. المواضيع الرئيسية (اذكر 3-5 مواضيع رئيسية)
2. المشاعر العامة (إيجابية/محايدة/سلبية)
3. ملخص موجز (جملة إلى جملتان)

ملاحظات التقييم:
{combined_notes}

{lang_instruction}
الرجاء الرد بصيغة JSON:
{{
    "themes": ["موضوع1", "موضوع2", ...],
    "sentiment": "positive/neutral/negative",
    "summary": "نص الملخص"
}}
"""
        else:
            prompt = f"""Analyze these evaluation feedback notes and provide:
1. Main themes (list 3-5 key themes)
2. Overall sentiment (positive/neutral/negative)
3. Brief summary (2-3 sentences)

Evaluation Notes:
{combined_notes}

{lang_instruction}
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
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""أنشئ تقريراً شاملاً عن أداء هذا أستاذ:

الأستاذ: {professor_data.get('name', 'غير معروف')}
إجمالي التقييمات: {professor_data.get('total_evaluations', 0)}
متوسط التقييم: {professor_data.get('avg_rating', 0)}/5
المقررات التي يدرسها: {professor_data.get('courses_count', 0)}

متوسطات الأسئلة:
{json.dumps(professor_data.get('question_averages', {}), indent=2)}

الملاحظات الحديثة:
{chr(10).join(professor_data.get('recent_notes', []))}

{lang_instruction}
قدم:
1. ملخص الأداء العام
2. نقاط القوة (بناءً على الأسئلة ذات التقييمات العالية)
3. مجالات التحسين (بناءً على الأسئلة ذات التقييمات المنخفضة)
4. التوصيات القابلة للتطبيق
5. تحليل الاتجاهات

حافظ على الأسلوب الاحترافي والبناء.
"""
        else:
            prompt = f"""Generate a comprehensive performance report for this professor:

Professor: {professor_data.get('name', 'Unknown')}
Total Evaluations: {professor_data.get('total_evaluations', 0)}
Average Rating: {professor_data.get('avg_rating', 0)}/5
Courses Taught: {professor_data.get('courses_count', 0)}

Question Averages:
{json.dumps(professor_data.get('question_averages', {}), indent=2)}

Recent Feedback:
{chr(10).join(professor_data.get('recent_notes', []))}

{lang_instruction}
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
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            system_context = """أنت مساعد ذكاء اصطناعي مفيد لنظام إدارة التقييم.
يدير هذا النظام:
- الأساتذة والمقررات التدريسية
- جلسات التدريب في مواقع مختلفة
- المشاركين الذين يحضرون التدريب
- التقييمات مع 15 سؤال تقييم (مقياس 1-5) بالإضافة إلى الملاحظات
- رسائل الاتصال

تساعد المستخدمين على التنقل في النظام، وفهم بيانتهم، واتخاذ القرارات.
كن موجزاً مفيداً واحترافياً.
"""
        else:
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
        
        system_context += f"\n\n{lang_instruction}"
        
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
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""صنّف رسالة الاتصال هذه:

الموضوع: {subject}
الرسالة: {message}

قدم:
1. الفئة (استفسار عام، دعم فني، شكوى، اقتراح، سؤال عن التقييم)
2. الأولوية (منخفضة، متوسطة، عالية، عاجلة)
3. قالب الرد المقترح (موجز)

{lang_instruction}
الرجاء الرد بصيغة JSON:
{{
    "category": "اسم الفئة",
    "priority": "مستوى الأولوية",
    "suggested_response": "نص القالب"
}}
"""
        else:
            prompt = f"""Categorize this contact message:

Subject: {subject}
Message: {message}

Provide:
1. Category (general_inquiry, technical_support, complaint, suggestion, evaluation_question)
2. Priority (low, medium, high, urgent)
3. Suggested response template (brief)

{lang_instruction}
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
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""حلل بيانات التقييم هذه وتنبأ بالمشاكل المحتملة:

إحصائيات التقييم الحديثة:
{json.dumps(evaluation_data, indent=2)}

حدد:
1. علامات التحذير (الاتجاهات المتراجعة، التقييمات المنخفضة)
2. المشاكل المتوقعة في الأيام الثلاثين القادمة
3. التوصيات الوقائية

{lang_instruction}
الرجاء الرد بصيغة JSON:
{{
    "warnings": ["تحذير1", "تحذير2"],
    "predictions": ["تنبؤ1", "تنبؤ2"],
    "recommendations": ["توصية1", "توصية2"]
}}
"""
        else:
            prompt = f"""Analyze this evaluation data and predict potential issues:

Recent Evaluation Stats:
{json.dumps(evaluation_data, indent=2)}

Identify:
1. Warning signs (declining trends, low scores)
2. Predicted issues within next 30 days
3. Preventive recommendations

{lang_instruction}
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
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""أنشئ 5 أسئلة تقييم ذات صلة لـ:

نوع المقرر: {course_type}
السياق: {context}

يجب أن تكون الأسئلة:
- محددة بناءً على نوع المقرر
- استخدام مقياس 1-5
- التركيز على جوانب مختلفة (المحتوى، التسليم، المواد، إلخ)

{lang_instruction}
قدم الرد كمصفوفة JSON من النصوص.
"""
        else:
            prompt = f"""Generate 5 relevant evaluation questions for:

Course Type: {course_type}
Context: {context}

Questions should be:
- Specific to the course type
- Use 1-5 scale
- Focus on different aspects (content, delivery, materials, etc.)

{lang_instruction}
Return as JSON array of strings.
"""
        
        response = self._generate_response(prompt)
        
        try:
            return json.loads(response)
        except:
            if self.current_language in ['ar']:
                return [
                    "كيف تقيم جودة المقرر العامة؟",
                    "ما مدى فعالية طريقة التدريس التي اتبعها الأستاذ؟",
                    "ما مدى ملاءمة محتوى المقرر لاحتياجاتك؟",
                    "كيف تقيم مواد المقرر؟",
                    "ما مدى احتمال أن توصي بهذا المقرر للآخرين؟"
                ]
            else:
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
        
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""بالنظر إلى الإدخال الجزئي "{partial_data}" لحقل {field_type}،
اقترح 3-5 تكملات منسقة بشكل صحيح.

{lang_instruction}
قدم الرسالة كمصفوفة JSON من النصوص.
"""
        else:
            prompt = f"""Given partial input "{partial_data}" for a {field_type} field,
suggest 3-5 properly formatted completions.

{lang_instruction}
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
        lang_instruction = self._get_language_instruction()
        
        if self.current_language in ['ar']:
            prompt = f"""بناءً على إحصائيات نظام التقييم هذه، أنشئ 3-5 رؤى أساسية:

الإحصائيات:
{json.dumps(stats, indent=2)}

قدم رؤى قابلة للتطبيق تساعد المسؤولين على اتخاذ القرارات.
كن محدداً واذكر الأرقام حيث وجد.

{lang_instruction}
"""
        else:
            prompt = f"""Based on these evaluation system statistics, generate 3-5 key insights:

Statistics:
{json.dumps(stats, indent=2)}

Provide actionable insights that help administrators make decisions.
Be specific and mention numbers where relevant.

{lang_instruction}
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
