from openai import OpenAI
client = OpenAI()
from .prompts import SOLVE_AND_EXPLAIN_PROMPT, DETAILED_EXPLANATION_PROMPT

class MathExplainer:
    def __init__(self, model="gpt-4o-mini", temperature=0.3):
        self.model = model
        self.temperature = temperature

    def explain_solution(self, problem: str, solution: str) -> str:
        """
        Generate a step-by-step explanation for a given problem and its solution.
        
        Args:
            problem (str): The original math problem.
            solution (str): The solved output (e.g., from MathSolver).
        
        Returns:
            str: LLM-generated explanation.
        """
        prompt = SOLVE_AND_EXPLAIN_PROMPT.format(problem=problem)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt + f"\nSolution: {solution}"}],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()

    def detailed_explanation(self, problem: str, solution: str) -> str:
        """
        Provide a more in-depth explanation, including common pitfalls.
        
        Args:
            problem (str): The original math problem.
            solution (str): The solved output.
        
        Returns:
            str: Detailed LLM response.
        """
        prompt = DETAILED_EXPLANATION_PROMPT.format(problem=problem, solution=solution)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class StepExplainer:
    def __init__(self, model="gemini-2.5-flash-preview-09-2025"):
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.2,
        )

    def explain_steps(self, normalized_steps: list[dict], final_answer: str, problem_type: str = "general") -> str:
        """
        Convert structured steps into a friendly natural language explanation.
        """

        # Format steps into readable bullets
        formatted_steps = "\n".join([
            f"Step {s['step_number']}: {s['type']} → {s['output']}"
            for s in normalized_steps
        ])

        prompt = f"""
You are a friendly math tutor. Explain the steps for solving a {problem_type} problem.

Steps performed:
{formatted_steps}

Final answer: {final_answer}

Explain what is happening in each step, and why it is correct.
Keep the explanation short, clean, and helpful for a student.
        """

        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"Explanation unavailable due to error: {str(e)}"
