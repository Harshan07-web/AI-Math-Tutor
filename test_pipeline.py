from _llm.explainer import StepExplainer

steps = StepExplainer()


nsteps = [{'step_number': 1, 'type': 'linearity', 'rule': None, 'input': 'x**3 + x**2 + 5',
            'output': 'd/dx(5) + d/dx(x**2) + d/dx(x**3)', 'explanation_hint': 'Split the derivative using linearity'},
            {'step_number': 2, 'type': 'rule_application', 'rule': 'constant_rule', 'input': '5', 'output': '0', 'explanation_hint': 'The derivative of a constant is zero'},
              {'step_number': 3, 'type': 'rule_application', 'rule': 'power_rule', 'input': 'x**2', 'output': '2*x', 'explanation_hint': 'Multiply by the exponent and reduce the power by 1'},
              {'step_number': 4, 'type': 'rule_application', 'rule': 'power_rule', 'input': 'x**3', 'output': '3*x**2', 'explanation_hint': 'Multiply by the exponent and reduce the power by 1'}]

ans = steps.explain_steps(normalized_steps=nsteps,final_answer='3*x**2 + 2*x')

print(ans)