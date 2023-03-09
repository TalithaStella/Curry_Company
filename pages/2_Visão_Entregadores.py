# =====================
# BIBLIOTECAS NECESSÁRIAS
# =====================

import pandas as pd
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go
import folium
from haversine import haversine
from PIL import Image #pip install Image (não PIL)
from streamlit_folium import folium_static


st.set_page_config( page_title='Visão Entregadores', layout='wide')
# ====================================================================================
# FUNÇÕES
# ====================================================================================


# --------------------------------------------------------
# Funções de limpeza
# --------------------------------------------------------

def clean_code(df1):
    """
    Função de limpeza: 
      - Remoção de espaços
      - Remoção de NaN
      - Alteração dos tipos de dados
      - Alteração da data
      - Remoção de STR da coluna TEMPO

      Input: Dataframe
      Output: Dataframe

    """

      # Remoção dos espaços
    df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()


      # Remoção de NaN
    trash1 = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[trash1, :].copy()

    trash2 = (df1['City'] != 'NaN')
    df1 = df1.loc[trash2, :].copy()

    trash3 = (df1['Weatherconditions'] != 'NaN')
    df1 = df1.loc[trash3, :].copy()

    trash4 = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[trash4, :].copy()

    trash04 = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[trash04, :].copy()

    trash5 = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[trash5, :].copy()
    
    
      # Alteração do tipo de dados
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

      # Alteração da data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')


      # Remoção de STR da coluna TEMPO-
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

df = pd.read_csv('train.csv')
df1 = clean_code(df)



# --------------------------------------------------------
# Funções de gráfico
# --------------------------------------------------------

def top_entregadores(df1, asc):

    df2 = df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending = asc ).reset_index()

    aux01 = df2.loc[df2['City'] == 'Metropolitician', :].head(10)
    aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    aux03 = df2.loc[df2['City'] == 'Semi_Urban', :].head(10)

    df3 = pd.concat( [aux01, aux02, aux03] ).reset_index(drop=True)

    return df3


# ===================================================================
# Slidebar no streamlit - TUDO QUE ESTIVER DENTRO DA BARRA PRECISA TER O .sidebar
# =================================================================== 

st.header('Visão Entregadores') # O header fica como se fosse o .markdown ##


# Comando pra trazer imagem
image = Image.open( 'foco.png' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")  # BARRA DE SEPARAÇÃO

st.sidebar.markdown('## Date Filter') # Adicionar a barra de arrastar

date_slider = st.sidebar.slider(
    'Select a date:',
    value=pd.datetime(2022, 4, 13), # ano/mes/dia
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Traffic Condition Filter') # Adicionar filtro multi selecionável

traffic_options = st.sidebar.multiselect(
    'Which traffic condition?', 
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] ) # pode deixar só com 1 parâmetro como padrão


st.sidebar.markdown("""---""") # Rodapé
st.sidebar.markdown("### Powered by Comunidade DS.")
st.sidebar.markdown("###### Talitha Oliveira")


# SETTANDO OS FILTROS

# Filtro de data
datas_sel = df1['Order_Date'] < date_slider
df1 = df1.loc[datas_sel, :]


# Filtro de transito
traff_sel = df1['Road_traffic_density'].isin( traffic_options ) # Isin - esta em <FILTRO CRIADO>
df1 = df1.loc[traff_sel, :]


# ===================================================================
# Layout no streamlit  -- Aqui vai no corpo da página
# ===================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )



with tab1: 
    
    with st.container():
        
        st.subheader ('Overall Metrics')
        
        
        col1, col2, col3, col4 = st.columns( 4, gap= 'large') 
        with col1:

            
            maior_idd = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idd )

        with col2:

            
            menor_idd = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idd )

        with col3:

            maior_vcl = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', maior_vcl )            


        with col4:

            menor_vcl = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', menor_vcl )
            
            
    with st.container():
        
        st.markdown("""---""")
        st.title( 'Avaliações' )
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.markdown(' #### Avaliação média por entregador')
            av_entregador = df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings'	]].groupby('Delivery_person_ID').mean().reset_index()
            
            st.dataframe(av_entregador)
        

        with col2:
            st.markdown('#### Avaliação média por trânsito')
            
            avg_std = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings' : ['mean', 'std']}).reset_index()
            
            
            avg_std.columns = ['Delivery_person_Ratings','delivery_mean', 'delivery_avg']  
            avg_std.reset_index()

            st.dataframe(avg_std)
            
            
            
            st.markdown('#### Avaliação média por clima')
            
            weather_avg_std = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean','std']})
            weather_avg_std.columns = [ 'weather_mean', 'weather_std']
            weather_avg_std.reset_index()

            st.dataframe(weather_avg_std)
            
            
            
    with st.container():
        st.markdown("""---""")
        st.subheader('Velocidade de entrega')
        
 # Iniciando as funções:        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Top entregadores mais rápidos')
            df3 = top_entregadores(df1, asc=True)
          
            st.dataframe(df3)
                         
                
        with col2:
            st.markdown('#### Top entregadores mais lentos')   
            df3 = top_entregadores(df1, asc=False)
            st.dataframe(df3)

                                     
            
       
    
with tab2:
    st.subheader ('_')

        
    
       
    

with tab3:
    st.subheader ('_')
    









