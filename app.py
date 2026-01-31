import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Genius Race AI", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- خوارزمية كسر التشفير ---
def deep_intelligence(v1, v2, v3, v_pos, v_type, data):
    if data.empty or len(data) < 2:
        return v1
    
    # 1. التنبؤ بالطريق القادم (Sequential Road Prediction)
    last_road = data.iloc[-1, 4 if v_pos=="L" else 5 if v_pos=="C" else 6]
    # البحث عن المرات التي ظهر فيها هذا الطريق سابقاً وماذا تبعه
    next_road_probs = data[data.shift(1).iloc[:, 4 if v_pos=="L" else 5 if v_pos=="C" else 6] == last_road]
    
    # 2. تحليل "المسار الأطول" التاريخي
    # هل هناك سيارة معينة تفوز دائماً عندما يكون مسارها هو الأطول؟
    longer_path_history = data[data.iloc[:, 7] == v_pos] # العمود H هو Longer Path
    
    # 3. حساب الوزن (Scoring)
    candidates = {v1: 0, v2: 0, v3: 0}
    for c in candidates:
        # وزن الفوز العام
        candidates[c] += len(data[data.iloc[:, 8] == c]) * 1 
        # وزن الفوز في هذا الطريق تحديداً
        candidates[c] += len(data[(data.iloc[:, 4 if v_pos=="L" else 5 if v_pos=="C" else 6] == v_type) & (data.iloc[:, 8] == c)]) * 3
    
    return max(candidates, key=candidates.get)

# --- الواجهة ---
st.title("🚀 محرك كسر خوارزمية السباق")

if not df.empty:
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("قوة الداتا التاريخية", f"{len(df)} جولة")
    with col_stat2:
        last_winner = df.iloc[-1, 8]
        st.write(f"آخر فائز مسجل: **{last_winner}**")

st.divider()

# المدخلات
with st.container(border=True):
    c = st.columns(3)
    v1 = c[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    prediction = deep_intelligence(v1, v2, v3, vp, vt, df)
    st.subheader(f"🔮 التوقع المبني على التراتبية: :green[{prediction}]")

# التسجيل
with st.expander("📝 تسجيل بيانات لكسر الخوارزمية"):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    lp = st.radio("أيهما كان الطريق الأطول؟", ["L", "C", "R"], horizontal=True)
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 معالجة وحفظ الجولة", use_container_width=True):
    r_map = {vp: vt, others[0]: h1_t, others[1]: h2_t}
    payload = {
        "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
        "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
        "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(prediction)
    }
    if requests.post(FORM_URL, data=payload).ok:
        st.success("تم تحديث قاعدة البيانات!")
        st.cache_data.clear()
        st.rerun()
