import os, sys
import json
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Add đường dẫn tới project Django
DJANGO_PROJECT_PATH = r"D:\HỌC TẬP\ĐỒ ÁN TỐT NGHIỆP\job-platform"
sys.path.insert(0, DJANGO_PROJECT_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsite.settings')
django.setup()

from jobs.models import JobCategory, JobPosition, Skill, Requirement

# Đường dẫn tới files JSON
JOB_CATEGORY_FILE = os.path.join(BASE_DIR, 'job_category.json')
SKILL_FILE = os.path.join(BASE_DIR, 'skill.json')
REQUIREMENT_FILE = os.path.join(BASE_DIR, 'requirement.json')

def import_job_categories():
    """Import danh mục ngành nghề từ job_category.json"""
    print("\n" + "="*50)
    print("📁 IMPORTING JOB CATEGORIES")
    print("="*50)
    
    try:
        with open(JOB_CATEGORY_FILE, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {JOB_CATEGORY_FILE}")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    
    created_count = 0
    position_count = 0
    
    for category_name, positions in categories_data.items():
        try:
            # Tạo category
            category, created = JobCategory.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Danh mục: {category_name}'}
            )
            
            if created:
                created_count += 1
                print(f"✅ Created category: {category.name}")
            else:
                print(f"ℹ️ Category already exists: {category.name}")
            
            # Tạo positions cho category này
            for position_name in positions:
                pos, pos_created = JobPosition.objects.get_or_create(
                    name=position_name,
                    category=category,
                    defaults={'description': f'{position_name} - {category_name}'}
                )
                
                if pos_created:
                    position_count += 1
                    print(f"   ✅ Created position: {position_name}")
        
        except Exception as e:
            print(f"❌ Error importing {category_name}: {str(e)}")
    
    print(f"\n✅ Job Categories Import Complete!")
    print(f"   Total categories created: {created_count}")
    print(f"   Total positions created: {position_count}")
    return True

def import_skills():
    """Import kỹ năng từ skill.json"""
    print("\n" + "="*50)
    print("💼 IMPORTING SKILLS")
    print("="*50)
    
    try:
        with open(SKILL_FILE, 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {SKILL_FILE}")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    
    created_count = 0
    
    for category_name, skills in skills_data.items():
        print(f"\n📂 Category: {category_name}")
        
        for skill_name in skills:
            try:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={
                        'category': category_name,
                        'description': f'{skill_name} - {category_name}'
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"   ✅ Created: {skill.name}")
                else:
                    print(f"   ℹ️ Already exists: {skill.name}")
            
            except Exception as e:
                print(f"   ❌ Error importing {skill_name}: {str(e)}")
    
    print(f"\n✅ Skills Import Complete!")
    print(f"   Total skills created: {created_count}")
    return True

def import_requirements():
    """Import yêu cầu công việc từ requirement.json"""
    print("\n" + "="*50)
    print("📋 IMPORTING REQUIREMENTS")
    print("="*50)
    
    try:
        with open(REQUIREMENT_FILE, 'r', encoding='utf-8') as f:
            requirements_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {REQUIREMENT_FILE}")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    
    created_count = 0
    
    # Map từ key JSON sang requirement_type trong model
    type_mapping = {
        'experience': 'experience',
        'education_level': 'education_level',
        'language': 'language',
        'employment_type': 'employment_type',
        'work_mode': 'work_mode',
        'gender_requirement': 'gender',
        'age_requirement': 'age',
        'skills': 'skills',
        'technical_skills': 'technical_skills',
        'salary_range': 'salary_range',
        'benefits': 'benefits',
        'probation_time': 'probation_time',
    }
    
    for req_key, req_values in requirements_data.items():
        # Get requirement type từ mapping
        req_type = type_mapping.get(req_key)
        
        if not req_type:
            print(f"⚠️ Unknown requirement type: {req_key}")
            continue
        
        print(f"\n📂 Type: {req_key}")
        
        for req_value in req_values:
            try:
                requirement, created = Requirement.objects.get_or_create(
                    requirement_type=req_type,
                    name=req_value,
                    defaults={'description': req_value}
                )
                
                if created:
                    created_count += 1
                    print(f"   ✅ Created: {req_value}")
                else:
                    print(f"   ℹ️ Already exists: {req_value}")
            
            except Exception as e:
                print(f"   ❌ Error importing {req_value}: {str(e)}")
    
    print(f"\n✅ Requirements Import Complete!")
    print(f"   Total requirements created: {created_count}")
    return True

def main():
    """Main import function"""
    print("\n" + "🚀 STARTING DATA IMPORT ".center(50, "="))
    
    # Import data
    success = True
    success = import_job_categories() and success
    success = import_skills() and success
    success = import_requirements() and success
    
    if success:
        print("\n" + "✅ ALL DATA IMPORTED SUCCESSFULLY! ".center(50, "="))
    else:
        print("\n" + "❌ SOME IMPORTS FAILED ".center(50, "="))
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    from jobs.models import JobCategory, JobPosition, Skill, Requirement
    print(f"✅ Total Job Categories: {JobCategory.objects.count()}")
    print(f"✅ Total Job Positions: {JobPosition.objects.count()}")
    print(f"✅ Total Skills: {Skill.objects.count()}")
    print(f"✅ Total Requirements: {Requirement.objects.count()}")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()