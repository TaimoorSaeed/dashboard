import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load datasets
healthy_diet = pd.read_csv("epi_r.csv")
epicurious = pd.read_csv("All_Diets.csv")

# Remove duplicate rows
epicurious = epicurious.drop_duplicates()
healthy_diet = healthy_diet.drop_duplicates()

# Rename the column in epicurious to match the 'title' column in healthy_diet
epicurious.rename(columns={'Recipe_name': 'title'}, inplace=True)

# Renaming columns in the epicurious dataset to match the healthy_diet
epicurious.rename(columns={'Protein(g)': 'protein', 'Fat(g)': 'fat'}, inplace=True)

# Clean both title columns (strip spaces, convert to lowercase)
healthy_diet['title'] = healthy_diet['title'].str.lower().str.strip()
epicurious['title'] = epicurious['title'].str.lower().str.strip()

# Merge datasets
merged_data = pd.merge(healthy_diet, epicurious, on="title", how="inner", suffixes=("_healthy", "_epi"))

# Combined data
combined_data = merged_data

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Interactive Recipe Dashboard", style={"textAlign": "center", "marginBottom": "30px", "color": "#2c3e50"}),

    # Filters
    html.Div(
        style={
            "backgroundColor": "#ecf0f1", 
            "padding": "20px", 
            "borderRadius": "12px", 
            "boxShadow": "0 6px 12px rgba(0, 0, 0, 0.1)", 
            "marginBottom": "40px"
        },
        children=[
            html.Label("Select Cuisine Type:", style={"fontSize": "18px", "color": "#34495E", "marginBottom": "10px"}),
            dcc.Dropdown(
                id="cuisine-filter",
                options=[{"label": cuisine, "value": cuisine} for cuisine in combined_data["Cuisine_type"].unique()],
                value=combined_data["Cuisine_type"].unique()[0],
                multi=False,
                style={"width": "60%", "padding": "12px", "fontSize": "16px", "borderRadius": "8px", "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.1)"}
            ),

            html.Label("Select Calorie Range:", style={"fontSize": "18px", "color": "#34495E", "marginTop": "30px", "marginBottom": "10px"}),
            
            # RangeSlider styling
            html.Div(
                dcc.RangeSlider(
                    id="calorie-slider",
                    min=combined_data["calories"].min(),
                    max=combined_data["calories"].max(),
                    step=50,
                    marks={
                        int(cal): str(int(cal)) for cal in range(int(combined_data["calories"].min()), int(combined_data["calories"].max()), 500)
                    },
                    value=[combined_data["calories"].min(), combined_data["calories"].max()],
                ),
                style={"width": "80%", "padding": "20px", "marginBottom": "20px"}
            ),
        ]
    ),

    # Visualizations
    html.Div([
        html.Div([
            dcc.Graph(id="bar-chart", style={"borderRadius": "8px", "boxShadow": "0 4px 8px rgba(0,0,0,0.1)", "padding": "10px"}),
        ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

        html.Div([
            dcc.Graph(id="scatter-plot", style={"borderRadius": "8px", "boxShadow": "0 4px 8px rgba(0,0,0,0.1)", "padding": "10px"}),
        ], style={"width": "48%", "display": "inline-block"}),
    ], style={"display": "flex", "justifyContent": "space-between"}),

    html.Div([
        html.Div([
            dcc.Graph(id="heatmap", style={"borderRadius": "8px", "boxShadow": "0 4px 8px rgba(0,0,0,0.1)", "padding": "10px"}),
        ], style={"width": "48%", "display": "inline-block", "paddingRight": "2%"}),

        html.Div([
            dcc.Graph(id="line-chart", style={"borderRadius": "8px", "boxShadow": "0 4px 8px rgba(0,0,0,0.1)", "padding": "10px"}),
        ], style={"width": "48%", "display": "inline-block"}),
    ], style={"display": "flex", "justifyContent": "space-between"}),
])

# Callbacks for interactivity
@app.callback(
    [
        Output("bar-chart", "figure"),
        Output("scatter-plot", "figure"),
        Output("heatmap", "figure"),
        Output("line-chart", "figure")
    ],
    [
        Input("cuisine-filter", "value"),
        Input("calorie-slider", "value")
    ]
)
def update_dashboard(selected_cuisine, calorie_range):
    # Filter data based on user input
    filtered_data = combined_data[(combined_data["Cuisine_type"] == selected_cuisine) &
                                  (combined_data["calories"] >= calorie_range[0]) &
                                  (combined_data["calories"] <= calorie_range[1])]

    # Bar Chart: Number of recipes per cuisine
    bar_chart = px.bar(filtered_data, x="Cuisine_type", y="title", title="Number of Recipes by Cuisine")

    # Scatter Plot: Calories vs Prep Time
    scatter_plot = px.scatter(filtered_data, x="rating", y="calories", color="Cuisine_type", title="Calories vs Rating")

    # Heatmap: Correlation between numerical values
    heatmap = px.imshow(filtered_data.corr(),
                        title="Correlation Heatmap",
                        color_continuous_scale="Viridis")

    # Line Chart: Recipe count over time (if date/time data exists, adjust accordingly)
    if "date" in filtered_data.columns:
        filtered_data["date"] = pd.to_datetime(filtered_data["date"], errors='coerce')
        line_chart = px.line(filtered_data, x="date", y="title", title="Recipe Trends Over Time")
        line_chart.update_traces(line=dict(width=2), marker=dict(size=6, opacity=0.8))  # Customize line and marker
    else:
        line_chart = px.line(title="No Date Information Available")

    return bar_chart, scatter_plot, heatmap, line_chart


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8054)
