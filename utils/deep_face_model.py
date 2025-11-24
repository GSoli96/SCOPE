import os
import requests
import gdown
from pathlib import Path

DEEPFACE_MODELS = [
    ("Facenet",
     "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet_weights.h5",
     ".deepface/weights/facenet_weights.h5"),

    ("VGG-Face",
     "https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5",
     ".deepface/weights/vgg_face_weights.h5"),

    ("ArcFace",
     "https://github.com/serengil/deepface_models/releases/download/v1.0/arcface_weights.h5",
     ".deepface/weights/arcface_weights.h5"),
]

downloaded_models = []

def safe_download(url: str, output: str, show_progress=False) -> bool:
    """
    Try to download with gdown, fallback to manual streaming download
    """
    os.makedirs(os.path.dirname(output), exist_ok=True)

    # ---- 1️⃣ Try gdown first ----
    try:
        if "drive.google.com" in url:
            gdown.download(url, output, quiet=not show_progress, fuzzy=True)
            return os.path.exists(output)
    except Exception:
        pass  # fallback below

    # ---- 2️⃣ Fallback: requests chunk download ----
    try:
        with requests.get(url, stream=True, timeout=20) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            chunk = 1024 * 1024

            with open(output, "wb") as f:
                downloaded = 0
                for data in r.iter_content(chunk):
                    f.write(data)
                    downloaded += len(data)
                    if show_progress and total:
                        pct = int(downloaded / total * 100)
                        print(f"\rDownloading {os.path.basename(output)} {pct}%", end="")
        return os.path.exists(output)
    except Exception as e:
        print(f"[!] Download failed: {e}")
        return False

def download_deepface_models(show_progress=False):
    """
    Download required DeepFace models safely.
    Returns dict: {model_name: downloaded_bool}
    """

    home = str(Path(os.getenv("DEEPFACE_HOME", Path.home())))
    results = {}
    for name, url, rel_path in DEEPFACE_MODELS:
        output = os.path.join(home, rel_path)

        if os.path.exists(output):
            results[name] = True
            continue

        print(f"[INFO] Downloading {name}...")
        ok = safe_download(url, output, show_progress)
        print(f"[OK] {name} saved to: {output}" if ok else f"[ERROR] {name} failed")
        results[name] = ok

        global downloaded_models
        downloaded_models.append(name)
