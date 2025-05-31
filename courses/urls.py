from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('create/', views.create_course, name='create_course'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('complete/<int:lesson_id>/', views.complete_lesson, name='complete_lesson'),
    path('course/<int:course_id>/add-lesson/', views.create_lesson, name='create_lesson'),
    path('lesson/<int:lesson_id>/add-quiz/', views.add_quiz, name='add_quiz'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name="quiz_detail"),
    path('quiz/<int:quiz_id>/add_question', views.add_question, name='add_question'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name="edit_lesson"),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name="delete_lesson"),

]
