import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go

def GetDiv():
    data = [go.Bar(
                x=['giraffes', 'orangutans', 'monkeys'],
                y=[20, 14, 23]
        )]

    fig = go.Figure(data=data)

    return offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)
