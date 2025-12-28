"""
Script import dữ liệu Tỉnh/Thành phố, Quận/Huyện, Xã/Phường
Phiên bản TIẾP TỤC - Không xóa dữ liệu cũ, chỉ thêm mới
Chạy: venv/Scripts/python scripts/import_locations_continue.py
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
    """Import Tỉnh/Thành phố - Chỉ thêm mới, không xóa"""
    print("📍 Importing Provinces (Tỉnh/Thành phố)...")
    data = load_json_file('tinh_tp.json')
    
    created_count = 0
    updated_count = 0
    
    for code, info in data.items():
        _, created = Province.objects.update_or_create(
            code=code,
            defaults={
                'name': info.get('name', ''),
                'slug': info.get('slug', ''),
                'type': info.get('type', ''),
                'name_with_type': info.get('name_with_type', info.get('name', '')),
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    print(f"   ✅ Provinces: {created_count} created, {updated_count} updated")
    return created_count


def import_districts():
    """Import Quận/Huyện - Chỉ thêm mới, không xóa"""
    print("📍 Importing Districts (Quận/Huyện)...")
    data = load_json_file('quan_huyen.json')
    
    created_count = 0
    updated_count = 0
    errors = 0
    
    for code, info in data.items():
        parent_code = info.get('parent_code')
        try:
            province = Province.objects.get(code=parent_code)
            _, created = District.objects.update_or_create(
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
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Province.DoesNotExist:
            errors += 1
    
    print(f"   ✅ Districts: {created_count} created, {updated_count} updated, {errors} errors")
    return created_count


def import_wards():
    """Import Xã/Phường - Chỉ thêm mới, không xóa"""
    print("📍 Importing Wards (Xã/Phường)...")
    data = load_json_file('xa_phuong.json')
    
    created_count = 0
    updated_count = 0
    errors = 0
    batch_size = 1000
    total = len(data)
    
    # Lấy danh sách các ward đã tồn tại
    existing_wards = set(Ward.objects.values_list('code', flat=True))
    print(f"   📊 Existing wards: {len(existing_wards)}")
    
    for idx, (code, info) in enumerate(data.items()):
        parent_code = info.get('parent_code')
        try:
            district = District.objects.get(code=parent_code)
            _, created = Ward.objects.update_or_create(
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
            if created:
                created_count += 1
            else:
                updated_count += 1
        except District.DoesNotExist:
            errors += 1
        
        # Progress indicator
        if (idx + 1) % batch_size == 0:
            print(f"   📊 Progress: {idx + 1}/{total} ({((idx + 1) / total * 100):.1f}%) - Created: {created_count}, Updated: {updated_count}")
    
    print(f"   ✅ Wards: {created_count} created, {updated_count} updated, {errors} errors")
    return created_count


def main():
    print("=" * 60)
    print("🚀 IMPORT LOCATION DATA - Việt Nam (CONTINUE MODE)")
    print("   Chế độ tiếp tục: Không xóa dữ liệu cũ")
    print("=" * 60)
    
    # Check current data
    print("\n📊 Current data status:")
    print(f"   - Provinces: {Province.objects.count()}")
    print(f"   - Districts: {District.objects.count()}")
    print(f"   - Wards: {Ward.objects.count()}")
    print()
    
    # Import in order (respecting foreign key relationships)
    provinces = import_provinces()
    districts = import_districts()
    wards = import_wards()
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETED!")
    print(f"   📊 Final data count:")
    print(f"   - Provinces: {Province.objects.count()}")
    print(f"   - Districts: {District.objects.count()}")
    print(f"   - Wards: {Ward.objects.count()}")
    print("=" * 60)


if __name__ == '__main__':
    main()
