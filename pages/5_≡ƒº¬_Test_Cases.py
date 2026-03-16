"""
Page: QA Test Case Generator
Auto-generate Gherkin, tabular and developer test cases from IEP business rules.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.markdown("## 🧪 QA Test Case Generator")
st.markdown(
    '<p style="color:#4a6080;margin-top:-10px;margin-bottom:24px;">'
    'Auto-generate structured test cases from IEP business rules. '
    'Export to CSV, JSON, or Gherkin format for Jira, TestRail, or Cucumber.</p>',
    unsafe_allow_html=True,
)

# ── Test case bank ────────────────────────────────────────────────────────────
TEST_BANK = {
    "Referral & Intake": [
        {
            "id": "TC-REF-001",
            "title": "Written referral required",
            "priority": "Critical",
            "rule": "IDEA §300.301",
            "given": "A parent or teacher wishes to refer a student for special education evaluation",
            "when":  "The referral is submitted to the CSE",
            "then":  "The system must require the referral to be in writing and timestamp the submission date",
            "negative": "Verbal referral is not accepted as valid initiation",
            "role":  "CSE Chairperson",
            "type":  "Functional",
        },
        {
            "id": "TC-REF-002",
            "title": "60-day clock starts on consent",
            "priority": "Critical",
            "rule": "R-001",
            "given": "A valid written referral has been received by the CSE",
            "when":  "The parent provides written consent for evaluation",
            "then":  "The 60 school-day evaluation clock must begin on the date consent is signed",
            "negative": "The clock does not start on the referral date, only on consent date",
            "role":  "CSE Chairperson",
            "type":  "Timing/Compliance",
        },
        {
            "id": "TC-REF-003",
            "title": "Parent notification within 10 days of referral",
            "priority": "Required",
            "rule": "IDEA §300.321",
            "given": "A referral has been received from a teacher",
            "when":  "The CSE processes the referral",
            "then":  "The parent must be notified of the referral within 10 school days",
            "negative": "Parent notification is not delayed pending internal review",
            "role":  "CSE Chairperson",
            "type":  "Timing/Compliance",
        },
    ],
    "Evaluation": [
        {
            "id": "TC-EVAL-001",
            "title": "All areas of suspected disability evaluated",
            "priority": "Critical",
            "rule": "IDEA §300.304(c)(4)",
            "given": "A student is referred with suspected autism and learning disabilities",
            "when":  "The evaluation team designs the assessment plan",
            "then":  "The plan must include assessments for ALL areas of suspected disability — both autism and learning disability domains",
            "negative": "Evaluating only one area when multiple are suspected is non-compliant",
            "role":  "School Psychologist",
            "type":  "Functional",
        },
        {
            "id": "TC-EVAL-002",
            "title": "Multiple evaluation tools required",
            "priority": "Critical",
            "rule": "IDEA §300.304(b)(2)",
            "given": "A school psychologist is planning an initial evaluation",
            "when":  "Assessment tools are selected",
            "then":  "A variety of assessment tools must be used — not a single test as the sole basis for eligibility",
            "negative": "Eligibility cannot be determined by a single standardized test alone",
            "role":  "School Psychologist",
            "type":  "Validation",
        },
        {
            "id": "TC-EVAL-003",
            "title": "Evaluation completed within 60 school days",
            "priority": "Critical",
            "rule": "R-001",
            "given": "Parent consent for evaluation is signed on Day 0",
            "when":  "The evaluation process concludes",
            "then":  "All evaluations must be complete and a CSE eligibility meeting scheduled by Day 60",
            "negative": "Day 61+ without an eligibility meeting is a IDEA violation",
            "role":  "CSE Chairperson",
            "type":  "Timing/Compliance",
        },
    ],
    "IEP Development": [
        {
            "id": "TC-IEP-001",
            "title": "Annual goals are measurable",
            "priority": "Critical",
            "rule": "IDEA §300.320(a)(2)",
            "given": "A special education teacher is writing annual goals for a student with reading difficulties",
            "when":  "Goals are entered into the IEP",
            "then":  "Each goal must be measurable, include a baseline, target, timeline, and method of measurement",
            "negative": "Goals that say only 'improve reading' without measurable criteria are non-compliant",
            "role":  "Special Education Teacher",
            "type":  "Data Validation",
        },
        {
            "id": "TC-IEP-002",
            "title": "Present levels link to goals",
            "priority": "Critical",
            "rule": "Best Practice / IDEA §300.320",
            "given": "The present levels of performance section documents a reading level of 2.5 grade equivalent",
            "when":  "Annual goals are written for reading",
            "then":  "Reading goals must reference the 2.5 grade equivalent baseline and target measurable growth",
            "negative": "A goal at a 4th grade level when present levels show 2nd grade is inconsistent",
            "role":  "Special Education Teacher",
            "type":  "Consistency",
        },
        {
            "id": "TC-IEP-003",
            "title": "Service delivery grid is complete",
            "priority": "Critical",
            "rule": "IDEA §300.320(a)(4)",
            "given": "The IEP team has determined a student needs speech therapy 2x per week",
            "when":  "Services are documented in the IEP",
            "then":  "The service grid must include: type of service, frequency, duration, setting, and start/end dates",
            "negative": "A service listed without frequency/duration/location is incomplete and non-compliant",
            "role":  "CSE Chairperson",
            "type":  "Data Completeness",
        },
        {
            "id": "TC-IEP-004",
            "title": "LRE documented and justified",
            "priority": "Critical",
            "rule": "R-003",
            "given": "The CSE determines a student should be placed in a 12:1:1 special class",
            "when":  "Placement is finalized",
            "then":  "The IEP must document why less restrictive options (ICT, Resource Room) were considered and rejected",
            "negative": "Placing in a 12:1:1 without documenting LRE analysis is non-compliant",
            "role":  "CSE",
            "type":  "Documentation",
        },
    ],
    "Parental Rights": [
        {
            "id": "TC-PAR-001",
            "title": "Prior Written Notice before any action",
            "priority": "Critical",
            "rule": "R-005",
            "given": "The CSE proposes to change a student's placement from ICT to a 12:1:1 special class",
            "when":  "The placement decision is finalized",
            "then":  "Prior Written Notice must be sent to the parent before the change is implemented, with rationale and parent rights",
            "negative": "Changing placement without PWN is a procedural violation",
            "role":  "CSE Chairperson",
            "type":  "Compliance",
        },
        {
            "id": "TC-PAR-002",
            "title": "Procedural Safeguards provided annually",
            "priority": "Required",
            "rule": "IDEA §300.504",
            "given": "An annual IEP review meeting is held",
            "when":  "The parent attends the meeting",
            "then":  "The parent must receive a copy of the Procedural Safeguards, and this must be documented in the meeting record",
            "negative": "Failing to provide Procedural Safeguards at the annual meeting is a documentation gap",
            "role":  "CSE Chairperson",
            "type":  "Compliance",
        },
    ],
    "Transition Planning": [
        {
            "id": "TC-TRANS-001",
            "title": "Transition goals required at age 15",
            "priority": "Critical",
            "rule": "IDEA §300.320(b)",
            "given": "A student turns 15 years old before or during the IEP year",
            "when":  "The IEP is developed or reviewed",
            "then":  "The IEP must include measurable post-secondary goals for education/training, employment, and (if applicable) independent living, plus transition services",
            "negative": "An IEP for a 15+ year old student without transition goals is non-compliant",
            "role":  "IEP Team",
            "type":  "Compliance",
        },
    ],
}

# ── Controls ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    domain_filter = st.selectbox("Domain", ["All"] + list(TEST_BANK.keys()))
with c2:
    priority_filter = st.selectbox("Priority", ["All", "Critical", "Required"])
with c3:
    type_filter = st.selectbox("Test Type", ["All", "Functional", "Compliance", "Timing/Compliance",
                                              "Data Validation", "Data Completeness", "Validation",
                                              "Consistency", "Documentation"])
with c4:
    export_format = st.selectbox("Export Format", ["Gherkin (BDD)", "CSV (TestRail)", "JSON"])

# ── Gather filtered tests ─────────────────────────────────────────────────────
all_tests = []
for domain, tests in TEST_BANK.items():
    for t in tests:
        all_tests.append({**t, "domain": domain})

filtered = [
    t for t in all_tests
    if (domain_filter   == "All" or t["domain"]    == domain_filter)
    and (priority_filter == "All" or t["priority"] == priority_filter)
    and (type_filter     == "All" or t["type"]     == type_filter)
]

# ── Summary row ───────────────────────────────────────────────────────────────
total_all  = len(all_tests)
crit_count = sum(1 for t in all_tests if t["priority"] == "Critical")
shown      = len(filtered)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
for col, (num, lbl) in zip(
    [col_m1, col_m2, col_m3, col_m4],
    [(total_all, "Total Cases"), (crit_count, "Critical"), (shown, "Filtered"), (len(TEST_BANK), "Domains")]
):
    with col:
        st.markdown(f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:12px;text-align:center;">
            <div style="font-size:1.8rem;font-weight:700;color:#2176ae;">{num}</div>
            <div style="font-size:0.72rem;color:#64748b;font-family:'IBM Plex Mono',monospace;
                        text-transform:uppercase;letter-spacing:0.06em;">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown(f"### Test Cases ({shown} shown)")

# ── Display ───────────────────────────────────────────────────────────────────
priority_colors = {"Critical": "#e63946", "Required": "#2176ae"}

for t in filtered:
    pc = priority_colors.get(t["priority"], "#888")
    with st.expander(
        f"`{t['id']}` · {t['title']} · {t['priority']} · {t['type']}",
        expanded=False
    ):
        tab_gherkin, tab_table, tab_dev = st.tabs(["Gherkin", "Structured", "Dev Notes"])

        with tab_gherkin:
            st.code(
                f"Feature: {t['domain']}\n\n"
                f"  Scenario: {t['title']}\n"
                f"    # Rule: {t['rule']}\n"
                f"    # Role: {t['role']} | Priority: {t['priority']} | Type: {t['type']}\n\n"
                f"    Given {t['given']}\n"
                f"    When  {t['when']}\n"
                f"    Then  {t['then']}\n\n"
                f"  Scenario: {t['title']} — Negative Case\n"
                f"    Given {t['given']}\n"
                f"    When  a non-compliant action is taken\n"
                f"    Then  {t['negative']}",
                language="gherkin",
            )

        with tab_table:
            st.markdown(f"""
            | Field | Value |
            |---|---|
            | **ID** | `{t['id']}` |
            | **Domain** | {t['domain']} |
            | **Priority** | {t['priority']} |
            | **Rule Reference** | {t['rule']} |
            | **Responsible Role** | {t['role']} |
            | **Type** | {t['type']} |
            | **Given** | {t['given']} |
            | **When** | {t['when']} |
            | **Then (Pass)** | {t['then']} |
            | **Then (Fail / Negative)** | {t['negative']} |
            """)

        with tab_dev:
            st.markdown(f"**API / System Check:** Verify that the backend validates: *{t['then']}*")
            st.markdown(f"**DB Assertion:** Confirm the rule `{t['rule']}` is enforced at the data layer.")
            st.markdown(f"**Regression Risk:** {'HIGH — IDEA violation if this fails' if t['priority'] == 'Critical' else 'MEDIUM — Required compliance item'}")
            st.code(
                f"# Unit test stub (Python / pytest)\n"
                f"def test_{t['id'].lower().replace('-','_')}():\n"
                f"    \"\"\"{t['title']} — {t['rule']}\"\"\"\n"
                f"    # Arrange: {t['given']}\n"
                f"    # Act:     {t['when']}\n"
                f"    # Assert:  {t['then']}\n"
                f"    raise NotImplementedError('Implement this test case')",
                language="python",
            )

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button(f"⬇️ Export {len(filtered)} Test Cases ({export_format})", use_container_width=True):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if export_format == "CSV (TestRail)":
        rows = [{
            "ID": t["id"], "Domain": t["domain"], "Title": t["title"],
            "Priority": t["priority"], "Rule": t["rule"], "Role": t["role"],
            "Type": t["type"], "Given": t["given"], "When": t["when"],
            "Then": t["then"], "Negative Case": t["negative"],
        } for t in filtered]
        csv = pd.DataFrame(rows).to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv, f"IEP_TestCases_{ts}.csv", "text/csv")

    elif export_format == "JSON":
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(filtered, indent=2),
            f"IEP_TestCases_{ts}.json",
            "application/json",
        )

    else:  # Gherkin
        lines = []
        current_domain = None
        for t in filtered:
            if t["domain"] != current_domain:
                current_domain = t["domain"]
                lines.append(f"\nFeature: {current_domain}\n")
            lines.append(
                f"  Scenario: {t['title']}\n"
                f"    # {t['id']} | Rule: {t['rule']} | Priority: {t['priority']}\n"
                f"    Given {t['given']}\n"
                f"    When  {t['when']}\n"
                f"    Then  {t['then']}\n"
            )
        st.download_button(
            "⬇️ Download .feature file",
            "\n".join(lines),
            f"IEP_TestCases_{ts}.feature",
            "text/plain",
        )
