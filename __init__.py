# -*- coding: utf-8 -*-
"""
MetOncoFit Interactive explorer

This application was built with a Flask framework using Dash and Plotly. The explorer shows three heatmaps that shows the top 10 features predicted by MetOncoFit on the y-axis, the genes corresponding to the feature predictions on the x-axis, and each cell is the corresponding gene-feature value.

@author: Scott Campit
"""
import pandas as pd
import numpy as np
import json

from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import flask

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'MetOncoFit'

df = pd.read_json('db.json')

up = df.loc[(df["Type"] == "UPREGULATED") | (df["Type"] == "GAIN")]
up = up.sort_values(by="Gini", ascending=False)
neut = df.loc[(df["Type"] == "NEUTRAL") | (df["Type"] == "NEUT")]
neut = neut.sort_values(by="Gini", ascending=False)
down = df.loc[(df["Type"] == "DOWNREGULATED") | (df["Type"] == "LOSS")]
down = down.sort_values(by="Gini", ascending=False)

# get values that will be used
num_uniq_genes = df["Gene"].nunique()
cancer_type = df["Cancer"].unique()
prediction_type = df["Target"].unique()

# Color scale:
colormap = [
    [0.0, 'rgb(165,0,38)'],
    [0.1111111111111111, 'rgb(215,48,39)'],
    [0.2222222222222222, 'rgb(244,109,67)'],
    [0.3333333333333333, 'rgb(253,174,97)'],
    [0.4444444444444444, 'rgb(254,224,144)'],
    [0.5555555555555556, 'rgb(224,243,248)'],
    [0.6666666666666666, 'rgb(171,217,233)'],
    [0.7777777777777778, 'rgb(116,173,209)'],
    [0.8888888888888888, 'rgb(69,117,180)'],
    [1.0, 'rgb(49,54,149)']
]

_body = dbc.Container(
    dbc.Row(
        [
            dbc.Col([
                html.Div([
                    html.H1("MetOncoFit")
                    ], style={'marginTop':30, 'marginBottom':30}),
                html.Div([
                    html.H4("A Machine Learning Algorithm to Identify Common Biochemical and Topological Attributes of Metabolic Genes Recurrently Dysregulated in Tumors"),
                    html.P(
                    """
                    MetOncoFit is a data-driven approach that uses biochemical and metabolic attributes to predict tumor differential expression, copy number variation, and patient survival.
                    """
                    )
                ], style={'marginTop':30, 'marginBottom':30}),
                html.Div([
                    html.H4("Installing MetOncoFit"),
                    html.P(
                    """
                    We recommend installing MetOncoFit inside a virtual environment.

                    To install the package, use PyPI:
                    """
                    )
                ], style={'marginTop':30, 'marginBottom':30}),
                html.Div([
                    html.P('''
                    > pip install metoncofit
                    ''')],
                    style={'marginTop':10, 'marginBottom':10, 'font-family':'courier', 'background-color':'#D3D3D3', 'color':'#111111', 'text-indent':'1em'}
                ),
                html.Div([
                    html.H4("Contributing to the MetOncoFit project"),
                    html.P(
                    """
                    Contributions are welcome! Please read the contributions guide to get started.
                    """),
                    html.P(
                    """
                    """
                    ),
                    html.P(
                    """
                    To support the MetOncoFit project, you can cite our publication:
                    """
                    ),
                    html.P(
                    """
                    """
                    ),
                    html.P(
                    """
                    Oruganty, K., Campit, S.E., Mamde, S., & Chandrasekaran, S. Common biochemical and topological attributes of metabolic genes recurrently dysregulated in tumors.
                    """
                    )
                ], style={'marginTop':30, 'marginBottom':30}),
                html.Div([
                    html.H4("MetOncoFit interactive explorer"),
                ])
            ])
        ]
    )
)

_widgets = dbc.Container(
    [
        # Text that updates with slider values
        dbc.Row(
            html.Div(id='updatemode-output-container',
            style={
                'margin-top':20,
                'padding':'0px 20px 20px 20px'
                }
            )
        ),

        # Slider
        dbc.Row(
            [
                html.Div(
                    dcc.Slider(
                        id='gene-slider',
                        min=1,
                        max=num_uniq_genes,
                        step=1,
                        value=25,
                        marks={
                            0: {'label':'0'},
                            100: {'label':'100'},
                            250: {'label':'250'},
                            500: {'label':'500'},
                            750: {'label':'750'},
                            num_uniq_genes: {'label':str(num_uniq_genes)}
                        },
                        updatemode='drag'
                    ),
                style={'width':'50%', 'padding':'0px 20px 20px 20px'},
                ),

                # Dropdown menus
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='cancer-type',
                            options=[{'label':i, 'value':i} for i in cancer_type],
                            value='Pan Cancer'
                        )
                    ),
                    width={"size":3.0},

                ),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='prediction-type',
                            options=[{'label':i,'value':i} for i in prediction_type],
                            value='Differential Expression'
                        )
                    ),
                    width={"size":3.0,
                        "offset":0.3}
                )
            ]
        )
    ]
)

