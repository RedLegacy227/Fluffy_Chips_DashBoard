import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df


def show_back_home():
    st.title("Fluffy Chips")
    st.header("Back Home")

    dia = st.date_input("Data da Analise", date.today())

    Jogos_do_Dia = pd.read_csv(f'')