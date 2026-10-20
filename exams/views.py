from django.shortcuts import render

def welcome(request):
    return render(request, 'exams/welcome.html', {'portal_name': 'Apex Exam Portal'})