import datetime
import random
import re
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
if "kb_store" not in st.session_state:
    st.session_state.kb_store = [
        {"id": "KB101", "title": "VPN Disconnection and Troubleshooting", "content": "If your Corporate VPN disconnects continuously, flush your DNS by running 'ipconfig /flushdns' in terminal. Verify UDP ports 4500 and 500 are open.", "category": "Networking", "source_link": "Internal Confluence"},
        {"id": "KB102", "title": "Mapping Corporate Network Drives", "content": "Open File Explorer, select 'This PC' -> 'Map network drive'. Input path '\\\\storage.internal\\shared\\departments'. Active VPN connection is required.", "category": "Storage", "source_link": "Internal Confluence"},
        {"id": "KB103", "title": "Outlook Exchange Sync Issues", "content": "Check network connection. Go to File -> Account Settings -> Reset Account. Force rebuilding local OST file data.", "category": "Applications", "source_link": "Internal Confluence"}
    ]

if "ticket_db" not in st.session_state:
    st.session_state.ticket_db = [
        {"ticket_id": "JIRA-4122", "user_id": "emp_45", "category": "Networking", "status": "Resolved", "description": "VPN dropouts on home wifi"},
        {"ticket_id": "JIRA-5512", "user_id": "emp_12", "category": "Applications", "status": "Open", "description": "Outlook completely disconnected from host"},
        {"ticket_id": "JIRA-1928", "user_id": "user123", "category": "Identity", "status": "Resolved", "description": "Auto-remediation account unlock verification"}
    ]

if "email_alerts" not in st.session_state:
    st.session_state["email_alerts"] = [
        {"sent_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recipient": "secops-alerts@company.internal", "severity": "CRITICAL HIGH", "subject": "SECURITY VIOLATION: UNLOCK_ACCOUNT Attempt blocked", "body": "The gate controller blocked an unauthorized token request. Context: User tried to bypass AD security gate without providing a valid identity passcode token."}
    ]

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "current_followup_node" not in st.session_state:
    st.session_state.current_followup_node = None

if "user_role" not in st.session_state:
    st.session_state.user_role = "Employee"
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = "emp_99"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat UI Interface"
class ITSMTools:
    def log_action(self, action_name, user_id, status, details):
        log_entry = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": action_name, "user_id": user_id, "status": status, "details": details}
        st.session_state.audit_log.append(log_entry)
        return log_entry

    def dispatch_secops_email(self, user_id, action_name, details):
        alert_entry = {"sent_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recipient": "secops-alerts@company.internal", "severity": "CRITICAL HIGH", "subject": f"SECURITY VIOLATION: {action_name} by {user_id}", "body": f"The gate controller blocked an unauthorized token request. Context: {details}"}
        st.session_state["email_alerts"].insert(0, alert_entry)

    def create_ticket(self, user_id, category, description):
        ticket_id = f"JIRA-{random.randint(6000, 9999)}"
        st.session_state.ticket_db.append({"ticket_id": ticket_id, "user_id": user_id, "category": category, "status": "Open", "description": description})
        self.log_action("CREATE_TICKET", user_id, "SUCCESS", f"Created ticket {ticket_id}")
        return ticket_id

    def unlock_account(self, user_id, identity_verified=False):
        if not identity_verified:
            self.log_action("UNLOCK_ACCOUNT", user_id, "REJECTED", "Missing Multi-Factor Verification.")
            self.dispatch_secops_email(user_id, "UNLOCK_ACCOUNT", f"User '{user_id}' attempted account unlock without passing identity verification step.")
            return "SECURITY ERROR: Account unlock rejected. Multi-Factor Identity Verification is missing. An alert has been forwarded to SecOps."
        self.log_action("UNLOCK_ACCOUNT", user_id, "SUCCESS", "Account unlocked via verification flow.")
        return f"SUCCESS: Account for user '{user_id}' has been unlocked in Active Directory."

