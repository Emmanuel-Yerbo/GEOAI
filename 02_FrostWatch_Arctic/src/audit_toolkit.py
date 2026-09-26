# ════════════════════════════════════════════════════════════════════════════════
# FROSTWATCH_AUDIT_TOOLKIT.py — Local dataset / prediction visual audit (V4D review)
# 2026 GeoAI Arctic Challenge (Cyber2A / HF) — companion to FROSTWATCH_DIAGNOSTIC_REVIEW.md
#
# Self-contained. Works WITHOUT model checkpoints (GT-only audit) and adds
# probability/prediction panels when checkpoints are supplied.
#
# Modes:
#   python FROSTWATCH_AUDIT_TOOLKIT.py stats
#   python FROSTWATCH_AUDIT_TOOLKIT.py gallery --n 20 [--ckpt-dir ./experiments_v4/checkpoints]
#   python FROSTWATCH_AUDIT_TOOLKIT.py submission JSONS/FrostWatch.json [more.json ...]
#   python FROSTWATCH_AUDIT_TOOLKIT.py verify-tensor
#
# Optional env: FROSTWATCH_DATA=<dataset root containing instances_train.json>
# If absent, common Kaggle/Colab/local paths are scanned; HF auto-download as fallback.
# ════════════════════════════════════════════════════════════════════════════════

import argparse
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

# ── Optional dependencies (graceful degradation) ────────────────────────────────
try:
    import cv2
except ImportError:
    sys.exit("opencv-python is required:  python -m pip install opencv-python-headless")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("matplotlib is required:  python -m pip install matplotlib")

try:
    from pycocotools import mask as mask_utils
    HAVE_PYCOCO = True
except ImportError:
    HAVE_PYCOCO = False

OUT_DIR = "./frostwatch_audit"
os.makedirs(OUT_DIR, exist_ok=True)

DATA_ROOT_CANDIDATES = [
    os.environ.get("FROSTWATCH_DATA", ""),
    "./dataset",
    "./dataset/competition_release",
    "/kaggle/working/dataset/competition_release",
    "/kaggle/working/dataset",
    "/kaggle/input/2026geoaiarcticchallengedataset",
    "/content/dataset",
]

BAND_NAMES = ["CoastalBlue", "Blue", "GreenI", "GreenII", "Yellow", "Red", "RedEdge", "NIR"]


# ── Dataset discovery ───────────────────────────────────────────────────────────
def find_dataset():
    for cand in DATA_ROOT_CANDIDATES:
        if cand and os.path.exists(cand):
            found = glob.glob(os.path.join(cand, "**", "instances_train.json"), recursive=True)
            if found:
                root = os.path.dirname(os.path.dirname(os.path.dirname(found[0])))
                return root, found[0]
    print("[!] Dataset not found locally. Attempting Hugging Face download...")
    try:
        from huggingface_hub import snapshot_download
        import zipfile
        dl = "./dataset"
        snapshot_download(repo_id="cyber2a/2026GeoAIArcticChallengeDataset",
                          repo_type="dataset", local_dir=dl)
        for zf in glob.glob(os.path.join(dl, "**", "*.zip"), recursive=True):
            with zipfile.ZipFile(zf, "r") as z:
                z.extractall(os.path.dirname(zf))
        found = glob.glob(os.path.join(dl, "**", "instances_train.json"), recursive=True)
        if found:
            return os.path.dirname(os.path.dirname(os.path.dirname(found[0]))), found[0]
    except Exception as e:
        print(f"[!] HF download failed: {e}")
    return None, None


def load_annotations(ann_file):
    with open(ann_file, "r") as f:
        coco = json.load(f)
    img_by_id = {im["id"]: im for im in coco["images"]}
    anns_by_img = defaultdict(list)
    for ann in coco["annotations"]:
        anns_by_img[ann["image_id"]].append(ann)
    return coco, img_by_id, anns_by_img


def decode_segmentation(seg, h, w):
    """Decode COCO segmentation (polygon list or RLE) into a binary mask."""
    mask = np.zeros((h, w), dtype=np.uint8)
    if isinstance(seg, list):
        for poly in seg:
            if len(poly) >= 6:
                pts = np.array(poly, dtype=np.int32).reshape(-1, 2)
                cv2.fillPoly(mask, [pts], 1)
    elif isinstance(seg, dict) and "counts" in seg:
        if not HAVE_PYCOCO:
            raise RuntimeError("pycocotools required for RLE annotations")
        if isinstance(seg["counts"], list):
            rle = mask_utils.frPyObjects(seg, h, w)
            m = mask_utils.decode(rle)
        else:
            m = mask_utils.decode(seg)
        if m.ndim == 3:
            m = m[:, :, 0]
        mask = np.maximum(mask, m.astype(np.uint8))
    return mask


