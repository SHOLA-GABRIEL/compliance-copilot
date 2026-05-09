"""
analyzer.py
Core AI analysis engine.
Uses the Anthropic API (Claude) to map policy text to compliance frameworks.
"""

import json
import os
import re

# ── Framework control registries ──────────────────────────────────────────────
FRAMEWORKS = {
    "NIST CSF 2.0": {
        "GV.OC-01": "Organizational mission is understood",
        "GV.OC-02": "Internal and external stakeholders identified",
        "GV.RM-01": "Risk management objectives established",
        "GV.RM-02": "Risk appetite and tolerance defined",
        "GV.RR-01": "Leadership accountable for cybersecurity risk",
        "GV.SC-01": "Cybersecurity supply chain risk management policy",
        "ID.AM-01": "IT hardware assets inventoried",
        "ID.AM-02": "Software assets inventoried",
        "ID.AM-03": "Network communication assets represented",
        "ID.RA-01": "Asset vulnerabilities identified",
        "ID.RA-02": "Cyber threat intelligence received",
        "ID.RA-06": "Risk responses chosen and prioritized",
        "PR.AA-01": "Identities and credentials managed",
        "PR.AA-02": "Identities proofed and bound to credentials",
        "PR.AA-03": "Users, services, hardware authenticated",
        "PR.AA-05": "Access permissions managed",
        "PR.AT-01": "Personnel awareness training provided",
        "PR.DS-01": "Data-at-rest protected",
        "PR.DS-02": "Data-in-transit protected",
        "PR.IR-01": "Networks and environments protected",
        "DE.CM-01": "Networks monitored to detect attacks",
        "DE.CM-09": "Computing hardware and software monitored",
        "DE.AE-02": "Potentially adverse events analyzed",
        "RS.MA-01": "Incident response plan exists",
        "RS.CO-02": "Internal stakeholders notified of incidents",
        "RC.RP-01": "Recovery plan exists",
    },
    "ISO 27001:2022": {
        "A.5.1":  "Policies for information security",
        "A.5.2":  "Information security roles and responsibilities",
        "A.5.8":  "Information security in project management",
        "A.5.15": "Access control policy",
        "A.5.16": "Identity management",
        "A.5.17": "Authentication information",
        "A.5.23": "Information security for cloud services",
        "A.6.3":  "Information security awareness/education/training",
        "A.6.8":  "Information security event reporting",
        "A.7.1":  "Physical security perimeter",
        "A.7.9":  "Security of assets off-premises",
        "A.8.1":  "User endpoint devices",
        "A.8.2":  "Privileged access rights",
        "A.8.4":  "Access to source code",
        "A.8.7":  "Protection against malware",
        "A.8.8":  "Management of technical vulnerabilities",
        "A.8.12": "Data leakage prevention",
        "A.8.13": "Information backup",
        "A.8.15": "Logging",
        "A.8.16": "Monitoring activities",
        "A.8.24": "Use of cryptography",
        "A.5.26": "Response to information security incidents",
        "A.5.30": "ICT readiness for business continuity",
    },
    "SOC 2 Type II": {
        "CC1.1": "COSO Principle 1 - Integrity and ethical values",
        "CC1.2": "Board independence and oversight",
        "CC2.1": "Information quality for internal control",
        "CC2.2": "External communication of objectives",
        "CC3.1": "Risk assessment objectives",
        "CC3.2": "Risk identification and analysis",
        "CC5.1": "Control activities selection",
        "CC6.1": "Logical access security measures",
        "CC6.2": "New user access provisioned with approval",
        "CC6.3": "Access removed or modified timely",
        "CC6.6": "Logical access security - external threats",
        "CC6.7": "Data transmission restricted to authorized parties",
        "CC7.1": "Vulnerability detection tooling",
        "CC7.2": "Infrastructure monitored for anomalies",
        "CC7.3": "Security events evaluated",
        "CC8.1": "Change management process",
        "CC9.1": "Risk mitigation for business disruption",
        "A1.1":  "Availability capacity planning",
        "PI1.1": "Processing integrity policies",
        "P1.1":  "Privacy notice",
    },
    "GDPR": {
        "Art.5":  "Principles of processing",
        "Art.6":  "Lawful basis for processing",
        "Art.7":  "Conditions for consent",
        "Art.12": "Transparent information to data subjects",
        "Art.13": "Information provided at collection",
        "Art.17": "Right to erasure",
        "Art.20": "Right to data portability",
        "Art.25": "Data protection by design and by default",
        "Art.28": "Processor agreements",
        "Art.30": "Records of processing activities",
        "Art.32": "Security of processing",
        "Art.33": "Breach notification to supervisory authority",
        "Art.34": "Breach notification to data subjects",
        "Art.35": "Data protection impact assessment",
        "Art.37": "Data Protection Officer designation",
    },
    "HIPAA": {
        "164.306":    "Security standards general requirements",
        "164.308a1":  "Security management process",
        "164.308a3":  "Workforce security",
        "164.308a4":  "Information access management",
        "164.308a5":  "Security awareness and training",
        "164.308a6":  "Security incident procedures",
        "164.308a7":  "Contingency plan",
        "164.310a1":  "Facility access controls",
        "164.310d1":  "Device and media controls",
        "164.312a1":  "Access control",
        "164.312a2":  "Audit controls",
        "164.312b":   "Person or entity authentication",
        "164.312c1":  "Integrity",
        "164.312e1":  "Transmission security",
        "164.514b":   "De-identification of PHI",
        "164.524":    "Access of individuals to PHI",
    },
}

