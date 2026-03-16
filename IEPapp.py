"""
 DOE IEP Intelligence Platform
Entry point — run with: streamlit run IEPapp.py
"""

import streamlit as st

st.set_page_config(
    page_title="DOE · IEP Intelligence Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global Styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');

:root {
    --navy:    #0d1b2a;
    --blue:    #1b4f8a;
    --sky:     #2176ae;
    --accent:  #e63946;
    --gold:    #f4a261;
    --mint:    #06d6a0;
    --light:   #f8f9fa;
    --muted:   #8096b0;
    --mono:    'IBM Plex Mono', monospace;
    --sans:    'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 2px solid rgba(230,57,70,0.35);
}
[data-testid="stSidebar"] * { color: #c8d8ee !important; }
[data-testid="stSidebarNav"] a {
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 8px 14px !important;
    border-left: 2px solid transparent;
    transition: all 0.2s ease;
    border-radius: 0 !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(33,118,174,0.2) !important;
    border-left-color: var(--sky) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(230,57,70,0.15) !important;
    border-left-color: var(--accent) !important;
}

/* ── Cards ── */
.iep-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-top: 3px solid var(--sky);
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(13,27,42,0.06);
    transition: box-shadow 0.2s;
}
.iep-card:hover { box-shadow: 0 6px 20px rgba(13,27,42,0.12); }
.iep-card.accent { border-top-color: var(--accent); }
.iep-card.gold   { border-top-color: var(--gold); }
.iep-card.mint   { border-top-color: var(--mint); }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 60%, #1e5799 100%);
    border-radius: 10px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        45deg,
        transparent, transparent 30px,
        rgba(255,255,255,0.015) 30px, rgba(255,255,255,0.015) 60px
    );
}
.hero-title {
    font-size: 2rem; font-weight: 700; color: white;
    letter-spacing: -0.02em; margin-bottom: 8px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.hero-sub {
    font-size: 0.95rem; color: #a8c4e0;
    font-family: var(--mono); letter-spacing: 0.04em;
}
.hero-badge {
    display: inline-block;
    background: var(--accent); color: white;
    font-family: var(--mono); font-size: 0.7rem;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-right: 8px; margin-bottom: 12px;
}

/* ── Metric tiles ── */
.metric-tile {
    background: white;
    border-radius: 8px;
    padding: 20px 24px;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.metric-tile .num  { font-size: 2.2rem; font-weight: 700; color: var(--blue); }
.metric-tile .lbl  { font-size: 0.78rem; color: #64748b; text-transform: uppercase;
                     letter-spacing: 0.06em; font-family: var(--mono); margin-top: 4px; }

/* ── Section header ── */
.section-head {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 10px;
}
.section-head h2 {
    font-size: 1.1rem; font-weight: 600;
    color: var(--navy); margin: 0;
    letter-spacing: -0.01em;
}
.section-head .tag {
    font-family: var(--mono); font-size: 0.68rem;
    background: #eef2f8; color: var(--blue);
    padding: 2px 8px; border-radius: 4px;
    letter-spacing: 0.05em;
}

/* ── Table styles ── */
.stDataFrame { border-radius: 8px !important; overflow: hidden; }

/* ── Buttons ── */
.stButton > button {
    background: var(--sky) !important;
    color: white !important;
    border: none !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em !important;
    padding: 8px 20px !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--blue) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(27,79,138,0.3) !important;
}

/* ── Search input ── */
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
    font-family: var(--sans) !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--sky) !important;
    box-shadow: 0 0 0 3px rgba(33,118,174,0.15) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.04em !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--sky) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}

