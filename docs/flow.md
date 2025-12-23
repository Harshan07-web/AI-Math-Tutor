**#1. The user provides a math problem as an image or text**
   -(Frontend: React / Streamlit, Browser Camera API or Text Input)

**#2. The input is converted into LaTeX or a SymPy-compatible format**
   -Image → LaTeX (pix2tex + OpenCV)
   -Text → Parsed format (Python parsing / SymPy parser)

**#3. A rule-based controller identifies the type of mathematical problem**
   -(Pure Python logic — no LLM, no LangChain)

**#4. SymPy solves the problem deterministically and generates symbolic steps**
   -(SymPy – symbolic computation engine)

**#5. An LLM explains these steps in simple, human-friendly language**
   -(LangChain + LLM such as Gemini 1.5 Pro / GPT-4 / Claude)

**#6. A text-to-speech engine converts the explanation into audio**
   -(edge-tts / Coqui TTS / ElevenLabs)

**#7. If the user asks a doubt, speech-to-text transcribes it, and the LLM provides a context-aware explanation grounded in the original steps**
   -Speech → Text (faster-whisper)
   -Explanation (LangChain + same LLM, using stored SymPy steps)