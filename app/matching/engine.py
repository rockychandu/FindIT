import math
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return ' '.join(text.split())

def calculate_text_similarity(str1, str2):
    norm1 = normalize_text(str1)
    norm2 = normalize_text(str2)
    
    if not norm1 or not norm2:
        return 0.0
    
    if norm1 == norm2:
        return 1.0
        
    try:
        vectorizer = TfidfVectorizer().fit_transform([norm1, norm2])
        vectors = vectorizer.toarray()
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(score)
    except Exception:
        # Fallback to Jaccard token similarity if TFIDF fails on single-word tokens
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union) if union else 0.0

def calculate_location_similarity(loc1, loc2):
    norm1 = normalize_text(loc1)
    norm2 = normalize_text(loc2)
    if not norm1 or not norm2:
        return 0.0
    if norm1 == norm2:
        return 1.0
    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())
    common = tokens1.intersection(tokens2)
    total = tokens1.union(tokens2)
    return len(common) / len(total) if total else 0.0

def calculate_time_similarity(date1, date2):
    if not date1 or not date2:
        return 0.5
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, '%Y-%m-%d').date()
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, '%Y-%m-%d').date()
    diff_days = abs((date1 - date2).days)
    if diff_days == 0:
        return 1.0
    elif diff_days <= 2:
        return 0.85
    elif diff_days <= 5:
        return 0.65
    elif diff_days <= 10:
        return 0.40
    elif diff_days <= 30:
        return 0.20
    else:
        return 0.05

def compute_match_score(lost_report, found_report):
    # Category score
    category_score = 1.0 if lost_report.category_id == found_report.category_id else 0.0
    
    # Text composite score
    lost_text = f"{lost_report.item_name} {lost_report.brand or ''} {lost_report.color or ''} {lost_report.description} {lost_report.distinguishing_features or ''}"
    found_text = f"{found_report.item_name} {found_report.brand or ''} {found_report.color or ''} {found_report.description} {found_report.distinguishing_features or ''}"
    
    text_score = calculate_text_similarity(lost_text, found_text)
    
    # Location score
    location_score = calculate_location_similarity(lost_report.location, found_report.location)
    
    # Time score
    time_score = calculate_time_similarity(lost_report.date, found_report.date)
    
    # Image score (placeholder 0.0 for now unless images features compared locally)
    image_score = 0.0
    
    # Overall score formula
    overall_score = (category_score * 0.25) + (text_score * 0.35) + (location_score * 0.25) + (time_score * 0.15)
    
    return {
        'category_score': category_score,
        'text_score': text_score,
        'location_score': location_score,
        'time_score': time_score,
        'image_score': image_score,
        'overall_score': round(overall_score, 4)
    }
