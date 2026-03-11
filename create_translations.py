#!/usr/bin/env python
"""
Script to create and populate translation files for the Evaluation System.
Supports: Arabic (ar), Turkish (tr), Kurdish (ku), and English (en - default).
"""
import os
import subprocess
import sys

# Translation dictionary with all the strings used in templates
TRANSLATIONS = {
    # Base template
    "Evaluation System": {
        "ar": "نظام التقييم",
        "tr": "Değerlendirme Sistemi",
        "ku": "سیستەمی هەڵسەنگاندن"
    },
    "Toggle Sidebar": {
        "ar": "تبديل الشريط الجانبي",
        "tr": "Kenar Çubuğunu Değiştir",
        "ku": "گۆڕینی لاتەنیشت"
    },
    "Loading...": {
        "ar": "جاري التحميل...",
        "tr": "Yükleniyor...",
        "ku": "بارکردن..."
    },
    "Home": {
        "ar": "الرئيسية",
        "tr": "Ana Sayfa",
        "ku": "سەرەکی"
    },
    "Evaluations": {
        "ar": "التقييمات",
        "tr": "Değerlendirmeler",
        "ku": "هەڵسەنگاندنەکان"
    },
    "Professors": {
        "ar": "الأساتذة",
        "tr": "Profesörler",
        "ku": "مامۆستایان"
    },
    "Courses": {
        "ar": "المواد الدراسية",
        "tr": "Dersler",
        "ku": "دەرسەکان"
    },
    "Trainers": {
        "ar": "المدربين",
        "tr": "Eğitmenler",
        "ku": "ڕاهێنەران"
    },
    "Locations": {
        "ar": "المواقع",
        "tr": "Konumlar",
        "ku": "شوێنەکان"
    },
    "All Rights Reserved": {
        "ar": "جميع الحقوق محفوظة",
        "tr": "Tüm Hakları Saklıdır",
        "ku": "هەموو مافەکان پارێزراون"
    },
    "Privacy": {
        "ar": "الخصوصية",
        "tr": "Gizlilik",
        "ku": "تایبەتمەندی"
    },
    "Support": {
        "ar": "الدعم",
        "tr": "Destek",
        "ku": "پشتگیری"
    },
    "System Version": {
        "ar": "إصدار النظام",
        "tr": "Sistem Sürümü",
        "ku": "وەشانی سیستەم"
    },
    
    # Index page
    "Welcome to the Evaluation System": {
        "ar": "مرحباً بك في نظام التقييم",
        "tr": "Değerlendirme Sistemine Hoş Geldiniz",
        "ku": "بەخێربێیت بۆ سیستەمی هەڵسەنگاندن"
    },
    "This is a web application built with Django 5.2 and Python 3.13.7 and Bootstrap 5, connected to MSSQL 2012 database.": {
        "ar": "هذا تطبيق ويب مبني باستخدام Django 5.2 و Python 3.13.7 و Bootstrap 5، متصل بقاعدة بيانات MSSQL 2012.",
        "tr": "Bu, MSSQL 2012 veritabanına bağlı Django 5.2, Python 3.13.7 ve Bootstrap 5 ile oluşturulmuş bir web uygulamasıdır.",
        "ku": "ئەمە بەرنامەیەکی ئینتەرنێتە کە بە Django 5.2 و Python 3.13.7 و Bootstrap 5 دروستکراوە، بەستراوەتەوە بە بنکەی دراوەی MSSQL 2012."
    },
    "Use the navigation bar above to view data from your database tables.": {
        "ar": "استخدم شريط التنقل أعلاه لعرض البيانات من جداول قاعدة البيانات الخاصة بك.",
        "tr": "Veritabanı tablolarınızdaki verileri görüntülemek için yukarıdaki gezinme çubuğunu kullanın.",
        "ku": "بەکارهێنانی شریتی گەڕان لە سەرەوە بۆ بینینی داتاکان لە خشتەکانی بنکەی دراوەکەت."
    },
    "View all submitted evaluations.": {
        "ar": "عرض جميع التقييمات المقدمة.",
        "tr": "Gönderilen tüm değerlendirmeleri görüntüleyin.",
        "ku": "بینینی هەموو هەڵسەنگاندنە ناردراوەکان."
    },
    "View Evaluations": {
        "ar": "عرض التقييمات",
        "tr": "Değerlendirmeleri Görüntüle",
        "ku": "بینینی هەڵسەنگاندنەکان"
    },
    "Professors and Courses": {
        "ar": "الأساتذة والمواد الدراسية",
        "tr": "Profesörler ve Dersler",
        "ku": "مامۆستایان و دەرسەکان"
    },
    "Manage and view professors and courses information.": {
        "ar": "إدارة وعرض معلومات الأساتذة والمواد الدراسية.",
        "tr": "Profesör ve ders bilgilerini yönetin ve görüntüleyin.",
        "ku": "بەڕێوەبردن و بینینی زانیاریەکانی مامۆستایان و دەرسەکان."
    },
    "View Professors": {
        "ar": "عرض الأساتذة",
        "tr": "Profesörleri Görüntüle",
        "ku": "بینینی مامۆستایان"
    },
    "Trainers and Locations": {
        "ar": "المدربين والمواقع",
        "tr": "Eğitmenler ve Konumlar",
        "ku": "ڕاهێنەران و شوێنەکان"
    },
    "Manage and view trainers and locations data.": {
        "ar": "إدارة وعرض بيانات المدربين والمواقع.",
        "tr": "Eğitmen ve konum verilerini yönetin ve görüntüleyin.",
        "ku": "بەڕێوەبردن و بینینی داتاکانی ڕاهێنەران و شوێنەکان."
    },
    "View Trainers": {
        "ar": "عرض المدربين",
        "tr": "Eğitmenleri Görüntüle",
        "ku": "بینینی ڕاهێنەران"
    },
    
    # Common terms
    "ID": {
        "ar": "المعرف",
        "tr": "Kimlik",
        "ku": "ناسنامە"
    },
    "Name": {
        "ar": "الاسم",
        "tr": "İsim",
        "ku": "ناو"
    },
    "Phone": {
        "ar": "الهاتف",
        "tr": "Telefon",
        "ku": "تەلەفۆن"
    },
    "Email": {
        "ar": "البريد الإلكتروني",
        "tr": "E-posta",
        "ku": "ئیمەیڵ"
    },
    "Actions": {
        "ar": "الإجراءات",
        "tr": "İşlemler",
        "ku": "کردارەکان"
    },
    "Edit": {
        "ar": "تعديل",
        "tr": "Düzenle",
        "ku": "دەستکاری"
    },
    "Delete": {
        "ar": "حذف",
        "tr": "Sil",
        "ku": "سڕینەوە"
    },
    "Save": {
        "ar": "حفظ",
        "tr": "Kaydet",
        "ku": "هەڵگرتن"
    },
    "Cancel": {
        "ar": "إلغاء",
        "tr": "İptal",
        "ku": "پاشگەزبوونەوە"
    },
    "Add": {
        "ar": "إضافة",
        "tr": "Ekle",
        "ku": "زیادکردن"
    },
    "N/A": {
        "ar": "غير متوفر",
        "tr": "Mevcut değil",
        "ku": "بەردەست نییە"
    },
    
    # List pages
    "Evaluation List": {
        "ar": "قائمة التقييمات",
        "tr": "Değerlendirme Listesi",
        "ku": "لیستی هەڵسەنگاندنەکان"
    },
    "Add Evaluation": {
        "ar": "إضافة تقييم",
        "tr": "Değerlendirme Ekle",
        "ku": "زیادکردنی هەڵسەنگاندن"
    },
    "Professor List": {
        "ar": "قائمة الأساتذة",
        "tr": "Profesör Listesi",
        "ku": "لیستی مامۆستایان"
    },
    "Add Professor": {
        "ar": "إضافة أستاذ",
        "tr": "Profesör Ekle",
        "ku": "زیادکردنی مامۆستا"
    },
    "Course List": {
        "ar": "قائمة المواد الدراسية",
        "tr": "Ders Listesi",
        "ku": "لیستی دەرسەکان"
    },
    "Add Course": {
        "ar": "إضافة مادة دراسية",
        "tr": "Ders Ekle",
        "ku": "زیادکردنی دەرس"
    },
    "Trainer List": {
        "ar": "قائمة المدربين",
        "tr": "Eğitmen Listesi",
        "ku": "لیستی ڕاهێنەران"
    },
    "Add Trainer": {
        "ar": "إضافة مدرب",
        "tr": "Eğitmen Ekle",
        "ku": "زیادکردنی ڕاهێنەر"
    },
    "Location List": {
        "ar": "قائمة المواقع",
        "tr": "Konum Listesi",
        "ku": "لیستی شوێنەکان"
    },
    "Add Location": {
        "ar": "إضافة موقع",
        "tr": "Konum Ekle",
        "ku": "زیادکردنی شوێن"
    },
    "Date": {
        "ar": "التاريخ",
        "tr": "Tarih",
        "ku": "بەروار"
    },
    "Trainer": {
        "ar": "المدرب",
        "tr": "Eğitmen",
        "ku": "ڕاهێنەر"
    },
    "Professor": {
        "ar": "الأستاذ",
        "tr": "Profesör",
        "ku": "مامۆستا"
    },
    "Course": {
        "ar": "المادة الدراسية",
        "tr": "Ders",
        "ku": "دەرس"
    },
    "Location": {
        "ar": "الموقع",
        "tr": "Konum",
        "ku": "شوێن"
    },
    "No evaluations found.": {
        "ar": "لم يتم العثور على تقييمات.",
        "tr": "Değerlendirme bulunamadı.",
        "ku": "هیچ هەڵسەنگاندنێک نەدۆزرایەوە."
    },
    "Average Q1-15": {
        "ar": "متوسط السؤال 1-15",
        "tr": "Ortalama S1-15",
        "ku": "ناوەندی پ١-١٥"
    },
    "No notes": {
        "ar": "لا توجد ملاحظات",
        "tr": "Not yok",
        "ku": "تێبینی نییە"
    },
    "No professors found.": {
        "ar": "لم يتم العثور على أساتذة.",
        "tr": "Profesör bulunamadı.",
        "ku": "هیچ مامۆستایەک نەدۆزرایەوە."
    },
    "No courses found.": {
        "ar": "لم يتم العثور على مواد دراسية.",
        "tr": "Ders bulunamadı.",
        "ku": "هیچ دەرسێک نەدۆزرایەوە."
    },
    "No trainers found.": {
        "ar": "لم يتم العثور على مدربين.",
        "tr": "Eğitmen bulunamadı.",
        "ku": "هیچ ڕاهێنەرێک نەدۆزرایەوە."
    },
    "No locations found.": {
        "ar": "لم يتم العثور على مواقع.",
        "tr": "Konum bulunamadı.",
        "ku": "هیچ شوێنێک نەدۆزرایەوە."
    },
    
    # Form pages
    "Professor ID": {
        "ar": "معرف الأستاذ",
        "tr": "Profesör Kimliği",
        "ku": "ناسنامەی مامۆستا"
    },
    "Course ID": {
        "ar": "معرف المادة",
        "tr": "Ders Kimliği",
        "ku": "ناسنامەی دەرس"
    },
    "Course Name": {
        "ar": "اسم المادة",
        "tr": "Ders Adı",
        "ku": "ناوی دەرس"
    },
    "Trainer ID": {
        "ar": "معرف المدرب",
        "tr": "Eğitmen Kimliği",
        "ku": "ناسنامەی ڕاهێنەر"
    },
    "Location ID": {
        "ar": "معرف الموقع",
        "tr": "Konum Kimliği",
        "ku": "ناسنامەی شوێن"
    },
    "Location Name": {
        "ar": "اسم الموقع",
        "tr": "Konum Adı",
        "ku": "ناوی شوێن"
    },
    "Select Trainer": {
        "ar": "اختر مدرب",
        "tr": "Eğitmen Seç",
        "ku": "هەڵبژاردنی ڕاهێنەر"
    },
    "Select Professor": {
        "ar": "اختر أستاذ",
        "tr": "Profesör Seç",
        "ku": "هەڵبژاردنی مامۆستا"
    },
    "Select Course": {
        "ar": "اختر مادة دراسية",
        "tr": "Ders Seç",
        "ku": "هەڵبژاردنی دەرس"
    },
    "Select Location": {
        "ar": "اختر موقع",
        "tr": "Konum Seç",
        "ku": "هەڵبژاردنی شوێن"
    },
    "Questions (Rating 1-5)": {
        "ar": "الأسئلة (التقييم من 1-5)",
        "tr": "Sorular (Derecelendirme 1-5)",
        "ku": "پرسیارەکان (پلەبەندی ١-٥)"
    },
    "Notes": {
        "ar": "الملاحظات",
        "tr": "Notlar",
        "ku": "تێبینیەکان"
    },
    
    # Delete confirmations
    "Delete Evaluation": {
        "ar": "حذف تقييم",
        "tr": "Değerlendirme Sil",
        "ku": "سڕینەوەی هەڵسەنگاندن"
    },
    "Delete Professor": {
        "ar": "حذف أستاذ",
        "tr": "Profesör Sil",
        "ku": "سڕینەوەی مامۆستا"
    },
    "Delete Course": {
        "ar": "حذف مادة دراسية",
        "tr": "Ders Sil",
        "ku": "سڕینەوەی دەرس"
    },
    "Delete Trainer": {
        "ar": "حذف مدرب",
        "tr": "Eğitmen Sil",
        "ku": "سڕینەوەی ڕاهێنەر"
    },
    "Delete Location": {
        "ar": "حذف موقع",
        "tr": "Konum Sil",
        "ku": "سڕینەوەی شوێن"
    },
    "Are you sure you want to delete this evaluation?": {
        "ar": "هل أنت متأكد من حذف هذا التقييم؟",
        "tr": "Bu değerlendirmeyi silmek istediğinizden emin misiniz?",
        "ku": "دڵنیایت لە سڕینەوەی ئەم هەڵسەنگاندنە؟"
    },
    "Are you sure you want to delete this professor?": {
        "ar": "هل أنت متأكد من حذف هذا الأستاذ؟",
        "tr": "Bu profesörü silmek istediğinizden emin misiniz?",
        "ku": "دڵنیایت لە سڕینەوەی ئەم مامۆستایە؟"
    },
    "Are you sure you want to delete this course?": {
        "ar": "هل أنت متأكد من حذف هذه المادة الدراسية؟",
        "tr": "Bu dersi silmek istediğinizden emin misiniz?",
        "ku": "دڵنیایت لە سڕینەوەی ئەم دەرسە؟"
    },
    "Are you sure you want to delete this trainer?": {
        "ar": "هل أنت متأكد من حذف هذا المدرب؟",
        "tr": "Bu eğitmeni silmek istediğinizden emin misiniz?",
        "ku": "دڵنیایت لە سڕینەوەی ئەم ڕاهێنەرە؟"
    },
    "Are you sure you want to delete this location?": {
        "ar": "هل أنت متأكد من حذف هذا الموقع؟",
        "tr": "Bu konumu silmek istediğinizden emin misiniz?",
        "ku": "دڵنیایت لە سڕینەوەی ئەم شوێنە؟"
    },
    "Yes, Delete": {
        "ar": "نعم، حذف",
        "tr": "Evet, Sil",
        "ku": "بەڵێ، بیسڕەوە"
    },
    "Warning": {
        "ar": "تحذير",
        "tr": "Uyarı",
        "ku": "ئاگاداری"
    },
    "This will also affect related courses and evaluations.": {
        "ar": "سيؤثر هذا أيضاً على المواد الدراسية والتقييمات المرتبطة.",
        "tr": "Bu aynı zamanda ilgili dersleri ve değerlendirmeleri de etkileyecektir.",
        "ku": "ئەمە کاریگەری لەسەر دەرس و هەڵسەنگاندنە پەیوەندیدارەکانیش دەبێت."
    },
    "This will also affect related evaluations.": {
        "ar": "سيؤثر هذا أيضاً على التقييمات المرتبطة.",
        "tr": "Bu aynı zamanda ilgili değerlendirmeleri de etkileyecektir.",
        "ku": "ئەمە کاریگەری لەسەر هەڵسەنگاندنە پەیوەندیدارەکانیش دەبێت."
    },
}


