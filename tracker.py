"""
tracker.py — Registro de visitas y preguntas en Google Sheets

Configuración necesaria en st.secrets (secrets.toml):

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

Pasos para configurarlo:
1. Ir a console.cloud.google.com → crear proyecto → activar Google Sheets API
2. Crear Service Account → descargar JSON de credenciales
3. Pegar los campos del JSON en st.secrets bajo [gcp_service_account]
4. Crear una Google Sheet con dos pestañas: "visitas" y "preguntas"
5. Compartir la Sheet con el email del Service Account (editor)
6. Copiar el ID de la URL de la Sheet en spreadsheet_id
"""

import streamlit as st
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


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
    """Devuelve la pestaña indicada de la spreadsheet."""
    client = _get_client()
    if client is None:
        return None
    try:
        spreadsheet_id = st.secrets["gsheets"]["spreadsheet_id"]
        sheet = client.open_by_key(spreadsheet_id)
        return sheet.worksheet(tab_name)
    except Exception as e:
        print(f"[tracker] Error accediendo a pestaña '{tab_name}': {e}")
        return None


def log_visit():
    """
    Registra una visita nueva en la pestaña 'visitas'.
    Se llama una vez por sesión usando session_state.
    Columnas: timestamp | session_id
    """
    if st.session_state.get("visit_logged"):
        return

    ws = _get_sheet("visitas")
    if ws is None:
        return

    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        session_id = st.runtime.scriptrunner.get_script_run_ctx().session_id
        ws.append_row([now, session_id], value_input_option="USER_ENTERED")
        st.session_state.visit_logged = True
    except Exception as e:
        print(f"[tracker] Error registrando visita: {e}")


def log_question(question: str):
    """
    Registra una pregunta en la pestaña 'preguntas'.
    Columnas: timestamp | session_id | pregunta
    """
    ws = _get_sheet("preguntas")
    if ws is None:
        return

    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        session_id = st.runtime.scriptrunner.get_script_run_ctx().session_id
        ws.append_row([now, session_id, question], value_input_option="USER_ENTERED")
    except Exception as e:
        print(f"[tracker] Error registrando pregunta: {e}")


def get_stats() -> dict:
    """
    Devuelve estadísticas básicas para el panel Admin.
    Retorna dict con: total_visits, total_questions, top_questions
    """
    stats = {
        "total_visits": "—",
        "total_questions": "—",
        "top_questions": [],
        "recent_questions": [],
    }

    try:
        ws_visits = _get_sheet("visitas")
        ws_questions = _get_sheet("preguntas")

        if ws_visits:
            visits = ws_visits.get_all_values()
            stats["total_visits"] = max(0, len(visits) - 1)  # -1 por cabecera

        if ws_questions:
            rows = ws_questions.get_all_values()
            data_rows = rows[1:] if len(rows) > 1 else []  # skip header
            stats["total_questions"] = len(data_rows)

            # Top 5 preguntas más frecuentes
            from collections import Counter
            questions_list = [r[2] for r in data_rows if len(r) > 2]
            top = Counter(questions_list).most_common(5)
            stats["top_questions"] = top

            # Últimas 10 preguntas
            stats["recent_questions"] = [
                (r[0], r[2]) for r in reversed(data_rows[-10:]) if len(r) > 2
            ]

    except Exception as e:
        print(f"[tracker] Error obteniendo stats: {e}")

    return stats