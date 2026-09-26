# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║          FROSTWATCH V5 — PHASE C: CORRECTED 13ch + 2-MODEL ENSEMBLE         ║
# ║                    (all 756 chips, TTA, dual-threshold)                     ║
# ║                                                                              ║
# ║  SUPERSEDES the V4/V5 "13ch physics tensor" — see V5_COCO_AUTOPSY.md:        ║
# ║    The band mapping was WRONG since V4. band_names.json (organizer           ║
# ║    metadata, empirically verified on the NPZs) says the 8 channels are:      ║
# ║      0:red  1:green  2:blue  3:NDVI  4:relative_elevation  5:shaded_relief   ║
# ║      6:nir  7:NDWI                                                          ║
# ║    All 5 derived channels of the old stack were meaningless ratios.          ║
# ║    Channels 4-5 are DEM-derived — the DARTS slope-discrimination feature     ║
# ║    we thought was missing from the dataset.                                  ║
# ║                                                                              ║
# ║  NEW 13-CHANNEL STACK (true semantics, FIX-2 order preserved):               ║
# ║    raw 8 : red, green, blue, NDVI, rel_elev, shaded_relief, nir, NDWI        ║
# ║    der 5 : iron_oxide (r-b)/(r+b) | brightness (r+g+b)/3 |                   ║
# ║            slope (Sobel |grad rel_elev|) | curvature (Lap rel_elev) |        ║
# ║            veg_slope (NDVI x slope — low-veg steep ground = RTS)             ║
# ║                                                                              ║
# ║  AUTOPSY-DRIVEN POST-PROCESSING (V5_COCO_AUTOPSY.md):                        ║
# ║    - 58.5% of GT is COCO-small at native res → MIN_AREA 8 native, top-10     ║
# ║    - GT strictly disjoint; 42% of adjacent pairs <12px apart →               ║
# ║      dual-threshold (detect 0.30 / refine+split 0.50)                        ║
# ║    - 35.6% of GT touches chip borders → NO border suppression                ║
# ║    - score = 0.5*mean + 0.5*p95 (de-biases the log-area ranking bias)        ║
# ║    - 8-fold dihedral TTA per model (V2's boundary-denoising edge)            ║
# ║                                                                              ║
# ║  TRAINING: all 756 chips (recipe-lock step 3). The frozen 136-holdout is     ║
# ║  now INSIDE training — its IoU is logged as regression tracking only         ║
# ║  (contaminated, never for decisions). Checkpoint = final epoch (cosine→0).   ║
# ║  Crash-resilient: _last.pth (model+opt+sched+epoch) every eval; re-running   ║
# ║  the cell RESUMES from it.                                                   ║
# ║                                                                              ║
# ║  KAGGLE SETUP: attach the competition dataset. GPU: T4/P100.                 ║
# ║    Runtime budget: mit_b5 ~7.5h + mit_b3 ~4h + inference ~20min.             ║
# ║    If the session dies mid-training, just re-run — it resumes.               ║
# ║                                                                              ║
# ║  OUTPUT (/kaggle/working):                                                   ║
# ║    FrostWatch.json            — submission (upload to HF space)              ║
# ║    v5c_checkpoints/*.pth      — final model weights                          ║
# ║    V5_PHASE_C_REPORT.json     — regression numbers + submission audit        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import os
import sys
import json
import glob
import math
import random
import time
import warnings
from collections import defaultdict

os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from scipy import ndimage

torch.backends.cudnn.benchmark = True
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

try:
    import segmentation_models_pytorch as smp
    from pycocotools import mask as mask_utils
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    _HAVE_DEPS = True
except ImportError:
    _HAVE_DEPS = False

try:
    import albumentations as A
    _HAVE_A = True
except ImportError:
    _HAVE_A = False

SEED = 42
IMG_SIZE = 512
N_CHANNELS = 13

