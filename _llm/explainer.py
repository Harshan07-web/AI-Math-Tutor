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