class AdvancedHelpDeskAgent:
    def __init__(self):
        self.tools = ITSMTools()
        
    def _retrieve_kb_semantic(self, query):
        if not st.session_state.kb_store:
            return None
        corpus = [f"{item['title']} {item['content']}" for item in st.session_state.kb_store]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vector = vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        best_match_idx = np.argmax(similarities)
        if similarities[best_match_idx] > 0.15:
            return st.session_state.kb_store[best_match_idx]
        return None

    def process_input(self, user_query, user_id="user123"):
        q = user_query.lower().strip()
        
        if st.session_state.current_followup_node == "network_vague":
            st.session_state.current_followup_node = None
            if "remote" in q or "vpn" in q or "home" in q:
                kb = self._retrieve_kb_semantic("vpn disconnection")
                return f"📋 **Context Confirmed: Remote Worker via VPN**\n\nHere is your runbook instructions:\n\n{kb['content']}"
            else:
                return "🏢 **Context Confirmed: Office Local Network Base LAN**\n\nPlease check if your physical ethernet cables are secure. A campus infrastructure alert ticket has been filed."

        if q in ["hi", "hello", "hey", "hi genie"]:
            return "Hello! I am HelpDeskGenie. How can I assist you with your network, account locks, or software systems today?"
        if "unlock" in q:
            verified = "verify" in q or "123456" in q
            return self.tools.unlock_account(user_id, identity_verified=verified)
        elif "log a ticket" in q or "create ticket" in q or "vpn isn't working" in q:
            cat = "Networking" if "vpn" in q else "Applications"
            t_id = self.tools.create_ticket(user_id, cat, user_query)
            return f"Ticket opened successfully: {t_id}."
            
        if q in ["network problem", "internet error", "connection dropped", "network issue"]:
            st.session_state.current_followup_node = "network_vague"
            return "🔍 **Genie Clarification Node:** I detected a general connectivity problem. To provide the correct troubleshooting manual, **are you working remotely from home on the VPN, or are you physically at the corporate office network?**"

        kb_record = self._retrieve_kb_semantic(user_query)
        if kb_record is not None:
            return f"### {kb_record['title']}\n{kb_record['content']}\n\nSource: {kb_record['source_link']}"
            
        return "Solution not found in internal runbooks. Would you like me to log a ticket?"

# UI Page Config
st.set_page_config(page_title="HelpDeskGenie AI Pro", layout="wide")

# --- SIDEBAR INTERFACE ---
st.sidebar.title("👤 User Authentication Profile")
st.sidebar.write(f"Logged in as: **{st.session_state.current_user_id}**")
st.sidebar.write(f"Access Level Clearance: **{st.session_state.user_role}**")

auth_input = st.sidebar.text_input("Enter Admin Password to Unlock Metrics", type="password")
if auth_input == "admin123":
    st.session_state.user_role = "Administrator"
    st.session_state.current_user_id = "admin_root"
    st.sidebar.success("🔓 Administrative clearance granted.")
else:
    st.session_state.user_role = "Employee"
    st.session_state.current_user_id = "emp_99"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Navigation Menu")

# ⚡ BULLETPROOF BUTTON NAVIGATION SYSTEM TO KILL STATE BUG COMPLETELY ⚡
if st.sidebar.button("💬 Chat UI Interface", use_container_width=True):
    st.session_state.current_page = "Chat UI Interface"

if st.sidebar.button("🧪 Automated Evaluation Suite (Iteration 3)", use_container_width=True):
    st.session_state.current_page = "Automated Evaluation"

if st.session_state.user_role == "Administrator":
    if st.sidebar.button("📊 IT Admin Dashboard (Stretch Goal)", use_container_width=True):
        st.session_state.current_page = "Admin Dashboard"
    if st.sidebar.button("📬 SecOps Dispatch Mailbox", use_container_width=True):
        st.session_state.current_page = "SecOps Mailbox"
    if st.sidebar.button("🔌 Iteration 6: Webhook Live Payload Monitor", use_container_width=True):
        st.session_state.current_page = "Webhook Monitor"

agent = AdvancedHelpDeskAgent()
mode = st.session_state.current_page

# --- CONTROLLER RENDERING LAYER ---
if mode == "Chat UI Interface":
    st.title("🧞 HelpDeskGenie Chat Gateway")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with your IT infrastructure today?"}]
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if user_input := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)
