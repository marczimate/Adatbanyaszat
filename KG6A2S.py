import os
import pandas as pd
import pycountry
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import plotly.graph_objects as go


# Dash app létrehozása
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# A program aktuális könyvtárának meghatározása és a fájl beolvasása
current_directory = os.path.dirname(os.path.abspath(__file__))
file_name = '3_varhato_elettartam.csv'  # A fájl neve
file_path = os.path.join(current_directory, file_name)

# Fájl beolvasása és hibakezelés
try:
    data = pd.read_csv(file_path)
    print("Fájl sikeresen beolvasva.")
except FileNotFoundError:
    data = pd.DataFrame()
    print(f"A fájl nem található ezen az útvonalon: {file_path}")
except Exception as e:
    data = pd.DataFrame()
    print(f"Hiba történt a fájl beolvasása közben: {e}")

# Átalakítjuk a 'Life expectancy' oszlopot numerikus értékekre, ha szükséges
data['Life expectancy'] = pd.to_numeric(data['Life expectancy'], errors='coerce')

# Manuális országnevek és kódok átalakítása
country_name_mapping = {
    "Bolivia (Plurinational State of)": "BOL",
    "Democratic Republic of the Congo": "COD",
    "Iran (Islamic Republic of)": "IRN",
    "Micronesia (Federated States of)": "FSM",
    "Republic of Korea": "KOR",
    "Swaziland": "SWZ",
    "The former Yugoslav republic of Macedonia": "MKD",
    "Turkey": "TUR",
    "Venezuela (Bolivarian Republic of)": "VEN"
}

# Országkódok hozzáadása az adatokhoz a "Country" oszlop alapján, speciális nevek átalakításával
def get_country_code(name):
    if name in country_name_mapping:
        return country_name_mapping[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return None

# Országkód hozzáadása
data['Country Code'] = data['Country'].apply(get_country_code)

# Ellenőrizzük, hogy minden országnak sikerült-e az országkódot hozzárendelni
if data['Country Code'].isnull().any():
    missing_countries = data[data['Country Code'].isnull()]['Country'].unique()
    print(f"Ezekhez az országokhoz nem találtunk kódot: {missing_countries}")

# Alkalmazás layoutja, háttérszín és stílus hozzáadása
app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '40px', 'fontFamily': 'Arial, sans-serif'},  # Világos háttér és nagyobb padding
    children=[
        html.H1("Interaktív Dash Alkalmazás", style={'textAlign': 'center', 'color': '#2c3e50', 'padding-bottom': '20px'}),

        # Tab struktúra létrehozása
        dcc.Tabs(id="tabs-example", value='tab-1', children=[
            dcc.Tab(label='Az Ön és a Projekt adatai', value='tab-1', style={'backgroundColor': '#e0e0e0', 'padding': '10px'}),
            dcc.Tab(label='Országok GDP elemzése', value='tab-2', style={'backgroundColor': '#e0e0e0', 'padding': '10px'}),
            dcc.Tab(label='Népesség és GDP szűrés', value='tab-3', style={'backgroundColor': '#e0e0e0', 'padding': '10px'}),
            dcc.Tab(label='Várható élettartam elemzés', value='tab-4', style={'backgroundColor': '#e0e0e0', 'padding': '10px'}),
            dcc.Tab(label='Év és változó gyakorisági elemzés', value='tab-5', style={'backgroundColor': '#e0e0e0', 'padding': '10px'}),
            dcc.Tab(label='Tematikus térkép', value='tab-6', style={'backgroundColor': '#e0e0e0', 'padding': '10px'}),
            dcc.Tab(label='Regressziós modell', value='tab-7', style={'backgroundColor': '#e0e0e0', 'padding': '10px'})
        ]),

        # Tab tartalmának megjelenítése
        html.Div(id='tabs-content-example', style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})
    ]
)

