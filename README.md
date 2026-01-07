# 🚀 Trading 212 v eDavke (Doh-KDVP)

Ta skripta omogoča samodejno pripravo XML datoteke za oddajo napovedi davka od dobička iz kapitala (**Doh-KDVP**) na portalu eDavki. Namenjena je uporabnikom **Trading 212**, ki trgujejo z delnicami in ETF-ji. Zdaj s posodobljenim spletnim vmesnikom za boljšo preglednost.

---

## 🛠️ 1. Priprava (samo prvič)

1.  **Namesti Python:** Prenesi ga na [python.org](https://www.python.org/downloads/).
    -   **Zelo pomembno:** Ob začetku namestitve obvezno obkljukaj polje **"Add Python to PATH"**.
2.  **Namesti knjižnice:** Odpri _Ukazni poziv_ (CMD) in vpiši:
    ```bash
    pip install streamlit pandas requests
    ```

---

## 📂 2. Priprava podatkov

1.  **Izvoz iz Trading 212:** V aplikaciji izvozi transakcije v **CSV** formatu.
2.  **Kopiranje:** Vse CSV datoteke skopiraj v mapo `input`.
    -   **💡 Nasvet:** Skopiraj celotno zgodovino od začetka trgovanja. Skripta potrebuje pretekle nakupe, da pravilno izračuna nabavno ceno (**FIFO**) za prodaje v tekočem letu.

---

## ⚙️ 3. Nastavitve (`settings.py`)

Odpri datoteko `settings.py` z Beležnico in uredi:

-   `TAX_YEAR`: Leto, za katero oddajaš (npr. 2025).
-   `TAX_NUMBER`, `NAME`, `ADDRESS`...: Tvoji osebni podatki za obrazec.

---

## ⚡ 4. Zagon in rezultati

1.  V mapi s skripto v naslovno vrstico raziskovalca vpiši `cmd` in pritisni Enter.
2.  Vpiši ukaz za zagon spletnega vmesnika:
    ```bash
    streamlit run app.py
    ```
3.  **V brskalniku se bo odprl vmesnik, kjer boš videl:**
    -   **Realni dobiček:** Dejanski zaslužek na borzi (brez FURS stroškov).
    -   **FURS dobiček:** Osnova za davek (upošteva 1% normiranih stroškov).
    -   **Stanje portfelja:** Pregled delnic, ki jih še imaš v lasti.
    -   **Gumb za prenos XML:** Nahaja se v stranskem meniju na levi.

---

## 💡 Zakaj je ta skripta boljša od ročnega vnosa?

-   **Grafični vmesnik:** Pregledne tabele in takojšen izračun brez ukvarjanja s kodo.
-   **Samodejni ECB tečaji:** Skripta sama prenese uradne tečaje na dan posla neposredno z ECB.
-   **FIFO Metoda:** Pravilno upošteva vrstni red nakupov in prodaj.
-   **Davčni ščit:** Avtomatsko poveča nabavno vrednost za 1% in zmanjša prodajno za 1%, kar zniža davčno osnovo.
-   **Stock Splits:** Pravilno obravnava delitve delnic (npr. Nvidia 2024).

---

### ☕ Podpora in donacije

Če ti je skripta prihranila čas in denar, bom vesel donacije za kavo!

👉 **[Doniraj preko PayPal](https://www.paypal.com/donate/?hosted_button_id=X35CTXP8REUVQ)**

---

Trading 212 Dashboard | Created by Žan Vranešič

**Opozorilo:** Skripta je informativni pripomoček. Pred oddajo na eDavke obvezno preveri izračune. Avtor ne prevzema odgovornosti za morebitne napake v davčni napovedi.
