"""
Prompt templates for LLM interactions in the Math Tutor.
"""

# Base prompt for solving/explaining math problems
SOLVE_AND_EXPLAIN_PROMPT = """
You are a math tutor. Solve the following math problem step-by-step, then provide a clear explanation.
Problem: {problem}
Steps to solve:
1. Identify the type of problem (e.g., quadratic equation, integral).
2. Show each mathematical step with reasoning.
3. Give the final answer in a boxed format.
Explanation: Make it simple for a student, using analogies if helpful. Avoid jargon unless explained.
"""

# Prompt for extracting/normalizing steps
EXTRACT_STEPS_PROMPT = """
From the following solution, extract the key steps in a numbered list. Normalize them to be concise and educational.
Solution: {solution}
Output format:
1. Step description: Math expression.
2. ...
Ensure steps are logical and build on each other.
"""

# Prompt for handling doubts
DOUBT_RESOLUTION_PROMPT = """
You are a patient math tutor. The student has a doubt about this step in the solution.
Original problem: {problem}
Solution steps: {steps}
Doubt: {doubt}
Respond by:
1. Rephrasing the confusing step simply.
2. Providing an example or visual analogy.
3. Asking a clarifying question if needed.
Keep it encouraging and under 200 words.
"""

# Prompt for detailed explanation
DETAILED_EXPLANATION_PROMPT = """
Explain the solution to this math problem in detail, tailored for a beginner.
Problem: {problem}
Solution: {solution}
Break it down: Why each step? Common mistakes? Real-world application?
"""