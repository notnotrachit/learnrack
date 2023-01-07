"""learnrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from .views import dashboard
from courses.views import new_course_page, new_course, course_notes, notes_update

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('new_course/', new_course_page, name='new_course_page'),
    path('new_course_add/', new_course, name='new_course_add'),
    path('courses/<int:course_id>/notes', course_notes, name='course_notes'),
    path('courses/notes_update', notes_update, name='notes_update')
]
