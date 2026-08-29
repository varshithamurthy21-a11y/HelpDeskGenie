# 🧞 HelpDeskGenie – Conversational IT Service Desk Assistant

An intelligent, security-first IT support chat engine built with Python and Streamlit. It uses Machine Learning semantic vector processing to query internal runbooks while enforcing corporate security gates for system remediations.

## 🚀 Key Implemented Features
- **Semantic RAG Search:** Leverages scikit-learn TF-IDF Vectorization to process custom text manuals natively.
- **Security Checkpoints:** Blocks high-risk actions (Active Directory account unlocking) unless multi-factor identity parameters pass validation.
- **Incident Escalation:** Falls back to generating a JIRA incident ticket ID if a runbook resolution isn't discovered.
- **SecOps Dashboard Matrix:** Includes a real-time system audit logging panel and a simulated SecOps warning alert outbox.

## 🛠️ Quick Start Instructions
1. Install dependencies:
   ```bash
   pip install streamlit pandas scikit-learn numpy
   ```
2. Run the application interface:
   ```bash
   streamlit run app/app.py
   ```
