import datetime
import random
import re
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =====================================================================
# CORE KNOWLEDGE BASE STORAGE (ITERATION 1 DATA BASELINE)
# =====================================================================
if "kb_store" not in st.session_state:
    st.session_state.kb_store = [
        {"id": "KB101", "title": "VPN Disconnection and Troubleshooting", "content": "If your Corporate VPN disconnects continuously, flush your DNS by running 'ipconfig /flushdns' in terminal. Verify UDP ports 4500 and 500 are open.", "category": "Networking", "source_link": "Internal Confluence"},
        {"id": "KB102", "title": "Mapping Corporate Network Drives", "content": "Open File Explorer, select 'This PC' -> 'Map network drive'. Input path '\\\\storage.internal\\shared\\departments'. Active VPN connection is required.", "category": "Storage", "source_link": "Internal Confluence"},
        {"id": "KB103", "title": "Outlook Exchange Sync Issues", "content": "Check network connection. Go to File -> Account Settings -> Reset Account. Force rebuilding local OST file data.", "category": "Applications", "source_link": "Internal Confluence"}
    ]

# =====================================================================
# SYSTEM IMMUTABLE STATE TRACKING (ITERATION 4 MODULE)
# =====================================================================
# Tracks short-term conversational node contexts across multiple turns
if "current_followup_node" not in st.session_state:
    st.session_state.current_followup_node = None

class SemanticHelpDeskAgent:
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

    def process_input(self, user_query):
        q = user_query.lower().strip()
        
        # -----------------------------------------------------------------
        # 🔄 ITERATION 4 CONVERSATIONAL MEMORY PROCESSING LAYER
        # -----------------------------------------------------------------
        # Check if the agent is actively waiting for a clarification response
        if st.session_state.current_followup_node == "network_vague":
            st.session_state.current_followup_node = None  # Instantly resolve node state
            if "remote" in q or "vpn" in q or "home" in q or "house" in q:
                kb = self._retrieve_kb_semantic("vpn disconnection")
                return f"📋 **Context Resolved (Remote Employee via VPN):**\n\nFollowing your environment data payload context tracking framework, execute this runbook instruction:\n\n{kb['content']}"
            else:
                return "🏢 **Context Resolved (On-Premises Office LAN Network):**\n\nLocal network traffic routers appear active. This typically points to a physical hardware Ethernet cable drop loop. I have updated the active local building triage network queue."

        # Standard baseline conversations
        if q in ["hi", "hello", "hey", "greetings"]:
            return "👋 Hello! I am HelpDeskGenie. How can I assist you with your corporate network parameters today?"

        # -----------------------------------------------------------------
        # 🔍 ITERATION 4 AMBIGUITY INTERCEPTION CORE
        # -----------------------------------------------------------------
        # Catches highly vague text inputs instead of processing incomplete matching calls
        if q in ["network problem", "internet error", "connection dropped", "network issue", "cannot connect"]:
            st.session_state.current_followup_node = "network_vague"  # Engage state lock
            return "🔍 **Genie Iteration 4 Clarification Loop:** I recognized a general system connectivity issue. To extract the exact infrastructure runbook mapping, **are you working remotely from home via VPN, or plugged in natively inside the Corporate Office Network?**"

        # Standard RAG routing fallback
        kb_record = self._retrieve_kb_semantic(user_query)
        if kb_record is not None:
            return f"### 📖 {kb_record['title']}\n{kb_record['content']}\n\n🔗 Source: {kb_record['source_link']}"
            
        return "❌ Solution parameters not found inside baseline memory matrices. Would you like me to log an incident tracking ticket?"

# =====================================================================
# STREAMLIT DISPLAY REGISTRY GATEWAY
# =====================================================================
st.set_page_config(page_title="HelpDeskGenie - Iteration 4", layout="wide")
st.title("🧞 HelpDeskGenie Chat Gateway – Iteration 4 Node")
st.caption("Testing Framework Profile: Multi-Turn State Retention Verification Interface")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Multi-turn context routing memory channels active. Input vague technical queries to verify tracking."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

agent = SemanticHelpDeskAgent()

if user_input := st.chat_input("Input IT environment error..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): 
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        response = agent.process_input(user_input)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
