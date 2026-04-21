"""
PDF generation service.

Encapsulates font registration, Arabic text processing, and shared drawing
helpers so that individual view PDFs stay thin and DRY.
"""
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display


# Arabic evaluation question labels (Q1-Q15)
EVALUATION_QUESTIONS = [
    "كان المدرب على دراية ومعرفة والمام كافي بمواضيع البرنامج",
    "نجح المدرب في ايصال المعلومة الى المتدربين بسهولة",
    "كان المدرب ذو مقدرة على احداث التفاعل والمشاركة البناءة وادارة النقاشات كما كان متمكنا في ادارة المدخلات والاستفسارات",
    "استطاع المدرب ربط المادة التدريبية بالواقع العملي للمتدربين",
    "استخدام المدرب وسائل وانشطة تدريبية مختلفة في تزويد المشاركين بالمهارات",
    "كانت المادة التدريبية المستخدمة ملائمة ومنسجمة مع اهداف البرنامج",
    "كانت المواضيع العلمية للبرنامج منظمة ومرتبطة بشكل منطقي مما سهل عملية التعلم المطلوبة",
    "سلامة وسلاسة اللغة التي كتبت بها المادة التدريبية",
    "المادة التي تم طرحها وتناولها غطت مفردات البرنامج",
    "التكنولوجيا الحديثة التي تم طرحها في البرنامج",
    "الاشعار بوقت تنفيذ البرنامج التدريبي ومكان انعقاد كان مناسب",
    "القاعات التدريبية وفرت بيئة تعليمية مريحة",
    "مكان ووقت وانعقاد البرنامج ساهم في زيادة فاعلية البرنامج",
    "تنظيم برنامج كان مناسبا من حيث (فترات الاستراحة ,مستلزمات التدريب ,الخ)",
    "مدة البرنامج كانت كافية لتغطية كافة اهداف الدورة التدريبية",
]

# Shared colour palette
PDF_COLORS = {
    'primary': colors.HexColor('#2c3e50'),
    'secondary': colors.HexColor('#3498db'),
    'accent': colors.HexColor('#27ae60'),
    'light_gray': colors.HexColor('#ecf0f1'),
    'separator': colors.HexColor('#95a5a6'),
}

_WINDOWS_FONTS = [
    ('C:\\Windows\\Fonts\\arial.ttf', 'C:\\Windows\\Fonts\\arialbd.ttf', 'Arial'),
    ('C:\\Windows\\Fonts\\tahoma.ttf', 'C:\\Windows\\Fonts\\tahomabd.ttf', 'Tahoma'),
    ('C:\\Windows\\Fonts\\times.ttf', 'C:\\Windows\\Fonts\\timesbd.ttf', 'Times'),
]

_registered_fonts: dict[str, tuple[str, str]] = {}


def get_arabic_fonts(base_dir: str | None = None) -> tuple[str, str]:
    """
    Return ``(normal_font, bold_font)`` names that support Arabic.
    Results are cached after the first successful registration.
    """
    cache_key = str(base_dir)
    if cache_key in _registered_fonts:
        return _registered_fonts[cache_key]

    for normal_path, bold_path, name in _WINDOWS_FONTS:
        if os.path.exists(normal_path):
            try:
                pdfmetrics.registerFont(TTFont(name, normal_path))
                bold_name = f'{name}-Bold'
                pdfmetrics.registerFont(
                    TTFont(bold_name, bold_path if os.path.exists(bold_path) else normal_path)
                )
                _registered_fonts[cache_key] = (name, bold_name)
                return name, bold_name
            except Exception:
                continue

    # Try bundled Amiri font if provided
    if base_dir:
        fonts_dir = os.path.join(base_dir, 'evaluation_app', 'static', 'evaluation_app', 'fonts')
        amiri = os.path.join(fonts_dir, 'Amiri-Regular.ttf')
        amiri_bold = os.path.join(fonts_dir, 'Amiri-Bold.ttf')
        if os.path.exists(amiri):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', amiri))
                bold_path = amiri_bold if os.path.exists(amiri_bold) else amiri
                pdfmetrics.registerFont(TTFont('Amiri-Bold', bold_path))
                _registered_fonts[cache_key] = ('Amiri', 'Amiri-Bold')
                return 'Amiri', 'Amiri-Bold'
            except Exception:
                pass

    _registered_fonts[cache_key] = ('Helvetica', 'Helvetica-Bold')
    return 'Helvetica', 'Helvetica-Bold'


def process_arabic_text(text: str) -> str:
    """Reshape Arabic text and apply the BiDi algorithm for correct PDF rendering."""
    if not text:
        return ''
    text = str(text)
    if any('\u0600' <= ch <= '\u06FF' for ch in text):
        return get_display(arabic_reshaper.reshape(text))
    return text


def get_evaluation_question_values(evaluation) -> list:
    return [
        evaluation.ev_q_1, evaluation.ev_q_2, evaluation.ev_q_3,
        evaluation.ev_q_4, evaluation.ev_q_5, evaluation.ev_q_6,
        evaluation.ev_q_7, evaluation.ev_q_8, evaluation.ev_q_9,
        evaluation.ev_q_10, evaluation.ev_q_11, evaluation.ev_q_12,
        evaluation.ev_q_13, evaluation.ev_q_14, evaluation.ev_q_15,
    ]