def seed_everything(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

seed_everything()

# ══════════════════════════════════════════════════════════════════════════════
# CELL 1: DATA DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════

DATA_ROOT_CANDIDATES = [
    "/kaggle/input/2026geoaiarcticchallengedataset/competition_release",
    "/kaggle/input/2026geoaiarcticchallengedataset",
    "/kaggle/working/dataset/competition_release",
    "/kaggle/working/dataset",
    "/content/drive/MyDrive/GeoAIArtic_Challenge/competition_release",
    "/content/dataset",
]

def find_data_dir():
    for cand in DATA_ROOT_CANDIDATES:
        if os.path.exists(cand):
            found = glob.glob(f"{cand}/**/instances_train.json", recursive=True)
            if found:
                return os.path.dirname(os.path.dirname(os.path.dirname(found[0])))
    found = (glob.glob("/kaggle/input/**/instances_train.json", recursive=True) +
             glob.glob("/kaggle/working/**/instances_train.json", recursive=True) +
             glob.glob("/content/**/instances_train.json", recursive=True))
    if found:
        return os.path.dirname(os.path.dirname(os.path.dirname(found[0])))
    return None

DATA_DIR = find_data_dir()
assert DATA_DIR is not None, ("Dataset not found — attach the competition "
                              "dataset as a notebook input and re-run.")
TRAIN_IMG_DIR = os.path.join(DATA_DIR, "train", "images")
TEST_IMG_DIR = os.path.join(DATA_DIR, "test", "images")
TRAIN_ANN_FILE = glob.glob(f"{DATA_DIR}/**/instances_train.json", recursive=True)[0]
TEST_MANIFEST = glob.glob(f"{DATA_DIR}/**/test_manifest.csv", recursive=True)[0]
print(f"[V5-C] Dataset root: {DATA_DIR}")

OUTPUT_DIR = "/kaggle/working" if os.path.exists("/kaggle") else "./v5_phase_c"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "v5c_checkpoints")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def import_prior_checkpoints():
    """Session continuity: copy checkpoints from ANY attached input into
    /kaggle/working/v5c_checkpoints/. Covers (a) a previous notebook's output
    mounted at /kaggle/input/<slug>/v5c_checkpoints/, (b) a manually-uploaded
    Kaggle dataset containing the checkpoints. Prints loudly what it found."""
    import shutil
    pats = ["/kaggle/input/*/v5c_checkpoints/*.pth",
            "/kaggle/input/*/*/v5c_checkpoints/*.pth",
            "/kaggle/input/v5c_checkpoints/*.pth"]
    copied = []
    for pat in pats:
        for src in glob.glob(pat):
            dst = os.path.join(CHECKPOINT_DIR, os.path.basename(src))
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied.append(os.path.basename(src))
    if copied:
        print(f"[V5-C] Imported {len(copied)} checkpoint(s) from attached "
              f"inputs: {sorted(set(copied))}")
    else:
        print("[V5-C] No prior checkpoints found in inputs "
              "(fresh start or none attached)")

import_prior_checkpoints()

with open(TRAIN_ANN_FILE, 'r') as f:
    coco_gt = json.load(f)
images = coco_gt['images']
anns = coco_gt['annotations']
id_to_file = {im['id']: im['file_name'] for im in images}
img_id_to_anns = defaultdict(list)
for a in anns:
    img_id_to_anns[a['image_id']].append(a)

# ── Frozen split (Phase A/B lock, regression tracking ONLY — now contaminated) ─
split_path = os.path.join(OUTPUT_DIR, "V5_HOLDOUT_SPLIT.json")
rng = random.Random(SEED)
per_chip = {im['file_name']: [im['id']] for im in images}
keys = sorted(per_chip.keys())
rng.shuffle(keys)
n_hold = max(1, int(round(len(keys) * 0.18)))
hold_keys = set(keys[:n_hold])
holdout_ids, train_ids = [], []
for k in keys:
    (holdout_ids if k in hold_keys else train_ids).extend(per_chip[k])
HOLDOUT_IDS = set(holdout_ids)
print(f"[V5-C] 756 chips total | frozen holdout (tracking only): {len(HOLDOUT_IDS)}")

# ══════════════════════════════════════════════════════════════════════════════
# CELL 2: CORRECTED PREPROCESSING (V5_COCO_AUTOPSY.md Finding 1)
# ══════════════════════════════════════════════════════════════════════════════

