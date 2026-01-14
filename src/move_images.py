from pathlib import Path
import shutil

# -------------------
# CONFIG
# -------------------
TRAIN_DIR = Path("../src/extracted_content/dogs-vs-cats/train")
CATS_DIR = TRAIN_DIR / "cats"
DOGS_DIR = TRAIN_DIR / "dogs"

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# -------------------
def main():
    if not TRAIN_DIR.exists():
        raise FileNotFoundError(f"{TRAIN_DIR} does not exist")

    CATS_DIR.mkdir(parents=True, exist_ok=True)
    DOGS_DIR.mkdir(parents=True, exist_ok=True)

    moved_cats = 0
    moved_dogs = 0
    skipped = 0

    for img in TRAIN_DIR.iterdir():
        # skip directories
        if img.is_dir():
            continue

        if img.suffix.lower() not in ALLOWED_EXTS:
            continue

        name = img.name.lower()

        if name.startswith("cat."):
            shutil.move(str(img), str(CATS_DIR / img.name))
            moved_cats += 1
        elif name.startswith("dog."):
            shutil.move(str(img), str(DOGS_DIR / img.name))
            moved_dogs += 1
        else:
            skipped += 1

    print("Done.")
    print(f"Moved cats: {moved_cats}")
    print(f"Moved dogs: {moved_dogs}")
    print(f"Skipped (unrecognized filenames): {skipped}")

if __name__ == "__main__":
    main()