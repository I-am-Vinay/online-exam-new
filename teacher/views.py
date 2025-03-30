from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as exam_models
from student import models as student_models
from exam import forms as exam_forms
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)  # Hashes the password before saving
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user  # Links teacher profile to user account
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')  # Creates teacher group if not exists
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()  # Verifies if user belongs to teacher group

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={
    'total_student':student_models.Student.objects.all().count()  # Gets total count of registered students
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=exam_forms.CourseForm()
    if request.method=='POST':
        courseForm=exam_forms.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()  # Creates new exam/course
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = exam_models.Course.objects.all()  # Retrieves all courses for display
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=exam_models.Course.objects.get(id=pk)
    course.delete()  # Deletes the specified course and its related questions
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=exam_forms.QuestionForm()
    if request.method=='POST':
        questionForm=exam_forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=exam_models.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course  # Associates question with specific course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses = exam_models.Course.objects.all()
    
    # Calculate actual totals for each course
    for course in courses:
        course.actual_question_count = exam_models.Question.objects.filter(course=course).count()
        course.actual_total_marks = exam_models.Question.objects.filter(course=course).aggregate(Sum('marks'))['marks__sum'] or 0
    
    # Handle SAQ grading if POST request
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        marks = request.POST.get('marks')
        if answer_id and marks:
            student_answer = exam_models.StudentAnswer.objects.get(id=answer_id)
            student_answer.marks_obtained = marks
            student_answer.is_graded = True
            student_answer.graded_by = models.Teacher.objects.get(user_id=request.user.id)
            student_answer.save()
            
            # Get the most recent result for this student and course
            result = exam_models.Result.objects.filter(
                student=student_answer.student,
                exam=student_answer.question.course
            ).order_by('-id').first()
            
            if result:
                result.marks += int(marks)
                result.save()
            
            return HttpResponseRedirect('/teacher/teacher-view-question')
    
    # Get ungraded SAQ answers
    ungraded_answers = exam_models.StudentAnswer.objects.filter(is_graded=False)
    
    return render(request,'teacher/teacher_view_question.html',{
        'courses': courses,
        'ungraded_answers': ungraded_answers
    })

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=exam_models.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=exam_models.Question.objects.get(id=pk)
    course_id = question.course.id  # Get the course ID before deleting
    question.delete()
    return HttpResponseRedirect(f'/teacher/see-question/{course_id}')

class TeacherLoginView(LoginView):
    template_name = 'teacher/teacherlogin.html'
    success_url = reverse_lazy('afterlogin')

    def form_valid(self, form):
        user = form.get_user()
        if not user.groups.filter(name='TEACHER').exists():
            form.add_error(None, "This account is not authorized to access the teacher portal.")
            return self.form_invalid(form)
        return super().form_valid(form)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_students_view(request):
    students = student_models.Student.objects.all()
    return render(request, 'teacher/teacher_view_students.html', {'students': students})
