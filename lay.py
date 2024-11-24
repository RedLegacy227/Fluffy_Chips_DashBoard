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
    # Base URL for CSV files
    base_url = "https://raw.githubusercontent.com/RedLegacy227/df_jogos_do_dia/refs/heads/main/"
    file_name = f"df_jogod_do_dia_{dia}.csv"
    file_url = base_url + file_name

    try:
        # Read CSV file from the constructed URL
        jogos_do_dia = pd.read_csv(file_url)

        # Define columns to retain
        selected_columns = [
            'League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'HT_Odd_Ov05', 'HT_Odd_Un05',
            'FT_Odd_Ov15', 'FT_Odd_Un15', 'FT_Odd_Ov25', 'FT_Odd_Un25', 'FT_Odd_BTTS_Y', 'FT_Odd_BTTS_N', 'Prob_H',
            'Prob_D', 'Prob_A', 'Prob_Ov05_HT', 'Prob_Un05_HT', 'Prob_Ov15_FT', 'Prob_Un15_FT', 'Prob_Ov25_FT',
            'Prob_Un25_FT', 'Prob_BTTS_Y_FT', 'Prob_BTTS_N_FT', 'H_D', 'H_A', 'D_H', 'D_A', 'A_H', 'A_D',
            'Dif_Abs_HomeAway', 'Dif_Abs_HomeDraw', 'Dif_Abs_DrawAway', 'Angle_HomeAway', 'Angle_HomeDraw',
            'Angle_DrawAway', 'Dif_Perc_HomeAway', 'Dif_Perc_HomeDraw', 'Dif_Perc_DrawAway', 'Media_Ptos_Home',
            'CV_Ptos_Home', 'Media_Ptos_Away', 'CV_Ptos_Away', 'Media_SG_Home', 'CV_SG_Home', 'Media_SG_Away',
            'CV_SG_Away', 'Media_GM_Home_1P', 'CV_GM_Home_1P', 'Media_GM_Away_1P', 'CV_GM_Away_1P',
            'Media_GS_Home_1P', 'CV_GS_Home_1P', 'Media_GS_Away_1P', 'CV_GS_Away_1P', 'Media_GM_Home', 'CV_GM_Home',
            'Media_GM_Away', 'CV_GM_Away', 'Media_GS_Home', 'CV_GS_Home', 'Media_GS_Away', 'CV_GS_Away',
            'Media_CGM_Home_01', 'CV_CGM_Home_01', 'Media_CGM_Away_01', 'CV_CGM_Away_01', 'Media_CGS_Home_01',
            'CV_CGS_Home_01', 'Media_CGS_Away_01', 'CV_CGS_Away_01', 'Media_CGM_Home_02', 'CV_CGM_Home_02',
            'Media_CGM_Away_02', 'CV_CGM_Away_02', 'Media_CGS_Home_02', 'CV_CGS_Home_02', 'Media_CGS_Away_02',
            'CV_CGS_Away_02', 'Media_RPS_MO_Home', 'CV_RPS_MO_Home', 'Media_RPS_MO_Away', 'CV_RPS_MO_Away',
            'Media_RPS_OvUn_Home', 'CV_RPS_OvUn_Home', 'Media_RPS_OvUn_Away', 'CV_RPS_OvUn_Away',
            'Media_RPS_BTTS_Home', 'CV_RPS_BTTS_Home', 'Media_RPS_BTTS_Away', 'CV_RPS_BTTS_Away', 'Media_Prob_Home',
            'CV_Med_Prob_Home', 'Media_Prob_Away', 'CV_Med_Prob_Away', 'Med_Prim_Golo_Marcado_Home',
            'Med_Prim_Golo_Sofrido_Home', 'Med_Prim_Golo_Marcado_Away', 'Med_Prim_Golo_Sofrido_Away',
            'Porc_Marcou_Primeiro_Golo_Home', 'Porc_Marcou_Primeiro_Golo_Away', 'Porc_Sofreu_Primeiro_Golo_Home',
            'Porc_Sofreu_Primeiro_Golo_Away', 'Porc_Marcou_Primeiro_Golo_Home_1P', 'Porc_Marcou_Primeiro_Golo_Away_1P',
            'Porc_Sofreu_Primeiro_Golo_Home_1P', 'Porc_Sofreu_Primeiro_Golo_Away_1P', 'Porc_BTTS_Y_Home',
            'Porc_BTTS_Y_Away', 'Porc_Over05HT_Home', 'Porc_Over05HT_Away', 'Porc_Under05HT_Home',
            'Porc_Under05HT_Away', 'Porc_Over15HT_Home', 'Porc_Over15HT_Away', 'Porc_Under15HT_Home',
            'Porc_Under15HT_Away', 'Porc_Over05FT_Home', 'Porc_Over05FT_Away', 'Porc_Under05FT_Home',
            'Porc_Under05FT_Away', 'Porc_Over15FT_Home', 'Porc_Over15FT_Away', 'Porc_Under15FT_Home',
            'Porc_Under15FT_Away', 'Porc_Over25FT_Home', 'Porc_Over25FT_Away', 'Porc_Under25FT_Home',
            'Porc_Under25FT_Away', 'Porc_Home_Win_HT', 'Porc_Away_Win_HT', 'Porc_Home_Win_FT', 'Porc_Away_Win_FT',
            'Porc_Score_Min_1G_Home', 'Porc_Score_Min_1G_Away', 'Porc_Took_Min_1G_Home', 'Porc_Took_Min_1G_Away',
            'Med_Power_Ranking_Home', 'CV_pwr_Home', 'Med_Power_Ranking_Away', 'CV_pwr_Away'
        ]

        # Filter columns
        jogos_do_dia = jogos_do_dia[selected_columns]

        # Reset index
        jogos_do_dia = drop_reset_index(jogos_do_dia)

    except Exception as e:
        st.error(f"Error loading data: {e}")
        jogos_do_dia = pd.DataFrame()  # Return empty DataFrame if error

    # Display in Streamlit
    st.dataframe(jogos_do_dia)

    return jogos_do_dia

def show_lay():
    st.title("Fluffy Chips DashBoard")
    

    dia = st.date_input("Data da Analise", date.today())

    Jogos_do_Dia = read_jogos(dia)
    st.write("")
    st.header("Lay Home")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.header("Lay Away")
    st.write("")
    st.write("")
    st.write("")
    st.write("")