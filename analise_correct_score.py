from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import streamlit as st
from datetime import date

# Funções auxiliares
def drop_reset_index(df):
    """Remove valores nulos e redefine o índice."""
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def read_jogos(dia):
    """Carrega os jogos do dia a partir de um arquivo remoto."""
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
    """Carrega a base de dados principal com colunas selecionadas."""
    url = "https://raw.githubusercontent.com/RedLegacy227/base_de_dados_fluffy_chips/refs/heads/main/fluffy_chips_2018_2024.csv"
    colunas_selecionadas = [
        "Date", "League", "Season", "Home", "Away", "HT_Goals_H", "HT_Goals_A", "FT_Goals_H", "FT_Goals_A",
        "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "HT_Odd_Over05", "HT_Odd_Under05", "FT_Odd_Over05", "FT_Odd_Under05",
        "FT_Odd_Over15", "FT_Odd_Under15", "FT_Odd_Over25", "FT_Odd_Under25", "Odd_BTTS_Yes", "Odd_BTTS_No",
        "Goals_Minutes_Home", "Goals_Minutes_Away",
    ]
    try:
        base_dados = pd.read_csv(url)
        base_dados = base_dados[colunas_selecionadas]
        base_dados = drop_reset_index(base_dados)
    except Exception as e:
        st.error(f"Erro ao carregar a base de dados: {e}")
        base_dados = pd.DataFrame()  # Retorna DataFrame vazio no caso de erro
    return base_dados

def calculate_results(df):
    """Calcula os resultados baseados nos gols de cada partida."""
    df['Resultado'] = df.apply(lambda row: f"{row['FT_Goals_H']}x{row['FT_Goals_A']}", axis=1)
    return df

def display_table_with_aggrid(dataframe):
    """Exibe o DataFrame com ajuste automático de colunas, altura e alinhamento central."""
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_default_column(
        resizable=True, autoSizeColumns=True, wrapText=True,
        cellStyle={'textAlign': 'center'}  # Alinhamento central
    )
    gb.configure_grid_options(domLayout='autoHeight')  # Altura dinâmica

    grid_options = gb.build()
    AgGrid(dataframe, gridOptions=grid_options, enable_enterprise_modules=False)

def display_result_frequencies_with_message(df, team, location='Home'):
    """Exibe frequência de resultados com mensagens personalizadas."""
    if location == 'Home':
        filtered_games = df[df['Home'] == team]
        result_column = ['FT_Goals_H', 'FT_Goals_A']
    else:
        filtered_games = df[df['Away'] == team]
        result_column = ['FT_Goals_H', 'FT_Goals_A']
    
    # Calcula a frequência dos resultados
    filtered_games['Resultado'] = filtered_games.apply(lambda row: f"{row[result_column[0]]}x{row[result_column[1]]}", axis=1)
    result_counts = filtered_games['Resultado'].value_counts()
    
    # Contagem de jogos analisados
    num_games = len(filtered_games)
    
    st.subheader(f"Frequência de Resultados ({location}) - {team}")
    st.write(f"**Total de jogos analisados: {num_games}**")
    
    # Exibir frequência de resultados
    for result, count in result_counts.items():
        st.write(f"Resultado **{result}**: {count} vezes")
    
    # Identificar goleadas
    goleadas = filtered_games[(filtered_games[result_column[0]] - filtered_games[result_column[1]]).abs() >= 4]
    goleada_count = len(goleadas)
    st.write(f"**Goleadas: {goleada_count} jogos**")
    st.dataframe(goleadas)

# Função principal
def show_analise_correct_score():
    """Exibe a análise no Streamlit."""
    st.title("Análise de Resultados - Correct Score")
    
    # Carregar os jogos do dia e a base de dados principal
    dia = st.date_input("Selecione a data para análise:", date.today())
    jogos_do_dia = read_jogos(dia)
    df_base = read_base_de_dados()

    if jogos_do_dia.empty or df_base.empty:
        st.warning("Nenhum jogo ou dados históricos disponíveis para análise.")
        return

    # Calcular resultados para a base
    df_base = calculate_results(df_base)

    # Criar lista de equipes únicas
    home_teams = sorted(jogos_do_dia['Home'].unique())
    
    # Selecionar equipe da casa
    selected_team = st.selectbox("Selecione a equipe da casa:", home_teams)
    
    if selected_team:
        st.header(f"Análise da equipe: {selected_team}")
        
        # Exibir jogos do dia
        st.subheader("Jogos do Dia")
        team_games_today = jogos_do_dia[jogos_do_dia['Home'] == selected_team]
        display_table_with_aggrid(team_games_today)
        
        # Exibir frequências de resultados
        display_result_frequencies_with_message(df_base, selected_team, location='Home')

        # Últimos jogos da equipe selecionada
        st.subheader(f"Últimos jogos da equipe {selected_team}")
        recent_games = df_base[df_base['Home'] == selected_team].sort_values(by='Date', ascending=False).head(5)
        display_table_with_aggrid(recent_games)
