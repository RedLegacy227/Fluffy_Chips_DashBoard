from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import streamlit as st
from datetime import date

# Helper functions
def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def read_jogos(dia):
    dia_str = dia.strftime('%Y-%m-%d')
    base_url = "https://raw.githubusercontent.com/RedLegacy227/df_jogos_do_dia/refs/heads/main/"
    file_name = f"df_jogos_do_dia_{dia_str}.csv"
    file_url = base_url + file_name
    
    try:
        jogos_do_dia = pd.read_csv(file_url)
        jogos_do_dia = drop_reset_index(jogos_do_dia)
    except Exception as e:
        st.error(f"Erro ao carregar dados dos jogos do dia: {e}")
        jogos_do_dia = pd.DataFrame()  # Retorna DataFrame vazio no caso de erro
    return jogos_do_dia

def read_base_de_dados():
    url = "https://raw.githubusercontent.com/RedLegacy227/base_de_dados_fluffy_chips/refs/heads/main/fluffy_chips_2018_2024.csv"
    colunas_selecionadas = [
        "Date", "League", "Season", "Home", "Away", "HT_Goals_H", "HT_Goals_A", "FT_Goals_H", "FT_Goals_A",
        "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "HT_Odd_Over05", "HT_Odd_Under05", "FT_Odd_Over05", "FT_Odd_Under05",
        "FT_Odd_Over15", "FT_Odd_Under15", "FT_Odd_Over25", "FT_Odd_Under25", "Odd_BTTS_Yes", "Odd_BTTS_No",
        "Goals_Minutes_Home", "Goals_Minutes_Away",
    ]
    try:
        # Carregar base de dados
        base_dados = pd.read_csv(url)
        
        # Selecionar apenas as colunas desejadas
        base_dados = base_dados[colunas_selecionadas]
        
        # Resetar índice e remover valores nulos
        base_dados = drop_reset_index(base_dados)
    except Exception as e:
        st.error(f"Erro ao carregar a base de dados: {e}")
        base_dados = pd.DataFrame()  # Retorna DataFrame vazio no caso de erro
    return base_dados

# Função principal para a página de análise dos resultados
def show_analise_correct_score():
    st.title("Análise de Resultados - Correct Score")
    
    # Seção: Seleção de Data
    dia = st.date_input("Selecione a data para análise", date.today())
    
    # Carregar dados
    st.subheader("Jogos do Dia")
    jogos_do_dia = read_jogos(dia)
    st.dataframe(jogos_do_dia)

    base_dados = read_base_de_dados()
    
    if not jogos_do_dia.empty and not base_dados.empty:
        # Filtrar dados da base até o dia anterior ao selecionado
        dia_anterior = pd.to_datetime(dia) - pd.Timedelta(days=1)
        base_filtrada = base_dados[pd.to_datetime(base_dados['Date']) <= dia_anterior]
        
        # Seleção da Equipe para Análise
        st.subheader("Selecione a equipe para análise detalhada")
        equipes_casa = jogos_do_dia['Home'].unique()
        equipe_selecionada = st.selectbox("Equipe da Casa:", sorted(equipes_casa))
    
    if equipe_selecionada:
        # Exibir Jogos do Dia para a Equipe Selecionada
        st.subheader(f"Jogos do Dia para {equipe_selecionada}")
        jogos_equipe_casa = jogos_do_dia[jogos_do_dia['Home'] == equipe_selecionada]
        st.dataframe(jogos_equipe_casa)
        
        for index, jogo in jogos_equipe_casa.iterrows():
            adversario = jogo['Away']
            st.write(f"**Analisando Jogo: {equipe_selecionada} (Home) vs {adversario} (Away)**")
            
            # **Análise para a Equipe da Casa (Home)**
            st.subheader(f"Frequência de Resultados - {equipe_selecionada} (Home)")
            resultados_home = base_filtrada[base_filtrada['Home'] == equipe_selecionada]
            resultados_home['Resultado'] = resultados_home.apply(lambda row: f"{row['FT_Goals_H']}x{row['FT_Goals_A']}", axis=1)
            freq_resultados_home = resultados_home['Resultado'].value_counts()
            st.bar_chart(freq_resultados_home)
            
            # Goleadas da Casa (Home)
            goleadas_home = resultados_home[
                (resultados_home['FT_Goals_H'] - resultados_home['FT_Goals_A']) >= 4
            ]
            st.write(f"**Goleadas Home ({len(goleadas_home)}):**")
            st.dataframe(goleadas_home)
            
            # **Análise para a Equipe Visitante (Away)**
            st.subheader(f"Frequência de Resultados - {adversario} (Away)")
            resultados_away = base_filtrada[base_filtrada['Away'] == adversario]
            resultados_away['Resultado'] = resultados_away.apply(lambda row: f"{row['FT_Goals_H']}x{row['FT_Goals_A']}", axis=1)
            freq_resultados_away = resultados_away['Resultado'].value_counts()
            st.bar_chart(freq_resultados_away)
            
            # Goleadas do Visitante (Away)
            goleadas_away = resultados_away[
                (resultados_away['FT_Goals_A'] - resultados_away['FT_Goals_H']) >= 4
            ]
            st.write(f"**Goleadas Away ({len(goleadas_away)}):**")
            st.dataframe(goleadas_away)