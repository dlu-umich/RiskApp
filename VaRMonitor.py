# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 16:56:44 2018

@author: Di LU
"""

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas_datareader.data as web
from datetime import datetime
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt


##desired layout and functions
#1. Select stocks for portfolio construction
#2. portfolio VaR map
#3. realized p&L plot exceedence
#4. 

#Display: Correlation matrix for stocks

def calVaR(df,pValue):
    
    # sort dates from early to late
    df = df.sort_values(by = ['Date'], ascending = True)
    # calculate log return
    df['LogReturn'] = np.log(df['AdjClose']/df['AdjClose'].shift(1))
    df['VaR'] = np.nan
  
    # number of historical data
    numData = len(df)
    # lamda = 0.94, then 99.9% of the information is contained in the last 112 days
    numDays = 112
  
    # loop day0 start from 1, to numData - numDays
    for i in range(numData - numDays):
        day0 = i + 1 # not including the first NA logreturn
        day1 = day0 + numDays
        df1 = df[day0 : (day1+1)]
        sigma = df1['LogReturn'].std() # estimate drift nad volatility and calculate VaR
        VaR = - norm.ppf(pValue) * sigma
        df['VaR'].iloc[day1-1] = VaR
   
    return df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash("Hello World", external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='VaR Monitor'),

    html.Div(children='''
        A Risk Management Application with Python.
    '''),
          
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Google', 'value': 'GOOG'},
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Amazon', 'value': 'AMZN'}
        ],
        value='AAPL'
    ),
    
    dcc.Graph(id='my-graph'),
    
    dcc.Graph(id='my-var')
    
],style={'width': '800'})
    
@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):

    df = web.DataReader(
        selected_dropdown_value,
        'quandl',
        datetime(2017, 1, 1),
        datetime.now(),
        access_key='jou3Hy9N_sKPZxy9mgxt'
    )
    
    return {
        'data': [{
            'x': df.index,
            'y': df.Close
        }],
        'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
    }

@app.callback(Output('my-var', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):

    df = web.DataReader(
        selected_dropdown_value,
        'quandl',
        datetime(2017, 1, 1),
        datetime.now(),
        access_key='jou3Hy9N_sKPZxy9mgxt'
    )
    
    
    dfVaR = calVaR(df,0.05)[112:]
    
    return {
        'data': [{
            'x': dfVaR.index,
            'y': dfVaR.VaR
        },
            {
            'x': dfVaR.index,
            'y': dfVaR.LogReturn
        }],
                
        'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
    }
    
    

if __name__ == '__main__':
    app.run_server(debug=True)
