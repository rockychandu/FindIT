# Matching Algorithms Deep Dive

## 1. Text Similarity (TF-IDF + Cosine Similarity)
- **Algorithm**: Term Frequency - Inverse Document Frequency (TF-IDF) vectorization using n-grams (1, 2) followed by Cosine Similarity.
- **Fields Evaluated**:
  - `item_name` (35% field weight)
  - `description` (30% field weight)
  - `brand` (15% field weight)
  - `color` (10% field weight)
  - `distinguishing_features` (10% field weight)
- **Zero Cloud Dependencies**: Implemented strictly using `scikit-learn` local vectorizers.

## 2. Category Similarity
- **Exact Match**: 100% score for identical category IDs.
- **Parent/Child Match**: 80% score for category hierarchy relationships.
- **Synonym Match**: 75% score for matching predefined synonym sets (e.g. Wallet/Purse, Phone/iPhone, Laptop/MacBook).
- **Mismatch**: 0% score.

## 3. Location Similarity (Haversine & Campus Text)
- **Haversine Distance**: Computes great-circle distance between coordinates in meters:
  \[ d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right) \]
- **Distance Decay Curve**:
  - \(\le 50\text{ m} \rightarrow 100\%\)
  - \(\le 200\text{ m} \rightarrow 90\% \text{ to } 75\%\)
  - \(\le 500\text{ m} \rightarrow 75\% \text{ to } 50\%\)
  - \(\le 2000\text{ m} \rightarrow 50\% \text{ to } 10\%\)
- **Text Location Fallback**: Jaccard token overlap + building/room number matching bonus.

## 4. Time Proximity Decay
- Delta calculation in hours:
  - \(0 - 6\text{ hours} \rightarrow 100\%\)
  - \(6 - 24\text{ hours} \rightarrow 90\%\)
  - \(1 - 3\text{ days} \rightarrow 80\%\)
  - \(3 - 7\text{ days} \rightarrow 65\%\)
  - \(1 - 4\text{ weeks} \rightarrow 40\%\)
  - \(> 4\text{ weeks} \rightarrow 20\%\)

## 5. Local Image Similarity
- **dHash (Difference Hash)**: Resizes image to \(9 \times 8\) grayscale matrix and computes horizontal pixel difference.
- **Color Histogram**: Calculates 3D RGB color distribution histogram and measures intersection.
- **Local Execution**: Uses Pillow and NumPy with zero API keys.
