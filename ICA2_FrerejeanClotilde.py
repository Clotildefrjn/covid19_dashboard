import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import numpy as np

app = dash.Dash()
df = pd.read_excel("covid_main_database.xlsx")
df2 = pd.read_excel("covid_second_database.xlsx")

app.title = 'DASHBOARD COVID-19'


#df['percentage'] = df_worldwide['percentage'].astype(str)
df['date'] = pd.to_datetime(df['date'])
df2['date'] = pd.to_datetime(df2['date'])
# selects the "data last updated" date and create a new dataset 
date_max_by_country = df2.groupby("country")["date"].idxmax()
vaccin_data = df2.loc[date_max_by_country,["continent", "country", "people_vaccinated","population"]]
                        
#new columns for positive tests
df2["positive_tests"] = df2["new_tests"] * df2["positive_rate"]


# Create a dropdown menu to select the continent
continent_options = [{"label": c, "value": c} for c in df["continent"].unique()]
continent_dropdown = dcc.Dropdown(id="continent-dropdown", options=continent_options, value="All")

# Create a dropdown menu to select the country
country_options = [{"label": c, "value": c} for c in df["country"].unique()]
country_dropdown = dcc.Dropdown(id="country-dropdown", options=country_options, value="All")


app.layout = html.Div([
    #import css file
	html.Link(
        rel='stylesheet',
        href='style.css'
    	),

    html.H1(children='Dashboard Covid 19'
        ),

    # Dropdown for continent selection
    html.Div(id='dropcont', children='Select continent:', style={'width': '49%', 'display': 'inline-block' }),
    continent_dropdown,
    
    # Dropdown for country selection
    html.Div(id='dropcount', children='Select country:', style={'width': '49%', 'display': 'inline-block' }),
    country_dropdown,
    
    # Counters for deaths, cases, and vaccine
    html.Div(id='counters', children=[

        html.Div(
            id='total-cases-counter',
            children=[
                html.H2(id='total-cases-value',children='0'),
                html.P('Total Cases')
            ],style={"marging":"50px"},
            className='counter'),

        html.Div([
            html.H2(id='total-deaths-counter',children="0"),
            html.P('Total Deaths')
        ], style={"marging":"50px"}, className='counter'),

        html.Div([
            html.H2(id='total-vaccins-counter',children="0"),
            html.P('Total Vaccinacion')
        ], style={"marging":"50px"},className='counter')
    ]),

    # Bar plot for total cases or deaths over location
    html.Div(id='bar',children=[
        dcc.RadioItems(id='total-cases-deaths-selector', options=[{'label': 'Cases', 'value': 'cases'}, {'label': 'Deaths', 'value': 'deaths'}],value='cases'),
        dcc.Graph(id='total-cases-deaths-histogram')
    ], style={"width": "49%", "display": "inline-block"}),
    
    # Line plot for evolution of cases or deaths over time
    html.Div(id='line',children=[
        dcc.RadioItems(id='cases-deaths-selector', options=[{'label': 'Cases', 'value': 'cases'}, {'label': 'Deaths', 'value': 'deaths'}], value='cases'),
        dcc.Graph(id='evolution-cases-deaths-lineplot')],
        style={"width": "49%", "display": "inline-block"}),

    # Stacked bar chart that shows the breakdown of icu_patients, hosp_patients, and total_tests by continent or country over time
    html.Div(id='stacked',children=[
        dcc.Graph(id='patient-test-breakdown-bar'),
    ], style={"width": "49%", "display": "inline-block"}),
    
    # Stacked area chart that shows the breakdown of new cases and deaths by location
     html.Div(id='area',children=[
        dcc.Graph(id='age-group-stacked-area'),
    ], style={"width": "49%", "display": "inline-block"}),
    
    # Bar plot for median age by country
     html.Div(id='age',children=[
        dcc.Graph(id='median-age-bar'),
    ], style={"width": "49%", "display": "inline-block"}),
    
     
    # Bubble chart of people vaccinated vs population
    html.Div(id='bubble',children=[
        dcc.Graph(id='bubble_chart'),
    ], style={"width": "49%", "display": "inline-block"}),

    # Scatter plot for reproduction rate over time
    html.Div(id='scatter',children=[
        dcc.Graph(id='reproduction-rate-scatter'),
    ], style={"width": "49%", "display": "inline-block"}),
    
    # Histogram
     html.Div(id='hist',children=[
        dcc.Graph(id='histogram_continent'),
    ], style={"width": "49%", "display": "inline-block"}),
    
    
    # Map for cases and deaths per population of countries
    html.Div(id='map',children=[
        dcc.RadioItems(id='map-cases-deaths-selector', options=[{'label': 'Cases', 'value': 'cases'}, {'label': 'Deaths', 'value': 'deaths'}], value='cases'),
        dcc.Graph(id='map-graph')],
    className='map-container'),
])