def stretch(band, p2=2, p98=98):
    """Percentile stretch of a raw reflectance band for display."""
    lo, hi = np.percentile(band, p2), np.percentile(band, p98)
    if hi - lo < 1e-8:
        return np.zeros_like(band)
    return np.clip((band - lo) / (hi - lo), 0, 1)


def false_color_rgb(image8):
    """True false-color composite from RAW bands: R=B5, G=B3, B=B1, percentile-stretched."""
    rgb = np.zeros((image8.shape[0], image8.shape[1], 3), dtype=np.float32)
    rgb[:, :, 0] = stretch(image8[:, :, 5])
    rgb[:, :, 1] = stretch(image8[:, :, 3])
    rgb[:, :, 2] = stretch(image8[:, :, 1])
    return rgb


# ── Physics indices (mirror of production code, raw-domain) ─────────────────────
def compute_spectral_indices(image_8band):
    eps = 1e-8
    b = [image_8band[:, :, i].astype(np.float32) for i in range(8)]
    idx = np.zeros(image_8band.shape[:2] + (5,), dtype=np.float32)
    idx[:, :, 0] = (b[7] - b[5]) / (b[7] + b[5] + eps)   # NDVI
    idx[:, :, 1] = (b[3] - b[7]) / (b[3] + b[7] + eps)   # NDWI
    idx[:, :, 2] = (b[7] - b[6]) / (b[7] + b[6] + eps)   # NDRE
    idx[:, :, 3] = (b[5] - b[1]) / (b[5] + b[1] + eps)   # IOR
    idx[:, :, 4] = (b[0] + b[1] + b[3] + b[4]) / 4.0     # Albedo
    return idx


def find_image_file(root, file_name):
    for pattern in (os.path.join(root, "**", os.path.basename(file_name)),):
        found = glob.glob(pattern, recursive=True)
        if found:
            return found[0]
    return None


# ┐
# │ MODE: stats — annotation census
# ┘
def mode_stats(args):
    root, ann_file = find_dataset()
    if not ann_file:
        sys.exit("[!] instances_train.json not found. Set FROSTWATCH_DATA=<root>.")
    coco, img_by_id, anns_by_img = load_annotations(ann_file)
    n_img = len(coco["images"])
    n_ann = len(coco["annotations"])

    areas, per_img_counts, dims = [], Counter(), Counter()
    for ann in coco["annotations"]:
        a = ann.get("area")
        if a is None:
            seg = ann.get("segmentation")
            a = 0
            if isinstance(seg, dict) and HAVE_PYCOCO:
                s = dict(seg)
                if isinstance(s["counts"], str):
                    s["counts"] = s["counts"].encode()
                a = int(mask_utils.area(s))
        areas.append(a)
        per_img_counts[ann["image_id"]] += 1
    for im in coco["images"]:
        dims[(im.get("height"), im.get("width"))] += 1

    areas = np.array(areas, dtype=float)
    positive = sum(1 for c in per_img_counts.values() if c > 0)
    small = int((areas < 1024).sum())
    medium = int(((areas >= 1024) & (areas < 9216)).sum())
    large = int((areas >= 9216).sum())

    print("=" * 70)
    print(f"  DATASET CENSUS  ({ann_file})")
    print("=" * 70)
    print(f"  Images: {n_img} | Annotations: {n_ann}")
    print(f"  Positive chips: {positive} ({100*positive/max(n_img,1):.1f}%) | "
          f"Empty chips: {n_img - positive}")
    print(f"  Chip dims (h,w): {dict(dims)}")
    print(f"  Instances/chip — mean: {n_ann/max(positive,1):.2f} on positive | "
          f"max: {max(per_img_counts.values()) if per_img_counts else 0}")
    print(f"  Area px — min/p10/med/p90/max: "
          f"{areas.min():.0f} / {np.percentile(areas,10):.0f} / "
          f"{np.median(areas):.0f} / {np.percentile(areas,90):.0f} / {areas.max():.0f}")
    print(f"  COCO buckets — small(<1024): {small} ({100*small/len(areas):.1f}%) | "
          f"medium(1024-9216): {medium} ({100*medium/len(areas):.1f}%) | "
          f"large(>9216): {large} ({100*large/len(areas):.1f}%)")
    hist = Counter(per_img_counts.values())
    print(f"  Instances-per-chip histogram: {dict(sorted(hist.items()))}")


