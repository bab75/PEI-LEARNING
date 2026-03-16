"""
Page: Document Search & Q&A (RAG)
Upload SOP PDFs → extract text → semantic search → Q&A
"""

import streamlit as st
import os, re, json
from pathlib import Path

# ── page config (inherited from IEPapp.py styles) ─────────────────────────────
st.markdown("## 📄 Document Search & Q&A")
st.markdown(
    '<p style="color:#4a6080;margin-top:-10px;margin-bottom:24px;">'
    'Upload your NYC DOE IEP SOP PDFs and ask natural-language questions. '
    'Results are cited with page numbers.</p>',
    unsafe_allow_html=True,
)

# ── helpers ───────────────────────────────────────────────────────────────────
DOCS_DIR = Path(__file__).parent.parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)


def extract_text_from_pdf(uploaded_file) -> dict[int, str]:
    """Return {page_num: text} dict. Tries pdfplumber, falls back to PyMuPDF."""
    pages = {}
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                pages[i] = text
        return pages
    except Exception:
        pass

    try:
        import fitz, io  # PyMuPDF
        uploaded_file.seek(0)
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for i, page in enumerate(doc, 1):
            pages[i] = page.get_text()
        return pages
    except Exception as e:
        st.error(f"PDF extraction failed: {e}. Install pdfplumber or PyMuPDF.")
        return {}


def chunk_pages(pages: dict, chunk_size: int = 400) -> list[dict]:
    """Split page text into overlapping chunks for retrieval."""
    chunks = []
    for page_num, text in pages.items():
        words = text.split()
        step = chunk_size // 2
        for start in range(0, max(1, len(words) - chunk_size + 1), step):
            chunk_words = words[start : start + chunk_size]
            chunks.append({
                "page": page_num,
                "text": " ".join(chunk_words),
                "start_word": start,
            })
    return chunks


