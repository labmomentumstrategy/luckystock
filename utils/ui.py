import streamlit as st
from pathlib import Path
import subprocess


def load_css(file_name="assets/style.css"):
    """
    Load an external CSS file and inject it into the Streamlit app.
    
    Args:
        file_name (str): Relative path to the CSS file (e.g., "assets/style.css")
    """
    # Use absolute path based on this file's location to avoid CWD issues
    css_path = Path(__file__).parent.parent / file_name
    
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {file_name}")

def inject_scanline_effect():
    """Inject the scanline HTML div (CSS handles the styling)."""
    st.markdown('<div class="scanline"></div>', unsafe_allow_html=True)


def render_sidebar():
    """Render the unified sidebar content (Navigation + CTAs + Learn More)."""
    with st.sidebar:
        # Navigation
        st.subheader("📍 Navigation")
        st.page_link("app.py", label="Observatory (Home)", icon="🔭")
        st.page_link("pages/1_Stock_Query.py", label="Stock Scanner", icon="📈")
        st.page_link("pages/2_Telegram_Channel.py", label="Telegram Channel", icon="📢", disabled=True)
        st.page_link("https://medium.com", label="Medium Theory", icon="📝", disabled=True)
        st.page_link("https://youtube.com", label="YouTube Stats", icon="📺", disabled=True)

        # --- Version ---
        st.markdown("---")
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%h | %cd", "--date=short"],
                capture_output=True, text=True, timeout=3
            )
            st.caption(f"🔖 {result.stdout.strip()}")
        except Exception:
            st.caption("🔖 version unknown")

        # --- System Resource Status ---
        try:
            from utils.system import get_memory_usage
            used_mb, limit_mb, mem_percent = get_memory_usage()
            
            # 直接在 Commit 資訊正下方顯示 RAM 資訊與進度條，不做收合
            st.caption(f"📟 RAM: {used_mb:.1f} MB / {limit_mb:.0f} MB")
            st.progress(min(1.0, mem_percent / 100.0))
        except Exception:
            pass

