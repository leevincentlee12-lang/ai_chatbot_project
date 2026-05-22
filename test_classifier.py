from intent_classifier import classify_intent

TEST_QUESTIONS = [
    "solve 2x + 3 = 7",
    "find x",
    "work out x",
    "factor x^2 + 5x + 6",
    "put x squared plus 5x plus 6 into brackets",
    "expand (x+2)(x+3)",
    "expand these brackets",
    "solve x+y=5 and x-y=1",
    "find the roots of x^2 + 5x + 6",
]


def main():
    for question in TEST_QUESTIONS:
        result = classify_intent(question)
        print(question, "->", result)


if __name__ == "__main__":
    main()