BANDS = {0: "red", 1: "green", 2: "blue", 3: "ndvi",
         4: "relative_elevation", 5: "shaded_relief", 6: "nir", 7: "ndwi"}

def compute_channels13(img8):
    """TRUE 13ch stack. Raw 8 (organizer semantics) + 5 valid derived channels.
    Called AFTER geometric augmentation (FIX-2 preserved: geometric transforms
    keep channel semantics; ratios stay physically consistent)."""
    eps = 1e-8
    red = img8[:, :, 0].astype(np.float32)
    green = img8[:, :, 1].astype(np.float32)
    blue = img8[:, :, 2].astype(np.float32)
    ndvi = img8[:, :, 3].astype(np.float32)
    rele = img8[:, :, 4].astype(np.float32)
    nir = img8[:, :, 6].astype(np.float32)
    ndwi = img8[:, :, 7].astype(np.float32)

    der = np.zeros(img8.shape[:2] + (5,), dtype=np.float32)
    der[:, :, 0] = (red - blue) / (red + blue + eps)
    der[:, :, 1] = (red + green + blue) / 3.0
    gy = cv2.Sobel(rele, cv2.CV_32F, 1, 0, ksize=3)
    gx = cv2.Sobel(rele, cv2.CV_32F, 0, 1, ksize=3)
    slope = np.sqrt(gx * gx + gy * gy)
    der[:, :, 2] = slope
    der[:, :, 3] = cv2.Laplacian(rele, cv2.CV_32F)
    der[:, :, 4] = ndvi * slope
    return np.concatenate([img8.astype(np.float32), der], axis=-1)

def clip_zscore(img):
    for c in range(img.shape[2]):
        band = img[:, :, c]
        p2, p98 = np.percentile(band, 2), np.percentile(band, 98)
        if p98 - p2 > 1e-8:
            band = np.clip(band, p2, p98)
        mu, sigma = band.mean(), band.std() + 1e-8
        img[:, :, c] = (band - mu) / sigma
    return img

def decode_ann_mask(img_id, H, W):
    mask = np.zeros((H, W), dtype=np.float32)
    for ann in img_id_to_anns.get(img_id, []):
        seg = ann.get('segmentation', None)
        if seg is None:
            continue
        if isinstance(seg, list):
            for poly in seg:
                if len(poly) >= 6:
                    pts = np.array(poly, dtype=np.int32).reshape(-1, 2)
                    cv2.fillPoly(mask, [pts], 1.0)
        elif isinstance(seg, dict) and 'counts' in seg:
            if isinstance(seg['counts'], list):
                rle = mask_utils.frPyObjects(seg, H, W)
                m = mask_utils.decode(rle)
            else:
                m = mask_utils.decode(seg)
            if m.ndim == 3:
                m = m[:, :, 0]
            mask = np.maximum(mask, m.astype(np.float32))
    return mask

def load_npz(path):
    img = np.load(path)['image'].astype(np.float32)
    return np.nan_to_num(img, nan=0.0, posinf=0.0, neginf=0.0)

def load_chip(img_id):
    base = os.path.basename(id_to_file[img_id])
    path = os.path.join(TRAIN_IMG_DIR, base)
    img = load_npz(path)
    H, W = img.shape[:2]
    return img, decode_ann_mask(img_id, H, W)

# ══════════════════════════════════════════════════════════════════════════════
# CELL 3: DATASET (geometric-only augs, indices after aug, pad-to-square 512)
# ══════════════════════════════════════════════════════════════════════════════

augment_fn = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.15, rotate_limit=45,
                       border_mode=cv2.BORDER_REFLECT_101, p=0.5),
])

