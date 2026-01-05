import os
import sys
import json
import django

# Setup Django
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) 
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsite.settings')
django.setup()

from jobs.models import Province, District, Ward

# Đường dẫn tới thư mục chứa dữ liệu JSON
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')


def load_json_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_provinces():
    """Import Tỉnh/Thành phố"""
    print("Importing Provinces (Tỉnh/Thành phố)...")
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
    
    print(f"   Imported {count} tỉnh/thành phố")
    return count


def import_districts():
    """Import Quận/Huyện"""
    print("Importing Districts (Quận/Huyện)...")
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
            print(f"   Tỉnh/Thành phố không tồn tại cho quận/huyện {info.get('name')} (parent_code: {parent_code})")
    
    print(f"   Imported {count} quận/huyện, {errors} errors")
    return count


def import_wards():
    """Import Xã/Phường"""
    print("Importing Wards (Xã/Phường)...")
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
        
        if (idx + 1) % batch_size == 0:
            print(f"   Progress: {idx + 1}/{total} ({((idx + 1) / total * 100):.1f}%)")
    
    print(f"   Imported {count} xã/phường, {errors} errors")
    return count


def clear_old_data():
    """Xóa dữ liệu cũ trước khi import"""
    print("Đang xóa dữ liệu cũ...")
    Ward.objects.all().delete()
    District.objects.all().delete()
    Province.objects.all().delete()
    print("Đã xóa dữ liệu cũ")


def main():
    print("=" * 60)
    print("IMPORT LOCATION DATA - Việt Nam")
    print("=" * 60)
    
    clear_old_data()
    
    provinces = import_provinces()
    districts = import_districts()
    wards = import_wards()
    
    print("=" * 60)
    print("Hoàn thành!")
    print(f"Tỉnh/Thành phố: {provinces}")
    print(f"Quận/Huyện: {districts}")
    print(f"Xã/Phường: {wards}")
    print("=" * 60)


if __name__ == '__main__':
    main()
