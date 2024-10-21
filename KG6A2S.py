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
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
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
data['Life expectancy '] = pd.to_numeric(data['Life expectancy '], errors='coerce')

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
    
    

# Alkalmazás layoutja, sötét színek hozzáadása az egész oldalra
app.layout = html.Div(
    style={
        'backgroundColor': '#343a40', 
        'padding': '40px', 
        'fontFamily': 'Arial, sans-serif', 
        'minHeight': '100vh', 
        'display': 'flex', 
        'flexDirection': 'column'
    },  # Egész oldal háttérszín
    children=[
        html.H1("Interaktív Dash Alkalmazás", style={'textAlign': 'center', 'color': '#3498db', 'padding-bottom': '20px'}),

        
        # Tab struktúra létrehozása sötét háttérrel és világos feliratokkal
        dcc.Tabs(id="tabs-example", value='tab-1', children=[
            dcc.Tab(label='Személyes és a Projekt adatai', value='tab-1', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'}),
            dcc.Tab(label='Országok GDP elemzése', value='tab-2', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'}),
            dcc.Tab(label='Népesség és GDP szűrés', value='tab-3', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'}),
            dcc.Tab(label='Várható élettartam elemzés', value='tab-4', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'}),
            dcc.Tab(label='Év és változó gyakorisági elemzés', value='tab-5', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'}),
            dcc.Tab(label='Tematikus térkép', value='tab-6', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'}),
            dcc.Tab(label='Regressziós modell', value='tab-7', style={'backgroundColor': '#343a40', 'color': '#ffffff', 'padding': '10px'})
        ]),
        
      


        # Tab tartalmának megjelenítése
        html.Div(id='tabs-content-example', style={
            'backgroundColor': '#343a40', 
            'padding': '20px', 
            'borderRadius': '10px', 
            'boxShadow': '0 0 10px rgba(255,255,255,0.1)', 
            'flex': '1'
        })
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
                html.H3('Személyes adatok', style={'textAlign': 'center', 'color': '#3498db', 'fontSize': '26px'}),  # Nagyobb betűméret
                dcc.Markdown('''
                             
                    **Név**: *Marczi Máté*
                    
                    **Neptun-kód**: *KG6A2S*  
                    
                    **Email**: *marczi.mate01@gmail.com*
                ''', style={'fontSize': '18px'}),  # Nagyobb betűméret a Markdown tartalomhoz
            ], style={'textAlign': 'center', 'padding': '25px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'backgroundColor': '#ffffff', 'marginBottom': '25px'}),
            
            html.Div([
                html.H3('A projekt adatai\n', style={'textAlign': 'center', 'color': '#3498db', 'fontSize': '26px'}),  # Nagyobb betűméret
                dcc.Markdown('''
                    **Cél**: Egy interaktív műszerfal létrehozása, amely vizualizálja a különböző országok várható élettartamát, GDP-jét és népességét, lehetővé téve az adatok időbeli elemzését és összehasonlítását. 
                    
                    **Megvalósítás**: Python és Plotly Dash használatával létrehozott alkalmazás, amely dinamikus legördülő menükkel, csúszkákkal és grafikonokkal segíti a felhasználói interakciót. Több lapot tartalmaz, ahol tematikus térképek és idősoros grafikonok jelenítik meg a kiválasztott adatokat.
                    
                    **Adathalmaz információ**: A 3_varhato_elettartam.csv adathalmaz országokra és évekre bontva tartalmazza a népesség, GDP és várható élettartam adatokat, amelyeket vizualizációkhoz és elemzésekhez használunk.  
                ''', style={'fontSize': '18px'}),  # Nagyobb betűméret a Markdown tartalomhoz
            ], style={'textAlign': 'center', 'padding': '25px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'backgroundColor': '#ffffff'})
        ], style={'maxWidth': '800px', 'margin': 'auto'})


    # További tabok tartalmának kezelése
    elif tab == 'tab-2':
        
        countries_with_gdp = data.dropna(subset=['GDP'])['Country'].unique()
        
        return html.Div([
            html.H3("Országok GDP elemzése évekre lebontva", style={'textAlign': 'center', 'color': '#3498db'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in countries_with_gdp],
                value=None,
                placeholder="Válasszon egy országot",
                style={'width': '25%', 'margin': 'auto','color': '#3498db'},
                className='country-dropdown'
            ),
            dcc.Graph(id='gdp-graph'),
            
        ], style={'backgroundColor': '#343a40', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(255,255,255,0.1)'})

    elif tab == 'tab-3':
        return html.Div([
        html.H3("Országok szűrése népesség és GDP alapján", style={'textAlign': 'center', 'color': '#3498db'}),
        html.Label('Válasszon népesség tartományt (millió fő):', style={'color': '#ffffff'}),
        dcc.RangeSlider(
            id='population-slider',
            min=data['Population'].min() / 1e6,
            max=data['Population'].max() / 1e6,
            step=1,
            value=[data['Population'].min() / 1e6, data['Population'].max() / 1e6],
            marks={int(i): {'label': f'{int(i)}M', 'style': {'color': '#ffffff'}} for i in range(int(data['Population'].min() / 1e6), int(data['Population'].max() / 1e6) + 1, 50)},  # Fehér szín a számokhoz
            tooltip={"placement": "bottom", "always_visible": False}
        ),
        html.Br(),
        html.Label('Válasszon GDP tartományt:', style={'color': '#ffffff'}),
        dcc.RangeSlider(
            id='gdp-slider',
            min=round(data['GDP'].min(), -3),
            max=round(data['GDP'].max(), -3),
            step=1000,
            value=[round(data['GDP'].min(), -3), round(data['GDP'].max(), -3)],
            marks={i: {'label': '{:,} USD'.format(i), 'style': {'color': '#ffffff'}} for i in range(round(int(data['GDP'].min()), -3), round(int(data['GDP'].max()), -3) + 10000, 10000)},  # Fehér szín a számokhoz
            tooltip={"placement": "bottom", "always_visible": False}
        ),
        html.Br(),
        html.Div(id='filtered-countries', style={'color': '#ffffff'})
    ], style={'backgroundColor': '#343a40', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(255,255,255,0.1)'})


    elif tab == 'tab-4':
        
        countries_with_life_expectancy = data.dropna(subset=['Life expectancy '])['Country'].unique()
        
        return html.Div([
        html.H3("Országok várható élettartam elemzése évekre lebontva", style={'textAlign': 'center', 'color': '#3498db'}),
        dcc.Dropdown(
            id='multi-country-dropdown',
            options=[{'label': country, 'value': country} for country in countries_with_life_expectancy],
            multi=True,
            placeholder="Válasszon egy vagy több országot",
            style={'width': '30%', 'margin': 'auto', 'color': '#3498db'},
            className='life-expectancy-dropdown'
        ),
        # Placeholder for the graph, initially empty
        html.Div(id='life-expectancy-graph-container')
    ], style={'backgroundColor': '#343a40', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(255,255,255,0.1)'})


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
                    marks={str(year): {'label': str(year), 'style': {'color': '#ffffff'}} for year in data['Year'].unique()},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={'width': '70%', 'display': 'inline-block', 'padding-right': '20px'}),  # Csúszka balra igazítva

            # Legördülő választó a változókhoz, jobbra igazítva
            html.Div([
                dcc.Dropdown(
                    id='variable-dropdown',
                    options=[{'label': 'GDP', 'value': 'GDP'},
                             {'label': 'Várható élettartam', 'value': 'Life expectancy '},
                             {'label': 'Népesség', 'value': 'Population'},                 
                             {'label': 'Felnőttkori halálozás', 'value': 'Adult Mortality'},
                             {'label': 'Csecsemőhalálozás', 'value': 'infant deaths'},
                             {'label': 'Alkohol fogysztás', 'value': 'Alcohol'},
                             {'label': 'Kiadások aránya', 'value': 'percentage expenditure'},
                             {'label': 'Hepatitisz B oltottság', 'value': 'Hepatitis B'},
                             {'label': 'Kanyaró', 'value': 'Measles '},
                             {'label': 'Átlagos testtömegindex', 'value': 'BMI '},
                             {'label': '5 éves kor alatti halálozás', 'value': 'under-five deaths '},
                             {'label': 'Polio oltottság', 'value': 'Polio'},
                             {'label': 'Állami eü kiadások', 'value': 'Total expenditure'},
                             {'label': 'Diftéria oltottság', 'value': 'Diphtheria '},
                             {'label': 'HIV/AIDS halálozások', 'value': 'HIV/AIDS'},
                             {'label': 'Soványság 1-19 éves', 'value': ' thinness  1-19 years'},
                             {'label': 'Soványság 5-9 éves', 'value': ' thinness 5-9 years'},
                             {'label': 'Emberi fejlettség', 'value': 'Income composition of resources'},
                             {'label': 'Iskolai évek száma', 'value': 'Schooling'},],
                    placeholder="Válasszon egy változót",
                    style={'width': '50%', 'margin': 'auto','color': '#3498db'},
                    className='variable-dropdown'
                ),
                
                
            ], style={'width': '40%', 'display': 'inline-block'}),  # Dropdown jobbra igazítva
        ], style={'display': 'flex', 'justify-content': 'space-between'}),  # Flexbox stílus a sorba rendezéshez

        html.Br(),
        html.Label('Válassza ki az osztályközök számát:', style={'color': '#ffffff'}),
        dcc.Input(id='bins-input', type='number', value=10, min=1, max=100, style={'width': '100px', 'textAlign': 'center', 'backgroundColor': '#343a40', 'color': '#ffffff'}),
        html.Br(),
        html.Br(),
        dcc.Graph(id='histogram-graph'),
    ], style={'backgroundColor': '#343a40', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(255,255,255,0.1)'})

    elif tab == 'tab-6':
        return html.Div([
        html.H3("Tematikus térkép", style={'textAlign': 'center', 'color': '#3498db'}),
        dcc.Dropdown(
            id='map-variable-dropdown',
            options=[{'label': 'GDP', 'value': 'GDP'},
                     {'label': 'Várható élettartam', 'value': 'Life expectancy '},
                     {'label': 'Népesség', 'value': 'Population'},                 
                     {'label': 'Felnőttkori halálozás', 'value': 'Adult Mortality'},
                     {'label': 'Csecsemőhalálozás', 'value': 'infant deaths'},
                     {'label': 'Alkohol fogysztás', 'value': 'Alcohol'},
                     {'label': 'Kiadások aránya', 'value': 'percentage expenditure'},
                     {'label': 'Hepatitisz B oltottság', 'value': 'Hepatitis B'},
                     {'label': 'Kanyaró', 'value': 'Measles '},
                     {'label': 'Átlagos testtömegindex', 'value': 'BMI '},
                     {'label': '5 éves kor alatti halálozás', 'value': 'under-five deaths '},
                     {'label': 'Polio oltottság', 'value': 'Polio'},
                     {'label': 'Állami eü kiadások', 'value': 'Total expenditure'},
                     {'label': 'Diftéria oltottság', 'value': 'Diphtheria '},
                     {'label': 'HIV/AIDS halálozások', 'value': 'HIV/AIDS'},
                     {'label': 'Soványság 1-19 éves', 'value': ' thinness  1-19 years'},
                     {'label': 'Soványság 5-9 éves', 'value': ' thinness 5-9 years'},
                     {'label': 'Emberi fejlettség', 'value': 'Income composition of resources'},
                     {'label': 'Iskolai évek száma', 'value': 'Schooling'},],
            placeholder="Válasszon egy változót",
            style={'width': '40%', 'margin': 'auto', 'color': '#3498db'},
    className='dropdown'
        ),
        html.Div(
            dcc.Graph(id='choropleth-map'),
            style={'display': 'flex', 'justify-content': 'center', 'backgroundColor': '#343a40'}
        ),
    ], style={'backgroundColor': '#343a40', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 0 10px rgba(255,255,255,0.1)'})


    elif tab == 'tab-7':
        return html.Div([
        html.H3("Regressziós modell: Várható élettartam és GDP kapcsolata", 
                style={'textAlign': 'center', 'color': '#3498db'}),

       html.Div(
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in data['Year'].unique()],
        value=None,
        placeholder="Válasszon egy évet",
        style={
            'width': '100%',  
            'color': '#3498db', 
            'backgroundColor': '#ffffff', 
            'borderRadius': '5px',  
            'border': 'none',
            'padding': '0px',
            'height': 'auto',
            'line-height': 'normal',
            'boxShadow': 'none'
        }
    ),
    style={
        'width': '20%',  
        'margin': 'auto',
        'backgroundColor': '#ffffff',
        'borderRadius': '5px',
        'padding': '0px',
        'boxShadow': '0 0 0 rgba(0, 0, 0, 0)'
    }
)

,
        html.Br(),
        html.Div([
            html.Label("Válasszon regressziós polinom fokozatot:", style={'color': '#ffffff'}),
            dcc.Slider(
                id='degree-slider',
                min=1,
                max=5,
                step=1,
                value=1,
                marks={i: f'Fokozat {i}' for i in range(1, 6)},
            ),
        ], style={'padding': '10px'}),

        html.Br(),

        dcc.Graph(id='regression-graph'),

        
               
    ], 
    style={'backgroundColor': '#343a40', 
           'padding': '20px', 
           'borderRadius': '10px', 
           'boxShadow': '0 0 10px rgba(255,255,255,0.1)'})



# Callback a GDP diagramhoz (Tab 2)
@app.callback(
    Output('gdp-graph', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_gdp_graph(selected_country):
    # Ha nincs kiválasztva ország, ne jelenítsen meg diagramot, üres layout
    if not selected_country:
        return go.Figure().update_layout(
            plot_bgcolor='#343a40',  # Alapértelmezett háttérszín, ha nincs adat
            paper_bgcolor='#343a40',  # Papír színe
            font=dict(color='#ffffff'),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )

    # Szűrjük az adatokat a kiválasztott ország alapján
    filtered_data = data[data['Country'] == selected_country]

    # Ellenőrizzük, hogy van-e adat a kiválasztott országra
    if filtered_data.empty:
        return go.Figure().update_layout(
            plot_bgcolor='#343a40',  # Alapértelmezett háttérszín, ha nincs adat
            paper_bgcolor='#343a40',  # Papír színe
            font=dict(color='#ffffff'),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )

    # GDP oszlopdiagram létrehozása
    fig = px.bar(
        filtered_data,
        x='Year',
        y='GDP',
        title=f'{selected_country} GDP alakulása oszlopdiagramon',
        labels={'GDP': 'GDP (USD)', 'Year': 'Év'}
    )

    # Diagram színeinek frissítése
    fig.update_layout(
        xaxis_title='Év',
        yaxis_title='GDP (USD)',
        title_x=0.5,
        plot_bgcolor='#343a40',  # Diagram háttérszíne
        paper_bgcolor='#343a40',  # Papír háttérszíne
        font=dict(color='#ffffff'),  # Szöveg színe
        bargap=0.1,
        xaxis=dict(
            tickmode='linear',
            tick0=filtered_data['Year'].min(),
            dtick=1,
            color='#ffffff'  # Tengely színe
        ),
        yaxis=dict(
            color='#ffffff'  # Tengely színe
        ),
        hoverlabel=dict(
            font_size=16
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

# Callback a szűrt országokhoz (Tab 3) fejlettségi szinttel együtt
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
    Output('life-expectancy-graph-container', 'children'),
    [Input('multi-country-dropdown', 'value')]
)
def update_life_expectancy_graph(selected_countries):
    # Ha nincs kiválasztva ország, vagy üres a lista, ne jelenjen meg semmi
    if not selected_countries or len(selected_countries) == 0:
        return html.Div()  # Üres div, hogy ne jelenjen meg semmi

    # Szűrjük az adatokat a kiválasztott országok alapján
    filtered_data = data[data['Country'].isin(selected_countries)]

    # Ha nincs adat a kiválasztott országokra, ne jelenjen meg a diagram
    if filtered_data.empty:
        return html.Div("Nincs elérhető adat a kiválasztott ország(ok)ra.", style={'color': 'white', 'textAlign': 'center'})

    # Vonaldiagram létrehozása a kiválasztott országok adataihoz
    fig = px.line(
        filtered_data,
        x='Year',
        y='Life expectancy ',
        color='Country',
        title='Várható élettartam alakulása több országban',
        labels={
            'Life expectancy ': 'Várható élettartam (év)',
            'Year': 'Év',
            'Country': 'Ország'
        }
    )

    fig.update_traces(
        mode="lines+markers",
        hovertemplate='<br>Várható élettartam=%{y} év',
    )

    # A layout testreszabása, hogy a stílus illeszkedjen a sötét témához
    fig.update_layout(
        xaxis_title='Év',
        yaxis_title='Várható élettartam (év)',
        title_x=0.5,
        showlegend=True,
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
        font=dict(color='#ffffff'),
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tick0=filtered_data['Year'].min(),
            color='#ffffff'
        ),
        yaxis=dict(
            color='#ffffff'
        ),
        hovermode='x unified',
        hoverlabel=dict(
            font_size=16
        )
        
    )

    # Csak akkor jelenjen meg a grafikon, ha van kiválasztott adat
    if not filtered_data.empty:
        return dcc.Graph(figure=fig)

    # Ha nincs kiválasztva adat, akkor ne jelenjen meg a grafikon
    return html.Div("Nincs elérhető adat a kiválasztott ország(ok)ra.", style={'color': 'white', 'textAlign': 'center'})






# Callback a gyakorisági diagram frissítéséhez (Tab 5)
@app.callback(
    Output('histogram-graph', 'figure'),
    [Input('year-slider', 'value'),
     Input('variable-dropdown', 'value'),
     Input('bins-input', 'value')]
)
def update_histogram(selected_year, selected_variable, bins):
    # Ellenőrizzük, hogy minden bemenet megvan-e
    if selected_year is None or not selected_variable or bins is None:
        # Üres diagram visszaadása, ha nincs megadva bemenet
        return go.Figure().update_layout(
            plot_bgcolor='#343a40', 
            paper_bgcolor='#343a40',
            font=dict(color='#ffffff'),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )

    # Szűrjük az adatokat a kiválasztott év alapján
    filtered_data = data[data['Year'] == selected_year]

    # Ha nincs adat, üres diagramot adunk vissza
    if filtered_data.empty:
        return go.Figure().update_layout(
            plot_bgcolor='#343a40', 
            paper_bgcolor='#343a40',
            font=dict(color='#ffffff'),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
    
    # Fordítás létrehozása a kiválasztott változóhoz
    variable_translation = {
        'Life expectancy ': 'Várható élettartam',
        'Population': 'Népesség',
        'Adult Mortality': 'Felnőttkori halálozás',
        'infant deaths': 'Csecsemőhalálozás',
        'GDP': 'GDP',
        'Alcohol': 'Alkohol fogysztás',
        'percentage expenditure': 'Kiadások aránya',
        'Hepatitis B': 'Hepatitisz B oltottság',
        'Measles ': 'Kanyaró',
        'BMI ': 'Átlagos testtömegindex',
        'under-five deaths ': '5 éves kor alatti halálozás',
        'Polio': 'Polio oltottság',
        'Total expenditure': 'Állami eü kiadások',
        'Diphtheria ': 'Diftéria oltottság',
        'HIV/AIDS': 'HIV/AIDS halálozások',
        ' thinness  1-19 years': 'Soványság 1-19 éves',
        ' thinness 5-9 years': 'Soványság 5-9 éves',
        'Income composition of resources': 'Emberi fejlettség',
        'Schooling': 'Iskolai évek száma',
        
    }
    
    translated_variable = variable_translation.get(selected_variable, selected_variable)

    # Gyakorisági diagram létrehozása a kiválasztott változóra
    fig = px.histogram(
        filtered_data,
        x=selected_variable,
        nbins=bins,
        title=f'{translated_variable} gyakorisági eloszlása {selected_year}-ben',
        labels={selected_variable: translated_variable}
    )
    
    fig.update_traces(
        hovertemplate=f'<b>{translated_variable}</b>: %{{x}}<br><b>Gyakoriság</b>: %{{y}}<extra></extra>'
    )

    # Diagram színének és stílusának testreszabása a sötét témához
    fig.update_layout(
        xaxis_title=translated_variable,
        yaxis_title='Gyakoriság',
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
        font=dict(color='#ffffff'),
        xaxis=dict(
            color='#ffffff'
        ),
        yaxis=dict(
            color='#ffffff'
        ),
        bargap=0.2,
        title_x=0.5,
        hoverlabel=dict(
            font_size=16
        )
    )

    return fig





# Callback a dinamikus tematikus térkép frissítéséhez (Tab 6)
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('map-variable-dropdown', 'value')]
)
def update_dynamic_map(selected_variable):
    # Ha nincs kiválasztva változó, akkor üres ábrát adunk vissza
    if not selected_variable:
        return go.Figure().update_layout(
            plot_bgcolor='#343a40',  # Háttérszín, ha nincs adat
            paper_bgcolor='#343a40',  # Papír színe
            font=dict(color='#ffffff'),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
    
   # Fordítás létrehozása a kiválasztott változóhoz
    variable_translation = {
        'Life expectancy ': 'Várható élettartam',
        'Population': 'Népesség',
        'GDP': 'GDP'
    }

    translated_variable = variable_translation.get(selected_variable, selected_variable)
    
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
        title=f'{translated_variable} alakulása dinamikusan az évek során'
    )

    # A layout testreszabása a jobb megjelenítés érdekében
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
        font=dict(color='#ffffff'),
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
    # Ha nincs kiválasztott év, üres diagram visszaadása
    if not selected_year:
        return go.Figure().update_layout(
            plot_bgcolor='#343a40',  # Háttérszín, ha nincs adat
            paper_bgcolor='#343a40',  # Papír háttérszín
            font=dict(color='#ffffff'),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )

    # Ha van kiválasztott év, folytatjuk az adatfeldolgozást
    filtered_data = data[data['Year'] == selected_year]
    filtered_data = filtered_data.dropna(subset=['GDP', 'Life expectancy '])

    X = filtered_data['GDP'].values.reshape(-1, 1)
    y = filtered_data['Life expectancy '].values

    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)

    X_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    X_range_poly = poly.transform(X_range)
    y_pred = model.predict(X_range_poly)

    fig = go.Figure()
    # Az eredeti adatok trace
    fig.add_trace(go.Scatter(
        x=filtered_data['GDP'], y=filtered_data['Life expectancy '],
        mode='markers', name='Eredeti adatok',
        hovertemplate='GDP: %{x}<br>Várható élettartam: %{y}',  # Csak x és y értékek megjelenítése
    ))

    # A regressziós modell trace
    fig.add_trace(go.Scatter(
        x=X_range.flatten(), y=y_pred,
        mode='lines', name=f'Regressziós modell (Fokozat: {degree})',
        hovertemplate='<b>GDP: %{x}<br>Várható élettartam: %{y}<b>',  # Csak x és y értékek megjelenítése
    ))

    fig.update_layout(
        title=f'Várható élettartam és GDP kapcsolata {selected_year}-ben',
        xaxis_title='GDP',
        yaxis_title='Várható élettartam',
        plot_bgcolor='#343a40',
        paper_bgcolor='#343a40',
        font=dict(color='#ffffff'),
        showlegend=True,
        title_x=0.5,
        hoverlabel=dict(
            font_size=16
        )
    )

    return fig


# Alkalmazás futtatása
if __name__ == '__main__':
    app.run_server(debug=True)

