TRADING 212 -> EDAVKE (Doh-KDVP)
================================

Skripta pretvori Trading 212 CSV izvoze v XML za uvoz v eDavke.
Uposteva FIFO, delitve delnic (splits), 1% normirane stroske in ECB tecaje.

NAVODILA ZA UPORABO:
--------------------

1. PRIPRAVA OKOLJA
   - Namesti Python (https://www.python.org/).
   - !!! Med namestitvijo obkljukaj "Add Python to PATH" !!!
   - Odpri CMD (ukazni poziv) in zazeni: 
     pip install pandas requests

2. PODATKI
   - Izvozi vse transakcije iz Trading 212 (CSV).
   - Pomembno: Izvozi celotno zgodovino trgovanja (ne le za letosnje leto).
   - Datoteke skopiraj v mapo 'input'.

3. NASTAVITVE
   - Odpri datoteko 'settings.py' z beleznico.
   - Vpisi svoje podatke (davcna, ime, naslov) in davcno leto.

4. ZAGON
   - V mapi s skripto v naslovno vrstico vpisi 'cmd' in pritisni Enter.
   - Vpisi ukaz: 
     python main.py

5. REZULTAT
   - V mapi 'output' bos nasel XML datoteko.
   - Uvozi jo v eDavke (Doh-KDVP).

--------------------
Ce ti je skripta prihranila cas in denar, bom vesel donacije za kavo ali pivo!:
https://www.paypal.com/donate/?hosted_button_id=X35CTXP8REUVQ

Pazi: Program je informativni pripomoček. Preden oddaš na eDavke, vseeno malo preveri številke, če se ti zdi vse smiselno. Za svojo davčno napoved odgovarjaš sam.

