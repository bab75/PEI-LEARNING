"""
Page: Rule Engine & Decision Trees
Interactive scenario navigator: given student profile → required services, timelines, docs.
"""

import streamlit as st
import json

st.markdown("## 🌳 Rule Engine & Decision Trees")
st.markdown(
    '<p style="color:#4a6080;margin-top:-10px;margin-bottom:24px;">'
    'Configure a student profile and the engine will determine required services, '
    'timelines, documents and generate test scenarios.</p>',
    unsafe_allow_html=True,
)

# ── IEP Business Rules Database ───────────────────────────────────────────────
RULES = {
    "evaluation_timeline": {
        "rule_id": "R-001",
        "name": "Initial Evaluation Timeline",
        "trigger": "Referral received",
        "law": "IDEA § 300.301(c)(1)",
        "condition": "Initial referral for special education",
        "outcome": "Evaluation must be completed within 60 school days of receiving parent consent",
        "exceptions": ["If parent repeatedly fails to produce child", "Child enrolls mid-evaluation from another district"],
        "roles": ["CSE Chairperson", "School Psychologist"],
    },
    "annual_review_timeline": {
        "rule_id": "R-002",
        "name": "Annual Review Requirement",
        "trigger": "IEP anniversary date approaching",
        "law": "IDEA § 300.324(b)",
        "condition": "Student has an active IEP",
        "outcome": "IEP must be reviewed at least once per year",
        "exceptions": ["Parents and school agree to revise IEP without a meeting"],
        "roles": ["IEP Team", "Parent"],
    },
    "lre_requirement": {
        "rule_id": "R-003",
        "name": "Least Restrictive Environment",
        "trigger": "Placement determination",
        "law": "IDEA § 300.114",
        "condition": "Any placement decision",
        "outcome": "Student must be educated in the least restrictive environment appropriate to their needs",
        "exceptions": ["Nature or severity of disability requires more restrictive setting"],
        "roles": ["CSE", "Parent"],
    },
    "parent_consent": {
        "rule_id": "R-004",
        "name": "Parental Consent Requirements",
        "trigger": "Initial evaluation or placement",
        "law": "IDEA § 300.300",
        "condition": "Initial evaluation OR initial placement",
        "outcome": "Written informed consent must be obtained before evaluation and before initial placement",
        "exceptions": ["Subsequent annual reviews do not require consent", "Amendments with written parent agreement"],
        "roles": ["CSE Chairperson", "Parent"],
    },
    "pwn_requirement": {
        "rule_id": "R-005",
        "name": "Prior Written Notice",
        "trigger": "Any proposed or refused action",
        "law": "IDEA § 300.503",
        "condition": "School proposes or refuses to change identification, evaluation, educational placement, or provision of FAPE",
        "outcome": "Prior Written Notice must be provided to parents in reasonable time before action",
        "exceptions": [],
        "roles": ["CSE Chairperson"],
    },
}

