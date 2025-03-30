from django.db import models

from student.models import Student
class Course(models.Model):
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()  # Total number of questions in the course
   total_marks = models.PositiveIntegerField()
   def __str__(self):
        return self.course_name

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('saq', 'Short Answer'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Links question to specific course, deletes questions if course is deleted
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='mcq')  # Determines if question is MCQ or SAQ
    option1 = models.CharField(max_length=200, null=True, blank=True)
    option2 = models.CharField(max_length=200, null=True, blank=True)
    option3 = models.CharField(max_length=200, null=True, blank=True)
    option4 = models.CharField(max_length=200, null=True, blank=True)
    cat = (('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer = models.CharField(max_length=1000)  # Increased length for SAQ answers
    max_words = models.PositiveIntegerField(null=True, blank=True, help_text='Maximum words for SAQ answers')

    def __str__(self):
        return f"{self.question} ({self.question_type})"

    def is_mcq(self):
        return self.question_type == 'mcq'

    def is_saq(self):
        return self.question_type == 'saq'

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()  # Stores the marks obtained by student
    date = models.DateTimeField(auto_now=True)  # Automatically records submission time

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()  # Stores student's written answer for SAQ
    is_graded = models.BooleanField(default=False)  # Tracks if teacher has graded the answer
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)  # Marks given by teacher for SAQ
    graded_by = models.ForeignKey('teacher.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Answer by {self.student} for {self.question}"

