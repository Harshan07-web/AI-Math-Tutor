from flask import Flask, render_template, request, jsonify
from PIL import Image
import json
import os

# ✅ Import Pipeline ONLY
from _core.pipeline import Pipeline
   # adjust path if needed

app = Flask(__name__,template_folder='_frontend/templates')

# ✅ Initialize pipeline once
pipeline = Pipeline()


@app.route("/")
def home():
    return render_template("index.html")


# 📸 OCR only (image → latex)
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
            "latex": result.get("expression", "")
        })

    except Exception as e:
        return jsonify({"error": "OCR failed", "message": str(e)})


# 🧮 Solve math (text OR image path)
@app.route("/solve_math", methods=["POST"])
def solve_math():
    user_input = request.form.get("math_input")

    if not user_input:
        return jsonify({"error": "No input provided"})

    result = pipeline.solve_and_explain(user_input)
    return jsonify(result)


# ❓ Ask doubt about a step
@app.route("/ask_doubt", methods=["POST"])
def ask_doubt():
    try:
        step_number = int(request.form.get("step_number", -1))
        question = request.form.get("question", "")

        if step_number < 0 or not question:
            return jsonify({"error": "Invalid doubt request"})

        answer = pipeline.answer_doubt(step_number, question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": "Doubt handling failed", "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
