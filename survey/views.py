from django.shortcuts import render


def survey_index(request):
    return render(request, 'survey/survey.html')
