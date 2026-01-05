from typing import Dict, List, Set, Optional
from django.db.models import QuerySet

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Error: Chưa cài đặt sklearn")

from .models import Job, Skill, UserSkillProfile


# ============================================================
# SKILL MATCHING
# ============================================================

# So sánh skills của user với skills yêu cầu của job.
def get_matched_skills(user_skill_ids: Set[int], job_skill_ids: Set[int]) -> Set[int]:
    return user_skill_ids.intersection(job_skill_ids)

# Tính phần trăm skills trùng khớp.
def calculate_skill_match_score(user_skill_ids: Set[int], job_skill_ids: Set[int]) -> int:
    if not job_skill_ids:
        return 0
    
    matched = len(user_skill_ids.intersection(job_skill_ids))
    total_required = len(job_skill_ids)
    
    return int((matched / total_required) * 100)


# ============================================================
# TF-IDF TEXT MATCHING
# ============================================================

# Tính độ tương đồng giữa 2 văn bản sử dụng TF-IDF và Cosine Similarity.
def calculate_text_similarity(text1: str, text2: str) -> float:
    if not SKLEARN_AVAILABLE:
        return 0.0
    
    if not text1 or not text2:
        return 0.0
    
    try:
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_features=5000
        )
        
        tfidf_matrix = vectorizer.fit_transform([text1.lower(), text2.lower()])
        
        # Cosine Similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
        
    except Exception as e:
        print(f"TF-IDF similarity error: {e}")
        return 0.0


# ============================================================
# MAIN MATCHING SERVICE
# ============================================================

# Service để tính điểm matching giữa User Skill Profile và Job.
class JobMatcher:
    def __init__(self, user_profile: Optional[UserSkillProfile] = None):
        self.user_profile = user_profile
        self._user_skill_ids = set()
        self._user_text = ""
        
        if user_profile:
            self._load_profile_data()
    
    def _load_profile_data(self):
        """Load data từ user profile."""
        if not self.user_profile:
            return
        
        self._user_skill_ids = set(self.user_profile.skills.values_list('id', flat=True))
        
        parts = []
        if self.user_profile.bio:
            parts.append(self.user_profile.bio)
        parts.append(self.user_profile.get_skills_text())
        parts.append(self.user_profile.get_categories_text())
        
        self._user_text = ' '.join(parts)
    
    def calculate_job_match(self, job: Job) -> Dict:
        """
        Tính điểm matching cho một job.
        """
        job_skill_ids = set(job.required_skills.values_list('id', flat=True))
        
        job_text_parts = [job.title, job.description or '']
        if job.requirements:
            job_text_parts.append(job.requirements)
        if job.responsibilities:
            job_text_parts.append(job.responsibilities)

        job_skills_text = ' '.join([s.name for s in job.required_skills.all()])
        job_text_parts.append(job_skills_text)
        job_text = ' '.join(job_text_parts)
        
        skill_score = calculate_skill_match_score(self._user_skill_ids, job_skill_ids)
        
        text_score = 0
        if self._user_text:
            similarity = calculate_text_similarity(self._user_text, job_text)
            text_score = int(similarity * 100)
        
        combined_score = int(skill_score * 0.6 + text_score * 0.4)
        
        matched_skill_ids = get_matched_skills(self._user_skill_ids, job_skill_ids)
        matched_skills = list(Skill.objects.filter(id__in=matched_skill_ids).values('id', 'name'))
        
        return {
            'matching_score': combined_score,
            'skill_score': skill_score,
            'text_score': text_score,
            'matched_skills': matched_skills,
            'matched_skill_count': len(matched_skill_ids),
            'total_required_skills': len(job_skill_ids),
        }
    
    # Tính điểm matching cho nhiều jobs.
    def calculate_jobs_match(self, jobs: QuerySet) -> Dict[int, Dict]:
        results = {}
        for job in jobs:
            results[job.id] = self.calculate_job_match(job)
        return results


# ============================================================
# HELPER FUNCTIONS
# ============================================================

# Lấy skill profile của user.
def get_user_skill_profile(user) -> Optional[UserSkillProfile]:
    try:
        return UserSkillProfile.objects.get(user=user)
    except UserSkillProfile.DoesNotExist:
        return None

# Lấy thông tin matching giữa job và user.
def get_job_matching_info(job: Job, user) -> Dict:
    profile = get_user_skill_profile(user)
    
    if not profile or profile.skills.count() == 0:
        return {
            'has_profile': False,
            'matching_score': 0,
            'skill_score': 0,
            'text_score': 0,
            'matched_skills': [],
        }
    
    matcher = JobMatcher(profile)
    match_info = matcher.calculate_job_match(job)
    match_info['has_profile'] = True
    
    return match_info

# Lấy danh sách jobs kèm điểm matching.
def get_jobs_with_matching_scores(jobs: QuerySet, user) -> List[Dict]:
    profile = get_user_skill_profile(user)
    
    if not profile or profile.skills.count() == 0:
        return [{'job': job, 'matching_score': 0, 'has_profile': False} for job in jobs]
    
    matcher = JobMatcher(profile)
    match_results = matcher.calculate_jobs_match(jobs)
    
    results = []
    for job in jobs:
        match_info = match_results.get(job.id, {})
        results.append({
            'job': job,
            'matching_score': match_info.get('matching_score', 0),
            'skill_score': match_info.get('skill_score', 0),
            'text_score': match_info.get('text_score', 0),
            'has_profile': True,
        })
    
    return results
