# Importações necessárias
import base64
import io
import time
from io import BytesIO
import os

import dash
from dash.dependencies import Input, Output, State
import utils.dash_reusable_components as drc
import dash_bootstrap_components as dbc
from dash import dcc, html, ctx

from app.DTR import *

Input_Columns = None
Output_Columns = None
Dataset = None

# Inicializa o app Dash
app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],)

app.title = "DTR"
server = app.server

app.layout = html.Div([
    html.Br(),
    html.Div([
        html.Img(src='assets/logo.png', style={'height': '100px', 'margin-left': 'auto', 'margin-right': 'auto'}),
    ], style={'text-align': 'center', 'margin-bottom': '10px'}),

    html.Br(),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select an Excel or CSV File (Your Dataset)')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
        },
        multiple=False
    ),

    html.Br(),

    html.Div([
        html.Div([
            dcc.Textarea(
                id='textarea',
                style={
                    'width': '80%',
                    'height': '300px',
                    'resize': 'none',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'fontSize': '18px',
                },
                readOnly=True
            ),
        ], style={'display': 'none'}, id='unique-div-id'),

        dcc.Graph(id='graph-output', style={'display': 'none'}),

    ], style={'display': 'flex', 'width': '100%', 'justifyContent': 'center', 'alignItems': 'stretch'}),


], style={'width': '80%', 'justifyContent': 'center', 'margin-left': 'auto', 'margin-right': 'auto'})



def parse_contents(contents, filename):
    global Dataset
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'xlsx' in filename:
            # Assume que é um arquivo Excel
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'csv' in filename:
            # Assume que é um arquivo CSV
            df = pd.read_csv(io.BytesIO(decoded))
        else:
            return html.Div([
                'Unsupported file type.'
            ])
    except Exception as e:
        return html.Div([
            'There was an error processing the file.'
        ])

    Dataset = df
    return df

@app.callback(Output('textarea', 'value'),
              Output('graph-output', 'figure'),
              Output('graph-output', 'style'),
              Output('unique-div-id', 'style'),
              Input("upload-data", "contents"),
              State('upload-data', 'filename'),
prevent_initial_call=True)


def RunDTR(list_of_contents, list_of_names):
    global Dataset
    if list_of_contents is not None:
        Dataset = parse_contents(list_of_contents, list_of_names)

    texto_informacoes, texto_informacoes2, fig = GeraGrafico(Dataset)

    style = {'width': '100%', 'justifyContent': 'center', 'margin-right': '20px', 'margin-left': '20px'}
    style2 = {'width': '100%', 'justifyContent': 'center', 'margin-right': '20px', 'margin-left': '20px'}

    texto_informacoes = texto_informacoes + texto_informacoes2

    return texto_informacoes, fig, style, style2

# Roda o app
if __name__ == '__main__':
    app.run_server(debug=False)
