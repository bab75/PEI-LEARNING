"""
Page: Compliance Checklist Generator
Generate, track and export IEP compliance checklists by type and role.
"""

import streamlit as st
import pandas as pd
import json
from datetime import date, datetime

st.markdown("## ✅ Compliance Checklist Generator")
st.markdown(
    '<p style="color:#4a6080;margin-top:-10px;margin-bottom:24px;">'
    'Generate role-specific compliance checklists for any IEP type. '
    'Track completion and export to CSV or JSON.</p>',
    unsafe_allow_html=True,
)

# ── Checklist definitions ─────────────────────────────────────────────────────
CHECKLISTS = {
    "Initial IEP": {
        "CSE Chairperson": [
            ("Prior Written Notice (PWN) sent to parent before meeting", "R-005", "Critical"),
            ("Written parental consent obtained for evaluation", "R-004", "Critical"),
            ("Meeting notice sent ≥ 14 days in advance", "R-002", "Required"),
            ("All required team members notified or excused in writing", "IDEA §300.321", "Required"),
            ("Parent rights notice (Procedural Safeguards) provided", "IDEA §300.504", "Critical"),
            ("Student invited to meeting if transition age (15+)", "IDEA §300.321(b)", "Required"),
            ("Evaluation results shared with parent before meeting", "Best Practice", "Recommended"),
        ],
        "School Psychologist": [
            ("Psychoeducational evaluation completed within 60 school days", "R-001", "Critical"),
            ("All areas of suspected disability assessed", "IDEA §300.304", "Critical"),
            ("Assessment tools are valid and non-discriminatory", "IDEA §300.304(c)", "Critical"),
            ("More than one assessment tool used", "IDEA §300.304(b)", "Required"),
            ("Report includes eligibility recommendation", "Best Practice", "Required"),
            ("Report shared with parent at least 1 day before meeting", "Best Practice", "Recommended"),
        ],
        "Special Education Teacher": [
            ("Educational assessment completed", "IDEA §300.304", "Critical"),
            ("Present levels of academic achievement documented", "IDEA §300.320(a)(1)", "Critical"),
            ("Annual goals are measurable and address areas of need", "IDEA §300.320(a)(2)", "Critical"),
            ("Goals linked directly to present levels", "Best Practice", "Required"),
            ("Service delivery grid completed (frequency, duration, location)", "IDEA §300.320(a)(4)", "Critical"),
            ("Accommodations and modifications listed", "IDEA §300.320(a)(4)", "Required"),
            ("Participation in state/district assessments addressed", "IDEA §300.320(a)(6)", "Required"),
        ],
        "Parent / Guardian": [
            ("Received Prior Written Notice", "R-005", "Critical"),
            ("Received and reviewed Procedural Safeguards", "IDEA §300.504", "Critical"),
            ("Provided written consent for initial evaluation", "R-004", "Critical"),
            ("Provided input on student strengths and needs", "IDEA §300.321(a)(1)", "Required"),
            ("Received copy of IEP at meeting or within reasonable time", "IDEA §300.322", "Critical"),
            ("Received Prior Written Notice of placement decision", "R-005", "Critical"),
        ],
    },
    "Annual Review": {
        "CSE Chairperson": [
            ("Meeting scheduled on or before IEP anniversary date", "R-002", "Critical"),
            ("Meeting notice sent ≥ 14 days in advance", "IDEA §300.322", "Required"),
            ("Prior Written Notice sent if any changes proposed", "R-005", "Required"),
            ("All required IEP team members present or excused", "IDEA §300.321", "Required"),
            ("Parent received Procedural Safeguards (if changed)", "IDEA §300.504", "Required"),
        ],
        "Special Education Teacher": [
            ("Progress on all annual goals reviewed and documented", "IDEA §300.324(b)", "Critical"),
            ("New measurable annual goals written", "IDEA §300.320(a)(2)", "Critical"),
            ("Present levels updated to reflect current performance", "IDEA §300.320(a)(1)", "Critical"),
            ("Services reviewed and adjusted as appropriate", "IDEA §300.324(b)(1)", "Required"),
            ("Accommodations reviewed and updated", "IDEA §300.320(a)(4)", "Required"),
            ("ESY eligibility reviewed and documented", "IDEA §300.106", "Required"),
        ],
        "Parent / Guardian": [
            ("Participated in annual review meeting", "IDEA §300.322", "Required"),
            ("Received updated IEP copy", "IDEA §300.322(f)", "Critical"),
            ("Informed of right to request additional evaluation", "IDEA §300.305", "Required"),
        ],
    },
    "Reevaluation": {
        "CSE Chairperson": [
            ("Reevaluation conducted within 3 years of last evaluation", "IDEA §300.303", "Critical"),
            ("Existing data review meeting held", "IDEA §300.305(a)", "Required"),
            ("Parent notified of reevaluation and purpose", "IDEA §300.304", "Required"),
            ("Written consent obtained if new assessments needed", "IDEA §300.300(c)", "Critical"),
            ("Parent informed even if consent not required", "Best Practice", "Recommended"),
        ],
        "School Psychologist": [
            ("Existing evaluation data reviewed", "IDEA §300.305(a)", "Critical"),
            ("Determination made of what new assessments are needed", "IDEA §300.305(b)", "Required"),
            ("New assessments completed if needed", "IDEA §300.304", "Required"),
            ("Continued eligibility determination documented", "IDEA §300.305(e)", "Critical"),
            ("De-classification notice provided if student no longer eligible", "IDEA §300.305(e)(2)", "Critical"),
        ],
    },
    "Amendment": {
        "CSE Chairperson": [
            ("Amendment need clearly documented", "Best Practice", "Required"),
            ("Written parent agreement to waive meeting obtained (if applicable)", "IDEA §300.324(a)(4)", "Critical"),
            ("Prior Written Notice of amendment provided", "R-005", "Critical"),
            ("All service providers notified of changes", "Best Practice", "Required"),
        ],
        "Special Education Teacher": [
            ("Specific IEP pages amended and dated", "Best Practice", "Required"),
            ("Amendment does not contradict Annual Review determinations", "Best Practice", "Required"),
            ("Goals and services remain aligned after amendment", "Best Practice", "Recommended"),
        ],
        "Parent / Guardian": [
            ("Received written notice of proposed amendment", "R-005", "Critical"),
            ("Provided written agreement (if meeting waived)", "IDEA §300.324(a)(4)", "Critical"),
            ("Received copy of amended IEP pages", "Best Practice", "Required"),
        ],
    },
}