# Callback for updating the country dropdown
            
@app.callback(
    Output("country-dropdown", "options"),
    [Input("continent-dropdown", "value")]
)
def update_country_dropdown(selected_continent):
    if selected_continent == "All":
        options = [{"label": country, "value": country} for country in df["country"].unique()]
    else:
        options = [{"label": country, "value": country} for country in df[df["continent"] == selected_continent]["country"].unique()]
    return options


# Callbacks for updating the counters and the visualizations
@app.callback(
    Output("total-cases-value", "children"), 
    [Input("continent-dropdown", "value"), Input("country-dropdown", "value")])
def update_total_cases_counter(selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent]
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["country"] == selected_country]
    else:
        filtered_df = df[
            (df["continent"] == selected_continent) & (df["country"] == selected_country)
        ]
    if filtered_df["new_cases"].sum() == 0:
        return "not specified"
    else:
        return filtered_df["new_cases"].sum()


@app.callback(Output("total-deaths-counter", "children"), [Input("continent-dropdown", "value"), Input("country-dropdown", "value")])
def update_total_deaths_counter(selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent]
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["country"] == selected_country]
    else:
        filtered_df = df[
            (df["continent"] == selected_continent) & (df["country"] == selected_country)
        ]
        
    if filtered_df["new_deaths"].sum() == 0:
        return "not specified"
    else:
        return filtered_df["new_deaths"].sum()

@app.callback(Output("total-vaccins-counter", "children"), [Input("continent-dropdown", "value"), Input("country-dropdown", "value")])
def update_total_vaccins_counter(selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filteredvaccin_data =  vaccin_data
    elif selected_continent != "All" and selected_country == "All":
        filteredvaccin_data = vaccin_data[vaccin_data["continent"] == selected_continent]
    elif selected_continent == "All" and selected_country != "All":
        filteredvaccin_data =  vaccin_data[vaccin_data["country"] == selected_country]
    else:
        filteredvaccin_data = vaccin_data[
            (vaccin_data["continent"] == selected_continent) & (vaccin_data["country"] == selected_country)
        ]

    if filteredvaccin_data["people_vaccinated"].sum() == 0:
        return "not specified"
    else:
        return filteredvaccin_data["people_vaccinated"].sum()

# Callback function that updates the total deaths or cases graph based on the selected continent and country
@app.callback(
    Output("total-cases-deaths-histogram", "figure"),
    [Input("continent-dropdown", "value"), Input("country-dropdown", "value"), Input("total-cases-deaths-selector", "value")]
)
def update_total_cases_deaths_graph(selected_continent, selected_country, cases_deaths):
    column_name = 'new_cases' if cases_deaths == 'cases' else 'new_deaths'
    
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df.groupby("continent")[column_name].sum()
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent].groupby("country")[column_name].sum()
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["country"] == selected_country].groupby("date")[column_name].sum()
    else:
        filtered_df = df[(df["continent"] == selected_continent) & (df["country"] == selected_country)].groupby("date")[column_name].sum()
    
    data = [go.Bar(x=filtered_df.index, y=filtered_df.values, name="Total Cases" if cases_deaths == 'cases' else "Total Deaths")]

    return {
        "data": data,
        "layout": go.Layout(
            title=f"Total {cases_deaths} per Location",
            yaxis={"title": f"Total {cases_deaths}"},
            xaxis={"title": "Location"}
        )
    }