def create_po_file(lang_code):
    """Create or update .po file for a specific language."""
    locale_dir = os.path.join('locale', lang_code, 'LC_MESSAGES')
    os.makedirs(locale_dir, exist_ok=True)
    
    po_file = os.path.join(locale_dir, 'django.po')
    
    # Create PO file header
    content = f'''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: Evaluation System 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-01-23 12:00+0000\\n"
"PO-Revision-Date: 2026-01-23 12:00+0000\\n"
"Last-Translator: Auto Generated\\n"
"Language-Team: {lang_code}\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

'''
    
    # Add translations
    for english, translations in TRANSLATIONS.items():
        content += f'msgid "{english}"\n'
        if lang_code in translations:
            content += f'msgstr "{translations[lang_code]}"\n'
        else:
            content += f'msgstr ""\n'
        content += '\n'
    
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created/Updated: {po_file}")
    return po_file


def compile_messages():
    """Compile all .po files to .mo files."""
    print("\n" + "="*60)
    print("Compiling translation files...")
    print("="*60)
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'compilemessages'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print("✓ Translation files compiled successfully!")
            if result.stdout:
                print(result.stdout)
        else:
            print("✗ Error compiling translation files:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Exception while compiling: {e}")
        return False
    
    return True


def main():
    print("="*60)
    print("Creating Translation Files for Evaluation System")
    print("="*60)
    print("\nLanguages: Arabic (ar), Turkish (tr), Kurdish (ku)")
    print(f"Total translations: {len(TRANSLATIONS)} strings\n")
    
    # Create .po files for each language
    languages = ['ar', 'tr', 'ku']
    
    for lang in languages:
        print(f"\nProcessing {lang}...")
        create_po_file(lang)
    
    # Compile messages
    if compile_messages():
        print("\n" + "="*60)
        print("✓ Translation system setup complete!")
        print("="*60)
        print("\nYou can now:")
        print("1. Run the development server: python manage.py runserver")
        print("2. Change language using the language switcher in the header")
        print("3. All text will automatically translate to the selected language")
        print("\nSupported languages:")
        print("  - English (en)")
        print("  - العربية (ar)")
        print("  - Türkçe (tr)")
        print("  - کوردی (ku)")
    else:
        print("\n" + "="*60)
        print("✗ Translation compilation failed")
        print("="*60)
        print("\nPlease ensure:")
        print("1. You're in the project root directory")
        print("2. Django is properly installed")
        print("3. manage.py exists")


if __name__ == '__main__':
    main()
