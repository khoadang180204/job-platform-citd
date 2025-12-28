"""
Auto Post Job Script - Tự động tạo job post với dữ liệu random
================================================================

Sử dụng:
    python manage.py auto_post_job --count 10
    python manage.py auto_post_job --category "IT"
    python manage.py auto_post_job --company_id 1 --count 5
"""

import json
import random
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from jobs.models import Job, JobCategory, Skill, Province, District, Ward, Requirement, Company


class Command(BaseCommand):
    help = 'Tự động tạo job post với dữ liệu random'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Số lượng job cần tạo'
        )
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='Tên danh mục công việc (nếu không chỉ định sẽ random)'
        )
        parser.add_argument(
            '--company_id',
            type=int,
            default=None,
            help='ID của company (bắt buộc)'
        )

    def handle(self, *args, **options):
        count = options['count']
        category_name = options['category']
        company_id = options['company_id']

        # Load JSON data
        base_path = os.path.join(settings.BASE_DIR, 'scripts')
        
        # Load location data
        with open(os.path.join(base_path, 'import_job_v2', 'tinh_tp.json'), 'r', encoding='utf-8') as f:
            provinces_data = json.load(f)
        
        with open(os.path.join(base_path, 'import_job_v2', 'quan_huyen.json'), 'r', encoding='utf-8') as f:
            districts_data = json.load(f)
        
        with open(os.path.join(base_path, 'import_job_v2', 'xa_phuong.json'), 'r', encoding='utf-8') as f:
            wards_data = json.load(f)

        # Load filter data
        with open(os.path.join(base_path, 'Import filter jobs', 'job_category.json'), 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        
        with open(os.path.join(base_path, 'Import filter jobs', 'skill.json'), 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
        
        with open(os.path.join(base_path, 'Import filter jobs', 'requirement.json'), 'r', encoding='utf-8') as f:
            requirements_data = json.load(f)

        # Get or validate company
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                self.stderr.write(f"Company với ID {company_id} không tồn tại!")
                self.stdout.write("Danh sách companies:")
                for c in Company.objects.all():
                    self.stdout.write(f"  - ID: {c.id}, Name: {c.name}")
                return
        else:
            companies = Company.objects.all()
            if not companies.exists():
                self.stderr.write("Không có company nào! Hãy tạo company trước.")
                return
            company = random.choice(list(companies))
            self.stdout.write(f"Sử dụng company: {company.name} (ID: {company.id})")

        # Job titles mẫu cho mỗi category
        job_titles = {
            "Nhân viên kinh doanh": [
                "Nhân viên kinh doanh", "Sales Executive", "Trưởng nhóm kinh doanh",
                "Nhân viên bán hàng", "Chuyên viên kinh doanh B2B", "Sales Manager"
            ],
            "Kế toán": [
                "Nhân viên kế toán", "Kế toán tổng hợp", "Kế toán trưởng",
                "Chuyên viên kế toán thuế", "Kế toán công nợ", "Kế toán nội bộ"
            ],
            "Marketing": [
                "Nhân viên Marketing", "Digital Marketing", "Content Creator",
                "SEO Specialist", "Brand Manager", "Marketing Executive"
            ],
            "Hành chính nhân sự": [
                "Nhân viên nhân sự", "HR Executive", "Chuyên viên tuyển dụng",
                "Hành chính văn phòng", "HR Manager", "C&B Specialist"
            ],
            "Chăm sóc khách hàng": [
                "Nhân viên CSKH", "Customer Service", "Call Center Agent",
                "Chuyên viên hỗ trợ khách hàng", "Trưởng nhóm CSKH"
            ],
            "Ngân hàng": [
                "Giao dịch viên ngân hàng", "Chuyên viên tín dụng",
                "Quan hệ khách hàng", "Thẩm định tín dụng"
            ],
            "IT": [
                "Lập trình viên", "Software Developer", "Backend Developer",
                "Frontend Developer", "Fullstack Developer", "QA Engineer",
                "DevOps Engineer", "Data Analyst", "UI/UX Designer"
            ],
            "Lao động phổ thông": [
                "Công nhân sản xuất", "Nhân viên kho", "Bảo vệ",
                "Nhân viên đóng gói", "Tạp vụ"
            ],
            "Senior": [
                "Senior Developer", "Senior Manager", "Team Leader",
                "Senior Consultant", "Senior Executive"
            ],
            "Kỹ sư xây dựng": [
                "Kỹ sư xây dựng", "Kỹ sư giám sát", "Kỹ sư dự toán",
                "Kỹ sư hiện trường", "Chỉ huy công trình"
            ],
            "Thiết kế đồ họa": [
                "Graphic Designer", "UI/UX Designer", "Brand Designer",
                "Motion Designer", "Creative Designer"
            ],
            "Bất động sản": [
                "Nhân viên môi giới BĐS", "Tư vấn bất động sản",
                "Quản lý sàn giao dịch", "Sales bất động sản"
            ],
            "Giáo dục": [
                "Giáo viên", "Trợ giảng", "Gia sư", "Giảng viên",
                "Quản lý giáo dục"
            ],
            "Telesales": [
                "Nhân viên Telesales", "Telesales Executive", "Trưởng nhóm Telesales",
                "Call Center Sales"
            ]
        }

        job_types = ["Full Time", "Part Time", "Remote", "Contract"]
        experience_levels = ["Fresher", "Junior", "Middle", "Senior", "Lead", "Manager"]

        # Descriptions mẫu
        descriptions = [
            "Chúng tôi đang tìm kiếm ứng viên năng động, có tinh thần học hỏi và mong muốn phát triển bản thân trong môi trường chuyên nghiệp.\n\nQuyền lợi:\n- Lương cạnh tranh theo năng lực\n- Bảo hiểm xã hội đầy đủ\n- Thưởng lễ tết hấp dẫn\n- Du lịch hàng năm",
            "Đây là cơ hội tuyệt vời để bạn phát triển sự nghiệp trong một môi trường làm việc năng động và sáng tạo.\n\nQuyền lợi:\n- Môi trường làm việc chuyên nghiệp\n- Cơ hội đào tạo và phát triển\n- Lương tháng 13\n- Team building định kỳ",
            "Công ty chúng tôi cam kết mang đến môi trường làm việc tốt nhất và cơ hội thăng tiến rõ ràng cho nhân viên.\n\nQuyền lợi:\n- Thu nhập hấp dẫn\n- Đãi ngộ tốt\n- Cơ hội thăng tiến rõ ràng\n- Làm việc linh hoạt",
            "Nếu bạn là người nhiệt huyết, có trách nhiệm và mong muốn đóng góp cho sự phát triển của công ty, hãy ứng tuyển ngay!\n\nQuyền lợi:\n- Lương thưởng hấp dẫn\n- Bảo hiểm đầy đủ\n- Cơ hội học hỏi",
        ]

        created_count = 0
        
        for i in range(count):
            try:
                # Chọn category
                if category_name:
                    selected_category_name = category_name
                else:
                    selected_category_name = random.choice(list(categories_data.keys()))
                
                # Lấy hoặc tạo JobCategory trong DB
                category_obj, _ = JobCategory.objects.get_or_create(name=selected_category_name)
                
                # Random Job Title
                if selected_category_name in job_titles:
                    title = random.choice(job_titles[selected_category_name])
                else:
                    title = f"Nhân viên {selected_category_name}"
                
                # Random location
                province_code = random.choice(list(provinces_data.keys()))
                province_info = provinces_data[province_code]
                
                # Tìm quận/huyện thuộc tỉnh
                district_codes = [code for code, info in districts_data.items() if info.get('parent_code') == province_code]
                district_code = random.choice(district_codes) if district_codes else None
                district_info = districts_data.get(district_code) if district_code else None
                
                # Tìm xã/phường thuộc quận
                ward_code = None
                ward_info = None
                if district_code:
                    ward_codes = [code for code, info in wards_data.items() if info.get('parent_code') == district_code]
                    if ward_codes:
                        ward_code = random.choice(ward_codes)
                        ward_info = wards_data.get(ward_code)
                
                # Lấy hoặc tạo Province, District, Ward trong DB
                province_obj, _ = Province.objects.get_or_create(
                    code=province_code,
                    defaults={
                        'name': province_info['name'],
                        'slug': province_info.get('slug', ''),
                        'type': province_info.get('type', 'tinh'),
                        'name_with_type': province_info.get('name_with_type', province_info['name'])
                    }
                )
                
                district_obj = None
                if district_info:
                    district_obj, _ = District.objects.get_or_create(
                        code=district_code,
                        defaults={
                            'name': district_info['name'],
                            'slug': district_info.get('slug', ''),
                            'type': district_info.get('type', 'huyen'),
                            'name_with_type': district_info.get('name_with_type', district_info['name']),
                            'path': district_info.get('path', ''),
                            'path_with_type': district_info.get('path_with_type', ''),
                            'parent_code': province_obj
                        }
                    )
                
                ward_obj = None
                if ward_info and district_obj:
                    ward_obj, _ = Ward.objects.get_or_create(
                        code=ward_code,
                        defaults={
                            'name': ward_info['name'],
                            'slug': ward_info.get('slug', ''),
                            'type': ward_info.get('type', 'xa'),
                            'name_with_type': ward_info.get('name_with_type', ward_info['name']),
                            'path': ward_info.get('path', ''),
                            'path_with_type': ward_info.get('path_with_type', ''),
                            'parent_code': district_obj
                        }
                    )

                # Random salary
                salary_min = random.choice([5, 8, 10, 12, 15, 20, 25, 30, None])
                salary_max = None
                if salary_min:
                    salary_max = salary_min + random.choice([3, 5, 8, 10, 15])

                # Random requirements
                experience = random.choice(requirements_data.get('experience', ['Không yêu cầu']))
                employment_type = random.choice(requirements_data.get('employment_type', ['Toàn thời gian']))

                # Build address detail (optional)
                address_detail = ""
                if ward_info:
                    address_detail = ward_info['name']

                # Create job
                job = Job.objects.create(
                    company=company,
                    title=title,
                    description=random.choice(descriptions),
                    requirements=f"- Kinh nghiệm: {experience}\n- Loại hình: {employment_type}",
                    responsibilities="- Thực hiện công việc theo yêu cầu\n- Báo cáo kết quả định kỳ\n- Phối hợp với các bộ phận liên quan",
                    address_detail=address_detail if address_detail else None,
                    province=province_obj,
                    district=district_obj,
                    ward=ward_obj,
                    job_type=random.choice(job_types),
                    experience_level=random.choice(experience_levels),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    category=category_obj,
                    is_active=True
                )

                # Add random skills từ category
                if selected_category_name in skills_data:
                    category_skills = skills_data[selected_category_name]
                    num_skills = random.randint(2, min(5, len(category_skills)))
                    selected_skills = random.sample(category_skills, num_skills)
                    
                    for skill_name in selected_skills:
                        skill_obj, _ = Skill.objects.get_or_create(
                            name=skill_name,
                            defaults={'category': category_obj}
                        )
                        job.required_skills.add(skill_obj)

                # Add random requirements
                req_skills = random.sample(requirements_data.get('skills', []), k=random.randint(1, 3))
                for req_name in req_skills:
                    req_obj, _ = Requirement.objects.get_or_create(name=req_name)
                    job.job_requirements.add(req_obj)

                job.save()
                created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{created_count}/{count}] Đã tạo: {title} - {province_info['name']} - {selected_category_name}"
                    )
                )

            except Exception as e:
                self.stderr.write(f"Lỗi khi tạo job: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Đã tạo thành công {created_count}/{count} jobs!"))