class PhaseCDataset(Dataset):
    """Corrected 13ch @512 pad-to-square. Geometric augs on the RAW 8 channels,
    indices computed after (FIX-2), clip/z-score all 13, pad, resize."""
    def __init__(self, ids, augment=False, img_size=IMG_SIZE):
        self.ids = sorted(ids)
        self.augment = augment
        self.img_size = img_size

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        img8, mask = load_chip(self.ids[idx])
        if self.augment:
            aug = augment_fn(image=img8, mask=mask.astype(np.float32))
            img8, mask = aug['image'], aug['mask']
        img13 = compute_channels13(img8)
        img13 = clip_zscore(img13)
        img13 = np.nan_to_num(img13, nan=0.0, posinf=0.0, neginf=0.0)
        mask = (mask > 0.5).astype(np.float32)
        H, W = img13.shape[:2]
        s = max(H, W)
        sq_img = np.zeros((s, s, img13.shape[2]), dtype=np.float32)
        sq_mask = np.zeros((s, s), dtype=np.float32)
        sq_img[:H, :W] = img13
        sq_mask[:H, :W] = mask
        if s != self.img_size:
            sq_img = cv2.resize(sq_img, (self.img_size, self.img_size),
                                interpolation=cv2.INTER_LINEAR)
            sq_mask = cv2.resize(sq_mask, (self.img_size, self.img_size),
                                 interpolation=cv2.INTER_NEAREST)
            sq_mask = (sq_mask > 0.5).astype(np.float32)
        return (torch.from_numpy(sq_img.transpose(2, 0, 1)),
                torch.from_numpy(sq_mask[np.newaxis, :, :]))

def preprocess_npz(img8):
    """Inference-time preprocessing of a raw 8ch NPZ array → (1,13,512,512)
    padded-square tensor + the native (H,W) it came from."""
    img13 = compute_channels13(img8)
    img13 = clip_zscore(img13)
    img13 = np.nan_to_num(img13, nan=0.0, posinf=0.0, neginf=0.0)
    H, W = img13.shape[:2]
    s = max(H, W)
    sq = np.zeros((s, s, 13), dtype=np.float32)
    sq[:H, :W] = img13
    if s != IMG_SIZE:
        sq = cv2.resize(sq, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_LINEAR)
    t = torch.from_numpy(sq.transpose(2, 0, 1)[np.newaxis])
    return t, (H, W)

# ══════════════════════════════════════════════════════════════════════════════
# CELL 4: LOSSES (unchanged from Phase B — FIX-1 / FIX-4 verified there)
# ══════════════════════════════════════════════════════════════════════════════

class FocalDiceLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0, dice_weight=0.5):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.dice_weight = dice_weight

    def forward(self, logits, targets):
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        probs = torch.sigmoid(logits)
        pt = probs * targets + (1.0 - probs) * (1.0 - targets)
        at = self.alpha * targets + (1.0 - self.alpha) * (1.0 - targets)
        focal = (at * (1.0 - pt) ** self.gamma * bce).mean()
        smooth = 1.0
        inter = (probs * targets).sum(dim=(2, 3))
        union = probs.sum(dim=(2, 3)) + targets.sum(dim=(2, 3))
        dice = (1.0 - (2.0 * inter + smooth) / (union + smooth)).mean()
        return (1.0 - self.dice_weight) * focal + self.dice_weight * dice

class LovaszHingeLoss(nn.Module):
    @staticmethod
    def lovasz_grad(gt_sorted):
        p = len(gt_sorted)
        gts = gt_sorted.sum()
        intersection = gts - gt_sorted.float().cumsum(0)
        union = gts + (1 - gt_sorted).float().cumsum(0)
        jaccard = 1.0 - intersection / union
        if p > 1:
            jaccard[1:p] = jaccard[1:p] - jaccard[0:-1]
        return torch.clamp(jaccard, 0.0, None)

    def forward(self, logits, targets):
        losses = []
        for b in range(logits.shape[0]):
            tg = (targets[b].reshape(-1) > 0.5).float()
            if tg.sum() == 0:
                losses.append(torch.tensor(0.0, device=logits.device))
                continue
            signs = 2.0 * tg - 1.0
            errors = 1.0 - logits[b].reshape(-1) * signs
            errors_sorted, perm = torch.sort(errors, descending=True)
            gt_sorted = tg[perm]
            grad = self.lovasz_grad(gt_sorted)
            losses.append(torch.dot(F.relu(errors_sorted), grad))
        return torch.stack(losses).mean()

# ══════════════════════════════════════════════════════════════════════════════
# CELL 5: TRAINING ENGINE (all 756 chips, TRUE crash-resume, final-epoch ckpt)
# ══════════════════════════════════════════════════════════════════════════════

