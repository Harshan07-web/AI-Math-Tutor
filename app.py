from flask import Flask, render_template, request, jsonify
from PIL import Image
import os

# ✅ Import Pipeline
# This assumes app.py is in the root, and _core is a folder in the root
from _core.pipeline import Pipeline

# ✅ Configure Flask to look inside _core/_frontend for HTML and CSS/JS
app = Flask(__name__, 
            template_folder='_frontend/templates',
            static_folder='_frontend/static')

# Initialize pipeline once
pipeline = Pipeline()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload_ocr", methods=["POST"])
def upload_ocr():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded"})

    try:
        img = Image.open(file)
        # Assuming solve_and_explain can take an image object directly
        result = pipeline.solve_and_explain(img) 
        
        if result.get("error"):
            return jsonify(result)

        return jsonify({
            "latex": result.get("expression", ""), # Send raw latex
            "solution": result.get("solution", "")  # Optional: if OCR solves it too
        })

    except Exception as e:
        return jsonify({"error": "OCR failed", "message": str(e)})

@app.route("/solve_math", methods=["POST"])
def solve_math():
    user_input = request.form.get("math_input")
    if not user_input:
        return jsonify({"error": "No input provided"})

    # Pipeline returns a dict with 'final_answer', 'steps', 'explanation'
    result = pipeline.solve_and_explain(user_input)
    return jsonify(result)

@app.route("/ask_doubt", methods=["POST"])
def ask_doubt():
    try:
        # Defaults to -1 if not provided (general doubt)
        step_number = int(request.form.get("step_number", -1))
        question = request.form.get("question", "")

        if not question:
            return jsonify({"error": "Please ask a specific question"})

        answer = pipeline.answer_doubt(step_number, question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": "Doubt handling failed", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)