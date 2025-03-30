from django import forms
from django.contrib.auth.models import User
from . import models

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

class TeacherSalaryForm(forms.Form):
    salary=forms.IntegerField()  # Form for admin to set teacher salary

class CourseForm(forms.ModelForm):
    class Meta:
        model=models.Course
        fields=['course_name','question_number','total_marks']  # Fields for creating new course/exam

class QuestionForm(forms.ModelForm):
    courseID = forms.ModelChoiceField(queryset=models.Course.objects.all(), empty_label="Course Name", to_field_name="id")  # Dropdown to select course for question
    
    class Meta:
        model = models.Question
        fields = ['question_type', 'marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer', 'max_words']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'answer': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'option1': forms.TextInput(attrs={'class': 'mcq-field'}),  # Styling for MCQ options
            'option2': forms.TextInput(attrs={'class': 'mcq-field'}),
            'option3': forms.TextInput(attrs={'class': 'mcq-field'}),
            'option4': forms.TextInput(attrs={'class': 'mcq-field'}),
            'max_words': forms.NumberInput(attrs={'class': 'saq-field'}),  # For SAQ word limit
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option1'].required = False  # Makes MCQ fields optional for SAQ questions
        self.fields['option2'].required = False
        self.fields['option3'].required = False
        self.fields['option4'].required = False
        self.fields['max_words'].required = False