def build_model(arch, encoder):
    return getattr(smp, arch)(encoder_name=encoder, encoder_weights='imagenet',
                              in_channels=N_CHANNELS, classes=1)

@torch.no_grad()
def tracking_iou(model, loader):
    """Contaminated regression tracker (holdout is inside training now)."""
    model.eval()
    inter, union = 0.0, 0.0
    for img, mask in loader:
        img, mask = img.to(DEVICE), mask.to(DEVICE)
        prob = torch.sigmoid(model(img))
        pred = (prob > 0.5).float()
        inter += (pred * mask).sum().item()
        union += (pred.sum() + mask.sum()).item() - (pred * mask).sum().item()
    model.train()
    return inter / max(union, 1e-8)

def train_model(name, model, epochs, batch_size, grad_accum,
                lr=1e-4, wd=1e-4, warmup=5, lovasz_start=25, num_workers=2):
    train_ds = PhaseCDataset(train_ids, augment=True)
    hold_ds = PhaseCDataset(HOLDOUT_IDS, augment=False)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=True,
                              drop_last=False, persistent_workers=num_workers > 0)
    hold_loader = DataLoader(hold_ds, batch_size=batch_size, shuffle=False,
                             num_workers=max(1, num_workers), pin_memory=True)

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lr_lambda=lambda ep:
            (ep + 1) / warmup if ep < warmup
            else 0.5 * (1 + math.cos(math.pi * (ep - warmup) / max(1, epochs - warmup))))
    crit_fd = FocalDiceLoss()
    crit_lv = LovaszHingeLoss()

    last_path = os.path.join(CHECKPOINT_DIR, f"v5c_{name}_last.pth")
    final_path = os.path.join(CHECKPOINT_DIR, f"v5c_{name}_final.pth")
    start_ep = 0
    if os.path.exists(final_path):
        sd = torch.load(final_path, map_location='cpu', weights_only=False)
        model.load_state_dict(sd['model_state_dict'])
        print(f"[V5-C] {name}: final checkpoint exists — skipping training")
        return model
    if os.path.exists(last_path):
        sd = torch.load(last_path, map_location='cpu', weights_only=False)
        model.load_state_dict(sd['model_state_dict'])
        if 'opt_state_dict' in sd:
            opt.load_state_dict(sd['opt_state_dict'])
            sched.load_state_dict(sd['sched_state_dict'])
            start_ep = sd['epoch'] + 1
        print(f"[V5-C] {name}: RESUMING from epoch {start_ep}")
    model.to(DEVICE)

    t0 = time.time()
    for ep in range(start_ep, epochs):
        model.train()
        running, nsteps = 0.0, 0
        opt.zero_grad()
        for step, (img, mask) in enumerate(train_loader):
            img = img.to(DEVICE, non_blocking=True)
            mask = mask.to(DEVICE, non_blocking=True)
            logits = model(img)
            loss = crit_fd(logits, mask)
            if ep >= lovasz_start:
                loss = 0.70 * loss + 0.30 * crit_lv(logits, mask)
            (loss / grad_accum).backward()
            if (step + 1) % grad_accum == 0 or (step + 1) == len(train_loader):
                opt.step(); opt.zero_grad()
            running += loss.item(); nsteps += 1
        sched.step()

        if (ep + 1) % 5 == 0 or ep == epochs - 1:
            iou = tracking_iou(model, hold_loader)
            torch.save({"model_state_dict": model.state_dict(),
                        "opt_state_dict": opt.state_dict(),
                        "sched_state_dict": sched.state_dict(),
                        "epoch": ep, "tracking_iou": iou, "name": name},
                       last_path)
            print(f"[V5-C] {name} ep {ep+1:3d}/{epochs} | train "
                  f"{running/max(1,nsteps):.4f} | trackIoU* {iou:.4f} "
                  f"| {(time.time()-t0)/60:.0f}m  (*contaminated)")
    torch.save({"model_state_dict": model.state_dict(), "epoch": epochs - 1,
                "name": name}, final_path)
    if os.path.exists(last_path):
        os.remove(last_path)
    print(f"[V5-C] {name}: DONE — final checkpoint saved "
          f"({(time.time()-t0)/60:.0f}m this session)")
    return model

