# 🛡️ Compliance Copilot

AI-powered compliance gap analysis. Upload a security/privacy policy PDF → get instant mapping to NIST CSF 2.0, ISO 27001:2022, SOC 2, GDPR, or HIPAA with a prioritized gap analysis and remediation plan.

---

## What it does

1. **Extracts** text from your policy PDF
2. **Maps** policy content to controls across 5 major frameworks
3. **Scores** your overall compliance posture (0–100)
4. **Surfaces gaps** with severity ratings (Critical → Low)
5. **Generates a remediation plan** ordered by impact/effort ratio
6. **Exports** findings as JSON or Markdown

---

## Quick start

### 1. Clone / unzip the project
```bash
cd compliance-copilot
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Anthropic API key
```bash
cp .env.example .env
# Edit .env and paste your key from https://console.anthropic.com
```

### 5. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Project structure

```
compliance-copilot/
├── app.py            # Streamlit UI
├── analyzer.py       # AI analysis engine (LangChain + Claude)
├── utils.py          # PDF extraction & text chunking
├── requirements.txt
├── .env.example
└── README.md
```

---

## Frameworks supported

| Framework       | Version    | Controls |
|----------------|------------|---------|
| NIST CSF        | 2.0        | 26      |
| ISO 27001       | 2022       | 23      |
| SOC 2           | Type II    | 20      |
| GDPR            | EU 2016/679| 15      |
| HIPAA           | Security Rule | 15   |

---

## Tips for best results

- Upload your **Information Security Policy**, **ISMS**, or **Privacy Policy**
- Larger, more detailed documents produce richer gap analyses
- Use **Deep Dive** mode for audits; **Quick Scan** for a first pass
- Select only the frameworks relevant to your industry to reduce noise

---

## Freelance / consulting use

This tool is well-suited for:
- **GRC consulting** — run initial gap assessments for clients in minutes
- **Startups** preparing for SOC 2 or ISO 27001 certification
- **SMBs** that can't afford a full-time compliance team
- **Auditors** needing a fast first-pass before manual review

Typical consulting rates for compliance gap analysis: $150–$400/hour (or $2k–$8k per engagement).

---

## Environment variables

| Variable            | Required | Description                       |
|---------------------|----------|-----------------------------------|
| `ANTHROPIC_API_KEY` | Yes      | Your Claude API key               |

---

## License

MIT — use freely, modify, and deploy for clients.
