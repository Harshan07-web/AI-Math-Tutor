from _core.pipeline import Pipeline

pipeline = Pipeline()

print("=== Solve ===")

# Change expression here for testing:
#user_expression = "d/dx((x^2 + 3*x) * sin(x))"
user_expression = "x^3 + 5*x"   # → Will ask: differentiate or integrate?
#user_expression = "∫(x^2 + 2) dx"  # If you later support symbolic integral frontend

result = pipeline.solve_and_explain(user_expression)

print(result)
