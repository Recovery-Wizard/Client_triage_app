
import streamlit as st
import pandas as pd
import requests

st.title("Client Recovery Triage Tool with Live Resource Lookup")

# AI triage logic
def triage_client(housing, substance, mental, support):
    if housing == 'Unstable':
        if int(substance) > 7 or int(mental) > 7:
            return 'Housing Referral'
    if int(mental) > 6:
        return 'Therapy'
    return 'Peer Support'

# Function to fetch resources using the SAMHSA Treatment Locator API
def fetch_samhsa_resources(zip_code, service_type):
    url = f"https://findtreatment.gov/api/facilities?zip={zip_code}&radius=50"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        facilities = data.get('data', [])
        resource_list = []
        for facility in facilities:
            name = facility.get('name')
            phone = facility.get('phone')
            address = facility.get('address', {}).get('address1', '')
            city = facility.get('address', {}).get('city', '')
            state = facility.get('address', {}).get('state', '')
            postal_code = facility.get('address', {}).get('postalCode', '')
            resource_list.append({
                'Name': name,
                'Phone': phone,
                'Address': f"{address}, {city}, {state} {postal_code}"
            })
        return pd.DataFrame(resource_list)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

menu = st.sidebar.selectbox("Choose Access Mode", ["Free Individual Search", "Organization Login"])

if menu == "Free Individual Search":
    st.header("Self-Help Screening Tool")
    zip_code = st.text_input("Your ZIP Code")
    housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'])
    substance_use = st.slider("Substance Use Severity (1-10)", 1, 10)
    mental_health = st.slider("Mental Health Severity (1-10)", 1, 10)
    support_system = st.selectbox("Do You Have a Support System?", ['Yes', 'No'])

    if st.button("Find Support Resources") and zip_code:
        support = 1 if support_system == 'Yes' else 0
        predicted_service = triage_client(housing_status, substance_use, mental_health, support)
        st.success(f"Recommended Support Type: {predicted_service}")

        st.info("Searching SAMHSA database for nearby treatment providers...")
        resources_df = fetch_samhsa_resources(zip_code, predicted_service)
        if not resources_df.empty:
            st.dataframe(resources_df)
        else:
            st.warning("No resources found or unable to fetch data.")

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
            substance_use = st.slider("Substance Use Severity (1-10)", 1, 10, key='org_substance')
            mental_health = st.slider("Mental Health Severity (1-10)", 1, 10, key='org_mental')
            support_system = st.selectbox("Support System", ['Yes', 'No'], key='org_support')
            goals = st.text_area("Client Goals")
            needs = st.text_area("Client Needs")

            if st.button("Triage Client") and zip_code:
                support = 1 if support_system == 'Yes' else 0
                predicted_service = triage_client(housing_status, substance_use, mental_health, support)
                st.success(f"Recommended Service for {client_name}: {predicted_service}")

                st.info("Searching SAMHSA database for nearby treatment providers...")
                resources_df = fetch_samhsa_resources(zip_code, predicted_service)
                if not resources_df.empty:
                    st.dataframe(resources_df)
                else:
                    st.warning("No resources found or unable to fetch data.")
        else:
            st.error("Invalid credentials. Contact support if needed.")
