"""
Page: IEP Workflow Process Maps
Visual timelines and flowcharts for the full IEP lifecycle.
"""

import streamlit as st
import json

st.markdown("## 🔀 IEP Workflow Process Maps")
st.markdown(
    '<p style="color:#4a6080;margin-top:-10px;margin-bottom:24px;">'
    'Interactive flowcharts for every stage of the IEP lifecycle. '
    'Click any step to see requirements, timelines and responsible parties.</p>',
    unsafe_allow_html=True,
)

# ── Workflow data ─────────────────────────────────────────────────────────────
WORKFLOWS = {
    "Initial IEP": {
        "description": "From referral to first IEP placement. IDEA mandates 60 school days.",
        "color": "#2176ae",
        "steps": [
            {"id": 1, "name": "Referral", "days": "Day 0",
             "owner": "Parent / Teacher / CSE",
             "desc": "Written referral submitted to Committee on Special Education (CSE). Can be initiated by parent, teacher, or school. Triggers the 60-school-day clock.",
             "docs": ["Written referral letter", "Referral form (CSE-1)"],
             "tests": [
                "Verify referral is in writing",
                "Confirm date stamp starts 60-day clock",
                "Check that parent notification is sent within 5 days",
             ]},
            {"id": 2, "name": "Consent for Evaluation", "days": "Day 1–10",
             "owner": "Parent / CSE",
             "desc": "School must notify parent and obtain written consent before conducting an initial evaluation. Consent is specific to this evaluation only.",
             "docs": ["Prior Written Notice (PWN)", "Parent consent form"],
             "tests": [
                "Verify PWN includes all required elements",
                "Confirm consent is signed before evaluation begins",
                "Check consent is not treated as consent for placement",
             ]},
            {"id": 3, "name": "Evaluation", "days": "Day 10–40",
             "owner": "Multi-Disciplinary Team",
             "desc": "Comprehensive evaluation across all suspected areas of disability. Must include psychological, educational, and any other relevant assessments. Parent has right to IEE if they disagree.",
             "docs": ["Psychoeducational report", "Speech/Language eval", "OT/PT eval (if applicable)", "Social history"],
             "tests": [
                "All domains of suspected disability evaluated",
                "Evaluation completed within 60-day window",
                "Qualified evaluators used for each domain",
             ]},
            {"id": 4, "name": "Eligibility Determination", "days": "Day 40–50",
             "owner": "CSE",
             "desc": "CSE meets to review evaluation data and determine if student meets eligibility criteria for one of 13 disability categories under IDEA. Parent is a required member.",
             "docs": ["Eligibility summary", "Classification determination"],
             "tests": [
                "Student meets criteria for at least one of 13 categories",
                "CSE minutes document parent participation",
                "Determination made by full CSE team",
             ]},
            {"id": 5, "name": "IEP Development", "days": "Day 50–58",
             "owner": "IEP Team",
             "desc": "Develop the IEP document including present levels, annual goals, special education services, related services, accommodations, and placement recommendation.",
             "docs": ["IEP document", "Present Levels of Performance", "Annual goals", "Service grid"],
             "tests": [
                "Present levels based on current evaluation data",
                "Goals are measurable and linked to present levels",
                "Service hours, frequency and location specified",
                "LRE determination documented",
             ]},
            {"id": 6, "name": "Placement & Implementation", "days": "Day 60",
             "owner": "Principal / CSE",
             "desc": "Parent receives a copy of the IEP and Prior Written Notice of placement. Services must begin as soon as possible. IEP must be in effect at the start of each school year.",
             "docs": ["Final IEP copy to parent", "Prior Written Notice of placement", "Parent rights notice"],
             "tests": [
                "IEP implemented within 60 school days of referral",
                "Parent receives copy of IEP",
                "All service providers have access to IEP goals",
             ]},
        ]
    },
    "Annual Review": {
        "description": "IEP must be reviewed at least once per year to assess progress and update goals.",
        "color": "#06d6a0",
        "steps": [
            {"id": 1, "name": "Progress Review", "days": "30 days before",
             "owner": "Special Ed Teacher",
             "desc": "Review progress on current annual goals. Collect data on all measurable goals. Determine if goals were met.",
             "docs": ["Progress reports", "Data collection sheets"],
             "tests": ["Progress data collected for all goals", "Parent notified of upcoming review"]},
            {"id": 2, "name": "Schedule Meeting", "days": "14 days before",
             "owner": "CSE Chairperson",
             "desc": "Send written notice to all required team members. Must include parent. Notice must be early enough for parent to attend.",
             "docs": ["Meeting notice", "Parent invitation"],
             "tests": ["Written notice sent ≥ 14 days before meeting", "Parent notified of rights"]},
            {"id": 3, "name": "Annual Review Meeting", "days": "On or before anniversary",
             "owner": "IEP Team",
             "desc": "Team reviews current IEP, progress on goals, evaluates continued eligibility, and develops new IEP for next year.",
             "docs": ["Updated IEP", "Meeting minutes", "New service grid"],
             "tests": ["Meeting held on/before anniversary date", "All team members present or excused in writing",
                       "New measurable annual goals written"]},
            {"id": 4, "name": "New IEP Implementation", "days": "Day of meeting",
             "owner": "Principal / Teachers",
             "desc": "New IEP goes into effect. All service providers must be notified and have access to the updated document.",
             "docs": ["IEP distribution log"],
             "tests": ["New IEP sent to all service providers", "Parent receives copy same day"]},
        ]
    },
    "Reevaluation": {
        "description": "Required at least every 3 years (triennial) OR when requested by parent/school.",
        "color": "#f4a261",
        "steps": [
            {"id": 1, "name": "Determine Reevaluation Need", "days": "3-year mark",
             "owner": "CSE",
             "desc": "CSE must reevaluate at least every 3 years or if a parent or teacher requests one. Purpose: determine if student still has a disability and their educational needs.",
             "docs": ["Reevaluation notice"],
             "tests": ["Reevaluation conducted within 3 years of last evaluation", "Parent notified of right to request reevaluation"]},
            {"id": 2, "name": "Review Existing Data", "days": "Days 1–15",
             "owner": "CSE Team",
             "desc": "Before conducting new assessments, CSE reviews all existing data including previous evaluations, classroom observations, and parent input to determine what additional data is needed.",
             "docs": ["Existing data review summary", "Parent questionnaire"],
             "tests": ["All existing data sources reviewed", "Parent input solicited in writing"]},
            {"id": 3, "name": "Consent (if new testing)", "days": "Days 15–25",
             "owner": "Parent",
             "desc": "If new assessments are needed, written parental consent must be obtained. If only reviewing existing data, consent is not required but parent must be notified.",
             "docs": ["Consent for reevaluation form"],
             "tests": ["Consent obtained before new assessments", "Parents informed even when consent not required"]},
            {"id": 4, "name": "Conduct Assessments", "days": "Days 25–50",
             "owner": "Evaluators",
             "desc": "Administer only assessments identified as necessary in the data review. Must cover all areas of the student's disability.",
             "docs": ["Updated evaluation reports"],
             "tests": ["Only necessary assessments conducted", "Results compared to baseline data"]},
            {"id": 5, "name": "CSE Eligibility Meeting", "days": "Days 50–60",
             "owner": "CSE",
             "desc": "Review reevaluation results. Determine if student still has a disability. If eligible, update IEP. If no longer eligible, document de-classification.",
             "docs": ["Updated eligibility determination", "Revised IEP or de-classification notice"],
             "tests": ["Eligibility re-determined using current data", "De-classification includes 1-year transition services if applicable"]},
        ]
    },
    "Amendment": {
        "description": "Changes to an IEP between annual reviews without a full IEP meeting.",
        "color": "#e63946",
        "steps": [
            {"id": 1, "name": "Identify Amendment Need", "days": "As needed",
             "owner": "Parent / CSE",
             "desc": "Either parent or school identifies a needed change to the IEP. Amendments can be made with or without a meeting if parent agrees in writing.",
             "docs": ["Amendment request"],
             "tests": ["Amendment need is documented", "Amendment does not require an annual review"]},
            {"id": 2, "name": "Parent Agreement", "days": "Days 1–5",
             "owner": "Parent",
             "desc": "Parent must be informed of the proposed amendment and agree in writing. A meeting can be waived only with explicit written parent agreement.",
             "docs": ["Written agreement to waive meeting"],
             "tests": ["Parent agreement is in writing", "Parent rights notice provided with amendment"]},
            {"id": 3, "name": "Document Amendment", "days": "Days 5–10",
             "owner": "CSE",
             "desc": "The IEP is amended in writing. All service providers must be notified of the change. Parent receives a copy of the amended IEP page(s).",
             "docs": ["IEP amendment pages", "Distribution log"],
             "tests": ["Amendment is specific and dated", "All affected providers notified", "Parent receives amended pages"]},
        ]
    }
}

