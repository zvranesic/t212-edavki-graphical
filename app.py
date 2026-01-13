import streamlit as st
import pandas as pd
import requests
import io
import os
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import deque

# --- KONFIGURACIJA ---
st.set_page_config(page_title="T212 - Poročanje davkov", layout="wide", page_icon="📈")

try:
    import user_settings
except ImportError:
    st.error("Nastavitve (user_settings.py) niso na voljo!")
    st.stop()

# --- CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 0% 0%, #131722 0%, #080a0f 50%),
                    radial-gradient(circle at 100% 100%, #0d1117 0%, #080a0f 50%);
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    .hero-title {
        font-size: 3.5rem; font-weight: 800; letter-spacing: -1.5px;
        background: linear-gradient(135deg, #ffffff 30%, #00d1ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem; line-height: 1.1;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.02); 
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; 
        padding: 24px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.2); 
        margin-bottom: 20px;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.015); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px; padding: 20px !important;
    }

    [data-testid="stMetricValue"] { color: #00d1ff !important; font-size: 2.4rem !important; font-weight: 700 !important; }

    .fixed-footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: rgba(8, 10, 15, 0.9); color: #464855;
        text-align: center; padding: 16px 0; font-size: 0.85rem;
        border-top: 1px solid rgba(255,255,255,0.05); z-index: 1000;
    }

    /* Večji napisi za leto obdelave */
    .stNumberInput label {
        font-size: 1.1rem !important;
        color: #808495 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- POMOŽNE FUNKCIJE ---
def fetch_ecb_rates():
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
    try:
        response = requests.get(url, timeout=10)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open('eurofxref-hist.csv') as f:
                rates_df = pd.read_csv(f)
        rates_df = rates_df[['Date', 'USD', 'GBP']]
        rates_df['Date'] = pd.to_datetime(rates_df['Date'])
        return rates_df.sort_values('Date').ffill()
    except: return None

def to_eur(row, col_val, col_curr, rates_df):
    val = float(row[col_val]) if pd.notnull(row[col_val]) else 0.0
    curr = row[col_curr]
    if curr == 'EUR': return val
    if curr == 'USD': return val / row['USD']
    if curr == 'GBP': return val / row['GBP']
    if curr == 'GBX': return (val / 100) / row['GBP']
    return val

def format_hp(val):
    return f"{float(val):.8f}".rstrip('0').rstrip('.')

# --- GLAVNA STRUKTURA ---
side_col, main_col = st.columns([1, 3.8], gap="large")

with side_col:
    st.markdown("<h2 style='color: white; font-weight: 700; font-size: 2rem;'>⚙️ Nastavitve</h2>", unsafe_allow_html=True)
    selected_year = st.number_input("Leto obdelave", value=user_settings.TAX_YEAR, step=1)
    kdvp_f = f"Doh_KDVP_{selected_year}.xml"
    div_f = f"Doh_Div_{selected_year}.xml"

    st.markdown(f"""
    <div class="glass-card">
        <p style="color:#808495; font-size:0.9rem; letter-spacing: 1px; font-weight: 600;">PROFIL</p>
        <p style="color:white; font-weight:800; font-size:1.5rem; margin:0; line-height: 1.2;">{user_settings.NAME}</p>
        <p style="color:#00d1ff; font-size:1.2rem; font-weight:700; margin:0;">{user_settings.TAX_NUMBER}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="padding: 20px; background: rgba(0, 209, 255, 0.03); border: 1px solid rgba(0, 209, 255, 0.15);">
        <p style="margin: 0; font-size: 1.1rem; color: #00d1ff; font-weight: 800;">📈 Doh-KDVP</p>
        <code style="font-size: 0.9rem; color: #808495; background: none;">{kdvp_f}</code>
    </div>
    <div class="glass-card" style="padding: 20px; margin-top: -10px; background: rgba(0, 209, 255, 0.03); border: 1px solid rgba(0, 209, 255, 0.15);">
        <p style="margin: 0; font-size: 1.1rem; color: #00d1ff; font-weight: 800;">💰 Doh-Div</p>
        <code style="font-size: 0.9rem; color: #808495; background: none;">{div_f}</code>
    </div>
    """, unsafe_allow_html=True)

with main_col:
    st.markdown("<h1 class='hero-title'>Trading212 - Poročanje davkov</h1>", unsafe_allow_html=True)
    rates_df = fetch_ecb_rates()
    csv_files = [f for f in os.listdir(user_settings.INPUT_FOLDER) if f.endswith('.csv')]

    if not csv_files:
        st.info("V mapo 'input' naložite Trading 212 CSV izpiske.")
    else:
        all_dfs = [pd.read_csv(os.path.join(user_settings.INPUT_FOLDER, f)) for f in csv_files]
        df = pd.concat(all_dfs, ignore_index=True)
        df['Time'] = pd.to_datetime(df['Time']).dt.floor('s')
        df['Date_only'] = df['Time'].dt.normalize()
        df = pd.merge_asof(df.sort_values('Time'), rates_df, left_on='Date_only', right_on='Date', direction='backward')

        df_trades = df[df['Action'].str.contains('buy|sell', case=False, na=False)].copy()
        for isin, s_date, ratio in user_settings.STOCK_SPLITS:
            mask = (df_trades['ISIN'] == isin) & (df_trades['Time'] < pd.to_datetime(s_date))
            df_trades.loc[mask, 'No. of shares'] *= ratio
            df_trades.loc[mask, 'Price / share'] /= ratio
        
        df_trades['Price_EUR'] = df_trades.apply(lambda r: to_eur(r, 'Price / share', 'Currency (Price / share)', rates_df), axis=1)
        all_buys = df_trades[df_trades['Action'].str.contains('buy', case=False)].copy()

        # LOGIKE OBRAČUNA
        fifo_inventory = {}   # Za FURS (FIFO)
        avg_inventory = {}    # Za REALNI P/L (Average Cost)
        tax_bins = {0.25: 0.0, 0.20: 0.0, 0.15: 0.0, 0.0: 0.0}
        kdvp_results = []
        total_real_pl, total_furs_pl = 0.0, 0.0
        sold_isins = set()
        eoy = pd.Timestamp(year=selected_year, month=12, day=31, hour=23, minute=59)

        for _, row in df_trades.sort_values('Time').iterrows():
            if row['Time'] > eoy: continue
            isin = row['ISIN']
            qty, price = float(row['No. of shares']), float(row['Price_EUR'])
            
            if isin not in fifo_inventory: fifo_inventory[isin] = deque()
            if isin not in avg_inventory: avg_inventory[isin] = {'total_qty': 0.0, 'total_cost': 0.0}

            if "buy" in row['Action'].lower():
                fifo_inventory[isin].append({'qty': qty, 'price': price, 'time': row['Time'], 'year': row['Time'].year})
                avg_inventory[isin]['total_qty'] += qty
                avg_inventory[isin]['total_cost'] += qty * price
            else:
                # 1. REALNI P/L
                current_avg_price = avg_inventory[isin]['total_cost'] / avg_inventory[isin]['total_qty'] if avg_inventory[isin]['total_qty'] > 0 else price
                if row['Time'].year == selected_year:
                    total_real_pl += (price - current_avg_price) * qty
                
                avg_inventory[isin]['total_qty'] -= qty
                avg_inventory[isin]['total_cost'] -= qty * current_avg_price

                # 2. FURS OSNOVA
                rem_qty = qty
                if row['Time'].year == selected_year: sold_isins.add(isin)
                while rem_qty > 0 and fifo_inventory[isin]:
                    batch = fifo_inventory[isin][0]; take = min(rem_qty, batch['qty'])
                    if row['Time'].year == selected_year:
                        f_pl = (price * 0.99 - batch['price'] * 1.01) * take
                        if f_pl < 0:
                            wash_buy = all_buys[(all_buys['ISIN'] == isin) & (all_buys['Time'] > row['Time']) & (all_buys['Time'] <= row['Time'] + pd.Timedelta(days=30))]
                            if not wash_buy.empty: f_pl = 0.0 
                        
                        diff_years = (row['Time'] - batch['time']).days / 365.25
                        rate = 0.25 if diff_years < 5 else 0.20 if diff_years < 10 else 0.15 if diff_years < 15 else 0.0
                        
                        total_furs_pl += f_pl
                        tax_bins[rate] += f_pl
                        kdvp_results.append({'Ticker': row['Ticker'], 'Realni P/L': (price - current_avg_price) * take, 'FURS P/L': f_pl})
                    
                    batch['qty'] -= take; rem_qty -= take
                    if batch['qty'] <= 1e-9: fifo_inventory[isin].popleft()

        total_tax_predicted = 0.0
        if total_furs_pl > 0:
            pos_gain_sum = sum(v for v in tax_bins.values() if v > 0)
            if pos_gain_sum > 0:
                reduction_factor = max(0, total_furs_pl / pos_gain_sum)
                total_tax_predicted = sum(v * k * reduction_factor for k, v in tax_bins.items() if v > 0)

        def generate_kdvp_xml():
            NS_EDP, NS_MAIN = "http://edavki.durs.si/Documents/Schemas/EDP-Common-1.xsd", "http://edavki.durs.si/Documents/Schemas/Doh_KDVP_9.xsd"
            ET.register_namespace('edp', NS_EDP); ET.register_namespace('', NS_MAIN)
            root = ET.Element(f"{{{NS_MAIN}}}Envelope")
            h = ET.SubElement(root, f"{{{NS_EDP}}}Header"); t = ET.SubElement(h, f"{{{NS_EDP}}}taxpayer")
            ET.SubElement(t, f"{{{NS_EDP}}}taxNumber").text = user_settings.TAX_NUMBER; ET.SubElement(t, f"{{{NS_EDP}}}taxpayerType").text = "FO"; ET.SubElement(t, f"{{{NS_EDP}}}name").text = user_settings.NAME
            ET.SubElement(t, f"{{{NS_EDP}}}address1").text = user_settings.ADDRESS; ET.SubElement(t, f"{{{NS_EDP}}}city").text = user_settings.CITY
            ET.SubElement(t, f"{{{NS_EDP}}}postNumber").text = user_settings.POST_NUMBER; ET.SubElement(t, f"{{{NS_EDP}}}postName").text = user_settings.POST_NAME
            ET.SubElement(root, f"{{{NS_EDP}}}AttachmentList"); ET.SubElement(root, f"{{{NS_EDP}}}Signatures")
            b = ET.SubElement(root, f"{{{NS_MAIN}}}body"); ET.SubElement(b, f"{{{NS_EDP}}}bodyContent")
            d = ET.SubElement(b, f"{{{NS_MAIN}}}Doh_KDVP"); k = ET.SubElement(d, f"{{{NS_MAIN}}}KDVP")
            ET.SubElement(k, f"{{{NS_MAIN}}}DocumentWorkflowID").text = "O"
            ET.SubElement(k, f"{{{NS_MAIN}}}Year").text = str(selected_year); ET.SubElement(k, f"{{{NS_MAIN}}}PeriodStart").text = f"{selected_year}-01-01"; ET.SubElement(k, f"{{{NS_MAIN}}}PeriodEnd").text = f"{selected_year}-12-31"
            ET.SubElement(k, f"{{{NS_MAIN}}}IsResident").text = "true"; ET.SubElement(k, f"{{{NS_MAIN}}}TelephoneNumber").text = user_settings.PHONE
            ET.SubElement(k, f"{{{NS_MAIN}}}SecurityCount").text = str(len(sold_isins))
            for tag in ["SecurityShortCount", "SecurityWithContractCount", "SecurityWithContractShortCount", "ShareCount", "SecurityCapitalReductionCount"]: ET.SubElement(k, f"{{{NS_MAIN}}}{tag}").text = "0"
            ET.SubElement(k, f"{{{NS_MAIN}}}Email").text = user_settings.EMAIL
            for isin in sold_isins:
                ticker = df_trades[df_trades['ISIN'] == isin]['Ticker'].iloc[0]
                ki = ET.SubElement(d, f"{{{NS_MAIN}}}KDVPItem")
                ET.SubElement(ki, f"{{{NS_MAIN}}}InventoryListType").text = "PLVP"; ET.SubElement(ki, f"{{{NS_MAIN}}}Name").text = f"{ticker} | {isin}"
                ET.SubElement(ki, f"{{{NS_MAIN}}}HasForeignTax").text = "false"
                sec = ET.SubElement(ki, f"{{{NS_MAIN}}}Securities"); ET.SubElement(sec, f"{{{NS_MAIN}}}ISIN").text = str(isin)
                ET.SubElement(sec, f"{{{NS_MAIN}}}Name").text = f"{ticker} | {isin}"; ET.SubElement(sec, f"{{{NS_MAIN}}}IsFond").text = "false"
                temp_inv, xml_rows = deque(), []
                for _, r in df_trades[df_trades['ISIN'] == isin].sort_values('Time').iterrows():
                    if r['Time'] > eoy: continue
                    p_e = to_eur(r, 'Price / share', 'Currency (Price / share)', rates_df)
                    if "buy" in r['Action'].lower():
                        temp_inv.append({'q': r['No. of shares'], 'p': p_e, 't': r['Time'], 'y': r['Time'].year})
                        if r['Time'].year == selected_year: xml_rows.append({'type': 'B', 'date': r['Time'], 'q': r['No. of shares'], 'p': p_e})
                    else:
                        t_q = r['No. of shares']
                        while t_q > 0 and temp_inv:
                            bb = temp_inv[0]; take = min(t_q, bb['q'])
                            if bb['y'] < selected_year and r['Time'].year == selected_year:
                                if not any(x['type']=='B' and x['date']==bb['t'] for x in xml_rows):
                                    xml_rows.append({'type': 'B', 'date': bb['t'], 'q': bb['q'], 'p': bb['p']})
                            bb['q'] -= take; t_q -= take
                            if bb['q'] <= 1e-9: temp_inv.popleft()
                        if r['Time'].year == selected_year: xml_rows.append({'type': 'S', 'date': r['Time'], 'q': r['No. of shares'], 'p': p_e})
                xml_rows.sort(key=lambda x: x['date']); run_q = 0.0
                for i, xr in enumerate(xml_rows):
                    rel = ET.SubElement(sec, f"{{{NS_MAIN}}}Row"); ET.SubElement(rel, f"{{{NS_MAIN}}}ID").text = str(i)
                    if xr['type'] == 'B':
                        run_q += xr['q']; p_el = ET.SubElement(rel, f"{{{NS_MAIN}}}Purchase")
                        ET.SubElement(p_el, f"{{{NS_MAIN}}}F1").text = xr['date'].strftime('%Y-%m-%d'); ET.SubElement(p_el, f"{{{NS_MAIN}}}F2").text = "B"
                        ET.SubElement(p_el, f"{{{NS_MAIN}}}F3").text = format_hp(xr['q']); ET.SubElement(p_el, f"{{{NS_MAIN}}}F4").text = format_hp(xr['p']); ET.SubElement(p_el, f"{{{NS_MAIN}}}F5").text = "0.0000"
                    else:
                        run_qty = run_q - xr['q']; s_el = ET.SubElement(rel, f"{{{NS_MAIN}}}Sale")
                        ET.SubElement(s_el, f"{{{NS_MAIN}}}F6").text = xr['date'].strftime('%Y-%m-%d'); ET.SubElement(s_el, f"{{{NS_MAIN}}}F7").text = format_hp(xr['q']); ET.SubElement(s_el, f"{{{NS_MAIN}}}F9").text = format_hp(xr['p'])
                        run_q = run_qty
                    ET.SubElement(rel, f"{{{NS_MAIN}}}F8").text = format_hp(max(0, run_q))
            return minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="\t").replace('xmlns:default', 'xmlns')

        def generate_div_xml():
            NS_EDP, NS_MAIN = "http://edavki.durs.si/Documents/Schemas/EDP-Common-1.xsd", "http://edavki.durs.si/Documents/Schemas/Doh_Div_3.xsd"
            ET.register_namespace('edp', NS_EDP); ET.register_namespace('', NS_MAIN)
            root = ET.Element(f"{{{NS_MAIN}}}Envelope")
            h = ET.SubElement(root, f"{{{NS_EDP}}}Header"); t = ET.SubElement(h, f"{{{NS_EDP}}}taxpayer")
            ET.SubElement(t, f"{{{NS_EDP}}}taxNumber").text = user_settings.TAX_NUMBER; ET.SubElement(t, f"{{{NS_EDP}}}taxpayerType").text = "FO"; ET.SubElement(t, f"{{{NS_EDP}}}name").text = user_settings.NAME
            ET.SubElement(root, f"{{{NS_EDP}}}AttachmentList"); ET.SubElement(root, f"{{{NS_EDP}}}Signatures")
            body = ET.SubElement(root, f"{{{NS_MAIN}}}body"); dd = ET.SubElement(body, f"{{{NS_MAIN}}}Doh_Div")
            ET.SubElement(dd, f"{{{NS_MAIN}}}Period").text = str(selected_year); ET.SubElement(dd, f"{{{NS_MAIN}}}EmailAddress").text = user_settings.EMAIL
            ET.SubElement(dd, f"{{{NS_MAIN}}}PhoneNumber").text = user_settings.PHONE; ET.SubElement(dd, f"{{{NS_MAIN}}}ResidentCountry").text = "SI"
            ET.SubElement(dd, f"{{{NS_MAIN}}}IsResident").text = "true"; ET.SubElement(dd, f"{{{NS_MAIN}}}Locked").text = "false"; ET.SubElement(dd, f"{{{NS_MAIN}}}SelfReport").text = "false"
            ET.SubElement(dd, f"{{{NS_MAIN}}}WfTypeU").text = "false"; ET.SubElement(dd, f"{{{NS_MAIN}}}Notes").text = ""
            for _, r in df_div_year.iterrows():
                div = ET.SubElement(body, f"{{{NS_MAIN}}}Dividend")
                ET.SubElement(div, f"{{{NS_MAIN}}}Date").text = r['Time'].strftime('%Y-%m-%d'); ET.SubElement(div, f"{{{NS_MAIN}}}PayerName").text = str(r['Ticker'])
                ET.SubElement(div, f"{{{NS_MAIN}}}Value").text = f"{r['Gross_EUR']:.2f}"; ET.SubElement(div, f"{{{NS_MAIN}}}ForeignTax").text = f"{r['Tax_EUR']:.2f}"
                isin = str(r['ISIN']); ET.SubElement(div, f"{{{NS_MAIN}}}SourceCountry").text = isin[:2] if len(isin) >= 2 else "US"
            return minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="\t").replace('xmlns:default', 'xmlns')

        if not os.path.exists(user_settings.OUTPUT_FOLDER): os.makedirs(user_settings.OUTPUT_FOLDER)
        if len(sold_isins) > 0:
            with open(os.path.join(user_settings.OUTPUT_FOLDER, kdvp_f), "w", encoding="utf-8") as f: f.write(generate_kdvp_xml())
        df_div_year = df[(df['Action'].str.contains('Dividend', case=False)) & (df['Time'].dt.year == selected_year)].copy()
        if not df_div_year.empty:
            df_div_year['Gross_EUR'] = df_div_year.apply(lambda r: to_eur(r, 'Total', 'Currency (Total)', rates_df), axis=1)
            df_div_year['Tax_EUR'] = df_div_year.apply(lambda r: to_eur(r, 'Withholding tax', 'Currency (Withholding tax)', rates_df), axis=1)
            with open(os.path.join(user_settings.OUTPUT_FOLDER, div_f), "w", encoding="utf-8") as f: f.write(generate_div_xml())

        st.success(f"Podatki za leto {selected_year} so obdelani.")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📑 KDVP Izračun", "💰 Dividende", "🏦 Obresti", "📦 Stanje Portfelja"])

        def style_pl(v):
            if isinstance(v, str) and '€' in v:
                try:
                    val = float(v.replace(' €', '').replace(',', ''))
                    return f'color: {"#22c55e" if val >= 0 else "#ff4b4b"}; font-weight: 700;'
                except: return ''
            return ''

        with tab1:
            m1, m2, m3 = st.columns(3)
            m1.metric("Realni P/L", f"{total_real_pl:,.2f} €", help="Zaslužek glede na povprečno nabavno ceno.")
            m2.metric("Osnova (FURS)", f"{total_furs_pl:,.2f} €", help="FIFO izračun z 1% normiranimi stroški.")
            m3.metric("Predviden davek", f"{total_tax_predicted:,.2f} €")
            if kdvp_results:
                res_df = pd.DataFrame(kdvp_results).groupby('Ticker').sum(numeric_only=True).reset_index()
                res_df['Realni P/L'] = res_df['Realni P/L'].map("{:,.2f} €".format)
                res_df['FURS P/L'] = res_df['FURS P/L'].map("{:,.2f} €".format)
                st.dataframe(res_df.style.map(style_pl), width="stretch", hide_index=True)

        with tab2:
            d_col1, d_col2 = st.columns(2)
            g_sum, t_sum = (df_div_year['Gross_EUR'].sum() if not df_div_year.empty else 0), (df_div_year['Tax_EUR'].sum() if not df_div_year.empty else 0)
            d_col1.metric("BRUTO DIVIDENDE", f"{g_sum:,.2f} €")
            d_col2.metric("PLAČAN TUJI DAVEK", f"{t_sum:,.2f} €")
            if not df_div_year.empty:
                disp = df_div_year[['Time', 'Ticker', 'Gross_EUR', 'Tax_EUR', 'ISIN']].copy()
                disp.columns = ['Datum', 'Ticker', 'Bruto (Value)', 'Plačan tuji davek', 'ISIN']
                st.dataframe(disp.style.format("{:.2f} €", subset=['Bruto (Value)', 'Plačan tuji davek']), width="stretch", hide_index=True)

        with tab3:
            df_int_year = df[(df['Action'].str.contains('Interest on cash', case=False)) & (df['Time'].dt.year == selected_year)].copy()
            int_sum = 0
            if not df_int_year.empty:
                df_int_year['Amount_EUR'] = df_int_year.apply(lambda r: to_eur(r, 'Total', 'Currency (Total)', rates_df), axis=1)
                int_sum = df_int_year['Amount_EUR'].sum()
            st.metric("Obresti na gotovino", f"{int_sum:,.2f} €")
            if not df_int_year.empty: st.dataframe(df_int_year[['Time', 'Amount_EUR']], width="stretch", hide_index=True)

        with tab4:
            p_data = []
            for isin, batches in fifo_inventory.items():
                qty = sum(b['qty'] for b in batches)
                if qty > 0.0001:
                    ticker = df_trades[df_trades['ISIN'] == isin]['Ticker'].iloc[0]
                    cost = sum(b['qty'] * b['price'] for b in batches)
                    p_data.append({"Ticker": ticker, "Količina": round(qty, 5), "Vrednost (€)": round(cost, 2)})
            if p_data: st.dataframe(pd.DataFrame(p_data), width="stretch", hide_index=True)

st.markdown('<div class="fixed-footer">Trading 212 Dashboard | Created by Žan Vranešič</div>', unsafe_allow_html=True)
