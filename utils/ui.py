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

        st.markdown("---")
        st.info("💡 **Pro Tip**: 使用 'Scanner'來幫你的持股動能健檢。")



        st.markdown("#### 📺 Learn More")
        st.markdown("觀看 YouTube 教學影片，了解如何使用此工具。")
        st.link_button("▶️ Watch Tutorial", "https://youtube.com/your_channel_link")

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

