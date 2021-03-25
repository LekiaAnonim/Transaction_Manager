import dash
import dash_core_components as dcc
import dash_html_components as html
#import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
from datetime import datetime

data = pd.read_excel("DataBase.xlsx")
df = pd.read_excel('DataBase.xlsx')
data.to_csv("DataBase.csv", index=None, header=True)

data["Date"] = pd.to_datetime(data["Date"])
data.sort_values("Date", inplace=True)

analysis_data = data.set_index('Date')
# analysis_data=analysis_data.fillna(0)
#now = datetime.now()
# dd/mm/YY H:M:S
#date_time = now.strftime("%B %d, %Y")
last_date = df['Date'].iloc[-1]
selected_data = analysis_data.loc[str(last_date)]


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Transaction Manager Dashboard"

#fig = px.bar(data, x="Date", y="Number of kg", color="Status", barmode="group")


def generate_table(dataframe, max_rows=1000):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Transaction Manager Dashboard", className="header-title"
                ),
                html.P(
                    children="Visualise your transactions over time",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(id='navigate-output',
                 children=[
                     html.Div(id="date-selector",
                              children=[
                                  html.Div(children="Date Selector",
                                           className="menu-title"),
                                  dcc.Input(id="date-select",
                                            placeholder='Enter date here...',
                                            type='text',
                                            value='')
                              ]
                              ),
                     html.Div(id="key-selector",
                              children=[
                                  html.Div(
                                      children="Key Indicators",
                                      className="key-title"
                                  ),
                                  dcc.Dropdown(id="key-dropdown",
                                               options=[
                                                   {'label': 'Amount Paid',
                                                    'value': 'Amount Paid'},
                                                   {'label': 'Number of Kg',
                                                    'value': 'Number of Kg'},
                                                   {'label': 'Debt',
                                                       'value': 'Debt'},
                                                   {'label': 'Credit',
                                                    'value': 'Credit'}
                                               ],
                                               value='Amount Paid',
                                               placeholder="Select key indicators",
                                               clearable=True
                                               #is_loading = True
                                               #labelStyle={'display': 'block'}
                                               ),

                              ]
                              ),

                 ]
                 ),
        html.Div(children='',id='my-output'),
        html.Div(id="table",
                 children=[
                     html.H4(children="Today's Sale"),
                     generate_table(selected_data)
                 ]
                 ),
        html.Div(id="date-picker",
                 children=[
                     html.Div(
                         children=[
                             html.Div(
                                 children="Chart Date Range Selector",
                                 className="menu-title"
                             ),
                             dcc.DatePickerRange(
                                 id="date-range",
                                 min_date_allowed=data.Date.min().date(),
                                 max_date_allowed=data.Date.max().date(),
                                 start_date=data.Date.min().date(),
                                 end_date=data.Date.max().date(),
                             ),
                         ]
                     )
                 ],
                 className="menu"
                 ),
        html.Div(id="charts",
                 children=[
                     html.Div(
                         children=dcc.Graph(
                             id="price-chart", config={"displayModeBar": True},
                         ),
                         className="card",
                     ),
                     html.Div(
                         children=dcc.Graph(
                             id="volume-chart", config={"displayModeBar": True},
                         ),
                         className="card",
                     ),
                 ],
                 className="wrapper",
                 ),
    ]
)

# ====================================================================


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(start_date, end_date):
    mask = (
        (data.Date >= start_date)
        & (data.Date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Amount Paid"],
                "type": "line",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Amount paid for sale",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "#", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Number of Kg"],
                "type": "line",
            },
        ],
        "layout": {
            "title": {"text": "Number of Kg Sold", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


# ====================================================================

@app.callback(
    Output("my-output", "children"),
    [
        Input("date-select", "value"),
        Input("key-dropdown", "value"),
    ],
)
def data_filter(date, label):
    global selected_data
    #analysis_data = data.set_index('Date')
    # analysis_data=analysis_data.fillna(0)
    selected_data = analysis_data.loc[str(date)]

    Label_output = selected_data[label].sum(skipna=True)
    return '{}'.format(Label_output)

#cleared =  len(selected_data[selected_data.Status=='Cleared'])
#notcleared = len(selected_data[selected_data.Status =='Not Cleared'])


if __name__ == "__main__":
    app.run_server(debug=True)
