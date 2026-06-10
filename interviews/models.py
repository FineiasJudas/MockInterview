from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Meta:
        app_label = 'interviews'

class Category(models.Model):
    name = models.CharField(max_length=64)  # React, Django, SQL, JavaScript, etc.
    icon = models.CharField(max_length=64, blank=True)  # ex: "fab fa-react"

    def __str__(self):
        return self.name


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=256)
    option_b = models.CharField(max_length=256)
    option_c = models.CharField(max_length=256)
    option_d = models.CharField(max_length=256)
    correct_option = models.CharField(max_length=1)  # 'a', 'b', 'c' ou 'd'
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    explanation = models.TextField(blank=True)  # explicação da resposta correta

    def get_options(self):
        return [
            ('a', self.option_a),
            ('b', self.option_b),
            ('c', self.option_c),
            ('d', self.option_d),
        ]

    def __str__(self):
        return f"[{self.category.name}] {self.text[:50]}"


class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    duration_seconds = models.IntegerField(default=0)  # tempo gasto pelo utilizador

    def __str__(self):
        return f"Exam #{self.id} by {self.user.username}"


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_given = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Exam #{self.exam.id} - Question #{self.question.id}"


class Result(models.Model):
    exam = models.OneToOneField(Exam, on_delete=models.CASCADE, related_name='result')
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    score_percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for Exam #{self.exam.id} - {self.score_percentage}%"
