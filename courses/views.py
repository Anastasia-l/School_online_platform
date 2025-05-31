from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, UserProgress, Lesson, Quiz
from .forms import CourseForm, LessonForm, QuizForm, QuestionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied

CustomUser = get_user_model()


# Create your views here.
@login_required
def course_list(request):
    all_courses = Course.objects.filter(is_published=True).select_related('teacher')

    # Пагинация
    paginator = Paginator(all_courses, 5)
    page_number = request.GET.get('page')

    try:
        courses = paginator.page(page_number)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course.objects.select_related('teacher'), pk=course_id)
    # Меню завершенных уроков курса
    completed_lessons = list(UserProgress.objects.filter(
        user=request.user,
        lesson__course=course
    ).values_list('lesson_id', flat=True))
    # Проверяем запись текущего пользователя на курс
    is_teacher = request.user == course.teacher
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    # Показываем уроки только записанным студентам
    lessons = course.lessons.all().order_by('order') if is_teacher or is_enrolled else None

    # Рассчитываем прогресс
    total_lessons = lessons.count() if lessons else 0
    completed_count = len(completed_lessons)
    progress_percent = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0

    return render(request, "courses/course_detail.html", {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher,
        'progress_percent': progress_percent,
        'total_lessons': total_lessons,
        'completed_count': completed_count,
        'completed_lessons': completed_lessons
    })


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=lesson_id)
    progress = None

    if request.user.is_authenticated:
        progress = UserProgress.objects.filter(
            user=request.user,
            lesson=lesson
        ).first()

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'progress': progress
    })


@login_required
def create_course(request):
    if request.user.role != get_user_model().TEACHER:
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('courses:course_detail', course_id=course.id)

        else:
            form = CourseForm()
        return render(request, 'courses/create_course.html', {'form': form})


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        if request.user == course.teacher:
            return redirect('courses:course_detail', course_id=course.id)

        Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )

    return redirect('courses:course_detail', course_id=course.id)


@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.method == 'POST':
        UserProgress.objects.update_or_create(user=request.user, lesson=lesson, defaults={'score': 100})
    return redirect('courses:lesson_detail', lesson_id=lesson.id)


# Добавление возможности учителям добавлять контент к курсам (и только учителям!)

def check_teacher_access(user, course):
    try:
        if user.role != get_user_model().TEACHER or course.teacher_id != user.id:
            raise PermissionDenied
    except AttributeError:
        raise PermissionDenied


@login_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    check_teacher_access(request.user, course)

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course  # Привязка урока к конкретному курсу
            lesson.save()
            return redirect('courses:course_detail', course_id=course.id)
        return render(request, 'courses/create_lesson.html', {
            "form": form,
            "course": course
        })
    else:
        form = LessonForm()
        return render(request, 'courses/create_lesson.html', {
            "form": form,
            "course": course
        })


@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    check_teacher_access(request.user, lesson.course)

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('courses:lesson_detail', lesson_id=lesson.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'courses/edit_lesson.html', {"form": form, "lesson": lesson})


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    check_teacher_access(request.user, lesson.course)

    if request.method == "POST":
        course_id = lesson.course.id
        lesson.delete()
        return redirect('courses:course_detail', course_id=course_id)

    return render(request, 'courses/delete_lesson.html', {"lesson": lesson})


@login_required
def add_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    check_teacher_access(request.user, lesson.course)

    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()
            return redirect("courses:quiz_detail", quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'courses/add_quiz.html', {'form': form, 'lesson': lesson})


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    return render(request, 'courses/quiz_detail.html', {
        'quiz': quiz,
        'questions': quiz.questions.all().order_by('order')
    })


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    check_teacher_access(request.user, quiz.lesson.course)

    next_order = quiz.questions.count() + 1

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.order = next_order
            question.save()
            return redirect("courses:quiz_detail", quiz_id=quiz.id)
    else:
        form = QuestionForm(initial={'order': next_order})

    return render(request, 'courses/add_question.html', {'form': form, 'quiz': quiz})

