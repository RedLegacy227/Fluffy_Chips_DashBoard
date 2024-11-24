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
        jogos_do_dia = pd.read_csv(file_url)
        jogos_do_dia = drop_reset_index(jogos_do_dia)
    except Exception as e:
        st.error(f"Erro ao carregar dados dos jogos do dia: {e}")
        jogos_do_dia = pd.DataFrame()  # Retorna DataFrame vazio no caso de erro
    return jogos_do_dia

def read_base_de_dados():
    url = "https://raw.githubusercontent.com/RedLegacy227/base_de_dados_fluffy_chips/refs/heads/main/fluffy_chips_2018_2024.csv"
    try:
        base_dados = pd.read_csv(url)
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
    st.dataframe(jogos_do_dia)

    base_dados = read_base_de_dados()
    
    if not jogos_do_dia.empty and not base_dados.empty:
        # Seção: Seleção de equipe
        st.subheader("Selecione a equipe")
        equipes_casa = jogos_do_dia['Home'].unique()
        equipe_selecionada = st.selectbox("Equipe da Casa:", sorted(equipes_casa))
        
        if equipe_selecionada:
            # Exibir jogos do dia para a equipe selecionada
            jogos_equipe_casa = jogos_do_dia[jogos_do_dia['Home'] == equipe_selecionada]
            
            for index, row in jogos_equipe_casa.iterrows():
                adversario = row['Away']
                st.write(f"**Jogo Selecionado:** {equipe_selecionada} vs {adversario}")
                
                # Odds atuais
                odd_home = row['FT_Odd_H']
                odd_away = row['FT_Odd_A']
                
                st.write(f"Odds para este jogo: Home {odd_home}, Away {odd_away}")
                
                # Histórico de Confrontos Diretos
                st.subheader(f"Histórico de Confrontos Diretos entre {equipe_selecionada} e {adversario}")
                h2h = base_dados[
                    (base_dados['Home'] == equipe_selecionada) & 
                    (base_dados['Away'] == adversario)
                ].sort_values(by='Date', ascending=False)
                if not h2h.empty:
                    st.dataframe(h2h)
                else:
                    st.write("Nenhum confronto direto encontrado.")
                
                # Últimos 5 jogos da equipe da casa
                st.subheader(f"Últimos 5 jogos da equipe da casa ({equipe_selecionada})")
                ultimos_jogos_casa = base_dados[
                    (base_dados['Home'] == equipe_selecionada)
                ].sort_values(by='Date', ascending=False).head(5)
                if not ultimos_jogos_casa.empty:
                    st.dataframe(ultimos_jogos_casa)
                else:
                    st.write("Nenhum jogo recente encontrado.")
                
                # Últimos 5 jogos da equipe visitante
                st.subheader(f"Últimos 5 jogos da equipe visitante ({adversario})")
                ultimos_jogos_visitante = base_dados[
                    (base_dados['Away'] == adversario)
                ].sort_values(by='Date', ascending=False).head(5)
                if not ultimos_jogos_visitante.empty:
                    st.dataframe(ultimos_jogos_visitante)
                else:
                    st.write("Nenhum jogo recente encontrado.")
                
                # Jogos Passados com Odds Semelhantes
                st.subheader(f"Jogos Passados com Odds Semelhantes ({equipe_selecionada} vs {adversario})")
                odd_margin = 0.1
                jogos_odds_semelhantes = base_dados[
                    (base_dados['Home'] == equipe_selecionada) & 
                    (base_dados['Away'] == adversario) &
                    (base_dados['FT_Odd_H'].between(odd_home - odd_margin, odd_home + odd_margin)) &
                    (base_dados['FT_Odd_A'].between(odd_away - odd_margin, odd_away + odd_margin))
                ].sort_values(by='Date', ascending=False)
                if not jogos_odds_semelhantes.empty:
                    st.dataframe(jogos_odds_semelhantes)
                else:
                    st.write("Nenhum jogo passado com odds semelhantes encontrado.")

# Run the dashboard
if __name__ == "__main__":
    show_analise_jogo_a_jogo()