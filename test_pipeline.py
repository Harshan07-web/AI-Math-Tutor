
from _core.pipeline import Pipeline

pipeline = Pipeline()

print("=== Solve ===")

# Change expression here for testing:
#user_expression = "abc"
user_expression = "2*x^2 + 4*x +4 = 0 "   # → Will ask: differentiate or integrate?
#user_expression = "∫(x^2 + 2) dx"  # If you later support symbolic integral frontend

result = pipeline.solve_and_explain(user_expression)

print(result)
