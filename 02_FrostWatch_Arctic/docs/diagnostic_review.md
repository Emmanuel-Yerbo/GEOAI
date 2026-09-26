# 🔬 FrostWatch Comprehensive Diagnostic Review
**Reviewer:** Independent diagnostic audit per `REVIEW_PROMPT.md`
**Scope:** `FROSTWATCH_V4A.py`, `FROSTWATCH_V4B_INFERENCE.py`, `FROSTWATCH_V4C_INFERENCE.py`, `JSONS/FrostWatch.json` (V4B output), `JSONS/FrostWatch4.json` (V4A output), `GEOAI_SKILLSET.md`, `GEOAI_SKILLS_SYNTHESIS.md`, `PAPER1_DEEP_ANALYSIS.md`, `PDG_SLIDES_DEEP_ANALYSIS.md`, `DARTS_LITERATURE_REVIEW.md`
**Date:** 2026-08-19

> **Housekeeping note:** The prompt's file map does not match the workspace: files live in the workspace root (not `permafrost/`), `PERMAFROST_SCIENCE_SYNTHESIS.md` does not exist, and there are six near-duplicate training-script variants (`FROSTWATCH_V4.py`, `FROSTWATCH_V4A.py`, `FROSTWATCH_V4_A.py`, ...) with conflicting hyperparameters (e.g., `V4A` = 120 epochs / TTA scales 0.85–1.15 vs `V4_A` = 100 epochs / scales 0.75–1.25). This is a reproducibility hazard: there is no way to know which variant produced the checkpoints behind the 11.00 AP V4B submission. Consolidate to one canonical file under version control.

---

## 1. Executive Assessment

### 1.1 Strengths
1. **Physics tensor ordering is mathematically correct and consistent.** All three scripts compute the 5 ratio indices on raw positive reflectance *before* percentile clipping and z-scoring, identically at train and test time (`FROSTWATCH_V4A.py:413-424`, `:832-842`; V4B/V4C cells 4–5 are byte-identical functions). This is the single most important normalization invariant in the pipeline and it holds.
2. **Sound empirical calibration loop.** The V4A → V4B → V4C iteration isolates post-processing variables one at a time (SAHI on/off, floor 0.25→0.45→0.32, min-area 5→25→8, morphology on→off). That is proper experimental method.
3. **Genuine architectural diversity.** FPN/MiT-B5 (global self-attention), U-Net/MiT-B3, U-Net++/SE-ResNeXt-50 (channel attention + dense skips), DeepLabV3+/Eff-B5 (dilated ASPP context) — 2 transformer + 2 CNN encoders with 4 distinct decoders. This is the right ensemble design.
4. **Lovász-Hinge implementation is correct** (Berman et al. sort-and-gradient form, `FROSTWATCH_V4A.py:502-528`), and phasing it in at epoch 25 (`:605-606`) with weights 0.35/0.35/0.30 is well-motivated.
5. **The core insight behind V4C is right**: raw sigmoid contours beat morphologically-eroded contours at IoU ≥ 0.75.

