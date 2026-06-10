from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json
import random
from .models import User, Category, Question, Exam, ExamQuestion, Result


# ─── Auth ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('interviews:index'))
        return render(request, 'interviews/login.html', {'message': 'Invalid credentials.'})
    return render(request, 'interviews/login.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('interviews:index'))


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']

        if password != confirmation:
            return render(request, 'interviews/register.html', {'message': 'Passwords must match.'})
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'interviews/register.html', {'message': 'Username already taken.'})

        login(request, user)
        return HttpResponseRedirect(reverse('interviews:index'))
    return render(request, 'interviews/register.html')


# ─── Main ─────────────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'interviews/index.html', {
        'categories': Category.objects.all()
    })


# ─── Exam ─────────────────────────────────────────────────────────────────────

@login_required
def new_exam(request):
    """Utilizador escolhe as categorias e o número de perguntas."""
    if request.method == 'POST':
        category_ids = request.POST.getlist('categories')
        num_questions = int(request.POST.get('num_questions', 10))

        if not category_ids:
            return render(request, 'interviews/new_exam.html', {
                'categories': Category.objects.all(),
                'message': 'Select at least one category.'
            })

        # Cria o exame
        exam = Exam.objects.create(user=request.user)
        categories = Category.objects.filter(id__in=category_ids)
        exam.categories.set(categories)
        exam.save()

        # Gera perguntas aleatórias das categorias escolhidas
        questions = list(Question.objects.filter(category__in=categories))
        random.shuffle(questions)
        selected = questions[:num_questions]

        for question in selected:
            ExamQuestion.objects.create(exam=exam, question=question)

        return HttpResponseRedirect(reverse('interviews:exam', args=[exam.id]))

    return render(request, 'interviews/new_exam.html', {
        'categories': Category.objects.all()
    })


@login_required
def exam(request, exam_id):
    exam = Exam.objects.get(id=exam_id)

    if exam.user != request.user:
        return HttpResponseRedirect(reverse('interviews:index'))

    if exam.completed:
        return HttpResponseRedirect(
            reverse('interviews:result', args=[exam_id])
        )

    exam_questions = exam.exam_questions.select_related(
        'question',
        'question__category'
    )

    for eq in exam_questions:
        eq.options = [
            ('a', eq.question.option_a),
            ('b', eq.question.option_b),
            ('c', eq.question.option_c),
            ('d', eq.question.option_d),
        ]

    return render(request, 'interviews/exam.html', {
        'exam': exam,
        'exam_questions': exam_questions,
        'total': exam_questions.count()
    })


@login_required
def submit_exam(request):
    """API endpoint — recebe respostas via fetch e calcula resultado."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    data = json.loads(request.body)
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})  # { "exam_question_id": "a", ... }
    duration = data.get('duration', 0)

    exam = Exam.objects.get(id=exam_id)

    if exam.user != request.user:
        return JsonResponse({'error': 'Unauthorized.'}, status=403)

    correct_count = 0
    total = 0

    for eq in exam.exam_questions.all():
        total += 1
        answer = answers.get(str(eq.id))
        eq.answer_given = answer
        if answer == eq.question.correct_option:
            eq.is_correct = True
            correct_count += 1
        else:
            eq.is_correct = False
        eq.save()

    percentage = round((correct_count / total) * 100, 1) if total > 0 else 0

    exam.completed = True
    exam.duration_seconds = duration
    exam.save()

    Result.objects.create(
        exam=exam,
        total_questions=total,
        correct_answers=correct_count,
        score_percentage=percentage
    )

    return JsonResponse({
        'success': True,
        'redirect': reverse('interviews:result', args=[exam_id])
    })


@login_required
def result(request, exam_id):
    """Página de resultados após completar o simulado."""
    exam = Exam.objects.get(id=exam_id)

    if exam.user != request.user:
        return HttpResponseRedirect(reverse('interviews:index'))

    result = exam.result
    exam_questions = exam.exam_questions.select_related('question').all()

    return render(request, 'interviews/result.html', {
        'exam': exam,
        'result': result,
        'exam_questions': exam_questions
    })


# ─── Histórico e Estatísticas ─────────────────────────────────────────────────

@login_required
def history(request):
    """Histórico de todos os simulados do utilizador."""
    exams = Exam.objects.filter(
        user=request.user,
        completed=True
    ).order_by('-created_at').select_related('result')

    return render(request, 'interviews/history.html', {
        'exams': exams
    })


@login_required
def stats(request):
    """Estatísticas por categoria/tecnologia."""
    categories = Category.objects.all()
    stats_data = []

    for category in categories:
        exam_questions = ExamQuestion.objects.filter(
            exam__user=request.user,
            exam__completed=True,
            question__category=category
        )
        total = exam_questions.count()
        correct = exam_questions.filter(is_correct=True).count()
        percentage = round((correct / total) * 100, 1) if total > 0 else 0

        stats_data.append({
            'category': category.name,
            'total': total,
            'correct': correct,
            'percentage': percentage
        })

    return render(request, 'interviews/stats.html', {
        'stats': stats_data
    })