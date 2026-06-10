from django.contrib import admin
from .models import User, Category, Question, Exam, ExamQuestion, Result

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(ExamQuestion)
admin.site.register(Result)
