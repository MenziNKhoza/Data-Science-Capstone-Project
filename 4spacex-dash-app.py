# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])


# TASK 2: Add a callback function to render success-pie-chart based on selected site dropdown
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df_grouped = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            df_grouped, 
            values='class', 
            names='Launch Site', 
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter the dataframe for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Fallback check: if the filtered dataset is empty
        if filtered_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title=f'No data available for site: {entered_site}',
                xaxis={'visible': False},
                yaxis={'visible': False},
                annotations=[{
                    'text': 'No matching records found for this selection.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16, 'color': 'gray'}
                }]
            )
            return fig
        
        # Render a pie chart showing success (class=1) vs failed (class=0) count for that site
        fig = px.pie(
            filtered_df, 
            names='class', 
            title=f'Total Success vs. Failed Launches for site {entered_site}'
        )
        return fig


# TASK 4: Add a callback function to render the success-payload-scatter-chart scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(entered_site, payload_slider):
    low, high = payload_slider
    
    # Filter the dataframe by the selected payload mass range first
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        target_df = filtered_df
        title_text = 'Correlation between Payload and Success for All Sites'
    else:
        target_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title_text = f'Correlation between Payload and Success for site {entered_site}'
        
    # Fallback check if filtered dataset is empty
    if target_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title_text,
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'No matching records found for this payload range and site.',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16, 'color': 'gray'}
            }]
        )
        return fig
        
    # Render scatter plot
    fig = px.scatter(
        target_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title_text
    )
    return fig

# Print confirmation to terminal so you know the newest file is running
print("Starting SpaceX Dash Application...")

# Run the app with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True, port=8050)
    
    