# Callback function that updates Line plot for evolution of cases or deaths over time
@app.callback(
    Output("evolution-cases-deaths-lineplot", "figure"),
    [Input("cases-deaths-selector", "value"),
     Input("continent-dropdown", "value"),
     Input("country-dropdown", "value")]
)
def update_evolution_cases_deaths_lineplot(selector, selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df.groupby("date").sum()
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent].groupby("date").sum()
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["country"] == selected_country].groupby("date").sum()
    else:
        filtered_df = df[(df["continent"] == selected_continent) & (df["country"] == selected_country)].groupby("date").sum()
    
    if selector == "cases":
        y_data = filtered_df["total_cases"]
    else:
        y_data = filtered_df["total_deaths"]
    
    return {
        "data": [
            {
                "x": filtered_df.index,
                "y": y_data,
                "type": "line",
                "name": selector
            }
        ],
        "layout": go.Layout(
            title=f"Evolution of {selector} over Time",
            xaxis={"title": f"New {selector}"},
            yaxis={"title": "Date"}
        ) 
   }


@app.callback(
    Output("reproduction-rate-scatter", "figure"),
    [Input("continent-dropdown", "value"), Input("country-dropdown", "value")]
)
def update_reproduction_rate_scatter(selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent]
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["country"] == selected_country]
    else:
        filtered_df = df[
            (df["continent"] == selected_continent) & (df["country"] == selected_country)
        ]

    data = [
        go.Scatter(
            x=filtered_df["date"],
            y=filtered_df["reproduction_rate"],
            mode="markers",
            name="Reproduction Rate"
        )
    ]
    return {
        "data": data,
        "layout": go.Layout(
            title="Reproduction Rate over Time",
            xaxis={"title": "Date"},
            yaxis={"title": "Reproduction Rate"}
        )
    }


@app.callback(
    Output("median-age-bar", "figure"),
    [Input("continent-dropdown", "value"), Input("country-dropdown", "value")]
)
def update_median_age_bar(selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df.groupby("continent").mean()
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent].groupby("country").mean()
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["continent"] == selected_continent].groupby("country").mean()
    else:
        filtered_df = df[df["continent"] == selected_continent].groupby("country").mean()

    data = [
            go.Bar(
                x=filtered_df.index,
                y=filtered_df["median_age"],
                name="Median Age"
            )
        ]
    return {
        "data": data,
        "layout": go.Layout(
            title="Median Age by Location",
            yaxis={"title": "Median Age"},
            xaxis={"title": "Location"}
        )
    }

@app.callback(
    Output("patient-test-breakdown-bar", "figure"),
    [Input("continent-dropdown", "value")]
)
def update_patient_test_breakdown_bar(selected_continent):
    if selected_continent == "All" :
        filtered_df2 = df2.groupby(["continent", "date"]).sum()
    else :
        filtered_df2 = df2[df2["continent"] == selected_continent].groupby(["country", "date"]).sum()

    data = [
        
        go.Bar(
            name="Positive Tests",
            x=filtered_df2.index.get_level_values(1),
            y=filtered_df2["positive_tests"],

        ),
        go.Bar(
            x=filtered_df2.index.get_level_values(1),
            y=filtered_df2["hosp_patients"],
            name="Hospitalized Patients",
            
        ),
        go.Bar(
            x=filtered_df2.index.get_level_values(1),
            y=filtered_df2["icu_patients"],
            name="ICU Patients",
        
        )
    ]

    return {
        "data": data,
        "layout": go.Layout(
            title=f"ICU/Hospital/Positive Tests breakdown for {selected_continent} over Time",
            xaxis={"title": "Date"},
            yaxis={"title": "Count"},
            
    )
}



# Create a callback function that updates the map graph based on the selected country map-cases-deaths-selector
@app.callback(
    Output("map-graph", "figure"),
    [Input("map-cases-deaths-selector", "value")]
)
def update_map_graph(selector):
                        
    filtered_df = df.groupby("country").mean()
    filtered_df2 = df.groupby("country").sum()
   
    if selector == "cases":
        data = filtered_df2["new_cases"]
    else:
        data = filtered_df2["new_deaths"]

    # calculate percentage of cases/deaths in the population
    data = data / filtered_df["population"] * 100
    locations = data.index.tolist()
    z = data.values.tolist()
    return {
        "data": [go.Choropleth(locations=locations, z=z, locationmode='country names')],
        "layout": go.Layout(title=f"Percentage of {selector} in Population by Country", geo={"projection": {"type": "natural earth"}})
    }


