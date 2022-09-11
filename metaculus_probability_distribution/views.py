import re
from datetime import date
from typing import Any
from typing import TYPE_CHECKING

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Prediction
from .models import PredictionPoint
from .models import Question

if TYPE_CHECKING:
    GenericListViewQuestion = generic.ListView[Question]
    GenericDetailViewQuestion = generic.DetailView[Question]
    GenericDetailViewPrediction = generic.DetailView[Prediction]
else:
    GenericListViewQuestion = generic.ListView
    GenericDetailViewQuestion = generic.DetailView
    GenericDetailViewPrediction = generic.DetailView


class IndexView(GenericListViewQuestion):
    template_name = "metaculus_probability_distribution/index.html"
    model = Question
    context_object_name = "questions"


class DetailView(GenericDetailViewQuestion):
    model = Question
    template_name = "metaculus_probability_distribution/detail.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        context["predictions"] = Prediction.objects.filter(question=context["question"])
        return context


class CloseQuestionView(GenericDetailViewQuestion):
    model = Question
    template_name = "metaculus_probability_distribution/close_question.html"


class PredictionDetailView(GenericDetailViewPrediction):
    model = Prediction
    template_name = "metaculus_probability_distribution/prediction.html"

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        context["prediction_points"] = PredictionPoint.objects.filter(
            prediction=context["prediction"]
        )
        return context


class PredictView(GenericDetailViewQuestion):
    model = Question
    template_name = "metaculus_probability_distribution/predict.html"


def add_question(request: HttpRequest) -> HttpResponse:
    return render(request, "metaculus_probability_distribution/add_question.html")


def close_question(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    # score question
    return HttpResponseRedirect(reverse("detail", args=(question.id,)))


def add_question_action(request: HttpRequest) -> HttpResponse:
    # TODO: check if timezones are handled correctly
    # TODO: allow entering time?
    # TODO: check that question is open
    errors = []
    question_title = request.POST["title"]
    question_description = request.POST["description"]
    timezone.now()

    # TODO: repopulate the form with previously entered values
    if not question_title:
        errors.append("invalid title")
    if not question_description:
        errors.append("invalid description")

    try:
        start_date = date.fromisoformat(request.POST["start_date"])
        if start_date < date.today():
            errors.append("start date must not be in the past")
    except ValueError:
        errors.append("invalid start date")

    try:
        end_date = date.fromisoformat(request.POST["end_date"])
        if start_date and end_date <= start_date:
            errors.append("end date must be after start date")
    except ValueError:
        errors.append("invalid end date")

    if errors:
        return render(
            request,
            "metaculus_probability_distribution/add_question.html",
            {"errors": errors},
        )

    Question.objects.create(
        question_title=question_title,
        question_description=question_description,
        start_date=start_date,
        end_date=end_date,
        pub_date=timezone.now(),
    )

    return HttpResponseRedirect(reverse("index"))


def add_prediction(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    # TODO: check that question is open
    error_keys = []
    predictions = {}
    error_msg = ""
    for key, value in request.POST.items():
        if not re.fullmatch(r"\d\d\d\d-\d\d-\d\d", key):
            continue
        if not isinstance(value, str):
            error_keys.append(key)
            continue
        if value == "":
            continue
        value = value.strip("%")
        if not re.fullmatch(r"\d+(.\d+)?", value):
            error_keys.append(key)
            continue
        floatvalue = float(value)
        if not 0 < floatvalue < 100:
            error_keys.append(key)
            continue

        predictions[key] = floatvalue / 100

    if not predictions:
        error_msg = "No valid predictions"

    if error_keys or error_msg:
        return render(
            request,
            "metaculus_probability_distribution/predict.html",
            {
                "question": question,
                "error_keys": error_keys,
                "error_msg": error_msg,
                "prev_values": request.POST.items(),
            },
        )

    prediction = Prediction.objects.create(
        question=question, prediction_time=timezone.now()
    )
    # TODO fill out missing values, either here or in evaluation
    for prediction_date, probability in predictions.items():
        PredictionPoint.objects.create(
            prediction=prediction, date=prediction_date, probability=probability
        )

    return HttpResponseRedirect(reverse("detail", args=(question.id,)))
