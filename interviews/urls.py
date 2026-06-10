from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    # Auth
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),

    # Main
    path('', views.index, name='index'),

    # Exam
    path('exam/new', views.new_exam, name='new_exam'),
    path('exam/<int:exam_id>', views.exam, name='exam'),
    path('exam/<int:exam_id>/result', views.result, name='result'),

    # API (chamadas via fetch/JavaScript)
    path('api/submit', views.submit_exam, name='submit_exam'),

    # Histórico e estatísticas
    path('history', views.history, name='history'),
    path('stats', views.stats, name='stats'),
]
