import streamlit as st

# ✅ FIX: Use Streamlit Secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("🔐 GROQ_API_KEY not found!")
    st.info("Please add it in Streamlit → Settings → Secrets")
    st.stop()

st.set_page_config(page_title="Visa Eligibility Checker", layout="centered")
if "step" not in st.session_state:
    st.session_state.step = 0
if "form_data" not in st.session_state:
    st.session_state.form_data = {"nationality": "", "age": "", "country": "", "visa_type": "", "purpose": "", "duration": "", "travel_history": ""}
if "rag_result" not in st.session_state:
    st.session_state.rag_result = None
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def next_step():
    st.session_state.step += 1

def prev_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

def reset_app():
    st.session_state.step = 0
    st.session_state.form_data = {"nationality": "", "age": "", "country": "", "visa_type": "", "purpose": "", "duration": "", "travel_history": ""}
    st.session_state.rag_result = None
    st.session_state.rag_pipeline = None
    st.session_state.chat_history = []

st.markdown("""
<style>
.stButton button { width: 100%; height: 45px; font-size: 16px; border-radius: 10px; border: none; background-color: #1f77b4; color: white; }
.stButton button:hover { background-color: #155a8a; }
.preview-box { background-color: #f8f9fa; border: 2px solid #1f77b4; border-radius: 10px; padding: 20px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🌍 Visa Eligibility Checker")

# STEP 0: About
if st.session_state.step == 0:
    st.subheader("About This App")
    st.write("""
    This app checks visa eligibility using AI-powered technology.
    
    **How it works:**
    1. Fill in your personal & travel details
    2. Preview and confirm your information
    3. Get AI-powered eligibility assessment
    
    **Fields marked with * are required**
    """)
    st.button("Start Application", use_container_width=True, on_click=next_step)

# STEP 1: Personal Details
elif st.session_state.step == 1:
    st.subheader("👤 Personal Details")
    st.markdown("*Required fields")
    data = st.session_state.form_data
    data["nationality"] = st.text_input("Nationality *", value=data["nationality"], key="s1_nat")
    data["age"] = st.selectbox("Age Range *", ["18-25", "26-35", "36-50", "50+"], index=["18-25", "26-35", "36-50", "50+"].index(data["age"]) if data["age"] in ["18-25", "26-35", "36-50", "50+"] else 0, key="s1_age")
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Next ➡️", use_container_width=True, on_click=next_step)

# STEP 2: Travel Details
elif st.session_state.step == 2:
    st.subheader("✈️ Travel Details")
    st.markdown("*Required fields")
    data = st.session_state.form_data
    data["country"] = st.text_input("Destination Country *", value=data["country"], key="s2_country")
    data["visa_type"] = st.selectbox("Visa Type *", ["Tourist", "Work", "Student"], index=["Tourist", "Work", "Student"].index(data["visa_type"]) if data["visa_type"] in ["Tourist", "Work", "Student"] else 0, key="s2_visa")
    data["purpose"] = st.text_input("Purpose of Travel *", value=data["purpose"], key="s2_purpose")
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Next ➡️", use_container_width=True, on_click=next_step)

# STEP 3: Additional Info
elif st.session_state.step == 3:
    st.subheader("📄 Additional Info")
    st.markdown("*Required fields")
    data = st.session_state.form_data
    data["duration"] = st.selectbox("Planned Duration *", ["<1 month", "1-6 months", "6+ months"], index=["<1 month", "1-6 months", "6+ months"].index(data["duration"]) if data["duration"] in ["<1 month", "1-6 months", "6+ months"] else 0, key="s3_duration")
    data["travel_history"] = st.selectbox("Travel History *", ["Yes", "No"], index=["Yes", "No"].index(data["travel_history"]) if data["travel_history"] in ["Yes", "No"] else 0, key="s3_history")
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Preview & Confirm ✅", use_container_width=True, on_click=next_step)

# STEP 4: Preview & Edit
elif st.session_state.step == 4:
    st.subheader("📋 Preview Your Information")
    st.markdown("Please review your details before proceeding. You can edit any field below.")
    
    data = st.session_state.form_data
    
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    
    st.write("### 👤 Personal Details")
    col1, col2 = st.columns(2)
    with col1:
        data["nationality"] = st.text_input("Nationality *", value=data["nationality"], key="edit_nat")
        data["age"] = st.selectbox("Age Range *", ["18-25", "26-35", "36-50", "50+"], index=["18-25", "26-35", "36-50", "50+"].index(data["age"]) if data["age"] in ["18-25", "26-35", "36-50", "50+"] else 0, key="edit_age")
    with col2:
        data["country"] = st.text_input("Destination Country *", value=data["country"], key="edit_country")
        data["visa_type"] = st.selectbox("Visa Type *", ["Tourist", "Work", "Student"], index=["Tourist", "Work", "Student"].index(data["visa_type"]) if data["visa_type"] in ["Tourist", "Work", "Student"] else 0, key="edit_visa")
    
    st.write("### ✈️ Travel Information")
    col1, col2 = st.columns(2)
    with col1:
        data["purpose"] = st.text_input("Purpose of Travel *", value=data["purpose"], key="edit_purpose")
        data["duration"] = st.selectbox("Planned Duration *", ["<1 month", "1-6 months", "6+ months"], index=["<1 month", "1-6 months", "6+ months"].index(data["duration"]) if data["duration"] in ["<1 month", "1-6 months", "6+ months"] else 0, key="edit_duration")
    with col2:
        data["travel_history"] = st.selectbox("Travel History *", ["Yes", "No"], index=["Yes", "No"].index(data["travel_history"]) if data["travel_history"] in ["Yes", "No"] else 0, key="edit_history")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info(f"💡 AI will assess your eligibility for **{data['country']} {data['visa_type']} Visa** only.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Get Eligibility Result 🚀", use_container_width=True, type="primary", on_click=next_step)

# STEP 5: Results (CLEAN - No User Profile)
elif st.session_state.step == 5:
    st.subheader("📊 Visa Eligibility Result")
    data = st.session_state.form_data
    
    # AI Analysis
    if st.session_state.rag_result is None:
        with st.spinner(f"🤖 AI Analyzing {data['country']} {data['visa_type']} Visa Eligibility..."):
            try:
                from rag_pipeline import RAGPipeline
                if st.session_state.rag_pipeline is None:
                    st.session_state.rag_pipeline = RAGPipeline(top_k=3)
                
                query = f"Eligibility requirements for {data['visa_type']} visa to {data['country']}"
                st.session_state.rag_result = st.session_state.rag_pipeline.query_with_sources(
                    query, 
                    user_profile=data,
                    destination_country=data['country']
                )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                col1, col2 = st.columns(2)
                with col1:
                    st.button("⬅️ Back to Edit", use_container_width=True, on_click=lambda: setattr(st.session_state, 'step', 4))
                with col2:
                    st.button("Restart 🔄", use_container_width=True, on_click=reset_app)
                st.stop()
    
    result = st.session_state.rag_result
    
    # Status Badge ONLY (No user profile summary)
    st.write("### 🎯 Eligibility Status")
    if "ELIGIBLE" in result.get("status", "").upper():
        st.success("✅ High Visa Approval Chances")
    elif "PARTIALLY" in result.get("status", "").upper():
        st.warning("⚠️ Moderate Visa Approval Chances")
    elif "NOT ELIGIBLE" in result.get("status", "").upper():
        st.error("❌ Low Visa Approval Chances")
    else:
        st.info("ℹ️ Assessment Below")
    
    # AI Explanation ONLY (No sources, no user profile)
    st.write("### 🧠 AI Eligibility Assessment")
    st.write(result.get("response", "No explanation available"))
    
    st.divider()
    
    # Action Buttons ONLY
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("⬅️ Edit Info", use_container_width=True, on_click=lambda: setattr(st.session_state, 'step', 4))
    with col2:
        st.button("Restart 🔄", use_container_width=True, on_click=reset_app)
    with col3:
        st.button("Ask AI 🤖", use_container_width=True, type="primary", on_click=lambda: setattr(st.session_state, 'step', 6))

# STEP 6: AI Chat (Optional)
elif st.session_state.step == 6:
    st.subheader("💬 Ask Visa Questions")
    data = st.session_state.form_data
    st.info(f"📋 Context: {data['visa_type']} Visa for {data['country']}")
    
    if st.session_state.rag_pipeline is None:
        from rag_pipeline import RAGPipeline
        st.session_state.rag_pipeline = RAGPipeline(top_k=3)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history:
        st.write(f"**{'👤 You' if msg['role']=='user' else '🤖 AI'}:** {msg['content']}")
    
    st.divider()
    user_query = st.text_input("Ask your question", key="chat_q")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get Answer 🤖", use_container_width=True) and user_query:
            with st.spinner("Thinking..."):
                result = st.session_state.rag_pipeline.query_with_sources(
                    f"Question: {user_query}", 
                    user_profile=data,
                    destination_country=data['country']
                )
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                st.session_state.chat_history.append({"role": "assistant", "content": result.get("response", "No response")})
                st.rerun()
    with col2:
        if st.button("⬅️ Back to Results", use_container_width=True):
            st.session_state.step = 5
            st.rerun()