# ── Controls ──────────────────────────────────────────────────────────────────
col_sel, col_view = st.columns([2, 1])
with col_sel:
    selected_wf = st.selectbox("Select IEP Process", list(WORKFLOWS.keys()))
with col_view:
    view_mode = st.radio("View", ["Flow", "Table", "Test Cases"], horizontal=True)

wf = WORKFLOWS[selected_wf]
color = wf["color"]

st.markdown(f"""
<div style="background:{color}18;border-left:3px solid {color};border-radius:6px;
            padding:12px 16px;margin:8px 0 24px;color:#374151;font-size:0.9rem;">
    <b>{selected_wf}</b> — {wf['description']}
</div>""", unsafe_allow_html=True)

# ── FLOW VIEW ─────────────────────────────────────────────────────────────────
if view_mode == "Flow":
    for i, step in enumerate(wf["steps"]):
        cols = st.columns([1, 11])
        with cols[0]:
            st.markdown(f"""
            <div style="width:40px;height:40px;border-radius:50%;
                        background:{color};color:white;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:700;font-size:0.9rem;margin-top:8px;">
                {step['id']}
            </div>""", unsafe_allow_html=True)
            if i < len(wf["steps"]) - 1:
                st.markdown(f"""
                <div style="width:2px;height:32px;background:{color}40;
                            margin:4px auto;"></div>""", unsafe_allow_html=True)

        with cols[1]:
            with st.expander(
                f"**{step['name']}**  ·  `{step['days']}`  ·  {step['owner']}",
                expanded=(i == 0)
            ):
                st.markdown(f"**Description:** {step['desc']}")

                d_col, _ = st.columns([1, 1])
                with d_col:
                    st.markdown("**Required Documents:**")
                    for doc in step["docs"]:
                        st.markdown(f"- 📄 {doc}")

                st.markdown("**QA Test Scenarios:**")
                for t in step["tests"]:
                    st.markdown(
                        f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;'
                        f'border-radius:4px;padding:4px 10px;font-size:0.83rem;'
                        f'color:#065f46;display:inline-block;margin:2px 0;">'
                        f'✓ {t}</span>',
                        unsafe_allow_html=True,
                    )

