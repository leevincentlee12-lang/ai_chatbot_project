"""Science-topic tutoring responses."""

import re

from utils.formatting import _build_explanation, _format_value


def handle_science(question):
    """Handle science-related questions with formula-based explanations."""
    q_lower = (question or "").lower()
    numbers = [float(match) for match in re.findall(r"-?\d+(?:\.\d+)?", q_lower)]

    if "force" in q_lower and "mass" in q_lower and "acceleration" in q_lower:
        if len(numbers) >= 2:
            mass = numbers[0]
            acceleration = numbers[1]
            force = mass * acceleration
            return _build_explanation(
                answer=f"Force = {_format_value(force)} N",
                method=(
                    "Use the formula F = ma.\n"
                    f"Substitute the values: F = {mass} x {acceleration}"
                ),
                why="Force increases when mass increases, acceleration increases, or both.",
                check="The unit for force is newtons (N).",
                next_step="If you want, I can rearrange the same formula to solve for mass or acceleration.",
            )
        return "Provide both mass and acceleration values."

    if "velocity" in q_lower and "acceleration" in q_lower:
        if len(numbers) >= 3:
            initial_velocity = numbers[0]
            acceleration = numbers[1]
            time = numbers[2]
            final_velocity = initial_velocity + acceleration * time
            return _build_explanation(
                answer=f"Final velocity = {_format_value(final_velocity)}",
                method=(
                    "Use v = u + at.\n"
                    f"Substitute: v = {initial_velocity} + ({acceleration} x {time})"
                ),
                why="Acceleration changes velocity over time, so the velocity shifts by a x t.",
                check="Make sure the time unit matches the acceleration unit.",
                next_step="Ask me to rearrange the formula if you want to solve for time or acceleration.",
            )
        return "Provide initial velocity, acceleration, and time."

    if "density" in q_lower:
        return _build_explanation(
            answer="Density = mass / volume",
            why="Density tells you how much mass is packed into a given space.",
            next_step="Send me the mass and volume if you want me to calculate it.",
        )

    if "photosynthesis" in q_lower:
        return _build_explanation(
            answer="Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
            method="Word equation: carbon dioxide + water -> glucose + oxygen",
            why="Plants use light energy to store energy in glucose.",
            check="The balanced chemical equation is 6CO2 + 6H2O -> C6H12O6 + 6O2.",
            next_step="Ask for the process in simple steps if you want a Year 7 style explanation.",
        )

    return "Specify the science formula or concept you want help with."
