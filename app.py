import streamlit as st

# ================= API KEY =================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("🔐 GROQ_API_KEY not found!")
    st.info("Please add it in Streamlit → Settings → Secrets")
    st.stop()

# ================= CONFIG =================
st.set_page_config(page_title="Visa Eligibility Checker", layout="centered")

# ================= SESSION STATE =================
if "step" not in st.session_state:
    st.session_state.step = 0

if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "full_name": "",
        "nationality": "",
        "age": "",
        "gender": "",
        "marital_status": "",
        "country": "",
        "visa_type": "",
        "purpose": "",
        "job_title": "",
        "experience": "",
        "company_name": "",
        "salary": "",
        "bank_balance": "",
        "sponsor": "",
        "duration": "",
        "travel_history": ""
    }

if "rag_result" not in st.session_state:
    st.session_state.rag_result = None

if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================= FUNCTIONS =================
def next_step():
    st.session_state.step += 1

def prev_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1

def reset_app():
    st.session_state.step = 0
    for key in st.session_state.form_data:
        st.session_state.form_data[key] = ""
    st.session_state.rag_result = None
    st.session_state.chat_history = []

# ================= STYLING =================
st.markdown("""
<style>
.stButton button { width: 100%; height: 45px; font-size: 16px; border-radius: 10px; border: none; background-color: #1f77b4; color: white; }
.stButton button:hover { background-color: #155a8a; }
.preview-box { background-color: #f8f9fa; border: 2px solid #1f77b4; border-radius: 10px; padding: 20px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🌍 Visa Eligibility Checker")

# ================= STEP 0 =================
if st.session_state.step == 0:
    st.subheader("About This App")

    st.markdown("""
    ### 🌍 Smart Visa Eligibility System

    This application helps users check visa eligibility using AI.

    **How it works:**
    - Fill personal & travel details  
    - Get AI-based eligibility  
    - Ask questions via chatbot  

    ⚠️ Fields marked with <span style='color:red'>*</span> are mandatory
    """, unsafe_allow_html=True)

    st.button("Start Application 🚀", use_container_width=True, on_click=next_step)

# ================= STEP 1 =================
elif st.session_state.step == 1:
    st.subheader("👤 Personal Details")
    data = st.session_state.form_data

    data["full_name"] = st.text_input("Full Name <span style='color:red'>*</span>", value=data["full_name"], key="s1_name")
    data["nationality"] = st.text_input("Nationality <span style='color:red'>*</span>", value=data["nationality"], key="s1_nat")

    data["age"] = st.selectbox("Age Range <span style='color:red'>*</span>", ["18-25","26-35","36-50","50+"],
        index=["18-25","26-35","36-50","50+"].index(data["age"]) if data["age"] else 0)

    data["gender"] = st.selectbox("Gender", ["Male","Female","Other"],
        index=["Male","Female","Other"].index(data["gender"]) if data["gender"] else 0)

    data["marital_status"] = st.selectbox("Marital Status", ["Single","Married"],
        index=["Single","Married"].index(data["marital_status"]) if data["marital_status"] else 0)

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Next ➡️", on_click=next_step)

# ================= STEP 2 =================
elif st.session_state.step == 2:
    st.subheader("✈️ Travel Details")
    data = st.session_state.form_data

    data["country"] = st.text_input("Destination Country <span style='color:red'>*</span>", value=data["country"], key="s2_country")

    data["visa_type"] = st.selectbox("Visa Type <span style='color:red'>*</span>", ["Tourist","Work","Student"],
        index=["Tourist","Work","Student"].index(data["visa_type"]) if data["visa_type"] else 0)

    data["purpose"] = st.text_input("Purpose <span style='color:red'>*</span>", value=data["purpose"], key="s2_purpose")

    # 🔥 Dynamic Fields
    if data["visa_type"] == "Work":
        st.write("### 💼 Employment Details")
        data["job_title"] = st.text_input("Job Title", value=data["job_title"])
        data["experience"] = st.text_input("Experience", value=data["experience"])
        data["company_name"] = st.text_input("Company Name", value=data["company_name"])
        data["salary"] = st.text_input("Salary", value=data["salary"])

    elif data["visa_type"] == "Student":
        st.write("### 🎓 Education Details")
        data["course"] = st.text_input("Course Name", value=data.get("course",""))
        data["university"] = st.text_input("University", value=data.get("university",""))

    elif data["visa_type"] == "Tourist":
        st.write("### 🌍 Travel Info")
        data["travel_plan"] = st.text_input("Travel Plan", value=data.get("travel_plan",""))

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Next ➡️", on_click=next_step)

# ================= STEP 3 =================
elif st.session_state.step == 3:
    st.subheader("💰 Financial & Additional Info")
    data = st.session_state.form_data

    data["bank_balance"] = st.text_input("Bank Balance", value=data["bank_balance"])

    data["sponsor"] = st.selectbox("Sponsor Available", ["Yes","No"],
        index=["Yes","No"].index(data["sponsor"]) if data["sponsor"] else 0)

    data["duration"] = st.selectbox("Duration", ["<1 month","1-6 months","6+ months"],
        index=["<1 month","1-6 months","6+ months"].index(data["duration"]) if data["duration"] else 0)

    data["travel_history"] = st.selectbox("Travel History", ["Yes","No"],
        index=["Yes","No"].index(data["travel_history"]) if data["travel_history"] else 0)

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Preview & Confirm ✅", on_click=next_step)

# ================= STEP 4 =================
elif st.session_state.step == 4:
    st.subheader("📋 Preview")
    data = st.session_state.form_data

    st.markdown('<div class="preview-box">', unsafe_allow_html=True)

    for key, value in data.items():
        st.write(f"**{key.replace('_',' ').title()}:** {value}")

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Edit", on_click=prev_step)
    with col2:
        st.button("Get Result 🚀", on_click=next_step)

# ================= STEP 5 =================
elif st.session_state.step == 5:
    st.subheader("📊 Visa Eligibility Result")
    data = st.session_state.form_data

    if st.session_state.rag_result is None:
        from rag_pipeline import RAGPipeline
        st.session_state.rag_pipeline = RAGPipeline(top_k=3)

        query = f"Eligibility for {data['visa_type']} visa to {data['country']}"
        st.session_state.rag_result = st.session_state.rag_pipeline.query_with_sources(
            query,
            user_profile=data,
            destination_country=data['country']
        )

    result = st.session_state.rag_result

    if "ELIGIBLE" in result["status"]:
        st.success("✅ High Visa Approval Chances")
    elif "PARTIALLY" in result["status"]:
        st.warning("⚠️ Moderate Visa Approval Chances")
    else:
        st.error("❌ Low Visa Approval Chances")

    st.write("### 🧠 AI Assessment")
    st.write(result["response"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("Restart 🔄", on_click=reset_app)
    with col2:
        st.button("Ask AI 🤖", on_click=lambda: setattr(st.session_state, "step", 6))

# ================= STEP 6 =================
elif st.session_state.step == 6:
    st.subheader("💬 Ask Visa Questions")

    user_query = st.text_input("Ask your question")

    if st.button("Get Answer"):
        st.write("AI response will appear here")

    st.button("⬅️ Back", on_click=lambda: setattr(st.session_state, "step", 5))