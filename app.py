
import streamlit as st
import pandas as pd
import os

st.title("Client Recovery Triage Tool (County & State Based with Expanded Assessments)")

# Load service database from CSV files in current directory
@st.cache_data
def load_all_services():
    dfs = []
    for file in os.listdir():
        if file.endswith("_Resources.csv"):
            df = pd.read_csv(file)
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

services_df = load_all_services()

# Triage logic
def triage_client(housing, substance, mental, support):
    if housing == 'Unstable':
        if substance > 7 or mental > 7:
            return 'Housing'
    if mental > 6:
        return 'Mental Health'
    return 'Peer Support'

menu = st.sidebar.selectbox("Choose Access Mode", ["Free Individual Search", "Organization Login"])

if menu == "Free Individual Search":
    st.header("Self-Help Screening Tool")
    county = st.text_input("County of Residence")
    state = st.text_input("State of Residence")
    housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'])
    substance_use = st.selectbox("Substance Use Severity", ['Mild (1-3)', 'Moderate (4-7)', 'Severe (8-10)'])
    mental_health = st.selectbox("Mental Health Concern Level", ['Low (1-3)', 'Moderate (4-7)', 'High (8-10)'])
    support_system = st.selectbox("Do You Have a Support System?", ['Yes', 'No'])

    st.subheader("Recovery Capital Assessment (1-5 Scale)")
    recovery_questions = {
        "I have stable and safe housing": st.slider("Housing", 1, 5, 3),
        "I have reliable transportation": st.slider("Transportation", 1, 5, 3),
        "I have a steady source of income": st.slider("Income", 1, 5, 3),
        "I have access to healthcare": st.slider("Healthcare", 1, 5, 3),
        "I have positive relationships": st.slider("Relationships", 1, 5, 3),
        "I feel hopeful about the future": st.slider("Hope", 1, 5, 3),
        "I engage in meaningful activities": st.slider("Meaningful Activity", 1, 5, 3),
        "I have coping skills to manage stress": st.slider("Coping Skills", 1, 5, 3),
        "I feel connected to my community": st.slider("Community Connection", 1, 5, 3),
        "I believe in my ability to recover": st.slider("Self-Efficacy", 1, 5, 3)
    }
    recovery_score = sum(recovery_questions.values())

    st.subheader("Columbia Suicide Severity Rating Scale (C-SSRS)")
    suicide_questions = {
        "Have you wished you were dead or wished you could go to sleep and not wake up?": st.selectbox("Passive Ideation", ['Yes', 'No']),
        "Have you actually had any thoughts of killing yourself?": st.selectbox("Active Ideation", ['Yes', 'No']),
        "Have you been thinking about how you might kill yourself?": st.selectbox("Methods Identified", ['Yes', 'No']),
        "Have you had these thoughts and had some intention of acting on them?": st.selectbox("Intent Without Plan", ['Yes', 'No']),
        "Have you started to work out or worked out the details of how to kill yourself?": st.selectbox("Plan With Intent", ['Yes', 'No']),
        "Have you ever done anything, started to do anything, or prepared to do anything to end your life?": st.selectbox("Attempt History", ['Yes', 'No'])
    }
    suicide_score = sum([1 for answer in suicide_questions.values() if answer == 'Yes'])

    if st.button("Find Support Resources"):
        substance_score = {'Mild (1-3)': 2, 'Moderate (4-7)': 5, 'Severe (8-10)': 9}[substance_use]
        mental_score = {'Low (1-3)': 2, 'Moderate (4-7)': 5, 'High (8-10)': 9}[mental_health]
        support = 1 if support_system == 'Yes' else 0

        predicted_service = triage_client(housing_status, substance_score, mental_score, support)
        st.success(f"Recommended Support Type: {predicted_service}")

        matched = services_df[
            (services_df['Category'].str.lower() == predicted_service.lower()) &
            (services_df['County'].str.lower() == county.lower()) &
            (services_df['State'].str.lower() == state.lower())
        ]
        if not matched.empty:
            st.write("### Recommended Local Resources:")
            st.dataframe(matched[['Name', 'Description', 'Address', 'Phone', 'Website']])
        else:
            st.warning("No matching services found in your area.")

        st.markdown(f"**Recovery Capital Score:** {recovery_score}/50")
        st.markdown(f"**Suicide Risk Score:** {suicide_score}/6")
