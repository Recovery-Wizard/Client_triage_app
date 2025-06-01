
import streamlit as st
import pandas as pd

st.title("Client Recovery Triage Tool (Curated Services Version)")

# Load service database
@st.cache_data
def load_services():
    return pd.read_csv("curated_services.csv")

services_df = load_services()

# ZIP to region mapping
region_map = {
    '47906': 'Tippecanoe',
    '46201': 'Marion',
    '46802': 'Allen'
}

# Triage logic
def triage_client(housing, substance, mental, support):
    if housing == 'Unstable':
        if substance > 7 or mental > 7:
            return 'Housing Referral'
    if mental > 6:
        return 'Therapy'
    return 'Peer Support'

menu = st.sidebar.selectbox("Choose Access Mode", ["Free Individual Search", "Organization Login"])

if menu == "Free Individual Search":
    st.header("Self-Help Screening Tool")
    zip_code = st.text_input("Your ZIP Code")
    housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'])
    substance_use = st.selectbox("Substance Use Severity", ['Mild (1-3)', 'Moderate (4-7)', 'Severe (8-10)'])
    mental_health = st.selectbox("Mental Health Concern Level", ['Low (1-3)', 'Moderate (4-7)', 'High (8-10)'])
    support_system = st.selectbox("Do You Have a Support System?", ['Yes', 'No'])

    if st.button("Find Support Resources") and zip_code:
        substance_score = {'Mild (1-3)': 2, 'Moderate (4-7)': 5, 'Severe (8-10)': 9}[substance_use]
        mental_score = {'Low (1-3)': 2, 'Moderate (4-7)': 5, 'High (8-10)': 9}[mental_health]
        support = 1 if support_system == 'Yes' else 0

        predicted_service = triage_client(housing_status, substance_score, mental_score, support)
        st.success(f"Recommended Support Type: {predicted_service}")

        region = region_map.get(zip_code, None)
        if region:
            matched = services_df[(services_df['region'] == region) & (services_df['type'] == predicted_service)]
            if not matched.empty:
                st.write("### Recommended Local Resources:")
                st.dataframe(matched[['name', 'contact', 'address']])
            else:
                st.warning("No matching services found in your area.")
        else:
            st.warning("Region for the provided ZIP code is not supported yet.")

elif menu == "Organization Login":
    st.header("Organization Client Intake")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.success("Access Granted")

            client_name = st.text_input("Client Name")
            zip_code = st.text_input("ZIP Code")
            housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'], key='org_housing')
            substance_use = st.selectbox("Substance Use Severity", ['Mild (1-3)', 'Moderate (4-7)', 'Severe (8-10)'], key='org_substance')
            mental_health = st.selectbox("Mental Health Concern Level", ['Low (1-3)', 'Moderate (4-7)', 'High (8-10)'], key='org_mental')
            support_system = st.selectbox("Support System", ['Yes', 'No'], key='org_support')
            goals = st.text_area("Client Goals")
            needs = st.text_area("Client Needs")

            if st.button("Triage Client") and zip_code:
                substance_score = {'Mild (1-3)': 2, 'Moderate (4-7)': 5, 'Severe (8-10)': 9}[substance_use]
                mental_score = {'Low (1-3)': 2, 'Moderate (4-7)': 5, 'High (8-10)': 9}[mental_health]
                support = 1 if support_system == 'Yes' else 0

                predicted_service = triage_client(housing_status, substance_score, mental_score, support)
                st.success(f"Recommended Service for {client_name}: {predicted_service}")

                region = region_map.get(zip_code, None)
                if region:
                    matched = services_df[(services_df['region'] == region) & (services_df['type'] == predicted_service)]
                    if not matched.empty:
                        st.write("### Recommended Local Resources:")
                        st.dataframe(matched[['name', 'contact', 'address']])
                    else:
                        st.warning("No matching services found in your area.")
                else:
                    st.warning("Region for the provided ZIP code is not supported yet.")
        else:
            st.error("Invalid credentials. Contact support if needed.")