/* ── Status badges ── */
.badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 0.72rem;
    font-family: var(--mono); letter-spacing: 0.05em;
    font-weight: 600; text-transform: uppercase;
}
.badge.green  { background: #d1fae5; color: #065f46; }
.badge.blue   { background: #dbeafe; color: #1e40af; }
.badge.orange { background: #fef3c7; color: #92400e; }
.badge.red    { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar branding ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 4px 24px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                    letter-spacing:0.12em;color:#5a7a9e;text-transform:uppercase;
                    margin-bottom:4px;">Department of Education</div>
        <div style="font-size:1.1rem;font-weight:700;color:white;line-height:1.2;">
            IEP Intelligence<br>Platform
        </div>
        <div style="width:32px;height:2px;background:#e63946;margin-top:10px;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;
                color:#5a7a9e;text-transform:uppercase;letter-spacing:0.1em;
                padding:0 4px 8px;">Navigation</div>
    """, unsafe_allow_html=True)

# ── Home page content ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div style="position:relative;z-index:1;">
        <span class="hero-badge">DOE</span>
        <span class="hero-badge" style="background:#2176ae;">SOP v2024</span>
        <div class="hero-title">IEP Intelligence Platform</div>
        <div class="hero-sub">
            Individualized Education Program · Standard Operating Procedures
        </div>
        <div style="margin-top:16px;color:#a8c4e0;font-size:0.88rem;max-width:600px;">
            One platform for Business Analysts, QA Testers, Developers and Special Ed
            Coordinators to navigate, validate and operationalize IEP rules.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Metric row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("5", "Modules"),
    ("80+", "SOP Pages"),
    ("4", "User Roles"),
    ("60", "Day Timeline"),
    ("100%", "IDEA Aligned"),
]
for col, (num, lbl) in zip([c1,c2,c3,c4,c5], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="num">{num}</div>
            <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ── Module cards ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <h2>Platform Modules</h2>
    <span class="tag">SELECT FROM SIDEBAR</span>
</div>
""", unsafe_allow_html=True)

cols = st.columns(2)
modules = [
    ("📄", "Document Search & Q&A",
     "Upload your SOP PDFs and ask natural-language questions. Powered by RAG — find the exact rule or clause in seconds.",
     "mint", ["Business Analyst", "Developer"]),
    ("🔀", "Workflow Process Maps",
     "Visual flowcharts of the full IEP lifecycle: Referral → Evaluation → Eligibility → IEP Meeting → Placement → Annual Review.",
     "blue", ["Business Analyst", "Special Ed Coordinator"]),
    ("🌳", "Rule Engine & Decision Trees",
     "Interactive decision trees: given a student's classification and needs, what services, timelines and documents are required?",
     "gold", ["Developer", "QA Tester"]),
    ("✅", "Compliance Checklist Generator",
     "Auto-generate checklists per IEP type (Initial, Annual Review, Reevaluation, Amendment). Export to PDF or CSV.",
     "accent", ["Special Ed Coordinator", "QA Tester"]),
]
for i, (icon, title, desc, color, roles) in enumerate(modules):
    with cols[i % 2]:
        role_badges = "".join(
            f'<span class="badge blue" style="margin-right:4px;">{r}</span>' for r in roles
        )
        st.markdown(f"""
        <div class="iep-card {color}">
            <div style="font-size:1.6rem;margin-bottom:10px;">{icon}</div>
            <div style="font-weight:700;color:#0d1b2a;font-size:1rem;margin-bottom:8px;">{title}</div>
            <div style="color:#4a6080;font-size:0.88rem;line-height:1.6;margin-bottom:14px;">{desc}</div>
            <div>{role_badges}</div>
        </div>""", unsafe_allow_html=True)

# ── Quick-start ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <h2>Quick Start</h2>
    <span class="tag">GETTING STARTED</span>
</div>
""", unsafe_allow_html=True)

q1, q2, q3 = st.columns(3)
steps = [
    ("01", "Upload your SOP PDFs", "Go to Document Search → Upload PDF. The platform indexes all 80+ pages automatically."),
    ("02", "Explore the workflow", "Use Process Maps to walk through the IEP timeline visually, role by role."),
    ("03", "Generate test cases", "Use the Rule Engine to produce Given/When/Then test scenarios for your QA suite."),
]
for col, (num, title, desc) in zip([q1,q2,q3], steps):
    with col:
        st.markdown(f"""
        <div class="iep-card" style="border-top-color:#06d6a0;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:2rem;
                        font-weight:700;color:#e2e8f0;margin-bottom:8px;">{num}</div>
            <div style="font-weight:600;color:#0d1b2a;margin-bottom:8px;">{title}</div>
            <div style="color:#4a6080;font-size:0.85rem;line-height:1.6;">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#94a3b8;font-size:0.75rem;
            font-family:'IBM Plex Mono',monospace;letter-spacing:0.05em;padding:8px 0;">
DOE · IEP Intelligence Platform · Built on public SOP documents · IDEA-aligned
</div>""", unsafe_allow_html=True)
