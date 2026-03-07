"""
tracker.py — Registro de visitas y preguntas en Google Sheets

Columnas en la Sheet:
  - visitas:   timestamp | session_id | visitor_id | ip | user_agent
  - preguntas: timestamp | session_id | visitor_id | pregunta

visitor_id: hash MD5 de IP + User-Agent. Identifica al mismo navegador/dispositivo
entre sesiones distintas, sin almacenar datos personales directamente.

Configuración en st.secrets (secrets.toml):

[gsheets]
spreadsheet_id = "tu_spreadsheet_id_aquí"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

[analytics]
ga_measurement_id = "G-XXXXXXXXXX"  # opcional
"""

import hashlib
import streamlit as st
from datetime import datetime, timezone
from collections import Counter

import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_visitor_info() -> tuple:
    """
    Extrae IP y User-Agent de los headers de Streamlit.
    Devuelve (visitor_id, ip, user_agent).

    visitor_id es un hash MD5 de IP+UA — permite reconocer al mismo
    usuario entre sesiones sin guardar datos personales directamente.
    """
    try:
        headers = st.context.headers
        # Streamlit Cloud pone la IP real en X-Forwarded-For
        ip = headers.get("X-Forwarded-For", headers.get("Remote-Addr", "unknown"))
        ip = ip.split(",")[0].strip()  # primera IP si hay proxies encadenados
        ua = headers.get("User-Agent", "unknown")
        visitor_id = hashlib.md5(f"{ip}|{ua}".encode()).hexdigest()[:12]
        return visitor_id, ip, ua
    except Exception:
        return "unknown", "unknown", "unknown"


def _get_session_id() -> str:
    try:
        return st.runtime.scriptrunner.get_script_run_ctx().session_id
    except Exception:
        return "unknown"


@st.cache_resource
def _get_client():
    """Crea y cachea el cliente de Google Sheets."""
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES,
        )
        return gspread.authorize(creds)
    except Exception as e:
        print(f"[tracker] No se pudo conectar a Google Sheets: {e}")
        return None


def _get_sheet(tab_name: str):
    client = _get_client()
    if client is None:
        return None
    try:
        spreadsheet_id = st.secrets["gsheets"]["spreadsheet_id"]
        return client.open_by_key(spreadsheet_id).worksheet(tab_name)
    except Exception as e:
        print(f"[tracker] Error accediendo a '{tab_name}': {e}")
        return None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ── Public API ────────────────────────────────────────────────────────────────

def log_visit():
    """
    Registra una visita en la pestaña 'visitas'. Una vez por sesión.
    Columnas: timestamp | session_id | visitor_id | ip | user_agent
    """
    if st.session_state.get("visit_logged"):
        return

    ws = _get_sheet("visitas")
    if ws is None:
        st.session_state.visit_logged = True
        return

    try:
        visitor_id, ip, ua = _get_visitor_info()
        ws.append_row(
            [_now(), _get_session_id(), visitor_id, ip, ua],
            value_input_option="USER_ENTERED"
        )
    except Exception as e:
        print(f"[tracker] Error registrando visita: {e}")
    finally:
        st.session_state.visit_logged = True


def log_question(question: str):
    """
    Registra una pregunta en la pestaña 'preguntas'.
    Columnas: timestamp | session_id | visitor_id | pregunta
    """
    ws = _get_sheet("preguntas")
    if ws is None:
        return

    try:
        visitor_id, _, _ = _get_visitor_info()
        ws.append_row(
            [_now(), _get_session_id(), visitor_id, question],
            value_input_option="USER_ENTERED"
        )
    except Exception as e:
        print(f"[tracker] Error registrando pregunta: {e}")


def get_stats() -> dict:
    """
    Devuelve estadísticas para el panel Admin.
    """
    stats = {
        "total_visits": "—",
        "unique_visitors": "—",
        "total_questions": "—",
        "top_questions": [],
        "recent_questions": [],
    }

    try:
        ws_visits = _get_sheet("visitas")
        ws_questions = _get_sheet("preguntas")

        if ws_visits:
            rows = ws_visits.get_all_values()
            data = rows[1:] if len(rows) > 1 else []
            stats["total_visits"] = len(data)
            # visitor_id está en columna índice 2
            unique = set(r[2] for r in data if len(r) > 2 and r[2] != "unknown")
            stats["unique_visitors"] = len(unique)

        if ws_questions:
            rows = ws_questions.get_all_values()
            data = rows[1:] if len(rows) > 1 else []
            stats["total_questions"] = len(data)

            # Top 5 preguntas (columna índice 3)
            questions_list = [r[3] for r in data if len(r) > 3]
            stats["top_questions"] = Counter(questions_list).most_common(5)

            # Últimas 10: (timestamp, visitor_id, pregunta)
            stats["recent_questions"] = [
                (r[0], r[2], r[3])
                for r in reversed(data[-10:])
                if len(r) > 3
            ]

    except Exception as e:
        print(f"[tracker] Error obteniendo stats: {e}")

    return stats