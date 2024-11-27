from django.shortcuts import render


def survey_index(request):
    return render(request, 'survey/survey.html')

def survey_second(request):
    return render(request, 'survey/survey_second.html')