app.layout = html.Div([_body, _widgets,
    html.Div(
        dcc.Graph(
            id='up-heatmap',
            figure={
                'data': [(
                    go.Heatmap(
                        x=up['Gene'],
                        y=up['Feature'],
                        z=up['Value'],
                        name='up',
                        colorscale=colormap)
                        )],
                'layout':go.Layout(
                    title=go.layout.Title(
                        text=('<b>Target label: '+up['Type'].iloc[0]+'</b>'),
                        xanchor='right',
                        yanchor='bottom',
                        x=0,
                        font=dict(
                            family='Arial',
                            size=16,
                            color='black'
                        )
                    ),
                    autosize=False,
                    #width=1000,
                    yaxis=dict(
                        automargin=True,
                        tickfont=dict(
                            family='Arial, sans-serif',
                            size=14,
                            color='black'
                        )
                    )
                )
            },
            config={
                'displayModeBar': False
            }
        )
    ),
    html.Div(
        dcc.Graph(
            id='neut-heatmap',
            figure={
                'data': [(
                    go.Heatmap(
                        x=neut['Gene'],
                        y=neut['Feature'],
                        z=neut['Value'],
                        name='neut',
                        colorscale=colormap)
                        )],
                'layout':go.Layout(
                    title=go.layout.Title(
                        text=('<b>Target label: '+neut['Type'].iloc[0]+'</b>'),
                        xanchor='right',
                        yanchor='bottom',
                        x=0,
                        font=dict(
                            family='Arial',
                            size=16,
                            color='black'
                        )
                    ),
                    autosize=False,
                    #width=1000,
                    yaxis=dict(
                        automargin=True,
                        tickfont=dict(
                            family='Arial, sans-serif',
                            size=14,
                            color='black'
                        )
                    )
                )
            },
            config={
                'displayModeBar': False
            }
        )
    ),
    html.Div(
        dcc.Graph(
            id='down-heatmap',
            figure={
                'data': [(
                    go.Heatmap(
                        x=down['Gene'],
                        y=down['Feature'],
                        z=down['Value'],
                        name='down',
                        colorscale=colormap)
                        )],
                'layout':go.Layout(
                    title=go.layout.Title(
                        text=('<b>Target label: '+down['Type'].iloc[0]+'</b>'),
                        xanchor='right',
                        yanchor='bottom',
                        x=0,
                        font=dict(
                            family='Arial',
                            size=16,
                            color='black'
                        )
                    ),
                    autosize=False,
                    #width=1000,
                    yaxis=dict(
                        automargin=True,
                        tickfont=dict(
                            family='Arial, sans-serif',
                            size=14,
                            color='black'
                        )
                    )
                )
            },
            config={
                'displayModeBar': False
            }
        )
    )
])

# Create callbacks - unfortunately Dash only supports one output per callback...
@app.callback(
    dash.dependencies.Output('up-heatmap', 'figure'),
    [dash.dependencies.Input('cancer-type', 'value'),
    dash.dependencies.Input('prediction-type', 'value'),
    dash.dependencies.Input('gene-slider', 'value')])
def update_up(cancer_choice, prediction_choice, slider_choice):
    up_df = up[up['Target'] == prediction_choice]
    up_df = up_df[up_df['Cancer'] == cancer_choice]
    up_tmp = up_df['Gene'].unique().tolist()
    up_tmp = up_tmp[0:slider_choice]
    up_df = up_df.loc[up_df['Gene'].isin(up_tmp)]

    custom_hover = []
    for _, i in up_df.iterrows():
        dat = 'Gene: '+'{}'.format(i['Gene'])+'<br>'+'Feature: '+'{}'.format(i['Feature'])+'<br>'+'Value: '+'{0:.2f}'.format(i['Value'])+'<br>'+'R: '+'{0:.2f}'.format(i['R'])
        custom_hover.append(dat)

    return {
        'data': [(
            go.Heatmap(
                x=up_df['Gene'],
                y=up_df['Feature'],
                z=up_df['Value'],
                name='up-heatmap',
                colorscale=colormap,
                text=custom_hover,
                hoverinfo='text')
                )],
        'layout':go.Layout(
            title=go.layout.Title(
                text=('<b>Target label: '+up_df['Type'].iloc[0]+'</b>'),
                xanchor='left',
                yanchor='bottom',
                x=0.47,
                font=dict(
                    family='Arial',
                    size=16,
                    color='black'
                )
            ),
            autosize=False,
            #width=1000,
            yaxis=dict(
                automargin=True,
                autorange='reversed',
                tickfont=dict(
                    family='Arial, sans-serif',
                    size=14,
                    color='black',
                )
            )
        )
    }

