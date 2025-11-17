import contextlib
import io
import os
from pathlib import Path

import streamlit as st

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


# ---- Helpers ----
def _persist_uploaded_file(uploaded_file, dest_path: Path) -> Path:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dest_path

def _default_imagefolder_if_empty(path_str: str) -> str:
    path_str = (path_str or "").strip()
    if path_str:
        return path_str
    # Mirror GUI3.py behavior: fallback to ./Input-Examples/imagefolder
    return os.path.join(os.getcwd(), "Input-Examples", "imagefolder")

def get_social_svg(name: str) -> str:
    """
    Ritorna una piccola SVG (badge tondo con iniziali) per il social indicato.
    NOTA: non è un logo ufficiale, ma un'icona generica auto-contenuta.
    """
    n = (name or "").strip().lower()

    # Colori "tipici" (non ufficiali)
    palette = {
        "linkedin":  ("#0A66C2", "in"),
        "facebook":  ("#1877F2", "f"),
        "instagram": ("#E1306C", "ig"),
        "threads":   ("#000000", "th"),
        "x":         ("#000000", "x"),
    }
    # Alias -> canonico
    aliases = {
        "ln": "linkedin",
        "linkedIn".lower(): "linkedin",
        "fb": "facebook",
        "ig": "instagram",
        "insta": "instagram",
        "threads": "threads",
        "tw": "x",
        "twitter": "x",
        "x (twitter)": "x",
    }
    canon = aliases.get(n, n)
    color, label = palette.get(canon, ("#888888", (canon[:2] or "?")))
    # SVG badge tondo con iniziali
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22" role="img" aria-label="{canon}">
  <circle cx="11" cy="11" r="10" fill="{color}"/>
  <text x="11" y="14" text-anchor="middle" font-size="10" font-family="Inter, Arial, sans-serif" fill="#FFFFFF">{label.upper()}</text>
</svg>'''
    return svg
