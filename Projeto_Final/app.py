import streamlit as st
import pandas as pd

st.set_option('deprecation.showfileUploaderEncoding', False)

from sklearn.preprocessing import (
    LabelEncoder, KBinsDiscretizer)
from sklearn.neighbors import NearestNeighbors

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href

def main():
    st.title("Gerador de Leads AUTOMATICO!")
    st.image("https://neilpatel.com/wp-content/uploads/2016/01/o-que-sao-leads.jpeg", width=300)

#------------------------------------------------------------------------------------
#                                   Loading data
#------------------------------------------------------------------------------------

    file = st.file_uploader('Escolha a base de dados do mercado tratada(.csv)', type = 'csv')
    if file is not None:
        st.markdown("Carregado com Sucesso!")
        
        mkt = pd.read_csv(file)
        
        st.write(f"O arquivo tem {mkt.shape[0]} linhas e {mkt.shape[1]} colunas")
        st.write(mkt.head())

#------------------------------------------------------------------------------------
#                                     Fitting
#------------------------------------------------------------------------------------
        
        st.write("Estou treinando o modelo agora, isso pode demorar um pouco... :confused:")
        
        mkt.set_index("id", inplace=True)
        
        nn = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(mkt)

# Getting the Leads

        port = st.file_uploader("Quase lá, escolha um portfolio com os ID's (.csv)", type="csv")
        if port is not None:
            distances, indices = nn.kneighbors(port)
            port_leads = pd.DataFrame([mkt.iloc[indices[row,col]] for row in range(indices.shape[0]) for col in range(indices.shape[1])])

            st.write("Sucesso! Aqui está a sua recomendação!")
            port_leads.set_index("id", inplace=True)
            st.write(pot_leads.index)

            st.markdown(get_table_download_link(df_inputado), unsafe_allow_html=True)
    
if __name__ == '__main__':
	main()