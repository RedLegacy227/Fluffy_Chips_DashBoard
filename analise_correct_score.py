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
        # Seleção da Equipe para Análise
        st.subheader("Selecione a equipe para análise detalhada")
        equipes_casa = jogos_do_dia['Home'].unique()
        equipe_selecionada = st.selectbox("Equipe da Casa:", sorted(equipes_casa))
        
        if equipe_selecionada:
            # Exibir Jogos do Dia para a Equipe Selecionada
            st.subheader(f"Jogos do Dia para {equipe_selecionada}")
            jogos_equipe_casa = jogos_do_dia[jogos_do_dia['Home'] == equipe_selecionada]
            st.dataframe(jogos_equipe_casa)
            
            # Análise de Frequência de Resultados
            st.subheader(f"Frequência de Resultados - {equipe_selecionada}")
            resultados = base_dados[base_dados['Home'] == equipe_selecionada]
            resultados['Resultado'] = resultados.apply(lambda row: f"{row['FT_Goals_H']}x{row['FT_Goals_A']}", axis=1)
            
            freq_resultados = resultados['Resultado'].value_counts()
            st.bar_chart(freq_resultados)
            
            # Legenda dos Resultados
            st.subheader("Legenda dos Resultados")
            for resultado, freq in freq_resultados.items():
                if freq == 0:
                    mensagem = "Limpinho (0)"
                elif 1 <= freq <= 3:
                    mensagem = "Favorável"
                elif 4 <= freq <= 7:
                    mensagem = "Cuidado"
                elif 8 <= freq <= 10:
                    mensagem = "Muito Cuidado"
                else:
                    mensagem = "Não Entrar"
                st.write(f"Resultado {resultado}: {mensagem}")
            
            # Goleadas Separadas
            st.subheader(f"Goleadas de {equipe_selecionada}")
            
            # Goleadas da Casa (Home)
            goleadas_home = resultados[
                (resultados['FT_Goals_H'] - resultados['FT_Goals_A']) >= 4
            ]
            st.write(f"**Goleadas em Casa ({len(goleadas_home)}):**")
            st.dataframe(goleadas_home)
            
            # Goleadas do Visitante (Away)
            goleadas_away = resultados[
                (resultados['FT_Goals_A'] - resultados['FT_Goals_H']) >= 4
            ]
            st.write(f"**Goleadas Sofridas ({len(goleadas_away)}):**")
            st.dataframe(goleadas_away)

# Executar o dashboard
if __name__ == "__main__":
    show_analise_correct_score()
