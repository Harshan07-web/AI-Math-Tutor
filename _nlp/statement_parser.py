from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()


class StatementParser:
    """
    Converts word problems into math expressions.
    Does NOT solve.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-09-2025",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.0  # deterministic
        )

    def parse(self, text: str) -> dict:
        prompt = f"""
You are a math expression extractor.

Your task:
- Convert the given word problem into a SINGLE valid math expression
- Do NOT solve
- Do NOT explain
- Output ONLY the expression
- Use Python/SymPy syntax
- If differentiation or integration is required, use:
  d/dx(...)
  integrate(...)

Word problem:
{text}

Output format:
<math_expression_only>
"""

        try:
            response = self.llm.invoke(prompt)
            expr = response.content.strip()

            if not expr:
                raise ValueError("Empty extraction")

            return {
                "expression": expr,
                "source": "nlp"
            }

        except Exception:
            return {
                "error": "Failed to extract math expression from statement"
            }
