# 🚀 Trading 212 ➡️ eDavke (Doh-KDVP)

Živijo! Ta skripta je nastala, da si malo olajšamo življenje pri tistem zoprnem opravilu – oddaji davčne napovedi za delnice na eDavke. Če trguješ na Trading 212, veš, da ročno vpisovanje vsakega posla traja celo večnost. Ta programček to naredi namesto tebe, pripravi XML datoteko, ki jo samo uvoziš na portal, in stvar je rešena.

Najnovejša verzija ima zdaj preprost grafični vmesnik, tako da ti ni treba gledati v črno okno (terminal), ampak vse urediša kar v brskalniku.

---

## 🛠️ Kaj moraš narediti (samo prvič)

1.  **Zrihtaj si Python:** Prenesi ga na [python.org](https://www.python.org/downloads/). 
    *   **Pazi:** Ko ga nameščaš, obvezno obkljukaj **"Add Python to PATH"**, sicer ga računalnik ne bo našel.
2.  **Namesti knjižnice:** Odpri *Ukazni poziv* (v iskanje vpiši `cmd`) in skopiraj tole notri:
    ```bash
    pip install streamlit pandas requests
    ```

---

## 📂 Kako pripraviš podatke

1.  V Trading 212 aplikaciji izvozi svoje transakcije v **CSV** formatu.
2.  Vse te datoteke preprosto vrzi v mapo `input`.
    *   **Nasvet:** Najbolje je, da skopiraš **vse CSV-je, odkar si začel trgovati**. Skripta potrebuje pretekle nakupe, da lahko pravilno izračuna nabavno ceno (**FIFO**) za tisto, kar si prodal letos.

---

## ⚙️ Nastavitve

V mapi imaš datoteko `settings.py`. Odpri jo z Beležnico (Notepad) in vpiši svoje podatke (davčno številko, ime, naslov ...), da bodo eDavki vedeli, čigava je napoved. Nastavi tudi `TAX_YEAR` na leto, za katero oddajaš (npr. 2025).

---

## ⚡ Zagon in uporaba

1.  Pojdi v mapo, kjer imaš skripto. Zgoraj v naslovno vrstico raziskovalca vpiši **cmd** in pritisni Enter.
2.  V črno okno vpiši:
    ```bash
    streamlit run app.py
    ```
3.  V brskalniku se ti bo odprla spletna stran. Tam boš videl:
    *   **Koliko si dejansko zaslužil** (tvoj realni profit).
    *   **Kakšna je osnova za davek po FURS-u** (upošteva se FIFO in 1 % normiranih stroškov).
    *   **Kaj imaš še na zalogi** (tvoj portfelj).

Na koncu v levem meniju klikni na gumb **Prenesi XML** in to datoteko naloži na eDavke pod obrazec Doh-KDVP.

---

## 💡 Zakaj je to fajn?

- **ECB tečaji:** Skripta sama pobere uradne tečaje z interneta, tako da ti ni treba nič preračunavati.
- **Manjši davek:** Avtomatsko upošteva 1 % stroškov pri nakupu in 1 % pri prodaji, kar ti malo zniža davčno osnovo.
- **Stock Splits:** Če si imel Nvidio leta 2024, veš, da so delili delnice 1:10. Skripta to upošteva, da ne boš v minusu s količino.
- **Dividende:** Poseben zavihek ti pripravi pregled dividend, da lažje izpolniš še obrazec Doh-Div.

---

### ☕ Častim kavo?

Če ti je skripta prihranila par ur živcev in kakšen evro pri davkih, bom vesel donacije za kavo!

👉 **[Doniraj preko PayPal](https://www.paypal.com/donate/?hosted_button_id=X35CTXP8REUVQ)**

---
Trading 212 Dashboard | Created by Žan Vranešič

**Opozorilo:** To je le pripomoček. Preden oddaš na eDavke, preveri, če se številke ujemajo s tvojim dejanskim stanjem. Za tvojo davčno napoved si odgovoren sam.
