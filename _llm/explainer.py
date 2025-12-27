from langchain_google_genai import ChatGoogleGenerativeAI
from .prompts import EXPLAINER_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()


class StepExplainer:
    def __init__(self,model_name="models/gemini-2.5-flash-preview-09-2025"):
        api_key = os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.3  # balanced tone for teaching
        )

    def explain_steps(self, normalized_steps: list[dict], final_answer: str) -> str:
        """
        Uses Gemini to convert normalized steps into a detailed, 
        human-friendly explanation.
        """

        formatted_steps = "\n".join([
            f"Step {s['step_number']}:\n"
            f"- From: {s['input']}\n"
            f"- To: {s['output']}\n"
            f"- Why: {s.get('explanation_hint', '')}\n"
            for s in normalized_steps
        ])

        prompt = EXPLAINER_PROMPT.format(
            steps=formatted_steps,
            final_answer=final_answer
        )

        response = self.llm.invoke(prompt)
        return response.content
