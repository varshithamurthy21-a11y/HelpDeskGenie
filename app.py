import datetime
import random
import re
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize Memory Store Databases
if "kb_store" not in st.session_state:
    st.session_state.kb_store = [
        {"id": "KB101", "title": "VPN Disconnection and Troubleshooting", "content": "If your Corporate VPN disconnects continuously, flush your DNS by running 'ipconfig /flushdns' in terminal. Verify UDP ports 4500 and 500 are open.", "category": "Networking", "source_link": "Internal Confluence"},
        {"id": "KB102", "title": "Mapping Corporate Network Drives", "content": "Open File Explorer, select 'This PC' -> 'Map network drive'. Input path '\\\\storage.internal\\shared\\departments'. Active VPN connection is required.", "category": "Storage", "source_link": "Internal Confluence"},
        {"id": "KB103", "title": "Outlook Exchange Sync Issues", "content": "Check network connection. Go to File -> Account Settings -> Reset Account. Force rebuilding local OST file data.", "category": "Applications", "source_link": "Internal Confluence"}
    ]

if "ticket_db" not in st.session_state:
    st.session_state.ticket_db = [
        {"ticket_id": "JIRA-4122", "user_id": "user789", "category": "Networking", "status": "Resolved", "description": "VPN dropouts on home wifi"},
        {"ticket_id": "JIRA-5512", "user_id": "user456", "category": "Applications", "status": "Open", "description": "Outlook completely disconnected from host"},
        {"ticket_id": "JIRA-1928", "user_id": "user123", "category": "Identity", "status": "Resolved", "description": "Auto-remediation account unlock verification"}
    ]

if "email_alerts" not in st.session_state:
    st.session_state["email_alerts"] = [
        {"sent_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recipient": "secops-alerts@company.internal", "severity": "CRITICAL HIGH", "subject": "SECURITY VIOLATION: UNLOCK_ACCOUNT Attempt blocked", "body": "The gate controller blocked an unauthorized token request. Context: User tried to bypass AD security gate without providing a valid identity passcode token."}
    ]

if "audit_log" not in st.session_state:
    st.session_state.audit_log = [
        {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d 09:14:22"), "action": "UNLOCK_ACCOUNT", "user_id": "user999", "status": "REJECTED", "details": "Missing Multi-Factor Verification."},
        {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d 10:05:00"), "action": "CREATE_TICKET", "user_id": "user789", "status": "SUCCESS", "details": "Created ticket JIRA-4122"}
    ]

# Core Message Memory Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome back! How can I help you with your IT infrastructure today?"}]

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
            return "❌ SECURITY ERROR: Account unlock rejected. Multi-Factor Identity Verification is missing. An alert has been forwarded to SecOps."
        self.log_action("UNLOCK_ACCOUNT", user_id, "SUCCESS", "Account unlocked via verification flow.")
        return f"✅ SUCCESS: Account for user '{user_id}' has been unlocked in Active Directory."

class SemanticHelpDeskAgent:
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
        if q in ["hi", "hello", "hey", "hi genie"]:
            return "Hello! I am HelpDeskGenie. How can I assist you with your network, account locks, or software systems today?"
        if "unlock" in q:
            verified = "verify" in q or "123456" in q
            return self.tools.unlock_account(user_id, identity_verified=verified)
        elif "log a ticket" in q or "create ticket" in q or "vpn isn't working" in q:
            cat = "Networking" if "vpn" in q else "Applications"
            t_id = self.tools.create_ticket(user_id, cat, user_query)
            return f"🎫 Ticket opened successfully: **{t_id}**."
        kb_record = self._retrieve_kb_semantic(user_query)
        if kb_record is not None:
            return f"### 📖 {kb_record['title']}\n{kb_record['content']}\n\n🔗 Source: {kb_record['source_link']}"
        return "❌ Solution not found in internal runbooks. Would you like me to **log a ticket**?"

# Dashboard Setup Configuration
st.set_page_config(page_title="HelpDeskGenie AI Pro", layout="wide")

# =====================================================================
# 🔐 IDENTITY ACCESS PROFILE GATEWAY & LOGIN FIREWALL
# =====================================================================
st.sidebar.title("👤 Identity Access Profile")

# Password input challenge field
password_input = st.sidebar.text_input("Enter Admin Password to Unlock Metrics Panels", type="password", help="Input admin password token to reveal admin panels.")

if password_input == "admin123":
    user_role = "Administrator"
    current_user_id = "admin_root"
    st.sidebar.success("🔓 Administrative clearance granted.")
else:
    user_role = "Employee"
    current_user_id = "emp_99"
    if password_input != "":
        st.sidebar.error("❌ Invalid Admin Password. Standard Access Active.")
    else:
        st.sidebar.info("Standard Employee view enabled.")

st.sidebar.markdown("---")

# Dynamic Menu Options Matrix mapping access level permissions
if user_role == "Administrator":
    navigation_options = [
        "Chat UI Interface", 
        "IT Admin Dashboard (Stretch Goal)",
        "Automated Evaluation Suite (Iteration 3)",
        "SecOps Dispatch Mailbox"
    ]
else:
    navigation_options = ["Chat UI Interface"]

mode = st.sidebar.selectbox("Navigation Panel View", navigation_options)
agent = SemanticHelpDeskAgent()

# =====================================================================
# INTERFACE MAIN PAGE VIEW ROUTER
# =====================================================================
if mode == "Chat UI Interface":
    st.title("🧞 HelpDeskGenie Chat Gateway")
    st.caption("Active Capabilities: Semantic Confluence RAG Search (Iter 1) & Self-Service Compliance Tools (Iter 2)")
    
    # Render historical conversation message bubbles cleanly on the page layout
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # FIXED: The chat entry text box container is anchored down cleanly right here
    if user_input := st.chat_input("Type your IT support query here (e.g. 'why does my VPN keep disconnecting')..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            response = agent.process_input(user_input, user_id=current_user_id)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

elif mode == "IT Admin Dashboard (Stretch Goal)":
    st.title("📊 IT Operations Command Dashboard")
    df_tickets = pd.DataFrame(st.session_state.ticket_db)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logged Tickets", len(df_tickets))
    col2.metric("Active Open Tickets", len(df_tickets[df_tickets["status"] == "Open"]))
    col3.metric("Auto-Remediation Success", len(df_tickets[df_tickets["status"] == "Resolved"]))
    
    st.markdown("### Active Ticket Tracking Logs")
    st.dataframe(df_tickets, use_container_width=True)
    
    st.markdown("### System Immutable Audit Log Trail")
    st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True)

elif mode == "Automated Evaluation Suite (Iteration 3)":
