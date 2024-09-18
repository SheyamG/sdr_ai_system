import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.title("AI-Driven Email Outreach System")
email_temp = "Subject: Unlock Amazing Discounts Just for You! Hi Customer, I hope this message finds you well! I wanted to reach out because we have amazing discounts on our premium products such as the Premium Running Shoes and the Smart Fitness Tracker, which I think you would love. We observed that the Smart Fitness Tracker suits your fitness goals perfectly, providing real-time tracking of your activities. Our products not only promise quality but also ensure you get the best value for your investment. I’d love to discuss how our offerings can fit into your lifestyle. Would you be available for a quick chat this week? Let me know what time works for you!Best regards"

# Prospect Research
st.header("1. Prospect Research")
prospect_name = st.text_input("Prospect Name")
company_name = st.text_input("Company Name")

if st.button("Research Prospect"):
    if prospect_name and company_name:
        response = requests.post(f"{BASE_URL}/research_prospect/", json={
            "name": prospect_name,
            "company": company_name
        })
        if response.status_code == 200:
            prospect_info = response.json()
            st.write("### Prospect Info")
            st.json(prospect_info)
            st.session_state['prospect_summary'] = ' '.join(prospect_info.get('search_results', []))
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    else:
        st.warning("Please provide both Prospect Name and Company Name.")


# Email Generation
st.header("2. Generate Email Draft")
if 'prospect_summary' in st.session_state:
    product_catalog = st.file_uploader("Upload Product Catalog (TXT)", type=["txt"])
    
    if product_catalog is not None and st.button("Generate Email"):
        product_catalog_text = product_catalog.getvalue().decode("utf-8")
        
        response = requests.post(f"{BASE_URL}/generate_email/", json={
            "prospect_summary": st.session_state['prospect_summary'],
            "product_catalog": product_catalog_text
        })
        if response.status_code == 200:
            email_draft = response.json()
            st.write("### Email Draft")
            st.text_area("Generated Email Draft", value=email_draft.get('email', ''), height=300)
            st.session_state['email_draft'] = email_draft.get('email', '')
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
else:
    st.warning("Research a prospect first.")

# Email Sending
st.header("3. Send Email")
if 'email_draft' in st.session_state:
    to_email = st.text_input("Recipient Email")
    email_subject = st.text_input("Email Subject")

    email_template = email_temp  # Default to generated draft

    if st.button("Send Email"):
        if to_email and email_subject:
            response = requests.post(f"{BASE_URL}/send_email/", json={
                "to_email": to_email,
                "subject": email_subject,
                "body": email_template
            })
            if response.status_code == 200:
                st.success("Email sent successfully!")