### 1.2 Critical Vulnerabilities (ranked by impact)
| # | Finding | Severity | Evidence |
|---|---|---|---|
| V1 | **Validation-set leakage**: the "10% internal validation" is a random `Subset` of the *full training set* (`FROSTWATCH_V4A.py:1263-1280`, sharing the same RAM cache). The reported Val IoUs (0.9295/0.9064/0.8827/0.8758) are **train-set IoU** and carry no generalization information. The claim "the 4 models are EXCELLENT (0.93 Val IoU)" in V4B's header is unsupported. | **Critical** | leaderboard AP (4.91–13.88) vs 0.93 IoU; V4B (11.00) still *below* V2 (13.88) |
| V2 | **Focal-loss α is a no-op for class balance**: `focal = (α·(1-pt)^γ·bce).mean()` applies α uniformly to *all* pixels (`FROSTWATCH_V4A.py:544-545`). Standard focal applies α to positives and (1−α) to negatives. As written, α=0.25 is a global 4× down-weight of the focal term; imbalance handling rests entirely on Dice. | High | `CompositeV4Loss.forward` |
| V3 | **Augmentations corrupt the physics channels**: indices are computed inside `_load_from_disk`, so `RandomBrightnessContrast`, `GaussNoise`, and `GaussianBlur` are applied to NDVI/NDWI/NDRE/IOR/Albedo *after* computation (`:446-448`). A contrast shift makes channel 9 no longer equal (G−NIR)/(G+NIR) of channels in 0–7. Worse, `GaussNoise(var_limit=(10,30))` = noise σ ≈ 3.2–5.5 injected into unit-variance z-scored channels — when it fires (p=0.15) the sample is largely destroyed while labels stay clean → label noise. | High | `v4_augment`, `__getitem__` |
| V4 | **Anisotropic aspect-ratio distortion**: test/train chips are ~289×159 px (confirmed from RLE `size` in both submission JSONs) but are `cv2.resize`d to 512×512 — ×1.77 horizontal, ×3.22 vertical stretch. Scalloped RTS geometry is systematically elongated; area scale between model space and submission space is 512²/(289·159) ≈ **5.70×**, so `MIN_AREA` values are not what they appear (V4C's "8 px" ≈ 46 px in model space; V4B's "25 px" ≈ 142 px). | High | `preprocess_test_image`, JSON forensics §3 |
| V5 | **Score-ranking, not prediction count, is the AP lever** — this is misunderstood in the docs. COCO AP is invariant to monotone score transforms; FPs ranked *below* all TPs are essentially free. V4A died not from "2,839 predictions" per se but from SAHI fragments/duplicates scoring *above* weak true positives (median SAHI-era score 0.420 vs V4B 0.709). | High | §3.2 |
| V6 | **No instance-level logic**: connected-component extraction (8-connectivity) merges adjacent slumps into one prediction; no NMS, no soft-NMS, no watershed splitting. | Medium | `generate_v4*_submission` |
| V7 | **Otsu adaptive threshold is mis-specified for zero-inflated probability maps**: on a chip where RTS pixels are <3%, Otsu splits the *background* mode, and the floor does all the work; on slump-heavy chips it can exceed the 0.65/0.70 cap and kill recall. The documented "falls back to default if nearly uniform" (`:867-876`) is **not implemented** — `default` is a dead parameter. | Medium | `compute_adaptive_threshold` |
| V8 | **Unverified claims treated as results**: "Target 25.0+ mAP", "AP_small/medium/large: High" for V4C appear in the compendium with no leaderboard submission behind them. Rank #1 rests entirely on V2. | Medium | doc cross-check |
| V9 | **2-GPU "parallel" training uses ThreadPoolExecutor with `num_workers=0`** — GIL contention from Python-side data pipeline (13×512×512 copies + albumentations per sample) will serialize both threads; expect ~50% GPU idle. Two threads also iterate the *same* DataLoader object (fragile, though per-iterator state currently avoids corruption). | Medium | `:1307-1343` |
| V10 | **RAM preload ≈ 10.3 GB** (756 chips × 13×512×512×float32 = 13.6 MB each) — borderline on 13 GB Kaggle instances; OOM risk when combined with 2 concurrent models. | Low | `cache_in_ram=True` |

### 1.3 Mathematical validity verdict
The 13-channel formulation, order-of-operations, phased loss schedule, TTA geometry (rot90/flip are exact isometries; scale passes resize back to native grid), IoU-weighted ensemble, and RLE encoding are all mathematically sound. The pipeline's *measurement* layer (validation) and *augmentation physics* layer are where rigor breaks down. Nothing found invalidates the V2 Rank-#1 result; several findings explain why V4 has not yet beaten it.

---

## 2. Pillar 1 — Code Architecture & Physics Tensor Verification

### 2.1 The 13-channel tensor: verified ✔ with caveats
Formulas as implemented (`compute_spectral_indices`, identical in all three scripts):

