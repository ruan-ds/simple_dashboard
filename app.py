import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output

# Load sales data from CSV file
df = pd.read_csv("sales.csv")
# Convert Date column to datetime format for proper filtering
df["Date"] = pd.to_datetime(df["Date"])

# Initialize the Dash application
app = dash.Dash(__name__)

# Define callback function that updates dashboard components based on user inputs
@app.callback(
    # Output components that will be updated
    [Output('kpis-container', 'children'),     # KPI cards container
     Output('bar-chart', 'figure'),            # Bar chart figure
     Output('line-chart', 'figure')],          # Line chart figure
    # Input components that trigger the callback
    [Input('product-dropdown', 'value'),       # Selected product from dropdown
     Input('date-range', 'start_date'),        # Start date from date picker
     Input('date-range', 'end_date'),          # End date from date picker
     Input('metric-radio', 'value')]           # Selected metric from radio buttons
)
def update_dashboard(selected_product, start_date, end_date, selected_metric):
    # Create date filter mask using boolean indexing
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    # Apply date filter to dataframe and create a copy
    filtered_df = df.loc[mask].copy()

    # Apply product filter if specific product is selected (not 'all')
    if selected_product != 'all':
        filtered_df = filtered_df[filtered_df['Product'] == selected_product]

    # Calculate KPI metrics from filtered data
    total_revenue = filtered_df["Total Value"].sum()        # Sum of all sales values
    total_quantity = filtered_df["Quantity"].sum()          # Sum of all quantities sold
    average_ticket = filtered_df["Total Value"].mean()      # Average transaction value

    # Create KPI cards as HTML div elements with formatted values
    kpis = [
        html.Div(f"Total Revenue: ${total_revenue:,.2f}", className="kpi-card"),
        html.Div(f"Total Quantity Sold: {total_quantity}", className="kpi-card"),
        html.Div(f"Average Ticket: ${average_ticket:,.2f}", className="kpi-card"),
    ]

    # Group filtered data by date and sum the selected metric for time series
    df_time_filtered = filtered_df.groupby("Date", as_index=False)[selected_metric].sum()

    # Create bar chart showing selected metric by product
    fig_bar = px.bar(filtered_df, x="Product", y=selected_metric, title=f"{selected_metric} per Product")
    # Apply dark theme styling to bar chart
    fig_bar.update_layout(
        paper_bgcolor="#1e293b",               # Background color around the plot area
        plot_bgcolor="#1e293b",                # Background color of the plot area itself
        font=dict(color="#e2e8f0")             # Light gray color for all text elements
    )
    # Style the grid lines with subtle transparency
    fig_bar.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")  # X-axis grid lines
    fig_bar.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")  # Y-axis grid lines

    # Create line chart showing selected metric over time
    fig_line = px.line(df_time_filtered, x="Date", y=selected_metric, title=f"{selected_metric} Over Time")
    # Apply dark theme styling to line chart
    fig_line.update_layout(
        paper_bgcolor="#1e293b",               # Background color around the plot area
        plot_bgcolor="#1e293b",                # Background color of the plot area itself
        font=dict(color="#e2e8f0")             # Light gray color for all text elements
    )
    # Style the grid lines with subtle transparency
    fig_line.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")  # X-axis grid lines
    fig_line.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")  # Y-axis grid lines

    # Return updated components: KPIs, bar chart, and line chart
    return kpis, fig_bar, fig_line

# Define the application layout structure
app.layout = html.Div([
    # Main dashboard title
    html.H1("Sales Dashboard"),

    # Controls section container
    html.Div([
        # Product selection dropdown
        html.Label("Select Product:", className="control-label"),        # Label for product dropdown
        dcc.Dropdown(
            id='product-dropdown',                                       # Unique ID for callback reference
            options=[{'label': 'All Products', 'value': 'all'}] +       # Default "All" option
                    [{'label': p, 'value': p} for p in df['Product'].unique()],  # Dynamic options from data
            value='all',                                                 # Default selected value
            className="dropdown"                                         # CSS class for styling
        ),

        # Date range selection
        html.Label("Select Date Range:", className="control-label"),     # Label for date picker
        dcc.DatePickerRange(
            id='date-range',                                             # Unique ID for callback reference
            min_date_allowed=df['Date'].min().date(),                    # Minimum selectable date from data
            max_date_allowed=df['Date'].max().date(),                    # Maximum selectable date from data
            start_date=df['Date'].min().date(),                          # Default start date
            end_date=df['Date'].max().date(),                            # Default end date
            display_format='YYYY-MM-DD',                                 # Date display format
            className="date-picker"                                      # CSS class for styling
        ),

        # Metric selection radio buttons
        html.Label("Select Metrics:", className="control-label"),        # Label for radio buttons
        dcc.RadioItems(
            id='metric-radio',                                           # Unique ID for callback reference
            options=[                                                    # Available metric options
                {'label': 'Revenue ($)', 'value': 'Total Value'},       # Revenue option
                {'label': 'Quantity', 'value': 'Quantity'}              # Quantity option
            ],
            value='Total Value',                                         # Default selected metric
            className="radio-group"                                      # CSS class for custom styling
        )
    ], className="controls-container"),                                  # Container CSS class

    # KPIs display container (populated by callback)
    html.Div(id='kpis-container', className="kpi-container"),

    # Charts section
    dcc.Graph(id='bar-chart', className="dash-graph"),                   # Bar chart component
    dcc.Graph(id='line-chart', className="dash-graph")                   # Line chart component
])

# Run the application in debug mode when script is executed directly
if __name__ == "__main__":
    app.run(debug=True)