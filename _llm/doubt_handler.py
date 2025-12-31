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
from langchain_google_genai import ChatGoogleGenerativeAI
from .prompts import DOUBT_HANDLER_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()


class DoubtHandler:
    def __init__(self,model_name="models/gemini-2.5-flash-preview-09-2025"):
        api_key = os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.2,  # Keep explanations focused
        )

    def answer_doubt(
        self,
        user_question: str,
        normalized_steps: list[dict],
        final_answer: str,
        previous_explanation: str = ""
    ) -> str:

        formatted_steps = "\n".join([
            f"Step {s['step_number']}: {s['input']} → {s['output']} ({s['explanation_hint']})"
            for s in normalized_steps
        ])

        prompt = DOUBT_HANDLER_PROMPT.format(
            user_question=user_question,
            steps=formatted_steps,
            final_answer=final_answer,
            explanation=previous_explanation
        )

        response = self.llm.invoke(prompt)
        return response.content