# ══════════════════════════════════════════════════════════════════════════════
# CELL 6: INFERENCE — 8-FOLD TTA + DUAL-THRESHOLD + p95 SCORING
# ══════════════════════════════════════════════════════════════════════════════

@torch.no_grad()
def predict_prob_tta(model, x):
    """8-fold dihedral TTA on a (1,13,512,512) square tensor → (1,1,512,512)."""
    model.eval()
    probs = []
    for k in range(4):
        for flip in (False, True):
            y = torch.rot90(x, k, dims=(2, 3))
            if flip:
                y = torch.flip(y, dims=(3,))
            p = torch.sigmoid(model(y.to(DEVICE)))
            if flip:
                p = torch.flip(p, dims=(3,))
            p = torch.rot90(p, -k, dims=(2, 3))
            probs.append(p.cpu())
    return torch.stack(probs).mean(0)

def prob_to_native(prob512, native_hw):
    """Crop the pad-square region back out, resize to native (H,W)."""
    H, W = native_hw
    S = prob512.shape[0]
    s = max(H, W)
    ch, cw = max(1, int(round(H / s * S))), max(1, int(round(W / s * S)))
    prob = prob512[:ch, :cw]
    return cv2.resize(prob, (W, H), interpolation=cv2.INTER_LINEAR)

THR_LO = 0.30    # detection threshold (recall)
THR_HI = 0.50    # refinement/split threshold (boundary + instance separation)
MIN_AREA = 8     # native px (autopsy: smallest GT 16 px)
TOP_K = 10       # autopsy: max GT density 10/chip

def instances_from_prob(prob):
    """Dual-threshold extraction (V5_COCO_AUTOPSY.md Finding 3):
    components at THR_LO; each component re-cut at THR_HI — surviving pieces
    (each >= MIN_AREA) become separate instances (this is also the instance
    SPLITTER for close pairs); a component with no surviving piece falls back
    to its full extent. Score = 0.5*mean + 0.5*p95."""
    binary = (prob > THR_LO).astype(np.uint8)
    labeled, n = ndimage.label(binary, structure=np.ones((3, 3), dtype=int))
    out = []
    for lab in range(1, n + 1):
        comp = labeled == lab
        if comp.sum() < MIN_AREA:
            continue
        refined = comp & (prob >= THR_HI)
        pieces = []
        if refined.sum() >= MIN_AREA:
            rl, rn = ndimage.label(refined.astype(np.uint8),
                                   structure=np.ones((3, 3), dtype=int))
            for r in range(1, rn + 1):
                m = rl == r
                if m.sum() >= MIN_AREA:
                    pieces.append(m)
        if not pieces:
            pieces = [comp]
        for m in pieces:
            pv = prob[m]
            score = 0.5 * float(pv.mean()) + 0.5 * float(np.percentile(pv, 95))
            out.append((m, score))
    out.sort(key=lambda t: -t[1])
    return out[:TOP_K]

@torch.no_grad()
def ensemble_instances(models, npz_path):
    """Full inference path: NPZ → 13ch@512 → per-model TTA prob (uniform
    average) → native prob → dual-threshold instances."""
    img8 = load_npz(npz_path)
    x, native_hw = preprocess_npz(img8)
    prob512 = None
    for m in models:
        p = predict_prob_tta(m, x)[0, 0].numpy()
        prob512 = p if prob512 is None else prob512 + p
    prob512 /= len(models)
    prob = prob_to_native(prob512, native_hw)
    return instances_from_prob(prob), native_hw

def rle_encode(mask):
    rle = mask_utils.encode(np.asfortranarray(mask.astype(np.uint8)))
    if isinstance(rle['counts'], bytes):
        rle['counts'] = rle['counts'].decode('ascii')
    return rle

# ══════════════════════════════════════════════════════════════════════════════
# CELL 7: HOLDOUT REGRESSION EVAL (contaminated — tracking only)
# ══════════════════════════════════════════════════════════════════════════════

