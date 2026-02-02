import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V34.2 - Stable Tone", layout="wide")

# دالة التنبيه الصوتي (نغمة هادئة وجميلة)
def play_soft_chime():
    components.html(
        """
        <audio autoplay>
          <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """,
        height=0,
    )

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- منطق محسّن لمنع الخطأ البرمجي ---
def logic_v34_2(v1, v2, v3, vp, vt, data):
    current_cars = [v1, v2, v3]
    if data.empty: return v1, v2, "بيانات أولية..", False
    
    pos_map = {"L": 4, "C": 5, "R": 6}
    recent_df = data.tail(150)
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        r_match = len(recent_df[(recent_df.iloc[:, pos_map[vp]] == vt) & (recent_df.iloc[:, 8] == car)])
        scores[car] += r_match * 45.0
        t_match = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)])
        scores[car] += t_match * 2.0

    # ترتيب النتائج مع ضمان عدم التكرار
    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1 = sorted_res[0][0]
    
    # ضمان أن p2 يختلف عن p1
    remaining_after_p1 = [v for v in current_cars if v != p1]
    # البحث عن الأفضل من المتبقيين
    p2_scores = {v: scores[v] for v in remaining_after_p1}
    p2 = max(p2_scores, key=p2_scores.get)
    
    # ضمان أن p3 يختلف عن p1 و p2 (لمنع خطأ الـ Index)
    p3 = [v for v in current_cars if v not in [p1, p2]][0]
    
    traitors = ["Atv", "Moto", "Car", "Orv"]
    is_bait = True if p3 in traitors and vt in ["potholes", "bumpy", "dirt"] else False
    
    status = "🚨 إنذار غدر!" if is_bait else "✅ نمط هادئ"
    return p1, p2, status, is_bait

# --- الواجهة ---
st.title("🛡️ مفاعل الاستقرار V34.2")

# إحصائيات عداد الجولات (عادت للظهور)
if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الجولات", len(df))
    c2.metric("الدقة الحالية", f"{rate:.1f}%")
    c3.metric("الحالة", "مستقر ✅")

st.divider()

with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    cp = st.columns([1, 2])
    vp = cp[0].radio("الموقع", ["L", "C", "R"], horizontal=True)
    vt = cp[1].selectbox("الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status, bait = logic_v34_2(v1, v2, v3, vp, vt, df)
    
    if bait:
        st.error(status)
        play_soft_chime() # نغمة هادئة وجميلة
    else:
        st.info(status)

    res = st.columns(2)
    res[0].success(f"🥇 التوقع الأول: **{p1}**")
    res[1].warning(f"🥈 التوقع الثاني: **{p2}**")

# قسم الترحيل مع الإشارة الخضراء
st.divider()
st.subheader("📥 ترحيل وحفظ البيانات")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل فوري (تحديث المفاعل)", use_container_width=True):
        payload = {"entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3, "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1}
        try:
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ رائع! تم ترحيل الجولة بنجاح.")
                time.sleep(2) # وقت لرؤية الإشارة الخضراء
                st.cache_data.clear()
                st.rerun()
        except: st.error("خطأ في الاتصال.")
