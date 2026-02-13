
import streamlit as st
import requests
import uuid
import threading


def get_client_id():
    """Generate or retrieve a client_id for this session."""
    if "client_id" not in st.session_state:
        st.session_state.client_id = str(uuid.uuid4())
    return st.session_state.client_id


def _send_event_async(url: str, payload: dict) -> None:
    """Fire-and-forget HTTP POST to GA4 (runs in background thread)."""
    try:
        requests.post(url, json=payload, timeout=3)
    except Exception:
        pass



def get_session_id():
    """Generate or retrieve a session_id for this session (timestamp)."""
    if "session_id" not in st.session_state:
        import time
        st.session_state.session_id = str(int(time.time()))
    return st.session_state.session_id


def track_event(event_name, params=None):
    """
    Send an event to GA4 via Measurement Protocol (non-blocking).
    
    Args:
        event_name (str): The name of the event (e.g., 'page_view', 'button_click').
        params (dict, optional): Additional parameters for the event.
    """
    # Retrieves secrets from Streamlit secrets
    ga4_secrets = st.secrets.get("ga4", {})
    measurement_id = ga4_secrets.get("measurement_id")
    api_secret = ga4_secrets.get("api_secret")
    
    if not measurement_id or not api_secret:
        # If secrets are missing, silently fail
        return

    client_id = get_client_id()
    session_id = get_session_id()
    
    # Enhanced core params for better user tracking
    core_params = {
        "session_id": session_id,
        "engagement_time_msec": "100",  # Critical for 'Active Users' counting
        "debug_mode": "true",  # Helpful for realtime debugging
    }
    
    # Merge core params with custom params
    final_params = {**core_params, **(params or {})}
    
    payload = {
        "client_id": client_id,
        "events": [{
            "name": event_name,
            "params": final_params
        }]
    }
    
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}"
    
    # Fire-and-forget: send in background thread to avoid blocking UI
    thread = threading.Thread(target=_send_event_async, args=(url, payload), daemon=True)
    thread.start()


def track_page_view(page_title, page_path="/"):
    """Helper to track page view events."""
    # Construct a fake URL for GA4 to report distinct pages
    base_url = "https://volume-momentum-radar.streamlit.app"
    full_url = f"{base_url}{page_path}"
    
    track_event("page_view", {
        "page_title": page_title,
        "page_location": full_url,
        "page_path": page_path
    })