def holdout_regression(models):
    hold_images = [im for im in images if im['id'] in HOLDOUT_IDS]
    hold_img_ids = {im['id'] for im in hold_images}
    hold_anns = [a for a in anns if a['image_id'] in hold_img_ids]
    gt_path = os.path.join(OUTPUT_DIR, "V5_HOLDOUT_GT.json")
    with open(gt_path, 'w') as f:
        json.dump({"images": hold_images, "annotations": hold_anns,
                   "categories": coco_gt.get('categories', [{"id": 1}])}, f)
    preds = []
    for iid in sorted(HOLDOUT_IDS):
        base = os.path.basename(id_to_file[iid])
        insts, _ = ensemble_instances(models, os.path.join(TRAIN_IMG_DIR, base))
        for m, score in insts:
            preds.append({"image_id": iid, "category_id": 1,
                          "segmentation": rle_encode(m),
                          "score": round(score, 4)})
    if not preds:
        return {"ap": None, "note": "no predictions"}
    coco = COCO(gt_path)
    dt = coco.loadRes(preds)
    ev = COCOeval(coco, dt, iouType='segm')
    ev.evaluate(); ev.accumulate(); ev.summarize()
    s = ev.stats
    return {"ap": 100*s[0], "ap50": 100*s[1], "ap75": 100*s[2],
            "ap_small": 100*s[3], "ap_medium": 100*s[4], "ap_large": 100*s[5],
            "ar_all": 100*s[8], "n_preds": len(preds),
            "note": "CONTAMINATED (holdout inside training) — tracking only"}

# ══════════════════════════════════════════════════════════════════════════════
# CELL 8: TEST SUBMISSION + SELF-AUDIT
# ══════════════════════════════════════════════════════════════════════════════

def generate_submission(models, out_path):
    manifest = pd.read_csv(TEST_MANIFEST)
    print(f"[V5-C] Test manifest: {len(manifest)} chips "
          f"(splits: {manifest['split'].value_counts().to_dict()})")
    preds = []
    t0 = time.time()
    for k, (_, row) in enumerate(manifest.iterrows()):
        img_id = int(row['image_id'])
        base = os.path.basename(row['file_name'])
        path = os.path.join(TEST_IMG_DIR, base)
        if not os.path.exists(path):
            hits = glob.glob(f"{DATA_DIR}/**/{base}", recursive=True)
            assert hits, f"test chip not found: {base}"
            path = hits[0]
        insts, _ = ensemble_instances(models, path)
        for m, score in insts:
            preds.append({"image_id": img_id, "category_id": 1,
                          "segmentation": rle_encode(m),
                          "score": round(score, 6)})
        if (k + 1) % 25 == 0:
            print(f"[V5-C]   test {k+1}/{len(manifest)} chips, "
                  f"{len(preds)} preds | {time.time()-t0:.0f}s")
    with open(out_path, 'w') as f:
        json.dump(preds, f)

    n_img = len({p['image_id'] for p in preds})
    scores = np.array([p['score'] for p in preds])
    areas = np.array([mask_utils.area(
        {**p['segmentation'],
         'counts': p['segmentation']['counts'].encode()}
        if isinstance(p['segmentation']['counts'], str) else p['segmentation'])
        for p in preds])
    audit = {
        "n_preds": len(preds), "images_with_preds": n_img,
        "preds_per_image": round(len(preds) / max(n_img, 1), 2),
        "score_min": float(scores.min()) if len(scores) else None,
        "score_median": float(np.median(scores)) if len(scores) else None,
        "score_max": float(scores.max()) if len(scores) else None,
        "area_p10": float(np.percentile(areas, 10)) if len(areas) else None,
        "area_median": float(np.median(areas)) if len(areas) else None,
        "area_p90": float(np.percentile(areas, 90)) if len(areas) else None,
        "share_lt_1024px": float((areas < 1024).mean()) if len(areas) else None,
    }
    print(f"[V5-C] SUBMISSION AUDIT: {json.dumps(audit, indent=2)}")
    print(f"[V5-C] GT density reference: 2.36/chip, expected ~326 preds")
    return audit

# ══════════════════════════════════════════════════════════════════════════════
# CELL 9: MAIN
# ══════════════════════════════════════════════════════════════════════════════

