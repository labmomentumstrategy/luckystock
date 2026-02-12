
import streamlit as st
import requests
import uuid

def get_client_id():
    """Generate or retrieve a client_id for this session."""
    if "client_id" not in st.session_state:
        st.session_state.client_id = str(uuid.uuid4())
    return st.session_state.client_id

def track_event(event_name, params=None):
    """
    Send an event to GA4 via Measurement Protocol.
    
    Args:
        event_name (str): The name of the event (e.g., 'page_view', 'button_click').
        params (dict, optional): Additional parameters for the event.
    """
    # Retrieves secrets from Streamlit secrets
    ga4_secrets = st.secrets.get("ga4", {})
    measurement_id = ga4_secrets.get("measurement_id")
    api_secret = ga4_secrets.get("api_secret")
    
    if not measurement_id or not api_secret:
        # If secrets are missing, silently fail (or log warning if logging set up)
        return

    client_id = get_client_id()
    
    payload = {
        "client_id": client_id,
        "events": [{
            "name": event_name,
            "params": params or {}
        }]
    }
    
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}"
    
    try:
        # Use a short timeout to not block UI
        requests.post(url, json=payload, timeout=2)
    except Exception as e:
        # Silently ignore errors to prevent UI disruption
        pass

def track_page_view(page_title):
    """Helper to track page view events."""
    track_event("page_view", {
        "page_title": page_title,
        "page_location": str(st.query_params) # Capture query params if any
    })
