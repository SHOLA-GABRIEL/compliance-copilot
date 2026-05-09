# 🛡️ Compliance Copilot

> AI-powered compliance gap analysis — upload a policy PDF and get instant mapping to NIST, ISO 27001, SOC 2, GDPR & HIPAA with a prioritized remediation plan.

![Demo](assets/demo.gif)
<!-- Replace with your actual Streamlit Cloud URL screenshot after deployment -->

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://shola-gabriel-compliance-copilot.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What It Does

Most small and mid-sized companies have a security policy document sitting in a folder somewhere — but have no idea how well it actually covers their compliance obligations. Hiring a GRC consultant to find out costs **$2,000–$8,000 per engagement**.

**Compliance Copilot solves this in under 60 seconds:**

1. 📄 Upload your policy PDF (Information Security Policy, Privacy Policy, ISMS, DR/BCP)
2. 🤖 AI reads and maps every clause to industry control frameworks
3. 📊 Get a compliance score, gap analysis, and remediation plan — instantly

---

## 🖥️ Live Demo

👉 **[Try it live →](https://shola-gabriel-compliance-copilot.streamlit.app)**

---

## 💡 Why I Built This

During my NYSC year, I was looking for a project that:
- Solved a **real business problem** companies actually pay for
- Could be built with **limited internet** (no heavy infrastructure)
- Had **genuine freelance potential** — not just a portfolio toy

GRC (Governance, Risk & Compliance) is a space where even a basic AI tool creates enormous value. Compliance analysts spend days manually cross-referencing policy documents against control frameworks. I wanted to compress that into a minute.

This project taught me how to combine **LLM reasoning** with **structured output parsing** to produce reliable, auditable results — not just chatbot responses.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                       │
└─────────────────────┬───────────────────────────────────┘
                      │ Upload PDF
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Streamlit UI (app.py)                  │
│  • File upload      • Results dashboard                 │
│  • Framework picker • Gap cards + severity filter       │
│  • Progress steps   • Export JSON / Markdown            │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌──────────────────┐   ┌─────────────────────────────────┐
│   utils.py       │   │        analyzer.py              │
│                  │   │                                 │
│ • PDF extraction │   │ • Control registry              │
│ • Text cleaning  │──▶│   (NIST / ISO / SOC2 /          │
│ • Chunking       │   │    GDPR / HIPAA)                │
└──────────────────┘   │ • Prompt engineering            │
                       │ • Claude API call               │
                       │ • JSON response parsing         │
                       └──────────────┬──────────────────┘
                                      │
                                      ▼
                       ┌─────────────────────────────────┐
                       │       Anthropic Claude API      │
                       │   (claude-opus-4-5)             │
                       │                                 │
                       │  Input:  policy text + controls │
                       │  Output: structured JSON        │
                       │  • overall_score                │
                       │  • gaps[] with severity         │
                       │  • coverage_matrix[]            │
                       │  • remediation_plan[]           │
                       └─────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| UI | Streamlit | Fastest way to ship a data app |
| AI | Anthropic Claude (claude-opus-4-5) | Best at structured reasoning |
| Orchestration | LangChain | Prompt management + chaining |
| PDF Parsing | pypdf | Lightweight, no server needed |
| Language | Python 3.12 | GRC tooling standard |
| Deployment | Streamlit Cloud | Free, one-click deploy |

---

## 📋 Frameworks Supported

| Framework | Version | Controls Mapped |
|-----------|---------|----------------|
| NIST Cybersecurity Framework | 2.0 | 26 |
| ISO 27001 | 2022 | 23 |
| SOC 2 | Type II | 20 |
| GDPR | EU 2016/679 | 15 |
| HIPAA | Security Rule | 15 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key → [Get one here](https://console.anthropic.com)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/SHOLA-GABRIEL/compliance-copilot.git
cd compliance-copilot

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🔐 Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Never commit your `.env` file. It's in `.gitignore` by default.

---

## 🧱 Challenges & How I Solved Them

### 1. Getting structured JSON from an LLM reliably
**Problem:** Claude sometimes returned markdown-wrapped JSON or added explanation text before the JSON object, breaking `json.loads()`.

**Solution:** Added a regex stripping step to remove markdown fences before parsing, plus a `_fallback_result()` method that returns a graceful error state instead of crashing the app.

```python
raw = re.sub(r"^```(?:json)?\s*", "", raw)
raw = re.sub(r"\s*```$", "", raw)
return json.loads(raw)
```

---

### 2. PDF text extraction quality
**Problem:** Many policy PDFs are scanned documents or have complex layouts — pypdf extracts garbled text from these.

**Solution:** Built a two-layer extraction system: pypdf as primary, pdfminer.six as fallback. Added a `_clean_text()` function to normalize whitespace and strip control characters before sending to the AI.

---

### 3. Context window limits
**Problem:** Large policy documents (50+ pages) exceed the token limit for a single API call.

**Solution:** Built `chunk_text()` and `truncate_for_context()` in `utils.py`. The truncation preserves the document beginning (scope/purpose) and end (appendices with controls) — the two most compliance-relevant sections.

---

### 4. Making the UI feel professional without a frontend framework
**Problem:** Default Streamlit looks generic and wouldn't impress clients or employers.

**Solution:** Injected ~200 lines of custom CSS to create a dark, terminal-inspired aesthetic with custom typography (Space Grotesk + JetBrains Mono), severity-coded gap cards, and a score gauge — all inside Streamlit's `st.markdown()`.

---

## 📁 Project Structure

```
compliance-copilot/
├── app.py              # Streamlit UI + page routing
├── analyzer.py         # AI engine + framework control registry
├── utils.py            # PDF extraction + text preprocessing
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Protects secrets
└── README.md           # You are here
```

---

## 💼 Business Use Cases

This tool is production-ready for:

- **GRC Consultants** — run initial gap assessments in minutes, not days
- **Startups** preparing for SOC 2 or ISO 27001 certification
- **SMBs** that can't afford a full-time compliance team
- **Internal Auditors** needing a first-pass before manual review
- **Law firms** doing due diligence on acquisition targets

---

## 🗺️ Roadmap

- [ ] Multi-document upload (compare policy suite holistically)
- [ ] Export to PDF report with company branding
- [ ] Evidence upload (attach proof documents to close gaps)
- [ ] Continuous monitoring mode (re-scan on policy updates)
- [ ] Fine-tuned model on real compliance audit data

---

## 👤 Author

**Shola Gabriel**
- GitHub: [@SHOLA-GABRIEL](https://github.com/SHOLA-GABRIEL)
- Built during NYSC · Nigeria · 2025

---

## 📄 License

MIT — free to use, modify, and deploy commercially.
