# NYC DOE IEP Intelligence Platform

> A Streamlit application for Business Analysts, QA Testers, Developers and Special Education Coordinators to navigate, validate and operationalize NYC DOE IEP Standard Operating Procedures.

---

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the App](#running-the-app)
- [Module Guide](#module-guide)
- [GitHub Workflow](#github-workflow)
- [Adding Your SOP PDFs](#adding-your-sop-pdfs)
- [Upgrading to Semantic Search (RAG)](#upgrading-to-semantic-search-rag)
- [For Business Analysts](#for-business-analysts)
- [For QA Testers](#for-qa-testers)
- [For Developers](#for-developers)
- [For Special Ed Coordinators](#for-special-ed-coordinators)

---

## Overview

This platform converts the NYC DOE IEP Standard Operating Procedures (80+ pages) into actionable, searchable, role-specific tooling. It is built on publicly available NYC DOE / IDEA documentation.

**Key capabilities:**
- Upload and search SOP PDFs with keyword-based retrieval (upgradeable to vector/semantic search)
- Visual workflow maps for all 4 IEP process types with embedded QA test scenarios
- Rule engine: configure a student profile → get required evaluations, services, documents, and triggered business rules
- Compliance checklists by IEP type and role, with CSV/JSON export
- BDD test case generator (Gherkin, pytest stub, TestRail CSV)

---

## Project Structure

```
nycdoe_iep/
│
├── IEPapp.py                        # ← Main entry point (run this)
│
├── pages/
│   ├── 1_📄_Document_Search.py      # PDF upload, keyword search, page browser
│   ├── 2_🔀_Process_Maps.py         # IEP lifecycle workflows (Initial, Annual, Reeval, Amendment)
│   ├── 3_🌳_Rule_Engine.py          # Student profile → rule engine → decision tree
│   ├── 4_✅_Compliance_Checklist.py # Checklist generator + export
│   └── 5_🧪_Test_Cases.py           # BDD test case bank + export
│
├── docs/                            # ← Place your SOP PDFs here
│   └── .gitkeep
│
├── utils/                           # Helper modules (extend here)
│   └── .gitkeep
│
├── requirements.txt                 # All Python dependencies
└── README.md                        # This file
```

---

## Setup & Installation

### Prerequisites
- Python 3.9 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_ORG/nycdoe-iep-platform.git
cd nycdoe-iep-platform
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Running the App

```bash
streamlit run IEPapp.py
```

The app will open at `http://localhost:8501`

---

## Module Guide

| Page | File | Purpose | Primary Users |
|------|------|---------|---------------|
| Home | `IEPapp.py` | Dashboard + navigation | All |
| Document Search | `1_📄_Document_Search.py` | Upload PDF, keyword Q&A, page browser | BA, Dev |
| Process Maps | `2_🔀_Process_Maps.py` | Visual IEP lifecycle, QA scenarios by phase | BA, Coordinator |
| Rule Engine | `3_🌳_Rule_Engine.py` | Student profile → triggered rules + services | Dev, QA |
| Compliance Checklist | `4_✅_Compliance_Checklist.py` | Generate, track, export checklists by role | Coordinator, QA |
| Test Cases | `5_🧪_Test_Cases.py` | BDD/Gherkin test case bank + export | QA, Dev |

---

## GitHub Workflow

### Recommended branch strategy
```
main          ← stable production branch
dev           ← integration branch
feature/*     ← individual feature work
hotfix/*      ← urgent fixes
```

### Storing SOP documents
Place your SOP PDFs in the `docs/` folder. Add to `.gitignore` if PDFs are large or contain sensitive information:

```
# .gitignore
docs/*.pdf
```

Or use Git LFS for large PDFs:
```bash
git lfs install
git lfs track "docs/*.pdf"
git add .gitattributes
```

### Environment variables
Create a `.env` file in the project root (never commit this):
```
# .env
OPENAI_API_KEY=sk-...          # Only needed if using OpenAI RAG upgrade
```

---

## Adding Your SOP PDFs

1. Copy your PDF files into the `docs/` folder
2. Launch the app and go to **Document Search**
3. Use the file uploader to upload a PDF from your local machine
4. The app extracts and indexes all pages automatically

**Supported PDF types:**
- Text-based PDFs (best results)
- Scanned PDFs are supported if the scan is clear (pdfplumber handles many cases)

---

## Upgrading to Semantic Search (RAG)

The default keyword search works well for specific terms. For natural-language questions, upgrade to vector search:

### Option A: Local embeddings (no API key)
```bash
pip install sentence-transformers faiss-cpu
```
Replace `keyword_search()` in `pages/1_📄_Document_Search.py` with a FAISS vector search using `sentence-transformers`.

### Option B: OpenAI embeddings
```bash
pip install openai langchain langchain-openai chromadb
```
Use LangChain's `RetrievalQA` chain with ChromaDB as the vector store. Set `OPENAI_API_KEY` in your `.env`.

---

## For Business Analysts

**Start here:** Process Maps (`2_🔀_Process_Maps.py`)

- Use **Flow view** to walk through each IEP process step by step
- Use **Table view** to get a summary matrix of all phases, timelines, and owners
- Use **Document Search** to look up specific SOP clauses by keyword
- Use **Rule Engine** to validate your process understanding against business rules

**Common BA questions this tool answers:**
- What triggers the 60-day clock? (Rule Engine → R-001)
- What documents are required at each phase? (Process Maps → expand any step)
- What is the difference between an Amendment and an Annual Review? (Process Maps → compare workflows)

---

## For QA Testers

**Start here:** Test Cases (`5_🧪_Test_Cases.py`)

- Filter by Domain (e.g., Evaluation, IEP Development) and Priority (Critical first)
- Copy Gherkin scenarios directly into Cucumber / SpecFlow / Behave
- Export CSV to import into TestRail, Jira Xray, or Azure DevOps Test Plans
- Use **Process Maps → Test Cases view** to generate phase-specific test scenarios

**Export workflow:**
1. Select domain and priority
2. Click Export → CSV (TestRail) or Gherkin
3. Import into your test management system

---

## For Developers

**Start here:** Rule Engine (`3_🌳_Rule_Engine.py`)

- Configure a student profile and export the JSON rule output
- Use this JSON as the spec for API validations and database constraints
- Business rules are stored in `RULES` dict — easy to extend
- The rule_id references (R-001, R-002…) map to IDEA citations for traceability

**Extending the rule engine:**
```python
# In pages/3_🌳_Rule_Engine.py, add to RULES dict:
RULES["new_rule"] = {
    "rule_id": "R-010",
    "name": "Your Rule Name",
    "trigger": "When this happens",
    "law": "IDEA §300.XXX",
    "condition": "Condition that triggers the rule",
    "outcome": "What must happen",
    "exceptions": ["Exception 1"],
    "roles": ["Responsible Role"],
}
```

---

## For Special Ed Coordinators

**Start here:** Compliance Checklist (`4_✅_Compliance_Checklist.py`)

- Select your IEP type and role
- Work through the checklist before and during each CSE meeting
- Export to CSV for your records or to share with supervisors
- The **All Roles Summary** shows completion across all team members at a glance

**Tips:**
- Run the checklist for CSE Chairperson first (highest number of Critical items)
- Filter by "Critical" to focus on IDEA-mandated items first
- Add student name and OSIS number before exporting for case documentation
