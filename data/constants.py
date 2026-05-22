"""Project-wide constant data for routing, follow-ups, and lesson content."""

EXPERIMENT_RESTRICTED_MESSAGE = (
    "This system is restricted to algebra questions for this experiment."
)
EXPERIMENT_MODE_PROMPT = (
    "Which mode should I use: Direct, Step-by-step, or Hint?"
)

SUBJECT_KEYWORDS = {
    "Math": [
        "solve",
        "equation",
        "quadratic",
        "factor",
        "simultaneous",
        "algebra",
        "fraction",
        "simplify",
        "trigonometry",
        "sine",
        "cosine",
        "tangent",
        "indices",
        "graph",
        "coordinate",
        "probability",
    ],
    "Science": [
        "force",
        "velocity",
        "acceleration",
        "mass",
        "density",
        "photosynthesis",
        "acid",
        "ph",
        "energy",
    ],
    "English": [
        "essay",
        "theme",
        "character",
        "analyse",
        "analyze",
        "paragraph",
        "quote",
        "teel",
    ],
    "Humanities": [
        "war",
        "revolution",
        "climate",
        "government",
        "democracy",
        "empire",
        "history",
        "geography",
    ],
}

TOPIC_BY_SUBJECT = {
    "Math": "Algebra and Problem Solving",
    "Science": "Core Science Concepts",
    "English": "Writing and Text Analysis",
    "Humanities": "History and Geography",
    "Unknown": "General Study Help",
}

FOLLOWUPS_BY_SUBJECT = {
    "Math": [
        "Show the full working",
        "Give me a harder practice problem",
        "Check my next algebra step",
    ],
    "Science": [
        "Give a simpler explanation",
        "Show the formula used",
        "Give a real-world example",
    ],
    "English": [
        "Turn this into a paragraph",
        "Give me a TEEL example",
        "Make it Year 8 friendly",
    ],
    "Humanities": [
        "Summarise the key causes",
        "Explain the significance",
        "Turn this into study notes",
    ],
    "Unknown": [
        "Ask a maths question",
        "Ask a science question",
        "Ask for writing help",
    ],
}

FOLLOWUPS_BY_TOPIC = {
    "Linear Equations": [
        "Give me another linear equation",
        "Check my answer for a linear equation",
        "Explain why each step keeps the equation balanced",
    ],
    "Quadratic Equations": [
        "Factor this quadratic instead",
        "Explain the discriminant",
        "Give me another quadratic to solve",
    ],
    "Factoring": [
        "Show me how to expand the factored form",
        "Give me another factoring question",
        "Explain why those brackets work",
    ],
    "Simultaneous Equations": [
        "Solve another system with x and y",
        "Show elimination method",
        "Check my simultaneous-equation steps",
    ],
}

