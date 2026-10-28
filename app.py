import streamlit as st
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import numpy as np

# Streamlit page configuration
st.set_page_config(
    layout="wide",
    page_title="Restaurant Dashboard",
    page_icon="",
    initial_sidebar_state="expanded"
)

# Professional restaurant-focused color palette (inspired by iFood and food industry trends)
RESTAURANT_COLORS = {
    'primary': '#EA1D2C',      # iFood red - stimulates appetite
    'secondary': '#FF6B47',    # Vibrant orange - energy and warmth
    'accent': '#FFD700',       # Gold - premium quality
    'success': '#32CD32',      # Fresh green - healthy
    'warning': '#FF8C42',      # Soft orange - attention
    'info': '#4ECDC4',         # Turquoise - modern feel
    'dark': '#2C3E50',         # Dark blue - professionalism
    'light': '#F8F9FA',        # Light gray - cleanliness
    'background': '#FFFFFF',   # White - purity
    'card_bg': '#FFF8F0',      # Soft beige - coziness
    'gradient_start': '#FF6B47',
    'gradient_end': '#FFD700'
}

# Custom CSS using the professional restaurant palette
st.markdown(f"""
<style>
    .main > div {{
        padding-top: 1rem;
    }}
    
    /* Custom metric cards */
    .metric-card {{
        background: linear-gradient(135deg, {RESTAURANT_COLORS['gradient_start']} 0%, {RESTAURANT_COLORS['gradient_end']} 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    }}
    
    .metric-card h3 {{
        margin: 0;
        font-size: 2.2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .metric-card p {{
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background: linear-gradient(180deg, {RESTAURANT_COLORS['card_bg']} 0%, {RESTAURANT_COLORS['light']} 100%);
    }}
    
    /* Main headings */
    h1 {{
        color: {RESTAURANT_COLORS['dark']};
        text-align: center;
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(45deg, {RESTAURANT_COLORS['primary']}, {RESTAURANT_COLORS['secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    h2 {{
        color: {RESTAURANT_COLORS['primary']};
        border-bottom: 3px solid {RESTAURANT_COLORS['primary']};
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-weight: 600;
    }}
    
    h3 {{
        color: {RESTAURANT_COLORS['secondary']};
        margin-top: 1.5rem;
        font-weight: 500;
    }}
    
    /* Selectbox styling */
    .stSelectbox > div > div {{
        background-color: {RESTAURANT_COLORS['card_bg']};
        border-radius: 10px;
        border: 2px solid {RESTAURANT_COLORS['accent']};
    }}
    
    .stMultiSelect > div > div {{
        background-color: {RESTAURANT_COLORS['card_bg']};
        border-radius: 10px;
        border: 2px solid {RESTAURANT_COLORS['info']};
    }}
    
    /* Info cards */
    .info-card {{
        background: {RESTAURANT_COLORS['card_bg']};
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid {RESTAURANT_COLORS['primary']};
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        color: {RESTAURANT_COLORS['dark']};
    }}
    
    .info-card h4 {{
        color: {RESTAURANT_COLORS['dark']};
        margin: 0 0 0.5rem 0;
    }}
    
    .info-card p {{
        color: {RESTAURANT_COLORS['dark']};
        margin: 0;
    }}
    
    /* Streamlit metrics */
    .stMetric {{
        background: linear-gradient(135deg, {RESTAURANT_COLORS['info']} 0%, {RESTAURANT_COLORS['success']} 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }}
    
    .stMetric > div {{
        color: white !important;
    }}
    
    .stMetric label {{
        color: white !important;
        font-weight: bold;
    }}
    
    /* Dividers */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, {RESTAURANT_COLORS['primary']}, {RESTAURANT_COLORS['accent']}, {RESTAURANT_COLORS['primary']});
        margin: 2rem 0;
    }}
</style>
""", unsafe_allow_html=True)

# Connects to MongoDB
@st.cache_resource
def connect_mongo(uri, db_name):
    client = MongoClient(uri)
    db = client[db_name]
    return db

# Converts ObjectId to string and handles nested types
def process_record(record):
    for key, value in record.items():
        if isinstance(value, ObjectId):
            record[key] = str(value)
        elif isinstance(value, dict):
            record[key] = process_record(value)
        elif isinstance(value, list):
            record[key] = [process_record(item) if isinstance(item, dict) else item for item in value]
    return record

