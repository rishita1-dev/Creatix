import streamlit as st
import requests
from pathlib import Path


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Creatix",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# Load Custom CSS
# --------------------------------------------------

def load_css():
    css_path = Path(__file__).parent / "styles" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# --------------------------------------------------
# Constants
# --------------------------------------------------

BACKEND_URL = "http://127.0.0.1:8000/generate"

TASK_MAP = {
    "💻 Generate Code": "Generate Code",
    "📖 Explain Code": "Explain Code",
    "🐞 Debug Code": "Debug Code",
    "📂 Review GitHub Repo": "Review GitHub Repository",
    "🔍 Repository Q&A": "Repository Q&A (RAG)",
}

REPO_PAGES = ["📂 Review GitHub Repo", "🔍 Repository Q&A"]

PLACEHOLDERS = {
    "💻 Generate Code": "Example: Write a Python program to check whether a string is a palindrome.",
    "📖 Explain Code": "Paste the code you want explained...",
    "🐞 Debug Code": "Paste your code and error message here...",
    "📂 Review GitHub Repo": "Example: Review this repository and identify code quality issues.",
    "🔍 Repository Q&A": "Example: What does pipeline.py do?",
}

NAV_OPTIONS = [
    "🏠 Home",
    "💻 Generate Code",
    "📖 Explain Code",
    "🐞 Debug Code",
    "📂 Review GitHub Repo",
    "🔍 Repository Q&A",
    "💬 History",
]


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🤖 Creatix")
    st.caption("Autonomous AI Coding Assistant")
    st.divider()

    st.session_state.page = st.radio(
        "Navigate",
        NAV_OPTIONS,
        index=NAV_OPTIONS.index(st.session_state.page),
        label_visibility="collapsed"
    )

    st.divider()
    st.write(f"Messages: {len(st.session_state.history)}")

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.success("Conversation history cleared.")
        st.rerun()

page = st.session_state.page


# --------------------------------------------------
# Build Conversation Context
# --------------------------------------------------

def build_conversation_context(history, max_messages=6):
    """
    Convert recent session history into text that can
    be sent to the backend as conversational context.
    """
    if not history:
        return ""

    recent_history = history[-max_messages:]
    context_parts = []

    for index, item in enumerate(recent_history, start=1):
        context_parts.append(
            f"""
Interaction {index}

Task:
{item.get("task", "Unknown")}

User:
{item.get("prompt", "")}

Creatix:
{item.get("response", "")}
"""
        )

    return "\n".join(context_parts)


# --------------------------------------------------
# Shared Submit + Render Logic (talks to your FastAPI backend)
# --------------------------------------------------

def run_task(page_label, prompt, repo_url=None):

    task = TASK_MAP[page_label]

    # ----------------------------------------------
    # Validate prompt
    # ----------------------------------------------
    if page_label != "📂 Review GitHub Repo" and not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    # ----------------------------------------------
    # Validate repository URL
    # ----------------------------------------------
    if page_label in REPO_PAGES and (not repo_url or not repo_url.strip()):
        st.warning("Please enter a GitHub Repository URL.")
        st.stop()

    try:
        conversation_context = build_conversation_context(st.session_state.history)

        with st.spinner("Creatix is processing your request..."):
            response = requests.post(
                BACKEND_URL,
                json={
                    "task": task,
                    "prompt": prompt,
                    "repo_url": repo_url.strip() if repo_url and repo_url.strip() else None,
                    "conversation_context": conversation_context,
                },
                timeout=300,
            )

        # --------------------------------------
        # Successful HTTP response
        # --------------------------------------
        if response.status_code == 200:

            result = response.json()

            if not result.get("success", False):
                st.error(result.get("error", "Unknown error occurred."))

            else:
                final_response = result.get("response", "")
                selected_task = result.get("selected_task", result.get("task", task))

                st.session_state.history.append({
                    "task": selected_task,
                    "prompt": prompt,
                    "response": final_response,
                    "repo_url": repo_url,
                    "revised": result.get("revised", False),
                })

                st.info(f"Selected task: {selected_task}")

                reason = result.get("reason")
                if reason:
                    st.caption(f"Reason: {reason}")

                if result.get("revised", False):
                    st.info(
                        "The original response was reviewed and improved by the Reviewer Agent."
                    )
                else:
                    st.caption("The response was approved by the Reviewer Agent.")

                st.success("Final Response")
                st.markdown(final_response)

        # --------------------------------------
        # HTTP Error
        # --------------------------------------
        else:
            st.error(f"Backend returned HTTP error: {response.status_code}")
            st.write(response.text)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend. Make sure FastAPI is running on port 8000.")

    except requests.exceptions.Timeout:
        st.error("The request took too long and timed out.")

    except Exception as e:
        st.error(f"An unexpected error occurred: {type(e).__name__}: {str(e)}")


# --------------------------------------------------
# Home Page
# --------------------------------------------------

if page == "🏠 Home":

    st.markdown("<div class='creatix-badge'>AI Coding Assistant</div>", unsafe_allow_html=True)
    st.title("Welcome to Creatix 🤖")
    st.write(
        "Generate, explain, debug and review code, and ask questions about any "
        "GitHub repo using RAG."
    )
    st.divider()

    features = [
        ("💻", "Generate Code", "Turn plain instructions into working code.", "💻 Generate Code"),
        ("📖", "Explain Code", "Understand what any snippet does, in plain English.", "📖 Explain Code"),
        ("🐞", "Debug Code", "Find and fix errors in your code fast.", "🐞 Debug Code"),
        ("📂", "Review GitHub Repos", "Get an AI walkthrough of any repository.", "📂 Review GitHub Repo"),
        ("🔍", "Repository Q&A", "Ask questions about a codebase using RAG.", "🔍 Repository Q&A"),
    ]

    cols = st.columns(3)

    for i, (icon, title, desc, target) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"<div class='creatix-card'><h3>{icon} {title}</h3><p>{desc}</p></div>",
                unsafe_allow_html=True
            )
            if st.button(f"Open {title}", key=f"open_{target}", use_container_width=True):
                st.session_state.page = target
                st.rerun()


# --------------------------------------------------
# Task Pages (Generate / Explain / Debug / Review / Q&A)
# --------------------------------------------------

elif page in TASK_MAP:

    st.title(page)
    st.markdown("<div class='creatix-card'>", unsafe_allow_html=True)

    repo_url = None
    if page in REPO_PAGES:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository"
        )

    prompt = st.text_area(
        "Your Prompt",
        placeholder=PLACEHOLDERS[page],
        height=200
    )

    submit = st.button("🚀 Submit", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if submit:
        run_task(page, prompt, repo_url)


# --------------------------------------------------
# History Page
# --------------------------------------------------

elif page == "💬 History":

    st.title("💬 Conversation History")

    if not st.session_state.history:
        st.info("No conversations yet. Try one of the tasks from the sidebar!")

    else:
        for index, item in enumerate(reversed(st.session_state.history), start=1):
            actual_number = len(st.session_state.history) - index + 1

            with st.expander(f"Interaction {actual_number}: {item['task']}"):

                st.markdown("**You:**")
                st.write(item["prompt"])

                if item.get("repo_url"):
                    st.markdown("**Repository:**")
                    st.code(item["repo_url"], language=None)

                st.markdown("**Creatix:**")
                st.markdown(item["response"])

                if item.get("revised", False):
                    st.caption("This response was improved by the Reviewer Agent.")