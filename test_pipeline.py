from _core.pipeline import MathPipeline

pipeline = MathPipeline()

print("\n=== Solve ===")
solve_out = pipeline.solve_and_explain("x^2 + x^3 + 5")
print(solve_out["final_answer"])
print(solve_out["explanation"])

print("\n=== Doubt ===")
ans = pipeline.answer_doubt("Why did 5 become 5x?")
print(ans)
