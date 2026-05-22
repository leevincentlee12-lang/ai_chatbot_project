from homework_helper import answer_question, _answer_quadratic_question

q = "solve x^2 - 9 = 0"
try:
	print("answer_question ->", answer_question(q, mode="step-by-step"))
except Exception as e:
	import traceback
	print("answer_question raised:")
	traceback.print_exc()

try:
	print("_answer_quadratic_question ->", _answer_quadratic_question(q, "step-by-step"))
except Exception as e:
	import traceback
	print("_answer_quadratic_question raised:")
	traceback.print_exc()
except Exception:
	pass

# inspect external classifier and understanding model
try:
	from intent_classifier import classify_intent as external_classify
	print("external classify ->", external_classify(q))
except Exception as e:
	print("external classify unavailable:", e)

try:
	from core.understanding import Understanding
	from homework_helper import understanding_model
	print("understanding detect ->", understanding_model.detect_intent(q))
except Exception as e:
	print("understanding model issue:", e)
