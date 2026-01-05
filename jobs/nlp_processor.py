import re
from typing import List, Tuple, Optional

# =================================================================
# IMPORT LIBRARIES
# =================================================================

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Error: Chưa cài đặt sklearn")

# Underthesea - Tiếng Việt
try:
    from underthesea import word_tokenize as vi_tokenize
    UNDERTHESEA_AVAILABLE = True
except ImportError:
    UNDERTHESEA_AVAILABLE = False
    print("Error: Chưa cài đặt underthesea")

# TextBlob - Tiếng Anh
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Error: Chưa cài đặt textblob")


# Phát hiện ngôn ngữ của văn bản (VI hoặc EN)
# Dựa trên việc đếm ký tự tiếng Việt đặc trưng
def detect_language(text: str) -> str:
    if not text:
        return 'vi'  # Default to Vietnamese
    
    # Các ký tự đặc trưng tiếng Việt
    vietnamese_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
    vietnamese_chars.update([c.upper() for c in vietnamese_chars])
    
    text_lower = text.lower()
    vietnamese_char_count = sum(1 for c in text_lower if c in vietnamese_chars)
    
    # Nếu có nhiều hơn 2% ký tự tiếng Việt -> tiếng Việt
    if len(text) > 0 and (vietnamese_char_count / len(text)) > 0.02:
        return 'vi'
    
    return 'en'


# =================================================================
# TEXT CLEANING
# =================================================================

# Làm sạch văn bản
def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Chuyển thành chữ thường
    text = text.lower()
    
    # Loại bỏ URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    
    # Loại bỏ email
    text = re.sub(r'\S+@\S+', '', text)
    
    # Loại bỏ số điện thoại
    text = re.sub(r'\b\d{9,11}\b', '', text)
    
    # Giữ lại ký tự chữ cái (bao gồm tiếng Việt) và khoảng trắng
    text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)
    
    # Loại bỏ số
    text = re.sub(r'\d+', '', text)
    
    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# =================================================================
# TOKENIZATION
# =================================================================

# Tách từ tiếng Việt sử dụng Underthesea
def tokenize_vietnamese(text: str) -> List[str]:
    if not UNDERTHESEA_AVAILABLE or not text:
        return text.split() if text else []
    
    try:
        tokens = vi_tokenize(text, format="text")
        return tokens.split()
    except Exception as e:
        print(f"Vietnamese tokenization error: {e}")
        return text.split() if text else []


def tokenize_english(text: str) -> List[str]:
    """
    Tách từ tiếng Anh sử dụng TextBlob.
    
    Args:
        text: Văn bản tiếng Anh
    
    Returns:
        List các từ đã được tách
    """
    if not TEXTBLOB_AVAILABLE or not text:
        return text.split() if text else []
    
    try:
        blob = TextBlob(text)
        return [str(word) for word in blob.words]
    except Exception as e:
        print(f"English tokenization error: {e}")
        return text.split() if text else []


def tokenize_text(text: str, language: Optional[str] = None) -> List[str]:
    if not text:
        return []
    
    if language is None:
        language = detect_language(text)
    
    cleaned = clean_text(text)
    
    if language == 'vi':
        return tokenize_vietnamese(cleaned)
    else:
        return tokenize_english(cleaned)

# Tách từ và trả về text đã tokenize.
def get_tokenized_text(text: str, language: Optional[str] = None) -> str:
    tokens = tokenize_text(text, language)
    return ' '.join(tokens)


# =================================================================
# TF-IDF VECTORIZATION & COSINE SIMILARITY
# =================================================================

# Tính độ tương đồng giữa 2 văn bản sử dụng TF-IDF và Cosine Similarity.
def calculate_tfidf_similarity(text1: str, text2: str, use_tokenization: bool = True) -> float:
    if not SKLEARN_AVAILABLE:
        return 0.0
    
    if not text1 or not text2:
        return 0.0
    
    try:
        combined_text = text1 + " " + text2
        language = detect_language(combined_text)
        
        if use_tokenization:
            processed_text1 = get_tokenized_text(text1, language)
            processed_text2 = get_tokenized_text(text2, language)
        else:
            processed_text1 = clean_text(text1)
            processed_text2 = clean_text(text2)
        
        if not processed_text1 or not processed_text2:
            return 0.0
        
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            max_features=5000
        )
        
        tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
        
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
        
    except Exception as e:
        print(f"TF-IDF không hợp lệ: {e}")
        return 0.0

# Tính điểm phù hợp giữa 2 văn bản (0-100).
def get_matching_score_percentage(text1: str, text2: str) -> int:
    similarity = calculate_tfidf_similarity(text1, text2)
    return min(int(similarity * 100), 100)


# =================================================================
# KEYWORD EXTRACTION
# =================================================================

# Trích xuất các từ khóa quan trọng nhất từ văn bản sử dụng TF-IDF.
def get_top_keywords(text: str, top_n: int = 20, language: Optional[str] = None) -> List[Tuple[str, float]]:
    if not SKLEARN_AVAILABLE or not text:
        return []
    
    try:
        if language is None:
            language = detect_language(text)
        
        tokenized = get_tokenized_text(text, language)
        
        if not tokenized:
            return []
        
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=100
        )
        
        tfidf_matrix = vectorizer.fit_transform([tokenized])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        keyword_scores = list(zip(feature_names, scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return keyword_scores[:top_n]
        
    except Exception as e:
        print(f"Từ khóa không hợp lệ: {e}")
        return []


# =================================================================
# UTILITY FUNCTIONS
# =================================================================

def is_sklearn_available() -> bool:
    return SKLEARN_AVAILABLE


def is_underthesea_available() -> bool:
    return UNDERTHESEA_AVAILABLE


def is_textblob_available() -> bool:
    return TEXTBLOB_AVAILABLE


def get_nlp_libraries_status() -> dict:
    return {
        'sklearn': SKLEARN_AVAILABLE,
        'underthesea': UNDERTHESEA_AVAILABLE,
        'textblob': TEXTBLOB_AVAILABLE,
    }
