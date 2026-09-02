import streamlit as st

# Initialize session state for login tracking
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🧞 HelpDeskGenie Gateway Login")
    
    # Segment the login pathways clearly
    login_type = st.radio("Select Account Type:", ["Standard User Portal", "IT Admin Portal"])
    
    username = st.text_input("Username / Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        if login_type == "Standard User Portal":
            # Simple demo check for standard users
            if username == "user" and password == "password":
                st.session_state.logged_in = True
                st.session_state.user_role = "User"
                st.rerun()
            else:
                st.error("Invalid user credentials.")
                
        elif login_type == "IT Admin Portal":
            # Simple demo check for administrators
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_role = "Admin"
                st.rerun()
            else:
                st.error("Invalid admin credentials.")

# --- APPLICATON APP CONTENT (Logged In) ---
else:
    # Add a logout button to the sidebar
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

    # --- DYNAMIC NAVIGATION PANEL BASED ON ROLE ---
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user_role}")
    
    if st.session_state.user_role == "Admin":
        # Admins can see EVERYTHING
        page = st.sidebar.radio("Navigation Panel", [
            "Chat UI Interface", 
            "IT Admin Dashboard (Stretch Goal)", 
            "Automated Evaluation Suite (Iteration 3)", 
            "SecOps Dispatch Mailbox"
        ])
    else:
        # Standard Users are strictly restricted to the support chat
        page = st.sidebar.radio("Navigation Panel", [
            "Chat UI Interface"
        ])

    # --- RENDER PAGES ---
    if page == "Chat UI Interface":
        st.title("🧞 HelpDeskGenie Chat Gateway")
        st.write("Welcome back! How can I help you with your IT Infrastructure today?")
        # [Insert your current Chat UI code here]
        
    elif page == "IT Admin Dashboard (Stretch Goal)":
        st.title("📊 IT Admin Dashboard")
        # [Insert your Dashboard code here]
        
    elif page == "Automated Evaluation Suite (Iteration 3)":
        st.title("🧪 Automated Evaluation Suite")
        # [Insert your Evaluation Pipeline code here]
        
    elif page == "SecOps Dispatch Mailbox":
        st.title("🚨 SecOps Dispatch Mailbox")
        # [Insert your SecOps code here]
