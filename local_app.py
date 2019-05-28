# simple go graph with nest data embeddings
# demo

import os
import numpy as np
import time
import base64
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import flask


app = dash.Dash('nest-data')
server = app.server

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

# Generate default scatter plot
datasets=pd.read_csv("../data/nest_vizdf.csv", sep='\t')
data = []

# get unique celltypes category
celltypes = datasets['celltypes'].drop_duplicates()
unique_celltypes = list(celltypes)

# Grouping tsne scatter plots by celltypes
for i in unique_celltypes:
    datasets_celltype = datasets.loc[(datasets['celltypes']==i)]
    scatter = go.Scatter(
            name=i,
            x=datasets_celltype['tSNE_x'],
            y=datasets_celltype['tSNE_y'],
            textposition='top left',
            # does text actually do what you want?
            text=[i for _ in range(datasets_celltype['tSNE_x'].shape[0])],
            mode='markers',
            marker=dict(
                size=2.5,
                symbol='circle'
            )
    )
    data.append(scatter)

#fig = dict(data=data, layout=tsne_layout)
#py.iplot(fig, filename="nest data demo")
def omit(omitted_keys, d):
    return {k: v for k, v in d.items() if k not in omitted_keys}


def Card(children, **kwargs):
    return html.Section(
        children,
        style=merge({
            'padding': 20,
            'margin': 5,
            'borderRadius': 5,
            'border': 'thin lightgrey solid',

            # Remove possibility to select the text for better UX
            'user-select': 'none',
            '-moz-user-select': 'none',
            '-webkit-user-select': 'none',
            '-ms-user-select': 'none'
        }, kwargs.get('style', {})),
        **omit(['style'], kwargs)
    )

def merge(a, b):
    return dict(a, **b)

# local_layout display
local_layout = html.Div(
    className="container",
    style={
        'width': '90%',
        'max-width': 'none',
        'font-size': '1.5rem',
        'padding': '10px 30px'
        },
    children=[
        # Main heading and title
        html.Div(className="row", children=[
            html.H1(
                children='Nest t-SNE data explorer',
                id="title",
                style={
                    'float':'left',
                    'margin-top':'20px',
                    'margin-bottom':'0',
                    'margin-left':'7px'
                }
            ),
        ]),

        # Information about loaded data
        # why do you have three div sections

        html.Div(className="five columns", children=[
            html.Div(className="row", children=[
                html.Div(className="five columns", children=[
                    dcc.Dropdown(
                        id='categories',
                        options=[{'label':i, 'value':i} for i in datasets['celltypes'].unique()],
                        multi=True
                 )],
                html.Div(className='three columns', children=[
                    # RadioItems to determine which axis to look at
                    dcc.RadioItems(
                        id='direction',
                        options=[
                            {'label':'X', 'value': 'X'},
                            {'label':'Y', 'value': 'Y'},
                            {'label':'Z', 'value':'Z'}
                            ],
                        labelStyle={'display':'inline-block'},
                        value='X')
                    ], style={'color': colors['text'], 'padding-top':'5px'}),
                html.Div(className='four columns', children=[
                    dcc.Slider(
                        min=0,
                        step=50,
                        value=5000,# find n_counts max value ,
                        id='n_counts'),
                    ], style={'padding-top': '5px'}),
                ], style={'padding-bottom': '20px'}),

            html.Div(className="row", children=[
                dcc.Graph(
                    id='tsne-plot',
                    style={'height':'98vh'}
                )

            ]),

            html.Div(className='row', children=[
                html.Div(className="two columns", children=[
                    html.Pre(id='hover-data', style=styles['pre'])
                ]),
                html.Div(className='two columns', children=[
                    html.P("Threshold:")
                    ], style={'textAlign': 'center', 'color': colors['text']}),
                html.Div(className='eight columns', children=[
                    dcc.Slider(id='threshold',
                        min=0,
                        max=5000,
                        step=1000,
                        value=1000
                        marks={i: i for i in np.arange(0,5000,1000)})
                    ], style={'padding-top':'5px'})
            ]),
        ]),
    ]
)


#def local_callbacks(app):
def generate_figure_image(data, layout):
    figure = go.Figure(
            data=data,
            layout=layout
            )

    return figure
#    def fill_dropdown_word_selection_options(dataset):
#        if dataset in DATASETS:
#            return [{'label': i, 'value': i} for i in data_dict[dataset].iloc[:,0].tolist()]

def display_scatter_plot(data, layout):
         # Layout for tsne grap
    axes=dict(
        title='',
        showgrid=True,
        zeroline=False,
        showticklabels=False
    )

    tsne_layout = go.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        scene=dict(xaxis=axes, yaxis=axes)
    )
    figure = generate_figure_image(data, layout)
    return figure
@app.callback(Output('tsne-plot', 'children'),
        [Input('data', 'children')])
@app.callback(Output('hover-data', 'children'),
              [Input('tsne-plot', 'data')])

@app.callback(Output('tsne-plot', 'children'),
        [Input('threshold', 'value')])
def update_plot(threshold, datasets, local_layout):
    tmp = datasets.loc[(datasets['n_counts']>threshold)]
    x_val = tmp['tSNE_x']
    y_val = tmp['tSNE_y']
    return display_scatter_plot(data={'x':x_val, 'y':y_val}, local_layout})


