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
        "function",
        "polynomial",
        "piecewise",
        "absolute value",
        "transformation",
        "circle",
        "radian",
        "identity",
        "exponential",
        "logarithm",
        "logarithmic",
        "calculus",
        "limit",
        "derivative",
        "differentiate",
        "rate of change",
        "statistics",
        "random variable",
        "variance",
        "standard deviation",
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
        "Ask how to use this platform",
        "Solve 2x + 4 = 10",
        "Practice problem",
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
    "algebra_functions": {
        "title": "Algebra and Functions",
        "button_label": "Algebra and Functions",
        "strand": "Senior Mathematics",
        "level": "Years 10-11",
        "summary": "Extend algebra into polynomials, piecewise rules, absolute values, and graph transformations.",
        "explanation": (
            "A function connects each input to an output. Senior algebra focuses "
            "on how different rules change the shape, domain, intercepts, and "
            "turning points of a graph."
        ),
        "key_points": [
            "Use function notation such as f(x) to describe input-output rules.",
            "Transformations like f(x) + k, f(x - h), and -f(x) move or reflect graphs.",
            "Piecewise functions use different rules on different parts of the domain.",
        ],
        "example": (
            "For f(x) = |x - 2| + 1\n"
            "Start with y = |x|\n"
            "x - 2 shifts the graph 2 units right\n"
            "+ 1 shifts the graph 1 unit up\n"
            "The vertex is (2, 1)"
        ),
        "common_mistakes": [
            "Moving a graph left when the expression x - h actually shifts it right.",
            "Ignoring domain restrictions in piecewise functions.",
            "Treating f(x) as multiplication instead of function notation.",
        ],
        "practice_prompts": [
            "learn algebra and functions",
            "revise graph transformations",
            "study piecewise functions",
        ],
        "starter_prompt": "learn algebra and functions",
        "related_topics": ["quadratics", "linear_graphs", "exponential_logarithmic_functions"],
        "keywords": [
            "algebra and functions",
            "functions",
            "polynomials",
            "piecewise",
            "absolute value",
            "graph transformations",
        ],
    },
    "senior_coordinate_geometry": {
        "title": "Senior Coordinate Geometry",
        "button_label": "Senior Coordinate Geometry",
        "strand": "Senior Mathematics",
        "level": "Years 10-11",
        "summary": "Use point-gradient form, equations of lines, and circle equations on the Cartesian plane.",
        "explanation": (
            "Coordinate geometry translates geometric relationships into algebraic "
            "equations, so lines, circles, distances, and gradients can be solved systematically."
        ),
        "key_points": [
            "Point-gradient form is y - y1 = m(x - x1).",
            "A circle with centre (a, b) and radius r has equation (x - a)^2 + (y - b)^2 = r^2.",
            "Perpendicular lines have gradients whose product is -1.",
        ],
        "example": (
            "Find the line through (2, 5) with gradient 3\n"
            "Use y - y1 = m(x - x1)\n"
            "y - 5 = 3(x - 2)\n"
            "y = 3x - 1"
        ),
        "common_mistakes": [
            "Substituting the point into point-gradient form in the wrong order.",
            "Forgetting to square the radius in a circle equation.",
            "Using the same gradient for perpendicular lines instead of the negative reciprocal.",
        ],
        "practice_prompts": [
            "learn senior coordinate geometry",
            "revise circle equations",
            "study point gradient form",
        ],
        "starter_prompt": "learn senior coordinate geometry",
        "related_topics": ["coordinate_geometry", "linear_graphs", "algebra_functions"],
        "keywords": [
            "senior coordinate geometry",
            "point gradient",
            "point-gradient",
            "circle equation",
            "equation of a line",
        ],
    },
    "advanced_trigonometry": {
        "title": "Advanced Trigonometry",
        "button_label": "Advanced Trigonometry",
        "strand": "Senior Mathematics",
        "level": "Years 10-11",
        "summary": "Move beyond right triangles into radian measure, identities, and trigonometric equations.",
        "explanation": (
            "Advanced trigonometry treats sine, cosine, and tangent as functions. "
            "Radians connect angle size directly to arc length, and identities help "
            "rewrite expressions into equivalent forms."
        ),
        "key_points": [
            "pi radians equals 180 degrees.",
            "The identity sin^2(x) + cos^2(x) = 1 is central.",
            "Trigonometric equations often have multiple solutions over a given interval.",
        ],
        "example": (
            "Convert 60 degrees to radians\n"
            "60 degrees x pi/180 = pi/3 radians"
        ),
        "common_mistakes": [
            "Mixing degrees and radians in the same calculation.",
            "Finding only one solution to a trigonometric equation over an interval.",
            "Using an identity in only one direction without checking equivalence.",
        ],
        "practice_prompts": [
            "learn advanced trigonometry",
            "revise radian measure",
            "study trigonometric identities",
        ],
        "starter_prompt": "learn advanced trigonometry",
        "related_topics": ["trigonometry", "algebra_functions", "calculus_intro"],
        "keywords": [
            "advanced trigonometry",
            "radians",
            "radian measure",
            "trigonometric identities",
            "trig equations",
        ],
    },
    "exponential_logarithmic_functions": {
        "title": "Exponential and Logarithmic Functions",
        "button_label": "Exponentials and Logarithms",
        "strand": "Senior Mathematics",
        "level": "Years 10-11",
        "summary": "Model growth and decay using exponential functions and their logarithmic inverses.",
        "explanation": (
            "Exponential functions model repeated multiplication, while logarithms "
            "answer the inverse question: what power produces this value?"
        ),
        "key_points": [
            "Exponential growth has the form y = a*b^x with b > 1.",
            "Exponential decay has 0 < b < 1.",
            "log_b(x) asks for the exponent needed to make b^exponent = x.",
        ],
        "example": (
            "If y = 100(1.05)^t\n"
            "The starting value is 100\n"
            "The growth factor is 1.05\n"
            "This represents 5 percent growth per time period"
        ),
        "common_mistakes": [
            "Confusing the starting value with the growth factor.",
            "Treating logarithms as ordinary division.",
            "Using a negative or zero input inside a real logarithm.",
        ],
        "practice_prompts": [
            "learn exponential and logarithmic functions",
            "study growth and decay models",
            "revise logarithm laws",
        ],
        "starter_prompt": "learn exponential and logarithmic functions",
        "related_topics": ["indices", "algebra_functions", "calculus_intro"],
        "keywords": [
            "exponential",
            "exponential functions",
            "logarithm",
            "logarithmic",
            "growth and decay",
        ],
    },
    "calculus_intro": {
        "title": "Introduction to Calculus",
        "button_label": "Introduction to Calculus",
        "strand": "Senior Mathematics",
        "level": "Year 11",
        "summary": "Understand limits, derivatives, rates of change, and basic differentiation rules.",
        "explanation": (
            "Calculus studies change. A derivative measures the instantaneous rate "
            "of change of a function, which is also the gradient of the tangent at a point."
        ),
        "key_points": [
            "A limit describes what a function approaches near a value.",
            "The derivative f'(x) gives the gradient function.",
            "The power rule says d/dx x^n = n*x^(n-1) for many polynomial terms.",
        ],
        "example": (
            "Differentiate f(x) = x^3 + 2x\n"
            "d/dx x^3 = 3x^2\n"
            "d/dx 2x = 2\n"
            "So f'(x) = 3x^2 + 2"
        ),
        "common_mistakes": [
            "Thinking an average rate of change is the same as an instantaneous rate.",
            "Dropping the coefficient when using the power rule.",
            "Forgetting that constants differentiate to 0.",
        ],
        "practice_prompts": [
            "learn introduction to calculus",
            "study derivatives and rates of change",
            "revise first principles",
        ],
        "starter_prompt": "learn introduction to calculus",
        "related_topics": ["algebra_functions", "advanced_trigonometry", "exponential_logarithmic_functions"],
        "keywords": [
            "calculus",
            "limits",
            "limit",
            "derivative",
            "differentiate",
            "rates of change",
            "first principles",
        ],
    },
    "statistics_probability": {
        "title": "Statistics and Probability",
        "button_label": "Statistics and Probability",
        "strand": "Senior Mathematics",
        "level": "Years 10-11",
        "summary": "Work with random variables, spread, and multi-stage probability experiments.",
        "explanation": (
            "Statistics describes data, while probability models uncertainty. Senior "
            "questions often combine expected value, variance, standard deviation, "
            "and tree diagrams."
        ),
        "key_points": [
            "A discrete random variable has listed outcomes with assigned probabilities.",
            "Variance measures average squared spread from the mean.",
            "Tree diagrams help organise multi-stage probability experiments.",
        ],
        "example": (
            "For X with values 0, 1, 2 and probabilities 0.2, 0.5, 0.3\n"
            "E(X) = 0(0.2) + 1(0.5) + 2(0.3)\n"
            "E(X) = 1.1"
        ),
        "common_mistakes": [
            "Forgetting that probabilities must add to 1.",
            "Using standard deviation when the question asks for variance.",
            "Adding probabilities in a tree diagram when multiplication is needed for a sequence.",
        ],
        "practice_prompts": [
            "learn statistics and probability",
            "study standard deviation",
            "revise discrete random variables",
        ],
        "starter_prompt": "learn statistics and probability",
        "related_topics": ["probability", "fractions"],
        "keywords": [
            "statistics",
            "statistics and probability",
            "random variable",
            "discrete random variables",
            "variance",
            "standard deviation",
            "multi-stage probability",
        ],
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