SYSTEM_PROMPT = """You are a senior GRC (Governance, Risk & Compliance) analyst and information security expert.
Your task is to analyze security/privacy policy documents and produce structured compliance gap analyses.
You MUST return ONLY valid JSON — no markdown, no preamble, no explanations outside the JSON structure.
Be thorough, specific, and actionable. Base your analysis solely on the policy text provided."""


def build_analysis_prompt(policy_text, frameworks, depth, controls):
    depth_instruction = {
        "Quick Scan": "Focus on the most critical gaps only (top 5-8). Be concise.",
        "Standard":   "Provide a balanced analysis covering major gaps (8-15 items).",
        "Deep Dive":  "Be exhaustive - cover all gaps including minor ones (15-25 items).",
    }.get(depth, "Standard")

    controls_json = json.dumps(controls, indent=2)

    return f"""Analyze the following policy document against these compliance frameworks.

FRAMEWORKS AND CONTROLS TO ASSESS:
{controls_json}

POLICY DOCUMENT:
---
{policy_text}
---

DEPTH INSTRUCTION: {depth_instruction}

Return a JSON object with EXACTLY this structure:
{{
  "overall_score": <integer 0-100 representing compliance completeness>,
  "total_controls": <total number of controls assessed>,
  "covered": <number of controls with clear evidence in the policy>,
  "partial": <number of controls with partial coverage>,
  "gaps": [
    {{
      "control_id": "<e.g. PR.AA-01 or A.5.1>",
      "framework": "<framework name>",
      "title": "<concise gap title, max 10 words>",
      "severity": "<Critical|High|Medium|Low>",
      "detail": "<2-3 sentences explaining what is missing or inadequate>",
      "recommendation": "<specific, actionable remediation step in 2-3 sentences>"
    }}
  ],
  "coverage_matrix": [
    {{
      "control_id": "<id>",
      "control_name": "<name>",
      "framework": "<framework>",
      "status": "<Covered|Partial|Missing>",
      "evidence": "<brief note on what was or was not found, max 15 words>"
    }}
  ],
  "remediation_plan": [
    {{
      "action": "<priority action title>",
      "effort": "<Low|Medium|High>",
      "impact": "<Low|Medium|High>",
      "timeline": "<e.g. 1-2 weeks, 1 month, Q3>",
      "detail": "<detailed implementation guidance in 3-4 sentences>",
      "controls_addressed": ["<control_id1>", "<control_id2>"]
    }}
  ]
}}

Sort gaps by severity (Critical first). Sort remediation_plan by impact/effort ratio (quick wins first).
Only include controls from the selected frameworks in the coverage_matrix."""


class ComplianceAnalyzer:
    def __init__(self):
        # Lazy import — only load anthropic when the class is actually used
        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY", "")
            )
        except ImportError:
            self.client = None

    def _build_controls_subset(self, frameworks):
        result = {}
        for fw in frameworks:
            if fw in FRAMEWORKS:
                result[fw] = FRAMEWORKS[fw]
        return result

    def analyze(self, policy_text, frameworks, depth):
        if self.client is None:
            return self._fallback_result(
                frameworks,
                {},
                "anthropic package not installed. Add 'anthropic' to requirements.txt",
            )

        controls = self._build_controls_subset(frameworks)
        prompt = build_analysis_prompt(policy_text, frameworks, depth, controls)

        try:
            response = self.client.messages.create(
                model="claude-opus-4-5",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            return json.loads(raw)

        except json.JSONDecodeError as e:
            return self._fallback_result(frameworks, controls, str(e))
        except Exception as e:
            return self._fallback_result(frameworks, controls, str(e))

    def _fallback_result(self, frameworks, controls, error):
        total = sum(len(v) for v in controls.values()) if controls else 0
        return {
            "overall_score": 0,
            "total_controls": total,
            "covered": 0,
            "partial": 0,
            "gaps": [{
                "control_id": "ERR-001",
                "framework": "System",
                "title": "Analysis failed - check API key",
                "severity": "Critical",
                "detail": f"The AI analysis could not complete. Error: {error[:200]}",
                "recommendation": "Ensure ANTHROPIC_API_KEY is set in Streamlit secrets and anthropic is in requirements.txt",
            }],
            "coverage_matrix": [],
            "remediation_plan": [],
        }
