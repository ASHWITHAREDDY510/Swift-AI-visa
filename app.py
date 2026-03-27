import streamlit as st

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
    ### 🌍 Smart Visa Eligibility System

    This app helps users:
    - Check visa eligibility  
    - Understand required documents  
    - Get AI-based guidance  

    ⚠️ Fields marked with <span style='color:red'>*</span> are mandatory
    """, unsafe_allow_html=True)

    st.button("Start Application 🚀", on_click=next_step)

# ================= STEP 1 =================
elif st.session_state.step == 1:
    st.subheader("👤 Personal Details")
    data = st.session_state.form_data

    st.markdown("Full Name <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["full_name"] = st.text_input("full_name", value=data["full_name"], key="full_name")

    st.markdown("Nationality <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["nationality"] = st.text_input("nationality", value=data["nationality"], key="nationality")

    st.markdown("Age <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["age"] = st.selectbox("age", ["18-25","26-35","36-50","50+"], key="age")

    data["gender"] = st.selectbox("Gender", ["Male","Female","Other"], key="gender")
    data["marital_status"] = st.selectbox("Marital Status", ["Single","Married"], key="marital")

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
    data["country"] = st.text_input("country", value=data["country"], key="country")

    st.markdown("Visa Type <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["visa_type"] = st.selectbox("visa", ["Tourist","Work","Student"], key="visa")

    st.markdown("Purpose <span style='color:red'>*</span>", unsafe_allow_html=True)
    data["purpose"] = st.text_input("purpose", value=data["purpose"], key="purpose")

    # Dynamic fields
    if data["visa_type"] == "Work":
        st.write("### 💼 Employment")
        data["job_title"] = st.text_input("Job Title", key="job")
        data["experience"] = st.text_input("Experience", key="exp")
        data["company_name"] = st.text_input("Company Name", key="company")
        data["salary"] = st.text_input("Salary", key="salary")

    elif data["visa_type"] == "Student":
        st.write("### 🎓 Education")
        data["course"] = st.text_input("Course", key="course")
        data["university"] = st.text_input("University", key="uni")

    elif data["visa_type"] == "Tourist":
        st.write("### 🌍 Travel Plan")
        data["travel_plan"] = st.text_input("Plan", key="plan")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Next ➡️", on_click=next_step)

# ================= STEP 3 =================
elif st.session_state.step == 3:
    st.subheader("💰 Financial Info")
    data = st.session_state.form_data

    data["bank_balance"] = st.text_input("Bank Balance", key="balance")
    data["sponsor"] = st.selectbox("Sponsor", ["Yes","No"], key="sponsor")
    data["duration"] = st.selectbox("Duration", ["<1 month","1-6 months","6+ months"], key="duration")
    data["travel_history"] = st.selectbox("Travel History", ["Yes","No"], key="history")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    with col2:
        st.button("Preview", on_click=next_step)

# ================= STEP 4 =================
elif st.session_state.step == 4:
    st.subheader("📋 Review")

    data = st.session_state.form_data

    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.write(data)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("Edit", on_click=prev_step)
    with col2:
        st.button("Submit", on_click=next_step)