def keyword_search(chunks: list[dict], query: str, top_k: int = 6) -> list[dict]:
    """TF-IDF-style keyword scoring — no external vector DB needed."""
    query_terms = re.findall(r'\w+', query.lower())
    scored = []
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        # exact phrase bonus
        exact = 5 if query.lower() in text_lower else 0
        # term frequency
        tf = sum(text_lower.count(term) for term in query_terms)
        # IEP-specific term weighting
        key_terms = {
            "iep": 3, "evaluation": 2, "eligibility": 2, "placement": 2,
            "annual review": 3, "amendment": 2, "consent": 2, "disability": 2,
            "classification": 2, "related services": 2, "least restrictive": 3,
        }
        domain_boost = sum(
            weight
            for kw, weight in key_terms.items()
            if kw in text_lower
        )
        score = tf + exact + domain_boost
        if score > 0:
            scored.append({**chunk, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def highlight(text: str, query: str) -> str:
    """Wrap query terms in <mark> for display."""
    terms = re.findall(r'\w+', query)
    for term in sorted(terms, key=len, reverse=True):
        text = re.sub(
            rf'\b({re.escape(term)})\b',
            r'<mark style="background:#fef3c7;border-radius:2px;">\1</mark>',
            text, flags=re.IGNORECASE
        )
    return text


# ── session state ─────────────────────────────────────────────────────────────
if "doc_chunks"   not in st.session_state: st.session_state.doc_chunks   = []
if "doc_pages"    not in st.session_state: st.session_state.doc_pages    = {}
if "doc_name"     not in st.session_state: st.session_state.doc_name     = ""
if "qa_history"   not in st.session_state: st.session_state.qa_history   = []

# ── layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2], gap="large")

# ── LEFT: Upload + controls ───────────────────────────────────────────────────
with left:
    st.markdown("### Upload SOP Document")
    uploaded = st.file_uploader(
        "Drag & drop your IEP SOP PDF (up to 80 pages)",
        type=["pdf"],
        help="Accepts any NYC DOE IEP SOP PDF. Text is extracted locally.",
    )

    if uploaded and uploaded.name != st.session_state.doc_name:
        with st.spinner("Extracting and indexing pages…"):
            pages = extract_text_from_pdf(uploaded)
            if pages:
                chunks = chunk_pages(pages)
                st.session_state.doc_pages  = pages
                st.session_state.doc_chunks = chunks
                st.session_state.doc_name   = uploaded.name
                st.session_state.qa_history = []
                st.success(f"✓ Indexed {len(pages)} pages · {len(chunks)} chunks")

    if st.session_state.doc_name:
        st.markdown(f"""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;
                    padding:14px;margin-top:8px;font-size:0.85rem;">
            <b style="color:#065f46;">Active document</b><br>
            <span style="color:#047857;font-family:'IBM Plex Mono',monospace;
                         font-size:0.78rem;">{st.session_state.doc_name}</span><br>
            <span style="color:#6b7280;margin-top:4px;display:block;">
                {len(st.session_state.doc_pages)} pages · 
                {len(st.session_state.doc_chunks)} searchable chunks
            </span>
        </div>""", unsafe_allow_html=True)

    # ── Suggested queries ─────────────────────────────────────────────────────
    st.markdown("### Suggested Queries")
    suggestions = [
        "What is the timeline for initial evaluation?",
        "When is parental consent required?",
        "What are the eligibility criteria for autism?",
        "How often must an IEP be reviewed annually?",
        "What related services must be documented?",
        "Define least restrictive environment (LRE)",
        "What triggers a reevaluation?",
        "What is included in the present levels section?",
    ]
    for s in suggestions:
        if st.button(s, key=f"sug_{s[:20]}", use_container_width=True):
            st.session_state["prefill_query"] = s
            st.rerun()

# ── RIGHT: Search + results ───────────────────────────────────────────────────
with right:
    # Q&A section
    st.markdown("### Ask a Question")
    prefill = st.session_state.pop("prefill_query", "")
    query = st.text_input(
        "Ask anything about the IEP SOP…",
        value=prefill,
        placeholder="e.g. What is the 60-day timeline for initial evaluation?",
        label_visibility="collapsed",
    )

    col_search, col_clear = st.columns([3, 1])
    with col_search:
        search_clicked = st.button("🔍  Search Document", use_container_width=True)
    with col_clear:
        if st.button("Clear history", use_container_width=True):
            st.session_state.qa_history = []
            st.rerun()

    if search_clicked and query:
        if not st.session_state.doc_chunks:
            st.warning("⚠️ Please upload a PDF document first.")
        else:
            with st.spinner("Searching…"):
                results = keyword_search(st.session_state.doc_chunks, query)
            st.session_state.qa_history.insert(0, {"query": query, "results": results})

    # ── Results display ───────────────────────────────────────────────────────
    if st.session_state.qa_history:
        for entry in st.session_state.qa_history:
            st.markdown(f"""
            <div style="background:#eff6ff;border-left:3px solid #2176ae;
                        border-radius:6px;padding:12px 16px;margin:16px 0 8px;">
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;
                             color:#64748b;text-transform:uppercase;letter-spacing:0.06em;">
                    Query</span><br>
                <span style="font-weight:600;color:#0d1b2a;">{entry['query']}</span>
            </div>""", unsafe_allow_html=True)

            if entry["results"]:
                for i, r in enumerate(entry["results"], 1):
                    snippet = r["text"][:450] + ("…" if len(r["text"]) > 450 else "")
                    highlighted = highlight(snippet, entry["query"])
                    with st.expander(f"Result {i} — Page {r['page']}  · score: {r['score']}", expanded=(i==1)):
                        st.markdown(f"""
                        <div style="font-size:0.88rem;line-height:1.8;color:#374151;">
                            {highlighted}
                        </div>
                        <div style="margin-top:10px;">
                            <span style="background:#dbeafe;color:#1e40af;font-family:'IBM Plex Mono',monospace;
                                         font-size:0.7rem;padding:2px 8px;border-radius:4px;">
                                📄 Page {r['page']}
                            </span>
                        </div>""", unsafe_allow_html=True)
            else:
                st.info("No relevant passages found. Try rephrasing or use a keyword from the document.")

    # ── Page browser ─────────────────────────────────────────────────────────
    if st.session_state.doc_pages:
        st.markdown("---")
        st.markdown("### 📖 Page Browser")
        max_page = len(st.session_state.doc_pages)
        page_num = st.number_input("Jump to page", 1, max_page, 1)
        text = st.session_state.doc_pages.get(page_num, "")
        st.markdown(f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:16px;max-height:400px;overflow-y:auto;
                    font-size:0.85rem;line-height:1.8;white-space:pre-wrap;
                    font-family:'IBM Plex Mono',monospace;color:#334155;">
{text if text else '(No text extracted from this page)'}
        </div>""", unsafe_allow_html=True)
