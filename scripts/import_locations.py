"""
Script import dữ liệu Tỉnh/Thành phố, Quận/Huyện, Xã/Phường
Chạy: python manage.py shell < scripts/import_locations.py
Hoặc: venv/Scripts/python manage.py runscript import_locations
"""
import os
import sys
import json
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsite.settings')
django.setup()

from jobs.models import Province, District, Ward


def load_json_file(filename):
    """Load JSON file with UTF-8 encoding"""
    filepath = os.path.join(os.path.dirname(__file__), 'import_job_v2', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_provinces():
    """Import Tỉnh/Thành phố"""
    print("📍 Importing Provinces (Tỉnh/Thành phố)...")
    data = load_json_file('tinh_tp.json')
    
    count = 0
    for code, info in data.items():
        Province.objects.update_or_create(
            code=code,
            defaults={
                'name': info.get('name', ''),
                'slug': info.get('slug', ''),
                'type': info.get('type', ''),
                'name_with_type': info.get('name_with_type', info.get('name', '')),
            }
        )
        count += 1
    
    print(f"   ✅ Imported {count} provinces")
    return count


def import_districts():
    """Import Quận/Huyện"""
    print("📍 Importing Districts (Quận/Huyện)...")
    data = load_json_file('quan_huyen.json')
    
    count = 0
    errors = 0
    for code, info in data.items():
        parent_code = info.get('parent_code')
        try:
            province = Province.objects.get(code=parent_code)
            District.objects.update_or_create(
                code=code,
                defaults={
                    'name': info.get('name', ''),
                    'slug': info.get('slug', ''),
                    'type': info.get('type', ''),
                    'name_with_type': info.get('name_with_type', info.get('name', '')),
                    'path': info.get('path', ''),
                    'path_with_type': info.get('path_with_type', ''),
                    'parent_code': province,
                }
            )
            count += 1
        except Province.DoesNotExist:
            errors += 1
            print(f"   ⚠️ Province not found for district {info.get('name')} (parent_code: {parent_code})")
    
    print(f"   ✅ Imported {count} districts, {errors} errors")
    return count


def import_wards():
    """Import Xã/Phường"""
    print("📍 Importing Wards (Xã/Phường)...")
    data = load_json_file('xa_phuong.json')
    
    count = 0
    errors = 0
    batch_size = 1000
    total = len(data)
    
    for idx, (code, info) in enumerate(data.items()):
        parent_code = info.get('parent_code')
        try:
            district = District.objects.get(code=parent_code)
            Ward.objects.update_or_create(
                code=code,
                defaults={
                    'name': info.get('name', ''),
                    'slug': info.get('slug', ''),
                    'type': info.get('type', ''),
                    'name_with_type': info.get('name_with_type', info.get('name', '')),
                    'path': info.get('path', ''),
                    'path_with_type': info.get('path_with_type', ''),
                    'parent_code': district,
                }
            )
            count += 1
        except District.DoesNotExist:
            errors += 1
        
        # Progress indicator
        if (idx + 1) % batch_size == 0:
            print(f"   📊 Progress: {idx + 1}/{total} ({((idx + 1) / total * 100):.1f}%)")
    
    print(f"   ✅ Imported {count} wards, {errors} errors")
    return count


def clear_old_data():
    """Xóa dữ liệu cũ trước khi import"""
    print("🗑️ Clearing old location data...")
    Ward.objects.all().delete()
    District.objects.all().delete()
    Province.objects.all().delete()
    print("   ✅ Old data cleared")


def main():
    print("=" * 60)
    print("🚀 IMPORT LOCATION DATA - Việt Nam")
    print("=" * 60)
    
    # Clear old data
    clear_old_data()
    
    # Import in order (respecting foreign key relationships)
    provinces = import_provinces()
    districts = import_districts()
    wards = import_wards()
    
    print("=" * 60)
    print(f"✅ COMPLETED!")
    print(f"   📍 Provinces: {provinces}")
    print(f"   📍 Districts: {districts}")
    print(f"   📍 Wards: {wards}")
    print("=" * 60)


if __name__ == '__main__':
    main()
