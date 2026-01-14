import random
import shutil
from pathlib import Path
from typing import List, Tuple

# -------------------
# CONFIG
# -------------------
ROOT = Path("../src/extracted_content/dogs-vs-cats")  # contains train/cats and train/dogs right now
INPUT_TRAIN = ROOT / "train"

OUT_TRAIN = ROOT / "train"
OUT_VAL   = ROOT / "val"
OUT_TEST  = ROOT / "test"

SPLIT = (0.8, 0.1, 0.1)   # train, val, test
SEED = 1337
MOVE_FILES = False        # False = copy (safe), True = move
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# -------------------
def list_images(folder: Path) -> List[Path]:
    return sorted([p for p in folder.iterdir()
                   if p.is_file() and p.suffix.lower() in ALLOWED_EXTS])

def split_list(items: List[Path], split: Tuple[float, float, float]):
    n = len(items)
    n_train = int(n * split[0])
    n_val   = int(n * split[1])
    # remainder goes to test
    train = items[:n_train]
    val   = items[n_train:n_train + n_val]
    test  = items[n_train + n_val:]
    return train, val, test

def ensure_dirs():
    for s in (OUT_TRAIN, OUT_VAL, OUT_TEST):
        for cls in ("cats", "dogs"):
            (s / cls).mkdir(parents=True, exist_ok=True)

def transfer(files: List[Path], dest_dir: Path):
    op = shutil.move if MOVE_FILES else shutil.copy2
    for src in files:
        dest = dest_dir / src.name
        if dest.exists():
            raise FileExistsError(
                f"File already exists: {dest}. "
                "Delete the destination folders or choose MOVE_FILES=False into a clean directory."
            )
        op(str(src), str(dest))

def main():
    if abs(sum(SPLIT) - 1.0) > 1e-9:
        raise ValueError(f"SPLIT must sum to 1.0, got {SPLIT} sum={sum(SPLIT)}")

    ensure_dirs()

    rng = random.Random(SEED)

    for cls in ("cats", "dogs"):
        src_dir = INPUT_TRAIN / cls
        if not src_dir.exists():
            raise FileNotFoundError(f"Missing folder: {src_dir}")

        files = list_images(src_dir)
        if not files:
            raise RuntimeError(f"No images found in {src_dir}")

        rng.shuffle(files)
        tr, va, te = split_list(files, SPLIT)

        # If you want to *keep* originals in dataset/train, leave MOVE_FILES=False.
        # If MOVE_FILES=True, note: train files stay in place only if we *don't* move them out.
        # So we handle it like this:
        if MOVE_FILES:
            # Move ALL files out of INPUT_TRAIN/cls, then move train split back in.
            # (Keeps the final structure clean.)
            temp_all = ROOT / "_temp_all" / cls
            temp_all.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.move(str(f), str(temp_all / f.name))

            # Now move into train/val/test
            transfer([temp_all / f.name for f in tr], OUT_TRAIN / cls)
            transfer([temp_all / f.name for f in va], OUT_VAL / cls)
            transfer([temp_all / f.name for f in te], OUT_TEST / cls)

            # cleanup temp folder (optional)
            try:
                (ROOT / "_temp_all" / cls).rmdir()
                (ROOT / "_temp_all").rmdir()
            except OSError:
                pass
        else:
            # Copy val/test out; keep train as-is, but train should only contain train split.
            # So: create a NEW clean train directory by copying train split into it too.
            # To avoid mixing, we’ll create ROOT/train_new then replace at the end.
            train_new = ROOT / "train_new" / cls
            train_new.mkdir(parents=True, exist_ok=True)

            transfer(tr, train_new)
            transfer(va, OUT_VAL / cls)
            transfer(te, OUT_TEST / cls)

    if not MOVE_FILES:
        # Replace existing train with train_new (safe-ish; you can comment this out if you prefer manual)
        backup = ROOT / "train_backup"
        if backup.exists():
            raise FileExistsError("train_backup already exists; remove it first to proceed.")
        shutil.move(str(OUT_TRAIN), str(backup))          # rename old train -> train_backup
        shutil.move(str(ROOT / "train_new"), str(OUT_TRAIN))  # rename train_new -> train

        print("Created new splits and replaced dataset/train with the train-only split.")
        print(f"Your original mixed train is saved at: {backup}")
    else:
        print("Moved files into train/val/test splits (no backup).")

    print("Done.")

if __name__ == "__main__":
    main()