# (arch, encoder, name, epochs, batch, grad_accum)
MODEL_CONFIG = [
    ("FPN", "mit_b5", "fpn_mit_b5", 90, 4, 2),
    ("Unet", "mit_b3", "unet_mit_b3", 90, 8, 1),
]

# ── SESSION PLAN (the ONLY line you ever edit) ────────────────────────────────
#   Session 1 (new notebook):            leave as-is  → trains ONLY model 1
#                                         (~9h, finishes CLEANLY — never killed)
#   Session 2 (new notebook + Session 1  change to:
#   output attached as input):             SESSION_MODELS = ["fpn_mit_b5", "unet_mit_b3"]
#                                         (model 1 skips instantly via imported
#                                          checkpoint, model 2 trains ~4h, then
#                                          eval + FrostWatch.json)
#   Inference/submission only runs when ALL models in MODEL_CONFIG are ready.
SESSION_MODELS = ["fpn_mit_b5"]

def verify_channels():
    """Empirical sanity check of the corrected mapping on one chip."""
    iid = sorted(id_to_file)[0]
    img8, _ = load_chip(iid)
    ndvi, ndwi = img8[:, :, 3], img8[:, :, 7]
    ok = ((-1.001 <= np.nanmin(ndvi) and np.nanmax(ndvi) <= 1.001) and
          (-1.001 <= np.nanmin(ndwi) and np.nanmax(ndwi) <= 1.001))
    print(f"[V5-C] Channel verify (chip {iid}): NDVI range "
          f"[{np.nanmin(ndvi):.3f},{np.nanmax(ndvi):.3f}] NDWI range "
          f"[{np.nanmin(ndwi):.3f},{np.nanmax(ndwi):.3f}] -> "
          f"{'OK' if ok else 'MISMATCH! CHECK BAND ORDER'}")
    return ok

def main():
    if not _HAVE_DEPS:
        os.system(f"{sys.executable} -m pip install -q "
                  "segmentation-models-pytorch pycocotools")
        print("[V5-C] Dependencies installed — RESTART runtime and re-run.")
        return
    if not _HAVE_A:
        os.system(f"{sys.executable} -m pip install -q albumentations")
        print("[V5-C] albumentations installed — RESTART runtime and re-run.")
        return
    verify_channels()

    report = {"phase": "C", "models": [], "autopsy": "V5_COCO_AUTOPSY.md"}
    models = []
    for arch, enc, name, epochs, bs, ga in MODEL_CONFIG:
        if name not in SESSION_MODELS:
            print(f"\n[V5-C] ══ MODEL {name}: not in SESSION_MODELS — skipping "
                  f"(Session 2 will train it) ══")
            continue
        print(f"\n[V5-C] ══ MODEL {name} ({arch}/{enc}, {epochs} ep) ══")
        model = build_model(arch, enc)
        model = train_model(name, model, epochs, bs, ga)
        model.to(DEVICE).eval()
        models.append((name, model))

    if len(models) < len(MODEL_CONFIG):
        print(f"\n[V5-C] Incomplete ensemble ({len(models)}/{len(MODEL_CONFIG)} "
              f"models) — skipping eval + submission (this is Session 1's "
              f"expected exit). Checkpoints are saved in this notebook's "
              f"Output. Now create Session 2: attach this output + the "
              f"competition dataset, set SESSION_MODELS to BOTH names, "
              f"Save & Run All.")
        return

    print("\n[V5-C] ══ Holdout regression eval (CONTAMINATED — tracking only) ══")
    reg = holdout_regression([m for _, m in models])
    print(f"[V5-C] {json.dumps(reg)}")
    report["holdout_regression"] = reg

    print("\n[V5-C] ══ Test submission ══")
    sub_path = os.path.join(OUTPUT_DIR, "FrostWatch.json")
    audit = generate_submission([m for _, m in models], sub_path)
    report["submission_audit"] = audit
    with open(os.path.join(OUTPUT_DIR, "V5_PHASE_C_REPORT.json"), 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n[V5-C] DONE. Submit {sub_path} to the HF space.")

if __name__ == "__main__":
    main()
