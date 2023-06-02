# =====================
# BIBLIOTECAS NECESSÁRIAS
# =====================

import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
import datetime
from haversine import haversine
from PIL import Image #pip install Image (não PIL)
from streamlit_folium import folium_static


st.set_page_config( page_title='Visão Restaurantes', layout='wide')
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
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y').dt.date


      # Remoção de STR da coluna TEMPO-
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

df = pd.read_csv('train.csv')
df1 = clean_code(df)



# --------------------------------------------------------
# Funções de gráfico
# --------------------------------------------------------

def distancia ( df1, fig):
    if fig == False:
        col_loc = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1 ['distance'] = df1.loc[:, col_loc].apply( lambda x:
                                  haversine(
                                      (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                      (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ) , axis=1)

        avg_distance = round(df1.loc[:, 'distance'].mean(), 2)
        return avg_distance
    
    else:
        col_loc = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1 ['distance'] = df1.loc[:, col_loc].apply( lambda x:
                                  haversine(
                                      (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                      (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ) , axis=1)

       
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig1 = go.Figure(data = [ go.Pie( labels=avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.05, 0])])
        
        return fig1





def avg_stf_time_delivery (df1, fest, op):
    
    """ Função para calcular média e desvio padrão do tempo de entrega durante festivais ou não
        Input: fest = 'Yes' ou 'No'
               op = 'avg' ou 'std'
        Output: Valor (int) da distancia. 
    """

    if fest == 'Yes' and op == 'avg':
        df_aux = round(df1.loc[ df1['Festival'] == 'Yes', 'Time_taken(min)'].mean(), 2)

    elif  fest == 'Yes' and op == 'std':
        df_aux = round(df1.loc[ df1['Festival'] == 'Yes', 'Time_taken(min)'].std(), 2)

    elif fest == 'No' and op == 'avg':
        df_aux = round(df1.loc[ df1['Festival'] == 'No', 'Time_taken(min)'].mean(), 2)

    elif fest == 'No' and op == 'std':
        df_aux = round(df1.loc[ df1['Festival'] == 'No', 'Time_taken(min)'].std(), 2)

    return df_aux

def med_dp_city(df1):

    avg_std_city = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({ 'Time_taken(min)' : ['mean', 'std']} )
    avg_std_city.columns = ['time_mean', 'time_std']
    avg_std_city = avg_std_city.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control', 
                          x= avg_std_city['City'], 
                          y= avg_std_city['time_mean'], 
                          error_y= dict (type = 'data', array=avg_std_city['time_std'] )))
    fig.update_layout(barmode='group')
    
    return fig


def tempo_medio_entrega(df1): 
    avg_std_city_traffic = df1.loc[:,['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std'] }).reset_index()
    avg_std_city_traffic.columns = ['City', 'Traffic', 'Time_mean', 'Time_std']
    avg_std_city_traffic.reset_index()

    fig2 = px.sunburst(avg_std_city_traffic, path=['City', 'Traffic'], values='Time_mean', 
                      color='Time_std', color_continuous_scale='RdBu', 
                      color_continuous_midpoint=np.average( avg_std_city_traffic['Time_std']))

    return fig2

def med_dp_cidade_trafego (df1):

    avg_std_city_traffic = df1.loc[:,['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std'] }).reset_index()
    avg_std_city_traffic.columns = ['City', 'Traffic', 'Time_mean', 'Time_std']
    grf = avg_std_city_traffic.reset_index(drop = True)

    return grf



# ===================================================================
# Slidebar no streamlit - TUDO QUE ESTIVER DENTRO DA BARRA PRECISA TER O .sidebar
# =================================================================== 

st.header('Visão Restaurantes') 



image = Image.open( 'foco.png' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Festest Delivery in Town')
st.sidebar.markdown("""---""")  

st.sidebar.markdown('## Date Filter') 

date_slider = st.sidebar.slider(
    'Select a date:',
    value=datetime.datetime(2022, 4, 13).date(), 
    min_value=datetime.datetime(2022, 2, 11).date(),
    max_value=datetime.datetime(2022, 4, 6).date()
)

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Traffic Condition Filter') 

traffic_options = st.sidebar.multiselect(
    'Which traffic condition?', 
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )


st.sidebar.markdown("""---""") 
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
        
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 ) 
        with col1:
                        
            ent_un = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', ent_un)
            


        with col2:
            avg_distance = distancia(df1, fig=False)
            col2.metric('Distâcia média', avg_distance)
            

                         
        with col3:
                       
            df_aux = avg_stf_time_delivery (df1, 'Yes', 'avg')
            col3.metric('Tempo de entrega médio c/ festival', df_aux)
                   
                         
        with col4:
            df_aux2 = avg_stf_time_delivery (df1, 'Yes', 'std')
            col4.metric('Desvio padrão de entregas c/ festival', df_aux2)           
                         
                
        with col5:
            df_aux3 = avg_stf_time_delivery (df1, 'No', 'avg')
            col5.metric('Tempo de entrega médio s/ festival', df_aux3)             
                         
                
        with col6:
            df_aux4 = avg_stf_time_delivery (df1, 'No', 'std')
            col6.metric('Desvio padrão de entrega médio s/ festival', df_aux4)


            
            
    with st.container():
        st.markdown("""---""")
        
        colu1, colu2 = st.columns(2)
        
        with colu1:
        
            st.markdown('#### Distribuição do tempo por cidade') 
            fig = med_dp_city(df1)
            st.plotly_chart(fig, use_container_width=True)
                 

            
        with colu2:

        
            st.markdown('#### Tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.' )
            grf = med_dp_cidade_trafego (df1)
            


            st.dataframe(grf)
            

                        
            
    with st.container():
        st.markdown("""---""")

        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Distância média por cidade' )
    
            fig1 = distancia(df1, fig=True)          
            st.plotly_chart( fig1, use_container_width=True)
            
                         
        with col2:
            st.markdown('#### Tempo médio por tipo de entrega') 
            
            fig2 = tempo_medio_entrega(df1)
            st.plotly_chart(fig2, use_container_width=True)
            
            
          
    
with tab2:
    st.subheader ('_')

        
    
       
    

with tab3:
    st.subheader ('_')



