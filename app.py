import base64
import io
import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Инициализация приложения
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Загрузка данных по умолчанию
def load_default_data():
    default_data = {
        'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                 '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10'],
        'segment': ['New', 'New', 'Returning', 'Returning', 'Loyal',
                   'New', 'Loyal', 'Returning', 'New', 'Loyal'],
        'visits': [5, 3, 7, 6, 10, 4, 8, 5, 6, 9],
        'time_spent': [10.5, 8.2, 15.3, 12.1, 20.0, 9.0, 18.5, 11.2, 10.8, 19.2],
        'conversion': [0.2, 0.15, 0.35, 0.3, 0.5, 0.18, 0.45, 0.25, 0.22, 0.48],
        'revenue': [120, 90, 210, 180, 300, 108, 270, 150, 132, 288]
    }
    return pd.DataFrame(default_data)

# Глобальная переменная для хранения данных
global_df = load_default_data()

# Макет приложения
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Анализ клиентской активности", className="text-center my-4"), width=12),
        dbc.Col(html.P("Интерактивный дашборд для анализа поведения клиентов", 
                      className="text-center text-muted mb-4"), width=12)
    ]),
    
    # Загрузка файла
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.I(className="bi bi-cloud-arrow-up me-2"),
                    "Перетащите или ",
                    html.A('выберите CSV файл')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0'
                },
                multiple=False
            ),
            html.Div(id='output-data-upload', className="small text-muted"),
        ], width=12)
    ]),
    
    # Фильтры и контролы
    dbc.Row([
        dbc.Col([
            html.Label("Выберите период:", className="form-label"),
            dcc.Dropdown(
                id='period-selector',
                options=[
                    {'label': 'День', 'value': 'D'},
                    {'label': 'Неделя', 'value': 'W'},
                    {'label': 'Месяц', 'value': 'M'},
                    {'label': 'Квартал', 'value': 'Q'},
                    {'label': 'Год', 'value': 'Y'}
                ],
                value='D',
                clearable=False,
                className="mb-3"
            )
        ], width=3),
        
        dbc.Col([
            html.Label("Выберите метрику:", className="form-label"),
            dcc.Dropdown(
                id='metric-selector',
                options=[
                    {'label': 'Количество посещений', 'value': 'visits'},
                    {'label': 'Время на сайте (мин)', 'value': 'time_spent'},
                    {'label': 'Конверсия (%)', 'value': 'conversion'},
                    {'label': 'Выручка ($)', 'value': 'revenue'}
                ],
                value='visits',
                clearable=False,
                className="mb-3"
            )
        ], width=3),
        
        dbc.Col([
            html.Label("Выберите сегмент:", className="form-label"),
            dcc.Dropdown(
                id='segment-selector',
                options=[{'label': seg, 'value': seg} for seg in global_df['segment'].unique()],
                value=global_df['segment'].unique().tolist(),
                multi=True,
                className="mb-3"
            )
        ], width=6)
    ], className="my-4 g-3"),
    
    # Индикаторы
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Всего клиентов", className="bg-primary text-white"),
            dbc.CardBody([
                html.H4(id='total-customers', className="card-title text-center")
            ])
        ], className="shadow-sm"), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Среднее время", className="bg-info text-white"),
            dbc.CardBody([
                html.H4(id='avg-time', className="card-title text-center")
            ])
        ], className="shadow-sm"), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Общая конверсия", className="bg-success text-white"),
            dbc.CardBody([
                html.H4(id='total-conversion', className="card-title text-center")
            ])
        ], className="shadow-sm"), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Средняя выручка", className="bg-warning text-dark"),
            dbc.CardBody([
                html.H4(id='avg-revenue', className="card-title text-center")
            ])
        ], className="shadow-sm"), width=3)
    ], className="my-4 g-4"),
    
    # Графики
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series-chart', className="border rounded p-2 bg-white"), width=12)
    ], className="my-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='category-pie', className="border rounded p-2 bg-white"), width=6),
        dbc.Col(dcc.Graph(id='histogram', className="border rounded p-2 bg-white"), width=6)
    ], className="my-4 g-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-plot', className="border rounded p-2 bg-white"), width=12)
    ], className="my-4"),
    
    # Таблица
    dbc.Row([
        dbc.Col([
            html.H5("Детальные данные", className="mt-4"),
            dash_table.DataTable(
                id='data-table',
                data=global_df.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in global_df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px'
                },
                filter_action="native",
                sort_action="native"
            )
        ], width=12)
    ], className="my-4")
], fluid=True)

