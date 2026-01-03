function openTab(evt, tabName) {
    let tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) tabcontent[i].style.display = "none";

    let tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) tablinks[i].className = tablinks[i].className.replace(" active", "");

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Open default tab
document.addEventListener("DOMContentLoaded", function() {
    document.getElementsByClassName("tablinks")[0].click();
});

function sendOCR() {
    let file = document.getElementById("ocr_file").files[0];
    let formData = new FormData();
    formData.append("image", file);

    fetch("/upload_ocr", {method: "POST", body: formData})
    .then(res => res.json())
    .then(data => {
        document.getElementById("ocr_result").textContent = data.latex || data.error;
        MathJax.typeset();
    });
}

function solveMath() {
    let input = document.getElementById("math_input").value;
    let formData = new FormData();
    formData.append("math_input", input);

    fetch("/solve_math", {method: "POST", body: formData})
    .then(res => res.json())
    .then(data => {
        document.getElementById("math_answer").textContent = "Answer: " + (data.final_answer || data.error);
        let stepsHtml = "";
        if (data.steps) {
            data.steps.forEach(s => stepsHtml += `Step ${s.step_number}: ${s.output}\n`);
        }
        document.getElementById("math_steps").textContent = stepsHtml;
        document.getElementById("math_explanation").textContent = data.explanation || "";
        MathJax.typeset();
    });
}

function askDoubt() {
    let question = document.getElementById("doubt_question").value;
    // You can enhance to send steps and final_answer as well
    let formData = new FormData();
    formData.append("question", question);

    fetch("/ask_doubt", {method: "POST", body: formData})
    .then(res => res.json())
    .then(data => {
        document.getElementById("doubt_answer").textContent = data.answer;
    });
}
