import pandas as pd
import glob
import os
from datetime import timedelta
import sort_dataframeby_monthorweek

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import dash_auth


##################################################### DATA prep ######################################################
#opening and reading the csv files contained in app data

path = "data"
backlog_files = glob.glob(os.path.join(path, "backlog-*.csv"))
raised_files = glob.glob(os.path.join(path, "raised-*.csv"))
closed_files = glob.glob(os.path.join(path, "closed-*.csv"))

df_raised = pd.concat(map(pd.read_csv, raised_files), ignore_index=True)
df_backlog = pd.concat(map(pd.read_csv, backlog_files), ignore_index=True)
df_closed = pd.concat(map(pd.read_csv, closed_files), ignore_index=True)

#filtering for IBERIA incidencts

df_raised = df_raised[df_raised['Customer Company Group']== 'IBERIA']
df_backlog = df_backlog[df_backlog['Customer Company Group']== 'IBERIA']
df_closed = df_closed[df_closed['Customer Company Group']== 'IBERIA']

#Drop all columns not relevant to kpi's

df_raised.drop(df_raised.columns.difference(['Priority', 'Inc. Type', 'Create Date-Time', 'Resolution Date-Time', 'Incidenct Code']), 1, inplace=True)
df_backlog.drop(df_backlog.columns.difference(['Priority', 'Incidenct Code']), 1, inplace=True)

#change dates to dateframes and create month column

df_raised['Create Date-Time'] = pd.to_datetime(df_raised['Create Date-Time'], format = "%d/%m/%Y %H:%M")
df_raised['Resolution Date-Time'] = pd.to_datetime(df_raised['Resolution Date-Time'], format = "%d/%m/%Y %H:%M")                                               

def months(df_raised):
    
    return int(df_raised["Create Date-Time"].month)

df_raised['month_num'] = df_raised.apply(months, axis=1)

df_raised['month'] = pd.to_datetime(df_raised['month_num'], format = '%m')
df_raised['month'] = df_raised['month'].dt.strftime('%b')



def year(df_raised):
    
    return df_raised["Create Date-Time"].year

df_raised['year'] = df_raised.apply(year, axis=1)


#create time taken to resolve incidenct column

df_raised['time taken'] = df_raised['Resolution Date-Time'] - df_raised['Create Date-Time']

#Create Sla met column for top priority

def SLA_met(df_raised):
    if df_raised['Priority'] == 'Crítica':
        if df_raised['time taken'] > timedelta(hours=4):
            return 'NO'
        else:
            return 'YES'

df_raised['SLA met'] = df_raised.apply(SLA_met, axis=1)


##################################################### DASH APP ######################################################

# Create username and password protection for th dashboard

app = dash.Dash(__name__, prevent_initial_callbacks=True)
application = app.server

VALID_USERNAME_PASSWORD_PAIRS = {
    'hellou': 'world'
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


# Create the dash layout
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                className="three columns div-user-controls",
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Img(
                            className="logo", src=app.get_asset_url('Iberia_air_logo.png')
                        ),

                        html.Div(
                            children=[
                                html.H2("IBERIA Dashboard"),
                        html.P(
                            """Select a range of months and KPI's to compare"""
                        ),                    
                            ]
                        ),
                        html.Hr(),
                        html.H6('Select year'),
                            
                    html.Div(
                        className='div-for-dropdown',
                        children=[
                            dcc.Dropdown(id='dropdowny', options=[
        {'label': i, 'value': i} for i in df_raised.year.unique()]),

                        ]
                    ),
                    html.Hr(),
                        html.H6('Select month range'),
                
                    html.Div(
                        className='div-for-dropdown',
                        children=[
                            dcc.RangeSlider(1, 12, 1,
                                id='date_slider',
                                value=[1, 5],
                                allowCross=False
                            
                                
                    )

                        ]
                    ),  
                        
                      html.Div(
                        className='div-for-dropdown',
                        children=[
                            dcc.RadioItems(
                                id="KPI_dropdown",
                                options=[{'label': 'Show ALL KPIs', 'value': 1},
                                  {'label': 'Number of critical incidencts in the month', 'value': 2},
                                  {'label': 'total number of incidences in the month', 'value': 3},      
                                  {'label': 'Number of incidences raised per priority in the month', 'value': 4},
                                  {'label': 'Number of incidences in the backlog per priority in the month', 'value': 5},
                                  {'label': 'Number of incidences per cause', 'value': 6},
                                  {'label': 'Number of incidences P1 in the month meeting SLA resolution time', 'value': 7},
                                  {'label': '% of incidences P1 meeting SLA', 'value': 8},
                                  {'label': 'Number of incidences P1 in the month not meeting SLA resolution time', 'value': 9},
                                  {'label': '% of incidences P1 not meeting SLA', 'value': 10} ,
                                  {'label': 'Average resolution time for incidences P1 meeting SLA', 'value': 11} ,
                                  {'label': 'Average resolution time for incidences P1 not meeting SLA', 'value': 12} ,
                                  {'label': 'Average resolution time per cause', 'value': 13} ,
                                  ],
                                value=1,
                                style = {'margin-top': '40px'},
                            )                             
                        ]
                    ),

                
                        ],
                    )                  
            ]
        ),

        # Plots
        html.Div(   
            className="nine columns div-for-charts bg-dark",             
                children=[html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className='six columns',
                            children=[dcc.Graph(
                                id='KPI1',
                                )]
                        ),
                        
                        html.Div(
                            className='six columns',
                            children=[dcc.Graph(
                                id='KPI2', 
                                )]
                        ),
                    ]                    
                ),
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI3', 
                                )]
                        ),
                          
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI4', 
                                )]
                        ),
                          
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI5', 
                                )]
                        ),
                          
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI6', 
                                )]
                        ),
                          
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI7', 
                                )]
                        ),
                    
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI8',
                                )]
                        ),  
                          
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI9',
                                )]
                        ),
                    
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI10', 
                                )]
                        ),
                    
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI11', 
                                )]
                        ),
                        
                    html.Div(
                        className='div-for-charts2',
                            children=[dcc.Graph(
                                id='KPI12', 
                                )]
                        ),
                    
            ]
        ),
            ],
        ),

    ]
)

