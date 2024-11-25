from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import streamlit as st
from datetime import date

# Helper functions
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

# Função para contar e exibir a legenda dos resultados com mensagens personalizadas
def display_result_frequencies_with_message(df, team, location='Home'):
    """Exibe frequência de resultados com mensagens personalizadas no Streamlit."""
    if location == 'Home':
        filtered_games = df[df['Home'] == team]
        result_column = ['FT_Goals_H', 'FT_Goals_A']
    else:
        filtered_games = df[df['Away'] == team]
        result_column = ['FT_Goals_H', 'FT_Goals_A']
    
    # Calcula a frequência dos resultados
    filtered_games['Resultado'] = filtered_games.apply(lambda row: f"{row[result_column[0]]}x{row[result_column[1]]}", axis=1)
    result_counts = filtered_games['Resultado'].value_counts().to_dict()
    
    # Contagem de jogos analisados
    num_games = len(filtered_games)
    
    # Lista de resultados para verificar
    target_results = [
        "0x0", "1x0", "0x1", "1x1", "2x0", "2x1", "2x2",
        "0x2", "1x2", "3x0", "3x1", "3x2", "3x3",
        "0x3", "1x3", "2x3"
    ]
    
    # Exibição no Streamlit
    st.markdown("")
    st.markdown (f"{team} - {num_games} jogos analisados")
    st.markdown("")
    for result in target_results:
        count = result_counts.get(result, 0)
        if count == 0:
            message = f"<span style='background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px;'>Limpinho ({count})</span>"
        elif 1 <= count <= 3:
            message = f"<span style='background-color: #c3e6cb; color: #0b5124; padding: 5px; border-radius: 5px;'>Favorável ({count})</span>"
        elif 4 <= count <= 7:
            message = f"<span style='background-color: #fff3cd; color: #856404; padding: 5px; border-radius: 5px;'>Cuidado ({count})</span>"
        elif 8 <= count <= 10:
            message = f"<span style='background-color: #f8d7da; color: #721c24; padding: 5px; border-radius: 5px;'>Muito Cuidado ({count})</span>"
        else:
            message = f"<span style='background-color: #f5c6cb; color: #491217; padding: 5px; border-radius: 5px;'>Não Entrar ({count})</span>"
        st.markdown(f"**Resultado {result}:** {message}", unsafe_allow_html=True)
    
    # Contagem de goleadas (vitórias com 4 ou mais gols de diferença)
    goleadas = filtered_games[
        (filtered_games[result_column[0]] - filtered_games[result_column[1]]).abs() >= 4
    ]
    goleada_count = len(goleadas)
    
    if goleada_count == 0:
        goleada_message = f"<span style='background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px;'>Limpinho ({goleada_count})</span>"
    elif 1 <= goleada_count <= 3:
        goleada_message = f"<span style='background-color: #c3e6cb; color: #0b5124; padding: 5px; border-radius: 5px;'>Favorável ({goleada_count})</span>"
    elif 4 <= goleada_count <= 7:
        goleada_message = f"<span style='background-color: #fff3cd; color: #856404; padding: 5px; border-radius: 5px;'>Cuidado ({goleada_count})</span>"
    elif 8 <= goleada_count <= 10:
        goleada_message = f"<span style='background-color: #f8d7da; color: #721c24; padding: 5px; border-radius: 5px;'>Muito Cuidado ({goleada_count})</span>"
    else:
        goleada_message = f"<span style='background-color: #f5c6cb; color: #491217; padding: 5px; border-radius: 5px;'>Não Entrar ({goleada_count})</span>"
    st.markdown(f"**Goleadas:** {goleada_message}", unsafe_allow_html=True)
# Função para exibir resultados com título formatado
def display_result_section(title, df, team, location='Home'):
    display_result_frequencies_with_message(df, team, location)

# Funções de exibição para diferentes filtros
def display_result_frequencies_3_seasons(df, team, location='Home'):
    """Exibe os resultados nas últimas 3 temporadas."""
    if location == 'Home':
        filtered_games = df[df['Home'] == team].sort_values(by='Date', ascending=False).head(114)
    else:
        filtered_games = df[df['Away'] == team].sort_values(by='Date', ascending=False).head(114)
    display_result_section("3 Temporadas", filtered_games, team, location)

def display_result_frequencies_2_seasons(df, team, location='Home'):
    """Exibe os resultados nas últimas 2 temporadas."""
    if location == 'Home':
        filtered_games = df[df['Home'] == team].sort_values(by='Date', ascending=False).head(76)
    else:
        filtered_games = df[df['Away'] == team].sort_values(by='Date', ascending=False).head(76)
    display_result_section("2 Temporadas", filtered_games, team, location)

def display_result_frequencies_current_season(df, team, location='Home', dia=None):
    """Exibe os jogos da temporada atual."""
    current_year = pd.to_datetime(dia).year
    current_season = f"{current_year}/{current_year + 1}"
    alternate_season = str(current_year)
    
    if location == 'Home':
        filtered_games = df[
            (df['Home'] == team) & 
            ((df['Season'] == current_season) | (df['Season'] == alternate_season))
        ].sort_values(by='Date', ascending=False)
    else:
        filtered_games = df[
            (df['Away'] == team) & 
            ((df['Season'] == current_season) | (df['Season'] == alternate_season))
        ].sort_values(by='Date', ascending=False)
    display_result_section("Temporada Atual", filtered_games, team, location)
    
