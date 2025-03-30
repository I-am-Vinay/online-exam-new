from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from teacher import models as teacher_models
from student import models as student_models
from teacher import forms as teacher_forms
from student import forms as student_forms
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


def home_view(request):
    if request.user.is_authenticated:  # Checks if user is already logged in to redirect to dashboard
        return HttpResponseRedirect('afterlogin')  
    return render(request,'exam/index.html')


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()  # Verifies if the user belongs to teacher group

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()  # Verifies if the user belongs to student group

def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student/student-dashboard')
                
    elif is_teacher(request.user):
        accountapproval=teacher_models.Teacher.objects.all().filter(user_id=request.user.id,status=True)  # Checks if teacher account is approved
        if accountapproval:
            return redirect('teacher/teacher-dashboard')
        else:
            return render(request,'teacher/teacher_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
    'total_student':student_models.Student.objects.all().count(),  # Gets total count of registered students
    'total_teacher':teacher_models.Teacher.objects.all().filter(status=True).count(),
    'total_course':models.Course.objects.all().count(),
    'total_question':models.Question.objects.all().count(),
    }
    return render(request,'exam/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    dict={
    'total_teacher':teacher_models.Teacher.objects.all().filter(status=True).count(),
    'pending_teacher':teacher_models.Teacher.objects.all().filter(status=False).count(),  # Gets count of teachers waiting for approval
    'salary':teacher_models.Teacher.objects.all().filter(status=True).aggregate(Sum('salary'))['salary__sum'],
    }
    return render(request,'exam/admin_teacher.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    teachers= teacher_models.Teacher.objects.all().filter(status=True)
    return render(request,'exam/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def update_teacher_view(request,pk):
    teacher=teacher_models.Teacher.objects.get(id=pk)
    user=teacher_models.User.objects.get(id=teacher.user_id)
    userForm=teacher_forms.TeacherUserForm(instance=user)
    teacherForm=teacher_forms.TeacherForm(request.FILES,instance=teacher)
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=teacher_forms.TeacherUserForm(request.POST,instance=user)
        teacherForm=teacher_forms.TeacherForm(request.POST,request.FILES,instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    return render(request,'exam/update_teacher.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_teacher_view(request,pk):
    teacher=teacher_models.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')




@login_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    teachers= teacher_models.Teacher.objects.all().filter(status=False)
    return render(request,'exam/admin_view_pending_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def approve_teacher_view(request,pk):
    teacherSalary=forms.TeacherSalaryForm()
    if request.method=='POST':
        teacherSalary=forms.TeacherSalaryForm(request.POST)
        if teacherSalary.is_valid():
            teacher=teacher_models.Teacher.objects.get(id=pk)
            teacher.salary=teacherSalary.cleaned_data['salary']
            teacher.status=True
            teacher.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-pending-teacher')
    return render(request,'exam/salary_form.html',{'teacherSalary':teacherSalary})

@login_required(login_url='adminlogin')
def reject_teacher_view(request,pk):
    teacher=teacher_models.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')

@login_required(login_url='adminlogin')
def admin_view_teacher_salary_view(request):
    teachers= teacher_models.Teacher.objects.all().filter(status=True)
    return render(request,'exam/admin_view_teacher_salary.html',{'teachers':teachers})




@login_required(login_url='adminlogin')
def admin_student_view(request):
    dict={
    'total_student':student_models.Student.objects.all().count(),
    }
    return render(request,'exam/admin_student.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students= student_models.Student.objects.all()
    return render(request,'exam/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
def update_student_view(request,pk):
    student=student_models.Student.objects.get(id=pk)
    user=student_models.User.objects.get(id=student.user_id)
    userForm=student_forms.StudentUserForm(instance=user)
    studentForm=student_forms.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=student_forms.StudentUserForm(request.POST,instance=user)
        studentForm=student_forms.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request,'exam/update_student.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student=student_models.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_course_view(request):
    return render(request,'exam/admin_course.html')


@login_required(login_url='adminlogin')
def admin_add_course_view(request):
    courseForm=forms.CourseForm()
    if request.method=='POST':
        courseForm=forms.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-course')
    return render(request,'exam/admin_add_course.html',{'courseForm':courseForm})


@login_required(login_url='adminlogin')
def admin_view_course_view(request):
    courses = models.Course.objects.all()
    for course in courses:
        # Calculate actual number of questions
        course.actual_question_count = models.Question.objects.filter(course=course).count()
        # Calculate actual total marks
        course.actual_total_marks = models.Question.objects.filter(course=course).aggregate(Sum('marks'))['marks__sum'] or 0
    return render(request,'exam/admin_view_course.html',{'courses':courses})

@login_required(login_url='adminlogin')
def delete_course_view(request,pk):
    course=models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/admin-view-course')



@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'exam/admin_question.html')


@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm=forms.QuestionForm()
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=models.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-question')
    return render(request,'exam/admin_add_question.html',{'questionForm':questionForm})


@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    courses = models.Course.objects.all()
    for course in courses:
        # Calculate actual number of questions
        course.actual_question_count = models.Question.objects.filter(course=course).count()
        # Calculate actual total marks
        course.actual_total_marks = models.Question.objects.filter(course=course).aggregate(Sum('marks'))['marks__sum'] or 0
    return render(request,'exam/admin_view_question.html',{'courses':courses})

@login_required(login_url='adminlogin')
def view_question_view(request,pk):
    questions=models.Question.objects.all().filter(course_id=pk)
    return render(request,'exam/view_question.html',{'questions':questions})

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    students = student_models.Student.objects.all()
    marks = models.Result.objects.all().select_related('student', 'exam')
    return render(request,'exam/admin_view_student_marks.html',{'students':students, 'marks':marks})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    courses = models.Course.objects.all()
    response =  render(request,'exam/admin_view_marks.html',{'courses':courses})
    response.set_cookie('student_id',str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request,pk):
    course = models.Course.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    student= student_models.Student.objects.get(id=student_id)

    results= models.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'exam/admin_check_marks.html',{'results':results})
    




def aboutus_view(request):
    return render(request,'exam/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'exam/contactussuccess.html')
    return render(request, 'exam/contactus.html', {'form':sub})

def logout_view(request):
    auth_logout(request)
    return redirect('/')

def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = models.Course.objects.get(id=course_id)
        
        total_marks = 0
        questions = models.Question.objects.all().filter(course=course)
        student = student_models.Student.objects.get(user_id=request.user.id)
        
        result = models.Result()
        result.exam = course
        result.student = student
        
        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i+1))  # Retrieves student's answer from cookies for each question
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks  # Accumulates marks for correct answers
        result.marks = total_marks
        result.save()
        return HttpResponseRedirect('view-result')

class AdminLoginView(LoginView):
    template_name = 'exam/adminlogin.html'
    success_url = reverse_lazy('afterlogin')

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser:
            form.add_error(None, "This account is not authorized to access the admin portal.")
            return self.form_invalid(form)
        return super().form_valid(form)


