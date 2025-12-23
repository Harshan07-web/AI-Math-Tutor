## Step 1: The user provides a math problem as an image or text
- **Frontend:** React / Streamlit  
- **Input:** Browser Camera API or Text Input

## Step 2: The input is converted into LaTeX or a SymPy-compatible format
- **Image → LaTeX:** pix2tex + OpenCV  
- **Text → Parsed format:** Python parsing / SymPy parser

## Step 3: A rule-based controller identifies the type of mathematical problem
- **Logic:** Pure Python (no LLM, no LangChain)

## Step 4: SymPy solves the problem deterministically and generates symbolic steps
- **Engine:** SymPy (symbolic computation)

## Step 5: An LLM explains these steps in simple, human-friendly language
- **Framework:** LangChain  
- **Models:** Gemini 1.5 Pro / GPT-4 / Claude

## Step 6: A text-to-speech engine converts the explanation into audio
- **TTS Engines:** edge-tts / Coqui TTS / ElevenLabs

## Step 7: User doubts are handled with speech-to-text and context-aware explanation
- **Speech → Text:** faster-whisper  
- **Explanation:** LangChain + same LLM  
- **Context:** Grounded in stored SymPy steps
