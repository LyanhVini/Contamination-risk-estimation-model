#Imports do projeto
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, Response
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Output, Input
from detection import VideoCamera, gen, df, risk, labels


#URL do vídeo de stream
url = "https://youtu.be/IVLD-t_vzeM"

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

@server.route('/video_feed')

def video_feed():
    return Response(gen(VideoCamera(url)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.callback(
            Output('live-update-graph', 'figure'),
            [Input('interval-component', "n_intervals")]
            )

def update_graph(n_intervals):
    fig = go.Figure(layout={"template":"plotly_dark"})
    fig.add_trace(go.Bar(x=df["timer"], y=df["count"]))
    fig.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, b=30, t=10),
        )
    return fig

@app.callback(
            Output('live-update-3d', 'figure'),
            [Input('interval-component', "n_intervals")]
            )

def update_3d(n_intervals):
    fig = go.Figure(go.Histogram2d(
                    x=(df["bboxes"][0]),
                    y=(list(map(lambda x: -x, df["bboxes"][1]))),
                    z=(df["count"])
    ))
    return fig

@app.callback(
            Output('live-velocimeter', 'figure'),
            [Input('interval-component', "n_intervals")]
            )
def velocimeter(n_intervals):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
    value = risk[-1],
    delta = {'reference': risk[-2]},
    gauge = {
        'axis': {'visible': False}},
    domain = {'row': 0, 'column': 0}))
    fig.update_layout(
    grid = {'rows': 1, 'columns': 1, 'pattern': "independent"},
    template = {'data' : {'indicator': [{
        'number':{'font_color':"white", 'suffix': "%"},
        'gauge':{'axis_range': (0,100)},
        'title': {'text': "Risco de contaminação", 'font_color':"white", 'font_size': 48},
        'mode' : "number+delta+gauge",
        'delta' : {'reference': risk[-2]}}]
                         }})
    fig.update_layout(paper_bgcolor = "rgb(3, 7, 15)")
    return fig

@app.callback(
            Output('live-pie', 'figure'),
            [Input('interval-component', "n_intervals")]
            )

def pie(n_intervals):
    fig = px.pie(values = labels.values(), names = labels.keys())
    fig.update_layout(legend_font_size = 32,paper_bgcolor = "rgb(3, 7, 15)")
    
    return fig

app.layout = html.Div(
    className= "layout",
    children=[
        html.Div(className="head",
        children=[
            html.H5("MONITORAMENTO DE LOCAL", className="anim-typewriter"),
            html.Img(className="button",src="assets/Group 3.png"),
            html.H4("AMBIENTE"),
            html.Img(className= "video",src="/video_feed"),
        ]),
        html.Div("CLASSES", className="classes"),
        html.H3("PESSOAS AO LONGO DO DIA", className="contPess"),
        dcc.Graph(id='live-update-graph', className='contagem'),
        html.H3("MAPA DE OCUPAÇÃO", className="contPess2d"),
        dcc.Graph(id='live-update-3d', className='contagem3d'),
        dcc.Graph(id='live-velocimeter', className='velocimeter'),
        dcc.Graph(id='live-pie', className='pie'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,
            n_intervals=0
            )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)