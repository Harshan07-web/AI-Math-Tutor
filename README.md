# AI MATH TUTOR

Suppose you have a mathematical doubt that is hard for you to solve by yourself, You try to search for a solution or use a LLM and you end up getting the solution for the particular problem. But the LLM or 
the solution you found on the internet consist of standard steps which might sometimes not be so understandable. So we built a better solution where you get the steps generated and also could resolve your
doubts about particular steps. The future features are planned to include TTS and STT feature between youself and the LLM agent for voice based doubt clarification and steps explanation. 

## FEATURES

* Support for both text and image input
* Calculations are carried out by Sympy
* LLM do not perfrom any sort of calculation, preventing halucinations
* LLM is used to explain the steps involved in solving the problem
* LLM agent uses the history of the specific problem to clear the doubts asked
* Gemini 2.5 Flash preview is used

## FUTURE FEATURES TO BE IMPLEMENTED 

* STT implementation so users could have live doubt clarrification via voice
* Upgrade the solver engine to solve more advanced problems
* A more detailed UI

## CURRENT TECH STACK

1. Primary Language - Python 3.10
2. OCR preprocessing - OpenCV , Pytorch
3. OCR to Latex - Pix2tex
4. Math Engine - Sympy
5. Step explanation and doubt handling - Gemini API(Langchain Wrapper)
6. UI - Streamlit

## CURRENT FOLDER STRUCUTRE 

📦Ai math tutor
 ┣ 📂data
 ┃ ┣ 📜cache
 ┃ ┣ 📜examples
 ┃ ┗ 📜sessions
 ┣ 📂docs
 ┃ ┣ 📜architecture.md
 ┃ ┗ 📜flow.md
 ┣ 📂scripts
 ┃ ┗ 📜steip_env.py
 ┣ 📂_app
 ┃ ┣ 📜config.py
 ┃ ┣ 📜main.py
 ┃ ┣ 📜routes.py
 ┃ ┗ 📜__init__.py
 ┣ 📂_core
 ┃ ┣ 📜controller.py
 ┃ ┣ 📜pipeline.py
 ┃ ┣ 📜state.py
 ┃ ┗ 📜__init__.py
 ┣ 📂_frontend
 ┃ ┣ 📜app.py
 ┃ ┣ 📜assets
 ┃ ┣ 📜components
 ┃ ┗ 📜utils
 ┣ 📂_llm
 ┃ ┣ 📜doubt_handler.py
 ┃ ┣ 📜explainer.py
 ┃ ┣ 📜prompts.py
 ┃ ┗ 📜__init__.py
 ┣ 📂_math_engine
 ┃ ┣ 📜solver.py
 ┃ ┣ 📜step_extractor.py
 ┃ ┣ 📜step_normalizer.py
 ┃ ┗ 📜__init__.py
 ┣ 📂_speech
 ┃ ┣ 📜stt.py
 ┃ ┣ 📜tts.py
 ┃ ┗ 📜__init__.py
 ┣ 📂_vision
 ┃ ┣ 📜ocr.py
 ┃ ┣ 📜preprocessing.py
 ┃ ┗ 📜__init__.py
 ┣ 📜.gitignore
 ┣ 📜LICENSE
 ┣ 📜requirements.txt


 ## HOW TO RUN 

1. In your terminal
```
> git clone "repo_url"
```
2. Install Required Libraries
```
> pip install -r requirements.txt
```
3. Create a .env file
4. Setup the desired API key
```
YOUR_API_KEY = "API_KEY"
```

#### EXAMPLE USAGE 
```
from _core.pipeline import MathPipeline

pipeline = MathPipeline()
result = pipeline.solve_and_explain("d/dx((x^2 + 3*x) * sin(x))")
print(result)
```

## CONTRIBUTORS

**Checkout the contributors.md file for contributor details**

## LICENSE

**THIS PROJECT IS LICENSED UNDER APACHE LICENSE 2.0**
> Full License detail availabe in the License File