| Ch | Index | Formula (as coded) | Bands | Verdict |
|---|---|---|---|---|
| 8 | NDVI | (NIR−R)/(NIR+R+ε) | B7, B5 | ✔ standard |
| 9 | NDWI | (G−NIR)/(G+NIR+ε) | **B3**, B7 | ✔ McFeeters form; note SKILLSET/SYNTHESIS disagree on whether "Green" is B2 or B3 — code pins B3 (547–583 nm), the correct choice, but the docs should be reconciled |
| 10 | NDRE | (NIR−RE)/(NIR+RE+ε) | B7, B6 | ✔ |
| 11 | IOR | (R−B)/(R+B+ε) | B5, B1 | ✔ iron-oxide ratio; consistent with DARTS' Red/Blue oxidized-sediment peak |
| 12 | Albedo | (CB+B+G+Y)/4 | B0,B1,B3,B4 | ✔ simple brightness; *not* a normalized index — raw reflectance scale, handled by the subsequent per-channel clip+z-score |

ε = 1e-8, consistently applied. Order of operations verified: **indices on raw positive data → per-channel p2–p98 clip → per-channel z-score** at both train (`FROSTWATCH_V4A.py:413-424`) and inference (`:832-842`). This correctly avoids the ratio-asymmetry distortion z-scoring would introduce.

Caveats:
- `np.nan_to_num(nan=0.0)` **before** index computation turns NaN pixels into zero-reflectance pixels; a (0,0) band pair yields index = 0/ε → 0, a *mid-range* value that masquerades as "no signal" rather than an outlier. A dedicated NaN mask channel would be cleaner.
- Indices are computed on the **resized** image (ratios of interpolated bands). This is self-consistent between train and test and is the correct choice — just note it differs from "resize the index map".
- The docs say "Lovász-Softmax" in one heading and "Lovász-Hinge" elsewhere; the code implements the **Hinge** (binary) variant, which is the correct one for `classes=1`.

### 2.2 Model diversity audit
| Model | Encoder | Params | Val IoU (⚠ train-contaminated) | Inductive bias | Assessment |
|---|---|---|---|---|---|
| fpn_mit_b5 | SegFormer MiT-B5 | 82M | 0.9295 | Global self-attention, hierarchical; FPN lateral decoder | Strongest; ViT bias suits coherent large-scarp semantics |
| unet_mit_b3 | MiT-B3 | 45M | 0.9064 | Same family as above | ⚠ Only *2* encoder families among 4 models (MiT-B5/B3 share pretraining, tokenizer, patch size) — diversity is mostly in decoders |
| unetpp_seresnext50 | SE-ResNeXt-50 | 33M | 0.8827 | Grouped conv + channel attention, dense nested skips | Good CNN complement |
| deeplabv3p_efficientb5 | EfficientNet-B5 | 30M | 0.8758 | MBConv + ASPP dilated context | Good for multi-scale slump-debris gradients |

Ensemble weights are val-IoU-proportional → (0.26, 0.25, 0.25, 0.24): effectively uniform. Since the ranking input is contaminated (V1), either use uniform weights explicitly or re-rank on an honest holdout. All encoders load `imagenet` weights with `in_channels=13` — SMP tiles/repeats the 3-channel stem weights, so the 5 physics channels start near-random; the 5-epoch warmup mitigates but does not eliminate this.

### 2.3 Loss formulation: verified with one real bug
- Phase transition at epoch 25 (`use_lovasz = True`, `FROSTWATCH_V4A.py:605-606`): Focal+Dice (0.5/0.5) → Focal+Dice+Lovász (0.35/0.35/0.30). ✔ matches spec.
- **Focal bug (V2 above):** correct binary form is `−[α·(1−pt)^γ·log pt | y=1] − [(1−α)·(1−pt)^γ·log pt | y=0]`. The code multiplies α into *both* classes. Net effect: focal term contributes ≈ 0.25×BCE-weighted-by-(1−pt)², i.e., Phase 1 is effectively ~0.125·BCE′ + 0.5·Dice. Training still works (Dice carries imbalance), but the intended α semantics is broken and the documented loss is not the executed loss.
- Dice: per-sample intersection/union then batch-mean, smooth=1.0. ✔
- Lovász-Hinge: sort-by-error, cumulative-Jaccard gradient, ReLU-dot. ✔ Implementation matches the reference. Minor: it flattens the whole *batch* into one sort (couples the 4 samples); per-image flattening is the reference behavior.
- Cosine schedule with 5-epoch warmup, AdamW wd=1e-4, grad accumulation ×2. ✔ sound.

