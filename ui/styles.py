"""
DevShield AI — Custom CSS Styles
Dark glassmorphism theme with security-grade branding.
"""


def get_css() -> str:
    return """
    <style>
    /* ── Google Fonts ───────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Design Tokens ──────────────────────────────────────────────────── */
    :root {
        --bg-base:       #070b14;
        --bg-surface:    #0d1117;
        --bg-card:       rgba(255,255,255,0.04);
        --bg-card-hover: rgba(255,255,255,0.07);
        --border:        rgba(255,255,255,0.08);
        --border-accent: rgba(0,255,136,0.25);
        --green:         #00ff88;
        --blue:          #00b4ff;
        --purple:        #7c3aed;
        --text-1:        #e6edf3;
        --text-2:        #8b949e;
        --text-3:        #484f58;
        --critical:      #ff2d55;
        --high:          #ff6b00;
        --medium:        #ffd60a;
        --low:           #30d158;
        --info:          #636366;
        --radius:        12px;
        --radius-sm:     8px;
        --shadow-green:  0 0 30px rgba(0,255,136,0.08);
    }

    /* ── Reset / Base ───────────────────────────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }

    .stApp {
        background: var(--bg-base);
        background-image:
            radial-gradient(ellipse 60% 50% at 10% 20%, rgba(0,255,136,0.04) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 85% 75%, rgba(0,180,255,0.03) 0%, transparent 60%);
        font-family: 'Inter', system-ui, sans-serif;
        color: var(--text-1);
        min-height: 100vh;
    }

    /* ── Sidebar ────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: rgba(13,17,23,0.97) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(24px);
    }
    [data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; }

    /* ── Typography ─────────────────────────────────────────────────────── */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    h1 { font-size: 1.9rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.1rem !important; }

    /* ── Cards ──────────────────────────────────────────────────────────── */
    .ds-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 24px;
        backdrop-filter: blur(12px);
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 16px;
    }
    .ds-card:hover {
        border-color: var(--border-accent);
        box-shadow: var(--shadow-green);
    }

    /* ── Stat Cards ─────────────────────────────────────────────────────── */
    .stat-card {
        background: linear-gradient(135deg, rgba(0,255,136,0.06) 0%, rgba(0,180,255,0.04) 100%);
        border: 1px solid rgba(0,255,136,0.18);
        border-radius: var(--radius);
        padding: 22px 18px;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-value {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--green), var(--blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        display: block;
    }
    .stat-label {
        font-size: 0.72rem;
        color: var(--text-2);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 6px;
        display: block;
        font-weight: 500;
    }

    /* ── Severity Badges ────────────────────────────────────────────────── */
    .badge {
        display: inline-block;
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-CRITICAL { background:rgba(255,45,85,0.15);  color:#ff2d55; border:1px solid rgba(255,45,85,0.3);  }
    .badge-HIGH     { background:rgba(255,107,0,0.12);  color:#ff8c42; border:1px solid rgba(255,107,0,0.3);  }
    .badge-MEDIUM   { background:rgba(255,214,10,0.12); color:#ffd60a; border:1px solid rgba(255,214,10,0.3); }
    .badge-LOW      { background:rgba(48,209,88,0.12);  color:#30d158; border:1px solid rgba(48,209,88,0.3);  }
    .badge-INFO     { background:rgba(99,99,102,0.12);  color:#a0a0a0; border:1px solid rgba(99,99,102,0.3);  }

    /* ── Grade Display ──────────────────────────────────────────────────── */
    .grade-A { color: #30d158; font-size: 3rem; font-weight: 800; }
    .grade-B { color: #00b4ff; font-size: 3rem; font-weight: 800; }
    .grade-C { color: #ffd60a; font-size: 3rem; font-weight: 800; }
    .grade-D { color: #ff6b00; font-size: 3rem; font-weight: 800; }
    .grade-F { color: #ff2d55; font-size: 3rem; font-weight: 800; }

    /* ── OWASP Tag ──────────────────────────────────────────────────────── */
    .owasp-tag {
        display: inline-block;
        background: rgba(124,58,237,0.15);
        border: 1px solid rgba(124,58,237,0.35);
        color: #a78bfa;
        border-radius: 5px;
        padding: 2px 9px;
        font-size: 0.68rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.3px;
    }

    /* ── Confidence Bar ─────────────────────────────────────────────────── */
    .conf-wrap {
        background: rgba(255,255,255,0.08);
        border-radius: 100px;
        height: 5px;
        overflow: hidden;
        margin-top: 6px;
    }
    .conf-fill {
        height: 100%;
        border-radius: 100px;
        background: linear-gradient(90deg, var(--green), var(--blue));
        transition: width 0.6s cubic-bezier(.4,0,.2,1);
    }

    /* ── Primary Button ─────────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00b4ff 100%) !important;
        color: #070b14 !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 10px 22px !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.2px;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(0,255,136,0.35) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Inputs ─────────────────────────────────────────────────────────── */
    .stTextArea textarea,
    .stTextInput input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-1) !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: rgba(0,255,136,0.4) !important;
        box-shadow: 0 0 0 3px rgba(0,255,136,0.08) !important;
    }

    .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-1) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ── Code Blocks ────────────────────────────────────────────────────── */
    .stCodeBlock {
        border: 1px solid rgba(0,255,136,0.15) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ── Progress Bar ───────────────────────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--green), var(--blue)) !important;
    }

    /* ── Metrics ────────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 16px !important;
    }

    /* ── Tabs ───────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 4px;
        border-bottom: 1px solid var(--border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-2) !important;
        font-weight: 500 !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--green) !important;
        border-bottom: 2px solid var(--green) !important;
    }

    /* ── Expander ───────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-1) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Divider ────────────────────────────────────────────────────────── */
    hr { border-color: var(--border) !important; opacity: 0.4; }

    /* ── Logo Pulse ─────────────────────────────────────────────────────── */
    @keyframes glow-pulse {
        0%, 100% { text-shadow: 0 0 12px rgba(0,255,136,0.6); }
        50%       { text-shadow: 0 0 28px rgba(0,255,136,1), 0 0 50px rgba(0,180,255,0.4); }
    }
    .logo-pulse { animation: glow-pulse 3s ease-in-out infinite; }

    /* ── Slide-In Animation ─────────────────────────────────────────────── */
    @keyframes slide-up {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .slide-up { animation: slide-up 0.4s ease forwards; }

    /* ── Scrollbar ──────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0,255,136,0.25);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,255,136,0.45); }

    /* ── Info / Warning / Success banners ──────────────────────────────── */
    .ds-info    { background:rgba(0,180,255,0.08); border-left:3px solid #00b4ff; padding:12px 16px; border-radius:0 8px 8px 0; margin:8px 0; }
    .ds-success { background:rgba(0,255,136,0.08); border-left:3px solid #00ff88; padding:12px 16px; border-radius:0 8px 8px 0; margin:8px 0; }
    .ds-warn    { background:rgba(255,214,10,0.08); border-left:3px solid #ffd60a; padding:12px 16px; border-radius:0 8px 8px 0; margin:8px 0; }
    .ds-danger  { background:rgba(255,45,85,0.08);  border-left:3px solid #ff2d55; padding:12px 16px; border-radius:0 8px 8px 0; margin:8px 0; }

    /* ── Sidebar nav label ──────────────────────────────────────────────── */
    .sidebar-brand {
        text-align: center;
        padding: 20px 12px 12px;
    }
    .sidebar-brand-title {
        font-size: 1.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff88, #00b4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.03em;
    }
    .sidebar-brand-sub {
        font-size: 0.7rem;
        color: var(--text-2);
        margin-top: 2px;
        font-weight: 400;
    }
    </style>
    """
