from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as exam_models
from teacher import models as teacher_models
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import urllib.parse

def logout_student(request):
    logout(request)  # Clears all session data for security
    return redirect('studentlogin')

def landing_page(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def register_student(request):
    user_form = forms.StudentUserForm()
    profile_form = forms.StudentForm()
    context = {
        'userForm': user_form,
        'studentForm': profile_form
    }
    
    if request.method == 'POST':
        user_form = forms.StudentUserForm(request.POST)
        profile_form = forms.StudentForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)  # Hashes the password for security
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user  # Links the profile to the user account
            profile.save()
            
            student_group, _ = Group.objects.get_or_create(name='STUDENT')  # Ensures student group exists
            student_group.user_set.add(user)
            
            return HttpResponseRedirect('studentlogin')
    return render(request, 'student/studentsignup.html', context=context)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def dashboard(request):
    context = {
        'total_course': exam_models.Course.objects.all().count(),
        'total_question': exam_models.Question.objects.all().count(),
    }
    return render(request, 'student/student_dashboard.html', context=context)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def available_exams(request):
    courses = exam_models.Course.objects.all()
    return render(request, 'student/student_exam.html', {'courses': courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def exam_details(request, pk):
    course = exam_models.Course.objects.get(id=pk)
    questions = exam_models.Question.objects.filter(course=course)
    total_marks = sum(question.marks for question in questions)
    context = {
        'course': course,
        'total_questions': questions.count(),
        'total_marks': total_marks
    }
    return render(request, 'student/take_exam.html', context)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam(request, pk):
    course = exam_models.Course.objects.get(id=pk)
    questions = exam_models.Question.objects.filter(course=course)
    response = render(request, 'student/start_exam.html', {
        'course': course,
        'questions': questions
    })
    response.set_cookie('course_id', course.id)  # Stores course ID in cookie for exam session
    return response

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks(request):
    if not request.COOKIES.get('course_id'):
        return HttpResponseRedirect('view-result')
        
    course_id = request.COOKIES.get('course_id')
    course = exam_models.Course.objects.get(id=course_id)
    student = models.Student.objects.get(user_id=request.user.id)
    questions = exam_models.Question.objects.filter(course=course)
    
    total_marks = 0
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
    
    # Create and save the result with total marks
    result = exam_models.Result(
        exam=course,
        student=student,
        marks=total_marks
    )
    result.save()
    
    return HttpResponseRedirect('view-result')

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_results(request):
    courses = exam_models.Course.objects.all()
    return render(request, 'student/view_result.html', {'courses': courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks(request, pk):
    course = exam_models.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results = exam_models.Result.objects.filter(exam=course, student=student)
    return render(request, 'student/check_marks.html', {'results': results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_marks(request):
    courses = exam_models.Course.objects.all()
    return render(request, 'student/student_marks.html', {'courses': courses})

class StudentLoginView(LoginView):
    template_name = 'student/studentlogin.html'
    success_url = reverse_lazy('afterlogin')

    def form_valid(self, form):
        user = form.get_user()
        if not user.groups.filter(name='STUDENT').exists():
            form.add_error(None, "This account is not authorized to access the student portal.")
            return self.form_invalid(form)
        return super().form_valid(form)
  