# Callback a tabok tartalmának megjelenítéséhez
@app.callback(
    Output('tabs-content-example', 'children'),
    Input('tabs-example', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.Div([
                html.H3('Az Ön adatai', style={'textAlign': 'center', 'color': '#3498db', 'fontSize': '26px'}),  # Nagyobb betűméret
                dcc.Markdown('''
                             
                    **Név**: *Marczi Máté*
                    
                    **Neptun-kód**: *KG6A2S*  
                    
                    **Email**: *marczi.mate01@gmail.com*
                ''', style={'fontSize': '18px'}),  # Nagyobb betűméret a Markdown tartalomhoz
            ], style={'textAlign': 'center', 'padding': '25px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'backgroundColor': '#ffffff', 'marginBottom': '25px'}),
            
            html.Div([
                html.H3('A projekt adatai\n', style={'textAlign': 'center', 'color': '#3498db', 'fontSize': '26px'}),  # Nagyobb betűméret
                dcc.Markdown('''
                    **Cél**: Ez a projekt bemutatja, hogyan lehet interaktív Dash alkalmazást létrehozni. 
                    
                    **Megvalósítás**: A Dash könyvtár segítségével.
                    
                    **Adathalmaz információ**: Az elemzéshez használt adatok a várható élettartamot tartalmazzák különböző országokban.  
                ''', style={'fontSize': '18px'}),  # Nagyobb betűméret a Markdown tartalomhoz
            ], style={'textAlign': 'center', 'padding': '25px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'backgroundColor': '#ffffff'})
        ], style={'maxWidth': '800px', 'margin': 'auto'})


    # További tabok tartalmának kezelése
    elif tab == 'tab-2':
        return html.Div([
            html.H3("Országok GDP elemzése évekre lebontva", style={'textAlign': 'center', 'color': '#3498db'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                value=None,
                placeholder="Válasszon egy országot",
                style={'width': '50%', 'margin': 'auto'}
            ),
            dcc.Graph(id='gdp-graph'),
            html.P("Az ország GDP alakulása az évek során.", style={'textAlign': 'center', 'color': '#7f8c8d'})
        ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})

    elif tab == 'tab-3':
        return html.Div([
            html.H3("Országok szűrése népesség és GDP alapján", style={'textAlign': 'center', 'color': '#3498db'}),
            html.Label('Válasszon népesség tartományt (millió fő):', style={'color': '#2c3e50'}),
            dcc.RangeSlider(
                id='population-slider',
                min=data['Population'].min() / 1e6,
                max=data['Population'].max() / 1e6,
                step=1,
                value=[data['Population'].min() / 1e6, data['Population'].max() / 1e6],
                marks={int(i): f'{int(i)}M' for i in range(int(data['Population'].min() / 1e6), int(data['Population'].max() / 1e6) + 1, 50)},
                tooltip={"placement": "bottom", "always_visible": False}
            ),
            html.Br(),
            html.Label('Válasszon GDP tartományt:', style={'color': '#2c3e50'}),
dcc.RangeSlider(
    id='gdp-slider',
    min=round(data['GDP'].min(), -3),  # Kerekítjük a legközelebbi 1000-re
    max=round(data['GDP'].max(), -3),  # Kerekítjük a legközelebbi 1000-re
    step=1000,  # 1000-es lépték
    value=[round(data['GDP'].min(), -3), round(data['GDP'].max(), -3)],  # Kerekítve
    marks={i: '{:,} USD'.format(i) for i in range(round(int(data['GDP'].min()), -3), round(int(data['GDP'].max()), -3) + 10000, 10000)},
    tooltip={"placement": "bottom", "always_visible": False}
),
html.Br(),
            html.Div(id='filtered-countries', style={'color': '#2c3e50'})
        ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})

    elif tab == 'tab-4':
        return html.Div([
            html.H3("Többváltozós legördülő: Várható élettartam", style={'textAlign': 'center', 'color': '#3498db'}),
            dcc.Dropdown(
                id='multi-country-dropdown',
                options=[{'label': country, 'value': country} for country in data['Country'].unique()],
                multi=True,
                placeholder="Válasszon egy vagy több országot",
                style={'width': '50%', 'margin': 'auto'}
            ),
            dcc.Graph(id='life-expectancy-graph'),
            html.P("Az országok várható élettartamának változása az évek során.", style={'textAlign': 'center', 'color': '#7f8c8d'})
        ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})

    elif tab == 'tab-5':
        return html.Div([
        html.H3("Év és változó gyakorisági elemzés", style={'textAlign': 'center', 'color': '#3498db'}),
        html.Div([
            # Csúszka az évek kiválasztásához
            html.Div([
                dcc.Slider(
                    id='year-slider',
                    min=data['Year'].min(),
                    max=data['Year'].max(),
                    step=1,
                    value=data['Year'].min(),
                    marks={str(year): str(year) for year in data['Year'].unique()},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={'width': '70%', 'display': 'inline-block', 'padding-right': '20px'}),  # Csúszka balra igazítva

            # Legördülő választó a változókhoz, jobbra igazítva
            html.Div([
                dcc.Dropdown(
                    id='variable-dropdown',
                    options=[{'label': 'GDP', 'value': 'GDP'},
                             {'label': 'Life expectancy', 'value': 'Life expectancy'},
                             {'label': 'Population', 'value': 'Population'}],
                    placeholder="Válasszon egy változót",
                    style={'width': '100%'}
                ),
            ], style={'width': '30%', 'display': 'inline-block'}),  # Dropdown jobbra igazítva
        ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Flexbox stílus a sorba rendezéshez

        html.Br(),
        html.Label('Válassza ki az osztályközök számát:', style={'color': '#2c3e50'}),
        dcc.Input(id='bins-input', type='number', value=10, min=1, max=100, style={'width': '100px', 'textAlign': 'center'}),
        html.Br(),
        html.Br(),
        dcc.Graph(id='histogram-graph'),
        html.P("A kiválasztott változó gyakorisági eloszlása az adott évben.", style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})

    elif tab == 'tab-6':
        return html.Div([
        html.H3("Tematikus térkép", style={'textAlign': 'center', 'color': '#3498db'}),
        dcc.Dropdown(
            id='map-variable-dropdown',
            options=[{'label': 'GDP', 'value': 'GDP'},
                     {'label': 'Life expectancy', 'value': 'Life expectancy'},
                     {'label': 'Population', 'value': 'Population'}],
            placeholder="Válasszon egy változót",
            style={'width': '50%', 'margin': 'auto'}
        ),
        html.Div(
            dcc.Graph(id='choropleth-map'),
            style={'display': 'flex', 'justify-content': 'center'}  # A térkép középre igazítása
        ),
        html.P("A kiválasztott változó alakulása térképen, dinamikusan az évek során.", style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})


    elif tab == 'tab-7':
        return html.Div([
            html.H3("Regressziós modell: Várható élettartam és GDP kapcsolata", style={'textAlign': 'center', 'color': '#3498db'}),
            html.Label("Válasszon egy évet:", style={'color': '#2c3e50'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in data['Year'].unique()],
                value=data['Year'].min(),
                placeholder="Válasszon egy évet",
                style={'width': '50%', 'margin': 'auto'}
            ),
            html.Br(),
            html.Label("Válasszon regressziós polinom fokozatot:", style={'color': '#2c3e50'}),
            dcc.Slider(
                id='degree-slider',
                min=1,
                max=5,
                step=1,
                value=1,
                marks={i: f'Fokozat {i}' for i in range(1, 6)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            dcc.Graph(id='regression-graph'),
            html.P("A regressziós modell vizualizálása.", style={'textAlign': 'center', 'color': '#7f8c8d'})
        ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(0,0,0,0.1)'})

# Callback a GDP diagramhoz (Tab 2)
@app.callback(
    Output('gdp-graph', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_gdp_graph(selected_country):
    # Ha nincs kiválasztva ország, ne jelenítsen meg grafikont
    if not selected_country:
        return go.Figure()  # Üres figurát ad vissza, ami nem jelenít meg semmit

    # Szűrjük az adatokat a kiválasztott ország alapján
    filtered_data = data[data['Country'] == selected_country]

    # GDP oszlopdiagram létrehozása
    fig = px.bar(
        filtered_data,
        x='Year',
        y='GDP',
        title=f'{selected_country} GDP alakulása oszlopdiagramon',
        labels={'GDP': 'GDP (USD)', 'Year': 'Év'}
    )

    # Csak a diagram háttérszínének megváltoztatása
    fig.update_layout(
        xaxis_title='Év',
        yaxis_title='GDP (USD)',
        title_x=0.5,
        plot_bgcolor='rgba(0, 136, 204, 0.1)',  # Világoskék háttér a diagramhoz
        bargap=0.1,
        xaxis=dict(
            tickmode='linear',
            tick0=filtered_data['Year'].min(),
            dtick=1,
        )
    )

    return fig





# A fejlettségi szint fordítása
def translate_status(status):
    if status == 'Developed':
        return 'Fejlett'
    elif status == 'Developing':
        return 'Fejlődő'
    else:
        return 'Ismeretlen'

# Callback a szűrt országokhoz (Tab 4) fejlettségi szinttel együtt
@app.callback(
    Output('filtered-countries', 'children'),
    [Input('population-slider', 'value'),
     Input('gdp-slider', 'value')]
)
def update_filtered_countries(pop_range, gdp_range):
    # Szűrjük az adatokat a népesség és GDP tartomány alapján
    filtered_data = data[
        (data['Population'] >= pop_range[0] * 1e6) & (data['Population'] <= pop_range[1] * 1e6) &
        (data['GDP'] >= gdp_range[0]) & (data['GDP'] <= gdp_range[1])
    ]

    if filtered_data.empty:
        return "Nincs találat a megadott feltételekkel."
    
    # Eltávolítjuk az ismétlődő országokat
    unique_countries = filtered_data.drop_duplicates(subset='Country')

    # Szűrt országok listázása, fejlettségi szinttel
    return html.Ul([
        html.Li(f"{country} - {translate_status(status)}") 
        for country, status in zip(unique_countries['Country'], unique_countries['Status'])
    ])

# Callback a várható élettartam grafikonhoz (Tab 4)
@app.callback(
    Output('life-expectancy-graph', 'figure'),
    [Input('multi-country-dropdown', 'value')]
)
def update_life_expectancy_graph(selected_countries):
    # Ha nincs kiválasztva ország, ne jelenítsen meg grafikont
    if not selected_countries:
        return go.Figure()  # Üres figurát ad vissza, ami nem jelenít meg semmit

    filtered_data = data[data['Country'].isin(selected_countries)]

    fig = px.line(
        filtered_data,
        x='Year',
        y='Life expectancy',
        color='Country',
        title='Várható élettartam alakulása több országban',
        labels={
            'Life expectancy': 'Várható élettartam (év)',
            'Year': 'Év',
            'Country': 'Ország'
        }
    )

    fig.update_traces(
        mode="lines+markers",
        hovertemplate='<br>Várható élettartam=%{y} év',
    )

    fig.update_layout(
        xaxis_title='Év',
        yaxis_title='Várható élettartam (év)',
        title_x=0.5,
        showlegend=True,
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tick0=filtered_data['Year'].min(),
        ),
        hovermode='x unified'
    )

    return fig





# Callback a gyakorisági diagram frissítéséhez (Tab 5)
@app.callback(
    Output('histogram-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('variable-dropdown', 'value'),
     Input('bins-input', 'value')]
)
def update_histogram(selected_year, selected_variable, bins):
    # Ha nincs kiválasztva változó vagy év, ne jelenítsen meg grafikont
    if not selected_variable or not selected_year:
        return go.Figure()  # Üres figurát ad vissza, ami nem jelenít meg semmit

    filtered_data = data[data['Year'] == selected_year]

    fig = px.histogram(
        filtered_data,
        x=selected_variable,
        nbins=bins,
        title=f'{selected_variable} gyakorisági eloszlása {selected_year}-ben',
        labels={selected_variable: selected_variable}
    )

    fig.update_layout(
        xaxis_title=selected_variable,
        yaxis_title='Gyakoriság',
        bargap=0.2,
        title_x=0.5
    )

    return fig


# Callback a dinamikus tematikus térkép frissítéséhez (Tab 6)
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('map-variable-dropdown', 'value')]
)
def update_dynamic_map(selected_variable):
    # Ha nincs kiválasztva változó, akkor ne jelenítsünk meg semmit
    if not selected_variable:
        return go.Figure()  # Üres figurát ad vissza, ami nem jelenít meg semmit

    # Rendezzük az adatokat az 'Year' szerint növekvő sorrendben
    filtered_data = data.sort_values(by='Year')

    # Dinamikus tematikus térkép létrehozása az év alapján animálva (legkisebb évszámtól a legnagyobbig)
    fig = px.choropleth(
        filtered_data,  # Az egész adatot használjuk, hogy minden év elérhető legyen
        locations='Country Code',
        color=selected_variable,
        hover_name='Country',
        animation_frame='Year',  # Az év animációs keretként használva
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f'{selected_variable} alakulása dinamikusan az évek során'
    )

    # A layout testreszabása a jobb megjelenítés érdekében
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        title_x=0.5,  # Cím középre igazítása
        height=600,  # Növeljük a térkép magasságát
        width=1000   # Növeljük a térkép szélességét
    )

    return fig







# Callback a regressziós modell frissítéséhez (Tab 7)
@app.callback(
    Output('regression-graph', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('degree-slider', 'value')]
)
def update_regression_graph(selected_year, degree):
    filtered_data = data[data['Year'] == selected_year]
    filtered_data = filtered_data.dropna(subset=['GDP', 'Life expectancy'])

    X = filtered_data['GDP'].values.reshape(-1, 1)
    y = filtered_data['Life expectancy'].values

    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)

    X_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    X_range_poly = poly.transform(X_range)
    y_pred = model.predict(X_range_poly)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_data['GDP'], y=filtered_data['Life expectancy'],
                             mode='markers', name='Eredeti adatok'))
    fig.add_trace(go.Scatter(x=X_range.flatten(), y=y_pred, mode='lines',
                             name=f'Regressziós modell (Fokozat: {degree})'))

    fig.update_layout(
        title=f'Várható élettartam és GDP kapcsolata {selected_year}-ben',
        xaxis_title='GDP',
        yaxis_title='Várható élettartam',
        showlegend=True,
        title_x=0.5
    )

    return fig

# Alkalmazás futtatása
if __name__ == '__main__':
    app.run_server(debug=True)

