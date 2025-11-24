import contextlib
import io
import os
import shutil
from typing import Any, Dict
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st

# ---- funzione per estrarre username da URL ----
def extract_username(url):
    if not isinstance(url, str) or url.strip() == "":
        return ""
    u = url.strip()
    parsed = urlparse(u)
    path = parsed.path

    # /in/username → linkedin
    # /profile/username
    # /@username → instagram / threads
    # /username
    name = path.split("/")[-1]

    # Se è @username → togli @
    return name.replace("@", "").strip()

# ---- Helpers ----
def _capture_run(func, *args, **kwargs):
    """Run a function capturing both stdout and stderr, returning the combined text."""
    buf_out, buf_err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        result = func(*args, **kwargs)
    return buf_out.getvalue() + buf_err.getvalue(), result

# ---- Patch tkinter messagebox used deep in the code so Streamlit can show messages ----
class _MsgShim:
    def showinfo(self, title, message):
        st.success(f"{title}: {message}")
    def showwarning(self, title, message):
        st.warning(f"{title}: {message}")
    def showerror(self, title, message):
        st.error(f"{title}: {message}")

def _patch_messagebox():
    try:
        import tkinter.messagebox as _mb
        shim = _MsgShim()
        for name in ("showinfo", "showwarning", "showerror"):
            setattr(_mb, name, getattr(shim, name))
        try:
            import social_mapper_automatic as _sma
            _sma.messagebox = _mb
        except Exception:
            pass
        try:
            import social_mapper_manual as _smm
            _smm.messagebox = _mb
        except Exception:
            pass
    except Exception:
        pass

def _default_imagefolder_if_empty(path_str: str) -> str:
    path_str = (path_str or "").strip()
    if path_str:
        return path_str
    # Mirror GUI3.py behavior: fallback to ./Input-Examples/imagefolder
    return os.path.join(os.getcwd(), "Input-Examples", "imagefolder")

def save_image(url_image_user, local_path_img):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(url_image_user, stream=True, headers=headers)
        response.raise_for_status()

        with open(local_path_img, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)

    except requests.exceptions.RequestException as e:
        print(e)
        raise Exception(f"Error while downloading image: {e}")

def format_social_sites_icons(sites: dict, width_height = None) -> str:
    """Restituisce solo le icone SVG dei social selezionati."""
    if not isinstance(sites, dict) or not sites:
        return "—"

    key_to_platform = {
        "ln": "linkedin",
        "fb": "facebook",
        "ig": "instagram",
        "th": "threads",
        "x":  "x",
    }

    icons_html = []

    for key, url in sites.items():
        if not url:
            continue
        platform = key_to_platform.get(key.lower())
        if not platform:
            continue

        svg = get_social_svg(platform, width_height)
        if svg:
            icons_html.append(f"<span style='margin-right:6px;'>{svg}</span>")

    if not sites:
        return "—"

    return "".join(icons_html)

def single_social_icon(code: str, width_height: int = 20):
    svg = get_social_svg({
        "ln": "linkedin",
        "fb": "facebook",
        "ig": "instagram",
        "th": "threads",
        "x":  "x"
    }[code], width_height=width_height)
    return f"<span style='vertical-align:middle;'>{svg}</span>"


# ------------------------------------------------
# SVG ICONS FOR SOCIALS
# ------------------------------------------------
def get_social_svg(platform, width_height=None):
    platform = platform.lower().strip()

    if width_height is None:
        width_height = 14

    icons = {
        "facebook": f"""<svg width="{width_height}" height="{width_height}" fill="#1877F2" viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.5 9.9v-7h-2v-3h2v-2.3c0-2 1.2-3.1 3-3.1.9 0 1.8.1 1.8.1v2h-1c-1 0-1.3.6-1.3 1.2V12h2.2l-.4 3h-1.8v7A10 10 0 0 0 22 12"/></svg>""",
        "linkedin": f"""<svg width="{width_height}" height="{width_height}" fill="#0A66C2" viewBox="0 0 24 24"><path d="M20 2H4C3 2 2 3 2 4v16c0 1 .9 2 2 2h16c1 0 2-1 2-2V4c0-1-.9-2-2-2zM8.3 18H5.6v-8h2.7v8zM7 8.7c-.9 0-1.6-.7-1.6-1.6S6.1 5.6 7 5.6s1.6.7 1.6 1.6S7.9 8.7 7 8.7zm11 9.3h-2.7v-4c0-1 0-2.3-1.4-2.3-1.4 0-1.6 1.1-1.6 2.2v4h-2.7v-8h2.6v1.1h.1c.4-.8 1.3-1.4 2.7-1.4 2.9 0 3.4 1.9 3.4 4.3v4z"/></svg>""",
        "instagram": f"""<svg width="{width_height}" height="{width_height}" fill="#E4405F" viewBox="0 0 24 24"><path d="M12 2.2c3 0 3.3 0 4.4.1 1 .1 1.7.3 2.3.6.6.4 1.1.8 1.6 1.4.5.5 1 1 1.4 1.6.3.6.5 1.3.6 2.3.1 1 .1 1.4.1 4.4s0 3.3-.1 4.4c-.1 1-.3 1.7-.6 2.3-.4.6-.8 1.1-1.4 1.6-.5.5-1 .9-1.6 1.4-.6.3-1.3.5-2.3.6-1 .1-1.4.1-4.4.1s-3.3 0-4.4-.1c-1-.1-1.7-.3-2.3-.6-.6-.4-1.1-.8-1.6-1.4-.5-.5-1-1-1.4-1.6-.3-.6-.5-1.3-.6-2.3C2.2 15.3 2.2 15 2.2 12s0-3.3.1-4.4c.1-1 .3-1.7.6-2.3.4-.6.8-1.1 1.4-1.6.5-.5 1-.9 1.6-1.4.6-.3 1.3-.5 2.3-.6C8.7 2.2 9 2.2 12 2.2m0 3.3A6.5 6.5 0 1 0 18.5 12 6.47 6.47 0 0 0 12 5.5zm6.8-.9a1.5 1.5 0 1 0 1.5 1.5 1.5 1.5 0 0 0-1.5-1.5zM12 8a4 4 0 1 1-4 4 4 4 0 0 1 4-4z"/></svg>""",
        "x": f"""<svg width="{width_height}" height="{width_height}" fill="#fff" viewBox="0 0 24 24"><path d="M18 2h3l-7 8 8 10h-6l-5-6-5 6H0l8-10L1 2h6l4 5 4-5z"/></svg>""",
        "threads": """<svg width="22" height="22" viewBox="0 0 24 24" fill="#000"><circle cx="12" cy="12" r="12" fill="black"/><text x="12" y="16" text-anchor="middle" font-size="14" font-family="Inter, Arial, sans-serif" fill="white" font-weight="bold">@</text></svg>"""       ,
}

    return icons.get(platform, "")

import math

# ========== Helper ==========
def is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    if isinstance(v, (list, dict, set, tuple)):
        return len(v) == 0
    return False

def dict_to_dataframe(d: Dict[str, Any]) -> pd.DataFrame:
    clean_items = [(str(k), str(v)) for k, v in d.items() if not is_empty(v)]
    if not clean_items:
        return pd.DataFrame(columns=["Campo", "Valore"])
    df = pd.DataFrame(clean_items, columns=["Campo", "Valore"])
    return df

def clean_dict(d):
    cleaned = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, float) and math.isnan(v):
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        cleaned[k] = v
    return cleaned