# ── Session state for checklist completion tracking ───────────────────────────
if "checklist_state" not in st.session_state:
    st.session_state.checklist_state = {}

# ── Controls ──────────────────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns([2, 2, 1])
with col_a:
    iep_type = st.selectbox("IEP Process Type", list(CHECKLISTS.keys()))
with col_b:
    available_roles = list(CHECKLISTS[iep_type].keys())
    role = st.selectbox("Your Role", available_roles)
with col_c:
    filter_priority = st.selectbox("Filter", ["All", "Critical", "Required", "Recommended"])

# ── Student / case info ───────────────────────────────────────────────────────
with st.expander("📌 Case Information (optional — for export)", expanded=False):
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        student_id   = st.text_input("Student ID / OSIS #")
        student_name = st.text_input("Student Name")
    with ci2:
        school_name = st.text_input("School Name")
        cse_date    = st.date_input("CSE Meeting Date", date.today())
    with ci3:
        reviewer    = st.text_input("Completed By")
        notes       = st.text_area("Notes", height=80)

# ── Checklist key for state ───────────────────────────────────────────────────
ck_key = f"{iep_type}_{role}"
items = CHECKLISTS[iep_type][role]

if ck_key not in st.session_state.checklist_state:
    st.session_state.checklist_state[ck_key] = {i: False for i in range(len(items))}

# ── Filter ────────────────────────────────────────────────────────────────────
filtered_items = [
    (idx, item) for idx, item in enumerate(items)
    if filter_priority == "All" or item[2] == filter_priority
]

# ── Progress bar ─────────────────────────────────────────────────────────────
completed = sum(1 for i in range(len(items)) if st.session_state.checklist_state[ck_key].get(i, False))
total     = len(items)
pct       = int(completed / total * 100) if total else 0

color_map = {"Critical": "#e63946", "Required": "#2176ae", "Recommended": "#06d6a0"}

