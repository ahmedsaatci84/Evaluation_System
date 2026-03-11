#!/usr/bin/env python
"""
Manually compile .po files to .mo files using polib.
"""
import os
import polib

def compile_po_to_mo(po_path):
    """Compile a single .po file to .mo format."""
    try:
        po = polib.pofile(po_path)
        mo_path = po_path.replace('.po', '.mo')
        po.save_as_mofile(mo_path)
        print(f"✓ Compiled: {po_path} -> {mo_path}")
        return True
    except Exception as e:
        print(f"✗ Error compiling {po_path}: {e}")
        return False

def main():
    print("="*60)
    print("Compiling Translation Files (.po to .mo)")
    print("="*60 + "\n")
    
    locale_dir = 'locale'
    compiled_count = 0
    
    if not os.path.exists(locale_dir):
        print(f"✗ Error: '{locale_dir}' directory not found!")
        return
    
    # Walk through locale directory
    for lang_code in os.listdir(locale_dir):
        lang_path = os.path.join(locale_dir, lang_code)
        if not os.path.isdir(lang_path):
            continue
            
        lc_messages_path = os.path.join(lang_path, 'LC_MESSAGES')
        if not os.path.exists(lc_messages_path):
            continue
            
        po_file = os.path.join(lc_messages_path, 'django.po')
        if os.path.exists(po_file):
            if compile_po_to_mo(po_file):
                compiled_count += 1
    
    print("\n" + "="*60)
    if compiled_count > 0:
        print(f"✓ Successfully compiled {compiled_count} language file(s)!")
    else:
        print("✗ No .po files found to compile")
    print("="*60)

if __name__ == '__main__':
    main()
