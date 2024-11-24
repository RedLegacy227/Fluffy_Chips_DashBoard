import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from scipy.stats import poisson
import ast

# Utility Function: Clean and Reset Index
def drop_reset_index(df):
    #df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

# Read and Process Daily Games
def read_jogos(dia):
    try:
        # Load CSV based on user-selected date
        url = f'https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia/refs/heads/main/Jogos_Flashscore_{dia}.csv'
        jogos_do_dia = pd.read_csv(url)
        
        # Filter and clean columns
        jogos_do_dia = jogos_do_dia[
            ['League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A',
             'HT_Odd_Over05', 'HT_Odd_Under05', 'FT_Odd_Over15', 'FT_Odd_Under15', 
             'FT_Odd_Over25', 'FT_Odd_Under25', 'Odd_BTTS_Yes', 'Odd_BTTS_No']
        ]
        jogos_do_dia = drop_reset_index(jogos_do_dia)
    except Exception as e:
        st.error(f"Error loading daily games data: {e}")
        jogos_do_dia = pd.DataFrame()  # Return an empty DataFrame on error

    st.dataframe(jogos_do_dia)  # Display data in Streamlit
    return jogos_do_dia

# Read and Process Historical Base Data
def read_base():
    try:
        # Load CSV from URL
        url = 'https://raw.githubusercontent.com/RedLegacy227/base_de_dados_fluffy_chips/refs/heads/main/fluffy_chips_2018_2024.csv'
        base_orig = pd.read_csv(url)
        
        # Select relevant columns
        columns = [
            "Date", "League", "Home", "Away", "HT_Goals_H", "HT_Goals_A",
            "FT_Goals_H", "FT_Goals_A", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", 
            "HT_Odd_Over05", "HT_Odd_Under05", "FT_Odd_Over05", "FT_Odd_Under05",
            "FT_Odd_Over15", "FT_Odd_Under15", "FT_Odd_Over25", "FT_Odd_Under25",
            "Odd_BTTS_Yes", "Odd_BTTS_No", "Goals_Minutes_Home", "Goals_Minutes_Away"
        ]
        base_orig = base_orig[columns]
        base_orig = drop_reset_index(base_orig)
    except Exception as e:
        st.error(f"Error loading base data: {e}")
        base_orig = pd.DataFrame()  # Return an empty DataFrame on error

    return base_orig

def obter_primeiro_gol(texto):
    try:
        lista = ast.literal_eval(texto)
        if isinstance(lista, list) and len(lista) > 0:
            primeiro_gol = lista[0]
            # Verifica se o valor do primeiro gol está no intervalo de 0 a 90 minutos
            return primeiro_gol if 0 <= primeiro_gol <= 90 else None
        else:
            return None
    except (ValueError, SyntaxError):
        return None

# Funções auxiliares
def calculate_over05_ht(df):
    # Over 0.5 HT: total de gols > 0
    df["Over05_HT"] = np.where(df["HT_Goals_H"] + df["HT_Goals_A"] > 0, 1, 0)

def calculate_under05_ht(df):
    # Under 0.5 HT: total de gols == 0
    df["Under05_HT"] = np.where(df["HT_Goals_H"] + df["HT_Goals_A"] == 0, 1, 0)

def calculate_over15_ht(df):
    # Over 1.5 HT: total de gols > 1
    df["Over15_HT"] = np.where(df["HT_Goals_H"] + df["HT_Goals_A"] > 1, 1, 0)

def calculate_under15_ht(df):
    # Under 1.5 HT: total de gols <= 1
    df["Under15_HT"] = np.where(df["HT_Goals_H"] + df["HT_Goals_A"] <= 1, 1, 0)
    
def calculate_over05_ft(df):
    # Over 0.5 FT: total de gols > 0
    df["Over05_FT"] = np.where(df["FT_Goals_H"] + df["FT_Goals_A"] > 1, 1, 0)
    
def calculate_under05_ft(df):
    # Under 0.5 FT: total de gols = 0
    df["Under05_FT"] = np.where(df["FT_Goals_H"] + df["FT_Goals_A"] == 0, 1, 0)

def calculate_over15_ft(df):
    # Over 1.5 FT: total de gols > 1
    df["Over15_FT"] = np.where(df["FT_Goals_H"] + df["FT_Goals_A"] > 0, 1, 0)

def calculate_under15_ft(df):
    # Under 1.5 FT: total de gols <= 1
    df["Under15_FT"] = np.where(df["FT_Goals_H"] + df["FT_Goals_A"] <= 1, 1, 0)

def calculate_over25_ft(df):
    # Over 2.5 FT: total de gols > 2
    df["Over25_FT"] = np.where(df["FT_Goals_H"] + df["FT_Goals_A"] > 2, 1, 0)

def calculate_under25_ft(df):
    # Under 2.5 FT: total de gols <= 2
    df["Under25_FT"] = np.where(df["FT_Goals_H"] + df["FT_Goals_A"] <= 2, 1, 0)

def calcular_primeiro_gol(df, column_name, new_column_name):
    """Converte a coluna de minutos para float e aplica a função para obter o primeiro gol."""
    df[new_column_name] = df[column_name].apply(obter_primeiro_gol)
    df[new_column_name] = pd.to_numeric(df[new_column_name], errors="coerce").astype(float)

n_per = 7
min_per = 5

