# Libraries

from haversine import haversine
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title= "Visão Restaurantes", page_icon="🍴", layout= "wide")
# ---------------------------------------------------------------
# Funções
# ---------------------------------------------------------------
def distance(df1, fig):
  if fig == False:
    cols = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]
    df1["distance"] = (df1.loc[:, cols]
                          .apply(lambda x:
                          haversine ((x["Restaurant_latitude"], x["Restaurant_longitude"]),
                          (x["Delivery_location_latitude"], 
                          x["Delivery_location_longitude"])), axis = 1))
    mean_distance = np.round(df1["distance"].mean(),2)
    return mean_distance 
  else:
    cols = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]
    df1["distance"] = (df1.loc[:, cols]
                        .apply(lambda x:
                        haversine ((x["Restaurant_latitude"], x["Restaurant_longitude"]),
                        (x["Delivery_location_latitude"], 
                        x["Delivery_location_longitude"])), axis = 1))
    distance = df1.loc[:, ["City", "distance"]].groupby("City").mean().reset_index()   
    # gráfico
    fig = go.Figure(data=[go.Pie(labels = distance["City"], values = distance["distance"], pull = [0, 0.1, 0])])
    return fig 
# -------------------------------------------------------------------
def mean_std_time_delivery(df1, festival, op):
  '''Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
    Parâmetros
    Input: 
    df: Dataframe com os dados necessários para o cálculo
    op: Tipo de operação que precisa ser calculada
      mean_time: Calcula o tempo médio do tempo
      std_time: Calcula o desvio padrão médio do tempo
    festival: requisição se tem festival ou não
      Yes: tem festival
      No: sem festival
    Output:
    df com 2 colunas e 1 linha'''
  df_distanc = (df1.loc[:, ["Time_taken(min)", "Festival"]]
                  .groupby(["Festival"])
                  .agg({"Time_taken(min)": ["mean", "std"]})
                  .round(2))
  df_distanc.columns = ["mean_time", "std_time"]
  df_distanc = df_distanc.reset_index()
  df_aux = df_distanc.loc[df_distanc["Festival"] == festival, op]
  return df_aux
# -------------------------------------------------------------------
def mean_std_time_graph(df1):
  df_distanc = (df1.loc[:, ["City", "Time_taken(min)"]]
                  .groupby("City")
                  .agg({"Time_taken(min)": ["mean", "std"]})
                  .round(2))
  df_distanc.columns = ["mean_time", "std_time"]
  df_distanc = df_distanc.reset_index()
  # gráfico
  fig = go. Figure()
  fig.add_trace(go.Bar(name = "Control",
                      x= df_distanc["City"],
                      y = df_distanc["mean_time"],
                      error_y = dict(type = "data", array = df_distanc["std_time"])))
  fig.update_layout(barmode = "group")
  return fig
# ------------------------------------------------------------------
def mean_std_time_on_traffic(df1):
  df_distanc = (df1.loc[:, ["City", "Time_taken(min)", "Road_traffic_density"]]
                      .groupby(["City", "Road_traffic_density"])
                      .agg({"Time_taken(min)": ["mean", "std"]})
                      .round(2))
  df_distanc.columns = ["mean_time", "std_time"]
  df_distanc = df_distanc.reset_index()
  fig = px.sunburst(df_distanc, path=["City", "Road_traffic_density"], values = "mean_time",
    color = "std_time", color_continuous_scale = "RdBu",
    color_continuous_midpoint=np.average(df_distanc["std_time"]))
  return fig
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
# ---------------------------- 
# import dataset
# ----------------------------
#import dataset
df = pd.read_csv("./dataset/train.csv")
df1 = df.copy()
# Limpando o dataset
df1 = clean_code(df)
# ==================================
# Barra lateral
# ===================================
st.header("Marketplace - Visão restaurantes")
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
tab1, tab2, tab3 = st.tabs (["Visão Gerencial", "-", "-"])
with tab1:
  with st.container():
    st.title ("Overall metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
      delivery_unique = df["Delivery_person_ID"].nunique()
      col1.metric('Entregadores únicos', delivery_unique)
    with col2:
      mean_distance = distance(df1, fig = False)
      col2.metric('Distancia média das entregas', mean_distance)
    with col3:
      df_aux = mean_std_time_delivery(df1, "Yes", "mean_time")
      col3.metric("Tempo médio de entrega com Festival", df_aux)
    with col4:
      df_aux = mean_std_time_delivery(df1, "Yes", "std_time")
      col4.metric("Desvio padrão das entregas com Festival", df_aux)
    with col5:
      df_aux = mean_std_time_delivery(df1, "No", "mean_time")
      col5.metric("Tempo médio de entrega sem Festival", df_aux)
    with col6:
      df_aux = mean_std_time_delivery(df1, "No", "std_time")
      col6.metric("Desvio padrão das entregas sem Festival", df_aux)

    with st.container():
      st.markdown("""---""")
      col1, col2 = st.columns(2)
      with col1:
        fig = mean_std_time_graph(df1)
        st.plotly_chart(fig, use_container_width= True)

      with col2:
        st.markdown("""---""")
        df_distanc = (df1.loc[:, ["City", "Time_taken(min)", "Type_of_order"]]
                        .groupby(["City", "Type_of_order"])
                        .agg({"Time_taken(min)": ["mean", "std"]})
                        .round(2))
        df_distanc.columns = ["mean_time", "std_time"]
        df_distanc= df_distanc.reset_index()
        st.dataframe(df_distanc)

    with st.container():
      st.markdown("""---""")
      st.title("Distribuição do tempo")
      col1, col2 = st.columns (2)
      with col1:
            fig = distance(df1, fig = True)
            st.plotly_chart(fig, use_container_width=True)
      with col2:
        fig = mean_std_time_on_traffic(df1)
        st.plotly_chart(fig, use_container_width= True)


