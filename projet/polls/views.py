from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64
from django.db.models.functions import TruncDay
from matplotlib.ticker import LinearLocator


import pandas as pd

import numpy as np

from .models import Question


def index(request):

    df = pd.read_table('https://www.data.gouv.fr/fr/datasets/r/817204ac-2202-4b4a-98e7-4184d154d98c', delimiter = '|')
    df = df.dropna(axis = 1, how = "all")
    df["Valeur fonciere"] = df["Valeur fonciere"].str.replace(',', '.').astype('float')
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def test(request):
    context = get_context_data()
    return render(request, 'polls/test.html', context)

def get_context_data(**kwargs):

    days = np.array([x for x in range(1, 16)])
    counts = np.array([5,15,12,31,28,19,8,13,20,16,19,27,14,10,7])

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(days, counts, '--bo')

    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_title('By date')
    ax.set_ylabel("Count")
    ax.set_xlabel("Date")
    ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
    ax.yaxis.set_minor_locator(LinearLocator(25))

    flike = io.BytesIO()
    fig.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    context = {'chart' : b64}
    return context