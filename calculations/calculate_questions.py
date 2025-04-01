import urllib


def calculate_marks_alternate(questions, request, student,exam_models):
    """Calculates the total marks obtained by a student in an exam based on their answers. """
    for i, question in enumerate(questions, start=1):
        if question.is_mcq():
            selected_ans = request.COOKIES.get(str(i))  # Gets student's answer from cookie
            if selected_ans:
                selected_ans = urllib.parse.unquote(selected_ans)  # Decode the cookie value
                if selected_ans == question.answer:
                    total_marks += question.marks
        else:  # SAQ
            student_answer = request.COOKIES.get(f"{i}_saq")
            if student_answer:
                student_answer = urllib.parse.unquote(student_answer)  # Decode the cookie value
                exam_models.StudentAnswer.objects.create(  # Creates record for teacher to grade SAQ
                    student=student,
                    question=question,
                    answer_text=student_answer,
                    is_graded=False
                )
    return None