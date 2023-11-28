# Libraries

from haversine import haversine
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title= "Visão Empresa", page_icon="📈", layout= "wide")
# ---------------------------------------------------------------
# Funções
# ---------------------------------------------------------------
def order_metric(df1):  
  cols = ["ID", "Order_Date"]
  df_aux = (df1.loc[:, cols]
            .groupby(["Order_Date"])
            .count().reset_index()
            .sort_values("Order_Date", ascending = False))
  # construindo o gráfico
  fig = px.bar(df_aux, x = "Order_Date", y = "ID")
  return fig
#------------------------------------------------------------------
def Traffic_order_share(df1):        
  linhas = df["Road_traffic_density"] != "NaN "
  cols = ["ID", "Road_traffic_density"]
  df_aux = (df1.loc[linhas, cols]
            .groupby(["Road_traffic_density"])
            .count()
            .reset_index())
  df_aux["traffic_percent"] = df_aux["ID"]/(df_aux["ID"].sum())
  # criando o gráfico de pizza
  fig = px.pie(df_aux, names = "Road_traffic_density", values = "traffic_percent")
  return fig
#--------------------------------------------------------------------
def Traffic_order_city(df1):
  cols = ["ID", "City", "Road_traffic_density"]
  df_aux = (df1.loc[:, cols]
              .groupby(["City", "Road_traffic_density"])
              .count()
              .reset_index())
  # criando o gráfico
  fig = px.scatter(df_aux, x = "City", y = "Road_traffic_density", size = "ID")
  return fig
# -------------------------------------------------------------------
def Order_by_week(df1):
  df1["weeks_of_year"] = df1["Order_Date"].dt.strftime("%U")
  cols = ["ID", "weeks_of_year"]
  df_aux = (df1.loc[:, cols]
              .groupby(["weeks_of_year"])
              .count()
              .reset_index())
  # criando o gráfico
  fig = px.line(df_aux, x = "weeks_of_year", y = "ID")
  return fig
# -------------------------------------------------------------------
def order_share_by_week(df1):
  df_aux01 = (df1.loc[:, ["ID", "weeks_of_year"]]
              .groupby(["weeks_of_year"])
              .count()
              .reset_index())
  df_aux02 = (df1.loc[:, ["Delivery_person_ID", "weeks_of_year"]]
              .groupby(["weeks_of_year"])
              .nunique()
              .reset_index())
  df_aux = pd.merge(df_aux01, df_aux02, how = "inner")
  df_aux["order_person"] = (df_aux["ID"] / df_aux["Delivery_person_ID"]).round(2)
  #criando o gráfico
  fig = px.line(df_aux, x = "weeks_of_year", y = "order_person")
  return fig
# ------------------------------------------------------------------
def country_maps(df1):
  linhas = (df1["City"] != "NaN ") & (df1["Road_traffic_density"] != "NaN ")
  cols = ["City", "Road_traffic_density", "Delivery_location_latitude", "Delivery_location_longitude"]
  df_aux = (df1.loc[linhas, cols]
              .groupby(["City","Road_traffic_density"])
              .median()
              .reset_index())
  # exibindo o mapa
  map = folium.Map()
  #colocando os pinos
  for index, location_info in df_aux.iterrows():
    folium.Marker([location_info["Delivery_location_latitude"],
    location_info["Delivery_location_longitude"]],
    popup = location_info[["City","Road_traffic_density"]]).add_to(map)
  folium_static(map, width = 1024, height = 600)
# -------------------------------------------------------------------
def clean_code(df1):
  '''Esta função tem a responsabilidade de limpar o dataframe
  
  Tipos de limpeza:
  1. Remoção dos dados NaN
  2. Mudança do tipo da coluna de dados
  3. Remoção dos espaços das variáveis de texto
  4. Formatação da coluna de datas
  5. limpeza da coluna de tempo (remoção do texto da variável numérica)
  
  Input: Dataframe
  Output: Dataframe'''

  # 1. Convertendo a coluna Age de texto para número
  linhas_sel = df1.loc[:, "Delivery_person_Age"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)

  # 2. Convertendo a coluna Ratings de texto para número decimal (float)
  linhas_sel_rate = df1["Delivery_person_Ratings"] != "NaN "
  df1 = df1.loc[linhas_sel_rate, :].copy()
  df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)

  # 3. Limpando os NaN
  linhas_sel = df1["Road_traffic_density"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  linhas_sel = df1["City"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  linhas_sel = df1.loc[:, "City"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  linhas_sel = df1["Festival"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()

  # 4. Convertendo multiple_deliveries de texto para número inteiro (int)
  linhas_sel = df1.loc[:, "multiple_deliveries"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)

  # 5. Convertendo a coluna order_date de texto para data
  df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format = "%d-%m-%Y")

  # 6. Removendo os espaços dentro de strings/texto/object
  cols_strip = ["ID", "Delivery_person_ID", "Road_traffic_density", "Type_of_order", "Type_of_vehicle", "City", "Festival"]
  for i in cols_strip:
    df1.loc[:, i] = df1.loc[:, i].str.strip()

  # 7 Limpando a coluna de time taken
  df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(lambda x: x.split( "(min) ")[1])
  df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)

  return df1

# ----------------------------------- Inicio da estrutura lógica do código
# ------------------------------------------------------------------------
#import dataset
# ------------------------------------------------------------------------
df = pd.read_csv("./dataset/train.csv")
# ------------------------------------------------------------------------
# Limpando os dados
# ------------------------------------------------------------------------
df1 = clean_code(df)

# ==================================
# Barra lateral
# ===================================
st.header("Marketplace - Visão cliente")
image_path = "./logo.png"
image = Image.open(image_path )
st.sidebar.image(image, width = 120)
st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fatest delivery in town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Selecione uma data limite")
date_slider = st.sidebar.slider(
  "Até qual valor?", 
  value = pd.datetime(2022, 4, 13),
  min_value = pd.datetime(2022,2,11),
  max_value = pd.datetime(2022, 4, 6),
  format = "DD-MM-YYYY")

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
  "Quais as condições do transito?",
  ["Low", "Medium", "High", "Jam"],
  default = ["Low", "Medium", "High", "Jam"])
st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by Christiano Peres - Comunidade DS")

# Filtro de data
linhas_selecionadas = df1["Order_Date"] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1["Road_traffic_density"].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==================================
# Layout no streamlit
# ===================================
tab1, tab2, tab3 = st.tabs (["Visão Gerencial", "Visão tática", "Visão geográfica"])

with tab1: 
      with st.container():
        # Order metric
        st.markdown("# Orders by Day")
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
        
      with st.container():
        col1, col2 = st.columns(2)
        with col1: 
            fig = Traffic_order_share(df1)
            st.header("Traffic Order Share")
            st.plotly_chart(fig, use_container_width=True)  
              
        with col2: 
          st.header("Traffic Order City")
          fig = Traffic_order_city(df1)
          st.plotly_chart(fig, use_container_width=True)

with tab2:
  with st.container():
    st.markdown("# Order by Week")
    fig = Order_by_week(df1)
    st.plotly_chart(fig, use_container_width=True)

  with st.container():
    st.markdown("# Order Share by Week")
    fig = order_share_by_week(df1)
    st.plotly_chart(fig, use_container_width=True)
    
with tab3: 
    st.markdown("# Country Maps")
    country_maps(df1)
   
      

