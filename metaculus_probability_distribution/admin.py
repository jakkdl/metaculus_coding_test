from django.contrib import admin

from .models import Prediction
from .models import PredictionPoint
from .models import Question

admin.site.register(Question)
admin.site.register(Prediction)
admin.site.register(PredictionPoint)
