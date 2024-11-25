import streamlit as st

from back import show_back
from lay import show_lay
from overs_unders_ht import show_overs_unders_ht
from overs_unders_ft import show_overs_unders_ft
from btts import show_btts
from lay_correct_score import show_lay_correct_score
from analise_jogo_a_jogo import show_analise_jogo_a_jogo
from analise_correct_score import show_analise_correct_score

### Criacao do Aplicativo ###

st.set_page_config(
    page_title="Fluffy Chips Dashboard", layout="wide"
)

pages = ["Back", "Lay", "Overs / Unders no HT", "Overs / Unders no FT", "BTTS", "Lay Correct Score", "Análise Jogo a Jogo", "Análise Correct Score"]

pick = st.sidebar.radio('', pages)

if pick == "Back":
    show_back()
elif pick == "Lay":
    show_lay()
elif pick == "Overs / Unders no HT":
    show_overs_unders_ht()
elif pick == "Overs / Unders no FT":
    show_overs_unders_ft()
elif pick == "BTTS":
    show_btts()
elif pick == "Lay Correct Score":
    show_lay_correct_score()
elif pick == "Análise Jogo a Jogo":
    show_analise_jogo_a_jogo()
elif pick == "Análise Correct Score":
    show_analise_correct_score()
