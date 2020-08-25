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

#--------------------------------------------------------------
# Loading data
#--------------------------------------------------------------

    file  = st.file_uploader('Escolha a base de dados do mercado (.csv)', type = 'csv')
    if file is not None:
        st.markdown("Carregado com Sucesso!")
        
        mkt = pd.read_csv(file)

        port1 = pd.read_csv("https://codenation-challenges.s3-us-west-1.amazonaws.com/ml-leads/estaticos_portfolio1.csv")
        port2 = pd.read_csv("https://codenation-challenges.s3-us-west-1.amazonaws.com/ml-leads/estaticos_portfolio2.csv")
        port3 = pd.read_csv("https://codenation-challenges.s3-us-west-1.amazonaws.com/ml-leads/estaticos_portfolio3.csv")
        
        st.write(f"O arquivo tem {mkt.shape[0]} linhas e {mkt.shape[1]} colunas")
        st.write(mkt.head())

#--------------------------------------------------------------
# Preprocessing
#--------------------------------------------------------------

        mkt.drop("nm_meso_regiao", axis=1, inplace=True)
    
        X = mkt.copy()

# Bin continuous data into intervals

        X.select_dtypes(include="number")

        est = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='uniform')
        est.fit(X[["dt_situacao", "idade_media_socios"]])
        X[["dt_situacao", "idade_media_socios"]] = est.transform(X[["dt_situacao", "idade_media_socios"]]).astype(int)

# Enconding

        cat_cols = X.select_dtypes(include=object).columns[1:]

        X[cat_cols] = X[cat_cols].apply(lambda col: LabelEncoder().fit_transform(col))

# Preparing the Portifolios

        port1 = port1[["id"]]

        port2.drop("Unnamed: 0", axis=1, inplace=True)
        port3.drop("Unnamed: 0", axis=1, inplace=True)

        port1 = port1.merge(right=X, how="inner", on="id")
        port2 = port2.merge(right=X, how="inner", on="id")
        port3 = port3.merge(right=X, how="inner", on="id")

        ports = pd.concat([port1, port2, port3])
        
        X.set_index('id', inplace=True)
        port1.set_index('id', inplace=True)
        port2.set_index('id', inplace=True)
        port3.set_index('id', inplace=True)

        X = X.drop(index=ports["id"])

#--------------------------------------------------------------
# Fitting
#--------------------------------------------------------------
        
        st.write("Estou treinando o modelo agora, isso pode demorar um pouco...", :confused:)
    
        nn = NearestNeighbors(n_neighbors=1)
        nn.fit(X)

# Getting the Leads

        distances, indices = nn.kneighbors(port1)
        port1_leads = pd.DataFrame([X.iloc[indices[row,col]] for row in range(indices.shape[0]) for col in range(indices.shape[1])])

        distances, indices = nn.kneighbors(port2)
        port2_leads = pd.DataFrame([X.iloc[indices[row,col]] for row in range(indices.shape[0]) for col in range(indices.shape[1])])
        
        distances, indices = nn.kneighbors(port3)
        port3_leads = pd.DataFrame([X.iloc[indices[row,col]] for row in range(indices.shape[0]) for col in range(indices.shape[1])])
       
        
        portfolio_select = st.radio("Selecione o portifolio para visualizar os IDs", ("portfolio1", "portfolio2", "portfolio3"))
        if portfolio_select == "portfolio1":
            st.write(port1_leads.index)
        if portfolio_select == "portfolio2":
            st.write(port2_leads.index)
        if portfolio_select == "portfolio3":
            st.wtite(port3_leads.index)
    
if __name__ == '__main__':
	main()