### 2.4 Training-engine notes
- Checkpoint selection by the contaminated val IoU (V1) — "best" checkpoints are selected for train-set fit.
- Grad-accum tail: an odd-length loader steps the optimizer on a half-scaled final accumulation (negligible).
- `FORCE_RETRAIN = True` silently discards existing checkpoints if a cell is re-run.

---

## 3. Pillar 2 — Post-Processing & COCO mAP Calibration

### 3.1 Submission forensics (measured from the JSONs in `JSONS/`)
| Metric | V2 (leaderboard) | **V4A** (`FrostWatch4.json`) | **V4B** (`FrostWatch.json`) | V4C (unverified) |
|---|---|---|---|---|
| Predictions | 261 | **2,839** | **222** | ~280–320 (target) |
| Images with ≥1 pred | ~138 | 138 | 136 | — |
| Preds/image (mean / max) | 1.89 / — | **20.57 / 50** | 1.63 / 7 | ~2.0–2.3 |
| Score min / median / max | — | 0.267 / **0.420** / 0.911 | 0.452 / **0.709** / 0.920 | — |
| Mask area p10 / median / p90 | — | **11 / 130 / 1,644** px | 83 / **795** / 4,298 px | — |
| Share < 32 px | — | **23.7%** | 1.8% | — |
| AP / AP50 / AP75 | 13.88 / 37.76 / 9.21 | 4.91 / 12.54 / 3.46 | 11.00 / 29.93 / 6.79 | — |
| AR | 16.56 | 19.63 | 15.55 | — |

Additional measurement: in V4B, Pearson r between log₁₀(mask area) and score = **0.676** — mean-prob-under-mask scoring systematically ranks large slumps above small ones (large = 0.767 mean score vs small = 0.623).

### 3.2 Mathematical critique of the thresholding / NMS / extraction logic