@app.callback(
    Output("age-group-stacked-area", "figure"),
    [Input("continent-dropdown", "value"), Input("country-dropdown", "value")]
)
def update_age_group_stacked_area(selected_continent, selected_country):
    if selected_continent == "All" and selected_country == "All":
        filtered_df = df.groupby(["date", "continent"]).sum()
    elif selected_continent != "All" and selected_country == "All":
        filtered_df = df[df["continent"] == selected_continent].groupby(["date", "country"]).sum()
    elif selected_continent == "All" and selected_country != "All":
        filtered_df = df[df["country"] == selected_country].groupby(["date"]).sum()
    else:
        filtered_df = df[(df["continent"] == selected_continent) & (df["country"] == selected_country)].groupby(["date"]).sum()

    data = [
        go.Scatter(
            x=filtered_df.index.get_level_values(0),
            y=filtered_df["new_cases"],
            name="New Cases",
            stackgroup='one',
            
            mode="lines",
            fill="tozeroy"
        ),
        go.Scatter(
            x=filtered_df.index.get_level_values(0),
            y=filtered_df["new_deaths"],
            name="New Deaths",
            stackgroup='one',   
            mode="lines",
            fill="tozeroy"
        )
    ]


    return {
    "data": data,
    "layout": go.Layout(
        title="New Cases and Deaths by time",
        yaxis={"title": "New cases and deaths", "type":"linear"},
        xaxis={"title": "Date"},
        legend={"x": 0, "y": 1},
        hovermode='x',
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=True,
        legend_orientation="h"
        )
    }

# Callback function that updates the bubble chart graph of people vaccinated by population
@app.callback(
    Output("bubble_chart", "figure"),
    [Input("continent-dropdown", "value")]
)
def update_bubble_chart(selected_continent):
    if selected_continent == "All" :
        filtered_df2 = vaccin_data.groupby("country").agg({'population': 'sum', 'people_vaccinated': 'sum', 'country': 'first'})
    elif selected_continent != "All" :
        filtered_df2 = vaccin_data[vaccin_data["continent"] == selected_continent].groupby("country").agg({'population': 'sum', 'people_vaccinated': 'sum', 'country': 'first'})
    
    data = [
        go.Scatter(
            x=filtered_df2["population"],
            y=filtered_df2["people_vaccinated"],
            mode='markers',
            text=filtered_df2["country"],
            marker=dict(size=filtered_df2["people_vaccinated"] / filtered_df2["population"] * 70, color=filtered_df2["people_vaccinated"]/ filtered_df2["population"] * 100),
        )
    ]

    return {
        "data": data,
        "layout": go.Layout(
            title="People Vaccinated vs Population",
            xaxis={"title": "Population"},
            yaxis={"title": "People Vaccinated"},
            showlegend=False,
            hovermode='closest',
            margin=dict(l=50, r=50, t=50, b=50)
       
   )
}



# Callback function that updates the total deaths or cases graph based on the selected continent and country
@app.callback(
    Output("histogram_continent", "figure"),
    [Input("continent-dropdown", "value")]
)
def update_histogram_continent(selected_continent):
    df["new_date"] = df["date"].dt.year
    filtered_df = df.groupby(["new_date", "continent"]).sum()
  
    data = []
    for c in filtered_df.index.levels[1]:
        # filter the dataframe again for the specific continent
        data.append(
            go.Histogram(
                x=filtered_df.index.get_level_values(0),
                y=filtered_df["new_cases"],
                name=f"{c}"
            )
        )

    return {
        "data": data,
        "layout": go.Layout(
            title=f"Total cases per Location",
            yaxis={"title": f"Total cases"},
            xaxis={"title": "Year"}
        )
    }



if __name__ == "__main__":
    app.run_server()
