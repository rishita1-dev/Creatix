import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import streamlit as st
import requests
from agents.pipeline import CreatixPipeline
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
    (   "Auto",
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

    if prompt.strip() == "":
        st.warning("Please enter a prompt.")

    elif task == "Repository Q&A (RAG)" and repo_url.strip() == "":
        st.warning("Please enter a GitHub Repository URL.")

    else:
        st.write("Sending request to backend...")
        st.write({"task": task, "prompt": prompt, "repo_url": repo_url})

        response = requests.post(
            "http://127.0.0.1:8000/generate",
            json={"task":task,"prompt": prompt,"repo_url": repo_url}, timeout=300
        )

        if response.status_code == 200:
            
            result = response.json()

    # Show which task the Planner Agent selected
            if "selected_task" in result:
                st.info(
                    f"Automatically selected: {result['selected_task']}"
                )

            # Show why the Planner Agent selected that task
            if "reason" in result:
                st.caption(
                    f"Reason: {result['reason']}"
                )

            # Show the final response
            if "response" in result:
                st.success("Response")
                st.write(result["response"])

            # Show backend error if returned in JSON
            elif "error" in result:
                st.error(result["error"])

            else:
                st.error("Unexpected response from backend.")

                    

        else:
            st.error(f"Backend Error: {response.status_code}")
            st.write(response.text)