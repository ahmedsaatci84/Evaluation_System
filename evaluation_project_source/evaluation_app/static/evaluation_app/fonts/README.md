# Arabic Fonts for PDF Generation

## Current Implementation

The PDF generation system now automatically uses Windows system fonts that support Arabic:
1. **Arial** (primary choice - excellent Arabic support)
2. **Tahoma** (secondary choice - good Arabic support)  
3. **Times New Roman** (tertiary choice)

These fonts are typically pre-installed on Windows systems and provide full Arabic character support.

## Optional: Adding Custom Arabic Fonts

If you want to use a specific Arabic font or if system fonts are not available, you can download and add Arabic fonts to this directory.

### Recommended Arabic Fonts

1. **Amiri** (Traditional Arabic font)
   - Download from: https://github.com/aliftype/amiri/releases
   - Files needed: `Amiri-Regular.ttf`, `Amiri-Bold.ttf`

2. **Noto Sans Arabic** (Modern Arabic font)
   - Download from: https://fonts.google.com/noto/specimen/Noto+Sans+Arabic
   - Files needed: `NotoSansArabic-Regular.ttf`, `NotoSansArabic-Bold.ttf`

3. **Scheherazade New** (Classical Arabic font)
   - Download from: https://software.sil.org/scheherazade/
   - Files needed: `ScheherazadeNew-Regular.ttf`, `ScheherazadeNew-Bold.ttf`

### Installation Steps

1. Download your preferred font files (.ttf format)
2. Copy the font files to this directory (`evaluation_app/static/evaluation_app/fonts/`)
3. The system will automatically detect and use `Amiri-Regular.ttf` and `Amiri-Bold.ttf` if present
4. For other fonts, update the `professor_download_pdf` function in `views.py` to register them

### Font Priority

The system tries fonts in this order:
1. Windows Arial (if available)
2. Windows Tahoma (if available)
3. Windows Times (if available)
4. Custom Amiri font (if placed in this directory)
5. Helvetica (fallback - won't display Arabic properly)

## Testing

After adding fonts, test the PDF generation by:
1. Navigate to the Professor List page
2. Click the PDF download button for any professor
3. Verify that Arabic text displays correctly (not as squares)
