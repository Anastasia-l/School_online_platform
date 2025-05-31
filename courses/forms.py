from django import forms
from .models import Course, Lesson, Quiz, Question


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_published']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'order', 'file']


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'correct_answer', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'order': forms.NumberInput(attrs={'min': 1})
        }
