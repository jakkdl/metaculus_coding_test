"""metaculus_probability_distribution URL Configuration

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
from django.urls import path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.IndexView.as_view(), name="index"),
    path("add_question/", views.add_question, name="add_question"),
    path("add_question_action/", views.add_question_action, name="add_question_action"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/predict", views.PredictView.as_view(), name="predict"),
    path(
        "<int:pk>/close", views.CloseQuestionView.as_view(), name="close_question_form"
    ),
    path(
        "<int:question_id>/add_prediction", views.add_prediction, name="add_prediction"
    ),
    path(
        "<int:question_id>/close_question", views.close_question, name="close_question"
    ),
    path(
        "prediction/<int:pk>/",
        views.PredictionDetailView.as_view(),
        name="prediction_detail",
    ),
]
