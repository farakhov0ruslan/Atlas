import json

from django.shortcuts import render
from django.http import JsonResponse


def survey_index(request):
    return render(request, 'survey/survey.html')


