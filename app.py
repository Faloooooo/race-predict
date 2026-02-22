import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V62.2 - Ultimate Victory", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1], data.columns[8]])
    except: return pd.DataFrame()

df = load_data()

tab1, tab2 = st.tabs(["🚀 كونسول الفوز المباشر", "🔬 مختبر كشف الغدر"])

with tab1:
    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>🛡️ محرك التوقع المزدوج V62.2</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        # حساب الدقة العامة
        recent = df.tail(100)
        acc = (len(recent[recent.iloc[:, 8] == recent.iloc[:, 9]]) / len(recent) * 100) if not recent.empty else 0
        m1, m2 = st.columns(2)
        m1.metric("📊 حجم الداتا", len(df))
        m2.metric("📈 قوة الخوارزمية", f"{acc:.1f}%")

    st.divider()
    
    # نموذج الإدخال (ثبات كامل)
    with st.form("input_and_predict"):
        st.subheader("🏁 أدخل معطيات الجولة")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        ci = st.columns([1, 2])
        vp = ci[0].radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True)
        vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        submit_btn = st.form_submit_button("⚡ استخراج خطة الفوز", use_container_width=True)

    if submit_btn:
        pos_map = {"L": 4, "C": 5, "R": 6}
        matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
        
        if not matches.empty:
            # 1. التوقع الأول (الأكثر تكراراً)
            counts = matches.iloc[:, 8].value_counts()
            p1 = counts.idxmax()
            
            # 2. التوقع الثاني (التراتبية)
            last_winner = matches.iloc[-1, 8]
            remaining = [v for v in [v1, v2, v3] if v != last_winner]
            p2 = remaining[0] if remaining else v1
            
            # 3. كاشف الـ LP
            lp_match = matches[matches.iloc[:, 7] == matches.iloc[:, 8]]
            lp_acc = (len(lp_match) / len(matches)) * 100

            st.markdown(f"""
            <div style="display: flex; justify-content: space-around; gap: 10px;">
                <div style="text-align: center; border: 2px solid #00FFCC; padding: 10px; border-radius: 10px; flex: 1;">
                    <h4 style="margin:0;">🥇 الخيار الأول (القوة)</h4>
                    <h2 style="color: #00FFCC;">{p1}</h2>
                </div>
                <div style="text-align: center; border: 2px solid #FFCC00; padding: 10px; border-radius: 10px; flex: 1;">
                    <h4 style="margin:0;">🥈 الخيار الثاني (الدور)</h4>
                    <h2 style="color: #FFCC00;">{p2}</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if lp_acc > 65:
                st.success(f"💎 هذا النمط 'مطيع' للـ LP بنسبة {lp_acc:.0f}%. اتبع المسار الأطول.")
            else:
                st.warning(f"⚠️ هذا النمط 'غدار' للـ LP بنسبة {100-lp_acc:.0f}%. اعتمد على التوقعات أعلاه.")
        else:
            st.info("🆕 نمط جديد - التوقع الافتراضي: " + v1)

    st.divider()
    
    # نموذج الترحيل (ثبات وبالونات)
    with st.form("save_form"):
        st.subheader("📥 تدوين النتيجة النهائية")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp_val = st.radio("الأطول (LP)", ["L", "C", "R"], horizontal=True)
        actual_w = st.selectbox("الفائز الفعلي", [v1, v2, v3])
        
        if st.form_submit_button("🚀 ترحيل وحفظ", use_container_width=True):
            # الكود يرسل التوقع الأول تلقائياً للشيت
            # ... (منطق الـ Payload كما هو في V62.1)
            st.balloons()
            st.success("✅ تم الحفظ بنجاح!")
            time.sleep(2)
            st.rerun()

# --- التاب الثاني (كما هو لا تغيير) ---
