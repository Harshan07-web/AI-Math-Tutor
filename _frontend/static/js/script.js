function openTab(evt, tabName) {
    let tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    let tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

function sendOCR() {
    let fileInput = document.getElementById("ocr_file");
    if(fileInput.files.length === 0) {
        alert("Please select a file first");
        return;
    }

    let resultBox = document.getElementById("ocr_result_box");
    let resultText = document.getElementById("ocr_result");
    
    // Show box & loading state
    resultBox.style.display = "block";
    resultText.innerHTML = '<span style="color:#aaa;">Scanning image...</span>';

    let formData = new FormData();
    formData.append("image", fileInput.files[0]);

    fetch("/upload_ocr", {method: "POST", body: formData})
    .then(res => res.json())
    .then(data => {
        if(data.error) {
            resultText.innerHTML = `<span style="color:#ff6b6b;">Error: ${data.message}</span>`;
        } else {
            resultText.innerHTML = "$$" + data.latex + "$$";
            MathJax.typeset(); 
        }
    })
    .catch(err => {
        console.error(err);
        resultText.innerHTML = "Server connection failed.";
    });
}

function solveMath() {
    let input = document.getElementById("math_input").value;
    if(!input) return;

    let resultBox = document.getElementById("math_result_box");
    // Show loading
    resultBox.style.display = "block";
    document.getElementById("math_answer").innerHTML = '<span style="color:#aaa;">Computing...</span>';
    document.getElementById("math_steps").innerHTML = "";
    document.getElementById("math_explanation").innerHTML = "";

    let formData = new FormData();
    formData.append("math_input", input);

    fetch("/solve_math", {method: "POST", body: formData})
    .then(res => res.json())
    .then(data => {
        if(data.error) {
            document.getElementById("math_answer").innerHTML = `<span style="color:#ff6b6b;">${data.message}</span>`;
        } else {
            document.getElementById("math_answer").innerHTML = "$$" + data.final_answer + "$$";

            let stepsHtml = "";
            if (data.steps && data.steps.length > 0) {
                data.steps.forEach(s => {
                    stepsHtml += `<div class="step-item">
                        <strong>Step ${s.step_number} <span style="font-weight:400; color:#94a3b8;">(${s.type})</span></strong> 
                        $$ ${s.output} $$
                    </div>`;
                });
            } else {
                stepsHtml = "<p style='color:#aaa'>No intermediate steps available.</p>";
            }
            document.getElementById("math_steps").innerHTML = stepsHtml;
            document.getElementById("math_explanation").innerHTML = data.explanation || "<p>No explanation provided.</p>";

            MathJax.typeset();
        }
    })
    .catch(err => console.error(err));
}

function askDoubt() {
    let question = document.getElementById("doubt_question").value;
    let stepNum = document.getElementById("doubt_step").value;

    if(!question) {
        alert("Please write a question.");
        return;
    }

    let resultBox = document.getElementById("doubt_result_box");
    let answerText = document.getElementById("doubt_answer");

    resultBox.style.display = "block";
    answerText.textContent = "Analyzing context...";

    let formData = new FormData();
    formData.append("question", question);
    formData.append("step_number", stepNum ? stepNum : -1);

    fetch("/ask_doubt", {method: "POST", body: formData})
    .then(res => res.json())
    .then(data => {
        answerText.innerHTML = data.answer || data.error;

    })
    .catch(err => console.error(err));
}