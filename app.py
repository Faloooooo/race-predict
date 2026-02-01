import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V32.2 - Deep Power", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- المحرك الشامل الموحد (The Unified Engine) ---
def master_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1, v2, v3, 0
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    votes = {v: 0.0 for v in current_cars}

    # 1. تصويت الذاكرة التاريخية (وزن الطرق)
    for car in current_cars:
        match = data[(data.iloc[:, pos_map[v_pos]] == v_type) & (data.iloc[:, 8] == car)]
        votes[car] += len(match) * 3.0

    # 2. تصويت السلسلة (آخر 5 جولات)
    last_5 = data.tail(5).iloc[:, 8].tolist()
    for car in current_cars:
        votes[car] += last_5.count(car) * 12.0

    # 3. حساب معدل الغدر (آخر 20 جولة)
    last_20 = data.tail(20)
    # نحسب كم مرة فازت السيارة الأضعف (التي لم تتوقعها الخوارزمية)
    betrayal_count = len(last_20[last_20.iloc[:, 8] != last_20.iloc[:, 9]])
    betrayal_rate = (betrayal_count / 20) * 100

    sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    p1 = sorted_votes[0][0]
    p2 = sorted_votes[1][0]
    p_last = sorted_votes[2][0] # السيارة المستبعدة للتحذير
    
    return p1, p2, p_last, betrayal_rate

# --- الواجهة ---
st.title("🔥 المحرك الشامل V32.2")

if not df.empty:
    total = len(df)
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الجولات المجمعة", total)
    c2.metric("دقة التوقع التاريخية", f"{rate:.1f}%")
    c3.metric("مستوى الطاقة", "عميق 🔋")

st.divider()

# المدخلات الأساسية
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, p_warn, b_rate = master_logic(v1, v2, v3, vp, vt, df)
    
    st.write("---")
    res_cols = st.columns(2)
    res_cols[0].success(f"🥇 التوقع الأول:\n**{p1}**")
    res_cols[1].info(f"🥈 التوقع الثاني:\n**{p2}**")

    # نظام التحذير من الغدر
    if b_rate > 45:
        st.error(f"⚠️ **تحذير غدر مرتفع ({b_rate:.0f}%)**: هناك احتمال كبير لفوز السيارة المستبعدة [ **{p_warn}** ] لكسر النمط!")
    else:
        st.info(f"✅ نمط اللعبة مستقر حالياً (الغدر: {b_rate:.0f}%)")

# --- نموذج ما بعد السباق (كامل البيانات) ---
with st.expander("📥 سجل معلومات ما بعد السباق", expanded=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    st.write("أدخل الطرق المخفية لاستكمال التحليل العنقودي:")
    c_road = st.columns(2)
    h_road1 = c_road[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h_road2 = c_road[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    
    st.write("---")
    lp = st.radio("المسار الأطول (حسب النتيجة النهائية)", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("من فاز فعلياً؟", [v1, v2, v3], key="aw")
    
    if st.button("🚀 حفظ وتفجير طاقة البيانات", use_container_width=True):
        r_map = {vp: vt, others[0]: h_road1, others[1]: h_road2}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        try:
            if requests.post(FORM_URL, data=payload, timeout=15).ok:
                st.balloons()
                st.toast("تم الإرسال بنجاح!", icon='✅')
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
        except: st.error("فشل الإرسال. تأكد من الإنترنت والبيانات لا تزال محفوظة.")
