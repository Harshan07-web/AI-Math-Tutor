"""
LLM module initialization for AI Math Tutor.
Handles OpenAI integration for explanations and doubt handling.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

__all__ = ["client", "MathExplainer", "DoubtHandler"]

# Export the client for use in other modules
client = _client

# Import other modules for easy access
from .explainer import MathExplainer
from .doubt_handler import DoubtHandler