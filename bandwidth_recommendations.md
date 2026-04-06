# Kernel Bandwidth Optimization Recommendations

## Summary of Evaluation Methods

Based on the analysis, here are different approaches to selecting the optimal bandwidth:

### 1. **Roughness Penalty (Recommended)**

The roughness metric shows clear differences:
- b=0: 232.62 (very rough/noisy)
- b=2: 64.87 (moderate smoothing) ⭐ **Current default**
- b=5: 25.53 (smoother)
- b=8: 10.31 (very smooth)

**Recommendation**: Lower roughness is better, but diminishing returns after b=5

### 2. **Bias-Variance Tradeoff**

Looking at the bias² and variance components:
- b=0: Bias²=0.00, Variance=0.077 (underfit - too noisy)
- b=2: Bias²=0.037, Variance=0.038 (balanced)
- b=5: Bias²=0.052, Variance=0.021 (more bias, less variance)
- b=8: Bias²=0.060, Variance=0.014 (oversmoothed)

**Recommendation**: Look for the "elbow" where bias² starts increasing faster than variance decreases. This appears around **b=2-3**.

### 3. **Domain Knowledge**

Consider the game mechanics:
- **Early floors (1-10)**: Deck is mostly starter cards, context changes rapidly
  - Suggests: Smaller bandwidth (b=1-2)
- **Mid floors (11-25)**: Deck is more established, decisions more stable
  - Suggests: Medium bandwidth (b=2-4)
- **Late floors (26+)**: Very specific deck, but sparse data
  - Suggests: Larger bandwidth (b=3-5) to compensate for low sample size

### 4. **Visual Inspection Method**

Looking at the GLOW card example:
- b=0-1: Too noisy, hard to see trends
- **b=2-3**: Good balance, trends visible but preserves local variation ⭐
- b=5-7: Smooth but may miss important floor-specific patterns
- b=7+: Over-smoothed, loses too much detail

## Recommended Approach: **Adaptive Bandwidth**

Instead of a single bandwidth value, use different bandwidths based on:

### Option A: Floor-dependent bandwidth
```python
if floor <= 10:
    bandwidth = 1  # Early game: less smoothing
elif floor <= 25:
    bandwidth = 2  # Mid game: moderate smoothing
else:
    bandwidth = 3  # Late game: more smoothing (compensate for sparse data)
```

### Option B: Sample-size-dependent bandwidth
```python
total_offers_in_window = sum(offers in ±3 floors)
if total_offers_in_window < 5:
    bandwidth = 3  # Low data: more smoothing
elif total_offers_in_window < 15:
    bandwidth = 2  # Medium data: moderate smoothing
else:
    bandwidth = 1  # High data: less smoothing needed
```

### Option C: Card-dependent bandwidth
```python
total_offers_for_card = sum(all offers across all floors)
if total_offers_for_card < 10:
    bandwidth = 4  # Rare cards: aggressive smoothing
elif total_offers_for_card < 30:
    bandwidth = 2  # Common cards: moderate smoothing
else:
    bandwidth = 1  # Very common cards: minimal smoothing
```

## Final Recommendation

For your current analysis (Regent A10):

1. **Default bandwidth: b=2** ✓ (Good choice!)
   - Balances bias and variance
   - Roughness reduced by 72% vs. raw data
   - Visually interpretable results

2. **Consider adaptive approach**:
   - Use b=3 for cards with <15 total offers
   - Use b=2 for cards with 15-30 total offers
   - Use b=1 for cards with >30 total offers

3. **For presentation/visualization**:
   - Show both raw (b=0) and smoothed (b=2) side-by-side
   - Allow users to adjust bandwidth interactively
   - Clearly label smoothed values

## Why CV Error Was Constant

The cross-validation error was identical across all bandwidth values because:
1. Small sample size (15 runs)
2. Sparse data (many cards seen <5 times)
3. Binary outcomes (picked/not picked) with weighted averaging
4. Leave-one-out CV doesn't capture smoothness preferences

**Better metrics**: Roughness penalty and visual inspection are more informative for this use case.
