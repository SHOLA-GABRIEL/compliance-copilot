import streamlit as st
import json
import time
from pathlib import Path
from analyzer import ComplianceAnalyzer
from utils import extract_text_from_pdf, chunk_text

st.set_page_config(
    page_title="Compliance Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1626;
    border-right: 1px solid #1e2d4a;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #94a3b8;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Header */
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}

.hero-sub {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* Framework badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin: 2px;
}
.badge-nist   { background: #1e3a5f; color: #60a5fa; border: 1px solid #2563eb44; }
.badge-iso    { background: #1a3a2a; color: #34d399; border: 1px solid #10b98144; }
.badge-soc2   { background: #2d1a3a; color: #a78bfa; border: 1px solid #7c3aed44; }
.badge-gdpr   { background: #3a2a1a; color: #fbbf24; border: 1px solid #f59e0b44; }
.badge-hipaa  { background: #3a1a1a; color: #f87171; border: 1px solid #ef444444; }

/* Cards */
.gap-card {
    background: #0f1626;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.gap-card:hover { border-color: #2d4a7a; }

.gap-critical { border-left: 3px solid #ef4444; }
.gap-high     { border-left: 3px solid #f97316; }
.gap-medium   { border-left: 3px solid #eab308; }
.gap-low      { border-left: 3px solid #22c55e; }

.gap-title {
    font-weight: 600;
    font-size: 0.95rem;
    color: #e2e8f0;
    margin-bottom: 0.35rem;
}
.gap-detail {
    font-size: 0.82rem;
    color: #64748b;
    line-height: 1.5;
}

.control-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: #1e2d4a;
    color: #60a5fa;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 6px;
}

/* Metric tiles */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-tile {
    background: #0f1626;
    border: 1px solid #1e2d4a;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-number {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.metric-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Score gauge */
.score-ring {
    text-align: center;
    padding: 1.5rem;
}

/* Upload zone */
.upload-zone {
    border: 2px dashed #1e2d4a;
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    transition: all 0.3s;
    background: #0a0e1a;
}
.upload-zone:hover { border-color: #2563eb; background: #0d1220; }

/* Progress */
.progress-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.6rem 0;
    color: #94a3b8;
    font-size: 0.85rem;
}
.step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #1e2d4a;
    flex-shrink: 0;
}
.step-dot.active  { background: #60a5fa; box-shadow: 0 0 8px #60a5fa66; }
.step-dot.done    { background: #34d399; }

/* Recommendation box */
.rec-box {
    background: #0a1628;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-top: 0.5rem;
    font-size: 0.83rem;
    color: #94a3b8;
    line-height: 1.6;
}

/* Table */
.coverage-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.83rem;
}
.coverage-table th {
    text-align: left;
    padding: 0.6rem 1rem;
    color: #64748b;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid #1e2d4a;
}
.coverage-table td {
    padding: 0.7rem 1rem;
    border-bottom: 1px solid #0f1626;
    color: #cbd5e1;
}

.pill-covered   { background:#1a3a2a; color:#34d399; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.pill-partial   { background:#3a2a1a; color:#fbbf24; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.pill-missing   { background:#3a1a1a; color:#f87171; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; }

/* Stlite hides button borders — fix */
.stButton > button {
    background: #1e2d4a !important;
    color: #e2e8f0 !important;
    border: 1px solid #2d4a7a !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #2d4a7a !important;
    border-color: #60a5fa !important;
}

/* Selectbox */
div[data-baseweb="select"] {
    background: #0f1626 !important;
}

/* Dividers */
hr { border-color: #1e2d4a !important; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Compliance Copilot")
    st.markdown("---")

    st.markdown("**FRAMEWORKS**")
    frameworks = st.multiselect(
        "Map against",
        ["NIST CSF 2.0", "ISO 27001:2022", "SOC 2 Type II", "GDPR", "HIPAA"],
        default=["NIST CSF 2.0", "ISO 27001:2022"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**ANALYSIS DEPTH**")
    depth = st.select_slider(
        "Depth",
        options=["Quick Scan", "Standard", "Deep Dive"],
        value="Standard",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**ABOUT**")
    st.caption("Upload a security or privacy policy PDF. The AI maps it to industry frameworks and surfaces compliance gaps with remediation guidance.")
    st.caption("v1.0 · Built with LangChain + Claude")


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">Compliance Copilot</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">AI-powered gap analysis against NIST, ISO 27001, SOC 2 & more</p>', unsafe_allow_html=True)

# Framework badges
badge_map = {
    "NIST CSF 2.0":    "nist",
    "ISO 27001:2022":  "iso",
    "SOC 2 Type II":   "soc2",
    "GDPR":            "gdpr",
    "HIPAA":           "hipaa",
}
badges_html = " ".join(
    f'<span class="badge badge-{badge_map[f]}">{f}</span>'
    for f in frameworks
)
st.markdown(badges_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── File Upload ───────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop your policy PDF here",
    type=["pdf"],
    label_visibility="collapsed",
)

if uploaded is None:
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size:2.5rem; margin-bottom:0.75rem">📄</div>
        <div style="color:#94a3b8; font-size:1rem; font-weight:500; margin-bottom:0.35rem">
            Drop your policy PDF
        </div>
        <div style="color:#475569; font-size:0.82rem">
            Information Security Policy · Privacy Policy · ISMS Documentation · DR/BCP Plans
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Analysis Flow ─────────────────────────────────────────────────────────────
if "results" not in st.session_state or st.session_state.get("last_file") != uploaded.name:
    col_prog, col_space = st.columns([1, 2])
    with col_prog:
        st.markdown("#### Analyzing policy…")
        steps = [
            "Extracting text from PDF",
            "Chunking & preprocessing",
            f"Mapping to {', '.join(frameworks)}",
            "Identifying coverage gaps",
            "Generating remediation plan",
        ]
        dots = []
        placeholders = []
        for s in steps:
            row = st.empty()
            dots.append(row)
            placeholders.append(s)

        def render_steps(active_idx):
            for i, (d, s) in enumerate(zip(dots, placeholders)):
                status = "done" if i < active_idx else ("active" if i == active_idx else "")
                icon = "✓" if i < active_idx else ("→" if i == active_idx else "·")
                color = "#34d399" if i < active_idx else ("#60a5fa" if i == active_idx else "#475569")
                d.markdown(
                    f'<div class="progress-step">'
                    f'<span style="color:{color}; font-size:0.9rem">{icon}</span>'
                    f'<span style="color:{"#e2e8f0" if i <= active_idx else "#475569"}">{s}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        render_steps(0)
        time.sleep(0.3)

        # Step 1 – extract text
        render_steps(1)
        pdf_bytes = uploaded.read()
        text = extract_text_from_pdf(pdf_bytes)
        time.sleep(0.2)

        # Step 2 – chunk
        render_steps(2)
        chunks = chunk_text(text)
        time.sleep(0.3)

        # Step 3–5 – AI analysis
        render_steps(3)
        analyzer = ComplianceAnalyzer()
        with st.spinner(""):
            results = analyzer.analyze(text[:12000], frameworks, depth)
        render_steps(4)
        time.sleep(0.3)
        render_steps(5)

        st.session_state.results = results
        st.session_state.last_file = uploaded.name
        time.sleep(0.5)

    st.rerun()

results = st.session_state.results

# ── Score & Metrics ───────────────────────────────────────────────────────────
score        = results.get("overall_score", 62)
total_ctrl   = results.get("total_controls", 0)
covered      = results.get("covered", 0)
partial      = results.get("partial", 0)
gaps         = results.get("gaps", [])
critical_ct  = sum(1 for g in gaps if g.get("severity") == "Critical")
high_ct      = sum(1 for g in gaps if g.get("severity") == "High")

score_color = "#ef4444" if score < 40 else "#f97316" if score < 60 else "#eab308" if score < 75 else "#22c55e"

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown(f"""
    <div style="background:#0f1626; border:1px solid #1e2d4a; border-radius:14px; padding:1.5rem; text-align:center;">
        <div style="font-size:0.72rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.75rem">
            Compliance Score
        </div>
        <div style="font-size:3.5rem; font-weight:700; color:{score_color}; line-height:1">{score}</div>
        <div style="font-size:1rem; color:#475569; margin-bottom:1rem">/ 100</div>
        <div style="height:6px; background:#1e2d4a; border-radius:3px; overflow:hidden;">
            <div style="height:100%; width:{score}%; background:{score_color}; border-radius:3px; transition:width 1s;"></div>
        </div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:0.75rem">
            {"🔴 Critical Risk" if score < 40 else "🟠 High Risk" if score < 60 else "🟡 Moderate" if score < 75 else "🟢 Good Standing"}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Controls Mapped",  str(total_ctrl))
    c2.metric("Covered",          str(covered),      delta=None)
    c3.metric("Critical Gaps",    str(critical_ct),  delta=f"+{critical_ct}" if critical_ct else None, delta_color="inverse")
    c4.metric("High Gaps",        str(high_ct),      delta=f"+{high_ct}" if high_ct else None, delta_color="inverse")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎯  Gap Analysis", "📊  Coverage Matrix", "📋  Remediation Plan"])

# ── Tab 1: Gap Analysis ───────────────────────────────────────────────────────
with tab1:
    if not gaps:
        st.success("No significant gaps detected across the selected frameworks.")
    else:
        sev_filter = st.segmented_control(
            "Filter by severity",
            ["All", "Critical", "High", "Medium", "Low"],
            default="All",
        )

        filtered = gaps if sev_filter == "All" else [g for g in gaps if g.get("severity") == sev_filter]

        if not filtered:
            st.info(f"No {sev_filter.lower()} severity gaps found.")
        else:
            for gap in filtered:
                sev  = gap.get("severity", "Medium")
                sev_class = sev.lower()
                ctrl = gap.get("control_id", "")
                title = gap.get("title", "Unnamed Gap")
                detail = gap.get("detail", "")
                rec   = gap.get("recommendation", "")
                framework = gap.get("framework", "")

                sev_colors = {
                    "Critical": "#ef4444", "High": "#f97316",
                    "Medium": "#eab308",   "Low": "#22c55e"
                }
                sev_col = sev_colors.get(sev, "#64748b")

                st.markdown(f"""
                <div class="gap-card gap-{sev_class}">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.4rem;">
                        <span class="control-id">{ctrl}</span>
                        <span style="font-size:0.72rem; color:{sev_col}; font-weight:600;
                              background:{sev_col}22; padding:2px 10px; border-radius:20px;">
                            {sev}
                        </span>
                        <span style="font-size:0.72rem; color:#475569; margin-left:auto;">{framework}</span>
                    </div>
                    <div class="gap-title">{title}</div>
                    <div class="gap-detail">{detail}</div>
                    <div class="rec-box">
                        <strong style="color:#60a5fa; font-size:0.78rem;">💡 RECOMMENDATION</strong><br>
                        {rec}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── Tab 2: Coverage Matrix ────────────────────────────────────────────────────
with tab2:
    matrix = results.get("coverage_matrix", [])
    if not matrix:
        st.info("Coverage matrix not available.")
    else:
        rows_html = ""
        for row in matrix:
            status = row.get("status", "Missing")
            pill_class = {"Covered": "pill-covered", "Partial": "pill-partial", "Missing": "pill-missing"}.get(status, "pill-missing")
            rows_html += f"""
            <tr>
                <td><code style="font-size:0.78rem; color:#60a5fa">{row.get('control_id','')}</code></td>
                <td>{row.get('control_name','')}</td>
                <td>{row.get('framework','')}</td>
                <td><span class="{pill_class}">{status}</span></td>
                <td style="color:#64748b; font-size:0.8rem">{row.get('evidence','')}</td>
            </tr>
            """

        st.markdown(f"""
        <table class="coverage-table">
            <thead>
                <tr>
                    <th>Control ID</th>
                    <th>Control Name</th>
                    <th>Framework</th>
                    <th>Status</th>
                    <th>Evidence Found</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

# ── Tab 3: Remediation Plan ───────────────────────────────────────────────────
with tab3:
    plan = results.get("remediation_plan", [])
    if not plan:
        st.info("Remediation plan not available.")
    else:
        for i, item in enumerate(plan, 1):
            effort  = item.get("effort", "Medium")
            impact  = item.get("impact", "Medium")
            effort_colors = {"Low":"#22c55e","Medium":"#eab308","High":"#f97316"}
            impact_colors = {"Low":"#64748b","Medium":"#60a5fa","High":"#a78bfa"}

            with st.expander(f"**{i}. {item.get('action','Action')}**"):
                c1, c2, c3 = st.columns(3)
                effort_col = effort_colors.get(effort, "#fff")
impact_col = impact_colors.get(impact, "#fff")

c1.markdown(f"**Effort:** <span style='color:{effort_col}'>{effort}</span>", unsafe_allow_html=True)
c2.markdown(f"**Impact:** <span style='color:{impact_col}'>{impact}</span>", unsafe_allow_html=True)
               with tab3:
    plan = results.get("remediation_plan", [])
    if not plan:
        st.info("Remediation plan not available.")
    else:
        for i, item in enumerate(plan, 1):
            effort = item.get("effort", "Medium")
            impact = item.get("impact", "Medium")
            effort_colors = {"Low": "#22c55e", "Medium": "#eab308", "High": "#f97316"}
            impact_colors = {"Low": "#64748b", "Medium": "#60a5fa", "High": "#a78bfa"}
            effort_col = effort_colors.get(effort, "#fff")
            impact_col = impact_colors.get(impact, "#fff")

            with st.expander(f"**{i}. {item.get('action', 'Action')}**"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Effort:** <span style='color:{effort_col}'>{effort}</span>", unsafe_allow_html=True)
                c2.markdown(f"**Impact:** <span style='color:{impact_col}'>{impact}</span>", unsafe_allow_html=True)
                c3.markdown(f"**Timeline:** {item.get('timeline', 'TBD')}")
                st.markdown(item.get("detail", ""))
                if item.get("controls_addressed"):
                    st.caption("Controls addressed: " + ", ".join(item["controls_addressed"]))
                st.markdown(item.get("detail", ""))
                if item.get("controls_addressed"):
                    st.caption("Controls addressed: " + ", ".join(item["controls_addressed"]))

st.markdown("---")

# ── Export ────────────────────────────────────────────────────────────────────
col_dl1, col_dl2, col_space = st.columns([1, 1, 3])
with col_dl1:
    report_json = json.dumps(results, indent=2)
    st.download_button(
        "⬇ Download JSON Report",
        data=report_json,
        file_name=f"compliance_gap_analysis_{uploaded.name.replace('.pdf','')}.json",
        mime="application/json",
    )
with col_dl2:
    # Build simple markdown report
    md_lines = [
        f"# Compliance Gap Analysis\n",
        f"**File:** {uploaded.name}  ",
        f"**Frameworks:** {', '.join(frameworks)}  ",
        f"**Score:** {score}/100\n",
        "## Gaps\n",
    ]
    for g in gaps:
        md_lines.append(f"### [{g.get('severity')}] {g.get('title')}")
        md_lines.append(f"**Control:** {g.get('control_id')} | **Framework:** {g.get('framework')}")
        md_lines.append(f"\n{g.get('detail')}\n")
        md_lines.append(f"**Recommendation:** {g.get('recommendation')}\n")
    md_report = "\n".join(md_lines)
    st.download_button(
        "⬇ Download MD Report",
        data=md_report,
        file_name=f"compliance_gap_analysis_{uploaded.name.replace('.pdf','')}.md",
        mime="text/markdown",
    )
