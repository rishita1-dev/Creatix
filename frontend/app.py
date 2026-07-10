import streamlit as st
import requests

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Creatix",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("🤖 Creatix")
st.subheader("Autonomous Coding Assistant")

st.markdown("---")

# -----------------------------
# Task Selection
# -----------------------------
task = st.radio(
    "Choose Task",
    (
        "Generate Code",
        "Explain Code",
        "Debug Code",
        "Review GitHub Repository",
        "Repository Q&A (RAG)"
    )
)

st.markdown("---")

# -----------------------------
# Prompt Box
# -----------------------------
prompt = st.text_area(
    "Prompt",
    placeholder="Enter your coding question here...",
    height=200
)

# -----------------------------
# Repository URL
# -----------------------------
repo_url = st.text_input(
    "Repository URL (Optional)",
    placeholder="https://github.com/username/repository"
)

st.markdown("---")

# -----------------------------
# Submit Button
# -----------------------------
if st.button("Submit", use_container_width=True):

    if prompt == "":
        st.warning("Please enter a prompt.")
    else:

        response = requests.post(
            "http://127.0.0.1:8000/generate",
            json={"task":task,"prompt": prompt}
        )

        if response.status_code == 200:

            result = response.json()

            st.success("Response")

            st.write(result["response"])

        else:

            st.error("Backend Error")