import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def read_jogos(dia):
    # Convert date to string format for the URL
    dia_str = dia.strftime('%Y-%m-%d')
    base_url = "https://raw.githubusercontent.com/RedLegacy227/df_jogos_do_dia/refs/heads/main/"
    file_name = f"df_jogos_do_dia_{dia_str}.csv"
    file_url = base_url + file_name
    
    try:
        jogos_do_dia = pd.read_csv(file_url)
        jogos_do_dia = drop_reset_index(jogos_do_dia)

    except Exception as e:
        st.error(f"Error loading data: {e}")
        jogos_do_dia = pd.DataFrame()  # Return empty DataFrame if error

    return jogos_do_dia

# Função genérica para selecionar as colunas
def select_columns(df_jogos_do_dia):
    selected_columns = [
        'League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'FT_Odd_Ov25', 
        'Prob_Ov15_FT', 'Prob_Un15_FT', 'Prob_BTTS_Y_FT', 'Prob_BTTS_N_FT', 'Media_RPS_OvUn_Home', 
        'CV_RPS_OvUn_Home', 'Media_RPS_OvUn_Away', 'CV_RPS_OvUn_Away', 'Media_RPS_BTTS_Home', 
        'CV_RPS_BTTS_Home', 'Media_RPS_BTTS_Away', 'CV_RPS_BTTS_Away', 'Media_SG_Home', 'CV_SG_Home', 
        'Media_SG_Away', 'CV_SG_Away', 'Media_GM_Home_1P', 'CV_GM_Home_1P', 'Media_GM_Away_1P', 
        'CV_GM_Away_1P', 'Media_GS_Home_1P', 'CV_GS_Home_1P', 'Media_GS_Away_1P', 'CV_GS_Away_1P', 
        'Media_GM_Home', 'CV_GM_Home', 'Media_GM_Away', 'CV_GM_Away', 'Media_GS_Home', 'CV_GS_Home', 
        'Media_GS_Away', 'CV_GS_Away', 'Media_CGM_Home_01', 'CV_CGM_Home_01', 'Media_CGM_Away_01', 
        'CV_CGM_Away_01', 'Media_CGS_Home_01', 'CV_CGS_Home_01', 'Media_CGS_Away_01', 'CV_CGS_Away_01', 
        'Media_CGM_Home_02', 'CV_CGM_Home_02', 'Media_CGM_Away_02', 'CV_CGM_Away_02', 'Media_CGS_Home_02', 
        'CV_CGS_Home_02', 'Media_CGS_Away_02', 'CV_CGS_Away_02', 'Med_Prim_Golo_Marcado_Home', 
        'Med_Prim_Golo_Sofrido_Home', 'Med_Prim_Golo_Marcado_Away', 'Med_Prim_Golo_Sofrido_Away', 
        'Porc_Marcou_Primeiro_Golo_Home', 'Porc_Marcou_Primeiro_Golo_Away', 'Porc_Sofreu_Primeiro_Golo_Home', 
        'Porc_Sofreu_Primeiro_Golo_Away', 'Porc_Marcou_Primeiro_Golo_Home_1P', 
        'Porc_Marcou_Primeiro_Golo_Away_1P', 'Porc_Sofreu_Primeiro_Golo_Home_1P', 
        'Porc_Sofreu_Primeiro_Golo_Away_1P', 'Porc_BTTS_Y_Home', 'Porc_BTTS_Y_Away', 'Porc_Over05HT_Home', 
        'Porc_Over05HT_Away', 'Porc_Under05HT_Home', 'Porc_Under05HT_Away', 'Porc_Over15HT_Home', 
        'Porc_Over15HT_Away', 'Porc_Under15HT_Home', 'Porc_Under15HT_Away', 'Porc_Over05FT_Home', 
        'Porc_Over05FT_Away', 'Porc_Under05FT_Home', 'Porc_Under05FT_Away', 'Porc_Over15FT_Home', 
        'Porc_Over15FT_Away', 'Porc_Under15FT_Home', 'Porc_Under15FT_Away', 'Porc_Over25FT_Home', 
        'Porc_Over25FT_Away', 'Porc_Under25FT_Home', 'Porc_Under25FT_Away', 'Porc_Score_Min_1G_Home', 
        'Porc_Score_Min_1G_Away', 'Porc_Took_Min_1G_Home', 'Porc_Took_Min_1G_Away',
    ]
    return df_jogos_do_dia.loc[:, selected_columns]

# Função para o filtro Over 1.5 FT
def filter_over_15_ft(df_jogos_do_dia):
    df = select_columns(df_jogos_do_dia)
    over_15_ft = df[
        (df["Porc_Over15FT_Home"] > 55) &
        (df["Porc_Over15FT_Away"] > 55) &
        (df["Porc_BTTS_Y_Home"] > 55) &
        (df["Porc_BTTS_Y_Away"] > 55) &
        (df['Media_GM_Home'] > 1) &
        (df['CV_GM_Home'] < 1) &
        (df['Media_GM_Away'] > 1) &
        (df['CV_GM_Away'] < 1) &
        (df['Media_GS_Home'] > 1) &
        (df['CV_GS_Home'] < 1) &
        (df['Media_GS_Away'] > 1) &
        (df['CV_GS_Away'] < 1)
    ]
    over_15_ft = over_15_ft.sort_values(by='Time', ascending=True)
    over_15_ft = drop_reset_index(over_15_ft)
    return over_15_ft

def show_overs_unders_ft():
    st.title("Fluffy Chips DashBoard")
    

    dia = st.date_input("Data da Analise", date.today())

    Jogos_do_Dia = read_jogos(dia)
    st.dataframe(Jogos_do_Dia)
    if not Jogos_do_Dia.empty:
        st.write("")
        st.header("Over 0,5 FT")
        st.write("")
        st.write("")
        st.write("Em Construção")
        st.write("")
        st.write("")
        st.header("Under 0,5 FT")
        st.write("")
        st.write("")
        st.write("Em Construção")
        st.write("")
        st.write("")
        # Filtros Over 1.5 FT
        st.header("Over 1,5 FT")
        over_15_ft = filter_over_15_ft(Jogos_do_Dia)
        if over_15_ft.empty:
            st.warning("No matches found for Over 1,5 FT filter.")
        else:
            st.dataframe(over_15_ft)
        st.header("Over 2,5 FT")
        st.write("")
        st.write("")
        st.write("Em Construção")
        st.write("")
        st.write("")
        st.header("Under 2,5 FT")
        st.write("")
        st.write("")
        st.write("Em Construção")
        st.write("")
        st.write("")