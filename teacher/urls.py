from django.urls import path
from . import views

urlpatterns = [
path('teacherclick', views.teacherclick_view),
path('teacherlogin', views.TeacherLoginView.as_view(),name='teacherlogin'),  # Custom login view for teachers
path('teachersignup', views.teacher_signup_view,name='teachersignup'),
path('teacher-dashboard', views.teacher_dashboard_view,name='teacher-dashboard'),
path('teacher-exam', views.teacher_exam_view,name='teacher-exam'),
path('teacher-add-exam', views.teacher_add_exam_view,name='teacher-add-exam'),  # Form to create new exam
path('teacher-view-exam', views.teacher_view_exam_view,name='teacher-view-exam'),
path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),  # Dynamic URL to delete specific exam
path('teacher-question', views.teacher_question_view,name='teacher-question'),
path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),  # Form to add questions to exam
path('teacher-view-question', views.teacher_view_question_view,name='teacher-view-question'),
path('see-question/<int:pk>', views.see_question_view,name='see-question'),  # Shows questions for specific exam
path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),  # Removes specific question
path('teacher-view-students', views.teacher_view_students_view,name='teacher-view-students'),  # New URL for viewing students
]