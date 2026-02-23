# check_settings.py
import os
import sys
from django.conf import settings

print("=== DJANGO SETTINGS DEBUG ===")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
print(f"STATICFILES_FINDERS: {settings.STATICFILES_FINDERS}")

print("\n=== UNFOLD SETTINGS ===")
unfold_settings = getattr(settings, 'UNFOLD', {})
print(f"UNFOLD: {unfold_settings}")

print("\n=== TEMPLATES ===")
print(f"TEMPLATES DIRS: {settings.TEMPLATES[0]['DIRS']}")
print(f"TEMPLATES APP_DIRS: {settings.TEMPLATES[0]['APP_DIRS']}")

print("\n=== INSTALLED APPS (Unfold related) ===")
unfold_apps = [app for app in settings.INSTALLED_APPS if 'unfold' in app]
print(f"Unfold apps: {unfold_apps}")

print("\n=== CHECKING UNFOLD TEMPLATES ===")
try:
    from django.template.loader import get_template
    template = get_template('unfold/base.html')
    print(f"✅ Unfold template found: {template.origin.name}")
except Exception as e:
    print(f"❌ Unfold template not found: {e}")

print("\n=== CHECKING UNFOLD STATIC FILES ===")
from django.contrib.staticfiles import finders
css_file = finders.find('unfold/css/styles.css')
if css_file:
    print(f"✅ Unfold CSS found: {css_file}")
else:
    print("❌ Unfold CSS not found")