import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V32.0 - Inversion", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- محرك التحليل العكسي وكشف الغدر ---
def inversion_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2, v3, 0
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # 1. حساب النقاط التقليدية (التاريخية)
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        road_match = data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)]
        scores[car] += len(road_match) * 5.0
        scores[car] += len(data[data.iloc[:, 8] == car]) * 0.5

    # ترتيب من الأقوى للأضعف تاريخياً
    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p_strong = sorted_res[0][0] # الأقوى تاريخياً
    p_mid = sorted_res[1][0]    # المتوسط
    p_weak = sorted_res[2][0]   # الأضعف تاريخياً (التي قد تفوز غدراً)

    # 2. تحليل "نمط الغدر" في آخر 20 جولة
    last_20 = data.tail(20)
    # كم مرة فازت السيارة التي لم تكن هي التوقع الأول؟
    betrayal_count = len(last_20[last_20.iloc[:, 8] != last_20.iloc[:, 9]])
    betrayal_rate = (betrayal_count / 20) * 100

    return p_strong, p_mid, p_weak, betrayal_rate

# --- واجهة العرض ---
st.title("🔄 المحرك العكسي وكاشف الغدر V32.0")

if not df.empty:
    total = len(df)
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الجولات الكلية", total)
    c2.metric("دقة التوقع التقليدي", f"{rate:.1f}%")
    c3.metric("حالة الخوارزمية", "تحليل عكسي 🔍")

st.divider()

# المدخلات
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    strong, mid, weak, b_rate = inversion_logic(v1, v2, v3, vp, vt, df)
    
    st.write("---")
    st.subheader(f"📊 تحليل الجولة (نسبة احتمال الغدر: {b_rate:.0f}%)")
    
    r1, r2, r3 = st.columns(3)
    r1.success(f"🥇 المرشح التاريخي:\n**{strong}**")
    r2.info(f"🥈 الخيار البديل:\n**{mid}**")
    r3.warning(f"⚠️ سيارة المفاجأة (الغدر):\n**{weak}**")

    if b_rate > 50:
        st.error(f"🚨 تنبيه: اللعبة حالياً في نمط 'غدر'. احتمالية فوز السيارة المستبعدة ({weak}) عالية جداً!")

# --- التسجيل الآمن ---
with st.expander("📝 تسجيل الجولة (حفظ البيانات مؤمن)", expanded=True):
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.button("🚀 حفظ وتحديث النمط العكسي"):
        # كود الإرسال مع الحماية
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.1625798960": str(aw), "entry.1007263974": str(strong) # نسجل التوقع الأول لمراقبة الدقة
        }
        try:
            r = requests.post(FORM_URL, data=payload, timeout=15)
            if r.status_code == 200:
                st.balloons()
                st.cache_data.clear()
                st.rerun()
        except:
            st.error("فشل الإرسال، بياناتك ما زالت هنا. حاول مجدداً.")