# ┐
# │ MODE: gallery — 4-panel visual audit (raw-reflectance based)
# ┘
def mode_gallery(args):
    root, ann_file = find_dataset()
    if not ann_file:
        sys.exit("[!] Dataset not found. Set FROSTWATCH_DATA=<root>.")
    coco, img_by_id, anns_by_img = load_annotations(ann_file)

    # Prefer positive chips, keep deterministic order
    positive = [im for im in coco["images"] if anns_by_img.get(im["id"])]
    empty = [im for im in coco["images"] if not anns_by_img.get(im["id"])]
    selected = (positive[:int(args.n * 0.8)] + empty[:args.n - int(args.n * 0.8)])[:args.n]

    # Optional model
    models = []
    if args.ckpt_dir:
        try:
            import torch
            import segmentation_models_pytorch as smp
        except ImportError:
            print("[!] torch/smp not installed — running GT-only audit.")
            args.ckpt_dir = None
    if args.ckpt_dir:
        registry = {
            "fpn_mit_b5": ("FPN", "mit_b5"),
            "unet_mit_b3": ("Unet", "mit_b3"),
            "unetpp_seresnext50": ("UnetPlusPlus", "se_resnext50_32x4d"),
            "deeplabv3p_efficientb5": ("DeepLabV3Plus", "efficientnet-b5"),
        }
        import torch
        dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        for name, (arch, enc) in registry.items():
            cp = os.path.join(args.ckpt_dir, f"{name}_best.pth")
            if os.path.exists(cp):
                m = getattr(smp, arch)(encoder_name=enc, encoder_weights=None,
                                       in_channels=13, classes=1).to(dev)
                ckpt = torch.load(cp, map_location=dev, weights_only=False)
                m.load_state_dict(ckpt.get("model_state_dict", ckpt.get("state_dict")))
                m.eval()
                models.append(m)
        print(f"  Loaded {len(models)} models from {args.ckpt_dir}")

    def predict_prob(image8):
        """Ensemble probability at native resolution (aspect-preserving pad)."""
        import torch
        h, w = image8.shape[:2]
        s = 512
        pad_h, pad_w = max(0, s - h), max(0, s - w)
        arr = cv2.copyMakeBorder(image8, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT_101)
        arr = cv2.resize(arr, (s, s), interpolation=cv2.INTER_LINEAR)
        t13 = compute_spectral_indices(arr)
        for c in range(t13.shape[2]):
            band = t13[:, :, c]
            p2, p98 = np.percentile(band, 2), np.percentile(band, 98)
            if p98 - p2 > 1e-8:
                band = np.clip(band, p2, p98)
            t13[:, :, c] = (band - band.mean()) / (band.std() + 1e-8)
        x = torch.from_numpy(t13.transpose(2, 0, 1)[None].astype(np.float32)).to(dev)
        probs = []
        with torch.no_grad():
            for m in models:
                for k in range(4):
                    xr = torch.rot90(x, k, dims=[2, 3])
                    p = torch.sigmoid(m(xr))
                    probs.append(torch.rot90(p, -k, dims=[2, 3])[0, 0].cpu().numpy())
                pf = torch.sigmoid(m(torch.flip(x, dims=[3])))
                probs.append(torch.flip(pf, dims=[3])[0, 0].cpu().numpy())
        prob = np.mean(probs, axis=0)
        prob = cv2.resize(prob, (s, s), interpolation=cv2.INTER_LINEAR)
        return prob[:h, :w] if pad_h == 0 and pad_w == 0 else prob[:h, :w]

    n_batches = (len(selected) + 4) // 5
    for b in range(n_batches):
        rows = selected[b * 5:(b + 1) * 5]
        fig, axes = plt.subplots(len(rows), 4, figsize=(20, 4.6 * len(rows)))
        if len(rows) == 1:
            axes = np.expand_dims(axes, 0)
        fig.suptitle(f"FrostWatch Audit Gallery — Batch {b+1}/{n_batches} "
                     f"(raw reflectance | {'model' if models else 'GT-only'})",
                     fontsize=15, fontweight="bold", y=0.995)

        for r, im in enumerate(rows):
            path = find_image_file(root, im["file_name"])
            if path is None:
                continue
            image8 = np.nan_to_num(np.load(path)["image"].astype(np.float32),
                                   nan=0.0, posinf=0.0, neginf=0.0)
            h, w = image8.shape[:2]
            gt = np.zeros((h, w), dtype=np.uint8)
            for ann in anns_by_img.get(im["id"], []):
                gt = np.maximum(gt, decode_segmentation(ann.get("segmentation"), h, w))

            rgb = false_color_rgb(image8)
            idx = compute_spectral_indices(image8)

            # Panel 1: true false-color RGB
            axes[r, 0].imshow(rgb)
            axes[r, 0].set_title(f"{im['file_name']}\nFalse-color RGB (B5/B3/B1, p2-98 stretch)",
                                 fontsize=10)
            axes[r, 0].axis("off")

            # Panel 2: GT + physics index (NDVI background)
            axes[r, 1].imshow(idx[:, :, 0], cmap="RdYlGn", vmin=-0.5, vmax=0.8)
            gt_cnts, _ = cv2.findContours(gt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in gt_cnts:
                if len(cnt) >= 3:
                    axes[r, 1].plot(cnt[:, 0, 0], cnt[:, 0, 1], color="#00FFFF", lw=2)
            axes[r, 1].set_title(f"GT on NDVI ({int(gt.sum())} px, "
                                 f"{len(gt_cnts)} instances)", fontsize=10)
            axes[r, 1].axis("off")

            if models:
                prob = predict_prob(image8)
                pred = (prob > args.threshold).astype(np.uint8)
                lab, n = cv2.connectedComponents(pred, connectivity=8)
                kept = np.zeros_like(pred)
                for i in range(1, n):
                    if (lab == i).sum() >= args.min_area:
                        kept[lab == i] = 1
                inter = (gt * kept).sum()
                union = ((gt + kept) > 0).sum()
                iou = inter / union if union else 1.0
                axes[r, 2].imshow(prob, cmap="viridis", vmin=0, vmax=1)
                axes[r, 2].set_title(f"Ensemble prob (fixed τ={args.threshold:.2f})", fontsize=10)
                axes[r, 3].imshow(rgb)
                for cnt in gt_cnts:
                    if len(cnt) >= 3:
                        axes[r, 3].plot(cnt[:, 0, 0], cnt[:, 0, 1], color="#00FF00", lw=2)
                pred_cnts, _ = cv2.findContours(kept, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in pred_cnts:
                    if len(cnt) >= 3:
                        axes[r, 3].plot(cnt[:, 0, 0], cnt[:, 0, 1], color="#FF00FF", lw=2, ls="--")
                axes[r, 3].set_title(f"GT (green) vs Pred (magenta) | chip IoU {iou:.3f}",
                                     fontsize=10)
            else:
                axes[r, 2].imshow(idx[:, :, 1], cmap="RdYlBu", vmin=-0.6, vmax=0.6)
                for cnt in gt_cnts:
                    if len(cnt) >= 3:
                        axes[r, 2].plot(cnt[:, 0, 0], cnt[:, 0, 1], color="#00FFFF", lw=2)
                axes[r, 2].set_title("GT on NDWI (water/saturation)", fontsize=10)
                axes[r, 3].imshow(rgb)
                for cnt in gt_cnts:
                    if len(cnt) >= 3:
                        axes[r, 3].plot(cnt[:, 0, 0], cnt[:, 0, 1], color="#00FF00", lw=2.5)
                axes[r, 3].set_title(f"GT overlay ({len(gt_cnts)} instances)", fontsize=10)
            axes[r, 2].axis("off")
            axes[r, 3].axis("off")

        plt.tight_layout()
        out = os.path.join(OUT_DIR, f"audit_gallery_part{b+1}.png")
        plt.savefig(out, dpi=180, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved {out}")


# ┐
# │ MODE: submission — JSON forensics
# ┘
def mode_submission(args):
    if not HAVE_PYCOCO:
        sys.exit("[!] pycocotools required for RLE decoding: python -m pip install pycocotools")
    for p in args.files:
        with open(p) as f:
            d = json.load(f)
        areas, scores, per_img = [], [], Counter()
        for a in d:
            rle = dict(a["segmentation"])
            rle["counts"] = rle["counts"].encode()
            areas.append(int(mask_utils.area(rle)))
            scores.append(a.get("score", 0))
            per_img[a["image_id"]] += 1
        areas, scores = np.array(areas, float), np.array(scores, float)
        n = len(d)
        small = int((areas < 1024).sum())
        medium = int(((areas >= 1024) & (areas < 9216)).sum())
        large = int((areas >= 9216).sum())
        la = np.log10(np.maximum(areas, 1))
        r = np.corrcoef(la, scores)[0, 1] if n > 2 else float("nan")
        print("=" * 70)
        print(f"  SUBMISSION: {p}")
        print("=" * 70)
        print(f"  Predictions: {n} | images: {len(per_img)} | "
              f"mean/max per img: {n/max(len(per_img),1):.2f} / {max(per_img.values())}")
        print(f"  Scores — min/p25/med/p75/max: "
              f"{scores.min():.3f} / {np.percentile(scores,25):.3f} / "
              f"{np.median(scores):.3f} / {np.percentile(scores,75):.3f} / {scores.max():.3f}")
        print(f"  Area px — min/p10/med/p90/max: {areas.min():.0f} / "
              f"{np.percentile(areas,10):.0f} / {np.median(areas):.0f} / "
              f"{np.percentile(areas,90):.0f} / {areas.max():.0f}")
        print(f"  COCO buckets — small: {small} ({100*small/n:.1f}%) | medium: {medium} "
              f"({100*medium/n:.1f}%) | large: {large} ({100*large/n:.1f}%)")
        print(f"  Pearson r(log10 area, score): {r:.3f}")
        print(f"  RLE size (h,w) of first entry: {d[0]['segmentation'].get('size')}")


# ┐
# │ MODE: verify-tensor — physics tensor sanity check
# ┘
def mode_verify_tensor(args):
    root, ann_file = find_dataset()
    if not root:
        sys.exit("[!] Dataset not found. Set FROSTWATCH_DATA=<root>.")
    files = sorted(glob.glob(os.path.join(root, "**", "*.npz"), recursive=True))[:3]
    for path in files:
        image8 = np.nan_to_num(np.load(path)["image"].astype(np.float32),
                               nan=0.0, posinf=0.0, neginf=0.0)
        idx = compute_spectral_indices(image8)
        ok_range = all(-1.001 <= idx[:, :, i].min() and idx[:, :, i].max() <= 1.001
                       for i in range(4))
        pos = bool((image8 >= 0).all())
        print(f"  {os.path.basename(path)}: shape={image8.shape} | "
              f"raw non-negative: {pos} | ratio indices in [-1,1]: {ok_range}")
        for i, name in enumerate(["NDVI", "NDWI", "NDRE", "IOR", "Albedo"]):
            ch = idx[:, :, i]
            print(f"    {name:7s} min={ch.min():+.3f} mean={ch.mean():+.3f} max={ch.max():+.3f}")
        if not ok_range:
            print("    [!] Ratio index outside [-1,1] — check for negative/zero reflectance "
                  "or NaN substitution artifacts.")
    print("  Verify: indices computed on RAW data BEFORE clip/z-score (ordering invariant "
          "matches production: FROSTWATCH_V4A.py:413-424).")


# ┐
# │ CLI
# ┘
def main():
    ap = argparse.ArgumentParser(description="FrostWatch local audit toolkit")
    sub = ap.add_subparsers(dest="mode", required=True)

    sub.add_parser("stats", help="Annotation census of instances_train.json")

    g = sub.add_parser("gallery", help="4-panel visual audit gallery")
    g.add_argument("--n", type=int, default=20)
    g.add_argument("--ckpt-dir", default=None,
                   help="Optional checkpoint dir; adds probability/prediction panels")
    g.add_argument("--threshold", type=float, default=0.32)
    g.add_argument("--min-area", type=int, default=8)

    s = sub.add_parser("submission", help="Submission JSON forensics")
    s.add_argument("files", nargs="+")

    sub.add_parser("verify-tensor", help="13-channel physics tensor sanity check")

    args = ap.parse_args()
    {"stats": mode_stats, "gallery": mode_gallery,
     "submission": mode_submission, "verify-tensor": mode_verify_tensor}[args.mode](args)


if __name__ == "__main__":
    main()