**(a) The precision-ceiling identity.** If a submission contains N_pred predictions of which N_gt match at a given IoU, then precision at full recall ≤ N_gt/N_pred. With ~250 GT instances (inferred from V2's AR), V4A's ceiling was ≈ 250/2839 ≈ **8.8%** — the observed 4.91 AP is close to that ceiling, i.e., V4A was near the best possible outcome *given its ranking contamination*. This is a clean quantitative explanation of the SAHI crash.

**(b) The ranking-invariance principle (the key missed insight).** COCO AP is a step-function integral of the precision–envelope over recall; it is invariant to any monotone transformation of scores, and predictions ranked *below the lowest-scoring TP add nothing and cost nothing* (they only append lower-precision points at unchanged recall). Therefore:
- "Over-generation" per se is not the enemy. V4A's problem was that ~2,500 SAHI fragments and tile-seam duplicates carried scores (median 0.42) that interleaved with and outranked weak true positives, inserting precision-dropping points *before* the recall frontier.
- The V4B response (raise floor to 0.45) threw away TPs (AR 16.56→15.55) to fix a ranking problem — that is why AP *fell* to 11.00 despite "cleaner" output.
- The correct instrument is **score-ordering fidelity + duplicate suppression**, not count minimization.

**(c) Otsu per-image threshold.** Otsu assumes a bimodal histogram. A 512×512 probability map with <3% positives is zero-inflated and unimodal-with-heavy-right-tail; Otsu splits *within the background* mode, yielding near-arbitrary low values that the floor then overrides (i.e., on most chips the "adaptive" threshold *is* the floor). On genuinely slump-heavy chips it can run into the 0.65/0.70 cap and delete valid instances. The `default` fallback parameter is dead code — the docstring's promised uniformity check does not exist. Recommendation: drop Otsu; use a fixed operating threshold chosen on an honest holdout, and spend the complexity budget on per-instance refinement (§3.3).

**(d) Area filters operate in the wrong space.** Instances are extracted on the original-resolution map (289×159), but the model operates at 512×512 — an area scale of 5.70×. V4C's `MIN_AREA=8` is ~46 px in model space (a real micro-slump filter); V4B's 25 is ~142 px (which is why "floor 0.45 filtered real medium slumps" — it was the *area* filter, not only the floor). Document and choose these in one coordinate system.

**(e) Morphology and Douglas-Peucker.** Witharana's troughs are 2–5 px wide; a 3×3 elliptical open removes exactly that class of structure, and close cannot restore it. `approxPolyDP(ε=0.005·perimeter)` systematically clips concavities — RTS scarps are concave-scalloped, so the simplification biases masks *smaller* and smoother, directly losing AP75 (V4B AP75 6.79 vs V2 9.21 despite better models). V4C's removal is correct and should be permanent.

**(f) Instance extraction is purely topological.** 8-connected components become instances. Two abutting slumps in GT (common in RTS complexes; DARTS documents power-law clustering) merge into one prediction → one IoU-diluted match + one missed GT. There is no instance-splitting (watershed on distance transform), no true NMS (without SAHI, components are disjoint by construction, so NMS is moot), and no border-fragment suppression (DARTS explicitly removes border detections).

**(g) SAHI post-mortem.** 256-px tiles at 20% overlap over 512-px chips → ~9 tiles × 4 models × 4 rotations, each tile thresholded at 0.35 with min-area 3. Fragments were scored by mean tile probability (inflated for small coherent patches), merged by IoU>0.5 NMS, and deduped against full-image instances at IoU>0.3 — but *not against each other across scales/rotations at lower overlaps*, and surviving fragments were resized 512→289×159 with INTER_NEAREST (jagged boundaries → AP75 loss). If SAHI is ever re-enabled, require: global NMS IoU ≥ 0.50 *and* conf ≥ 0.50 for tile-only instances (the SKILLSET already codifies this rule), plus soft boundary re-resolution of merged masks from the full-image probability map.

### 3.3 Further post-processing optimizations (concrete)
1. **Dual-threshold instance refinement (highest value).** Detect connected components at the low threshold (0.30–0.32) for recall, then re-cut each instance's final mask at its own higher level set (e.g., the τ* ∈ [0.45, 0.60] maximizing mean-probability × compactness, or simply 0.5). This decouples the recall threshold from the boundary threshold and directly targets AP75 — the current single threshold forces one trade-off where two are available.
2. **Score = ordering, engineered deliberately.** Replace mean-prob with `0.5·mean_prob + 0.5·(95th-percentile prob)` or mean of top-k pixels — peak probability correlates with match likelihood better than area-correlated means (r=0.676 bias). Alternatively blend `mean_prob` with a size prior.
3. **Over-generate deliberately:** floor 0.25–0.30, `MIN_AREA` 8 (model-space ≈ 46 px), top-**k**=6 per image, and let ranking do the filtering. Expected submission size 350–500. Since sub-TP-ranked FPs are free, this strictly dominates hard filtering *provided* (1)–(2) are in place.
4. **Watershed instance splitting** of merged components (distance-transform peaks, min-distance ≈ 8 px) before RLE.
5. **Literature-supported FP rejection:** NDWI-watermask on predictions (Witharana's pipeline; DARTS' land-cover masking) — drop or down-rank predictions whose pixels are predominantly NDWI > ~0.3; GLCM entropy filter for flat bare soil (§5).
6. **Border suppression:** discard components touching chip edges with <50% of their bbox inside (DARTS rule).
7. **Logit-space ensemble:** average pre-sigmoid logits rather than probabilities — sigmoid-averaging flattens sharp boundaries; logits preserve confidence contrast, sharpening the 0.5 level set that AP75 sees.
8. **Per-image prediction prior:** GT density is ~1.5–2.5 slumps/chip; a mild top-k cap (5–6) is a cheap prior consistent with the data.

---

## 4. Pillar 3 — Data, Download & Visual Audit Workflow

### 4.1 Dataset structure (as consumed by the code)
```
<DATA_DIR>/train/images/*.npz        # 8-band PlanetScope float32, key 'image' (H×W×8)
<DATA_DIR>/train/.../instances_train.json   # COCO: images[].{id,file_name}, annotations[].{image_id,segmentation(polygon|RLE)}
<DATA_DIR>/test/images/*.npz        # 289×159 native (verified from submission RLE sizes)
<DATA_DIR>/test/.../test_manifest.csv      # image_id, file_name
```
- **Download/cache:** all three scripts auto-resolve Kaggle/Colab/local roots and fall back to `snapshot_download(repo_id="cyber2a/2026GeoAIArcticChallengeDataset", repo_type="dataset")` with zip extraction (`FROSTWATCH_V4A.py:87-120`). For local work: `huggingface-cli download cyber2a/2026GeoAIArcticChallengeDataset --repo-type dataset --local-dir ./dataset`, then unzip. Train set = 756 chips.
- **Caching:** the RAM preload (10.3 GB) is the main scalability constraint — prefer lazy loading + `num_workers>0` over threads.
- ⚠ Neither compendium documents the *evaluation protocol* (IoU sweep, maxDets, size-bucket cutoffs). Standard COCO is AP@[.50:.95], maxDets=100, small<32², medium<96² — **but on 289×159 chips, "small" <1024 px is where ~55% of V4B predictions live**, so confirm the exact protocol before optimizing buckets.

### 4.2 Review of the 20-image 4-panel audit pipeline (V4A Cell 17 / V4C Cell 10)
Verdict: **directionally useful, materially flawed.**
1. **"False-Color RGB" is built from z-scored channels** (`img_tensor[5/3/1]`, then min-max) — the model input, not raw reflectance. Colors are washed out and not a true false-color composite; use raw npz bands with a 2–98 percentile stretch.
2. **IoU shown is chip-level semantic IoU** (all instances merged), not instance-matched — it cannot reveal the merge/split failures and AP75 boundary behavior that actually drive the score.
3. **The audited chips are training chips** (leakage V1): the gallery measures memorization, not spatial reasoning. It *will* look excellent regardless of generalization.
4. **The V4A gallery applies morphology + DP smoothing while V4C does not** — the visualizer config drifts from the production config; audits must mirror the exact submission path.
5. Minor: repeated `label=` per contour (legend never rendered); `plt.show()` in library code; positive-chip selection scans only the first 150 chips in V4C.

### 4.3 Deliverable — `FROSTWATCH_AUDIT_TOOLKIT.py`
A self-contained audit script (written alongside this report) with four modes:
- `python FROSTWATCH_AUDIT_TOOLKIT.py stats` — annotation census: instance count, area distribution, COCO bucket shares, per-image density, positive-chip fraction.
- `... gallery --n 20` — 4-panel visual audit **from raw npz reflectance** (true false-color RGB), GT contours, NDVI/NDWI physics panels, overlay; works **without checkpoints** (model-independent GT audit), and adds probability + prediction panels when `--ckpt-dir` is supplied.
- `... submission <file.json>` — the forensics of §3.1 on any submission JSON (counts, density histogram, score/area distributions, area-bucket shares, score↔area correlation).
- `... verify-tensor` — numerical sanity check of the 13-channel construction on a sample chip (index ranges ∈ [−1,1], ordering invariants).

---

## 5. Pillar 4 — Future Roadmap (V5) & Score Trajectory

### 5.1 Reality check on the 25–35 mAP target
Literature bounds: DARTS pan-Arctic RTS F1 = 0.263–0.70 (regional specialization up to 0.85, Huang et al.); 12-expert inter-annotator disagreement on RTS *boundaries* (Nitze et al. 2025) imposes a hard ceiling on high-IoU matching — GT polygons themselves are noisy, which caps AP75/AP90 more than model capacity does. Pixel-F1 ≈ 0.7 typically co-exists with COCO mAP well below 30 when instances are small and boundaries contested. **A defensible target band is mAP 18–25 with AP50 50–65**; 30+ requires the instance-level and FP-rejection wins below, and possibly favorable test-region density (DARTS: accuracy scales with RTS density).

### 5.2 Prioritized V5 backlog
| P | Item | Mechanism | Expected effect |
|---|---|---|---|
| 0 | **Honest holdout** (split by scene/region, not random chip) + re-rank ensemble weights and all thresholds on it | Fixes V1; every downstream decision currently tuned on noise | Correctness of all tuning |
| 0 | **Dual-threshold refinement + ranking-based scoring + top-k** (§3.3.1–3) | Decouples recall from boundary precision; exploits ranking invariance | Largest AP75/AP lever; +4–8 AP plausible |
| 1 | **Aspect-preserving resize (pad to 512)** at train & test; unify area filters to one coordinate system | Removes anisotropic geometry bias | AP75 & morphology fidelity |
| 2 | **Fix focal α; recompute indices after photometric augs; resize GaussNoise to σ≈0.01–0.05 or drop** | Removes label noise & physics inconsistency | Cleaner training, +1–2 AP |
| 3 | **NDWI water-mask + GLCM entropy rejection of flat bare-soil FPs** (Witharana L2 ruleset; DARTS land-cover masking) | Direct precision on the two dominant FP classes per literature | +2–4 AP in AP/precision-heavy regimes |
| 4 | **Watershed instance splitting + border suppression** | Recovers merged GT instances; removes seam fragments | AP & AR on clustered slumps |
| 5 | **Dual-stream morphology channels**: Top-Hat (bright scarp rims) & Black-Hat (dark saturated troughs) appended as channels 13–14, computed on the albedo channel before normalization | Literature-native feature explicitation (Witharana's workhorse operators) | +1–3 AP, cheap |
| 6 | **V2+V4 grand ensemble** (if V2 checkpoints survive): V2 is still the leaderboard-best model (13.88); blend its probability maps with V4's | Free diversity across resolutions/inputs | +1–3 AP |
| 7 | **Foundation-model adaptation — with caveats**: Prithvi-EO-2.0 is 30 m HLS 6-band (resolution & band mismatch with 3 m 8-band PlanetScope); Clay is RGBN-only. Realistic path: frozen FM stem is *not* usable; instead LoRA-adapt a ViT encoder with a **band-adapter conv stem** (8+5 → 3-ch projected) and train the decoder; treat as an architecture swap for one ensemble member, not a backbone for all | Hyped but high-variance | Unknown; budget-box it |
| 8 | Boundary-aware losses (e.g., Boundary Loss / Tversky-on-edges) replacing plain Focal in Phase 1; per-image Lovász | Boundary sharpening where labels permit | AP75 |
| 9 | Region-balanced sampling + seasonal/lighting augmentation (albumentations), per DARTS' domain-shift findings (Witharana: cross-tundra F1 0.92→0.81) | Generalization variance | Test-region robustness |
| 10 | Repo hygiene: single canonical training file, honest experiment log, submission archive keyed to config | Reproducibility | — |

### 5.3 Immediate next submission (V4D) — concrete recipe
Floor 0.30 (fixed, no Otsu) · detect at 0.30, refine masks at per-instance 0.5 level set · MIN_AREA 8 model-space-equivalent, stated in original coords as 8 px · top-k 6/image · watershed split · NDWI>0.3 down-rank · logit-ensemble · no morphology, no DP smoothing · expected ~350–450 predictions. Ablate one variable per submission while submission quota lasts.

---

## 6. Verdict

The FrostWatch system is scientifically literate and engineering-sound at its core (physics tensor, loss phasing, ensemble design, and the V4C post-processing philosophy are all defensible). Its two systemic weaknesses are **measurement** (contaminated validation that inflates model confidence and mis-tunes every threshold) and **mis-modeled optimization objective** (fighting prediction *count* instead of score *ordering* and boundary fidelity). Fixing the validation split, adopting dual-threshold instance refinement with ranking-aware scoring, and unifying the coordinate system of all geometric filters is the shortest path from 13.88 toward the low-20s — with literature suggesting the high-20s/30s band requires the FP-rejection and instance-splitting wins on top, and a favorable test-region density.