@app.callback(
    [Output('KPI1', 'figure'),
    Output('KPI2', 'figure'),
    Output('KPI3', 'figure'),
    Output('KPI4', 'figure'),
    Output('KPI5', 'figure'),
    Output('KPI6', 'figure'),
    Output('KPI7', 'figure'),
    Output('KPI8', 'figure'),
    Output('KPI9', 'figure'),
    Output('KPI10', 'figure'),
    Output('KPI11', 'figure'),
    Output('KPI12', 'figure'),
    ],
    [Input('dropdowny', 'value'),
     Input('date_slider', 'value'),
     Input('KPI_dropdown', 'value'),
    ]
)

def upadte_figure(year_selected, date_slider, KPI):
    
##################################################### KPI calculations ######################################################
    
    start = date_slider[0]
    end = date_slider[1]
    df_raised2 = df_raised.query("month_num >= @start and month_num <= @end and year == @year_selected")
    
    KPI1 = df_raised2[df_raised2['Priority'] == 'Crítica'].groupby('month').size()
    KPI1 = KPI1.rename('size').reset_index()

    KPI1 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI1,monthcolumnname='month')

    fig1 = px.bar(KPI1, x= 'month', y=KPI1['size'], color='size', color_continuous_scale='reds')

    fig1.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Number of critical incidencts in the month',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})




    #Total number of incidences raised in the month

    KPI2 = df_raised2.groupby(['month']).size()
    KPI2 = KPI2.rename('size').reset_index()
    KPI2 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI2,monthcolumnname='month')

    fig2 = px.line(KPI2, x='month', y=KPI2['size'])

    fig2.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Total number of incidences raised in the month',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})


    #Number of incidences raised per priority in the month

    KPI3 = df_raised2.groupby(['month', 'Priority']).size()
    KPI3 = KPI3.rename('size').reset_index()
    KPI3 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI3,monthcolumnname='month')


    fig3 = px.bar(KPI3, x='month', y='size', color='Priority', barmode = 'stack')

    fig3.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Number of incidences raised per priority in the month',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})


    #Number of incidences in the backlog per priority in the month

    #Number of incidences per cause

    KPI5 = df_raised2.groupby(['month', 'Inc. Type', ]).size()
    KPI5 = KPI5.rename('size').reset_index()
    KPI5 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI5,monthcolumnname='month')

    fig5 = px.bar(KPI5, x='month', y='size', color='Inc. Type', barmode = 'stack')

    fig5.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Number of incidences per cause',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})

    #Number of incidences P1 in the month meeting SLA resolution time


    KPI6 = df_raised2[df_raised2['SLA met']=='YES'].groupby('month').size()
    KPI6 = KPI6.rename('size').reset_index()
    KPI6 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI6,monthcolumnname='month')

    fig6 = px.bar(KPI6, x= 'month', y='size', color='size', color_continuous_scale='reds')

    fig6.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Number of incidences P1 in the month meeting SLA resolution time',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})


    #% of incidences P1 meeting SLA

    KPI7 = pd.DataFrame(columns=['month', '% SLA met'])
    KPI7['month'] = KPI6['month']
    meeting_SLA = round(KPI6['size']/KPI1['size']*100, 2)
    KPI7['% SLA met'] = meeting_SLA

    fig7 = px.bar(KPI7, x= 'month', y='% SLA met', color='% SLA met', color_continuous_scale='reds')

    fig7.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = '% of incidences P1 meeting SLA',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})

    #Number of incidences P1 in the month not meeting SLA resolution time

    KPI8 = pd.DataFrame(columns=['month', 'Not SLA'])
    KPI8['month'] = KPI6['month']
    KPI8['Not SLA'] = KPI1['size']-KPI6['size']

    fig8 = px.bar(KPI8, x= 'month', y='Not SLA', color='Not SLA', color_continuous_scale='reds')

    fig8.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Number of incidences P1 in the month not meeting SLA resolution time',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})

    #% of incidences P1 not meeting SLA

    KPI9 = pd.DataFrame(columns=['month', '% SLA not met'])
    KPI9['month'] = KPI6['month']
    KPI9['% SLA not met'] = KPI8['Not SLA']/KPI1['size']

    fig9 = px.bar(KPI9, x= 'month', y=KPI9['% SLA not met'], color='% SLA not met', color_continuous_scale='reds')

    fig9.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='n_incidents',
                                    xaxis_title_text="'month'", showlegend=True, title = '% of incidences P1 not meeting SLA',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})

    #Average resolution time for incidences P1 meeting SLA

    KPI10 = df_raised2[df_raised2['SLA met']== 'YES']
    KPI10 = KPI10.groupby(['month'])['time taken'].mean()
    KPI10 = KPI10.rename('avg').reset_index()
    KPI10 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI10,monthcolumnname='month')

    fig10 = px.bar(KPI10, x= 'month', y= (KPI10['avg'].dt.total_seconds())/60, color= (KPI10['avg'].dt.total_seconds())/60, color_continuous_scale='reds')

    fig10.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='average resolution time in minutes',
                                    xaxis_title_text="month", showlegend=True, title = 'Average resolution time for incidences P1 meeting SLA',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})



    #Average resolution time for incidences P1 not meeting SLA

    KPI11 = df_raised2[df_raised2['SLA met']== 'NO']

    KPI11 = KPI11.groupby(['month'])['time taken'].mean()
    KPI11 = KPI11.rename('avg').reset_index()
    KPI11 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI11,monthcolumnname='month')


    fig11 = px.bar(KPI11, x= 'month', y= (KPI11['avg'].dt.total_seconds())/60, color= (KPI11['avg'].dt.total_seconds())/60, color_continuous_scale='reds')

    fig11.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='average resolution time in minutes',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Average resolution time for incidences P1 not meeting SLA',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})

    #Average resolution time per cause

    KPI12= df_raised2.groupby(['month', 'Inc. Type', ])['time taken'].mean()
    KPI12 = KPI12.rename('avg').reset_index()
    KPI12 = sort_dataframeby_monthorweek.Sort_Dataframeby_Month(df=KPI12,monthcolumnname='month')

    fig12 = px.bar(KPI12, x= 'month', y= (KPI12['avg'].dt.total_seconds())/3600, color = 'Inc. Type', barmode = 'stack')

    fig12.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_title_text='average resolution time in hours',
                                    xaxis_title_text="'month'", showlegend=True, title = 'Average resolution time per cause',
                                    plot_bgcolor="#323130", paper_bgcolor="#323130", font=dict(color="white"),
                                    margin= {'t': 50, 'b': 10, 'l': 10, 'r': 0})
    
    output= [fig1, fig2, fig3, fig3, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12]
    
    if KPI == 1:
        return output
    elif KPI == 2:
        return fig1
    elif KPI == 3:
        return fig2
    elif KPI == 4:
        return fig3
    elif KPI == 5:
        return fig4
    elif KPI == 6:
        return fig5
    elif KPI == 7:
        return fig6
    elif KPI == 8:
        return fig7
    elif KPI == 9:
        return fig8
    elif KPI == 10:
        return fig9
    elif KPI == 11:
        return fig10
    elif KPI == 12:
        return fig11
    elif KPI == 13:
        return fig12


if __name__ == '__main__':
    application.run(debug=True, use_reloader=False)
