import os, sys
import json
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Add đường dẫn tới project Django
DJANGO_PROJECT_PATH = r"D:\HỌC TẬP\ĐỒ ÁN TỐT NGHIỆP\job-platform"
sys.path.insert(0, DJANGO_PROJECT_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsite.settings')
django.setup()

from jobs.models import City

# Đường dẫn tới file cities.json
CITIES_FILE = f'{BASE_DIR}\\cities.json'

def import_cities():
    """Import cities từ cities.json vào database"""
    
    try:
        with open(CITIES_FILE, 'r', encoding='utf-8') as f:
            cities_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {CITIES_FILE}")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return
    
    # Xóa các city cũ (optional)
    City.objects.all().delete()
    print("🗑️ Deleted old cities")
    
    # Import cities mới
    created_count = 0
    for city_data in cities_data:
        try:
            city, created = City.objects.get_or_create(
                city=city_data['city'],
                defaults={
                    'province': city_data.get('province', ''),
                    'area': city_data.get('area', ''),
                    'population': city_data.get('population', '')
                }
            )
            
            if created:
                created_count += 1
                print(f"✅ Created: {city.city}")
            else:
                print(f"ℹ️ Already exists: {city.city}")
        
        except Exception as e:
            print(f"❌ Error importing {city_data.get('city')}: {str(e)}")
    
    print(f"\n✅ Import completed! Total created: {created_count}")

if __name__ == '__main__':
    import_cities()