# Streamlit Dashboard Function
def show_back():
    st.title("Fluffy Chips DashBoard")
    
    # Date Input
    dia = st.date_input("Data da Analise", date.today())
    
    # Read Data
    jogos_do_dia = read_jogos(dia)
    Jogos_do_Dia = jogos_do_dia.copy()
    base = read_base()
    
    df_liga = None  # Initialize df_liga
    
    if not base.empty:
        # Ensure proper datetime format for filtering
        base['Date'] = pd.to_datetime(base['Date'], errors='coerce')
        dia = pd.to_datetime(dia)

        # Drop rows with invalid dates
        base = base.dropna(subset=['Date'])

        # Filter base data for dates before the selected day
        base_filtered = base[base['Date'] < dia].sort_values('Date')
        
        # Create a copy for league-specific analysis
        df_liga = base_filtered.copy()

        # Sort and clean up the league DataFrame
        df_liga["Date"] = pd.to_datetime(df_liga["Date"], format="%Y-%m-%d")
        df_liga = df_liga.sort_values(by=['Date'])
        df_liga.reset_index(inplace=True, drop=True)
        df_liga.index = df_liga.index.set_names(['Nº Jogo'])
        df_liga = df_liga.rename(index=lambda x: x + 1)
        
        # Conversão de tipos de colunas
        df_liga["FT_Goals_H"] = pd.to_numeric(df_liga["FT_Goals_H"], errors='coerce').fillna(0).astype(int)
        df_liga["FT_Goals_A"] = pd.to_numeric(df_liga["FT_Goals_A"], errors='coerce').fillna(0).astype(int)
        df_liga["HT_Goals_H"] = pd.to_numeric(df_liga["HT_Goals_H"], errors='coerce').fillna(0).astype(int)
        df_liga["HT_Goals_A"] = pd.to_numeric(df_liga["HT_Goals_A"], errors='coerce').fillna(0).astype(int)
        
        # Criando as novas colunas de Saldo de Golos e Cálculo de Total_Goals_FT e Total_Goals_HT
        df_liga["Total_Goals_FT"] = df_liga["FT_Goals_H"] + df_liga["FT_Goals_A"]
        df_liga["Total_Goals_HT"] = df_liga["HT_Goals_H"] + df_liga["HT_Goals_A"]
        
        # Convertendo as colunas 'Goals_Minutes_Home' e 'Goals_Minutes_Away' para string
        df_liga["Goals_Minutes_Home"] = df_liga["Goals_Minutes_Home"].astype(str)
        df_liga["Goals_Minutes_Away"] = df_liga["Goals_Minutes_Away"].astype(str)
        
        #Probabilidades
        df_liga['p_H'] = 1 / df_liga['FT_Odd_H']
        df_liga['p_H'] = df_liga['p_H'].round(4)
        df_liga['p_D'] = 1 / df_liga['FT_Odd_D']
        df_liga['p_D'] = df_liga['p_D'].round(4)
        df_liga['p_A'] = 1 / df_liga['FT_Odd_A']
        df_liga['p_A'] = df_liga['p_A'].round(4)
        df_liga['p_Over_05_HT'] = 1 / df_liga['HT_Odd_Over05']
        df_liga['p_Over_05_HT'] = df_liga['p_Over_05_HT'].round(4)
        df_liga['p_Under_05_HT'] = 1 / df_liga['HT_Odd_Under05']
        df_liga['p_Under_05_HT'] = df_liga['p_Under_05_HT'].round(4)
        df_liga['p_Over_15_FT'] = 1 / df_liga['FT_Odd_Over15']
        df_liga['p_Over_15_FT'] = df_liga['p_Over_15_FT'].round(4)
        df_liga['p_Under_15_FT'] = 1 / df_liga['FT_Odd_Under15']
        df_liga['p_Under_15_FT'] = df_liga['p_Under_15_FT'].round(4)
        df_liga['p_Over_25_FT'] = 1 / df_liga['FT_Odd_Over25']
        df_liga['p_Over_25_FT'] = df_liga['p_Over_25_FT'].round(4)
        df_liga['p_Under_25_FT'] = 1 / df_liga['FT_Odd_Under25']
        df_liga['p_Under_25_FT'] = df_liga['p_Under_25_FT'].round(4)
        df_liga['p_BTTS_Yes_FT'] = 1 / df_liga['Odd_BTTS_Yes']
        df_liga['p_BTTS_Yes_FT'] = df_liga['p_BTTS_Yes_FT'].round(4)
        df_liga['p_BTTS_No_FT'] = 1 / df_liga['Odd_BTTS_No']
        df_liga['p_BTTS_No_FT'] = df_liga['p_BTTS_No_FT'].round(4)
        
        # Criando a Coluna de Resultado do Meio Tempo
        def Result_HT(HT_Goals_H, HT_Goals_A):
            if HT_Goals_H > HT_Goals_A:
                return 'H'
            elif HT_Goals_H == HT_Goals_A:
                return 'D'
            else:
                return 'A'
            
        # Criando a Coluna de Resultado Final
        def Result_FT(FT_Goals_H, FT_Goals_A):
            if FT_Goals_H > FT_Goals_A:
                return 'H'
            elif FT_Goals_H == FT_Goals_A:
                return 'D'
            else:
                return 'A'
        # Criando a Coluna de Overs
        def Result_Goals(Total_Goals_FT):
            if Total_Goals_FT > 2:
                return 'Ov'
            else:
                return 'Un'
        # Criando a Coluna de Ambas Marcam
        def BTTS(FT_Goals_H, FT_Goals_A):
            if FT_Goals_H > 0 and FT_Goals_A > 0:
                return 'Yes'
            else:
                return 'No'
            
        #Aplicando as funções ao dataframe
        df_liga['Result_FT'] = df_liga.apply(lambda row: Result_FT(row['FT_Goals_H'], row['FT_Goals_A']), axis=1)
        df_liga['Result_HT'] = df_liga.apply(lambda row: Result_HT(row['HT_Goals_H'], row['HT_Goals_A']), axis=1)
        df_liga['Result_Goals'] = df_liga.apply(lambda row: Result_Goals(row['FT_Goals_H'] + row['FT_Goals_A']), axis=1) # Corrigi aqui para calcular a soma dos gols
        df_liga['BTTS'] = df_liga.apply(lambda row: BTTS(row['FT_Goals_H'], row['FT_Goals_A']), axis=1)
        
        # Proporção entre as Odds
        df_liga['H_D'] = df_liga['FT_Odd_H'] / df_liga['FT_Odd_D']
        df_liga['H_A'] = df_liga['FT_Odd_H'] / df_liga['FT_Odd_A']
        df_liga['D_H'] = df_liga['FT_Odd_D'] / df_liga['FT_Odd_H']
        df_liga['D_A'] = df_liga['FT_Odd_D'] / df_liga['FT_Odd_A']
        df_liga['A_H'] = df_liga['FT_Odd_A'] / df_liga['FT_Odd_H']
        df_liga['A_D'] = df_liga['FT_Odd_A'] / df_liga['FT_Odd_D']
        # Diferença Absoluta entre as Odds
        df_liga['DifAbs_HomeAway'] = np.abs(df_liga['FT_Odd_H'] - df_liga['FT_Odd_A'])
        df_liga['DifAbs_HomeDraw'] = np.abs(df_liga['FT_Odd_H'] - df_liga['FT_Odd_D'])
        df_liga['DifAbs_DrawAway'] = np.abs(df_liga['FT_Odd_D'] - df_liga['FT_Odd_A'])
        
        # Angulo de Disparidade entre as Odds
        df_liga['Angle_HomeAway'] = np.degrees(np.arctan((df_liga['FT_Odd_A'] - df_liga['FT_Odd_H']) / 2))
        df_liga['Angle_HomeDraw'] = np.degrees(np.arctan((df_liga['FT_Odd_D'] - df_liga['FT_Odd_H']) / 2))
        df_liga['Angle_DrawAway'] = np.degrees(np.arctan((df_liga['FT_Odd_A'] - df_liga['FT_Odd_D']) / 2))
        
        # Diferenças Percentuais entre as Odds
        df_liga['DifPer_HomeAway'] = np.abs((df_liga['FT_Odd_H'] - df_liga['FT_Odd_A'])) / df_liga['FT_Odd_A']
        df_liga['DifPer_HomeDraw'] = np.abs((df_liga['FT_Odd_H'] - df_liga['FT_Odd_D'])) / df_liga['FT_Odd_D']
        df_liga['DifPer_DrawAway'] = np.abs((df_liga['FT_Odd_D'] - df_liga['FT_Odd_A'])) / df_liga['FT_Odd_A']
        
        #Criando o Calculo de Pontos
        df_liga['Ptos_H'] = np.where(df_liga['FT_Goals_H'] >  df_liga['FT_Goals_A'], 3, np.where(df_liga['FT_Goals_H'] == df_liga['FT_Goals_A'], 1, 0))
        df_liga['Ptos_A'] = np.where(df_liga['FT_Goals_A'] > df_liga['FT_Goals_H'], 3, np.where(df_liga['FT_Goals_H'] == df_liga['FT_Goals_A'], 1, 0))
        
        #Valor de Pontos
        df_liga['Value_Ptos_H'] = df_liga['Ptos_H'] * df_liga['p_A']
        df_liga['Value_Ptos_H'] = df_liga['Value_Ptos_H'].round(4)
        df_liga['Value_Ptos_A'] = df_liga['Ptos_A'] * df_liga['p_H']
        df_liga['Value_Ptos_A'] = df_liga['Value_Ptos_A'].round(4)
        
        #Saldo de Golos Home e Away
        df_liga['SG_H'] = df_liga['FT_Goals_H'] - df_liga['FT_Goals_A']
        df_liga['SG_A'] = df_liga['FT_Goals_A'] - df_liga['FT_Goals_H']
        
        #Valor do Saldo De Golos 
        df_liga['Value_SG_H'] = df_liga['SG_H'] * df_liga['p_A']
        df_liga['Value_SG_H'] = df_liga['Value_SG_H'].round(4)
        df_liga['Value_SG_A'] = df_liga['SG_A'] * df_liga['p_H']
        df_liga['Value_SG_A'] = df_liga['Value_SG_A'].round(4)
        
        #Valor dos Golos Marcados 1 Parte
        df_liga['Value_GM_H_1P'] = df_liga['HT_Goals_H'] * df_liga['p_A']
        df_liga['Value_GM_H_1P'] = df_liga['Value_GM_H_1P'].round(4)
        df_liga['Value_GM_A_1P'] = df_liga['HT_Goals_A'] * df_liga['p_H']
        df_liga['Value_GM_A_1P'] = df_liga['Value_GM_A_1P'].round(4)
        
        #Valor dos Golos Sofridos 1 Parte
        df_liga['Value_GS_H_1P'] = df_liga['HT_Goals_A'] * df_liga['p_A']
        df_liga['Value_GS_H_1P'] = df_liga['Value_GS_H_1P'].round(4)
        df_liga['Value_GS_A_1P'] = df_liga['HT_Goals_H'] * df_liga['p_H']
        df_liga['Value_GS_A_1P'] = df_liga['Value_GS_A_1P'].round(4)
                
        #Valor dos Golos Marcados
        df_liga['Value_GM_H'] = df_liga['FT_Goals_H'] * df_liga['p_A'] 
        df_liga['Value_GM_H'] = df_liga['Value_GM_H'].round(4)
        df_liga['Value_GM_A'] = df_liga['FT_Goals_A'] * df_liga['p_H']
        df_liga['Value_GM_A'] = df_liga['Value_GM_A'].round(4)
        
        #Valor dos Golos Sofridos
        df_liga['Value_GS_H'] = df_liga['FT_Goals_A'] * df_liga['p_A']
        df_liga['Value_GS_H'] = df_liga['Value_GS_H'].round(4)
        df_liga['Value_GS_A'] = df_liga['FT_Goals_H'] * df_liga['p_H']
        df_liga['Value_GS_A'] = df_liga['Value_GS_A'].round(4)
        
        #Custo do Golo Marcado 1.0
        df_liga['CG_GM_H_01'] = df_liga['FT_Goals_H'] / df_liga['p_H']
        df_liga['CG_GM_H_01'] = df_liga['CG_GM_H_01'].round(4)
        df_liga['CG_GM_A_01'] = df_liga['FT_Goals_A'] / df_liga['p_A']
        df_liga['CG_GM_A_01'] = df_liga['CG_GM_A_01'].round(4)
        
        #Custo do Golo Sofrido 1.0
        df_liga['CG_GS_H_01'] = df_liga['FT_Goals_A'] / df_liga['p_H']
        df_liga['CG_GS_H_01'] = df_liga['CG_GS_H_01'].round(4)
        df_liga['CG_GS_A_01'] = df_liga['FT_Goals_H'] / df_liga['p_A']
        df_liga['CG_GS_A_01'] = df_liga['CG_GS_A_01'].round(4)
        
        #Custo do Golo Marcado 2.0
        df_liga['CG_GM_H_02'] = (df_liga['FT_Goals_H'] / 2) + (df_liga['p_H'] / 2)
        df_liga['CG_GM_H_02'] = df_liga['CG_GM_H_02'].round(4)
        df_liga['CG_GM_A_02'] = (df_liga['FT_Goals_A'] / 2) + (df_liga['p_A'] / 2)
        df_liga['CG_GM_A_02'] = df_liga['CG_GM_A_02'].round(4)
        
        #Custo do Golo Sofrido 2.0
        df_liga['CG_GS_H_02'] = (df_liga['FT_Goals_A'] / 2) + (df_liga['p_H'] / 2)
        df_liga['CG_GS_H_02'] = df_liga['CG_GS_H_02'].round(4)
        df_liga['CG_GS_A_02'] = (df_liga['FT_Goals_H'] / 2) + (df_liga['p_A'] / 2)
        df_liga['CG_GS_A_02'] = df_liga['CG_GS_A_02'].round(4)
        
        #RPS Match Odds - Abaixo de 0,33 Tendencia - Acima Assimetria
        df_liga['RPS_MO'] = np.where(df_liga['Result_FT'] == "H",(1/df_liga['FT_Odd_H'] - 1)**2 + (1/df_liga['FT_Odd_D'])**2 + (1/df_liga['FT_Odd_A'])**2,np.where(df_liga['Result_FT'] == "D",(1/df_liga['FT_Odd_H'])**2 + (1/df_liga['FT_Odd_D'] - 1)**2 + (1/df_liga['FT_Odd_A'])**2,(1/df_liga['FT_Odd_H'])**2 + (1/df_liga['FT_Odd_D'])**2 + (1/df_liga['FT_Odd_A'] - 1)**2))
        df_liga['RPS_MO'] = df_liga['RPS_MO'].round(4)
        
        #RPS Over/Under - Abaixo de 0,50 Tendencia - Acima Assimetria
        df_liga['RPS_OV_UN'] = np.where(df_liga['Result_Goals'] == "OV",(1/df_liga['FT_Odd_Over25'] - 1)**2 + (1/df_liga['FT_Odd_Under25'])**2,(1/df_liga['FT_Odd_Over25'])**2 + (1/df_liga['FT_Odd_Under25'] - 1)**2)
        df_liga['RPS_OV_UN'] = df_liga['RPS_OV_UN'].round(4)
        
        #RPS BTTS - Abaixo de 0,50 Tendencia - Acima Assimetria
        df_liga['RPS_BTTS'] = np.where(df_liga['BTTS'] == "Yes",(1/df_liga['Odd_BTTS_Yes'] - 1)**2 + (1/df_liga['Odd_BTTS_No'])**2,(1/df_liga['Odd_BTTS_Yes'])**2 + (1/df_liga['Odd_BTTS_No'] - 1)**2) 
        df_liga['RPS_BTTS'] = df_liga['RPS_BTTS'].round(4)
        
        #Média de Pontos Ponderada
        df_liga['Media_Ptos_H'] = df_liga.groupby('Home')['Value_Ptos_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Home')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_Ptos_H'] = df_liga['Media_Ptos_H'].round(4)
        df_liga['Media_Ptos_A'] = df_liga.groupby('Away')['Value_Ptos_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Away')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_Ptos_A'] = df_liga['Media_Ptos_A'].round(4)
        df_liga['Media_Ptos_H'] = df_liga.groupby('Home')['Media_Ptos_H'].shift(1)
        df_liga['Media_Ptos_A'] = df_liga.groupby('Away')['Media_Ptos_A'].shift(1)
        
        df_liga['DesvPad_Ptos_H'] = df_liga.groupby('Home')['Ptos_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_Ptos_H'] = df_liga['DesvPad_Ptos_H'].round(4)
        df_liga['DesvPad_Ptos_A'] = df_liga.groupby('Away')['Ptos_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_Ptos_A'] = df_liga['DesvPad_Ptos_A'].round(4)
        df_liga['DesvPad_Ptos_H'] = df_liga.groupby('Home')['DesvPad_Ptos_H'].shift(1)
        df_liga['DesvPad_Ptos_A'] = df_liga.groupby('Away')['DesvPad_Ptos_A'].shift(1)
        
        df_liga['CV_Ptos_H'] = df_liga['DesvPad_Ptos_H'] / df_liga['Media_Ptos_H']
        df_liga['CV_Ptos_H'] = df_liga['CV_Ptos_H'].round(4)
        df_liga['CV_Ptos_A'] = df_liga['DesvPad_Ptos_A'] / df_liga['Media_Ptos_A']
        df_liga['CV_Ptos_A'] = df_liga['CV_Ptos_A'].round(4)
        
        #Média do Saldo de Golos Ponderada
        df_liga['Media_SG_H'] = df_liga.groupby('Home')['Value_SG_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Home')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_SG_H'] = df_liga['Media_SG_H'].round(4)
        df_liga['Media_SG_A'] = df_liga.groupby('Away')['Value_SG_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Away')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_SG_A'] = df_liga['Media_SG_A'].round(4)
        df_liga['Media_SG_H'] = df_liga.groupby('Home')['Media_SG_H'].shift(1)
        df_liga['Media_SG_A'] = df_liga.groupby('Away')['Media_SG_A'].shift(1)
        
        df_liga['DesvPad_SG_H'] = df_liga.groupby('Home')['Value_SG_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_SG_H'] = df_liga['DesvPad_SG_H'].round(4)
        df_liga['DesvPad_SG_A'] = df_liga.groupby('Away')['Value_SG_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_SG_A'] = df_liga['DesvPad_SG_A'].round(4)
        df_liga['DesvPad_SG_H'] = df_liga.groupby('Home')['DesvPad_SG_H'].shift(1)
        df_liga['DesvPad_SG_A'] = df_liga.groupby('Away')['DesvPad_SG_A'].shift(1)
        
        df_liga['CV_SG_H'] = df_liga['DesvPad_SG_H'] / df_liga['Media_SG_H']
        df_liga['CV_SG_H'] = df_liga['CV_SG_H'].round(4)
        df_liga['CV_SG_A'] = df_liga['DesvPad_SG_A'] / df_liga['Media_SG_A']
        df_liga['CV_SG_A'] = df_liga['CV_SG_A'].round(4)
        
        #Média de Golos Marcados Ponderados 1 Parte
        df_liga['Media_GM_H_1P'] = df_liga.groupby('Home')['Value_GM_H_1P'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Home')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GM_H_1P'] = df_liga['Media_GM_H_1P'].round(4)
        df_liga['Media_GM_A_1P'] = df_liga.groupby('Away')['Value_GM_A_1P'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Away')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GM_A_1P'] = df_liga['Media_GM_A_1P'].round(4)
        df_liga['Media_GM_H_1P'] = df_liga.groupby('Home')['Media_GM_H_1P'].shift(1)
        df_liga['Media_GM_A_1P'] = df_liga.groupby('Away')['Media_GM_A_1P'].shift(1)
        
        df_liga['DesvPad_GM_H_1P'] = df_liga.groupby('Home')['HT_Goals_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GM_H_1P'] = df_liga['DesvPad_GM_H_1P'].round(4)
        df_liga['DesvPad_GM_A_1P'] = df_liga.groupby('Away')['HT_Goals_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GM_A_1P'] = df_liga['DesvPad_GM_A_1P'].round(4)
        df_liga['DesvPad_GM_H_1P'] = df_liga.groupby('Home')['DesvPad_GM_H_1P'].shift(1)
        df_liga['DesvPad_GM_A_1P'] = df_liga.groupby('Away')['DesvPad_GM_A_1P'].shift(1)
        
        df_liga['CV_GM_H_1P'] = df_liga['DesvPad_GM_H_1P'] / df_liga['Media_GM_H_1P']
        df_liga['CV_GM_H_1P'] = df_liga['CV_GM_H_1P'].round(4)
        df_liga['CV_GM_A_1P'] = df_liga['DesvPad_GM_A_1P'] / df_liga['Media_GM_A_1P']
        df_liga['CV_GM_A_1P'] = df_liga['CV_GM_A_1P'].round(4)
        
        #Média de Golos Sofridos Ponderados 1 Parte
        df_liga['Media_GS_H_1P'] = df_liga.groupby('Home')['Value_GS_H_1P'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Home')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GS_H_1P'] = df_liga['Media_GS_H_1P'].round(4)
        df_liga['Media_GS_A_1P'] = df_liga.groupby('Away')['Value_GS_A_1P'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Away')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GS_A_1P'] = df_liga['Media_GS_A_1P'].round(4)
        df_liga['Media_GS_H_1P'] = df_liga.groupby('Home')['Media_GS_H_1P'].shift(1)
        df_liga['Media_GS_A_1P'] = df_liga.groupby('Away')['Media_GS_A_1P'].shift(1)
        
        df_liga['DesvPad_GS_H_1P'] = df_liga.groupby('Home')['HT_Goals_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GS_H_1P'] = df_liga['DesvPad_GS_H_1P'].round(4)
        df_liga['DesvPad_GS_A_1P'] = df_liga.groupby('Away')['HT_Goals_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GS_A_1P'] = df_liga['DesvPad_GS_A_1P'].round(4)
        df_liga['DesvPad_GS_H_1P'] = df_liga.groupby('Home')['DesvPad_GS_H_1P'].shift(1)
        df_liga['DesvPad_GS_A_1P'] = df_liga.groupby('Away')['DesvPad_GS_A_1P'].shift(1)
        
        df_liga['CV_GS_H_1P'] = df_liga['DesvPad_GS_H_1P'] / df_liga['Media_GS_H_1P']
        df_liga['CV_GS_H_1P'] = df_liga['CV_GS_H_1P'].round(4)
        df_liga['CV_GS_A_1P'] = df_liga['DesvPad_GS_A_1P'] / df_liga['Media_GS_A_1P']
        df_liga['CV_GS_A_1P'] = df_liga['CV_GS_A_1P'].round(4)
        
        #Média de Golos Marcados Ponderados
        df_liga['Media_GM_H'] = df_liga.groupby('Home')['Value_GM_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Home')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GM_H'] = df_liga['Media_GM_H'].round(4)
        df_liga['Media_GM_A'] = df_liga.groupby('Away')['Value_GM_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Away')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GM_A'] = df_liga['Media_GM_A'].round(4)
        df_liga['Media_GM_H'] = df_liga.groupby('Home')['Media_GM_H'].shift(1)
        df_liga['Media_GM_A'] = df_liga.groupby('Away')['Media_GM_A'].shift(1)
        
        df_liga['DesvPad_GM_H'] = df_liga.groupby('Home')['FT_Goals_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GM_H'] = df_liga['DesvPad_GM_H'].round(4)
        df_liga['DesvPad_GM_A'] = df_liga.groupby('Away')['FT_Goals_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GM_A'] = df_liga['DesvPad_GM_A'].round(4)
        df_liga['DesvPad_GM_H'] = df_liga.groupby('Home')['DesvPad_GM_H'].shift(1)
        df_liga['DesvPad_GM_A'] = df_liga.groupby('Away')['DesvPad_GM_A'].shift(1)
        
        df_liga['CV_GM_H'] = df_liga['DesvPad_GM_H'] / df_liga['Media_GM_H']
        df_liga['CV_GM_H'] = df_liga['CV_GM_H'].round(4)
        df_liga['CV_GM_A'] = df_liga['DesvPad_GM_A'] / df_liga['Media_GM_A']
        df_liga['CV_GM_A'] = df_liga['CV_GM_A'].round(4)
        
        #Média de Golos Sofridos Ponderados
        df_liga['Media_GS_H'] = df_liga.groupby('Home')['Value_GS_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Home')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GS_H'] = df_liga['Media_GS_H'].round(4)
        df_liga['Media_GS_A'] = df_liga.groupby('Away')['Value_GS_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True) / df_liga.groupby('Away')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_GS_A'] = df_liga['Media_GS_A'].round(4)
        df_liga['Media_GS_H'] = df_liga.groupby('Home')['Media_GS_H'].shift(1)
        df_liga['Media_GS_A'] = df_liga.groupby('Away')['Media_GS_A'].shift(1)
        
        df_liga['DesvPad_GS_H'] = df_liga.groupby('Home')['FT_Goals_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GS_H'] = df_liga['DesvPad_GS_H'].round(4)
        df_liga['DesvPad_GS_A'] = df_liga.groupby('Away')['FT_Goals_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_GS_A'] = df_liga['DesvPad_GS_A'].round(4)
        df_liga['DesvPad_GS_H'] = df_liga.groupby('Home')['DesvPad_GS_H'].shift(1)
        df_liga['DesvPad_GS_A'] = df_liga.groupby('Away')['DesvPad_GS_A'].shift(1)
        
        df_liga['CV_GS_H'] = df_liga['DesvPad_GS_H'] / df_liga['Media_GS_H']
        df_liga['CV_GS_H'] = df_liga['CV_GS_H'].round(4)
        df_liga['CV_GS_A'] = df_liga['DesvPad_GS_A'] / df_liga['Media_GS_A']
        df_liga['CV_GS_A'] = df_liga['CV_GS_A'].round(4)
        
        #Média de Custo do Golo Marcado  01
        df_liga['Media_CGM_H_01'] = df_liga.groupby('Home')['CG_GM_H_01'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGM_H_01'] = df_liga['Media_CGM_H_01'].round(4)
        df_liga['Media_CGM_A_01'] = df_liga.groupby('Away')['CG_GM_A_01'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGM_A_01'] = df_liga['Media_CGM_A_01'].round(4)
        
        df_liga['DesvPad_CGM_H_01'] = df_liga.groupby('Home')['Media_CGM_H_01'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGM_H_01'] = df_liga['DesvPad_CGM_H_01'].round(4)
        df_liga['DesvPad_CGM_A_01'] = df_liga.groupby('Away')['Media_CGM_A_01'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGM_A_01'] = df_liga['DesvPad_CGM_A_01'].round(4)
        df_liga['DesvPad_CGM_H_01'] = df_liga.groupby('Home')['DesvPad_CGM_H_01'].shift(1)
        df_liga['DesvPad_CGM_A_01'] = df_liga.groupby('Away')['DesvPad_CGM_A_01'].shift(1)
        
        df_liga['CV_CGM_H_01'] = df_liga['DesvPad_CGM_H_01'] / df_liga['Media_CGM_H_01']
        df_liga['CV_CGM_H_01'] = df_liga['CV_CGM_H_01'].round(4)
        df_liga['CV_CGM_A_01'] = df_liga['DesvPad_CGM_A_01'] / df_liga['Media_CGM_A_01']
        df_liga['CV_CGM_A_01'] = df_liga['CV_CGM_A_01'].round(4)
        
        #Média de Custo do Golo Sofrido 01
        df_liga['Media_CGS_H_01'] = df_liga.groupby('Home')['CG_GS_H_01'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGS_H_01'] = df_liga['Media_CGS_H_01'].round(4)
        df_liga['Media_CGS_A_01'] = df_liga.groupby('Away')['CG_GS_A_01'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGS_A_01'] = df_liga['Media_CGS_A_01'].round(4)
        
        df_liga['DesvPad_CGS_H_01'] = df_liga.groupby('Home')['Media_CGS_H_01'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGS_H_01'] = df_liga['DesvPad_CGS_H_01'].round(4)
        df_liga['DesvPad_CGS_A_01'] = df_liga.groupby('Away')['Media_CGS_A_01'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGS_A_01'] = df_liga['DesvPad_CGS_H_01'].round(4)
        df_liga['DesvPad_CGS_H_01'] = df_liga.groupby('Home')['DesvPad_CGS_H_01'].shift(1)
        df_liga['DesvPad_CGS_A_01'] = df_liga.groupby('Away')['DesvPad_CGS_A_01'].shift(1)
        
        df_liga['CV_CGS_H_01'] = df_liga['DesvPad_CGS_H_01'] / df_liga['Media_CGS_H_01']
        df_liga['CV_CGS_H_01'] = df_liga['CV_CGS_H_01'].round(4)
        df_liga['CV_CGS_A_01'] = df_liga['DesvPad_CGS_A_01'] / df_liga['Media_CGS_A_01']
        df_liga['CV_CGS_A_01'] = df_liga['CV_CGS_A_01'].round(4)
        
        #Média de Custo do Golo Marcado  02
        df_liga['Media_CGM_H_02'] = df_liga.groupby('Home')['CG_GM_H_02'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGM_H_02'] = df_liga['Media_CGM_H_02'].round(4)
        df_liga['Media_CGM_A_02'] = df_liga.groupby('Away')['CG_GM_A_02'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGM_A_02'] = df_liga['Media_CGM_A_02'].round(4)
        
        df_liga['DesvPad_CGM_H_02'] = df_liga.groupby('Home')['Media_CGM_H_02'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGM_H_02'] = df_liga['DesvPad_CGM_H_02'].round(4)
        df_liga['DesvPad_CGM_A_02'] = df_liga.groupby('Away')['Media_CGM_A_02'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGM_A_02'] = df_liga['DesvPad_CGM_A_02'].round(4)
        df_liga['DesvPad_CGM_H_02'] = df_liga.groupby('Home')['DesvPad_CGM_H_02'].shift(1)
        df_liga['DesvPad_CGM_A_02'] = df_liga.groupby('Away')['DesvPad_CGM_A_02'].shift(1)
        
        df_liga['CV_CGM_H_02'] = df_liga['DesvPad_CGM_H_02'] / df_liga['Media_CGM_H_02']
        df_liga['CV_CGM_H_02'] = df_liga['CV_CGM_H_02'].round(4)
        df_liga['CV_CGM_A_02'] = df_liga['DesvPad_CGM_A_02'] / df_liga['Media_CGM_A_02']
        df_liga['CV_CGM_A_02'] = df_liga['CV_CGM_A_02'].round(4)
        
        #Média de Custo do Golo Sofrido 02
        df_liga['Media_CGS_H_02'] = df_liga.groupby('Home')['CG_GS_H_02'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGS_H_02'] = df_liga['Media_CGS_H_02'].round(4)
        df_liga['Media_CGS_A_02'] = df_liga.groupby('Away')['CG_GS_A_02'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_CGS_A_02'] = df_liga['Media_CGS_A_02'].round(4)
        
        df_liga['DesvPad_CGS_H_02'] = df_liga.groupby('Home')['Media_CGS_H_02'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGS_H_02'] = df_liga['DesvPad_CGS_H_02'].round(4)
        df_liga['DesvPad_CGS_A_02'] = df_liga.groupby('Away')['Media_CGS_A_02'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_CGS_A_02'] = df_liga['DesvPad_CGS_H_02'].round(4)
        df_liga['DesvPad_CGS_H_02'] = df_liga.groupby('Home')['DesvPad_CGS_H_02'].shift(1)
        df_liga['DesvPad_CGS_A_02'] = df_liga.groupby('Away')['DesvPad_CGS_A_02'].shift(1)
        
        df_liga['CV_CGS_H_02'] = df_liga['DesvPad_CGS_H_02'] / df_liga['Media_CGS_H_02']
        df_liga['CV_CGS_H_02'] = df_liga['CV_CGS_H_02'].round(4)
        df_liga['CV_CGS_A_02'] = df_liga['DesvPad_CGS_A_02'] / df_liga['Media_CGS_A_02']
        df_liga['CV_CGS_A_02'] = df_liga['CV_CGS_A_02'].round(4)
        
        #Media RPS MO 
        df_liga['Media_RPS_MO_H'] = df_liga.groupby('Home')['RPS_MO'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_RPS_MO_H'] =df_liga['Media_RPS_MO_H'].round(4)
        df_liga['Media_RPS_MO_A'] = df_liga.groupby('Away')['RPS_MO'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_RPS_MO_A'] =df_liga['Media_RPS_MO_A'].round(4)
        
        df_liga['DesvPad_RPS_MO_H'] = df_liga.groupby('Home')['Media_RPS_MO_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_RPS_MO_H'] = df_liga['DesvPad_RPS_MO_H'].round(4)
        df_liga['DesvPad_RPS_MO_A'] = df_liga.groupby('Away')['Media_RPS_MO_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_RPS_MO_A'] = df_liga['DesvPad_RPS_MO_A'].round(4)
        df_liga['DesvPad_RPS_MO_H'] = df_liga.groupby('Home')['DesvPad_RPS_MO_H'].shift(1)
        df_liga['DesvPad_RPS_MO_A'] = df_liga.groupby('Away')['DesvPad_RPS_MO_A'].shift(1)
        
        df_liga['CV_RPS_MO_H'] = df_liga['DesvPad_RPS_MO_H'] / df_liga['Media_RPS_MO_H']
        df_liga['CV_RPS_MO_H'] = df_liga['CV_RPS_MO_H'].round(4)
        df_liga['CV_RPS_MO_A'] = df_liga['DesvPad_RPS_MO_A'] / df_liga['Media_RPS_MO_A']
        df_liga['CV_RPS_MO_A'] = df_liga['CV_RPS_MO_A'].round(4)
        
        #Media RPS OvUn 
        df_liga['Media_RPS_OvUn_H'] = df_liga.groupby('Home')['RPS_OV_UN'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_RPS_OvUn_H'] =df_liga['Media_RPS_OvUn_H'].round(4)
        df_liga['Media_RPS_OvUn_A'] = df_liga.groupby('Away')['RPS_OV_UN'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_RPS_OvUn_A'] =df_liga['Media_RPS_OvUn_A'].round(4)
        
        df_liga['DesvPad_RPS_OvUn_H'] = df_liga.groupby('Home')['Media_RPS_OvUn_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_RPS_OvUn_H'] = df_liga['DesvPad_RPS_OvUn_H'].round(4)
        df_liga['DesvPad_RPS_OvUn_A'] = df_liga.groupby('Away')['Media_RPS_OvUn_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_RPS_OvUn_A'] = df_liga['DesvPad_RPS_OvUn_A'].round(4)
        df_liga['DesvPad_RPS_OvUn_H'] = df_liga.groupby('Home')['DesvPad_RPS_OvUn_H'].shift(1)
        df_liga['DesvPad_RPS_OvUn_A'] = df_liga.groupby('Away')['DesvPad_RPS_OvUn_A'].shift(1)
        
        df_liga['CV_RPS_OvUn_H'] = df_liga['DesvPad_RPS_OvUn_H'] / df_liga['Media_RPS_OvUn_H']
        df_liga['CV_RPS_OvUn_H'] = df_liga['CV_RPS_OvUn_H'].round(4)
        df_liga['CV_RPS_OvUn_A'] = df_liga['DesvPad_RPS_OvUn_A'] / df_liga['Media_RPS_OvUn_A']
        df_liga['CV_RPS_OvUn_A'] = df_liga['CV_RPS_OvUn_A'].round(4)
        
        #Media RPS BTTS
        df_liga['Media_RPS_BTTS_H'] = df_liga.groupby('Home')['RPS_BTTS'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_RPS_BTTS_H'] =df_liga['Media_RPS_BTTS_H'].round(4)
        df_liga['Media_RPS_BTTS_A'] = df_liga.groupby('Away')['RPS_BTTS'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_RPS_BTTS_A'] =df_liga['Media_RPS_BTTS_A'].round(4)
        
        df_liga['DesvPad_RPS_BTTS_H'] = df_liga.groupby('Home')['Media_RPS_BTTS_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_RPS_BTTS_H'] = df_liga['DesvPad_RPS_BTTS_H'].round(4)
        df_liga['DesvPad_RPS_BTTS_A'] = df_liga.groupby('Away')['Media_RPS_BTTS_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_RPS_BTTS_A'] = df_liga['DesvPad_RPS_BTTS_A'].round(4)
        df_liga['DesvPad_RPS_BTTS_H'] = df_liga.groupby('Home')['DesvPad_RPS_BTTS_H'].shift(1)
        df_liga['DesvPad_RPS_BTTS_A'] = df_liga.groupby('Away')['DesvPad_RPS_BTTS_A'].shift(1)
        
        df_liga['CV_RPS_BTTS_H'] = df_liga['DesvPad_RPS_BTTS_H'] / df_liga['Media_RPS_BTTS_H']
        df_liga['CV_RPS_BTTS_H'] = df_liga['CV_RPS_BTTS_H'].round(4)
        df_liga['CV_RPS_BTTS_A'] = df_liga['DesvPad_RPS_BTTS_A'] / df_liga['Media_RPS_BTTS_A']
        df_liga['CV_RPS_BTTS_A'] = df_liga['CV_RPS_BTTS_A'].round(4)
        
        #Media das Probabilidades
        df_liga['Media_p_H'] = df_liga.groupby('Home')['p_H'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_p_H'] =df_liga['Media_p_H'].round(4)
        df_liga['Media_p_A'] = df_liga.groupby('Away')['p_A'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0,drop=True)
        df_liga['Media_p_A'] =df_liga['Media_p_A'].round(4)
        
        df_liga['DesvPad_p_H'] = df_liga.groupby('Home')['Media_p_H'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_p_H'] = df_liga['DesvPad_p_H'].round(4)
        df_liga['DesvPad_p_A'] = df_liga.groupby('Away')['Media_p_A'].rolling(window=n_per, min_periods=min_per).std().reset_index(0,drop=True)
        df_liga['DesvPad_p_A'] = df_liga['DesvPad_p_A'].round(4)
        df_liga['DesvPad_p_H'] = df_liga.groupby('Home')['DesvPad_p_H'].shift(1)
        df_liga['DesvPad_p_A'] = df_liga.groupby('Away')['DesvPad_p_A'].shift(1)
        
        df_liga['CV_p_H'] = df_liga['DesvPad_p_H'] / df_liga['Media_p_H']
        df_liga['CV_p_H'] = df_liga['CV_p_H'].round(4)
        df_liga['CV_p_A'] = df_liga['DesvPad_p_A'] / df_liga['Media_p_A']
        df_liga['CV_p_A'] = df_liga['CV_p_A'].round(4)
        
        #CV Match Odds -
        # 0 a 0,10 Jogo Super Equilibrado
        # 0,11 a 0,30 Jogo equilibrado
        #0,31 a 1 Jogo Desiquilibrado
        desvio_padrao = df_liga[['p_H','p_D','p_A']].std(axis=1)
        media = df_liga[['p_H','p_D','p_A']].mean(axis=1)
        CV_Odds = desvio_padrao / media
        df_liga['CV_MO_FT'] = CV_Odds
        df_liga['CV_MO_FT'] = df_liga['CV_MO_FT'].round(4)
        
        # #Predicao de Golos Marcados
        # df_liga['(P)GM_H_2.0'] = (df_liga['Media_CGM_H_02'] - (df_liga['p_H']/2))*2
        # df_liga['(P)GM_H_2.0'] = df_liga['(P)GM_H_2.0'].round(4)
        # df_liga['(P)GM_A_2.0'] = (df_liga['Media_CGM_A_02'] - (df_liga['p_A']/2))*2
        # df_liga['(P)GM_A_2.0'] = df_liga['(P)GM_A_2.0'].round(4)
        
        # #Predicao de Golos Sofridos
        # df_liga['(P)GS_H_2.0'] = (df_liga['Media_CGS_H_02'] - (df_liga['p_H']/2))*2
        # df_liga['(P)GS_H_2.0'] = df_liga['(P)GS_H_2.0'].round(4)
        # df_liga['(P)GS_A_2.0'] = (df_liga['Media_CGS_A_02'] - (df_liga['p_A']/2))*2
        # df_liga['(P)GS_A_2.0'] = df_liga['(P)GS_A_2.0'].round(4)
        
        # #Poisson Home Marca
        # df_liga['Poisson_GM_H_0'] = poisson.pmf(0, df_liga['Media_GM_H'])
        # df_liga['Poisson_GM_H_0'] = df_liga['Poisson_GM_H_0'].round(4)
        # df_liga['Poisson_GM_H_1'] = poisson.pmf(1, df_liga['Media_GM_H'])
        # df_liga['Poisson_GM_H_1'] = df_liga['Poisson_GM_H_1'].round(4)
        # df_liga['Poisson_GM_H_2'] = poisson.pmf(2, df_liga['Media_GM_H'])
        # df_liga['Poisson_GM_H_2'] = df_liga['Poisson_GM_H_2'].round(4)
        # df_liga['Poisson_GM_H_3'] = poisson.pmf(3, df_liga['Media_GM_H'])
        # df_liga['Poisson_GM_H_3'] = df_liga['Poisson_GM_H_3'].round(4)
        # df_liga['Poisson_GM_H_4'] = poisson.pmf(4, df_liga['Media_GM_H'])
        # df_liga['Poisson_GM_H_4'] = df_liga['Poisson_GM_H_4'].round(4)
        
        # #Poisson Away Marca
        # df_liga['Poisson_GM_A_0'] = poisson.pmf(0, df_liga['Media_GM_A'])
        # df_liga['Poisson_GM_A_0'] = df_liga['Poisson_GM_A_0'].round(4)
        # df_liga['Poisson_GM_A_1'] = poisson.pmf(1, df_liga['Media_GM_A'])
        # df_liga['Poisson_GM_A_1'] = df_liga['Poisson_GM_A_1'].round(4)
        # df_liga['Poisson_GM_A_2'] = poisson.pmf(2, df_liga['Media_GM_A'])
        # df_liga['Poisson_GM_A_2'] = df_liga['Poisson_GM_A_2'].round(4)
        # df_liga['Poisson_GM_A_3'] = poisson.pmf(3, df_liga['Media_GM_A'])
        # df_liga['Poisson_GM_A_3'] = df_liga['Poisson_GM_A_3'].round(4)
        # df_liga['Poisson_GM_A_4'] = poisson.pmf(4, df_liga['Media_GM_A'])
        # df_liga['Poisson_GM_A_4'] = df_liga['Poisson_GM_A_4'].round(4)
        
        # #Poisson Home Sofre
        # df_liga['Poisson_GS_H_0'] = poisson.pmf(0, df_liga['Media_GS_H'])
        # df_liga['Poisson_GS_H_0'] = df_liga['Poisson_GS_H_0'].round(4)
        # df_liga['Poisson_GS_H_1'] = poisson.pmf(1, df_liga['Media_GS_H'])
        # df_liga['Poisson_GS_H_1'] = df_liga['Poisson_GS_H_1'].round(4)
        # df_liga['Poisson_GS_H_2'] = poisson.pmf(2, df_liga['Media_GS_H'])
        # df_liga['Poisson_GS_H_2'] = df_liga['Poisson_GS_H_2'].round(4)
        # df_liga['Poisson_GS_H_3'] = poisson.pmf(3, df_liga['Media_GS_H'])
        # df_liga['Poisson_GS_H_3'] = df_liga['Poisson_GS_H_3'].round(4)
        # df_liga['Poisson_GS_H_4'] = poisson.pmf(4, df_liga['Media_GS_H'])
        # df_liga['Poisson_GS_H_4'] = df_liga['Poisson_GS_H_4'].round(4)
        
        # #Poisson Away Sofre
        # df_liga['Poisson_GS_A_0'] = poisson.pmf(0, df_liga['Media_GS_A'])
        # df_liga['Poisson_GS_A_0'] = df_liga['Poisson_GS_A_0'].round(4)
        # df_liga['Poisson_GS_A_1'] = poisson.pmf(1, df_liga['Media_GS_A'])
        # df_liga['Poisson_GS_A_1'] = df_liga['Poisson_GS_A_1'].round(4)
        # df_liga['Poisson_GS_A_2'] = poisson.pmf(2, df_liga['Media_GS_A'])
        # df_liga['Poisson_GS_A_2'] = df_liga['Poisson_GS_A_2'].round(4)
        # df_liga['Poisson_GS_A_3'] = poisson.pmf(3, df_liga['Media_GS_A'])
        # df_liga['Poisson_GS_A_3'] = df_liga['Poisson_GS_A_3'].round(4)
        # df_liga['Poisson_GS_A_4'] = poisson.pmf(4, df_liga['Media_GS_A'])
        # df_liga['Poisson_GS_A_4'] = df_liga['Poisson_GS_A_4'].round(4)
        
        # Primeiro gol marcado e sofrido
        calcular_primeiro_gol(df_liga, "Goals_Minutes_Home", "primeiro_gol_home")
        calcular_primeiro_gol(df_liga, "Goals_Minutes_Away", "primeiro_gol_away")
        
        # Substituir NaN por 0 nas colunas 'primeiro_gol_home' e 'primeiro_gol_away'
        df_liga["primeiro_gol_home"] = df_liga["primeiro_gol_home"].fillna(0)
        df_liga["primeiro_gol_away"] = df_liga["primeiro_gol_away"].fillna(0)
        
        # Média móvel do primeiro gol marcado
        df_liga["Media_primeiro_gol_home"] = (df_liga.groupby("Home")["primeiro_gol_home"]
                                      .rolling(window=n_per, min_periods=min_per)
                                      .mean().reset_index(0, drop=True)).shift(1).round(2)
        df_liga["Media_primeiro_gol_away"] = (df_liga.groupby("Away")["primeiro_gol_away"]
                                      .rolling(window=n_per, min_periods=min_per)
                                      .mean().reset_index(0, drop=True)).shift(1).round(2)
        
        # Média móvel do primeiro gol sofrido
        df_liga["Media_primeiro_gol_home_sofrido"] = (df_liga.groupby("Home")["primeiro_gol_away"]
                                              .rolling(window=n_per, min_periods=min_per)
                                              .mean().reset_index(0, drop=True)).shift(1).round(2)
        df_liga["Media_primeiro_gol_away_sofrido"] = (df_liga.groupby("Away")["primeiro_gol_home"]
                                              .rolling(window=n_per, min_periods=min_per)
                                              .mean().reset_index(0, drop=True)).shift(1).round(2)
        
        # Porcentagem de jogos em que o time marcou primeiro
        # Criando as colunas 'Marcou_Primeiro_Golo_H' e 'Marcou_Primeiro_Golo_A'
        df_liga["Marcou_Primeiro_Golo_H"] = np.where(df_liga["primeiro_gol_home"] < df_liga["primeiro_gol_away"], 1, 0)
        df_liga["Marcou_Primeiro_Golo_A"] = np.where(df_liga["primeiro_gol_home"] > df_liga["primeiro_gol_away"], 1, 0)
        
        # Certificando-se de que valores nulos ou zero na coluna de primeiro gol não contam como tendo marcado o primeiro gol
        df_liga["Marcou_Primeiro_Golo_H"] = np.where(df_liga["primeiro_gol_home"].isnull() | (df_liga["primeiro_gol_home"] == 0), 0, df_liga["Marcou_Primeiro_Golo_H"])
        df_liga["Marcou_Primeiro_Golo_A"] = np.where(df_liga["primeiro_gol_away"].isnull() | (df_liga["primeiro_gol_away"] == 0), 0, df_liga["Marcou_Primeiro_Golo_A"])
        df_liga["Porc_Marcou_Primeiro_Golo_H"] = (df_liga.groupby("Home")["Marcou_Primeiro_Golo_H"]
                                          .rolling(window=n_per, min_periods=min_per)
                                          .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Marcou_Primeiro_Golo_A"] = (df_liga.groupby("Away")["Marcou_Primeiro_Golo_A"]
                                          .rolling(window=n_per, min_periods=min_per)
                                          .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Porcentagem de jogos em que o time marcou primeiro no primeiro tempo
        # Criando as colunas 'Marcou_Primeiro_Golo_H_1P' e 'Marcou_Primeiro_Golo_A_1P'
        df_liga["Marcou_Primeiro_Golo_H_1P"] = np.where((df_liga["primeiro_gol_home"] < df_liga["primeiro_gol_away"]) & (df_liga["primeiro_gol_home"] <= 45), 1, 0)
        df_liga["Marcou_Primeiro_Golo_A_1P"] = np.where((df_liga["primeiro_gol_home"] > df_liga["primeiro_gol_away"]) & (df_liga["primeiro_gol_away"] <= 45), 1, 0)
        
        # Garantir que valores nulos ou valores acima de 45 minutos não sejam considerados
        df_liga["Marcou_Primeiro_Golo_H_1P"] = np.where((df_liga["primeiro_gol_home"].isnull() | (df_liga["primeiro_gol_home"] > 45)), 0, df_liga["Marcou_Primeiro_Golo_H_1P"])
        df_liga["Marcou_Primeiro_Golo_A_1P"] = np.where((df_liga["primeiro_gol_away"].isnull() | (df_liga["primeiro_gol_away"] > 45)), 0, df_liga["Marcou_Primeiro_Golo_A_1P"])
        
        df_liga["Porc_Marcou_Primeiro_Golo_H_1P"] = (df_liga.groupby("Home")["Marcou_Primeiro_Golo_H_1P"]
                                             .rolling(window=n_per, min_periods=min_per)
                                             .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Marcou_Primeiro_Golo_A_1P"] = (df_liga.groupby("Away")["Marcou_Primeiro_Golo_A_1P"]
                                             .rolling(window=n_per, min_periods=min_per)
                                             .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Porcentagem de jogos em que o time sofreu o primeiro gol
        # Criando as colunas 'Sofreu_Primeiro_Golo_H' e 'Sofreu_Primeiro_Golo_A'
        df_liga["Sofreu_Primeiro_Golo_H"] = np.where(df_liga["primeiro_gol_home"] > df_liga["primeiro_gol_away"], 1, 0)
        df_liga["Sofreu_Primeiro_Golo_A"] = np.where(df_liga["primeiro_gol_home"] < df_liga["primeiro_gol_away"], 1, 0)
        
        # Garantindo que valores nulos ou zero na coluna de primeiro gol não sejam considerados como tendo sofrido o primeiro gol
        df_liga["Sofreu_Primeiro_Golo_H"] = np.where(df_liga["primeiro_gol_home"].isnull() | (df_liga["primeiro_gol_home"] == 0), 0, df_liga["Sofreu_Primeiro_Golo_H"])
        df_liga["Sofreu_Primeiro_Golo_A"] = np.where(df_liga["primeiro_gol_away"].isnull() | (df_liga["primeiro_gol_away"] == 0), 0, df_liga["Sofreu_Primeiro_Golo_A"])
        
        df_liga["Porc_Sofreu_Primeiro_Golo_H"] = (df_liga.groupby("Home")["Sofreu_Primeiro_Golo_H"]
                                          .rolling(window=n_per, min_periods=min_per)
                                          .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Sofreu_Primeiro_Golo_A"] = (df_liga.groupby("Away")["Sofreu_Primeiro_Golo_A"]
                                          .rolling(window=n_per, min_periods=min_per)
                                          .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Porcentagem de jogos em que o time sofreu o primeiro gol no primeiro tempo
        # Criando as colunas 'Sofreu_Primeiro_Golo_H_1P' e 'Sofreu_Primeiro_Golo_A_1P'
        df_liga["Sofreu_Primeiro_Golo_H_1P"] = np.where((df_liga["primeiro_gol_home"] > df_liga["primeiro_gol_away"]) & (df_liga["primeiro_gol_home"] <= 45), 1, 0)
        df_liga["Sofreu_Primeiro_Golo_A_1P"] = np.where((df_liga["primeiro_gol_home"] < df_liga["primeiro_gol_away"]) & (df_liga["primeiro_gol_away"] <= 45), 1, 0)
        
        # Garantindo que valores nulos ou gols após os 45 minutos não sejam considerados
        df_liga["Sofreu_Primeiro_Golo_H_1P"] = np.where((df_liga["primeiro_gol_home"].isnull() | (df_liga["primeiro_gol_home"] > 45)), 0, df_liga["Sofreu_Primeiro_Golo_H_1P"])
        df_liga["Sofreu_Primeiro_Golo_A_1P"] = np.where((df_liga["primeiro_gol_away"].isnull() | (df_liga["primeiro_gol_away"] > 45)), 0, df_liga["Sofreu_Primeiro_Golo_A_1P"])
        
        df_liga["Porc_Sofreu_Primeiro_Golo_H_1P"] = (df_liga.groupby("Home")["Sofreu_Primeiro_Golo_H_1P"]
                                             .rolling(window=n_per, min_periods=min_per)
                                             .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Sofreu_Primeiro_Golo_A_1P"] = (df_liga.groupby("Away")["Sofreu_Primeiro_Golo_A_1P"]
                                             .rolling(window=n_per, min_periods=min_per)
                                             .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Porcentagem de jogos com Both Teams To Score (BTTS)
        # Corrigir a coluna 'BTTS' para conter apenas valores numéricos
        df_liga["BTTS"] = np.where((df_liga["FT_Goals_H"] > 0) & (df_liga["FT_Goals_A"] > 0), 1, 0)
        # Garantir que a coluna seja do tipo inteiro
        df_liga["BTTS"] = df_liga["BTTS"].astype(int)
        
        df_liga["Porc_BTTS_Home"] = (df_liga.groupby("Home")["BTTS"]
                             .rolling(window=n_per, min_periods=min_per)
                             .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_BTTS_Away"] = (df_liga.groupby("Away")["BTTS"]
                             .rolling(window=n_per, min_periods=min_per)
                             .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Calcular Over/Under no Primeiro Tempo
        calculate_over05_ht(df_liga)
        calculate_under05_ht(df_liga)
        calculate_over15_ht(df_liga)
        calculate_under15_ht(df_liga)
        
        # Calcular Over/Under no Tempo Total
        calculate_over05_ft(df_liga)
        calculate_under05_ft(df_liga)
        calculate_over15_ft(df_liga)
        calculate_under15_ft(df_liga)
        calculate_over25_ft(df_liga)
        calculate_under25_ft(df_liga)
        
        # Calcular porcentagens Over/Under no Primeiro Tempo com shift aplicado diretamente
        df_liga["Porc_Over05HT_Home"] = (df_liga.groupby("Home")["Over05_HT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over05HT_Away"] = (df_liga.groupby("Away")["Over05_HT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under05HT_Home"] = (df_liga.groupby("Home")["Under05_HT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under05HT_Away"] = (df_liga.groupby("Away")["Under05_HT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over15HT_Home"] = (df_liga.groupby("Home")["Over15_HT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over15HT_Away"] = (df_liga.groupby("Away")["Over15_HT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under15HT_Home"] = (df_liga.groupby("Home")["Under15_HT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under15HT_Away"] = (df_liga.groupby("Away")["Under15_HT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Calcular porcentagens Over/Under no Tempo Total com shift aplicado diretamente
        df_liga["Porc_Over05FT_Home"] = (df_liga.groupby("Home")["Over05_FT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over05FT_Away"] = (df_liga.groupby("Away")["Over05_FT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under05FT_Home"] = (df_liga.groupby("Home")["Under05_FT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under05FT_Away"] = (df_liga.groupby("Away")["Under05_FT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over15FT_Home"] = (df_liga.groupby("Home")["Over15_FT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over15FT_Away"] = (df_liga.groupby("Away")["Over15_FT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under15FT_Home"] = (df_liga.groupby("Home")["Under15_FT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under15FT_Away"] = (df_liga.groupby("Away")["Under15_FT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        df_liga["Porc_Over25FT_Home"] = (df_liga.groupby("Home")["Over25_FT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Over25FT_Away"] = (df_liga.groupby("Away")["Over25_FT"]
                                 .rolling(window=n_per, min_periods=min_per)
                                 .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under25FT_Home"] = (df_liga.groupby("Home")["Under25_FT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Under25FT_Away"] = (df_liga.groupby("Away")["Under25_FT"]
                                  .rolling(window=n_per, min_periods=min_per)
                                  .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Create the columns using apply and lambda functions
        df_liga["Marcou_1_Golo_Min_Home"] = np.where(df_liga["primeiro_gol_home"] != 0, 1, 0)
        df_liga["Marcou_1_Golo_Min_Away"] = np.where(df_liga["primeiro_gol_away"] != 0, 1, 0)
        df_liga["Sofreu_1_Golo_Min_Home"] = np.where(df_liga["primeiro_gol_away"] != 0, 1, 0)
        df_liga["Sofreu_1_Golo_Min_Away"] = np.where(df_liga["primeiro_gol_home"] != 0, 1, 0)
        
        df_liga["Porc_1GM_FT_Home"] = (df_liga.groupby("Home")['Marcou_1_Golo_Min_Home']
                               .rolling(window=n_per, min_periods=min_per)
                               .mean().reset_index(0, drop=True)
                               * 100).shift(1).fillna(0).round(2)
        
        df_liga["Porc_1GM_FT_Away"] = (df_liga.groupby("Away")['Marcou_1_Golo_Min_Away']
                               .rolling(window=n_per, min_periods=min_per)
                               .mean().reset_index(0, drop=True)
                               * 100).shift(1).fillna(0).round(2)
        df_liga["Porc_1GS_FT_Home"] = (df_liga.groupby("Home")['Sofreu_1_Golo_Min_Home']
                               .rolling(window=n_per, min_periods=min_per)
                               .mean().reset_index(0, drop=True)
                               * 100).shift(1).fillna(0).round(2)
        
        df_liga["Porc_1GS_FT_Away"] = (df_liga.groupby("Away")['Sofreu_1_Golo_Min_Away']
                               .rolling(window=n_per, min_periods=min_per)
                               .mean().reset_index(0, drop=True)
                               * 100).shift(1).fillna(0).round(2)
        
        # Calcular porcentagens de vitórias no Primeiro Tempo com shift aplicado diretamente
        # Criando as colunas 'Home_Win_HT' e 'Away_Win_HT' para indicar vitória no primeiro tempo
        df_liga["Home_Win_HT"] = np.where(df_liga["HT_Goals_H"] > df_liga["HT_Goals_A"], 1, 0)
        df_liga["Away_Win_HT"] = np.where(df_liga["HT_Goals_H"] < df_liga["HT_Goals_A"], 1, 0)
        
        df_liga["Porc_Home_Win_HT"] = (df_liga.groupby("Home")["Home_Win_HT"]
                                .rolling(window=n_per, min_periods=min_per)
                                .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Away_Win_HT"] = (df_liga.groupby("Away")["Away_Win_HT"]
                                .rolling(window=n_per, min_periods=min_per)
                                .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Calcular porcentagens de vitórias no Tempo Total com shift aplicado diretamente
        # Criando as colunas 'Home_Win_FT' e 'Away_Win_FT' para indicar vitória no tempo total
        df_liga["Home_Win_FT"] = np.where(df_liga["FT_Goals_H"] > df_liga["FT_Goals_A"], 1, 0)
        df_liga["Away_Win_FT"] = np.where(df_liga["FT_Goals_H"] < df_liga["FT_Goals_A"], 1, 0)
        
        df_liga["Porc_Home_Win_FT"] = (df_liga.groupby("Home")["Home_Win_FT"]
                                .rolling(window=n_per, min_periods=min_per)
                                .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        df_liga["Porc_Away_Win_FT"] = (df_liga.groupby("Away")["Away_Win_FT"]
                                .rolling(window=n_per, min_periods=min_per)
                                .mean().reset_index(0, drop=True) * 100).shift(1).round(2)
        
        # Pesos
        w1, w2, w3, w4, w5 = 2, 0.6, 0.5, 0.4, 0.3
        penalizacao_0x0 = 100  # Penalização para jogos que terminam 0 a 0
        penalizacao_empate = 75  # Penalização para qualquer empate
        
        # Calculando o Power_Ranking_Home
        df_liga["Power_Ranking_Home"] = (
            w1 * df_liga["Value_Ptos_H"] +
            w2 * df_liga["Value_SG_H"] +
            w3 * df_liga["Value_GM_H_1P"] +
            w3 * (df_liga["FT_Goals_H"] - df_liga["HT_Goals_H"]) * (df_liga["FT_Goals_H"] - df_liga["HT_Goals_H"]) -  # Impacto cumulativo dos gols do 2º tempo (marcados)
            w4 * df_liga["Value_GM_A_1P"] -
            w4 * (df_liga["FT_Goals_A"] - df_liga["HT_Goals_A"]) * (df_liga["FT_Goals_A"] - df_liga["HT_Goals_A"]) +   # Impacto cumulativo dos gols do 2º tempo (sofridos)
            w5 * (df_liga["p_H"] - df_liga["p_A"].replace(0, np.nan).fillna(1))
            )
        
        # Aplicando penalizações para jogos com placar final 0x0 e para empates em geral
        df_liga.loc[(df_liga["FT_Goals_H"] == 0) & (df_liga["FT_Goals_A"] == 0), "Power_Ranking_Home"] -= penalizacao_0x0
        df_liga.loc[(df_liga["FT_Goals_H"] == df_liga["FT_Goals_A"]) & (df_liga["FT_Goals_H"] != 0),"Power_Ranking_Home",] -= penalizacao_empate
        
        # Normalização para 0 a 500 para Power_Ranking_Home
        min_rank_home = df_liga["Power_Ranking_Home"].min()
        max_rank_home = df_liga["Power_Ranking_Home"].max()
        df_liga["Power_Ranking_Home"] = (500 * (df_liga["Power_Ranking_Home"] - min_rank_home) / (max_rank_home - min_rank_home))
        df_liga["Power_Ranking_Home"] = df_liga["Power_Ranking_Home"].round(4)
        
        # Calculando o Power_Ranking_Away
        df_liga["Power_Ranking_Away"] = (
            w1 * df_liga["Value_Ptos_A"] +
            w2 * df_liga["Value_SG_A"] +
            w3 * df_liga["Value_GM_A_1P"] +
            w3 * (df_liga["FT_Goals_A"] - df_liga["HT_Goals_A"]) * (df_liga["FT_Goals_A"] - df_liga["HT_Goals_A"]) -  # Impacto cumulativo dos gols do 2º tempo (marcados)
            w4 * df_liga["Value_GM_H_1P"]  -
            w4 * (df_liga["FT_Goals_H"] - df_liga["HT_Goals_H"]) * (df_liga["FT_Goals_H"] - df_liga["HT_Goals_H"]) -  # Impacto cumulativo dos gols do 2º tempo (sofridos)
            w5 * (df_liga["p_A"] - df_liga["p_H"].replace(0, np.nan).fillna(1))
            )
        
        # Aplicando penalizações para jogos com placar final 0x0 e para empates em geral
        df_liga.loc[(df_liga["FT_Goals_A"] == 0) & (df_liga["FT_Goals_H"] == 0), "Power_Ranking_Away"] -= penalizacao_0x0
        df_liga.loc[(df_liga["FT_Goals_A"] == df_liga["FT_Goals_H"]) & (df_liga["FT_Goals_A"] != 0),"Power_Ranking_Away",] -= penalizacao_empate
        
        # Normalização para 0 a 500 para Power_Ranking_Away
        min_rank_away = df_liga["Power_Ranking_Away"].min()
        max_rank_away = df_liga["Power_Ranking_Away"].max()
        df_liga["Power_Ranking_Away"] = (500  * (df_liga["Power_Ranking_Away"] - min_rank_away) / (max_rank_away - min_rank_away))
        df_liga["Power_Ranking_Away"] = df_liga["Power_Ranking_Away"].round(4)
        
        # Média e Desvio Padrão do Power Ranking com Penalização
        df_liga['Med_Power_Ranking_Home'] = df_liga.groupby('Home')['Power_Ranking_Home'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0, drop=True)
        df_liga['Med_Power_Ranking_Home'] = df_liga['Med_Power_Ranking_Home'].round(4)
        df_liga['Med_Power_Ranking_Away'] = df_liga.groupby('Away')['Power_Ranking_Away'].rolling(window=n_per, min_periods=min_per).mean().reset_index(0, drop=True)
        df_liga['Med_Power_Ranking_Away'] = df_liga['Med_Power_Ranking_Away'].round(4)
        
        df_liga['DesvPad_pwr_H'] = df_liga.groupby('Home')['Power_Ranking_Home'].rolling(window=n_per, min_periods=min_per).std().reset_index(0, drop=True)
        df_liga['DesvPad_pwr_H'] = df_liga['DesvPad_pwr_H'].round(4)
        df_liga['DesvPad_pwr_A'] = df_liga.groupby('Away')['Power_Ranking_Away'].rolling(window=n_per, min_periods=min_per).std().reset_index(0, drop=True)
        df_liga['DesvPad_pwr_A'] = df_liga['DesvPad_pwr_A'].round(4)
        df_liga['DesvPad_pwr_H'] = df_liga.groupby('Home')['DesvPad_pwr_H'].shift(1)
        df_liga['DesvPad_pwr_A'] = df_liga.groupby('Away')['DesvPad_pwr_A'].shift(1)
        
        df_liga['CV_pwr_H'] = df_liga['DesvPad_pwr_H'] / df_liga['Med_Power_Ranking_Home']
        df_liga['CV_pwr_H'] = df_liga['CV_pwr_H'].round(4)
        df_liga['CV_pwr_A'] = df_liga['DesvPad_pwr_A'] / df_liga['Med_Power_Ranking_Away']
        df_liga['CV_pwr_A'] = df_liga['CV_pwr_A'].round(4)
        
        colunas_deletar = [
            'Result_FT','Result_HT','Result_Goals','BTTS','Ptos_H','Ptos_A','Value_Ptos_H','Value_Ptos_A','SG_H','SG_A','Value_SG_H','Value_SG_A','Value_GM_H_1P','Value_GM_A_1P',
            'Value_GS_H_1P','Value_GS_A_1P','Value_GM_H','Value_GM_A','Value_GS_H','Value_GS_A','CG_GM_H_01','CG_GM_A_01','CG_GS_H_01','CG_GS_A_01','CG_GM_H_02','CG_GM_A_02',
            'CG_GS_H_02','CG_GS_A_02','RPS_MO','RPS_OV_UN','RPS_BTTS','Power_Ranking_Home','Power_Ranking_Away','DesvPad_Ptos_H','DesvPad_Ptos_A','DesvPad_SG_H','DesvPad_SG_A',
            'DesvPad_GM_H_1P','DesvPad_GM_A_1P','DesvPad_GS_H_1P','DesvPad_GS_A_1P','DesvPad_GM_H','DesvPad_GM_A','DesvPad_GS_H','DesvPad_GS_A','DesvPad_CGM_H_01','DesvPad_CGM_A_01',
            'DesvPad_CGS_H_01','DesvPad_CGS_A_01','DesvPad_CGM_H_02','DesvPad_CGM_A_02','DesvPad_CGS_H_02','DesvPad_CGS_A_02','DesvPad_RPS_MO_H','DesvPad_RPS_MO_A',
            'DesvPad_RPS_OvUn_H','DesvPad_RPS_OvUn_A','DesvPad_RPS_BTTS_H','DesvPad_RPS_BTTS_A','DesvPad_p_H','DesvPad_p_A','DesvPad_pwr_H','DesvPad_pwr_A','primeiro_gol_home',
            'primeiro_gol_away','Marcou_Primeiro_Golo_H','Marcou_Primeiro_Golo_A','Marcou_Primeiro_Golo_H_1P','Marcou_Primeiro_Golo_A_1P','Sofreu_Primeiro_Golo_H','Sofreu_Primeiro_Golo_A',
            'Sofreu_Primeiro_Golo_H_1P','Sofreu_Primeiro_Golo_A_1P','Home_Win_HT','Away_Win_HT','Home_Win_FT','Away_Win_FT','Goals_Minutes_Home','Goals_Minutes_Away','Marcou_1_Golo_Min_Home',
            'Marcou_1_Golo_Min_Away','Sofreu_1_Golo_Min_Home','Sofreu_1_Golo_Min_Away',
            ]
        
        # Filtrando as colunas que realmente existem no dataframe antes de tentar removê-las
        colunas_existentes = [col for col in colunas_deletar if col in df_liga.columns]
        # Removendo as colunas existentes e redefinindo o índice do dataframe
        df_liga.replace(np.inf, np.nan, inplace=True)
        df_liga = df_liga.drop(columns=colunas_existentes, axis=1)
        df_liga = drop_reset_index(df_liga)
        
        df0 = df_liga.copy()
        df0 = df0.reset_index()
        
        df_H = df0 [
            [
                'Home',
                'Media_Ptos_H',
                'CV_Ptos_H',
                'Media_SG_H',
                'CV_SG_H',
                'Media_GM_H_1P',
                'CV_GM_H_1P',
                'Media_GS_H_1P',
                'CV_GS_H_1P',
                'Media_GM_H',
                'CV_GM_H',
                'Media_GS_H',
                'CV_GS_H',
                'Media_CGM_H_01',
                'CV_CGM_H_01',
                'Media_CGS_H_01',
                'CV_CGS_H_01',
                'Media_CGM_H_02',
                'CV_CGM_H_02',
                'Media_CGS_H_02',
                'CV_CGS_H_02',
                'Media_RPS_MO_H',
                'CV_RPS_MO_H',
                'Media_RPS_OvUn_H',
                'CV_RPS_OvUn_H',
                'Media_RPS_BTTS_H',
                'CV_RPS_BTTS_H',
                'Media_p_H',
                'CV_p_H',
                'Media_primeiro_gol_home',
                'Media_primeiro_gol_home_sofrido',
                'Porc_Marcou_Primeiro_Golo_H',
                'Porc_Marcou_Primeiro_Golo_H_1P',
                'Porc_Sofreu_Primeiro_Golo_H',
                'Porc_Sofreu_Primeiro_Golo_H_1P',
                'Porc_BTTS_Home',
                'Porc_Over05HT_Home',
                'Porc_Under05HT_Home',
                'Porc_Over15HT_Home',
                'Porc_Under15HT_Home',
                'Porc_Over05FT_Home',
                'Porc_Under05FT_Home',
                'Porc_Over15FT_Home',
                'Porc_Under15FT_Home',
                'Porc_Over25FT_Home',
                'Porc_Under25FT_Home',
                'Porc_Home_Win_HT',
                'Porc_Home_Win_FT',
                'Porc_1GM_FT_Home',
                'Porc_1GS_FT_Home',
                'Med_Power_Ranking_Home',
                'CV_pwr_H',
                ]
            ]
        
        df_A = df0[
            [
                'Away',
                'Media_Ptos_A',
                'CV_Ptos_A',
                'Media_SG_A',
                'CV_SG_A',
                'Media_GM_A_1P',
                'CV_GM_A_1P',
                'Media_GS_A_1P',
                'CV_GS_A_1P',
                'Media_GM_A',
                'CV_GM_A',
                'Media_GS_A',
                'CV_GS_A',
                'Media_CGM_A_01',
                'CV_CGM_A_01',
                'Media_CGS_A_01',
                'CV_CGS_A_01',
                'Media_CGM_A_02',
                'CV_CGM_A_02',
                'Media_CGS_A_02',
                'CV_CGS_A_02',
                'Media_RPS_MO_A',
                'CV_RPS_MO_A',
                'Media_RPS_OvUn_A',
                'CV_RPS_OvUn_A',
                'Media_RPS_BTTS_A',
                'CV_RPS_BTTS_A',
                'Media_p_A',
                'CV_p_A',
                'Media_primeiro_gol_away',
                'Media_primeiro_gol_away_sofrido',
                'Porc_Marcou_Primeiro_Golo_A',
                'Porc_Marcou_Primeiro_Golo_A_1P',
                'Porc_Sofreu_Primeiro_Golo_A',
                'Porc_Sofreu_Primeiro_Golo_A_1P',
                'Porc_BTTS_Away',
                'Porc_Over05HT_Away',
                'Porc_Under05HT_Away',
                'Porc_Over15HT_Away',
                'Porc_Under15HT_Away',
                'Porc_Over05FT_Away',
                'Porc_Under05FT_Away',
                'Porc_Over15FT_Away',
                'Porc_Under15FT_Away',
                'Porc_Over25FT_Away',
                'Porc_Under25FT_Away',
                'Porc_Away_Win_HT',
                'Porc_Away_Win_FT',
                'Porc_1GM_FT_Away',
                'Porc_1GS_FT_Away',
                'Med_Power_Ranking_Away',
                'CV_pwr_A',
                ]
            ]
        
        jogo_lista = []
        
        for index, row in Jogos_do_Dia.iterrows():
            League = row["League"]
            Date = row["Date"]
            Time = row["Time"]
            home = row["Home"]
            away = row["Away"]
            FT_Odd_H = row["FT_Odd_H"]
            FT_Odd_D = row["FT_Odd_D"]
            FT_Odd_A = row["FT_Odd_A"]
            HT_Odd_Ov05 = row["HT_Odd_Over05"]
            HT_Odd_Un05 = row["HT_Odd_Under05"]
            FT_Odd_Ov15 = row["FT_Odd_Over15"]
            FT_Odd_Un15 = row["FT_Odd_Under15"]
            FT_Odd_Ov25 = row["FT_Odd_Over25"]
            FT_Odd_Un25 = row["FT_Odd_Under25"]
            FT_Odd_BTTS_Y = row["Odd_BTTS_Yes"]
            FT_Odd_BTTS_N = row["Odd_BTTS_No"]
            
            # Probabilidades calculadas e arredondadas
            prob_H = round(1 / FT_Odd_H, 4) if FT_Odd_H != 0 else None
            prob_D = round(1 / FT_Odd_D, 4) if FT_Odd_D != 0 else None
            prob_A = round(1 / FT_Odd_A, 4) if FT_Odd_A != 0 else None
            prob_Ov05_HT = round(1 / HT_Odd_Ov05, 4) if HT_Odd_Ov05 != 0 else None
            prob_Un05_HT = round(1 / HT_Odd_Un05, 4) if HT_Odd_Un05 != 0 else None
            prob_Ov15_FT = round(1 / FT_Odd_Ov15, 4) if FT_Odd_Ov15 != 0 else None
            prob_Un15_FT = round(1 / FT_Odd_Un15, 4) if FT_Odd_Un15 != 0 else None
            prob_Ov25_FT = round(1 / FT_Odd_Ov25, 4) if FT_Odd_Ov25 != 0 else None
            prob_Un25_FT = round(1 / FT_Odd_Un25, 4) if FT_Odd_Un25 != 0 else None
            prob_BTTS_Y_FT = round(1 / FT_Odd_BTTS_Y, 4) if FT_Odd_BTTS_Y != 0 else None
            prob_BTTS_N_FT = round(1 / FT_Odd_BTTS_N, 4) if FT_Odd_BTTS_N != 0 else None
            
            # Proporção entre as Odds
            H_D = round(FT_Odd_H / FT_Odd_D, 4) if FT_Odd_D != 0 else None
            H_A = round(FT_Odd_H / FT_Odd_A, 4) if FT_Odd_A != 0 else None
            D_H = round(FT_Odd_D / FT_Odd_H, 4) if FT_Odd_H != 0 else None
            D_A = round(FT_Odd_D / FT_Odd_A, 4) if FT_Odd_A != 0 else None
            A_H = round(FT_Odd_A / FT_Odd_H, 4) if FT_Odd_H != 0 else None
            A_D = round(FT_Odd_A / FT_Odd_D, 4) if FT_Odd_D != 0 else None
            
            # Diferença Absoluta entre as Odds
            DifAbs_HomeAway = round(np.abs(FT_Odd_H - FT_Odd_A), 4)
            DifAbs_HomeDraw = round(np.abs(FT_Odd_H - FT_Odd_D), 4)
            DifAbs_DrawAway = round(np.abs(FT_Odd_D - FT_Odd_A), 4)
            
            # Ângulo de Disparidade entre as Odds
            Angle_HomeAway = round(np.degrees(np.arctan((FT_Odd_A - FT_Odd_H) / 2)), 4)
            Angle_HomeDraw = round(np.degrees(np.arctan((FT_Odd_D - FT_Odd_H) / 2)), 4)
            Angle_DrawAway = round(np.degrees(np.arctan((FT_Odd_A - FT_Odd_D) / 2)), 4)
            
            # Diferenças Percentuais entre as Odds
            DifPer_HomeAway = round(np.abs((FT_Odd_H - FT_Odd_A)) / FT_Odd_A, 4) if FT_Odd_A != 0 else None    
            DifPer_HomeDraw = round(np.abs((FT_Odd_H - FT_Odd_D)) / FT_Odd_D, 4) if FT_Odd_D != 0 else None
            DifPer_DrawAway = round(np.abs((FT_Odd_D - FT_Odd_A)) / FT_Odd_A, 4) if FT_Odd_A != 0 else None
            
            try:
                df1 = df_H[df_H.Home == home].tail(1)
                df2 = df_A[df_A.Away == away].tail(1)
                if not df1.empty:
                    Med_Ptos_Home = round(df1["Media_Ptos_H"].iloc[0], 4) if pd.notna(df1["Media_Ptos_H"].iloc[0]) else None
                    Cv_Med_Ptos_Home = round(df1["CV_Ptos_H"].iloc[0], 4) if pd.notna(df1["CV_Ptos_H"].iloc[0]) else None
                    Med_SG_Home = round(df1["Media_SG_H"].iloc[0], 4) if pd.notna(df1["Media_SG_H"].iloc[0]) else None
                    Cv_Med_SG_Home = round(df1["CV_SG_H"].iloc[0], 4) if pd.notna(df1["CV_SG_H"].iloc[0]) else None
                    Med_GM_Home_1P = round(df1["Media_GM_H_1P"].iloc[0], 4) if pd.notna(df1["Media_GM_H_1P"].iloc[0]) else None
                    Cv_Med_GM_Home_1P = round(df1["CV_GM_H_1P"].iloc[0], 4) if pd.notna(df1["CV_GM_H_1P"].iloc[0]) else None
                    Med_GS_Home_1P = round(df1["Media_GS_H_1P"].iloc[0], 4) if pd.notna(df1["Media_GS_H_1P"].iloc[0]) else None
                    Cv_Med_GS_Home_1P = round(df1["CV_GS_H_1P"].iloc[0], 4) if pd.notna(df1["CV_GS_H_1P"].iloc[0]) else None
                    Med_GM_Home = round(df1["Media_GM_H"].iloc[0], 4) if pd.notna(df1["Media_GM_H"].iloc[0]) else None
                    Cv_Med_GM_Home = round(df1["CV_GM_H"].iloc[0], 4) if pd.notna(df1["CV_GM_H"].iloc[0]) else None
                    Med_GS_Home = round(df1["Media_GS_H"].iloc[0], 4) if pd.notna(df1["Media_GS_H"].iloc[0]) else None
                    Cv_Med_GS_Home = round(df1["CV_GS_H"].iloc[0], 4) if pd.notna(df1["CV_GS_H"].iloc[0]) else None
                    Med_CGM01_Home = round(df1["Media_CGM_H_01"].iloc[0], 4) if pd.notna(df1["Media_CGM_H_01"].iloc[0]) else None
                    Cv_Med_CGM01_Home = round(df1["CV_CGM_H_01"].iloc[0], 4) if pd.notna(df1["CV_CGM_H_01"].iloc[0]) else None
                    Med_CGS01_Home = round(df1["Media_CGS_H_01"].iloc[0], 4) if pd.notna(df1["Media_CGS_H_01"].iloc[0]) else None
                    Cv_Med_CGS01_Home = round(df1["CV_CGS_H_01"].iloc[0], 4) if pd.notna(df1["CV_CGS_H_01"].iloc[0]) else None
                    Med_CGM02_Home = round(df1["Media_CGM_H_02"].iloc[0], 4) if pd.notna(df1["Media_CGM_H_02"].iloc[0]) else None
                    Cv_Med_CGM02_Home = round(df1["CV_CGM_H_02"].iloc[0], 4) if pd.notna(df1["CV_CGM_H_02"].iloc[0]) else None
                    Med_CGS02_Home = round(df1["Media_CGS_H_02"].iloc[0], 4) if pd.notna(df1["Media_CGS_H_02"].iloc[0]) else None
                    Cv_Med_CGS02_Home = round(df1["CV_CGS_H_02"].iloc[0], 4) if pd.notna(df1["CV_CGS_H_02"].iloc[0]) else None
                    Med_RPS_MO_Home = round(df1["Media_RPS_MO_H"].iloc[0], 4) if pd.notna(df1["Media_RPS_MO_H"].iloc[0]) else None
                    Cv_Med_RPS_MO_Home = round(df1["CV_RPS_MO_H"].iloc[0], 4) if pd.notna(df1["CV_RPS_MO_H"].iloc[0]) else None
                    Med_RPS_OvUn_Home = round(df1["Media_RPS_OvUn_H"].iloc[0], 4) if pd.notna(df1["Media_RPS_OvUn_H"].iloc[0]) else None
                    Cv_Med_RPS_OvUn_Home = round(df1["CV_RPS_OvUn_H"].iloc[0], 4) if pd.notna(df1["CV_RPS_OvUn_H"].iloc[0]) else None
                    Med_RPS_BTTS_Home = round(df1["Media_RPS_BTTS_H"].iloc[0], 4) if pd.notna(df1["Media_RPS_BTTS_H"].iloc[0]) else None
                    Cv_Med_RPS_BTTS_Home = round(df1["CV_RPS_BTTS_H"].iloc[0], 4) if pd.notna(df1["CV_RPS_BTTS_H"].iloc[0]) else None
                    Med_prob_Home = round(df1["Media_p_H"].iloc[0], 4) if pd.notna(df1["Media_p_H"].iloc[0]) else None
                    Cv_Med_prob_Home = round(df1["CV_p_H"].iloc[0], 4) if pd.notna(df1["CV_p_H"].iloc[0]) else None
                    Med_Primeiro_Golo_Marcado_Home = round(df1["Media_primeiro_gol_home"].iloc[0], 4) if pd.notna(df1["Media_primeiro_gol_home"].iloc[0]) else None
                    Med_Primeiro_Golo_Sofrido_Home = round(df1["Media_primeiro_gol_home_sofrido"].iloc[0], 4) if pd.notna(df1["Media_primeiro_gol_home_sofrido"].iloc[0]) else None
                    Porc_Marcou_Primeiro_Home_FT = round(df1["Porc_Marcou_Primeiro_Golo_H"].iloc[0], 4) if pd.notna(df1["Porc_Marcou_Primeiro_Golo_H"].iloc[0]) else None
                    Porc_Marcou_Primeiro_Home_HT = round(df1["Porc_Marcou_Primeiro_Golo_H_1P"].iloc[0], 4) if pd.notna(df1["Porc_Marcou_Primeiro_Golo_H_1P"].iloc[0]) else None
                    Porc_Sofreu_Primeiro_Home_FT = round(df1["Porc_Sofreu_Primeiro_Golo_H"].iloc[0], 4) if pd.notna(df1["Porc_Sofreu_Primeiro_Golo_H"].iloc[0]) else None
                    Porc_Sofreu_Primeiro_Home_HT = round(df1["Porc_Sofreu_Primeiro_Golo_H_1P"].iloc[0], 4) if pd.notna(df1["Porc_Sofreu_Primeiro_Golo_H_1P"].iloc[0]) else None
                    Porc_BTTS_Y_Home = round(df1["Porc_BTTS_Home"].iloc[0], 4) if pd.notna(df1["Porc_BTTS_Home"].iloc[0]) else None
                    Porc_Ov05_HT_Home = round(df1["Porc_Over05HT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Over05HT_Home"].iloc[0]) else None
                    Porc_Un05_HT_Home = round(df1["Porc_Under05HT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Under05HT_Home"].iloc[0]) else None
                    Porc_Ov15_HT_Home = round(df1["Porc_Over15HT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Over15HT_Home"].iloc[0]) else None
                    Porc_Un15_HT_Home = round(df1["Porc_Under15HT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Under15HT_Home"].iloc[0]) else None
                    Porc_Ov05_FT_Home = round(df1["Porc_Over05FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Over05FT_Home"].iloc[0]) else None
                    Porc_Un05_FT_Home = round(df1["Porc_Under05FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Under05FT_Home"].iloc[0]) else None            
                    Porc_Ov15_FT_Home = round(df1["Porc_Over15FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Over15FT_Home"].iloc[0]) else None
                    Porc_Un15_FT_Home = round(df1["Porc_Under15FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Under15FT_Home"].iloc[0]) else None
                    Porc_Ov25_FT_Home = round(df1["Porc_Over25FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Over25FT_Home"].iloc[0]) else None
                    Porc_Un25_FT_Home = round(df1["Porc_Under25FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_Under25FT_Home"].iloc[0]) else None
                    Porc_Win_HT_Home = round(df1["Porc_Home_Win_HT"].iloc[0], 4) if pd.notna(df1["Porc_Home_Win_HT"].iloc[0]) else None
                    Porc_Win_FT_Home = round(df1["Porc_Home_Win_FT"].iloc[0], 4) if pd.notna(df1["Porc_Home_Win_FT"].iloc[0]) else None
                    Porc_Score_FT_Home = round(df1["Porc_1GM_FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_1GM_FT_Home"].iloc[0]) else None
                    Porc_Took_FT_Home = round(df1["Porc_1GS_FT_Home"].iloc[0], 4) if pd.notna(df1["Porc_1GS_FT_Home"].iloc[0]) else None
                    Med_Power_Ranking_Home = round(df1["Med_Power_Ranking_Home"].iloc[0], 4) if pd.notna(df1["Med_Power_Ranking_Home"].iloc[0]) else None
                    Cv_Med_Power_Ranking_Home = round(df1["CV_pwr_H"].iloc[0], 4) if pd.notna(df1["CV_pwr_H"].iloc[0]) else None
                    
                else:
                    Med_Ptos_Home, Cv_Med_Ptos_Home = [None] * 2
                    Med_SG_Home, Cv_Med_SG_Home = [None] * 2
                    Med_GM_Home_1P, Cv_Med_GM_Home_1P = [None] * 2
                    Med_GS_Home_1P, Cv_Med_GS_Home_1P = [None] * 2
                    Med_GM_Home, Cv_Med_GM_Home = [None] * 2
                    Med_GS_Home, Cv_Med_GS_Home = [None] * 2
                    Med_CGM01_Home, Cv_Med_CGM01_Home = [None] * 2
                    Med_CGS01_Home, Cv_Med_CGS01_Home = [None] * 2
                    Med_CGM02_Home, Cv_Med_CGM02_Home = [None] * 2
                    Med_CGS02_Home, Cv_Med_CGS02_Home = [None] * 2
                    Med_RPS_MO_Home, Cv_Med_RPS_MO_Home = [None] * 2
                    Med_RPS_OvUn_Home, Cv_Med_RPS_OvUn_Home = [None] * 2
                    Med_RPS_BTTS_Home, Cv_Med_RPS_BTTS_Home = [None] * 2
                    Med_prob_Home, Cv_Med_prob_Home = [None] * 2
                    Med_Primeiro_Golo_Marcado_Home, Med_Primeiro_Golo_Sofrido_Home = [None] * 2
                    Porc_Marcou_Primeiro_Home_FT, Porc_Marcou_Primeiro_Home_HT = [None] * 2
                    Porc_Sofreu_Primeiro_Home_FT, Porc_Sofreu_Primeiro_Home_HT = [None] * 2
                    Porc_BTTS_Y_Home, Porc_Ov05_HT_Home = [None] * 2
                    Porc_Un05_HT_Home, Porc_Ov15_HT_Home = [None] * 2
                    Porc_Un15_HT_Home, Porc_Ov15_FT_Home = [None] * 2
                    Porc_Ov05_FT_Home, Porc_Un05_FT_Home = [None] * 2
                    Porc_Un15_FT_Home, Porc_Ov25_FT_Home = [None] * 2
                    Porc_Un25_FT_Home, Porc_Win_HT_Home = [None] * 2
                    Porc_Score_FT_Home, Porc_Took_FT_Home = [None] * 2
                    Porc_Win_FT_Home, Med_Power_Ranking_Home, Cv_Med_Power_Ranking_Home = [None] * 3
                    
                    if not df2.empty:
                        Med_Ptos_Away = round(df2["Media_Ptos_A"].iloc[0], 4) if pd.notna(df2["Media_Ptos_A"].iloc[0]) else None
                        Cv_Med_Ptos_Away = round(df2["CV_Ptos_A"].iloc[0], 4) if pd.notna(df2["CV_Ptos_A"].iloc[0]) else None
                        Med_SG_Away = round(df2["Media_SG_A"].iloc[0], 4) if pd.notna(df2["Media_SG_A"].iloc[0]) else None
                        Cv_Med_SG_Away = round(df2["CV_SG_A"].iloc[0], 4) if pd.notna(df2["CV_SG_A"].iloc[0]) else None
                        Med_GM_Away_1P = round(df2["Media_GM_A_1P"].iloc[0], 4) if pd.notna(df2["Media_GM_A_1P"].iloc[0]) else None
                        Cv_Med_GM_Away_1P = round(df2["CV_GM_A_1P"].iloc[0], 4) if pd.notna(df2["CV_GM_A_1P"].iloc[0]) else None
                        Med_GS_Away_1P = round(df2["Media_GS_A_1P"].iloc[0], 4) if pd.notna(df2["Media_GS_A_1P"].iloc[0]) else None
                        Cv_Med_GS_Away_1P = round(df2["CV_GS_A_1P"].iloc[0], 4) if pd.notna(df2["CV_GS_A_1P"].iloc[0]) else None
                        Med_GM_Away = round(df2["Media_GM_A"].iloc[0], 4) if pd.notna(df2["Media_GM_A"].iloc[0]) else None
                        Cv_Med_GM_Away = round(df2["CV_GM_A"].iloc[0], 4) if pd.notna(df2["CV_GM_A"].iloc[0]) else None
                        Med_GS_Away = round(df2["Media_GS_A"].iloc[0], 4) if pd.notna(df2["Media_GS_A"].iloc[0]) else None
                        Cv_Med_GS_Away = round(df2["CV_GS_A"].iloc[0], 4) if pd.notna(df2["CV_GS_A"].iloc[0]) else None
                        Med_CGM01_Away = round(df2["Media_CGM_A_01"].iloc[0], 4) if pd.notna(df2["Media_CGM_A_01"].iloc[0]) else None
                        Cv_Med_CGM01_Away = round(df2["CV_CGM_A_01"].iloc[0], 4) if pd.notna(df2["CV_CGM_A_01"].iloc[0]) else None
                        Med_CGS01_Away = round(df2["Media_CGS_A_01"].iloc[0], 4) if pd.notna(df2["Media_CGS_A_01"].iloc[0]) else None
                        Cv_Med_CGS01_Away = round(df2["CV_CGS_A_01"].iloc[0], 4) if pd.notna(df2["CV_CGS_A_01"].iloc[0]) else None
                        Med_CGM02_Away = round(df2["Media_CGM_A_02"].iloc[0], 4) if pd.notna(df2["Media_CGM_A_02"].iloc[0]) else None
                        Cv_Med_CGM02_Away = round(df2["CV_CGM_A_02"].iloc[0], 4) if pd.notna(df2["CV_CGM_A_02"].iloc[0]) else None
                        Med_CGS02_Away = round(df2["Media_CGS_A_02"].iloc[0], 4) if pd.notna(df2["Media_CGS_A_02"].iloc[0]) else None
                        v_Med_CGS02_Away = round(df2["CV_CGS_A_02"].iloc[0], 4) if pd.notna(df2["CV_CGS_A_02"].iloc[0]) else None
                        Med_RPS_MO_Away = round(df2["Media_RPS_MO_A"].iloc[0], 4) if pd.notna(df2["Media_RPS_MO_A"].iloc[0]) else None
                        Cv_Med_RPS_MO_Away = round(df2["CV_RPS_MO_A"].iloc[0], 4) if pd.notna(df2["CV_RPS_MO_A"].iloc[0]) else None
                        Med_RPS_OvUn_Away = round(df2["Media_RPS_OvUn_A"].iloc[0], 4) if pd.notna(df2["Media_RPS_OvUn_A"].iloc[0]) else None
                        Cv_Med_RPS_OvUn_Away = round(df2["CV_RPS_OvUn_A"].iloc[0], 4) if pd.notna(df2["CV_RPS_OvUn_A"].iloc[0]) else None
                        Med_RPS_BTTS_Away = round(df2["Media_RPS_BTTS_A"].iloc[0], 4) if pd.notna(df2["Media_RPS_BTTS_A"].iloc[0]) else None
                        Cv_Med_RPS_BTTS_Away = round(df2["CV_RPS_BTTS_A"].iloc[0], 4) if pd.notna(df2["CV_RPS_BTTS_A"].iloc[0]) else None
                        Med_prob_Away = round(df2["Media_p_A"].iloc[0], 4) if pd.notna(df2["Media_p_A"].iloc[0]) else None
                        Cv_Med_prob_Away = round(df2["CV_p_A"].iloc[0], 4) if pd.notna(df2["CV_p_A"].iloc[0]) else None
                        Med_Primeiro_Golo_Marcado_Away = round(df2["Media_primeiro_gol_away"].iloc[0], 4) if pd.notna(df2["Media_primeiro_gol_away"].iloc[0]) else None
                        Med_Primeiro_Golo_Sofrido_Away = round(df2["Media_primeiro_gol_away_sofrido"].iloc[0], 4) if pd.notna(df2["Media_primeiro_gol_away_sofrido"].iloc[0]) else None
                        Porc_Marcou_Primeiro_Away_FT = round(df2["Porc_Marcou_Primeiro_Golo_A"].iloc[0], 4) if pd.notna(df2["Porc_Marcou_Primeiro_Golo_A"].iloc[0]) else None
                        Porc_Marcou_Primeiro_Away_HT = round(df2["Porc_Marcou_Primeiro_Golo_A_1P"].iloc[0], 4) if pd.notna(df2["Porc_Marcou_Primeiro_Golo_A_1P"].iloc[0]) else None
                        Porc_Sofreu_Primeiro_Away_FT = round(df2["Porc_Sofreu_Primeiro_Golo_A"].iloc[0], 4) if pd.notna(df2["Porc_Sofreu_Primeiro_Golo_A"].iloc[0]) else None
                        Porc_Sofreu_Primeiro_Away_HT = round(df2["Porc_Sofreu_Primeiro_Golo_A_1P"].iloc[0], 4) if pd.notna(df2["Porc_Sofreu_Primeiro_Golo_A_1P"].iloc[0]) else None
                        Porc_BTTS_Y_Away = round(df2["Porc_BTTS_Away"].iloc[0], 4) if pd.notna(df2["Porc_BTTS_Away"].iloc[0]) else None
                        Porc_Ov05_HT_Away = round(df2["Porc_Over05HT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Over05HT_Away"].iloc[0]) else None
                        Porc_Un05_HT_Away = round(df2["Porc_Under05HT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Under05HT_Away"].iloc[0]) else None
                        Porc_Ov15_HT_Away = round(df2["Porc_Over15HT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Over15HT_Away"].iloc[0]) else None
                        Porc_Un15_HT_Away = round(df2["Porc_Under15HT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Under15HT_Away"].iloc[0]) else None
                        Porc_Ov05_FT_Away = round(df2["Porc_Over05FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Over05FT_Away"].iloc[0]) else None
                        Porc_Un05_FT_Away = round(df2["Porc_Under05FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Under05FT_Away"].iloc[0]) else None            
                        Porc_Ov15_FT_Away = round(df2["Porc_Over15FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Over15FT_Away"].iloc[0]) else None
                        Porc_Un15_FT_Away = round(df2["Porc_Under15FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Under15FT_Away"].iloc[0]) else None
                        Porc_Ov25_FT_Away = round(df2["Porc_Over25FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Over25FT_Away"].iloc[0]) else None
                        Porc_Un25_FT_Away = round(df2["Porc_Under25FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_Under25FT_Away"].iloc[0]) else None
                        Porc_Win_HT_Away = round(df2["Porc_Away_Win_HT"].iloc[0], 4) if pd.notna(df2["Porc_Away_Win_HT"].iloc[0]) else None
                        Porc_Win_FT_Away = round(df2["Porc_Away_Win_FT"].iloc[0], 4) if pd.notna(df2["Porc_Away_Win_FT"].iloc[0]) else None
                        Porc_Score_FT_Away = round(df2["Porc_1GM_FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_1GM_FT_Away"].iloc[0]) else None
                        Porc_Took_FT_Away = round(df2["Porc_1GS_FT_Away"].iloc[0], 4) if pd.notna(df2["Porc_1GS_FT_Away"].iloc[0]) else None
                        Med_Power_Ranking_Away = round(df2["Med_Power_Ranking_Away"].iloc[0], 4) if pd.notna(df2["Med_Power_Ranking_Away"].iloc[0]) else None
                        Cv_Med_Power_Ranking_Away = round(df2["CV_pwr_A"].iloc[0], 4) if pd.notna(df2["CV_pwr_A"].iloc[0]) else None
                        
                    else:
                        Med_Ptos_Away, Cv_Med_Ptos_Away = [None] * 2
                        Med_SG_Away, Cv_Med_SG_Away = [None] * 2
                        Med_GM_Away_1P, Cv_Med_GM_Away_1P = [None] * 2
                        Med_GS_Away_1P, Cv_Med_GS_Away_1P = [None] * 2
                        Med_GM_Away, Cv_Med_GM_Away = [None] * 2
                        Med_GS_Away, Cv_Med_GS_Away = [None] * 2
                        Med_CGM01_Away, Cv_Med_CGM01_Away = [None] * 2
                        Med_CGS01_Away, Cv_Med_CGS01_Away = [None] * 2
                        Med_CGM02_Away, Cv_Med_CGM02_Away = [None] * 2
                        Med_CGS02_Away, Cv_Med_CGS02_Away = [None] * 2
                        Med_RPS_MO_Away, Cv_Med_RPS_MO_Away = [None] * 2
                        Med_RPS_OvUn_Away, Cv_Med_RPS_OvUn_Away = [None] * 2
                        Med_RPS_BTTS_Away, Cv_Med_RPS_BTTS_Away = [None] * 2
                        Med_prob_Away, Cv_Med_prob_Away = [None] * 2
                        Med_Primeiro_Golo_Marcado_Away, Med_Primeiro_Golo_Sofrido_Away = [None] * 2
                        Porc_Marcou_Primeiro_Away_FT, Porc_Marcou_Primeiro_Away_HT = [None] * 2
                        Porc_Sofreu_Primeiro_Away_FT, Porc_Sofreu_Primeiro_Away_HT = [None] * 2
                        Porc_BTTS_Y_Away, Porc_Ov05_HT_Away = [None] * 2
                        Porc_Un05_HT_Away, Porc_Ov15_HT_Away = [None] * 2
                        Porc_Un15_HT_Away, Porc_Ov15_FT_Away = [None] * 2
                        Porc_Ov05_FT_Away, Porc_Un05_FT_Away = [None] * 2
                        Porc_Un15_FT_Away, Porc_Ov25_FT_Away = [None] * 2
                        Porc_Un25_FT_Away, Porc_Win_HT_Away = [None] * 2
                        Porc_Score_FT_Away, Porc_Took_FT_Away = [None] * 2
                        Porc_Win_FT_Away, Med_Power_Ranking_Away, Cv_Med_Power_Ranking_Away = [None] * 3
                        
                        
                        #Ordem da Colunas do Dataframe
                        jogo = {
                            "League" : League,
                            "Date" : Date,
                            "Time" : Time,
                            "Home" : home,
                            "Away" : away,
                            "FT_Odd_H" : FT_Odd_H,
                            "FT_Odd_D" : FT_Odd_D,
                            "FT_Odd_A" : FT_Odd_A,
                            "HT_Odd_Ov05": HT_Odd_Ov05,
                            "HT_Odd_Un05" : HT_Odd_Un05,
                            "FT_Odd_Ov15" : FT_Odd_Ov15,
                            "FT_Odd_Un15" : FT_Odd_Un15,
                            "FT_Odd_Ov25" : FT_Odd_Ov25,
                            "FT_Odd_Un25" : FT_Odd_Un25,
                            "FT_Odd_BTTS_Y" : FT_Odd_BTTS_Y,
                            "FT_Odd_BTTS_N" : FT_Odd_BTTS_N,
                            "Prob_H" : prob_H,
                            "Prob_D" : prob_D,
                            "Prob_A" :prob_A,
                            "Prob_Ov05_HT" : prob_Ov05_HT,
                            "Prob_Un05_HT" : prob_Un05_HT,
                            "Prob_Ov15_FT" : prob_Ov15_FT,
                            "Prob_Un15_FT" : prob_Un15_FT,
                            "Prob_Ov25_FT" : prob_Ov25_FT,
                            "Prob_Un25_FT" : prob_Un25_FT,
                            "Prob_BTTS_Y_FT" : prob_BTTS_Y_FT,
                            "Prob_BTTS_N_FT" : prob_BTTS_N_FT,
                            "H_D" : H_D,
                            "H_A" : H_A,
                            "D_H" : D_H,
                            "D_A" : D_A,
                            "A_H" : A_H,
                            "A_D" : A_D,
                            "Dif_Abs_HomeAway" : DifAbs_HomeAway,
                            "Dif_Abs_HomeDraw" : DifAbs_HomeDraw,
                            "Dif_Abs_DrawAway" : DifAbs_DrawAway,
                            "Angle_HomeAway": Angle_HomeAway,
                            "Angle_HomeDraw" : Angle_HomeDraw,
                            "Angle_DrawAway" : Angle_DrawAway,
                            "Dif_Perc_HomeAway" : DifPer_HomeAway,
                            "Dif_Perc_HomeDraw" : DifPer_HomeDraw,
                            "Dif_Perc_DrawAway" : DifPer_DrawAway,
                            "Media_Ptos_Home" : Med_Ptos_Home,
                            "CV_Ptos_Home" : Cv_Med_Ptos_Home,
                            "Media_Ptos_Away" : Med_Ptos_Away,
                            "CV_Ptos_Away" : Cv_Med_Ptos_Away,
                            "Media_SG_Home" : Med_SG_Home,
                            "CV_SG_Home" : Cv_Med_SG_Home,
                            "Media_SG_Away" : Med_SG_Away,
                            "CV_SG_Away" : Cv_Med_SG_Away,
                            "Media_GM_Home_1P" : Med_GM_Home_1P,
                            "CV_GM_Home_1P" : Cv_Med_GM_Home_1P,
                            "Media_GM_Away_1P" : Med_GM_Away_1P,
                            "CV_GM_Away_1P" : Cv_Med_GM_Away_1P,
                            "Media_GS_Home_1P" : Med_GS_Home_1P,
                            "CV_GS_Home_1P" : Cv_Med_GS_Home_1P,
                            "Media_GS_Away_1P" : Med_GS_Away_1P,
                            "CV_GS_Away_1P" : Cv_Med_GS_Away_1P,
                            "Media_GM_Home" : Med_GM_Home,
                            "CV_GM_Home" : Cv_Med_GM_Home,
                            "Media_GM_Away" : Med_GM_Away,
                            "CV_GM_Away" : Cv_Med_GM_Away,
                            "Media_GS_Home" : Med_GS_Home,
                            "CV_GS_Home" : Cv_Med_GS_Home,
                            "Media_GS_Away" : Med_GS_Away,
                            "CV_GS_Away" : Cv_Med_GS_Away,
                            "Media_CGM_Home_01" : Med_CGM01_Home,
                            "CV_CGM_Home_01" : Cv_Med_CGM01_Home,
                            "Media_CGM_Away_01" : Med_CGM01_Away,
                            "CV_CGM_Away_01" : Cv_Med_CGM01_Away,
                            "Media_CGS_Home_01" : Med_CGS01_Home,
                            "CV_CGS_Home_01" : Cv_Med_CGS01_Home,
                            "Media_CGS_Away_01" : Med_CGS01_Away,
                            "CV_CGS_Away_01" : Cv_Med_CGS01_Away,
                            "Media_CGM_Home_02" : Med_CGM02_Home,
                            "CV_CGM_Home_02" : Cv_Med_CGM02_Home,
                            "Media_CGM_Away_02" : Med_CGM02_Away,
                            "CV_CGM_Away_02" : Cv_Med_CGM02_Away,
                            "Media_CGS_Home_02" : Med_CGS02_Home,
                            "CV_CGS_Home_02" : Cv_Med_CGS02_Home,
                            "Media_CGS_Away_02" : Med_CGS02_Away,
                            "CV_CGS_Away_02" : Cv_Med_CGS02_Away,
                            "Media_RPS_MO_Home" : Med_RPS_MO_Home,
                            "CV_RPS_MO_Home" : Cv_Med_RPS_MO_Home,
                            "Media_RPS_MO_Away" : Med_RPS_MO_Away,
                            "CV_RPS_MO_Away" : Cv_Med_RPS_MO_Away,
                            "Media_RPS_OvUn_Home" : Med_RPS_OvUn_Home,
                            "CV_RPS_OvUn_Home" : Cv_Med_RPS_OvUn_Home,
                            "Media_RPS_OvUn_Away" : Med_RPS_OvUn_Away,
                            "CV_RPS_OvUn_Away" : Cv_Med_RPS_OvUn_Away,
                            "Media_RPS_BTTS_Home" : Med_RPS_BTTS_Home,
                            "CV_RPS_BTTS_Home" : Cv_Med_RPS_BTTS_Home,
                            "Media_RPS_BTTS_Away" : Med_RPS_BTTS_Away,
                            "CV_RPS_BTTS_Away" : Cv_Med_RPS_BTTS_Away,
                            "Media_Prob_Home" : Med_prob_Home,
                            "CV_Med_Prob_Home" : Cv_Med_prob_Home,
                            "Media_Prob_Away" : Med_prob_Away,
                            "CV_Med_Prob_Away" : Cv_Med_prob_Away,
                            "Med_Prim_Golo_Marcado_Home" : Med_Primeiro_Golo_Marcado_Home,
                            "Med_Prim_Golo_Sofrido_Home" : Med_Primeiro_Golo_Sofrido_Home,
                            "Med_Prim_Golo_Marcado_Away" : Med_Primeiro_Golo_Marcado_Away,
                            "Med_Prim_Golo_Sofrido_Away" : Med_Primeiro_Golo_Sofrido_Away,
                            "Porc_Marcou_Primeiro_Golo_Home" : Porc_Marcou_Primeiro_Home_FT,
                            "Porc_Marcou_Primeiro_Golo_Away" : Porc_Marcou_Primeiro_Away_FT,
                            "Porc_Sofreu_Primeiro_Golo_Home" : Porc_Sofreu_Primeiro_Home_FT,
                            "Porc_Sofreu_Primeiro_Golo_Away" : Porc_Sofreu_Primeiro_Away_FT,
                            "Porc_Marcou_Primeiro_Golo_Home_1P" : Porc_Marcou_Primeiro_Home_HT,
                            "Porc_Marcou_Primeiro_Golo_Away_1P" : Porc_Marcou_Primeiro_Away_HT,
                            "Porc_Sofreu_Primeiro_Golo_Home_1P" : Porc_Sofreu_Primeiro_Home_HT,
                            "Porc_Sofreu_Primeiro_Golo_Away_1P" : Porc_Sofreu_Primeiro_Away_HT,
                            "Porc_BTTS_Y_Home" : Porc_BTTS_Y_Home,
                            "Porc_BTTS_Y_Away" : Porc_BTTS_Y_Away,
                            "Porc_Over05HT_Home" : Porc_Ov05_HT_Home,
                            "Porc_Over05HT_Away" : Porc_Ov05_HT_Away,
                            "Porc_Under05HT_Home" : Porc_Un05_HT_Home,
                            "Porc_Under05HT_Away" : Porc_Un05_HT_Away,
                            "Porc_Over15HT_Home" : Porc_Ov15_HT_Home,
                            "Porc_Over15HT_Away" : Porc_Ov15_HT_Away,
                            "Porc_Under15HT_Home" : Porc_Un15_HT_Home,
                            "Porc_Under15HT_Away" : Porc_Un15_HT_Away,
                            "Porc_Over05FT_Home" : Porc_Ov05_FT_Home,
                            "Porc_Over05FT_Away" : Porc_Ov05_FT_Away,
                            "Porc_Under05FT_Home" : Porc_Un05_FT_Home,
                            "Porc_Under05FT_Away" : Porc_Un05_FT_Away,
                            "Porc_Over15FT_Home" : Porc_Ov15_FT_Home,
                            "Porc_Over15FT_Away" : Porc_Ov15_FT_Away,
                            "Porc_Under15FT_Home" : Porc_Un15_FT_Home,
                            "Porc_Under15FT_Away" : Porc_Un15_FT_Away,
                            "Porc_Over25FT_Home" : Porc_Ov25_FT_Home,
                            "Porc_Over25FT_Away" : Porc_Ov25_FT_Away,
                            "Porc_Under25FT_Home" : Porc_Un25_FT_Home,
                            "Porc_Under25FT_Away" : Porc_Un25_FT_Away,
                            "Porc_Home_Win_HT" : Porc_Win_HT_Home,
                            "Porc_Away_Win_HT" : Porc_Win_HT_Away,
                            "Porc_Home_Win_FT" : Porc_Win_FT_Home,
                            "Porc_Away_Win_FT" : Porc_Win_FT_Away,
                            "Porc_Score_Min_1G_Home": Porc_Score_FT_Home,
                            "Porc_Score_Min_1G_Away": Porc_Score_FT_Away,
                            "Porc_Took_Min_1G_Home" : Porc_Took_FT_Home,  
                            "Porc_Took_Min_1G_Away" : Porc_Took_FT_Away,
                            "Med_Power_Ranking_Home" : Med_Power_Ranking_Home,
                            "CV_pwr_Home" : Cv_Med_Power_Ranking_Home,
                            "Med_Power_Ranking_Away" : Med_Power_Ranking_Away,
                            "CV_pwr_Away" : Cv_Med_Power_Ranking_Away,
                            }
                        jogo_lista.append(jogo)
            except Exception as e:
                print(f'Error processing row{index}: {e}')
                pass
            df_jogos_do_dia = pd.DataFrame(jogo_lista)
            df_jogos_do_dia.index = df_jogos_do_dia.index + 1
            df_jogos_do_dia.index.name = "Nº"
            
            
                    
    else:
        st.warning("No data available in the base dataset.")
    
    # Analysis sections
    st.header("Back Home")
#     Back_Home = df_jogos_do_dia[
#     (df_jogos_do_dia['Med_Power_Ranking_Home'] >= 250) & (df_jogos_do_dia['Med_Power_Ranking_Away'] < 250) &
#     (df_jogos_do_dia['Media_CGM_Home_01'] > 3.5) & (df_jogos_do_dia['Media_CGM_Home_02'] > 1) & (df_jogos_do_dia['CV_CGM_Home_02'] < 0.7)
# ]
    # Back_Home = Back_Home.sort_values(by='Time', ascending=True)
    # Back_Home = drop_reset_index(Back_Home)
    # st.write("")
    st.dataframe(df_jogos_do_dia)
    st.write("")
    st.write("")
    st.write("")
    st.header("Back Away")
    st.write("This section can include analysis or visualizations for Away Back strategies.")
    
    return df_liga
    