# ── Disability → required services mapping ────────────────────────────────────
DISABILITY_RULES = {
    "Autism": {
        "required_evals": ["Psychological", "Educational", "Speech/Language", "Occupational Therapy", "Behavioral Assessment"],
        "common_services": ["Special Education", "Speech/Language Therapy", "Occupational Therapy", "ABA (if appropriate)", "Counseling"],
        "key_considerations": [
            "Consider need for behavioral intervention plan (BIP)",
            "Evaluate communication needs across all environments",
            "Consider extended school year (ESY) services",
            "Address sensory processing needs in IEP",
        ],
        "timeline_notes": "ADOS-2 assessment recommended; may require extended evaluation time",
    },
    "Learning Disability": {
        "required_evals": ["Psychological", "Educational", "Academic Achievement", "Processing Speed", "Working Memory"],
        "common_services": ["Resource Room", "Integrated Co-Teaching (ICT)", "Consultant Teacher", "Reading Specialist"],
        "key_considerations": [
            "Identify specific areas of deficit (reading, math, writing)",
            "Document discrepancy between ability and achievement",
            "Consider assistive technology needs",
            "Address homework and testing accommodations",
        ],
        "timeline_notes": "Response to Intervention (RTI) data should be included if available",
    },
    "Speech/Language Impairment": {
        "required_evals": ["Speech/Language Evaluation", "Hearing Screening", "Educational Assessment"],
        "common_services": ["Speech/Language Therapy (individual and/or group)"],
        "key_considerations": [
            "Specify therapy frequency and duration precisely",
            "Distinguish between articulation, language, and fluency goals",
            "Consider AAC if applicable",
        ],
        "timeline_notes": "ASHA-certified SLP must conduct evaluation",
    },
    "Emotional Disturbance": {
        "required_evals": ["Psychological", "Social History", "Psychiatric (if applicable)", "Educational"],
        "common_services": ["Counseling", "Social Work", "Special Class (if needed)", "Crisis Intervention"],
        "key_considerations": [
            "Behavioral Intervention Plan (BIP) strongly recommended",
            "Functional Behavioral Assessment (FBA) required if BIP developed",
            "Consider wraparound services and community supports",
            "Document manifestation determination process if discipline issues",
        ],
        "timeline_notes": "Consider trauma-informed approaches; coordinate with mental health providers",
    },
    "Intellectual Disability": {
        "required_evals": ["Psychological (IQ testing)", "Adaptive Behavior Assessment", "Educational", "Medical (if applicable)"],
        "common_services": ["Special Class", "Life Skills Instruction", "Vocational Training (age 14+)", "Related Services as needed"],
        "key_considerations": [
            "Adaptive behavior must be assessed across multiple settings",
            "Transition planning begins at age 15 (NYC DOE) — document in IEP",
            "Consider community-based instruction",
        ],
        "timeline_notes": "Adaptive behavior instruments (Vineland, ABAS) should be administered",
    },
    "Other Health Impairment": {
        "required_evals": ["Medical documentation", "Educational", "Psychological (if applicable)"],
        "common_services": ["Varies by condition", "Health-related accommodations", "Resource Room or ICT"],
        "key_considerations": [
            "Medical documentation from physician required",
            "Address how health condition impacts educational performance",
            "Consider 504 plan if special education not needed",
            "Medication management and health plans may be needed",
        ],
        "timeline_notes": "ADHD most common OHI; confirm medical diagnosis documentation",
    },
}

