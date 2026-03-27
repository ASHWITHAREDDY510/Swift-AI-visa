import streamlit as st
from dotenv import load_dotenv
import os

# ================= CONFIG =================
st.set_page_config(page_title="Visa Eligibility Checker", layout="centered")

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
.stButton button {
    width: 100%;
    height: 45px;
    font-size: 16px;
    border-radius: 10px;
    border: none;
    background-color: #1f77b4;
    color: white;
}
.stButton button:hover {
    background-color: #155a8a;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.title("🌍 Visa Eligibility Checker")

# ================= STEP 0 =================
if st.session_state.step == 0:
    st.subheader("About This App")
    st.write("This app checks visa eligibility using AI.")
    st.button("Start Application", use_container_width=True, on_click=next_step)

# ================= STEP 1 =================
elif st.session_state.step == 1:
    st.subheader("👤 Personal Details")
    data = st.session_state.form_data

    data["full_name"] = st.text_input("Full Name", value=data["full_name"])
    data["nationality"] = st.text_input("Nationality", value=data["nationality"])

    data["age"] = st.selectbox("Age", ["18-25","26-35","36-50","50+"],
        index=0 if not data["age"] else ["18-25","26-35","36-50","50+"].index(data["age"]))

    data["gender"] = st.selectbox("Gender", ["Male","Female","Other"],
        index=0 if not data["gender"] else ["Male","Female","Other"].index(data["gender"]))

    data["marital_status"] = st.selectbox("Marital Status", ["Single","Married"],
        index=0 if not data["marital_status"] else ["Single","Married"].index(data["marital_status"]))

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Next ➡️", use_container_width=True, on_click=next_step)

# ================= STEP 2 =================
elif st.session_state.step == 2:
    st.subheader("✈️ Travel & Employment Details")
    data = st.session_state.form_data

    data["country"] = st.text_input("Destination Country", value=data["country"])

    data["visa_type"] = st.selectbox("Visa Type", ["Tourist","Work","Student"],
        index=0 if not data["visa_type"] else ["Tourist","Work","Student"].index(data["visa_type"]))

    data["purpose"] = st.text_input("Purpose", value=data["purpose"])

    st.write("### 💼 Employment")

    data["job_title"] = st.text_input("Job Title", value=data["job_title"])
    data["experience"] = st.text_input("Years of Experience", value=data["experience"])
    data["company_name"] = st.text_input("Company Name", value=data["company_name"])
    data["salary"] = st.text_input("Salary", value=data["salary"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Next ➡️", use_container_width=True, on_click=next_step)

# ================= STEP 3 =================
elif st.session_state.step == 3:
    st.subheader("💰 Financial & Additional Info")
    data = st.session_state.form_data

    data["bank_balance"] = st.text_input("Bank Balance", value=data["bank_balance"])

    data["sponsor"] = st.selectbox("Sponsor Available", ["Yes","No"],
        index=0 if not data["sponsor"] else ["Yes","No"].index(data["sponsor"]))

    data["duration"] = st.selectbox("Duration", ["<1 month","1-6 months","6+ months"],
        index=0 if not data["duration"] else ["<1 month","1-6 months","6+ months"].index(data["duration"]))

    data["travel_history"] = st.selectbox("Travel History", ["Yes","No"],
        index=0 if not data["travel_history"] else ["Yes","No"].index(data["travel_history"]))

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Preview ✅", use_container_width=True, on_click=next_step)

# ================= STEP 4 =================
elif st.session_state.step == 4:
    st.subheader("📋 Preview")
    data = st.session_state.form_data

    for key, value in data.items():
        st.write(f"**{key.replace('_',' ').title()}:** {value}")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Edit", use_container_width=True, on_click=prev_step)
    with col2:
        st.button("Get Result 🚀", use_container_width=True, on_click=next_step)

# ================= STEP 5 =================
elif st.session_state.step == 5:
    st.subheader("📊 Result")
    data = st.session_state.form_data

    # simple logic
    try:
        balance = int(data["bank_balance"])
    except:
        balance = 0

    if balance > 5000 and data["travel_history"] == "Yes":
        st.success("✅ High Chance")
    else:
        st.warning("⚠️ Moderate Chance")

    st.write("### 🧠 Explanation")
    st.write("Eligibility depends on financial strength, travel history, and purpose.")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Restart 🔄", use_container_width=True, on_click=reset_app)
    with col2:
        st.button("Ask AI 🤖", use_container_width=True, on_click=lambda: setattr(st.session_state, "step", 6))

# ================= STEP 6 =================
elif st.session_state.step == 6:
    st.subheader("💬 Ask AI")
    data = st.session_state.form_data

    user_query = st.text_input("Ask question")

    if st.button("Get Answer"):
        st.write("AI response will come here (connect RAG)")

    st.button("⬅️ Back", use_container_width=True, on_click=lambda: setattr(st.session_state, "step", 5))