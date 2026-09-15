# Scoring System and Weight Redistribution

## Default Signal Weighting
The overall match score is calculated using weighted signals:

| Signal | Default Weight | Description |
| :--- | :--- | :--- |
| **Text Similarity** | 40% | TF-IDF Cosine Similarity |
| **Category Similarity** | 20% | Category matrix & hierarchy |
| **Location Similarity** | 15% | Haversine distance / campus text |
| **Time Proximity** | 15% | Temporal proximity decay |
| **Image Similarity** | 10% | Local dHash & color histogram |

## Dynamic Weight Redistribution
When optional signals (such as `image_score`) are missing (`None`), the system redistributes the unavailable weight proportionally across all available signals so that valid reports are not penalized unfairly.

### Formula
For available signal set \(S\):
\[ W_{\text{effective}}(s) = \frac{W_{\text{default}}(s)}{\sum_{k \in S} W_{\text{default}}(k)} \]

\[ \text{Overall Score} = \sum_{s \in S} \text{Score}(s) \times W_{\text{effective}}(s) \]

## Confidence Levels & Thresholds
- **HIGH (80.0% – 100.0%)**: High probability candidate match.
- **MEDIUM (60.0% – 79.99%)**: Moderate probability candidate match.
- **LOW (45.0% – 59.99%)**: Low probability candidate match.
- **NOT_SUITABLE (0.0% – 44.99%)**: Excluded from match list.
