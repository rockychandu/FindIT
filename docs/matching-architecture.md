# Intelligent Matching Engine Architecture

The FindIT Intelligent Matching Engine is a multi-signal decision support system developed as Member 2's core module.

## High-Level Architecture

```
+---------------------------------------------------------------------------------------+
|                                 MATCHING SERVICE LAYER                                |
+---------------------------------------------------------------------------------------+
                                           |
    +------------------+-------------------+--------------------+------------------+
    |                  |                   |                    |                  |
    v                  v                   v                    v                  v
+----------+   +---------------+   +---------------+   +---------------+   +---------------+
| Text     |   | Category      |   | Location      |   | Time          |   | Image         |
| Matcher  |   | Matcher       |   | Matcher       |   | Matcher       |   | Matcher       |
| (TF-IDF) |   | (Hierarchical)|   | (Haversine/   |   | (Temporal     |   | (PIL dHash /  |
|          |   |               |   | Text)         |   | Decay)        |   | Color Hist)   |
+----------+   +---------------+   +---------------+   +---------------+   +---------------+
    |                  |                   |                    |                  |
    +------------------+-------------------+--------------------+------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |          SCORE CALCULATOR           |
                        | (Weighted Sum + Dynamic Weighting)  |
                        +-------------------------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |            MATCH RANKER             |
                        | (Confidence Level: HIGH/MED/LOW/NS) |
                        +-------------------------------------+
```

## Core Components
- `matching/preprocessing.py`: Normalizes text inputs, strips punctuation, tokenizes, and removes standard stop-words.
- `matching/text_matcher.py`: Computes TF-IDF vectors and Cosine Similarity across item name, description, brand, color, and distinguishing features.
- `matching/category_matcher.py`: Evaluates exact category ID match, parent/child hierarchy, and synonym groups.
- `matching/location_matcher.py`: Computes Haversine distance for geo-coordinates or text location token overlap for campus building/room names.
- `matching/time_matcher.py`: Computes temporal proximity score with decay based on days/hours delta between lost and found timestamps.
- `matching/image_matcher.py`: Local PIL/NumPy image feature comparison combining 64-bit dHash Hamming distance and 3D RGB color histogram intersection.
- `matching/score_calculator.py`: Combines signal scores using configurable weights and dynamically redistributes weights if optional signals (such as images) are missing.
- `matching/ranking.py`: Maps overall scores to confidence levels (`HIGH`, `MEDIUM`, `LOW`, `NOT_SUITABLE`) and ranks candidate matches.