# ── TABLE VIEW ────────────────────────────────────────────────────────────────
elif view_mode == "Table":
    import pandas as pd
    rows = []
    for step in wf["steps"]:
        rows.append({
            "Step": step["id"],
            "Phase": step["name"],
            "Timeline": step["days"],
            "Responsible Party": step["owner"],
            "Key Documents": ", ".join(step["docs"]),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── TEST CASES VIEW ───────────────────────────────────────────────────────────
else:
    st.markdown("### 🧪 Generated Test Cases")
    st.markdown(
        '<p style="color:#4a6080;margin-bottom:20px;">Copy these into your test management system (Jira, TestRail, Azure DevOps).</p>',
        unsafe_allow_html=True,
    )
    tc_count = 0
    for step in wf["steps"]:
        st.markdown(f"**{step['name']}** · `{step['days']}`")
        for t in step["tests"]:
            tc_count += 1
            st.code(
                f"TC-{tc_count:03d}: {selected_wf.upper()} - {step['name']}\n"
                f"Given: Student is in the {step['name']} phase of {selected_wf}\n"
                f"When: The CSE processes the request\n"
                f"Then: {t}",
                language="gherkin",
            )

    if st.button("📋 Export All Test Cases"):
        all_tests = []
        tc = 0
        for step in wf["steps"]:
            for t in step["tests"]:
                tc += 1
                all_tests.append({
                    "id": f"TC-{tc:03d}",
                    "process": selected_wf,
                    "phase": step["name"],
                    "timeline": step["days"],
                    "owner": step["owner"],
                    "test": t,
                })
        import pandas as pd
        df = pd.DataFrame(all_tests)
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            csv,
            file_name=f"IEP_{selected_wf.replace(' ','_')}_TestCases.csv",
            mime="text/csv",
        )