# Fetches data from a collection
@st.cache_data(ttl=600)
def fetch_data_from_mongo(_db, collection_name):
    collection = _db[collection_name]
    data = list(collection.find({}))
    processed_data = [process_record(record) for record in data]
    return pd.DataFrame(processed_data)

# Builds custom metric cards
def create_metric_card(title, value, icon):
    return f"""
    <div class="metric-card">
        <h3>{icon} {value}</h3>
        <p>{title}</p>
    </div>
    """

# Builds styled charts with a consistent palette
def create_styled_chart(fig, title, height=500):
    fig.update_layout(
        title={
            'text': f"<b>{title}</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': RESTAURANT_COLORS['dark']}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': RESTAURANT_COLORS['dark'], 'family': "Arial"},
        margin=dict(l=20, r=20, t=60, b=20),
        height=height,
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.85)",
            font_size=14,
            font_family="Arial",
            font_color="white",
            bordercolor="white"
        ),
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    return fig

# Chart colors based on the professional palette
CHART_COLORS = [
    RESTAURANT_COLORS['primary'],
    RESTAURANT_COLORS['secondary'],
    RESTAURANT_COLORS['accent'],
    RESTAURANT_COLORS['success'],
    RESTAURANT_COLORS['info'],
    RESTAURANT_COLORS['warning'],
    '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'
]

# MongoDB connection URI
uri = st.secrets["MONGODB_URI"]
db_name = "restaurante_reviews_db"

try:
    db = connect_mongo(uri, db_name)
    st.success("Successfully connected to MongoDB!")
except Exception as e:
    st.error(f"Error connecting to MongoDB: {e}")
    st.stop()

# Load all data from the collections
@st.cache_data(ttl=600)
def load_all_data(_db):
    data = {}
    collections = ["avaliacoes", "cardapios", "mensagens", "notificacoes", "pedidos", "pratos", "relatorios", "restaurantes", "usuarios"]
    for col_name in collections:
        data[col_name] = fetch_data_from_mongo(_db, col_name)
    return data

all_data = load_all_data(db)

# --- SIDEBAR WITH SMART FILTERS ---
st.sidebar.markdown("## Smart Filters")

# Initialize the DataFrames
df_pedidos = all_data.get('pedidos', pd.DataFrame()).copy()
df_restaurantes = all_data.get('restaurantes', pd.DataFrame()).copy()

# Category filter (NEW)
if not df_restaurantes.empty and 'categorias' in df_restaurantes.columns:
    # Extract all unique categories
    all_categories = []
    for categorias in df_restaurantes['categorias'].dropna():
        if isinstance(categorias, list):
            all_categories.extend(categorias)
        elif isinstance(categorias, str):
            all_categories.append(categorias)

    unique_categories = sorted(list(set(all_categories)))

    if unique_categories:
        selected_categories = st.sidebar.multiselect(
            "Restaurant Categories",
            unique_categories,
            default=[],
            help="Select the restaurant categories to filter by"
        )

        # Apply category filter
        if selected_categories:
            filtered_restaurant_ids = []
            for idx, row in df_restaurantes.iterrows():
                if isinstance(row['categorias'], list):
                    if any(cat in selected_categories for cat in row['categorias']):
                        filtered_restaurant_ids.append(row['_id'])
                elif isinstance(row['categorias'], str):
                    if row['categorias'] in selected_categories:
                        filtered_restaurant_ids.append(row['_id'])

            if not df_pedidos.empty and filtered_restaurant_ids:
                df_pedidos = df_pedidos[df_pedidos['restaurante_id'].isin(filtered_restaurant_ids)]

# Date range filter
if not df_pedidos.empty and 'data_hora_pedido' in df_pedidos.columns:
    df_pedidos['data_hora_pedido'] = pd.to_datetime(df_pedidos['data_hora_pedido'])

    min_date = df_pedidos['data_hora_pedido'].min().date()
    max_date = df_pedidos['data_hora_pedido'].max().date()

    date_range = st.sidebar.date_input(
        "Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        df_pedidos = df_pedidos[
            (df_pedidos['data_hora_pedido'].dt.date >= start_date) &
            (df_pedidos['data_hora_pedido'].dt.date <= end_date)
        ]

