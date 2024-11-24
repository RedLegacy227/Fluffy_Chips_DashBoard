import streamlit as st

from back import show_back
from lay import show_lay
from overs_unders_ht import show_overs_unders_ht
from overs_unders_ft import show_overs_unders_ft
from btts import show_btts
from correct_score import show_correct_score

### Criacao do Aplicativo ###

st.set_page_config(
    page_title="Fluffy Chips Dashboard", layout="wide"
)

pages = ["Back Home", "Back Away", "Lay Home", "Lay Away", "Overs / Unders no HT", "Overs / Unders no FT", "BTTS", "Correct Score"]

pick = st.sidebar.radio('', pages)

if pick == "Back Home":
    show_back()
elif pick == "Lay Home":
    show_lay()
elif pick == "Lay Away":
    show_lay()
elif pick == "Overs / Unders no HT":
    show_overs_unders_ht()
elif pick == "Overs / Unders no FT":
    show_overs_unders_ft()
elif pick == "BTTS":
    show_btts()
elif pick == "Correct Score":
    show_correct_score()