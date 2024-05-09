#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

def draw_questions(question_types, num_questions_per_type):
    """
    Draw 3 questions from N types of questions, with 1 question from each type.

    Args:
        question_types (list): List of N types of questions (e.g. ["math", "science", "history"])
        num_questions_per_type (dict): Dictionary mapping each question type to the number of questions (e.g. {"math": 5, "science": 3, "history": 4})

    Returns:
        list: List of 3 questions, one from each of the randomly selected types
    """
    # Randomly select 3 question types
    selected_types = random.sample(question_types, 3)

    # Draw 1 question from each of the selected types
    questions = []
    for question_type in selected_types:
        num_questions = num_questions_per_type[question_type]
        question_index = random.randint(0, num_questions - 1)
        question = f"{question_type}_{question_index + 1}"  # e.g. "math_1", "science_2", etc.
        questions.append(question)

    return questions

question_types = ["cp1", "cp2", "cp3", "cp4", "cp5", "cp6"]
num_questions_per_type = {"cp1": 9, "cp2": 10, "cp3": 7, "cp4": 12, "cp5": 10, "cp6":1}

questions = draw_questions(question_types, num_questions_per_type)
print(questions)  # e.g. ["math_2", "science_1", "history_3"]