@app.callback(
    dash.dependencies.Output('neut-heatmap', 'figure'),
    [dash.dependencies.Input('cancer-type', 'value'),
    dash.dependencies.Input('prediction-type', 'value'),
    dash.dependencies.Input('gene-slider', 'value')])
def update_neut(cancer_choice, prediction_choice, slider_choice):
    neut_df = neut[neut['Target'] == prediction_choice]
    neut_df = neut_df[neut_df['Cancer'] == cancer_choice]
    neut_tmp = neut_df['Gene'].unique().tolist()
    neut_tmp = neut_tmp[0:slider_choice]
    neut_df = neut_df.loc[neut_df['Gene'].isin(neut_tmp)]

    custom_hover = []
    for _, i in neut_df.iterrows():
        dat = 'Gene: '+'{}'.format(i['Gene'])+'<br>'+'Feature: '+'{}'.format(i['Feature'])+'<br>'+'Value: '+'{0:.2f}'.format(i['Value'])+'<br>'+'R: '+'{0:.2f}'.format(i['R'])
        custom_hover.append(dat)

    return {
        'data': [(
            go.Heatmap(
                x=neut_df['Gene'],
                y=neut_df['Feature'],
                z=neut_df['Value'],
                name='neut-heatmap',
                colorscale=colormap,
                text=custom_hover,
                hoverinfo='text')
                )],
        'layout':go.Layout(
            title=go.layout.Title(
                text=('<b>Target label: '+neut_df['Type'].iloc[0]+'</b>'),
                xanchor='left',
                yanchor='bottom',
                x=0.47,
                font=dict(
                    family='Arial',
                    size=16,
                    color='black'
                )
            ),
            autosize=False,
            #width=1000,
            yaxis=dict(
                automargin=True,
                autorange='reversed',
                tickfont=dict(
                    family='Arial, sans-serif',
                    size=14,
                    color='black'
                )
            )
        )
    }

@app.callback(
    dash.dependencies.Output('down-heatmap', 'figure'),
    [dash.dependencies.Input('cancer-type', 'value'),
    dash.dependencies.Input('prediction-type', 'value'),
    dash.dependencies.Input('gene-slider', 'value')])
def update_down(cancer_choice, prediction_choice, slider_choice):
    down_df = down[down['Target'] == prediction_choice]
    down_df = down_df[down_df['Cancer'] == cancer_choice]
    down_tmp = down_df['Gene'].unique().tolist()
    down_tmp = down_tmp[0:slider_choice]
    down_df = down_df.loc[down_df['Gene'].isin(down_tmp)]

    custom_hover = []
    for _, i in down_df.iterrows():
        dat = 'Gene: '+'{}'.format(i['Gene'])+'<br>'+'Feature: '+'{}'.format(i['Feature'])+'<br>'+'Value: '+'{0:.2f}'.format(i['Value'])+'<br>'+'R: '+'{0:.2f}'.format(i['R'])
        custom_hover.append(dat)

    return {
        'data': [(
            go.Heatmap(
                x=down_df['Gene'],
                y=down_df['Feature'],
                z=down_df['Value'],
                name='down-heatmap',
                colorscale=colormap,
                text=custom_hover,
                hoverinfo='text')
                )],
        'layout':go.Layout(
            title=go.layout.Title(
                text=('<b>Target label: '+down_df['Type'].iloc[0]+'</b>'),
                xanchor='left',
                yanchor='bottom',
                x=0.47,
                font=dict(
                    family='Arial',
                    size=16,
                    color='black'
                )
            ),
            autosize=False,
            #width=1000,
            yaxis=dict(
                automargin=True,
                autorange='reversed',
                tickfont=dict(
                    family='Arial, sans-serif',
                    size=14,
                    color='black'
                )
            )
        )
    }

# Callback for the slider
@app.callback(Output('updatemode-output-container', 'children'),
    [dash.dependencies.Input('gene-slider', 'value')])
def display_value(value):
    return 'Number of genes displayed: {}'.format(value, value)

# For server
#server = app.server

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
