import streamlit as st
from PIL import Image

st.set_page_config( # Aqui definimos a configuração da página
    page_title='Home'
)

# image_path = "C:\C.Python\1CDS\Materiais\analise_python\Scripts"
# image = Image.open (image_path + 'foco.png' )
# st.sidebar.image (image, width=120)

image = Image.open( 'foco.png' )
st.sidebar.image( image, width=120 )



st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Festest Delivery in Town')
st.sidebar.markdown("""---""")  

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi constru[ido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes. 
    ### Como utilizar esse Growth Dashboard? 
    - Visão empresa:
        - Visão gerencial: Métricas gerais de comportamento.
        - Visão tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
        
    - Visão entregador:
        -Acompanhamento dos indicadores semaians de crescimento
        
    - Visão Restaurantes: 
        - Indicadores semanais de crescimento dos restaurantes
    
    ### Ask for help
    - Time de Data Science no Discord
        - @talithastella   
    
    """)


