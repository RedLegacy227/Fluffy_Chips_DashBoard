import streamlit as st
import pandas as pd
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
        # Carregar o DataFrame sem índice adicional
        jogos_do_dia = pd.read_csv(file_url)
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

# Main dashboard
def show_analise_jogo_a_jogo():
    st.title("Fluffy Chips Dashboard")
    
    # Seção: Seleção de Data
    dia = st.date_input("Selecione a data para análise", date.today())
    
    # Carregar dados
    st.subheader("Jogos do Dia")
    jogos_do_dia = read_jogos(dia)
    
    if not jogos_do_dia.empty:
        # Remover as colunas indesejadas e exibir
        jogos_do_dia_display = jogos_do_dia.drop(columns=['index', 'Nº'], errors='ignore')
        st.dataframe(jogos_do_dia_display)

    base_dados = read_base_de_dados()
    
    if not jogos_do_dia.empty and not base_dados.empty:
        # Seção: Seleção de equipe
        st.subheader("Selecione a equipe")
        equipes_casa = jogos_do_dia['Home'].unique()
        equipe_selecionada = st.selectbox("Equipe da Casa:", sorted(equipes_casa))
        
        if equipe_selecionada:
            # Exibir detalhes do jogo selecionado
            jogos_equipe_casa = jogos_do_dia[jogos_do_dia['Home'] == equipe_selecionada]
            
            for index, row in jogos_equipe_casa.iterrows():
                adversario = row['Away']
                st.write(f"**Jogo Selecionado:** {equipe_selecionada} vs {adversario}")
                
                # Exibir dados completos do jogo selecionado
                st.subheader("Dados do Jogo Selecionado")
                colunas_selecionadas_jogo = [
                    'League', 'Date', 'Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'HT_Odd_Ov05',
                    'HT_Odd_Un05', 'FT_Odd_Ov15', 'FT_Odd_Un15', 'FT_Odd_Ov25', 'FT_Odd_Un25', 'FT_Odd_BTTS_Y',
                    'FT_Odd_BTTS_N', 'Prob_H', 'Prob_D', 'Prob_A', 'Prob_Ov05_HT', 'Prob_Un05_HT', 'Prob_Ov15_FT',
                    'Prob_Un15_FT', 'Prob_Ov25_FT', 'Prob_Un25_FT', 'Prob_BTTS_Y_FT', 'Prob_BTTS_N_FT', 'H_D', 'H_A',
                    'D_H', 'D_A', 'A_H', 'A_D', 'Dif_Abs_HomeAway', 'Dif_Abs_HomeDraw', 'Dif_Abs_DrawAway',
                    'Angle_HomeAway', 'Angle_HomeDraw', 'Angle_DrawAway', 'Dif_Perc_HomeAway', 'Dif_Perc_HomeDraw',
                    'Dif_Perc_DrawAway', 'Media_Ptos_Home', 'CV_Ptos_Home', 'Media_Ptos_Away', 'CV_Ptos_Away',
                    'Media_SG_Home', 'CV_SG_Home', 'Media_SG_Away', 'CV_SG_Away', 'Media_GM_Home_1P',
                    'CV_GM_Home_1P', 'Media_GM_Away_1P', 'CV_GM_Away_1P', 'Media_GS_Home_1P', 'CV_GS_Home_1P',
                    'Media_GS_Away_1P', 'CV_GS_Away_1P', 'Media_GM_Home', 'CV_GM_Home', 'Media_GM_Away', 'CV_GM_Away',
                    'Media_GS_Home', 'CV_GS_Home', 'Media_GS_Away', 'CV_GS_Away', 'Media_CGM_Home_01',
                    'CV_CGM_Home_01', 'Media_CGM_Away_01', 'CV_CGM_Away_01', 'Media_CGS_Home_01', 'CV_CGS_Home_01',
                    'Media_CGS_Away_01', 'CV_CGS_Away_01', 'Media_CGM_Home_02', 'CV_CGM_Home_02', 'Media_CGM_Away_02',
                    'CV_CGM_Away_02', 'Media_CGS_Home_02', 'CV_CGS_Home_02', 'Media_CGS_Away_02', 'CV_CGS_Away_02',
                    'Media_RPS_MO_Home', 'CV_RPS_MO_Home', 'Media_RPS_MO_Away', 'CV_RPS_MO_Away', 'Media_RPS_OvUn_Home',
                    'CV_RPS_OvUn_Home', 'Media_RPS_OvUn_Away', 'CV_RPS_OvUn_Away', 'Media_RPS_BTTS_Home',
                    'CV_RPS_BTTS_Home', 'Media_RPS_BTTS_Away', 'CV_RPS_BTTS_Away', 'Media_Prob_Home',
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
                    'Porc_Under25FT_Away', 'Porc_Home_Win_HT', 'Porc_Away_Win_HT', 'Porc_Home_Win_FT',
                    'Porc_Away_Win_FT', 'Porc_Score_Min_1G_Home', 'Porc_Score_Min_1G_Away', 'Porc_Took_Min_1G_Home',
                    'Porc_Took_Min_1G_Away', 'Med_Power_Ranking_Home', 'CV_pwr_Home', 'Med_Power_Ranking_Away',
                    'CV_pwr_Away'
                ]
                st.dataframe(row[colunas_selecionadas_jogo])
                # Histórico de Confrontos Diretos
                st.subheader(f"Histórico de Confrontos Diretos entre {equipe_selecionada} e {adversario}")
                colunas_confrontos = [
                    "Date", "League", "Season", "Home", "Away", "HT_Goals_H", "HT_Goals_A", "FT_Goals_H", "FT_Goals_A",
                    "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "HT_Odd_Over05", "HT_Odd_Under05", "FT_Odd_Over05",
                    "FT_Odd_Under05", "FT_Odd_Over15", "FT_Odd_Under15", "FT_Odd_Over25", "FT_Odd_Under25",
                    "Odd_BTTS_Yes", "Odd_BTTS_No", "Goals_Minutes_Home", "Goals_Minutes_Away"
                ]
                h2h = base_dados[(base_dados['Home'] == equipe_selecionada) & (base_dados['Away'] == adversario)].sort_values(by='Date', ascending=False)
                if not h2h.empty:
                    st.dataframe(h2h[colunas_confrontos])
                else:
                    st.write("Nenhum confronto direto encontrado.")
                
                # Últimos 5 jogos da equipe da casa
                st.subheader(f"Últimos 5 jogos da equipe da casa ({equipe_selecionada})")
                ultimos_jogos_casa = base_dados[
                    (base_dados['Home'] == equipe_selecionada)
                ].sort_values(by='Date', ascending=False).head(5)
                if not ultimos_jogos_casa.empty:
                    st.dataframe(ultimos_jogos_casa[colunas_confrontos])
                else:
                    st.write("Nenhum jogo recente encontrado.")
                
                # Últimos 5 jogos da equipe visitante
                st.subheader(f"Últimos 5 jogos da equipe visitante ({adversario})")
                ultimos_jogos_visitante = base_dados[
                    (base_dados['Away'] == adversario)
                ].sort_values(by='Date', ascending=False).head(5)
                if not ultimos_jogos_visitante.empty:
                    st.dataframe(ultimos_jogos_visitante[colunas_confrontos])
                else:
                    st.write("Nenhum jogo recente encontrado.")
                
                # Jogos Passados com Odds Semelhantes
                st.subheader(f"Jogos Passados com Odds Semelhantes ({equipe_selecionada} vs {adversario})")
                odd_home = row['FT_Odd_H']
                odd_away = row['FT_Odd_A']
                odd_margin = 0.10
                jogos_odds_semelhantes = base_dados[
                    (base_dados['Home'] == equipe_selecionada) & 
                    (base_dados['Away'] == adversario) &
                    (base_dados['FT_Odd_H'].between(odd_home - odd_margin, odd_home + odd_margin)) &
                    (base_dados['FT_Odd_A'].between(odd_away - odd_margin, odd_away + odd_margin))
                ].sort_values(by='Date', ascending=False)
                if not jogos_odds_semelhantes.empty:
                    st.dataframe(jogos_odds_semelhantes[colunas_confrontos])
                else:
                    st.write("Nenhum jogo passado com odds semelhantes encontrado.")


