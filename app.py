import streamlit as st
import pandas as pd
import requests
import io
import os
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import deque

try:
    import settings
except ImportError:
    st.error("Nastavitve (settings.py) niso na voljo!")
    st.stop()


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
    except:
        return None


def format_high_precision(val):
    return f"{float(val):.8f}".rstrip('0').rstrip('.')


st.set_page_config(page_title="T212 Dashboard", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    header {visibility: hidden;}
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #1f77b4; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #262730; 
        border-radius: 5px 5px 0px 0px; 
        padding: 10px 20px;
        color: white !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #464855 !important; 
        border-bottom: 2px solid #ff4b4b !important;
    }
    .fixed-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117;
        color: #808495;
        text-align: center;
        padding: 15px 0;
        font-size: 14px;
        border-top: 1px solid #31333F;
        z-index: 1000;
    }
    .main .block-container {
        padding-bottom: 100px;
        padding-top: 2rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Trading 212: Preglednica za eDavke")

if not os.path.exists(settings.INPUT_FOLDER):
    st.error(f"Mapa {settings.INPUT_FOLDER} ne obstaja!")
    st.stop()

csv_files = [f for f in os.listdir(
    settings.INPUT_FOLDER) if f.endswith('.csv')]

if not csv_files:
    st.warning(f"V mapi `{settings.INPUT_FOLDER}` ni CSV datotek.")
else:
    rates_df = fetch_ecb_rates()
    all_dfs = [pd.read_csv(os.path.join(settings.INPUT_FOLDER, file))
               for file in csv_files]
    df = pd.concat(all_dfs, ignore_index=True)
    df['Time'] = pd.to_datetime(df['Time']).dt.floor('s')
    df = df.drop_duplicates(
        subset=['Time', 'Action', 'ISIN', 'No. of shares', 'Price / share'])
    df = df.sort_values('Time')
    df_trades = df[df['Action'].str.contains(
        'buy|sell', case=False, na=False)].copy()

    for isin, split_date, ratio in settings.STOCK_SPLITS:
        split_dt = pd.to_datetime(split_date)
        mask = (df_trades['ISIN'] == isin) & (df_trades['Time'] < split_dt)
        df_trades.loc[mask, 'No. of shares'] = df_trades.loc[mask,
                                                             'No. of shares'] * ratio
        df_trades.loc[mask, 'Price / share'] = df_trades.loc[mask,
                                                             'Price / share'] / ratio

    df_trades['Date_only'] = df_trades['Time'].dt.normalize()
    df_trades = pd.merge_asof(
        df_trades, rates_df, left_on='Date_only', right_on='Date', direction='backward')

    def to_eur(row):
        curr = row['Currency (Price / share)']
        val = float(row['Price / share'])
        if curr == 'EUR':
            return val
        if curr == 'USD':
            return val / row['USD']
        if curr == 'GBP':
            return val / row['GBP']
        if curr == 'GBX':
            return (val / 100) / row['GBP']
        return val

    df_trades['Price_EUR'] = df_trades.apply(to_eur, axis=1)
    df_trades['Year_val'] = df_trades['Time'].dt.year

    with st.sidebar:
        st.header("⚙️ Nastavitve")
        selected_year = st.number_input(
            "Izberi davčno leto", value=settings.TAX_YEAR, step=1)
        st.subheader("👤 Osebni podatki")
        st.info(
            f"**Ime:** {settings.NAME}\n\n**Davčna:** {settings.TAX_NUMBER}")
        st.divider()

    inventory = {}
    yearly_stats = {}
    total_real_pl = 0.0
    total_furs_pl = 0.0

    for _, row in df_trades.iterrows():
        isin = row['ISIN']
        qty = float(row['No. of shares'])
        price_eur = float(row['Price_EUR'])
        is_buy = "buy" in row['Action'].lower()

        if isin not in inventory:
            inventory[isin] = deque()
        if isin not in yearly_stats:
            yearly_stats[isin] = {
                'ticker': row['Ticker'], 'real': 0.0, 'furs': 0.0}

        if is_buy:
            inventory[isin].append(
                {'qty': qty, 'price': price_eur, 'time': row['Time'], 'year': row['Year_val']})
        else:
            temp_qty = qty
            while temp_qty > 0 and inventory[isin]:
                oldest_buy = inventory[isin][0]
                sell_from_this_batch = min(temp_qty, oldest_buy['qty'])
                if row['Year_val'] == selected_year:
                    real_p = (
                        price_eur - oldest_buy['price']) * sell_from_this_batch
                    furs_p = (price_eur * 0.99 -
                              oldest_buy['price'] * 1.01) * sell_from_this_batch
                    yearly_stats[isin]['real'] += real_p
                    yearly_stats[isin]['furs'] += furs_p
                    total_real_pl += real_p
                    total_furs_pl += furs_p
                oldest_buy['qty'] -= sell_from_this_batch
                temp_qty -= sell_from_this_batch
                if oldest_buy['qty'] <= 1e-9:
                    inventory[isin].popleft()

    st.success("Obdelava zaključena!")
    c1, c2, c3 = st.columns(3)
    c1.metric("Realni P/L", f"{total_real_pl:,.2f} €")
    c2.metric("FURS Davčna osnova", f"{total_furs_pl:,.2f} €")
    davek = max(0, total_furs_pl * 0.25)
    c3.metric("Predviden davek (25%)", f"{davek:,.2f} €")

    tab1, tab2 = st.tabs(
        ["📑 Trgovanje v letu " + str(selected_year), "💰 Trenutni Portfelj"])

    with tab1:
        st.subheader("Dobiček/izguba po delnicah")
        res_data = []
        for isin, data in yearly_stats.items():
            if abs(data['real']) > 0.01:
                res_data.append({
                    "Ticker": data['ticker'],
                    "Realni P/L (€)": data['real'],
                    "FURS P/L (€)": data['furs']
                })
        if res_data:
            res_df = pd.DataFrame(res_data)

            def style_pl(v):
                return f'color: {"#22c55e" if v >= 0 else "#ef4444"}; font-weight: bold;'
            st.dataframe(
                res_df.style.format(
                    subset=['Realni P/L (€)', 'FURS P/L (€)'], formatter="{:.2f}")
                .applymap(style_pl, subset=['Realni P/L (€)', 'FURS P/L (€)']),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("V tem letu ni bilo prodaj.")

    with tab2:
        st.subheader("Zaloga delnic na računu")
        port_data = []
        for isin, batches in inventory.items():
            rem_qty = sum(b['qty'] for b in batches)
            if rem_qty > 0.0001:
                ticker = df_trades[df_trades['ISIN'] == isin]['Ticker'].iloc[0]
                book_val = sum(b['qty'] * b['price'] for b in batches)
                port_data.append({
                    "Ticker": ticker,
                    "Količina": round(rem_qty, 5),
                    "Nabavna vrednost (€)": round(book_val, 2)
                })
        if port_data:
            st.dataframe(pd.DataFrame(port_data),
                         use_container_width=True, hide_index=True)
        else:
            st.write("Portfelj je prazen.")

    def generate_xml():
        NS_EDP = "http://edavki.durs.si/Documents/Schemas/EDP-Common-1.xsd"
        NS_MAIN = "http://edavki.durs.si/Documents/Schemas/Doh_KDVP_9.xsd"
        ET.register_namespace('edp', NS_EDP)
        ET.register_namespace('', NS_MAIN)
        root = ET.Element(f"{{{NS_MAIN}}}Envelope")
        header = ET.SubElement(root, f"{{{NS_EDP}}}Header")
        taxpayer = ET.SubElement(header, f"{{{NS_EDP}}}taxpayer")
        ET.SubElement(
            taxpayer, f"{{{NS_EDP}}}taxNumber").text = settings.TAX_NUMBER
        ET.SubElement(taxpayer, f"{{{NS_EDP}}}taxpayerType").text = "FO"
        ET.SubElement(taxpayer, f"{{{NS_EDP}}}name").text = settings.NAME
        ET.SubElement(
            taxpayer, f"{{{NS_EDP}}}address1").text = settings.ADDRESS
        ET.SubElement(taxpayer, f"{{{NS_EDP}}}city").text = settings.CITY
        ET.SubElement(
            taxpayer, f"{{{NS_EDP}}}postNumber").text = settings.POST_NUMBER
        ET.SubElement(
            taxpayer, f"{{{NS_EDP}}}postName").text = settings.POST_NAME
        ET.SubElement(root, f"{{{NS_EDP}}}AttachmentList")
        ET.SubElement(root, f"{{{NS_EDP}}}Signatures")
        body = ET.SubElement(root, f"{{{NS_MAIN}}}body")
        ET.SubElement(body, f"{{{NS_EDP}}}bodyContent")
        doh_kdvp = ET.SubElement(body, f"{{{NS_MAIN}}}Doh_KDVP")

        sold_isins = df_trades[(df_trades['Action'].str.contains('sell', case=False)) & (
            df_trades['Year_val'] == selected_year)]['ISIN'].unique()

        kdvp = ET.SubElement(doh_kdvp, f"{{{NS_MAIN}}}KDVP")
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}DocumentWorkflowID").text = "O"
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}Year").text = str(selected_year)
        ET.SubElement(
            kdvp, f"{{{NS_MAIN}}}PeriodStart").text = f"{selected_year}-01-01"
        ET.SubElement(
            kdvp, f"{{{NS_MAIN}}}PeriodEnd").text = f"{selected_year}-12-31"
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}IsResident").text = "true"
        ET.SubElement(
            kdvp, f"{{{NS_MAIN}}}TelephoneNumber").text = settings.PHONE
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}SecurityCount").text = str(
            len(sold_isins))

        # VRSTNI RED JE POMEMBEN: Vsi števci morajo biti pred Emailom
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}SecurityShortCount").text = "0"
        ET.SubElement(
            kdvp, f"{{{NS_MAIN}}}SecurityWithContractCount").text = "0"
        ET.SubElement(
            kdvp, f"{{{NS_MAIN}}}SecurityWithContractShortCount").text = "0"
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}ShareCount").text = "0"
        ET.SubElement(
            kdvp, f"{{{NS_MAIN}}}SecurityCapitalReductionCount").text = "0"
        ET.SubElement(kdvp, f"{{{NS_MAIN}}}Email").text = settings.EMAIL

        for isin in sold_isins:
            ticker = df_trades[df_trades['ISIN'] == isin]['Ticker'].iloc[0]
            k_item = ET.SubElement(doh_kdvp, f"{{{NS_MAIN}}}KDVPItem")
            ET.SubElement(
                k_item, f"{{{NS_MAIN}}}InventoryListType").text = "PLVP"
            ET.SubElement(
                k_item, f"{{{NS_MAIN}}}Name").text = f"{ticker} | {isin}"
            ET.SubElement(k_item, f"{{{NS_MAIN}}}HasForeignTax").text = "false"
            sec = ET.SubElement(k_item, f"{{{NS_MAIN}}}Securities")
            ET.SubElement(sec, f"{{{NS_MAIN}}}ISIN").text = str(isin)
            ET.SubElement(
                sec, f"{{{NS_MAIN}}}Name").text = f"{ticker} | {isin}"
            ET.SubElement(sec, f"{{{NS_MAIN}}}IsFond").text = "false"

            temp_inv = deque()
            xml_rows = []
            group = df_trades[df_trades['ISIN'] == isin].copy()

            for _, row in group.iterrows():
                q = float(row['No. of shares'])
                buy = "buy" in row['Action'].lower()
                if buy:
                    temp_inv.append(
                        {'qty': q, 'price': row['Price_EUR'], 'time': row['Time'], 'year': row['Year_val']})
                    if row['Year_val'] == selected_year:
                        xml_rows.append(
                            {'type': 'B', 'date': row['Time'], 'qty': q, 'price': row['Price_EUR']})
                else:
                    t_qty = q
                    while t_qty > 0 and temp_inv:
                        o_buy = temp_inv[0]
                        take = min(t_qty, o_buy['qty'])
                        if o_buy['year'] < selected_year and row['Year_val'] == selected_year:
                            if not any(x['type'] == 'B' and x['date'] == o_buy['time'] for x in xml_rows):
                                xml_rows.append(
                                    {'type': 'B', 'date': o_buy['time'], 'qty': o_buy['qty'], 'price': o_buy['price']})
                        o_buy['qty'] -= take
                        t_qty -= take
                        if o_buy['qty'] <= 1e-9:
                            temp_inv.popleft()
                    if row['Year_val'] == selected_year:
                        xml_rows.append(
                            {'type': 'S', 'date': row['Time'], 'qty': q, 'price': row['Price_EUR']})

            xml_rows.sort(key=lambda x: x['date'])
            run_qty = 0.0
            for idx, xr in enumerate(xml_rows):
                row_el = ET.SubElement(sec, f"{{{NS_MAIN}}}Row")
                ET.SubElement(row_el, f"{{{NS_MAIN}}}ID").text = str(idx)
                if xr['type'] == 'B':
                    run_qty += xr['qty']
                    p = ET.SubElement(row_el, f"{{{NS_MAIN}}}Purchase")
                    ET.SubElement(p, f"{{{NS_MAIN}}}F1").text = xr['date'].strftime(
                        '%Y-%m-%d')
                    ET.SubElement(p, f"{{{NS_MAIN}}}F2").text = "B"
                    ET.SubElement(
                        p, f"{{{NS_MAIN}}}F3").text = format_high_precision(xr['qty'])
                    ET.SubElement(p, f"{{{NS_MAIN}}}F4").text = format_high_precision(
                        xr['price'])
                    ET.SubElement(p, f"{{{NS_MAIN}}}F5").text = "0.0000"
                else:
                    run_qty -= xr['qty']
                    s = ET.SubElement(row_el, f"{{{NS_MAIN}}}Sale")
                    ET.SubElement(s, f"{{{NS_MAIN}}}F6").text = xr['date'].strftime(
                        '%Y-%m-%d')
                    ET.SubElement(
                        s, f"{{{NS_MAIN}}}F7").text = format_high_precision(xr['qty'])
                    ET.SubElement(s, f"{{{NS_MAIN}}}F9").text = format_high_precision(
                        xr['price'])
                ET.SubElement(row_el, f"{{{NS_MAIN}}}F8").text = format_high_precision(
                    max(0, run_qty))

        xml_str = ET.tostring(root, encoding='utf-8')
        return minidom.parseString(xml_str).toprettyxml(indent="\t").replace('xmlns:default', 'xmlns')

    current_sold_isins = df_trades[(df_trades['Action'].str.contains(
        'sell', case=False)) & (df_trades['Year_val'] == selected_year)]['ISIN'].unique()

    if len(current_sold_isins) > 0:
        if not os.path.exists(settings.OUTPUT_FOLDER):
            os.makedirs(settings.OUTPUT_FOLDER)
        xml_data = generate_xml()
        base_name = f"Doh_KDVP_{selected_year}"
        out_path = os.path.join(settings.OUTPUT_FOLDER, f"{base_name}.xml")
        if os.path.exists(out_path):
            counter = 1
            while os.path.exists(os.path.join(settings.OUTPUT_FOLDER, f"{base_name}_v{counter:02d}.xml")):
                counter += 1
            out_path = os.path.join(
                settings.OUTPUT_FOLDER, f"{base_name}_v{counter:02d}.xml")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml_data)
        st.sidebar.info(f"📁 Shranjeno v: {os.path.basename(out_path)}")
        with st.sidebar:
            st.download_button(
                label="📥 Prenesi XML za eDavke",
                data=xml_data,
                file_name=os.path.basename(out_path),
                mime="application/xml",
                use_container_width=True
            )
    else:
        with st.sidebar:
            st.warning("Ni prodaj v izbranem letu.")

st.markdown("""
    <div class="fixed-footer">
        Trading 212 Dashboard | Created by Žan Vranešič
    </div>
    """, unsafe_allow_html=True)