st.markdown(f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:16px 0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-weight:600;color:#0d1b2a;">{iep_type} — {role}</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.85rem;color:#2176ae;font-weight:600;">
            {completed}/{total} complete · {pct}%
        </span>
    </div>
    <div style="background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden;">
        <div style="background:{'#06d6a0' if pct==100 else '#2176ae' if pct>=50 else '#e63946'};
                    height:100%;width:{pct}%;border-radius:4px;transition:width 0.3s;"></div>
    </div>
</div>""", unsafe_allow_html=True)

# ── Checklist items ───────────────────────────────────────────────────────────
st.markdown("### Checklist Items")

for idx, (task, rule_ref, priority) in filtered_items:
    col_cb, col_task = st.columns([1, 11])
    with col_cb:
        checked = st.checkbox(
            "", 
            value=st.session_state.checklist_state[ck_key].get(idx, False),
            key=f"chk_{ck_key}_{idx}",
        )
        st.session_state.checklist_state[ck_key][idx] = checked

    with col_task:
        color = color_map.get(priority, "#888")
        task_style = "text-decoration:line-through;color:#94a3b8;" if checked else "color:#1e293b;"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0;">
            <div style="{task_style}font-size:0.9rem;flex:1;">{task}</div>
            <span style="background:{color}22;color:{color};border-radius:4px;
                         font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                         padding:2px 8px;white-space:nowrap;font-weight:600;">{priority}</span>
            <span style="color:#94a3b8;font-family:'IBM Plex Mono',monospace;
                         font-size:0.7rem;white-space:nowrap;">{rule_ref}</span>
        </div>""", unsafe_allow_html=True)

# ── Action row ────────────────────────────────────────────────────────────────
st.markdown("---")
btn1, btn2, btn3, btn4 = st.columns(4)

with btn1:
    if st.button("✅ Mark All Complete", use_container_width=True):
        for i in range(len(items)):
            st.session_state.checklist_state[ck_key][i] = True
        st.rerun()

with btn2:
    if st.button("⬜ Clear All", use_container_width=True):
        for i in range(len(items)):
            st.session_state.checklist_state[ck_key][i] = False
        st.rerun()

with btn3:
    # CSV export
    rows = []
    for idx, (task, rule_ref, priority) in enumerate(items):
        rows.append({
            "Student ID": student_id,
            "Student Name": student_name,
            "School": school_name,
            "CSE Date": str(cse_date),
            "IEP Type": iep_type,
            "Role": role,
            "Task": task,
            "Rule Reference": rule_ref,
            "Priority": priority,
            "Complete": "Yes" if st.session_state.checklist_state[ck_key].get(idx, False) else "No",
            "Completed By": reviewer,
            "Notes": notes,
        })
    df = pd.DataFrame(rows)
    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️ Export CSV",
        csv,
        file_name=f"IEP_Checklist_{iep_type.replace(' ','_')}_{role.replace(' ','_')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with btn4:
    # JSON export
    export = {
        "generated_at": datetime.now().isoformat(),
        "case_info": {
            "student_id": student_id, "student_name": student_name,
            "school": school_name, "cse_date": str(cse_date),
            "completed_by": reviewer, "notes": notes,
        },
        "checklist": {
            "iep_type": iep_type, "role": role,
            "completion": f"{completed}/{total}",
            "items": [
                {"task": task, "rule": rule_ref, "priority": priority,
                 "complete": st.session_state.checklist_state[ck_key].get(idx, False)}
                for idx, (task, rule_ref, priority) in enumerate(items)
            ],
        },
    }
    st.download_button(
        "⬇️ Export JSON",
        json.dumps(export, indent=2),
        file_name=f"IEP_Checklist_{iep_type.replace(' ','_')}.json",
        mime="application/json",
        use_container_width=True,
    )

# ── Summary for all roles ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### All Roles Summary")
summary_rows = []
for r in available_roles:
    rk = f"{iep_type}_{r}"
    r_items = CHECKLISTS[iep_type][r]
    if rk not in st.session_state.checklist_state:
        st.session_state.checklist_state[rk] = {i: False for i in range(len(r_items))}
    r_done = sum(1 for i in range(len(r_items)) if st.session_state.checklist_state[rk].get(i, False))
    r_crit = sum(1 for _, _, p in r_items if p == "Critical")
    r_crit_done = sum(1 for i, (_, _, p) in enumerate(r_items) if p == "Critical" and st.session_state.checklist_state[rk].get(i, False))
    summary_rows.append({
        "Role": r,
        "Completed": f"{r_done}/{len(r_items)}",
        "% Done": f"{int(r_done/len(r_items)*100)}%",
        "Critical Done": f"{r_crit_done}/{r_crit}",
        "Status": "✅ Complete" if r_done == len(r_items) else ("⚠️ In Progress" if r_done > 0 else "⬜ Not Started"),
    })

df_summary = pd.DataFrame(summary_rows)
st.dataframe(df_summary, use_container_width=True, hide_index=True)
