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



st.set_page_config( page_title='Visão Empresa', layout='wide')
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


# GRÁFICO BARRAS
def order_metric(df1): 

    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']


    grf1 = px.bar( df_aux, x='order_date', y='qtde_entregas' )

    return grf1


# GRÁFICO DE PIZZA
def traffic_order_share(df1):

    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )

    # gráfico
    grf2 = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )

    return grf2 


# GRÁFICO BOLHAS
def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()


    grf3 = px.scatter( df_aux, x='City', y='Road_traffic_density', size = 'ID', color='City' )

    return grf3


# GRÁFICOS EM LINHAS DE SEMANA - VISÃO TÁTICA
def order_by_week( df1):

    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()


    grf4 = px.line( df_aux, x='week_of_year', y='ID' ) 

    return grf4


# GRÁFICOS EM LINHAS DE SEMANA - VISÃO TÁTICA
def delivery_by_week( df1):

    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()

    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']


    grf5 = px.line( df_aux, x='week_of_year', y='order_by_delivery' )

    return grf5


# GRÁFICO DE MAPA
def country_map(df1):

    data_plot = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby( ['City', 'Road_traffic_density']).median().reset_index()

    map_ = folium.Map( zoom_start=11 )

    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )

    folium_static(map_, width=1024 , height=600 )




# ===================================================================
# Slidebar no streamlit - TUDO QUE ESTIVER DENTRO DA BARRA PRECISA TER O .sidebar
# =================================================================== 

st.header('Marketplace - Visão Cliente') 


# Comando pra trazer imagem
image = Image.open( 'foco.png' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")  

st.sidebar.markdown('## Date Filter') 

date_slider = st.sidebar.slider(
    'Select a date:',
    value=pd.to_datetime(2022, 4, 13), 
    min_value=pd.to_datetime(2022, 2, 11),
    max_value=pd.to_datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Traffic Condition Filter')
traffic_options = st.sidebar.multiselect(
    'Which traffic condition?', 
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] ) 


st.sidebar.markdown("""---""") 
st.sidebar.markdown("### Powered by Comunidade DS.")
st.sidebar.markdown("###### Talitha Oliveira")






datas_sel = df1['Order_Date'] < date_slider
df1 = df1.loc[datas_sel, :]



traff_sel = df1['Road_traffic_density'].isin( traffic_options ) 
df1 = df1.loc[traff_sel, :]





# ===================================================================
# Layout no streamlit  -- Aqui vai no corpo da página
# ===================================================================



tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão geográfica'] )



with tab1: 
    

    with st.container():
        grf1 = order_metric(df1)
        st.markdown('## Order by Day')
        
        st.plotly_chart(grf1, use_container_width=True) 
        

        

    with st.container():
        col1, col2 = st.columns( 2 ) 
        
        with col1:
            grf2 = traffic_order_share(df1)
            st.markdown ('## Traffic Order Share')
            st.plotly_chart(grf2, use_container_width=True)
            

            


        with col2:
            st.markdown ('## Traffic Order City')
            grf3 = traffic_order_city(df1)
                    
            st.plotly_chart(grf3, use_container_width=True)
        
    
       
    
with tab2:
    with st.container():    
        st.markdown('# Order by Week')
        grf4 = order_by_week(df1)
        
        st.plotly_chart(grf4, use_container_width=True)
        
        
    with st.container():
        st.markdown('# Delivery by Weeek')
        grf5 = delivery_by_week( df1)     
        
        st.plotly_chart(grf5, use_container_width=True)
        
    
       
    

with tab3:
    st.markdown('## Location by Traffic:')
    map_ = country_map(df1)
    
    