# Restaurant filter
if not df_restaurantes.empty:
    restaurantes_list = ['All'] + sorted(df_restaurantes['nome'].unique().tolist())
    selected_restaurants = st.sidebar.multiselect(
        "Restaurants",
        restaurantes_list,
        default=['All']
    )

    if 'All' not in selected_restaurants and selected_restaurants:
        if not df_pedidos.empty:
            restaurant_ids = df_restaurantes[df_restaurantes['nome'].isin(selected_restaurants)]['_id'].tolist()
            df_pedidos = df_pedidos[df_pedidos['restaurante_id'].isin(restaurant_ids)]

# Order status filter
if not df_pedidos.empty:
    status_list = ['All'] + df_pedidos['status_pedido'].unique().tolist()
    selected_status = st.sidebar.multiselect(
        "Order Status",
        status_list,
        default=['All']
    )

    if 'All' not in selected_status and selected_status:
        df_pedidos = df_pedidos[df_pedidos['status_pedido'].isin(selected_status)]

# --- MAIN DASHBOARD ---
st.markdown("# Restaurant Analytics Dashboard")
st.markdown("### Complete, Smart Analysis of Restaurant Data")
st.markdown("---")

# --- KEY METRICS IN CUSTOM CARDS ---
if not df_pedidos.empty:
    # Compute metrics
    total_pedidos = len(df_pedidos)
    valor_total = df_pedidos['valor_total'].sum()
    pedidos_entregues = df_pedidos[df_pedidos['status_pedido'] == 'entregue'].shape[0]
    taxa_sucesso = (pedidos_entregues / total_pedidos * 100) if total_pedidos > 0 else 0
    ticket_medio = valor_total / total_pedidos if total_pedidos > 0 else 0

    # 4-column layout for metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(create_metric_card("Total Orders", f"{total_pedidos:,}", ""), unsafe_allow_html=True)

    with col2:
        st.markdown(create_metric_card("Total Revenue", f"R$ {valor_total:,.2f}", ""), unsafe_allow_html=True)

    with col3:
        st.markdown(create_metric_card("Success Rate", f"{taxa_sucesso:.1f}%", ""), unsafe_allow_html=True)

    with col4:
        st.markdown(create_metric_card("Average Ticket", f"R$ {ticket_medio:.2f}", ""), unsafe_allow_html=True)

    st.markdown("---")
else:
    st.warning("No order data found for the selected filters.")

