import streamlit as st
import requests


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Creatix",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# Initialize Session State
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.title("🤖 Creatix")

    st.caption(
        "Autonomous AI Coding Assistant"
    )

    st.divider()

    st.subheader("Conversation")

    st.write(
        f"Messages: {len(st.session_state.history)}"
    )

    if st.button(
        "🗑️ Clear History",
        use_container_width=True
    ):

        st.session_state.history = []

        st.success(
            "Conversation history cleared."
        )

        st.rerun()


# --------------------------------------------------
# Main Title
# --------------------------------------------------

st.title("🤖 Creatix")

st.subheader(
    "Autonomous AI Coding Assistant"
)

st.write(
    """
    Generate code, explain programs, debug errors,
    review GitHub repositories, and ask questions
    about your codebase using AI.
    """
)

st.divider()


# --------------------------------------------------
# Task Selection
# --------------------------------------------------

task = st.radio(
    "Choose Task",
    (
        "Auto",
        "Generate Code",
        "Explain Code",
        "Debug Code",
        "Review GitHub Repository",
        "Repository Q&A (RAG)"
    ),
    horizontal=True
)


# --------------------------------------------------
# Repository URL
# --------------------------------------------------

repository_tasks = [
    "Review GitHub Repository",
    "Repository Q&A (RAG)"
]


repo_url = None


if task in repository_tasks:

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder=(
            "https://github.com/username/repository"
        )
    )


# --------------------------------------------------
# Prompt Input
# --------------------------------------------------

prompt_placeholders = {

    "Auto":
        "Describe what you want Creatix to do...",

    "Generate Code":
        "Example: Write a Python program to check "
        "whether a string is a palindrome.",

    "Explain Code":
        "Paste the code you want explained...",

    "Debug Code":
        "Paste your code and error message here...",

    "Review GitHub Repository":
        "Example: Review this repository and identify "
        "code quality issues.",

    "Repository Q&A (RAG)":
        "Example: What does pipeline.py do?"
}


prompt = st.text_area(
    "Your Prompt",
    placeholder=prompt_placeholders[task],
    height=200
)


# --------------------------------------------------
# Build Conversation Context
# --------------------------------------------------

def build_conversation_context(
    history,
    max_messages=6
):

    """
    Convert recent session history into text that can
    be sent to the backend as conversational context.

    Only the most recent interactions are included to
    prevent the prompt from becoming unnecessarily large.
    """

    if not history:
        return ""


    recent_history = history[-max_messages:]


    context_parts = []


    for index, item in enumerate(
        recent_history,
        start=1
    ):

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
# Submit Request
# --------------------------------------------------

if st.button(
    "🚀 Submit",
    use_container_width=True
):

    # ----------------------------------------------
    # Validate prompt
    # ----------------------------------------------

    if not prompt.strip():

        st.warning(
            "Please enter a prompt."
        )


    # ----------------------------------------------
    # Validate repository URL
    # ----------------------------------------------

    elif (
        task in repository_tasks
        and (
            not repo_url
            or not repo_url.strip()
        )
    ):

        st.warning(
            "Please enter a GitHub repository URL."
        )


    else:

        try:

            conversation_context = (
                build_conversation_context(
                    st.session_state.history
                )
            )


            with st.spinner(
                "Creatix is processing your request..."
            ):

                response = requests.post(

                    "http://127.0.0.1:8000/generate",

                    json={
                        "task": task,

                        "prompt": prompt,

                        "repo_url": (
                            repo_url.strip()
                            if repo_url
                            and repo_url.strip()
                            else None
                        ),

                        "conversation_context":
                            conversation_context
                    },

                    timeout=300
                )


            # --------------------------------------
            # Successful HTTP response
            # --------------------------------------

            if response.status_code == 200:

                result = response.json()


                # ----------------------------------
                # Pipeline/backend error
                # ----------------------------------

                if not result.get(
                    "success",
                    False
                ):

                    st.error(
                        result.get(
                            "error",
                            "Unknown error occurred."
                        )
                    )


                # ----------------------------------
                # Successful response
                # ----------------------------------

                else:

                    final_response = result.get(
                        "response",
                        ""
                    )


                    selected_task = result.get(
                        "selected_task",
                        result.get(
                            "task",
                            task
                        )
                    )


                    # ------------------------------
                    # Save interaction in history
                    # ------------------------------

                    st.session_state.history.append(
                        {
                            "task": selected_task,

                            "prompt": prompt,

                            "response":
                                final_response,

                            "repo_url":
                                repo_url,

                            "revised":
                                result.get(
                                    "revised",
                                    False
                                )
                        }
                    )


                    # ------------------------------
                    # Show selected task
                    # ------------------------------

                    if task == "Auto":

                        st.info(
                            "Automatically selected: "
                            f"{selected_task}"
                        )

                    else:

                        st.info(
                            "Selected task: "
                            f"{selected_task}"
                        )


                    # ------------------------------
                    # Show routing reason
                    # ------------------------------

                    reason = result.get("reason")


                    if reason:

                        st.caption(
                            f"Reason: {reason}"
                        )


                    # ------------------------------
                    # Reviewer information
                    # ------------------------------

                    if result.get(
                        "revised",
                        False
                    ):

                        st.info(
                            "The original response was "
                            "reviewed and improved by "
                            "the Reviewer Agent."
                        )

                    else:

                        st.caption(
                            "The response was approved "
                            "by the Reviewer Agent."
                        )


                    # ------------------------------
                    # Final response
                    # ------------------------------

                    st.success("Final Response")

                    st.markdown(
                        final_response
                    )


            # --------------------------------------
            # HTTP Error
            # --------------------------------------

            else:

                st.error(
                    "Backend returned HTTP error: "
                    f"{response.status_code}"
                )

                st.write(
                    response.text
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the backend. "
                "Make sure FastAPI is running on "
                "port 8000."
            )


        except requests.exceptions.Timeout:

            st.error(
                "The request took too long and "
                "timed out."
            )


        except Exception as e:

            st.error(
                "An unexpected error occurred: "
                f"{type(e).__name__}: {str(e)}"
            )


# --------------------------------------------------
# Conversation History Display
# --------------------------------------------------

if st.session_state.history:

    st.divider()

    st.header("💬 Conversation History")


    for index, item in enumerate(
        reversed(st.session_state.history),
        start=1
    ):

        actual_number = (
            len(st.session_state.history)
            - index
            + 1
        )


        with st.expander(
            f"Interaction {actual_number}: "
            f"{item['task']}"
        ):

            st.markdown("**You:**")

            st.write(
                item["prompt"]
            )


            if item.get("repo_url"):

                st.markdown(
                    "**Repository:**"
                )

                st.code(
                    item["repo_url"],
                    language=None
                )


            st.markdown("**Creatix:**")

            st.markdown(
                item["response"]
            )


            if item.get(
                "revised",
                False
            ):

                st.caption(
                    "This response was improved "
                    "by the Reviewer Agent."
                )