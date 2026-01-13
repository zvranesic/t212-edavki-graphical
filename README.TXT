============================================================
   TRADING 212 Edavki Poročanje - NAVODILA ZA UPORABO
============================================================

Pozdravljeni! Ta program je namenjen avtomatizaciji priprave
davčne napovedi za uporabnike Trading 212 v Sloveniji.

1. PRIPRAVA (Samo prvič)
-------------------------
- Namestite Python (https://www.python.org/).
  POMEMBNO: Obkljukajte "Add Python to PATH" pri namestitvi!
- Vse ostalo bo namestila datoteka 'run.bat'.

2. PRIPRAVA PODATKOV
---------------------
- Iz Trading 212 izvozite transakcije v CSV formatu.
- Datoteke skopirajte v mapo 'input'. 
  NASVET: V mapi naj bodo vsi CSV-ji od začetka trgovanja, 
  da bo izračun nabavne cene (FIFO) pravilen.

3. OSEBNE NASTAVITVE
---------------------
- Odprite datoteko 'user_settings.py' (desni klik -> Uredi/Notepad).
- Vpišite svojo davčno številko, ime, naslov in ostalo.
- Shranite datoteko.

4. ZAGON PROGRAMA
------------------
- Dvokliknite na datoteko 'run.bat'.
- Okno konzole bo preverilo knjižnice in zagnalo vmesnik.
- V brskalniku se bo odprla stran Trading 212 Tax Hub.

5. UPORABA IN IZVOZ
--------------------
- Na levi strani izberite davčno leto (npr. 2025).
- Program bo izračunal:
    * REALNI P/L: Koliko ste dejansko zaslužili (v žep).
    * OSNOVA FURS: Izračun s stroški in FIFO metodo.
    * DAVČNA STOPNJA: Avtomatsko znižanje (25% -> 0%) glede 
      na to, koliko let ste imeli delnico.
- XML datoteke se SAMODEJNO shranijo v mapo 'output'.
- Te datoteke naložite na portal eDavki.

------------------------------------------------------------
Trading 212 Dashboard | Created by Žan Vranešič

Če ti je program prihranil čas, živce in denar pri davkih, bom vesel donacije za kavo ali pivo!
PayPal: https://www.paypal.com/donate/?hosted_button_id=X35CTXP8REUVQ
------------------------------------------------------------

Opozorilo: Program je informativni pripomoček. Preden oddaš na eDavke, vseeno malo preveri številke,
če se ti zdi vse smiselno. Za svojo davčno napoved odgovarjaš sam.
============================================================
