============================================================
   TRADING 212 DASHBOARD - NAVODILA ZA UPORABO
============================================================

1. PRIPRAVA OKOLJA (Samo prvič)
---------------------------------
- Namesti Python: https://www.python.org/ 
  (Obvezno označi "Add Python to PATH"!)
- Odpri Ukazni poziv (CMD) in namesti Streamlit z ukazom:
  pip install streamlit pandas requests

2. PRIPRAVA PODATKOV
---------------------------
- CSV izvoze iz Trading 212 skopiraj v mapo 'input'.
- V mapi naj bo celotna zgodovina (vsi CSV-ji), da bo
  FIFO izračun nabavne cene pravilen.

3. NASTAVITVE (settings.py)
---------------------------
- Odpri 'settings.py' in vpiši svojo davčno številko, 
  ime, naslov in ostale podatke. Datoteko shrani.

4. ZAGON PROGRAMA
-----------------
- Odpri mapo, kjer je datoteka 'app.py'.
- V naslovno vrstico mape (zgoraj) vpiši 'cmd' in pritisni Enter.
- Vpiši ukaz: streamlit run app.py
- Program se bo odprl v vašem spletnem brskalniku.

5. UPORABA VMESNIKA
-------------------
- Na levi strani preveri svoje podatke in izberi leto.
- V zavihkih si oglej profit po delnicah in stanje zalog.
- XML datoteka se samodejno shrani v mapo 'output'.
- Gumb za prenos XML najdeš v stranskem meniju na levi.

------------------------------------------------------------
Trading 212 Dashboard | Created by Žan Vranešič

Če ti je program prihranil čas, lahko doniraš za kavo:
PayPal: https://www.paypal.com/donate/?hosted_button_id=X35CTXP8REUVQ
------------------------------------------------------------

OPOMBA: Program je informativni pripomoček. Pred oddajo
na portal eDavki obvezno preverite izračun.