LESSON_CATALOG = {
    "algebra": {
        "title": "Solving Linear Equations",
        "button_label": "Algebra",
        "strand": "Math",
        "level": "Years 7-9",
        "summary": "Learn how to isolate x using inverse operations while keeping the equation balanced.",
        "explanation": (
            "A linear equation has the variable raised to power 1. "
            "Move constants away from the variable and then divide by its coefficient."
        ),
        "key_points": [
            "Do the same operation to both sides of the equation.",
            "Move constants first, then divide by the coefficient of x.",
            "Always substitute your answer back to check it.",
        ],
        "example": (
            "Solve 3x + 5 = 11\n"
            "Step 1: subtract 5 from both sides -> 3x = 6\n"
            "Step 2: divide both sides by 3 -> x = 2"
        ),
        "common_mistakes": [
            "Changing the sign of a term without doing the same operation to both sides.",
            "Stopping at 3x = 6 and forgetting the final division.",
            "Substituting the answer incorrectly when checking.",
        ],
        "practice_prompts": [
            "solve 4x + 3 = 19",
            "solve 7x - 8 = 20",
            "show the full working for 5x + 6 = 26",
        ],
        "starter_prompt": "solve 4x + 3 = 19",
        "related_topics": ["fractions", "simultaneous_equations", "quadratics"],
        "keywords": ["algebra", "linear equation", "equations"],
    },
    "fractions": {
        "title": "Fractions and Operations",
        "button_label": "Fractions",
        "strand": "Math",
        "level": "Years 7-9",
        "summary": "Build confidence with equivalent fractions, common denominators, and fraction arithmetic.",
        "explanation": (
            "Fractions represent parts of a whole. "
            "When adding or subtracting, convert to a common denominator before combining numerators."
        ),
        "key_points": [
            "Equivalent fractions represent the same value in different forms.",
            "Find a common denominator before adding or subtracting.",
            "Simplify the final answer whenever possible.",
        ],
        "example": (
            "Add 1/4 + 1/2\n"
            "Convert 1/2 to 2/4\n"
            "1/4 + 2/4 = 3/4"
        ),
        "common_mistakes": [
            "Adding both the top and bottom numbers directly.",
            "Forgetting to simplify the final fraction.",
            "Using different denominators in the final line.",
        ],
        "practice_prompts": [
            "what is 2/5 + 1/10",
            "simplify 12/18",
            "explain how to find a common denominator",
        ],
        "starter_prompt": "what is 2/5 + 1/10",
        "related_topics": ["algebra", "probability"],
        "keywords": ["fractions", "fraction", "common denominator"],
    },
    "trigonometry": {
        "title": "Right-Angle Trigonometry",
        "button_label": "Trigonometry",
        "strand": "Math",
        "level": "Years 9-10",
        "summary": "Use sine, cosine, and tangent to connect angles with side lengths in right-angled triangles.",
        "explanation": (
            "SOH-CAH-TOA helps you choose the correct ratio. "
            "Identify the side names relative to the given angle before substituting numbers."
        ),
        "key_points": [
            "Sine uses opposite over hypotenuse.",
            "Cosine uses adjacent over hypotenuse.",
            "Tangent uses opposite over adjacent.",
        ],
        "example": (
            "Find x if sin 30 = x/10\n"
            "sin 30 = opposite / hypotenuse\n"
            "1/2 = x/10\n"
            "x = 5"
        ),
        "common_mistakes": [
            "Using the wrong ratio because the side names were identified incorrectly.",
            "Treating the side opposite one angle as opposite every angle.",
            "Forgetting that SOH-CAH-TOA only applies to right-angled triangles.",
        ],
        "practice_prompts": [
            "learn trigonometry",
            "explain sine cosine and tangent",
            "find x if sin 35 = x/12",
        ],
        "starter_prompt": "find x if sin 35 = x/12",
        "related_topics": ["coordinate_geometry", "linear_graphs"],
        "keywords": ["trigonometry", "sine", "cosine", "tangent", "sohcahtoa"],
    },
    "indices": {
        "title": "Indices and Powers",
        "button_label": "Indices",
        "strand": "Math",
        "level": "Years 8-10",
        "summary": "Use index laws to simplify powers and write expressions more efficiently.",
        "explanation": (
            "Indices describe repeated multiplication. "
            "The laws of indices help combine powers with the same base."
        ),
        "key_points": [
            "a^m x a^n = a^(m+n)",
            "a^m / a^n = a^(m-n)",
            "(a^m)^n = a^(mn)",
        ],
        "example": (
            "Simplify 2^3 x 2^4\n"
            "Same base, so add the powers\n"
            "2^(3+4) = 2^7"
        ),
        "common_mistakes": [
            "Adding powers when the bases are different.",
            "Multiplying powers instead of adding them for repeated bases.",
            "Ignoring brackets in expressions such as (a^2)^3.",
        ],
        "practice_prompts": [
            "simplify 3^2 x 3^5",
            "simplify (x^2)^4",
            "explain the laws of indices",
        ],
        "starter_prompt": "simplify 3^2 x 3^5",
        "related_topics": ["quadratics", "algebra"],
        "keywords": ["indices", "powers", "index laws", "exponents"],
    },
    "quadratics": {
        "title": "Quadratic Equations",
        "button_label": "Quadratics",
        "strand": "Math",
        "level": "Years 9-10",
        "summary": "Solve quadratic equations using standard form, discriminants, and factorisation.",
        "explanation": (
            "A quadratic includes x^2. "
            "Rewrite it as ax^2 + bx + c = 0 before factoring or using the quadratic formula."
        ),
        "key_points": [
            "Write the equation in standard form first.",
            "Check whether it factors cleanly before using the quadratic formula.",
            "Use the discriminant to understand the number of real solutions.",
        ],
        "example": (
            "Solve x^2 - 5x + 6 = 0\n"
            "Factor to (x - 2)(x - 3) = 0\n"
            "So x = 2 or x = 3"
        ),
        "common_mistakes": [
            "Forgetting to move everything to one side before solving.",
            "Dropping one of the two possible roots.",
            "Using the wrong signs when substituting into the quadratic formula.",
        ],
        "practice_prompts": [
            "solve x^2 - 5x + 6 = 0",
            "explain the discriminant in x^2 - 4x + 3 = 0",
            "factor x^2 + 7x + 12",
        ],
        "starter_prompt": "solve x^2 - 5x + 6 = 0",
        "related_topics": ["algebra", "indices", "linear_graphs"],
        "keywords": ["quadratic", "quadratics", "x^2", "parabola"],
    },
    "simultaneous_equations": {
        "title": "Simultaneous Equations",
        "button_label": "Simultaneous Equations",
        "strand": "Math",
        "level": "Years 9-10",
        "summary": "Solve two equations together to find the single pair of values that satisfies both.",
        "explanation": (
            "Simultaneous equations are solved by elimination or substitution. "
            "The solution must make both equations true at the same time."
        ),
        "key_points": [
            "Line up like terms carefully before eliminating a variable.",
            "Substitute the first solution back in to find the second variable.",
            "Check the ordered pair in both original equations.",
        ],
        "example": (
            "Solve x + y = 7 and x - y = 1\n"
            "Add the equations -> 2x = 8\n"
            "x = 4, then y = 3"
        ),
        "common_mistakes": [
            "Adding or subtracting equations with unlike terms not aligned.",
            "Solving for one variable and forgetting to find the other.",
            "Checking the answer in only one equation.",
        ],
        "practice_prompts": [
            "solve x + y = 9 and x - y = 3",
            "show elimination method for 2x + y = 11 and x - y = 1",
            "learn simultaneous equations",
        ],
        "starter_prompt": "solve x + y = 9 and x - y = 3",
        "related_topics": ["algebra", "linear_graphs"],
        "keywords": ["simultaneous equations", "elimination", "substitution"],
    },
    "linear_graphs": {
        "title": "Linear Graphs",
        "button_label": "Linear Graphs",
        "strand": "Math",
        "level": "Years 8-10",
        "summary": "Understand gradient, intercepts, and how equations describe straight lines.",
        "explanation": (
            "A straight line can be written as y = mx + c, where m is the gradient and c is the y-intercept."
        ),
        "key_points": [
            "The gradient shows steepness and direction.",
            "The y-intercept is where the line crosses the y-axis.",
            "Two points are enough to determine a unique straight line.",
        ],
        "example": (
            "For y = 2x + 3, the gradient is 2 and the y-intercept is 3.\n"
            "When x = 0, y = 3 so the line crosses the y-axis at (0, 3)."
        ),
        "common_mistakes": [
            "Confusing the gradient with the intercept.",
            "Swapping x and y values in a table of coordinates.",
            "Using rise over run in the wrong order.",
        ],
        "practice_prompts": [
            "what is the gradient of y = 4x - 7",
            "explain y = mx + c",
            "find the y-intercept of y = -3x + 5",
        ],
        "starter_prompt": "what is the gradient of y = 4x - 7",
        "related_topics": ["coordinate_geometry", "algebra", "quadratics"],
        "keywords": ["linear graphs", "gradient", "y intercept", "straight line"],
    },
    "coordinate_geometry": {
        "title": "Coordinate Geometry",
        "button_label": "Coordinate Geometry",
        "strand": "Math",
        "level": "Years 9-10",
        "summary": "Use coordinates to measure distance, midpoints, and relationships between points and lines.",
        "explanation": (
            "Coordinate geometry combines algebra with graphs. "
            "Use formulas and geometric reasoning on the Cartesian plane."
        ),
        "key_points": [
            "The midpoint lies halfway between two coordinates.",
            "The distance formula comes from Pythagoras' theorem.",
            "Gradients help compare whether lines are parallel or perpendicular.",
        ],
        "example": (
            "Find the midpoint of (2, 5) and (6, 9)\n"
            "((2 + 6)/2, (5 + 9)/2) = (4, 7)"
        ),
        "common_mistakes": [
            "Averaging one coordinate but not the other.",
            "Using subtraction in the wrong order inside formulas.",
            "Forgetting that parallel lines have equal gradients.",
        ],
        "practice_prompts": [
            "find the midpoint of (2, 5) and (6, 9)",
            "what is the distance between (1, 2) and (4, 6)",
            "learn coordinate geometry",
        ],
        "starter_prompt": "find the midpoint of (2, 5) and (6, 9)",
        "related_topics": ["linear_graphs", "trigonometry"],
        "keywords": ["coordinate geometry", "midpoint", "distance formula"],
    },
    "probability": {
        "title": "Probability Basics",
        "button_label": "Probability",
        "strand": "Math",
        "level": "Years 7-10",
        "summary": "Work out the chance of events using outcomes, fractions, and simple sample spaces.",
        "explanation": (
            "Probability measures how likely an event is. "
            "Write it as favourable outcomes over total outcomes."
        ),
        "key_points": [
            "Probability = favourable outcomes / total outcomes",
            "Probabilities range from 0 to 1.",
            "A complete sample space helps avoid missing outcomes.",
        ],
        "example": (
            "What is the probability of rolling a 4 on a fair die?\n"
            "There is 1 favourable outcome out of 6 total outcomes.\n"
            "Probability = 1/6"
        ),
        "common_mistakes": [
            "Using the wrong total number of outcomes.",
            "Confusing probability with prediction or certainty.",
            "Adding probabilities without checking whether events overlap.",
        ],
        "practice_prompts": [
            "what is the probability of rolling an even number on a die",
            "explain sample space",
            "learn probability",
        ],
        "starter_prompt": "what is the probability of rolling an even number on a die",
        "related_topics": ["fractions"],
        "keywords": ["probability", "sample space", "chance"],
    },
}
