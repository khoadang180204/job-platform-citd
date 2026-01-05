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

from jobs.models import JobCategory, JobPosition, Skill, Requirement

# Đường dẫn tới thư mục chứa dữ liệu JSON
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
JOB_CATEGORY_FILE = os.path.join(DATA_DIR, 'job_category.json')
SKILL_FILE = os.path.join(DATA_DIR, 'skill.json')
REQUIREMENT_FILE = os.path.join(DATA_DIR, 'requirement.json')

# Import danh mục ngành nghề
def import_job_categories():
    print("\n" + "="*50)
    print("Thêm danh mục ngành nghề")
    print("="*50)
    
    try:
        with open(JOB_CATEGORY_FILE, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
    except FileNotFoundError:
        print(f"Không tìm thấy file: {JOB_CATEGORY_FILE}")
        return False
    except json.JSONDecodeError:
        print("Không đúng định dạng JSON file")
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
                print(f"Tạo danh mục: {category.name}")
            else:
                print(f"ℹDanh mục đã tồn tại: {category.name}")
            
            # Tạo positions cho category này
            for position_name in positions:
                pos, pos_created = JobPosition.objects.get_or_create(
                    name=position_name,
                    category=category,
                    defaults={'description': f'{position_name} - {category_name}'}
                )
                
                if pos_created:
                    position_count += 1
                    print(f"   Tạo vị trí: {position_name}")
        
        except Exception as e:
            print(f"Lỗi khi thêm {category_name}: {str(e)}")
    
    print(f"\nHoàn thành!")
    print(f"   Tổng danh mục tạo: {created_count}")
    print(f"   Tổng vị trí tạo: {position_count}")
    return True

# Import kỹ năng
def import_skills():
    print("\n" + "="*50)
    print("Thêm kỹ năng")
    print("="*50)
    
    try:
        with open(SKILL_FILE, 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
    except FileNotFoundError:
        print(f"Không tìm thấy file: {SKILL_FILE}")
        return False
    except json.JSONDecodeError:
        print("Không đúng định dạng JSON file")
        return False
    
    created_count = 0
    
    for category_name, skills in skills_data.items():
        print(f"\nThêm danh mục kỹ năng: {category_name}")
        
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
                    print(f"Tạo kỹ năng: {skill.name}")
                else:
                    print(f"Kỹ năng đã tồn tại: {skill.name}")
            
            except Exception as e:
                print(f"Lỗi khi thêm {skill_name}: {str(e)}")
    
    print(f"\nHoàn thành!")
    print(f"   Tổng kỹ năng tạo: {created_count}")
    return True

# Import yêu cầu công việc
def import_requirements():
    print("\n" + "="*50)
    print("Thêm yêu cầu")
    print("="*50)
    
    try:
        with open(REQUIREMENT_FILE, 'r', encoding='utf-8') as f:
            requirements_data = json.load(f)
    except FileNotFoundError:
        print(f"Không tìm thấy file: {REQUIREMENT_FILE}")
        return False
    except json.JSONDecodeError:
        print("Không đúng định dạng JSON file")
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
        req_type = type_mapping.get(req_key)
        
        if not req_type:
            print(f"Loại yêu cầu không hợp lệ: {req_key}")
            continue
        
        print(f"\nLoại yêu cầu: {req_key}")
        
        for req_value in req_values:
            try:
                requirement, created = Requirement.objects.get_or_create(
                    requirement_type=req_type,
                    name=req_value,
                    defaults={'description': req_value}
                )
                
                if created:
                    created_count += 1
                    print(f"Tạo yêu cầu: {req_value}")
                else:
                    print(f"Yêu cầu đã tồn tại: {req_value}")
            
            except Exception as e:
                print(f"Lỗi khi thêm {req_value}: {str(e)}")
    
    print(f"\nHoàn thành!")
    print(f"   Tổng yêu cầu tạo: {created_count}")
    return True


def main():
    print("\n" + "BẮT ĐẦU IMPORT DỮ LIỆU ".center(50, "="))
    
    # Import data
    success = True
    success = import_job_categories() and success
    success = import_skills() and success
    success = import_requirements() and success
    
    if success:
        print("\nHoàn thành!")
    else:
        print("\nLỗi khi import dữ liệu!")
    
    # Summary
    print("\n" + "="*50)
    print("Tóm tắt")
    print("="*50)
    print(f"Tổng danh mục: {JobCategory.objects.count()}")
    print(f"Tổng vị trí: {JobPosition.objects.count()}")
    print(f"Tổng kỹ năng: {Skill.objects.count()}")
    print(f"Tổng yêu cầu: {Requirement.objects.count()}")
    print("="*50 + "\n")


if __name__ == '__main__':
    main()