import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
from query_builder import selectQueryBuilder

def GetDiv():
    trace1 = go.Bar(
        x=['giraffes', 'orangutans', 'monkeys'],
        y=[20, 14, 23],
        name='SF Zoo'
    )
    trace2 = go.Bar(
        x=['giraffes', 'orangutans', 'monkeys'],
        y=[12, 18, 29],
        name='LA Zoo'
    )

    data = [trace1, trace2]
    layout = go.Layout(
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)

    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)

def Graph_AAWinners(count=10, show_nominations=True):
    pass

def MakeBarTrace():
    pass

print(selectQueryBuilder(
    columns = ['Title','Release','AA_Wins'],
    table = 'Film',
    order_by ='AA_Wins',
    limit=['top',10]
))
