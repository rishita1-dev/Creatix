import streamlit as st
import requests

# Page Title
st.set_page_config(page_title="Creatix", page_icon="🤖")

st.title("🤖 Creatix")
st.subheader("Autonomous Coding Assistant")

prompt = st.text_area(
    "Enter your coding question",
    height=200
)

if st.button("Generate"):

    if prompt == "":
        st.warning("Please enter a prompt.")
    else:

        url = "http://127.0.0.1:8000/generate"

        data = {
            "prompt": prompt
        }

        response = requests.post(url, json=data)

        if response.status_code == 200:

            result = response.json()

            st.success("Response Generated")

            st.write(result["response"])

        else:

            st.error("Something went wrong.")