# --- ADVANCED ORDER ANALYSIS ---
if not df_pedidos.empty:
    st.markdown("## Detailed Order Analysis")

    # 2-column layout for charts
    col1, col2 = st.columns(2)

    with col1:
        # Pie chart of order status
        status_counts = df_pedidos['status_pedido'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']

        fig_status = px.pie(
            status_counts,
            names='status',
            values='count',
            title='Order Status Distribution',
            color_discrete_sequence=CHART_COLORS,
            hole=0.4
        )
        fig_status.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        )
        st.plotly_chart(create_styled_chart(fig_status, 'Order Status'), use_container_width=True)

    with col2:
        # Bar chart of orders by day of week
        df_pedidos['dia_semana'] = df_pedidos['data_hora_pedido'].dt.day_name()
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_pt = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        pedidos_dia = df_pedidos['dia_semana'].value_counts().reindex(dias_ordem).reset_index()
        pedidos_dia.columns = ['dia', 'count']
        pedidos_dia['dia_pt'] = dias_pt

        fig_dias = px.bar(
            pedidos_dia,
            x='dia_pt',
            y='count',
            title='Orders by Day of Week',
            labels={'dia_pt': 'Day', 'count': 'Orders'},
            color='count',
            color_continuous_scale=[[0, RESTAURANT_COLORS['info']], [1, RESTAURANT_COLORS['primary']]]
        )
        fig_dias.update_traces(
            hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        )
        st.plotly_chart(create_styled_chart(fig_dias, 'Orders by Day of Week'), use_container_width=True)

    # Time-series chart (full width)
    st.markdown("### Orders Over Time")
    df_pedidos['data'] = df_pedidos['data_hora_pedido'].dt.date
    pedidos_tempo = df_pedidos.groupby('data').agg({
        'valor_total': 'sum',
        '_id': 'count'
    }).reset_index()
    pedidos_tempo.columns = ['data', 'faturamento', 'quantidade']

    fig_tempo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_tempo.add_trace(
        go.Scatter(
            x=pedidos_tempo['data'],
            y=pedidos_tempo['quantidade'],
            name="Number of Orders",
            line=dict(color=RESTAURANT_COLORS['primary'], width=3),
            hovertemplate='<b>Date: %{x}</b><br>Orders: %{y}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        ),
        secondary_y=False
    )
    fig_tempo.add_trace(
        go.Scatter(
            x=pedidos_tempo['data'],
            y=pedidos_tempo['faturamento'],
            name="Revenue (R$)",
            line=dict(color=RESTAURANT_COLORS['success'], width=3),
            hovertemplate='<b>Date: %{x}</b><br>Revenue: R$ %{y:,.2f}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        ),
        secondary_y=True
    )
    fig_tempo.update_xaxes(title_text="Date")
    fig_tempo.update_yaxes(title_text="Number of Orders", secondary_y=False)
    fig_tempo.update_yaxes(title_text="Revenue (R$)", secondary_y=True)
    st.plotly_chart(create_styled_chart(fig_tempo, 'Over Time: Orders vs Revenue', 400), use_container_width=True)
    st.markdown("---")

# --- RESTAURANT ANALYSIS ---
if not df_pedidos.empty:
    st.markdown("## Restaurant Performance")

    if not df_restaurantes.empty:
        df_rest_pedidos = pd.merge(df_pedidos, df_restaurantes[['_id', 'nome', 'categorias']],
                                 left_on='restaurante_id', right_on='_id', how='left')

        # 2-column layout
        col1, col2 = st.columns(2)

        with col1:
            # Top restaurants by revenue
            top_rest_faturamento = df_rest_pedidos.groupby('nome')['valor_total'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_top_rest = px.bar(
                top_rest_faturamento,
                x='valor_total',
                y='nome',
                orientation='h',
                title='Top 10 Restaurants by Revenue',
                labels={'valor_total': 'Revenue (R$)', 'nome': 'Restaurant'},
                color='valor_total',
                color_continuous_scale=[[0, RESTAURANT_COLORS['accent']], [1, RESTAURANT_COLORS['primary']]]
            )
            fig_top_rest.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_top_rest.update_traces(
                hovertemplate='<b>%{y}</b><br>Revenue: R$ %{x:,.2f}<extra></extra>',
                hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
            )
            st.plotly_chart(create_styled_chart(fig_top_rest, 'Top Restaurants - Revenue'), use_container_width=True)

        with col2:
            # Revenue by category
            if 'categorias' in df_rest_pedidos.columns and not df_rest_pedidos['categorias'].isnull().all():
                df_exploded = df_rest_pedidos.explode('categorias')
                cozinha_faturamento = df_exploded.groupby('categorias')['valor_total'].sum().reset_index()

                fig_cozinha = px.pie(
                    cozinha_faturamento,
                    names='categorias',
                    values='valor_total',
                    title='Revenue by Cuisine Type',
                    color_discrete_sequence=CHART_COLORS
                )
                fig_cozinha.update_traces(
                    hovertemplate='<b>%{label}</b><br>Revenue: R$ %{value:,.2f}<br>Share: %{percent}<extra></extra>',
                    hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
                )
                st.plotly_chart(create_styled_chart(fig_cozinha, 'Cuisine Types'), use_container_width=True)
            else:
                st.info("Column 'categorias' is unavailable or has no data to analyze.")
    else:
        st.warning("No restaurant data found for performance analysis.")

# --- RATINGS ANALYSIS ---
st.markdown("---")
st.markdown("## Ratings and Satisfaction Analysis")
df_avaliacoes = all_data.get('avaliacoes', pd.DataFrame()).copy()

if not df_avaliacoes.empty:
    df_avaliacoes['data_avaliacao'] = pd.to_datetime(df_avaliacoes['data_avaliacao'])

    # Rating metrics in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        nota_media = df_avaliacoes['nota'].mean()
        st.metric(label="Overall Average Rating", value=f"{nota_media:.2f}")

    with col2:
        total_avaliacoes = len(df_avaliacoes)
        st.metric(label="Total Ratings", value=f"{total_avaliacoes:,}")

    with col3:
        avaliacoes_positivas = df_avaliacoes[df_avaliacoes['nota'] >= 4].shape[0]
        taxa_satisfacao = (avaliacoes_positivas / total_avaliacoes * 100) if total_avaliacoes > 0 else 0
        st.metric(label="Satisfaction Rate", value=f"{taxa_satisfacao:.1f}%")

    # Rating charts in 2 columns
    col1, col2 = st.columns(2)

    with col1:
        # Rating histogram
        fig_notas = px.histogram(
            df_avaliacoes,
            x='nota',
            nbins=5,
            title='Rating Distribution',
            labels={'nota': 'Rating'},
            color_discrete_sequence=[RESTAURANT_COLORS['primary']]
        )
        fig_notas.update_traces(
            marker_line_width=2,
            marker_line_color="white",
            hovertemplate='<b>Rating: %{x}</b><br>Count: %{y}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        )
        st.plotly_chart(create_styled_chart(fig_notas, 'Rating Distribution'), use_container_width=True)

    with col2:
        # Ratings over time
        df_avaliacoes['mes_ano'] = df_avaliacoes['data_avaliacao'].dt.to_period('M').astype(str)
        avaliacoes_tempo = df_avaliacoes.groupby('mes_ano')['nota'].mean().reset_index()

        fig_aval_tempo = px.line(
            avaliacoes_tempo,
            x='mes_ano',
            y='nota',
            title='Average Rating Over Time',
            labels={'mes_ano': 'Month', 'nota': 'Average Rating'},
            markers=True,
            line_shape='spline'
        )
        fig_aval_tempo.update_traces(
            line=dict(color=RESTAURANT_COLORS['success'], width=4),
            marker=dict(size=8, color=RESTAURANT_COLORS['success']),
            hovertemplate='<b>Period: %{x}</b><br>Average Rating: %{y:.2f}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        )
        st.plotly_chart(create_styled_chart(fig_aval_tempo, 'Ratings Over Time'), use_container_width=True)
else:
    st.warning("No rating data found.")

# --- DISH ANALYSIS ---
st.markdown("---")
st.markdown("## Menu and Dish Analysis")
df_pratos = all_data.get('pratos', pd.DataFrame()).copy()

if not df_pratos.empty:
    # 2-column layout for dish analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution
        fig_precos = px.histogram(
            df_pratos, 
            x='preco', 
            nbins=20,
            title='Dish Price Distribution',
            labels={'preco': 'Price (R$)'},
            color_discrete_sequence=['#E3B778'] 
        )
        fig_precos.update_traces(
            hovertemplate='<b>Price Range: R$ %{x:.2f}</b><br>Number of dishes: %{y}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        )
        st.plotly_chart(create_styled_chart(fig_precos, 'Dish Price Distribution'), use_container_width=True)
    
    with col2:
        # Top most expensive dishes
        top_pratos_caros = df_pratos.nlargest(10, 'preco')
        fig_caros = px.bar(
            top_pratos_caros, 
            x='preco', 
            y='nome',
            orientation='h', 
            title='Top 10 Most Expensive Dishes',
            labels={'preco': 'Price (R$)', 'nome': 'Dish'},
            color='preco', 
            color_continuous_scale=[[0, RESTAURANT_COLORS['warning']], [1, RESTAURANT_COLORS['primary']]]
        )
        fig_caros.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_caros.update_traces(
            hovertemplate='<b>%{y}</b><br>Price: R$ %{x:.2f}<extra></extra>',
            hoverlabel=dict(bgcolor="rgba(0,0,0,0.85)", font_color="white", font_size=14, bordercolor="white")
        )
        st.plotly_chart(create_styled_chart(fig_caros, 'Most Expensive Dishes'), use_container_width=True)
else:
    st.warning("No dish data found.")

# --- INFO FOOTER ---
st.markdown("---")
st.markdown("### System Information")

# 3-column layout for system information
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <h4>Refresh</h4>
        <p>Data refreshed every 10 minutes</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h4>Data Source</h4>
        <p>MongoDB - Real-time connection</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <h4>Dashboard</h4>
        <p>Complete, interactive analysis</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-style: italic; margin-top: 2rem;">
    Dashboard built for smart analysis of restaurant data<br>
</div>
""", unsafe_allow_html=True)