# Callback для загрузки данных
@callback(
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Output('segment-selector', 'options'),
    Output('segment-selector', 'value'),
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_data(contents, filename):
    global global_df
    
    if contents is None:
        return dash.no_update
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename.lower():
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Неподдерживаемый формат файла"
        
        # Проверяем необходимые колонки
        required_columns = ['date', 'segment', 'visits', 'time_spent', 'conversion']
        if not all(col in df.columns for col in required_columns):
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Файл должен содержать колонки: date, segment, visits, time_spent, conversion"
        
        global_df = df
        
        # Генерируем опции для селектора сегментов
        segment_options = [{'label': seg, 'value': seg} for seg in df['segment'].unique()]
        
        # Подготавливаем данные для таблицы
        columns = [{'name': col, 'id': col} for col in df.columns]
        data = df.to_dict('records')
        
        return data, columns, segment_options, df['segment'].unique().tolist(), f"Загружен файл: {filename}"
    
    except Exception as e:
        print(e)
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"Ошибка при загрузке файла: {str(e)}"

# Callback для обновления графиков и индикаторов
@callback(
    Output('time-series-chart', 'figure'),
    Output('category-pie', 'figure'),
    Output('histogram', 'figure'),
    Output('scatter-plot', 'figure'),
    Output('total-customers', 'children'),
    Output('avg-time', 'children'),
    Output('total-conversion', 'children'),
    Output('avg-revenue', 'children'),
    Input('data-table', 'data'),
    Input('period-selector', 'value'),
    Input('metric-selector', 'value'),
    Input('segment-selector', 'value')
)
def update_visualizations(data, period, metric, segments):
    if not data:
        return {}, {}, {}, {}, "0", "0 мин", "0%", "$0"
    
    df = pd.DataFrame(data)
    
    # Фильтрация по сегментам
    if segments:
        df = df[df['segment'].isin(segments)]
    
    # Преобразование даты
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Группировка по периоду
    period_df = df.resample(period).sum()
    period_df.reset_index(inplace=True)
    
    # Форматирование метрик
    metric_labels = {
        'visits': 'Количество посещений',
        'time_spent': 'Время на сайте (мин)',
        'conversion': 'Конверсия (%)',
        'revenue': 'Выручка ($)'
    }
    
    # Временной ряд
    time_series = px.line(
        period_df, 
        x='date', 
        y=metric,
        title=f"Динамика {metric_labels[metric]} по периоду",
        labels={'date': 'Дата', metric: metric_labels[metric]},
        template='plotly_white'
    )
    time_series.update_layout(
        hovermode="x unified",
        xaxis_title="Дата",
        yaxis_title=metric_labels[metric]
    )
    
    # Круговая диаграмма по сегментам
    pie_df = df.groupby('segment').sum().reset_index()
    pie = px.pie(
        pie_df,
        names='segment',
        values=metric,
        title=f"Распределение {metric_labels[metric]} по сегментам",
        hole=0.3,
        template='plotly_white'
    )
    pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # Гистограмма
    hist = px.histogram(
        df, 
        x=metric, 
        color='segment',
        title=f"Распределение {metric_labels[metric]}",
        barmode='overlay',
        nbins=10,
        template='plotly_white',
        labels={metric: metric_labels[metric]}
    )
    hist.update_layout(
        bargap=0.1,
        xaxis_title=metric_labels[metric],
        yaxis_title="Количество записей"
    )
    
    # Scatter plot
    scatter = px.scatter(
        df.reset_index(),
        x='visits',
        y='conversion',
        color='segment',
        title="Корреляция между посещениями и конверсией",
        size='revenue' if 'revenue' in df.columns else None,
        hover_data=['date'],
        template='plotly_white',
        labels={
            'visits': 'Количество посещений',
            'conversion': 'Уровень конверсии',
            'revenue': 'Выручка',
            'segment': 'Сегмент'
        }
    )
    scatter.update_layout(
        xaxis_title="Количество посещений",
        yaxis_title="Уровень конверсии"
    )
    
    # Индикаторы
    total_customers = len(df)
    avg_time = f"{df['time_spent'].mean():.1f} мин"
    total_conversion = f"{df['conversion'].mean()*100:.1f}%"
    avg_revenue = f"${df['revenue'].mean():.0f}" if 'revenue' in df.columns else "$0"
    
    return (
        time_series,
        pie,
        hist,
        scatter,
        total_customers,
        avg_time,
        total_conversion,
        avg_revenue
    )

if __name__ == '__main__':
    app.run(debug=True)
