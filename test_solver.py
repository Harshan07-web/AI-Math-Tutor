from _math_engine.solver import MathSolver
from _math_engine.step_extractor import StepExtractor
from _math_engine.step_normalizer import StepNormalizer


prob = MathSolver()
steps = StepExtractor()
nsteps = StepNormalizer()

problem_input = {
    "problem_type": "differentiation",
    "expression": "x**2 + x**3 + 5",
    "variable": "x",
    "metadata": {
        "difficulty": "basic",
        "source": "text"
    }
}


output = prob.solve(problem_input=problem_input)

output_steps = steps.extract_steps(solver_output=output)

noutput_steps = nsteps.normalize_steps(output_steps)
print("\n\n")
print("ANSWER:\n",output)
print("\n\n")
print("EXTRACTED STEPS:\n",output_steps)
print("\n\n")
print("NORMALIZED STEPS\n",noutput_steps)
print()

key = ['step_number','input','output','explanation_hint'] 

for i in noutput_steps:
    for j,k in i.items():
        if j in key:
            if j=='explanation_hint':
                print(j)
                print(k)
            else:
                print(f"{j} : {k}")
    print()





