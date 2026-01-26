from flask import Flask, render_template, request, jsonify
from PIL import Image
import os

# ✅ Import Pipeline
from _core.pipeline import Pipeline

# ✅ Flask configuration
app = Flask(
    __name__,
    template_folder="_frontend/templates",
    static_folder="_frontend/static"
)

# ✅ Initialize pipeline once
pipeline = Pipeline()


# --------------------------------------------------
# 🏠 HOME
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# 🖼 OCR IMAGE UPLOAD
# --------------------------------------------------
@app.route("/upload_ocr", methods=["POST"])
def upload_ocr():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image uploaded"})

    try:
        img = Image.open(file)
        result = pipeline.solve_and_explain(img)

        if result.get("error"):
            return jsonify(result)

        return jsonify({
            "expression": result.get("expression", ""),
            "final_answer": result.get("final_answer", ""),
            "steps": result.get("steps", []),
            "explanation": result.get("explanation", ""),
            "problem_type": result.get("problem_type", "")
        })

    except Exception as e:
        return jsonify({
            "error": "OCR processing failed",
            "message": str(e)
        })


# --------------------------------------------------
# 🧮 TEXT / STATEMENT INPUT
# --------------------------------------------------
@app.route("/solve_math", methods=["POST"])
def solve_math():
    user_input = request.form.get("math_input")

    if not user_input:
        return jsonify({"error": "No input provided"})

    result = pipeline.solve_and_explain(user_input)

    if result.get("error"):
        return jsonify(result)

    return jsonify({
        "expression": result.get("expression", ""),
        "final_answer": result.get("final_answer", ""),
        "steps": result.get("steps", []),
        "explanation": result.get("explanation", ""),
        "problem_type": result.get("problem_type", "")
    })


# --------------------------------------------------
# ❓ STEP-BASED DOUBTS
# --------------------------------------------------
@app.route("/ask_doubt", methods=["POST"])
def ask_doubt():
    try:
        step_number = int(request.form.get("step_number", -1))
        question = request.form.get("question", "").strip()

        if not question:
            return jsonify({"error": "Please ask a valid question"})

        answer = pipeline.answer_doubt(step_number, question)

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({
            "error": "Doubt handling failed",
            "message": str(e)
        })


# --------------------------------------------------
# 🚀 RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
