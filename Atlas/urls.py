"""
URL configuration for Atlas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from Atlas import settings
from django.urls import path
from survey.views import survey_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace="main")),
    path('survey/', survey_view, name='survey_combined'),
    path('survey/', include('survey.urls', namespace='survey')),
    path('routes/', include('routes.urls', namespace='routes')),
]

if settings.DEBUG:
    # urlpatterns += [
    #     path('__debug__/', include("debug_toolbar.urls"))
    # ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
