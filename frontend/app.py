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
# Title
# --------------------------------------------------

st.title("🤖 Creatix")

st.subheader(
    "Autonomous AI Coding Assistant"
)

st.markdown("---")


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
    )
)

st.markdown("---")


# --------------------------------------------------
# Prompt Input
# --------------------------------------------------

prompt = st.text_area(
    "Prompt",
    placeholder=(
        "Enter your coding question here..."
    ),
    height=200
)


# --------------------------------------------------
# Repository URL
# --------------------------------------------------

repo_url = st.text_input(
    "Repository URL (Optional)",
    placeholder=(
        "https://github.com/username/repository"
    )
)

st.markdown("---")


# --------------------------------------------------
# Submit Button
# --------------------------------------------------

if st.button(
    "Submit",
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
        task in [
            "Review GitHub Repository",
            "Repository Q&A (RAG)"
        ]
        and not repo_url.strip()
    ):

        st.warning(
            "Please enter a GitHub Repository URL."
        )


    else:

        try:

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
                            if repo_url.strip()
                            else None
                        )
                    },
                    timeout=300
                )


            # --------------------------------------
            # Successful HTTP response
            # --------------------------------------

            if response.status_code == 200:

                result = response.json()


                # ----------------------------------
                # Backend/pipeline error
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
                # Successful Creatix response
                # ----------------------------------

                else:

                    selected_task = result.get(
                        "selected_task"
                    )

                    if selected_task:

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
                    # Planner/routing reason
                    # ------------------------------

                    reason = result.get("reason")

                    if reason:

                        st.caption(
                            f"Reason: {reason}"
                        )


                    # ------------------------------
                    # Reviewer information
                    # ------------------------------

                    if "revised" in result:

                        if result["revised"]:

                            st.info(
                                "The original response "
                                "was reviewed and improved "
                                "by the Reviewer Agent."
                            )

                        else:

                            st.caption(
                                "The original response "
                                "was approved by the "
                                "Reviewer Agent."
                            )


                    # ------------------------------
                    # Final response
                    # ------------------------------

                    if "response" in result:

                        st.success("Response")

                        st.markdown(
                            result["response"]
                        )

                    else:

                        st.error(
                            "No response was returned "
                            "by the backend."
                        )


            # --------------------------------------
            # HTTP error
            # --------------------------------------

            else:

                st.error(
                    "Backend Error: "
                    f"{response.status_code}"
                )

                st.write(
                    response.text
                )


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the backend. "
                "Make sure FastAPI is running "
                "on port 8000."
            )


        except requests.exceptions.Timeout:

            st.error(
                "The request took too long "
                "and timed out."
            )


        except Exception as e:

            st.error(
                "An unexpected error occurred: "
                f"{type(e).__name__}: {str(e)}"
            )