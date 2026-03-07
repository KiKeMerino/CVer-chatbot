# Configuración (modelos, paths, etc.)
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "cv_collection"
EMBEDDING_MODEL = "text-embedding-3-large"

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { display: none !important; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f1117 !important;
    color: #e2e4eb !important;
}

*:not([data-testid="stIconMaterial"]):not([class*="material"]) {
    font-family: 'DM Sans', sans-serif;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f1117; }
::-webkit-scrollbar-thumb { background: #2a2d3e; border-radius: 4px; }

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background-color: #0a0c12 !important;
    border-right: 1px solid #1e2030 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
[data-testid="stSidebar"] label {
    color: #6b7280 !important;
    font-size: 0.82rem !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #9ca3af !important;
    font-size: 0.85rem !important;
}

.block-container {
    padding: 1.2rem 3rem 2rem 3rem !important;
    max-width: 900px !important;
}

h1, h2, h3 { color: #f0f2f8 !important; letter-spacing: -0.02em !important; }

.hero-wrap {
    margin: 0.5rem 0 1.2rem 0;
    padding: 1.6rem 2.2rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #141828 0%, #0f1117 60%, #111827 100%);
    border: 1px solid #1e2030;
    position: relative;
    overflow: hidden;
}

.hero-wrap::after {
    content: "";
    position: absolute;
    top: 0; right: 0;
    width: 300px; height: 300px;
    background: radial-gradient(circle at top right, rgba(56,189,248,0.07) 0%, transparent 65%);
    pointer-events: none;
}

.hero-prompt {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #38bdf8;
    opacity: 0.8;
    margin-bottom: 0.5rem;
}

.hero-name {
    font-size: 2.1rem;
    font-weight: 600;
    color: #f0f2f8;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 0.6rem;
}

.hero-bio {
    color: #8b93a7;
    font-size: 0.88rem;
    line-height: 1.65;
    max-width: 540px;
    margin-bottom: 1.2rem;
}

.hero-bio span { color: #38bdf8; font-weight: 500; }

.hero-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }

.tag {
    display: inline-block;
    padding: 0.22rem 0.65rem;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #38bdf8;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.2);
}

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #3d4460;
    margin-bottom: 0.7rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e2030;
}

.stButton > button {
    background: #141828 !important;
    border: 1px solid #1e2030 !important;
    color: #8b93a7 !important;
    font-size: 0.83rem !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
    background: rgba(56,189,248,0.06) !important;
}

.stButton > button[kind="primary"] {
    background: rgba(56,189,248,0.1) !important;
    border-color: rgba(56,189,248,0.4) !important;
    color: #38bdf8 !important;
    font-weight: 500 !important;
}

[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.9rem !important;
    line-height: 1.75 !important;
    color: #d1d5e0 !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #141828 !important;
    border: 1px solid #1e2030 !important;
    border-radius: 10px !important;
    padding: 0.8rem 1.2rem !important;
    margin-left: 2rem !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(56,189,248,0.04) !important;
    border: 1px solid rgba(56,189,248,0.1) !important;
    border-radius: 10px !important;
    padding: 0.8rem 1.2rem !important;
}

/* ── Chat input: kill the white wrapper ──────── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottom"] > div > div > div,
[data-testid="stChatInputContainer"],
.stChatInputContainer {
    background: #0f1117 !important;
    background-color: #0f1117 !important;
    border: none !important;
    border-top: 1px solid #1e2030 !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] {
    max-width: 780px !important;
    margin: 0 auto !important;
    background: transparent !important;
}

[data-testid="stChatInput"] textarea {
    background: #141828 !important;
    border: 1px solid #1e2030 !important;
    border-radius: 10px !important;
    color: #e2e4eb !important;
    font-size: 0.88rem !important;
    caret-color: #38bdf8 !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(56,189,248,0.5) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.08) !important;
}

[data-testid="stChatInput"] textarea::placeholder { color: #3d4460 !important; }

.stTextInput input {
    background: #141828 !important;
    border: 1px solid #1e2030 !important;
    color: #e2e4eb !important;
    border-radius: 8px !important;
}

[data-testid="stMetric"] {
    background: #141828 !important;
    border: 1px solid #1e2030 !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
}

[data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 600 !important; }

.stProgress > div > div {
    background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
    border-radius: 999px !important;
}

[data-testid="stNotification"] {
    background: #141828 !important;
    border: 1px solid #1e2030 !important;
    border-radius: 8px !important;
    color: #8b93a7 !important;
    font-size: 0.84rem !important;
}

hr { border-color: #1e2030 !important; }

.stSpinner > div { border-color: #38bdf8 transparent transparent transparent !important; }

code {
    background: #141828 !important;
    color: #38bdf8 !important;
    font-family: 'DM Mono', monospace !important;
    border: 1px solid #1e2030 !important;
    border-radius: 5px !important;
    padding: 0.1rem 0.4rem !important;
    font-size: 0.83rem !important;
}

.sidebar-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #2a2d3e !important;
    margin-bottom: 0.8rem;
}

.q-counter {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #3d4460;
    text-align: right;
    margin-bottom: 0.5rem;
}

[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 { color: #f0f2f8 !important; }
</style>
"""