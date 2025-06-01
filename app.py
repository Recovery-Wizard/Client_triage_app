
import streamlit as st
import pandas as pd
from datetime import datetime

# Simulated AI triage function
def triage_client(housing, substance, mental, support):
    if housing == 'Unstable':
        if int(substance) > 7 or int(mental) > 7:
            return 'Housing Referral'
    if int(mental) > 6:
        return 'Therapy'
    return 'Peer Support'

# Simulated daily updated resource data
resources = pd.DataFrame([
    {'name': 'Phoenix Peer Hub', 'type': 'Peer Support', 'zip': '47906', 'county': 'Tippecanoe',
     'contact': '765-555-1111', 'address': '123 Recovery Way', 'website': 'http://phoenixpeer.org', 'verified': datetime.today().date()},
    {'name': 'West Lafayette Counseling Center', 'type': 'Therapy', 'zip': '47906', 'county': 'Tippecanoe',
     'contact': '765-555-2222', 'address': '456 Wellness Blvd', 'website': 'http://wlcc.org', 'verified': datetime.today().date()},
    {'name': 'Lafayette Housing Outreach', 'type': 'Housing Referral', 'zip': '47906', 'county': 'Tippecanoe',
     'contact': '765-555-3333', 'address': '789 Shelter Ln', 'website': 'http://housinglaf.org', 'verified': datetime.today().date()},
])

# Streamlit App
st.title("Client Recovery Triage Tool")

menu = st.sidebar.selectbox("Choose Access Mode", ["Free Individual Search", "Organization Login"])

if menu == "Free Individual Search":
    st.header("Self-Help Screening Tool")
    client_zip = st.text_input("Your ZIP Code")
    housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'])
    substance_use = st.slider("Substance Use Severity (1-10)", 1, 10)
    mental_health = st.slider("Mental Health Severity (1-10)", 1, 10)
    support_system = st.selectbox("Do You Have a Support System?", ['Yes', 'No'])

    if st.button("Find Support Resources"):
        support = 1 if support_system == 'Yes' else 0
        predicted_service = triage_client(housing_status, substance_use, mental_health, support)
        st.success(f"Recommended Support Type: {predicted_service}")

        matched = resources[(resources['zip'] == client_zip) & (resources['type'] == predicted_service)]
        if not matched.empty:
            st.write("### Resources Near You:")
            st.dataframe(matched[['name', 'contact', 'address', 'website']])
        else:
            st.warning("No matching resources found in this ZIP code.")

elif menu == "Organization Login":
    st.header("Organization Client Intake")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.success("Access Granted")

            client_name = st.text_input("Client Name")
            client_zip = st.text_input("ZIP Code")
            housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'], key='org_housing')
            substance_use = st.slider("Substance Use Severity (1-10)", 1, 10, key='org_substance')
            mental_health = st.slider("Mental Health Severity (1-10)", 1, 10, key='org_mental')
            support_system = st.selectbox("Support System", ['Yes', 'No'], key='org_support')
            goals = st.text_area("Client Goals")
            needs = st.text_area("Client Needs")

            if st.button("Triage Client"):
                support = 1 if support_system == 'Yes' else 0
                predicted_service = triage_client(housing_status, substance_use, mental_health, support)
                st.success(f"Recommended Service for {client_name}: {predicted_service}")

                matched = resources[(resources['zip'] == client_zip) & (resources['type'] == predicted_service)]
                if not matched.empty:
                    st.write("### Local Matched Resources:")
                    st.dataframe(matched[['name', 'contact', 'address', 'website']])
                else:
                    st.warning("No matching resources found in this ZIP code.")
        else:
            st.error("Invalid credentials. Contact support if needed.")
