from openai import OpenAI
client = OpenAI()
from .prompts import DOUBT_RESOLUTION_PROMPT

class DoubtHandler:
    def __init__(self, model="gpt-4o-mini", temperature=0.5):
        self.model = model
        self.temperature = temperature  # Slightly higher for more natural responses

    def resolve_doubt(self, problem: str, steps: str, doubt: str) -> str:
        """
        Resolve a specific doubt about the solution steps.
        
        Args:
            problem (str): Original math problem.
            steps (str): Normalized or extracted steps.
            doubt (str): User's question (e.g., "Why do we factor like that?").
        
        Returns:
            str: Helpful LLM response.
        """
        prompt = DOUBT_RESOLUTION_PROMPT.format(
            problem=problem, steps=steps, doubt=doubt
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()