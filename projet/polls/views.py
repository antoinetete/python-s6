from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

import io
import base64

import pandas as pd
import plotly.offline as opy
import plotly.express as px
import geopandas as gpd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64
from django.db.models.functions import TruncDay
from matplotlib.ticker import LinearLocator

from .models import Question
from .models import Map


def index(request):
    df = pd.read_table('./here.csv', delimiter = ',')
    df = df[df['Valeur fonciere'] <= 5000000]
    df['Surface Carrez du 1er lot'] = df['Surface Carrez du 1er lot'].fillna(0)
    df['Surface Carrez du 1er lot'] = df['Surface Carrez du 1er lot'].apply(lambda x : str(x).replace(',','.')).astype(float)
    context = get_graph(1, 1, df)
    return render(request, 'polls/test.html', context)


    # latest_question_list = Question.objects²
    # map_list = Map.objects.order_by('id')
    # context = {'map_list': map_list, 'type': ['map']}
    # return render(request, 'polls/index.html', context)

def detail(request, map_id):
    map = get_object_or_404(Map, pk=map_id)
    context = get_map(request,map)
    return render(request, 'polls/detail.html', context)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def test(request):
    context = get_map()
    return render(request, 'polls/test.html', context)

def get_graph(x, y, df):
    df2 = df.groupby('Date mutation')['Valeur fonciere'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df2['Date mutation'], df2["Valeur fonciere"])
    ax.set_title="Valeur foncière en fonction du temps"
    flike = io.BytesIO()
    plt.savefig(flike)
    b641 = base64.b64encode(flike.getvalue()).decode()

    # df2 = df2.groupby('Code departement')['Valeur fonciere'].mean().reset_index().head(90)
    # fig2 = plt.bar(x=df2['Code departement'], height=df2["Valeur fonciere"])
    # fig2.set_title="Valeur foncière moyenne par département"
    # flike2 = io.BytesIO()
    # plt.savefig(flike2)
    # b642 = base64.b64encode(flike2.getvalue()).decode()

    df2 = df[df['Nature mutation'] == 'Vente']
    df2 = df2.groupby('Type local')['Nature mutation'].count().reset_index()
    fig3 = plt.bar(height=df2['Nature mutation'], x=df2["Type local"])
    fig3.set_title="Nombre de ventes par type de local"
    flike3 = io.BytesIO()
    plt.savefig(flike3)
    b643 = base64.b64encode(flike3.getvalue()).decode()

    df2 = df[df['Nature mutation'] == 'Expropriation']
    df2 = df2.groupby('Type local')['Nature mutation'].count().reset_index()
    fig4 = plt.bar(height=df2['Nature mutation'], x=df2["Type local"])
    fig4.set_title="Nombre d'expropriations par type de local"
    flike4 = io.BytesIO()
    plt.savefig(flike4)
    b644 = base64.b64encode(flike4.getvalue()).decode()

    df2 = df.groupby('Date mutation')['Valeur fonciere'].sum().reset_index()
    fig5 = plt.bar(x=df2['Date mutation'], height=df2["Valeur fonciere"])
    fig5.set_title="Valeur foncière en fonction du temps"
    flike5 = io.BytesIO()
    plt.savefig(flike5)
    b645 = base64.b64encode(flike5.getvalue()).decode()



    context = {'chart1' : b641, 'chart2' : b643, 'chart3' : b643, 'chart4' : b644, 'chart5' : b645}
    return context


def get_map(request, map):
    df = pd.read_table('./here.csv', delimiter = ',')
    df = df[df['Valeur fonciere'] <= 5000000]
    df['Surface Carrez du 1er lot'] = df['Surface Carrez du 1er lot'].fillna(0)
    df['Surface Carrez du 1er lot'] = df['Surface Carrez du 1er lot'].apply(lambda x : str(x).replace(',','.')).astype(float)
    df2 = df.groupby('Code departement', as_index = False)[f'{map.field_name}'].mean()
    df2["Code departement"] = df2["Code departement"].astype('str')
    df2.rename(columns = {f'{map.field_name}' : f'{map.field_rename}'}, inplace = True)

    for i in range(1, 10):
        df2["Code departement"].replace({str(i): "0" + str(i)}, inplace = True)
    df2["Code departement"] = df2["Code departement"].astype('str')

    sf = gpd.read_file('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson')

    jf = sf.merge(df2, left_on='code', right_on='Code departement', suffixes=('','_data'))

    fig = px.choropleth(jf,
                    geojson=sf,
                    locations=jf.code,
                    featureidkey="properties.code",
                    color=f'{map.field_rename}',
                    projection="mercator",
                    title=f'{map.map_name}')
    fig.update_geos(fitbounds="locations", visible=False)

    div = opy.plot(fig, auto_open=False, output_type='div')
    
    buffer = io.BytesIO()
    fig.write_html(buffer)
    html_bytes = buffer.getvalue().encode()
    encoded = base64.b64encode(html_bytes).decode()

    # flike = io.BytesIO()
    # fig.savefig(flike)
    # b64 = base64.b64encode(flike.getvalue()).decode()
    context = {'chart' : div, 'map_name' : map.map_name}
    return context