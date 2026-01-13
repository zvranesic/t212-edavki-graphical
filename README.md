# 📈 Trading 212 - Edavki poročanje

Živijo! Ta skripta je nastala, da ti prihrani ure (ali dni) ročnega vpisovanja transakcij v portal eDavki. Če uporabljaš Trading 212, ta programček samodejno prebere tvoje CSV izpiske, izračuna vse potrebno po slovenski zakonodaji in ti pripravi XML datoteke, ki jih samo uvoziš.

---

## 🚀 Kaj program zmore?

-   **FURS FIFO logika:** Avtomatski izračun nabavne cene po metodi prvi noter, prvi ven.
-   **Normirani stroški (1%):** Avtomatsko prišteje 1% pri nakupu in odšteje 1% pri prodaji (zniža tvoj davek!).
-   **Holding Period (Zniževanje davka):** Program ve, koliko let si imel delnico. Avtomatsko upošteva lestvico (25%, 20%, 15%, 0%) glede na čas imetništva.
-   **30-dnevno pravilo (Wash Sales):** Prepozna, če si delnico kupil nazaj v 30 dneh po prodaji z izgubo (FURS pravilo 97. člena ZDoh-2).
-   **Realni P/L vs. FURS P/L:** Vidiš dejanski profit glede na povprečno nabavno ceno (tako kot v T212 aplikaciji) in ločeno FURS-ovo številko.
-   **ECB tečaji:** Samodejno pridobi uradne tečaje ECB na dan transakcije.
-   **Stock Splits:** Podpora za delitve delnic (npr. Nvidia 1:10), da se količine ne pomešajo.
-   **XML Izvoz:** Generira datoteki za obrazca **Doh-KDVP** (delnice) in **Doh-Div** (dividende).

---

## 🛠️ Hitra priprava (Samo prvič)

1.  **Namesti Python:** Prenesi ga na [python.org](https://www.python.org/downloads/).
    -   **Nujno:** Ob namestitvi obkljukaj **"Add Python to PATH"**.
2.  **Podatki:** V mapo `input` skopiraj vse svoje Trading 212 CSV izpiske (najbolje od samega začetka trgovanja).
3.  **Nastavitve:** Odpri `user_settings.py` z Beležnico in vpiši svoje podatke (davčno, ime, naslov ...).

---

## ⚡ Zagon

Pozabi na ukaze v terminalu! Samo **dvoklikni na datoteko `run.bat`**.

-   Skripta bo sama namestila/posodobila knjižnice (`streamlit`, `pandas`, `requests`).
-   Avtomatsko bo zagnala grafični vmesnik v tvojem brskalniku.

---

## 📂 Kje so moji dokumenti?

Ko program zaženeš in izbereš leto:

1.  XML datoteke se **samodejno ustvarijo/posodobijo** v mapi `output`.
2.  Datoteki `Doh_KDVP_xxxx.xml` in `Doh_Div_xxxx.xml` preprosto naložiš na portal eDavki (Uvoz dokumenta).

---

### ☕ Podpora

Če ti je program prihranil čas, živce in denar pri davkih, bom vesel donacije za kavo ali pivo!

👉 **[Doniraj preko PayPal-a](https://www.paypal.com/donate/?hosted_button_id=X35CTXP8REUVQ)**

---

**Opozorilo:** Program je informativni pripomoček. Preden oddaš na eDavke, vseeno malo preveri številke, če se ti zdi vse smiselno. Za svojo davčno napoved odgovarjaš sam.
