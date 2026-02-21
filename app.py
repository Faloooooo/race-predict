import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V80.0 - Precision Search", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_db()

# العدادات في القمة
if not df.empty:
    m1, m2 = st.columns(2)
    m1.metric("📊 إجمالي السجلات", len(df))
    recent_100 = df.tail(100)
    acc = (len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]]) / len(recent_100)) * 100 if len(recent_100) > 0 else 0
    m2.metric("📈 دقة النظام %", f"{acc:.1f}%")
st.divider()

tab1, tab2 = st.tabs(["🚀 غرفة التوقع والترحيل", "🔬 مختبر البحث عن نمط"])

# --- التاب الأول: غرفة التوقع ---
with tab1:
    with st.container(border=True):
        st.subheader("🏁 إدخال الجولة الحالية")
        c_cols = st.columns(3)
        v1 = c_cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c_cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c_cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        ir = st.columns([1, 2])
        vp = ir[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    p_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, p_map[vp]] == vt)]
    
    if not matches.empty:
        last_winner = matches.iloc[-1, 8]
        st.markdown(f"""<div style="text-align: center; border: 2px solid #00FFCC; border-radius: 10px; padding: 15px; background-color: #0E1117;">
        <h3 style="margin:0;">🎯 أحدث فوز لهذا النمط:</h3><h1 style="color:#00FFCC; font-size:50px; margin:5px;">{last_winner}</h1></div>""", unsafe_allow_html=True)
        
        st.write("📊 **إحصائيات تكرار الفوز:**")
        counts = matches.iloc[:, 8].value_counts()
        c_stats = st.columns(len(counts))
        for i, (car, count) in enumerate(counts.items()):
            c_stats[i].warning(f"**{car}**: {count} مرات")
    else:
        st.info("🆕 نمط جديد")

    with st.form("save_v80"):
        st.subheader("📥 ترحيل البيانات")
        # منطق الترحيل كما هو معتمد
        st.form_submit_button("🚀 حفظ التحديث")

# --- التاب الثاني: مختبر البحث (المطلوب بدقة) ---
with tab2:
    st.header("🔬 البحث عن نمط محدد")
    with st.container(border=True):
        st.write("🔎 حدد النمط الذي تريد البحث عنه في التاريخ:")
        f_cols = st.columns(3)
        fv1 = f_cols[0].selectbox("Car 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f1')
        fv2 = f_cols[1].selectbox("Car 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f2')
        fv3 = f_cols[2].selectbox("Car 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='f3')
        
        f_road = st.columns([1, 2])
        fvp = f_road[0].selectbox("جهة الطريق الظاهر", ["L", "C", "R"], key='fp')
        fvt = f_road[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='ft')

    # الفلترة بناءً على العناصر الخمسة فقط
    p_idx = {"L": 4, "C": 5, "R": 6}
    res = df[(df.iloc[:, 1] == fv1) & (df.iloc[:, 2] == fv2) & (df.iloc[:, 3] == fv3) & (df.iloc[:, p_idx[fvp]] == fvt)].copy()
    
    if not res.empty:
        st.success(f"✅ تم العثور على {len(res)} جولة مطابقة لهذا النمط")
        # عرض السيارات، الطريق الظاهر وجهته، ثم الفائز
        display_df = res.iloc[:, [1, 2, 3, p_idx[fvp], 8]].copy()
        display_df.columns = ['Car 1', 'Car 2', 'Car 3', 'نوع الطريق', 'الفائز الفعلي']
        display_df.insert(3, 'الجهة', fvp)
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("لم يسبق تدوين هذا النمط من قبل.")
