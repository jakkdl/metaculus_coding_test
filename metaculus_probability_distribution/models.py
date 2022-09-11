from datetime import date
from datetime import timedelta
from typing import Iterator

from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint
from django.db.models import Q


class Question(models.Model):
    question_title = models.CharField(max_length=200)
    question_description = models.CharField(max_length=2000)
    pub_date = models.DateTimeField("date published")
    start_date = models.DateTimeField("start date")
    end_date = models.DateTimeField("end date")
    question_open = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.question_title}"

    def remaining_days(self) -> Iterator[str]:
        current = date.today()
        while current <= self.end_date.date():
            yield str(current)
            current += timedelta(days=1)


class Prediction(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    prediction_time = models.DateTimeField("datetime predicted")
    brier_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    def __str__(self) -> str:
        return str(self.prediction_time)

    class Meta:
        constraints = (
            # for checking in the DB
            CheckConstraint(
                check=Q(brier_score__gte=0.0) & Q(brier_score__lte=1.0),
                name="brier_score_range_constraint",
            ),
        )


class PredictionPoint(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    date = models.DateField("prediction date point")
    probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    def __str__(self) -> str:
        return f"{self.date}: {self.probability*100}%"

    class Meta:
        constraints = (
            # for checking in the DB
            CheckConstraint(
                check=Q(probability__gte=0.0) & Q(probability__lte=1.0),
                name="probability_range_constraint",
            ),
        )
