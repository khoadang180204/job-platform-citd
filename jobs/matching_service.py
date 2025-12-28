"""
Job Matching Service - Đơn giản hóa
====================================
Tính điểm phù hợp giữa User Skills và Job dựa trên:
1. Skill Matching - So sánh skills của user với skills yêu cầu của job
2. TF-IDF + Cosine Similarity - So sánh bio của user với job description

KHÔNG sử dụng OCR hay deep learning.
"""

from typing import Dict, List, Set, Optional
from django.db.models import QuerySet

# NLP Libraries
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

def get_matched_skills(user_skill_ids: Set[int], job_skill_ids: Set[int]) -> Set[int]:
    """
    So sánh skills của user với skills yêu cầu của job.
    
    Args:
        user_skill_ids: Set các skill ID mà user có
        job_skill_ids: Set các skill ID mà job yêu cầu
    
    Returns:
        Set các skill ID trùng khớp
    """
    return user_skill_ids.intersection(job_skill_ids)


def calculate_skill_match_score(user_skill_ids: Set[int], job_skill_ids: Set[int]) -> int:
    """
    Tính phần trăm skills trùng khớp.
    
    Args:
        user_skill_ids: Set các skill ID mà user có
        job_skill_ids: Set các skill ID mà job yêu cầu
    
    Returns:
        Phần trăm trùng khớp (0-100)
    """
    if not job_skill_ids:
        return 0
    
    matched = len(user_skill_ids.intersection(job_skill_ids))
    total_required = len(job_skill_ids)
    
    return int((matched / total_required) * 100)


# ============================================================
# TF-IDF TEXT MATCHING
# ============================================================

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Tính độ tương đồng giữa 2 văn bản sử dụng TF-IDF và Cosine Similarity.
    
    Args:
        text1: Văn bản thứ nhất (user bio + skills)
        text2: Văn bản thứ hai (job description + skills)
    
    Returns:
        Điểm tương đồng từ 0.0 đến 1.0
    """
    if not SKLEARN_AVAILABLE:
        return 0.0
    
    if not text1 or not text2:
        return 0.0
    
    try:
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Unigrams và bigrams
            min_df=1,
            max_features=5000
        )
        
        # Fit and transform
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

class JobMatcher:
    """
    Service để tính điểm matching giữa User Skill Profile và Job.
    """
    
    def __init__(self, user_profile: Optional[UserSkillProfile] = None):
        """
        Initialize matcher với profile của user.
        
        Args:
            user_profile: UserSkillProfile object
        """
        self.user_profile = user_profile
        self._user_skill_ids = set()
        self._user_text = ""
        
        if user_profile:
            self._load_profile_data()
    
    def _load_profile_data(self):
        """Load data từ user profile."""
        if not self.user_profile:
            return
        
        # Get skill IDs
        self._user_skill_ids = set(self.user_profile.skills.values_list('id', flat=True))
        
        # Build user text for TF-IDF (bio + skills + categories)
        parts = []
        if self.user_profile.bio:
            parts.append(self.user_profile.bio)
        parts.append(self.user_profile.get_skills_text())
        parts.append(self.user_profile.get_categories_text())
        
        self._user_text = ' '.join(parts)
    
    def calculate_job_match(self, job: Job) -> Dict:
        """
        Tính điểm matching cho một job.
        
        Args:
            job: Job object
        
        Returns:
            Dict chứa matching scores và thông tin
        """
        # Get job skill IDs
        job_skill_ids = set(job.required_skills.values_list('id', flat=True))
        
        # Build job text for TF-IDF
        job_text_parts = [job.title, job.description or '']
        if job.requirements:
            job_text_parts.append(job.requirements)
        if job.responsibilities:
            job_text_parts.append(job.responsibilities)
        # Add job skills to text
        job_skills_text = ' '.join([s.name for s in job.required_skills.all()])
        job_text_parts.append(job_skills_text)
        job_text = ' '.join(job_text_parts)
        
        # Calculate skill match score (60% weight)
        skill_score = calculate_skill_match_score(self._user_skill_ids, job_skill_ids)
        
        # Calculate text similarity score (40% weight)
        text_score = 0
        if self._user_text:
            similarity = calculate_text_similarity(self._user_text, job_text)
            text_score = int(similarity * 100)
        
        # Combined score
        combined_score = int(skill_score * 0.6 + text_score * 0.4)
        
        # Get matched skills details
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
    
    def calculate_jobs_match(self, jobs: QuerySet) -> Dict[int, Dict]:
        """
        Tính điểm matching cho nhiều jobs.
        
        Args:
            jobs: QuerySet of Job objects
        
        Returns:
            Dict mapping job_id to match info
        """
        results = {}
        for job in jobs:
            results[job.id] = self.calculate_job_match(job)
        return results


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_user_skill_profile(user) -> Optional[UserSkillProfile]:
    """
    Lấy skill profile của user.
    
    Args:
        user: User object
    
    Returns:
        UserSkillProfile object hoặc None
    """
    try:
        return UserSkillProfile.objects.get(user=user)
    except UserSkillProfile.DoesNotExist:
        return None


def get_job_matching_info(job: Job, user) -> Dict:
    """
    Lấy thông tin matching giữa job và user.
    
    Args:
        job: Job object
        user: User object
    
    Returns:
        Dict chứa matching info
    """
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


def get_jobs_with_matching_scores(jobs: QuerySet, user) -> List[Dict]:
    """
    Lấy danh sách jobs kèm điểm matching.
    
    Args:
        jobs: QuerySet of Job objects
        user: User object
    
    Returns:
        List of job dicts with matching scores
    """
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
