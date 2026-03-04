"""HTTP client wrapper for the FastAPI backend."""

import os
from typing import Optional

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")


def _handle_error(resp: requests.Response) -> None:
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        st.error(f"API Error ({resp.status_code}): {detail}")


def api_get(path: str, params: Optional[dict] = None):
    try:
        resp = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=10)
        if resp.status_code >= 400:
            _handle_error(resp)
            return None
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running?")
        return None
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_post(path: str, data: dict):
    try:
        resp = requests.post(f"{API_BASE_URL}{path}", json=data, timeout=30)
        if resp.status_code >= 400:
            _handle_error(resp)
            return None
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running?")
        return None
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_put(path: str, data: dict):
    try:
        resp = requests.put(f"{API_BASE_URL}{path}", json=data, timeout=30)
        if resp.status_code >= 400:
            _handle_error(resp)
            return None
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running?")
        return None
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_patch(path: str, data: dict):
    try:
        resp = requests.patch(f"{API_BASE_URL}{path}", json=data, timeout=30)
        if resp.status_code >= 400:
            _handle_error(resp)
            return None
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running?")
        return None
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_delete(path: str) -> bool:
    try:
        resp = requests.delete(f"{API_BASE_URL}{path}", timeout=10)
        if resp.status_code >= 400:
            _handle_error(resp)
            return False
        return True
    except requests.ConnectionError:
        st.error("Cannot connect to API. Is the backend running?")
        return False
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return False


def api_health() -> bool:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def get_export_url(assessment_id: str, fmt: str) -> str:
    return f"{API_BASE_URL}/api/assessments/{assessment_id}/export/{fmt}"
