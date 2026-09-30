from llm.gemini import ask_gemini


def review_repository(repository_text, user_prompt=""):

    if user_prompt.strip():

        instruction = f"""
The student has requested the following:

{user_prompt}

While reviewing the repository, pay special attention to this request.
"""

    else:

        instruction = """
Perform an innovation-oriented repository review.
"""

    prompt = f"""
You are a Senior Software Engineer and Technology Innovation Analyst
working for Creatix, an AI-powered Student Innovation Platform.

Your job is to analyze an existing software repository and identify how
its technological resources can be intelligently reused, adapted, and
improved for student innovation.

{instruction}

Analyze the repository and provide the following sections:

# 1. Repository Overview
Briefly explain what the repository does and its main purpose.

# 2. Technology Stack
Identify the important languages, frameworks, libraries, APIs,
databases, AI/ML technologies, and other major technologies used.

# 3. Existing Resources
Identify useful existing resources in the repository, such as:

- reusable functions
- modules
- APIs
- models
- components
- algorithms
- datasets
- integrations
- useful architectural patterns

# 4. Resource Utilization
Explain how the existing resources could be reused or adapted.

For each important resource, explain:

- What it does
- Why it is useful
- How it could be reused
- What modifications may be required

# 5. Improvement Opportunities
Identify areas where the existing implementation could be improved.

Focus on:

- functionality
- performance
- scalability
- usability
- reliability
- AI/ML improvements
- architecture

# 6. Innovation Opportunities
Suggest practical ways the existing technology could be extended
to create new student projects, prototypes, or innovative solutions.

Do not suggest completely unrelated ideas.

Base suggestions on the actual technologies and resources found
in the repository.

# 7. Suggested Development Path
Give a short step-by-step path for turning the identified resources
into an improved prototype or innovation.

Important rules:

- Base your analysis only on the repository content provided.
- Do not claim that you searched the internet.
- Do not invent technologies that are not present in the repository.
- Clearly distinguish existing resources from suggested improvements.
- Keep the recommendations practical for student developers.

Repository:

{repository_text}
"""

    return ask_gemini(prompt)