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

def filter_lay_home(df_jogos_do_dia):
    # Select columns specific to Lay Home
    selected_columns = [
        'League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H','FT_Odd_D','FT_Odd_A','Med_Power_Ranking_Home','CV_pwr_Home',
        'Med_Power_Ranking_Away', 'CV_pwr_Away','Media_RPS_MO_Home','CV_RPS_MO_Home','Media_RPS_MO_Away',
        'CV_RPS_MO_Away','Media_Ptos_Home','CV_Ptos_Home','Media_Ptos_Away', 'CV_Ptos_Away','Media_CGM_Home_01', 
        'CV_CGM_Home_01', 'Media_CGM_Away_01','CV_CGM_Away_01', 'Media_CGS_Home_01','CV_CGS_Home_01', 'Media_CGS_Away_01',
        'CV_CGS_Away_01', 'Media_CGM_Home_02','CV_CGM_Home_02','Media_CGM_Away_02', 'CV_CGM_Away_02', 'Media_CGS_Home_02',
        'CV_CGS_Home_02', 'Media_CGS_Away_02','CV_CGS_Away_02','Media_Prob_Home','CV_Med_Prob_Home', 'Media_Prob_Away', 
        'CV_Med_Prob_Away', 'Med_Prim_Golo_Marcado_Home','Med_Prim_Golo_Sofrido_Home', 'Med_Prim_Golo_Marcado_Away', 
        'Med_Prim_Golo_Sofrido_Away','Porc_Marcou_Primeiro_Golo_Home','Porc_Marcou_Primeiro_Golo_Away', 'Porc_Sofreu_Primeiro_Golo_Home',
        'Porc_Sofreu_Primeiro_Golo_Away', 'Porc_Marcou_Primeiro_Golo_Home_1P','Porc_Marcou_Primeiro_Golo_Away_1P',
        'Porc_Sofreu_Primeiro_Golo_Home_1P', 'Porc_Sofreu_Primeiro_Golo_Away_1P', 'Porc_BTTS_Y_Home','Porc_BTTS_Y_Away',
        'Porc_Home_Win_HT', 'Porc_Away_Win_HT', 'Porc_Home_Win_FT', 'Porc_Away_Win_FT','Porc_Score_Min_1G_Home',
        'Porc_Score_Min_1G_Away', 'Porc_Took_Min_1G_Home', 'Porc_Took_Min_1G_Away',
    ]
    df = df_jogos_do_dia.loc[:, selected_columns]

    # Apply Lay Home filters
    Lay_Home = df[
        #(df['FT_Odd_A'] <= 2.5) & 
        #(df['FT_Odd_H'].between(3, 10)) &
        (df['Med_Power_Ranking_Away'] > df['Med_Power_Ranking_Home'] ) &
        ((df["Med_Power_Ranking_Away"] - df["Med_Power_Ranking_Home"]) > 20) &
        (df['Media_SG_Away'] > df['Media_SG_Home']) & (df['CV_SG_Away'] <= 0.7) 
        (df['Media_CGM_Away_02'] >= 0.9) & (df['CV_CGM_Away_02'] < 0.7)
    ]
    Lay_Home = Lay_Home.sort_values(by='Time', ascending=True)
    Lay_Home = drop_reset_index(Lay_Home)
    return Lay_Home

def filter_lay_away(df_jogos_do_dia):
    # Select columns specific to Lay Away
    selected_columns = [
        'League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H','FT_Odd_D','FT_Odd_A','Med_Power_Ranking_Home','CV_pwr_Home',
        'Med_Power_Ranking_Away', 'CV_pwr_Away','Media_RPS_MO_Home','CV_RPS_MO_Home','Media_RPS_MO_Away',
        'CV_RPS_MO_Away','Media_Ptos_Home','CV_Ptos_Home','Media_Ptos_Away', 'CV_Ptos_Away','Media_CGM_Home_01', 
        'CV_CGM_Home_01', 'Media_CGM_Away_01','CV_CGM_Away_01', 'Media_CGS_Home_01','CV_CGS_Home_01', 'Media_CGS_Away_01',
        'CV_CGS_Away_01', 'Media_CGM_Home_02','CV_CGM_Home_02','Media_CGM_Away_02', 'CV_CGM_Away_02', 'Media_CGS_Home_02',
        'CV_CGS_Home_02', 'Media_CGS_Away_02','CV_CGS_Away_02','Media_Prob_Home','CV_Med_Prob_Home', 'Media_Prob_Away', 
        'CV_Med_Prob_Away', 'Med_Prim_Golo_Marcado_Home','Med_Prim_Golo_Sofrido_Home', 'Med_Prim_Golo_Marcado_Away', 
        'Med_Prim_Golo_Sofrido_Away','Porc_Marcou_Primeiro_Golo_Home','Porc_Marcou_Primeiro_Golo_Away', 'Porc_Sofreu_Primeiro_Golo_Home',
        'Porc_Sofreu_Primeiro_Golo_Away', 'Porc_Marcou_Primeiro_Golo_Home_1P','Porc_Marcou_Primeiro_Golo_Away_1P',
        'Porc_Sofreu_Primeiro_Golo_Home_1P', 'Porc_Sofreu_Primeiro_Golo_Away_1P', 'Porc_BTTS_Y_Home','Porc_BTTS_Y_Away',
        'Porc_Home_Win_HT', 'Porc_Away_Win_HT', 'Porc_Home_Win_FT', 'Porc_Away_Win_FT','Porc_Score_Min_1G_Home',
        'Porc_Score_Min_1G_Away', 'Porc_Took_Min_1G_Home', 'Porc_Took_Min_1G_Away',
    ]
    df = df_jogos_do_dia.loc[:, selected_columns]

    # Apply Lay Away filters (customize as needed)
    Lay_Away = df[
        #(df['FT_Odd_H'] <= 2.5) & 
        #(df['FT_Odd_A'].between(3, 10)) &
        (df['Med_Power_Ranking_Home'] > df['Med_Power_Ranking_Away'] ) &
        ((df["Med_Power_Ranking_Home"] - df["Med_Power_Ranking_Away"])> 15) &
        (df['Media_SG_Home'] > df['Media_SG_Away']) & (df['CV_SG_Home'] <= 0.7) 
        (df['Media_CGM_Home_02'] >= 0.9) & (df['CV_CGM_Home_02'] < 0.7)
    ]
    Lay_Away = Lay_Away.sort_values(by='Time', ascending=True)
    Lay_Away = drop_reset_index(Lay_Away)
    return Lay_Away

def show_lay():
    st.title("Fluffy Chips Dashboard")

    # User selects the date
    dia = st.date_input("Data da Analise", date.today())
    
    # Load jogos data
    Jogos_do_Dia = read_jogos(dia)
    st.dataframe(Jogos_do_Dia)
    
    if not Jogos_do_Dia.empty:
        # Lay Home
        st.header("Lay Home")
        Lay_Home = filter_lay_home(Jogos_do_Dia)
        if Lay_Home.empty:
            st.warning("No matches found for Lay Home filter.")
        else:
            st.dataframe(Lay_Home)
        
        # Lay Away
        st.header("Lay Away")
        Lay_Away = filter_lay_away(Jogos_do_Dia)
        if Lay_Away.empty:
            st.warning("No matches found for Lay Away filter.")
        else:
            st.dataframe(Lay_Away)
    
    else:
        st.warning("No data available for the selected date.")
