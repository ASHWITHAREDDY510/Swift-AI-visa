def query_with_sources(self, query: str, user_profile: dict = None, destination_country: str = None) -> dict:

    retrieved_docs = self.retrieve(query)

    if retrieved_docs:
        context = "\n\n".join([doc["content"] for doc in retrieved_docs])
    else:
        context = "No policy documents available. Provide general visa guidance."

    # 🔥 NEW: Inject user profile into prompt
    user_info = ""
    if user_profile:
        user_info = f"""
User Profile:
- Full Name: {user_profile.get('full_name')}
- Nationality: {user_profile.get('nationality')}
- Age: {user_profile.get('age')}
- Gender: {user_profile.get('gender')}
- Marital Status: {user_profile.get('marital_status')}
- Destination: {user_profile.get('country')}
- Visa Type: {user_profile.get('visa_type')}
- Purpose: {user_profile.get('purpose')}

Employment:
- Job Title: {user_profile.get('job_title')}
- Experience: {user_profile.get('experience')}
- Company: {user_profile.get('company_name')}
- Salary: {user_profile.get('salary')}

Financial:
- Bank Balance: {user_profile.get('bank_balance')}
- Sponsor: {user_profile.get('sponsor')}

Travel:
- Duration: {user_profile.get('duration')}
- Travel History: {user_profile.get('travel_history')}
"""

    # 🔥 STRONGER PROMPT
    prompt = f"""
You are an expert visa officer.

Analyze the user's eligibility carefully using:
1. Their personal profile
2. Financial strength
3. Travel history
4. Employment stability

{user_info}

User Question:
{query}

Context:
{context}

Give output STRICTLY in this format:

STATUS: (ELIGIBLE / PARTIALLY ELIGIBLE / NOT ELIGIBLE)

EXPLANATION:
Explain clearly based on user profile.

REQUIRED DOCUMENTS:
- List documents

NEXT STEPS:
- List actions
"""

    try:
        chain = ChatPromptTemplate.from_template(prompt) | self.llm | StrOutputParser()
        response = chain.invoke({})

        response_upper = response.upper()

        if "NOT ELIGIBLE" in response_upper:
            status = "NOT ELIGIBLE"
        elif "PARTIALLY" in response_upper:
            status = "PARTIALLY ELIGIBLE"
        elif "ELIGIBLE" in response_upper:
            status = "ELIGIBLE"
        else:
            status = "UNKNOWN"

        return {
            "response": response,
            "status": status
        }

    except Exception as e:
        return {
            "response": f"❌ Error: {str(e)}",
            "status": "ERROR"
        }