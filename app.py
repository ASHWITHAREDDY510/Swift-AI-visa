import streamlit as st

# ================= API KEY =================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("🔐 GROQ_API_KEY not found!")
    st.stop()

# ================= CONFIG =================
st.set_page_config(page_title="Visa Eligibility Checker", layout="centered")

# ================= SESSION =================
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

# ================= STYLE =================
st.markdown("""
<style>
.stButton button {
    width: 100%;
    height: 45px;
    font-size: 16px;
    border-radius: 10px;
    background-color: #1f77b4;
    color: white;
    transition: 0.3s;
}
.stButton button:hover {
    background-color: #155a8a;
    transform: scale(1.05);
}
.preview-box {
    background-color: #f8f9fa;
    border: 2px solid #1f77b4;
    border-radius: 10px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Visa Eligibility Checker")

# ================= STEP 0 =================
if st.session_state.step == 0:
    st.subheader("About This App")
    st.markdown("""
    This app checks visa eligibility using AI.

    ⚠️ Fields marked with <span style='color:red'>*</span> are mandatory
    """, unsafe_allow_html=True)

    st.button("Start Application 🚀", on_click=next_step)

# ================= STEP 1 =================
elif st.session_state.step == 1:
    st.subheader("👤 Personal Details")
    data = st.session_state.form_data

    st.markdown("Full Name <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["full_name"] = st.text_input("", value=data["full_name"])

    st.markdown("Nationality <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["nationality"] = st.text_input("", value=data["nationality"])

    st.markdown("Age <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["age"] = st.selectbox("", ["18-25","26-35","36-50","50+"],
        index=["18-25","26-35","36-50","50+"].index(data["age"]) if data["age"] else 0)

    data["gender"] = st.selectbox("Gender", ["Male","Female","Other"])
    data["marital_status"] = st.selectbox("Marital Status", ["Single","Married"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Next ➡️", on_click=next_step)

# ================= STEP 2 =================
elif st.session_state.step == 2:
    st.subheader("✈️ Travel Details")
    data = st.session_state.form_data

    st.markdown("Destination Country <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["country"] = st.text_input("", value=data["country"])

    st.markdown("Visa Type <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["visa_type"] = st.selectbox("", ["Tourist","Work","Student"])

    st.markdown("Purpose <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["purpose"] = st.text_input("", value=data["purpose"])

    # 🔥 Dynamic Fields
    if data["visa_type"] == "Work":
        st.write("### 💼 Employment")
        data["job_title"] = st.text_input("Job Title")
        data["experience"] = st.text_input("Experience")
        data["company_name"] = st.text_input("Company Name")
        data["salary"] = st.text_input("Salary")

    elif data["visa_type"] == "Student":
        st.write("### 🎓 Education")
        data["course"] = st.text_input("Course Name")
        data["university"] = st.text_input("University")

    elif data["visa_type"] == "Tourist":
        st.write("### 🌍 Travel Plan")
        data["travel_plan"] = st.text_input("Travel Plan")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Next ➡️", on_click=next_step)

# ================= STEP 3 =================
elif st.session_state.step == 3:
    st.subheader("💰 Financial & Additional")
    data = st.session_state.form_data

    data["bank_balance"] = st.text_input("Bank Balance")
    data["sponsor"] = st.selectbox("Sponsor", ["Yes","No"])
    data["duration"] = st.selectbox("Duration", ["<1 month","1-6 months","6+ months"])
    data["travel_history"] = st.selectbox("Travel History", ["Yes","No"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Preview ✅", on_click=next_step)

# ================= STEP 4 =================
elif st.session_state.step == 4:
    st.subheader("📋 Review Your Information")
    data = st.session_state.form_data

    st.markdown('<div class="preview-box">', unsafe_allow_html=True)

    st.markdown(f"""
    **Personal Details**  
    Name: {data['full_name']}  
    Nationality: {data['nationality']}  
    Age: {data['age']}  
    Gender: {data['gender']}  

    **Travel Details**  
    Country: {data['country']}  
    Visa Type: {data['visa_type']}  
    Purpose: {data['purpose']}

    **Financial**  
    Balance: {data['bank_balance']}  
    Sponsor: {data['sponsor']}
    """)

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("✏️ Edit", on_click=prev_step)
    with col2:
        st.button("Get Result 🚀", on_click=next_step)

# ================= STEP 5 =================
elif st.session_state.step == 5:
    st.subheader("📊 Result")
    data = st.session_state.form_data

    from rag_pipeline import RAGPipeline

    with st.spinner("🤖 AI analyzing..."):
        import time
        progress = st.progress(0)

        for i in range(100):
            time.sleep(0.01)
            progress.progress(i+1)

        rag = RAGPipeline(top_k=3)
        result = rag.query_with_sources(
            f"Eligibility for {data['visa_type']} visa to {data['country']}",
            user_profile=data
        )

        progress.empty()

    st.balloons()

    st.write(result["response"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("Restart 🔄", on_click=reset_app)
    with col2:
        st.button("Ask AI 🤖", on_click=lambda: setattr(st.session_state,"step",6))

# ================= STEP 6 =================
elif st.session_state.step == 6:
    st.subheader("💬 Ask AI")

    query = st.text_input("Ask your question")

    if st.button("Get Answer"):
        st.write("AI response here")

    st.button("⬅️ Back", on_click=lambda: setattr(st.session_state,"step",5))