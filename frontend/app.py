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

BACKEND_URL = "https://creatix-backend-y8oh.onrender.com/generate"

TASK_MAP = {
    "💡 Innovation Mode": "Auto",
    "🛠️ Build Solution": "Generate Code",
    "📖 Understand Technology": "Explain Code",
    "🔧 Improve Solution": "Debug Code",
    "📂 Explore GitHub Resources": "Review GitHub Repository",
    "🔍 Extract Repository Knowledge": "Repository Q&A (RAG)",
}

REPO_PAGES = [
    "📂 Explore GitHub Resources",
    "🔍 Extract Repository Knowledge"
]

PLACEHOLDERS = {
    "💡 Innovation Mode": "Example: I want to develop an AI system for detecting potholes using mobile cameras.",
    "🛠️ Build Solution": "Describe the solution or feature you want to build.",
    "📖 Understand Technology": "Paste the code or technology you want explained...",
    "🔧 Improve Solution": "Paste your code and error message here...",
    "📂 Explore GitHub Resources": "Optional: Tell Creatix what you want to focus on while reviewing this repository.",
    "🔍 Extract Repository Knowledge": "Example: What technologies are used in this repository and which components could be reused?",
}

HOME_OPTION = "🏠 Home"
HISTORY_OPTION = "💬 History"

TASK_OPTIONS = [
    "💡 Innovation Mode",
    "🛠️ Build Solution",
    "📖 Understand Technology",
    "🔧 Improve Solution",
    "📂 Explore GitHub Resources",
    "🔍 Extract Repository Knowledge",
]

# Kept for backward-compatible reference to "every page label"
NAV_OPTIONS = [HOME_OPTION] + TASK_OPTIONS + [HISTORY_OPTION]


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "page" not in st.session_state:
    st.session_state.page = HOME_OPTION


def set_page(target):
    """Navigate to `target` and keep the task radio in sync with it."""
    st.session_state.page = target
    # Only highlight the radio group when the target is one of the task
    # pages. Streamlit does not allow assigning None directly to a radio's
    # session_state value (None is only valid as the `index` constructor
    # arg), so to clear the selection when Home/History is picked, we
    # remove the key entirely -- the widget then falls back to index=None
    # (nothing selected) on its next render.
    if target in TASK_OPTIONS:
        st.session_state.nav_radio = target
    else:
        st.session_state.pop("nav_radio", None)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🤖 Creatix")
    st.caption("AI-Powered Student Innovation Platform")
    st.divider()

    # ---- Home bar ----
    st.button(
        HOME_OPTION,
        key="nav_home_btn",
        use_container_width=True,
        type="primary" if st.session_state.page == HOME_OPTION else "secondary",
        on_click=set_page,
        args=(HOME_OPTION,),
    )

    st.divider()

    # ---- Task pages bar (radio buttons) ----
    task_index = (
        TASK_OPTIONS.index(st.session_state.page)
        if st.session_state.page in TASK_OPTIONS
        else None
    )
    st.radio(
        "Navigate",
        TASK_OPTIONS,
        index=task_index,
        label_visibility="collapsed",
        key="nav_radio",
        on_change=lambda: set_page(st.session_state.nav_radio),
    )

    st.divider()

    # ---- History bar ----
    st.button(
        HISTORY_OPTION,
        key="nav_history_btn",
        use_container_width=True,
        type="primary" if st.session_state.page == HISTORY_OPTION else "secondary",
        on_click=set_page,
        args=(HISTORY_OPTION,),
    )

    st.divider()
    st.write(f"Messages: {len(st.session_state.history)}")

    if st.button("🗑️ Clear History", use_container_width=True, type="primary"):
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

if page == HOME_OPTION:

    st.markdown(
        "<div class='creatix-badge'>AI-Powered Student Innovation Platform</div>",
        unsafe_allow_html=True
    )

    st.title("Welcome to Creatix 🤖")

    st.subheader("Explore • Understand • Build • Innovate")

    st.write(
        "Creatix uses AI to help students explore existing technological "
        "resources, extract useful insights, build solutions, and improve "
        "their innovations."
    )

    st.divider()

    features = [
    (
        "💡",
        "Innovation Mode",
        "Turn an idea into an AI-guided innovation and development path.",
        "💡 Innovation Mode"
    ),
    (
        "🛠️",
        "Build Solution",
        "Turn an idea or requirement into working code.",
        "🛠️ Build Solution"
    ),
    (
        "📖",
        "Understand Technology",
        "Understand existing code and technologies in simple language.",
        "📖 Understand Technology"
    ),
    (
        "🔧",
        "Improve Solution",
        "Find bugs and improve existing implementations.",
        "🔧 Improve Solution"
    ),
    (
        "📂",
        "Explore GitHub Resources",
        "Analyze existing repositories and identify reusable resources.",
        "📂 Explore GitHub Resources"
    ),
    (
        "🔍",
        "Extract Repository Knowledge",
        "Use RAG to extract useful knowledge from existing codebases.",
        "🔍 Extract Repository Knowledge"
    ),
]

    cols = st.columns(3)

    for i, (icon, title, desc, target) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"<div class='creatix-card'><h3>{icon} {title}</h3><p>{desc}</p></div>",
                unsafe_allow_html=True
            )
            st.button(
                f"Open {title}",
                key=f"open_{target}",
                use_container_width=True,
                on_click=set_page,
                args=(target,),
            )


# --------------------------------------------------
# Task Pages (Generate / Explain / Debug / Review / Q&A)
# --------------------------------------------------

elif page in TASK_MAP:

    st.title(page)
    st.divider()

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

    if submit:
        run_task(page, prompt, repo_url)


# --------------------------------------------------
# History Page
# --------------------------------------------------

elif page == HISTORY_OPTION:

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