# ── Placement options ─────────────────────────────────────────────────────────
PLACEMENT_OPTIONS = {
    "General Education with Accommodations (504)": {
        "restrictiveness": 1,
        "desc": "Student remains in general education class with documented accommodations only.",
        "eligibility": "Disability substantially limits a major life activity but does not require specialized instruction.",
    },
    "Consultant Teacher (CT)": {
        "restrictiveness": 2,
        "desc": "Special education teacher provides services within the general education classroom.",
        "eligibility": "Student can access general education curriculum with support.",
    },
    "Resource Room": {
        "restrictiveness": 3,
        "desc": "Student receives supplemental special education instruction in a small group, separate from general ed.",
        "eligibility": "Student needs direct specialized instruction for part of the day.",
    },
    "Integrated Co-Teaching (ICT)": {
        "restrictiveness": 3,
        "desc": "General and special education teacher co-teach in a classroom with up to 40% students with IEPs.",
        "eligibility": "Student benefits from general education setting with additional support.",
    },
    "Special Class (12:1:1)": {
        "restrictiveness": 4,
        "desc": "12 students, 1 teacher, 1 paraprofessional. Specialized curriculum.",
        "eligibility": "Student requires specialized instruction more than 60% of the day.",
    },
    "Special Class (8:1:1)": {
        "restrictiveness": 5,
        "desc": "8 students, 1 teacher, 1 paraprofessional. Significant supports.",
        "eligibility": "Student has moderate to severe needs requiring intensive support.",
    },
    "Special Class (6:1:1)": {
        "restrictiveness": 6,
        "desc": "6 students, 1 teacher, 1 paraprofessional. High-intensity environment.",
        "eligibility": "Significant behavioral and/or academic needs requiring high staff ratio.",
    },
    "Special Day School": {
        "restrictiveness": 7,
        "desc": "Separate school for students with disabilities.",
        "eligibility": "General education environment cannot meet needs even with supports.",
    },
    "Residential Placement": {
        "restrictiveness": 8,
        "desc": "24-hour placement. Most restrictive option.",
        "eligibility": "Educational needs require 24-hour programming; safety concerns.",
    },
}

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎯  Student Profile Decision Tree", "📏  Business Rules Explorer", "🗺️  LRE Continuum"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Student Profile Decision Tree
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Configure Student Profile")
    st.markdown("Fill in the student parameters. The rule engine will determine applicable rules and requirements.")

    c1, c2, c3 = st.columns(3)
    with c1:
        iep_type = st.selectbox(
            "IEP Stage",
            ["Initial Evaluation", "Annual Review", "Reevaluation", "Amendment"],
        )
        disability = st.selectbox("Disability Classification", list(DISABILITY_RULES.keys()))
        grade = st.selectbox("Grade Level", ["PreK", "K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])

    with c2:
        age = st.number_input("Student Age", 3, 21, 10)
        placement = st.selectbox("Current Placement", list(PLACEMENT_OPTIONS.keys()))
        parent_consent = st.checkbox("Parent Consent on File", value=True)

    with c3:
        has_bip = st.checkbox("Has Behavioral Intervention Plan (BIP)")
        esy_needed = st.checkbox("Extended School Year (ESY) Consideration")
        transition_age = age >= 15
        if transition_age:
            st.info("🔔 Transition planning required (age 15+)")

    generate = st.button("⚡ Generate Rules & Requirements", use_container_width=True)

    if generate:
        drules = DISABILITY_RULES[disability]
        placement_info = PLACEMENT_OPTIONS[placement]

        st.markdown("---")
        st.markdown("### 📋 Rule Engine Output")

        # ── Required evaluations ──────────────────────────────────────────────
        st.markdown("#### Required Evaluations")
        eval_cols = st.columns(len(drules["required_evals"]))
        for col, ev in zip(eval_cols, drules["required_evals"]):
            with col:
                st.markdown(f"""
                <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
                            padding:12px;text-align:center;font-size:0.83rem;color:#1e40af;
                            font-weight:600;">{ev}</div>""", unsafe_allow_html=True)

        # ── Required services ─────────────────────────────────────────────────
        st.markdown("#### Recommended Services")
        for svc in drules["common_services"]:
            st.markdown(
                f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;'
                f'padding:4px 12px;font-size:0.85rem;color:#065f46;display:inline-block;'
                f'margin:3px;">✓ {svc}</span>',
                unsafe_allow_html=True,
            )

        # ── Key considerations ────────────────────────────────────────────────
        st.markdown("#### Key Considerations for this Profile")
        for kc in drules["key_considerations"]:
            st.markdown(f"- {kc}")
        if transition_age:
            st.markdown("- ⚠️ **Transition planning must be included** — student is 15+ years old")
        if has_bip:
            st.markdown("- ⚠️ **FBA must precede BIP** — ensure Functional Behavioral Assessment is documented")
        if esy_needed:
            st.markdown("- ⚠️ **ESY determination required** — document rationale in IEP")

        # ── Placement analysis ────────────────────────────────────────────────
        st.markdown("#### Current Placement Analysis")
        lre_level = placement_info["restrictiveness"]
        lre_bar = "🟦" * lre_level + "⬜" * (8 - lre_level)
        st.markdown(f"""
        <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:16px;">
            <b style="color:#92400e;">{placement}</b><br>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:1.1rem;">
                {lre_bar} {lre_level}/8
            </span><br>
            <span style="color:#78350f;font-size:0.85rem;margin-top:6px;display:block;">
                {placement_info['desc']}
            </span>
        </div>""", unsafe_allow_html=True)

        # ── Triggered business rules ──────────────────────────────────────────
        st.markdown("#### Triggered Business Rules")
        triggered = []
        if iep_type == "Initial Evaluation": triggered.append("evaluation_timeline")
        triggered.extend(["annual_review_timeline", "lre_requirement", "pwn_requirement"])
        if not parent_consent: triggered.append("parent_consent")

        for rule_key in triggered:
            rule = RULES[rule_key]
            st.markdown(f"""
            <div style="border:1px solid #e2e8f0;border-left:3px solid #2176ae;
                        border-radius:6px;padding:14px;margin:8px 0;">
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
                             color:#64748b;">{rule['rule_id']}</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
                             color:#94a3b8;margin-left:8px;">{rule['law']}</span>
                <div style="font-weight:600;color:#0d1b2a;margin:4px 0;">{rule['name']}</div>
                <div style="color:#374151;font-size:0.88rem;">{rule['outcome']}</div>
                {('<div style="color:#92400e;font-size:0.82rem;margin-top:6px;">⚠️ Consent required — not on file</div>' if not parent_consent and rule_key == 'parent_consent' else '')}
            </div>""", unsafe_allow_html=True)

        # ── Export ────────────────────────────────────────────────────────────
        st.markdown("---")
        export_data = {
            "student_profile": {
                "iep_type": iep_type, "disability": disability,
                "grade": grade, "age": age, "placement": placement,
                "parent_consent": parent_consent, "has_bip": has_bip,
                "esy_consideration": esy_needed, "transition_required": transition_age,
            },
            "required_evaluations": drules["required_evals"],
            "recommended_services": drules["common_services"],
            "key_considerations": drules["key_considerations"],
            "triggered_rules": [RULES[r]["rule_id"] + ": " + RULES[r]["name"] for r in triggered],
        }
        st.download_button(
            "⬇️ Export Rule Output (JSON)",
            json.dumps(export_data, indent=2),
            file_name="IEP_RuleEngine_Output.json",
            mime="application/json",
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Business Rules Explorer
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### All Business Rules")
    search_rule = st.text_input("Filter rules…", placeholder="Search by name, law, or trigger…")

    for key, rule in RULES.items():
        if search_rule.lower() and search_rule.lower() not in json.dumps(rule).lower():
            continue
        with st.expander(f"`{rule['rule_id']}` · {rule['name']} · {rule['law']}"):
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown(f"**Trigger:** {rule['trigger']}")
                st.markdown(f"**Condition:** {rule['condition']}")
                st.markdown(f"**Outcome:** {rule['outcome']}")
            with c_right:
                st.markdown(f"**Responsible Roles:** {', '.join(rule['roles'])}")
                if rule["exceptions"]:
                    st.markdown("**Exceptions:**")
                    for ex in rule["exceptions"]:
                        st.markdown(f"- ⚠️ {ex}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — LRE Continuum
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### Least Restrictive Environment (LRE) Continuum")
    st.markdown("IDEA mandates placement in the **least restrictive environment** appropriate to the student's needs.")

    for name, info in sorted(PLACEMENT_OPTIONS.items(), key=lambda x: x[1]["restrictiveness"]):
        bar = "🟦" * info["restrictiveness"] + "⬜" * (8 - info["restrictiveness"])
        color_map = {1: "#06d6a0", 2: "#2176ae", 3: "#4c9be8", 4: "#f4a261",
                     5: "#e07b2a", 6: "#d45a1a", 7: "#c23a1a", 8: "#9b0a0a"}
        c = color_map.get(info["restrictiveness"], "#888")
        st.markdown(f"""
        <div style="border:1px solid #e2e8f0;border-left:4px solid {c};
                    border-radius:8px;padding:14px 18px;margin:8px 0;
                    background:white;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:600;color:#0d1b2a;">{name}</div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:1rem;">{bar}</span>
            </div>
            <div style="color:#64748b;font-size:0.85rem;margin-top:6px;">{info['desc']}</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:4px;font-style:italic;">
                Eligibility: {info['eligibility']}
            </div>
        </div>""", unsafe_allow_html=True)
