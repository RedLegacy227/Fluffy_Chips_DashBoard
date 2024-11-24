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
    jogos_do_dia = pd.read_csv(f'https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia/refs/heads/main/Jogos_Flashscore_' + str(dia) + '.csv')
    try:
        jogos_do_dia = jogos_do_dia[['League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A','HT_Odd_Over05', 'HT_Odd_Under05', 'FT_Odd_Over15','FT_Odd_Under15','FT_Odd_Over25','FT_Odd_Under25', 'Odd_BTTS_Yes', 'Odd_BTTS_No']]
        jogos_do_dia = drop_reset_index(jogos_do_dia)
    except:
        jogos_do_dia = jogos_do_dia[['League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A','HT_Odd_Over05', 'HT_Odd_Under05', 'FT_Odd_Over15','FT_Odd_Under15','FT_Odd_Over25','FT_Odd_Under25', 'Odd_BTTS_Yes', 'Odd_BTTS_No']]
        jogos_do_dia.columns = ['League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A','HT_Odd_Over05', 'HT_Odd_Under05', 'FT_Odd_Over15','FT_Odd_Under15','FT_Odd_Over25','FT_Odd_Under25', 'Odd_BTTS_Yes', 'Odd_BTTS_No']
        jogos_do_dia = drop_reset_index(jogos_do_dia)
    st.dataframe(jogos_do_dia)

    return jogos_do_dia

def show_back():
    st.title("Fluffy Chips DashBoard")
    

    dia = st.date_input("Data da Analise", date.today())

    Jogos_do_Dia = read_jogos(dia)
    st.write("")
    st.header("Back Home")
    st.write("")
    st.write("")
    st.write("Em Construção")
    st.write("")
    st.write("")
    st.header("Back Away")
    st.write("")
    st.write("")
    st.write("Em Construção")
    st.write("")
    st.write("")
    