# Exibir a legenda dos resultados para jogos em casa das equipes selecionadas
def display_home_and_away_results(df_liga1, team, team_games_today):
    """Exibe resultados lado a lado para jogos em casa e fora."""
    # Criar duas colunas para a exibição lado a lado
    col1, col2 = st.columns(2)

    # Exibir os últimos 20 jogos em casa
    with col1:
        display_home_and_away_results(f"{team}", df_liga1, team, location='Home')

    # Exibir os últimos 20 jogos fora para cada adversário
    with col2:
        for opponent in team_games_today['Away'].unique():
            display_home_and_away_results(f"{opponent}", df_liga1, opponent, location='Away')

def display_last_3_seasons_side_by_side(df_liga1, team, team_games_today):
    """Exibe os últimos 20 jogos de casa e fora lado a lado no Streamlit."""

    # Criar duas colunas para a exibição lado a lado
    col1, col2 = st.columns(2)

    # Exibir os últimos 20 jogos em casa
    with col1:
        display_result_frequencies_3_seasons(df_liga1, team, location='Home')

    # Exibir os últimos 20 jogos fora para cada adversário
    with col2:
        for opponent in team_games_today['Away'].unique():
            display_result_frequencies_3_seasons(df_liga1, opponent, location='Away')

def display_last_2_seasons_side_by_side(df_liga1, team, team_games_today):
    """Exibe os últimos 10 jogos de casa e fora lado a lado no Streamlit."""

    # Criar duas colunas para a exibição lado a lado
    col1, col2 = st.columns(2)

    # Exibir os últimos 10 jogos em casa
    with col1:
        display_result_frequencies_2_seasons(df_liga1, team, location='Home')

    # Exibir os últimos 10 jogos fora para cada adversário
    with col2:
        for opponent in team_games_today['Away'].unique():
            display_result_frequencies_2_seasons(df_liga1, opponent, location='Away')
            
def display_current_season_side_by_side(df_liga1, team, team_games_today, dia):
    """Exibe os jogos da temporada atual de casa e fora lado a lado no Streamlit."""

    # Criar duas colunas para a exibição lado a lado
    col1, col2 = st.columns(2)

    # Exibir os jogos da temporada atual em casa
    with col1:
        display_result_frequencies_current_season(df_liga1, team, location='Home', dia=dia)

    # Exibir os jogos da temporada atual fora para cada adversário
    with col2:
        for opponent in team_games_today['Away'].unique():
            display_result_frequencies_current_season(df_liga1, opponent, location='Away', dia=dia)
            
def display_table_with_aggrid(dataframe):
    """Exibe o DataFrame com ajuste automático de colunas, altura e alinhamento central."""
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    
    # Configurar alinhamento central
    gb.configure_default_column(
        resizable=True, autoSizeColumns=True, wrapText=True, 
        cellStyle={'textAlign': 'center'}  # Alinhamento central
    )
    
    # Ajustar altura automaticamente
    gb.configure_grid_options(domLayout='autoHeight')  # Altura dinâmica

    grid_options = gb.build()

    AgGrid(dataframe, gridOptions=grid_options, enable_enterprise_modules=False)
    

# Main dashboard
def show_analise_correct_score():
    """Exibe o painel principal para análise jogo a jogo."""
    st.title("Fluffy Chips Dashboard")

    # Seção: Seleção de Data
    dia = st.date_input("Selecione a data para análise", date.today())

    # Carregar dados
    st.subheader("Jogos do Dia")
    jogos_do_dia = read_jogos(dia)

    if not jogos_do_dia.empty:
        # Exibir jogos do dia com cabeçalhos corrigidos e ajuste automático
        display_table_with_aggrid(jogos_do_dia)

        # Seleção da equipe para análise
        st.subheader("Selecione a Equipe para Análise Detalhada")
        equipes_casa = sorted(jogos_do_dia['Home'].unique())
        equipe_selecionada = st.selectbox("Equipe da Casa:", equipes_casa)

        # Carregar a base de dados principal
        base_dados = read_base_de_dados()

        if not base_dados.empty and equipe_selecionada:            
            # Filtrar jogos do dia para a equipe selecionada
            jogos_equipe_casa = jogos_do_dia[jogos_do_dia['Home'] == equipe_selecionada]

            # Resultados gerais: Home e Away
            st.markdown("<h2 style='text-align: center;'>Resultados Verificados no Total da Base de Dados</h2>", unsafe_allow_html=True)
            st.markdown("")
            display_home_and_away_results(base_dados, equipe_selecionada, jogos_equipe_casa)

            # 3 Temporadas: Home e Away
            st.markdown("<h2 style='text-align: center;'>Resultados Verificados nas Últimas 3 Temporadas</h2>", unsafe_allow_html=True)
            st.markdown("")
            display_last_3_seasons_side_by_side(base_dados, equipe_selecionada, jogos_equipe_casa)

            # 2 Temporadas: Home e Away
            st.markdown("<h2 style='text-align: center;'>Resultados Verificados nas Últimas 2 Temporadas</h2>", unsafe_allow_html=True)
            st.markdown("")
            display_last_2_seasons_side_by_side(base_dados, equipe_selecionada, jogos_equipe_casa)

            # Temporada atual: Home e Away
            st.markdown("<h2 style='text-align: center;'>Resultados Verificados na Temporada Atual</h2>", unsafe_allow_html=True)
            st.markdown("")
            display_current_season_side_by_side(base_dados, equipe_selecionada, jogos_equipe_casa, dia)

    else:
        st.warning("Nenhum jogo encontrado para o dia selecionado. Por favor, escolha outra data.")
