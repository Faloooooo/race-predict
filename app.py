import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V62.7 - Data Recovery", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_data()

# العداد مع حساب الدقة اللحظية لآخر 50 جولة
if not df.empty:
    recent = df.tail(50)
    current_acc = (len(recent[recent.iloc[:, 8] == recent.iloc[:, 9]]) / 50) * 100
    st.markdown(f"""<div style='text-align: center; background-color: #0E1117; padding: 10px; border-radius: 10px; border: 1px solid #FF4B4B;'>
    <h2 style='margin:0; color: #00FFCC;'>📊 السجل: {len(df)} جولة | 📈 دقة الموجة الحالية: {current_acc:.1f}%</h2></div>""", unsafe_allow_html=True)

# مدخلات النمط - تصميم سريع
st.subheader("🏁 رادار النمط اللحظي")
c1, c2, c3 = st.columns(3)
v1 = c1.selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=0)
v2 = c2.selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1)
v3 = c3.selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2)

ci = st.columns([1, 2])
vp = ci[0].radio("الظاهر", ["L", "C", "R"], horizontal=True)
vt = ci[1].selectbox("طريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

# --- محرك التوقع V62.7 العكسي ---
pos_map = {"L": 4, "C": 5, "R": 6}
matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]

if not matches.empty:
    counts = matches.iloc[:, 8].value_counts()
    last_actual = matches.iloc[-1, 8]
    
    # 1. التوقع الذهبي (الأكثر تكراراً)
    p1 = counts.index[0]
    # 2. التوقع الفضي (السيارة التي لم تظهر مؤخراً - تعويض)
    p2_candidates = [v for v in [v1, v2, v3] if v != last_actual]
    p2 = p2_candidates[0] if p2_candidates else v2
    # 3. التوقع البرونزي (نادر - كاسر النمط)
    p3 = counts.index[-1] if len(counts) > 1 else v3

    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin: 15px 0;">
        <div style="flex:1; text-align:center; border:2px solid #00FFCC; border-radius:10px; padding:10px; background-color:#1a1c24;">
            <h4 style="margin:0; color:#AAA;">🥇 التاريخي</h4><h2 style="margin:0; color:#00FFCC;">{p1}</h2>
        </div>
        <div style="flex:1; text-align:center; border:2px solid #FFCC00; border-radius:10px; padding:10px; background-color:#1a1c24;">
            <h4 style="margin:0; color:#AAA;">🥈 العكسي (الدور)</h4><h2 style="margin:0; color:#FFCC00;">{p2}</h2>
        </div>
        <div style="flex:1; text-align:center; border:2px solid #FF4B4B; border-radius:10px; padding:10px; background-color:#1a1c24;">
            <h4 style="margin:0; color:#AAA;">🥉 الكاسر</h4><h2 style="margin:0; color:#FF4B4B;">{p3}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # تحذير الغدر بناءً على آخر 3 جولات لهذا النمط
    if len(matches) >= 2:
        last_lp_status = (matches.iloc[-1, 7] == matches.iloc[-1, 8])
        if not last_lp_status:
            st.error("⚠️ تحذير: هذا النمط كسر الـ LP في آخر جولة. السيرفر في وضع الغدر حالياً.")
else:
    st.info("🆕 نمط جديد")

st.divider()

# منطقة الترحيل (ثبات كامل)
with st.form("data_upload"):
    st.subheader("📥 تدوين وحفظ")
    others = [p for p in ["L", "C", "R"] if p != vp]
    h1 = st.selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    h2 = st.selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    lp_val = st.radio("LP", ["L", "C", "R"], horizontal=True)
    aw_val = st.selectbox("الفائز", [v1, v2, v3])
    
    if st.form_submit_button("🚀 ترحيل", use_container_width=True):
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp_val, "entry.1625798960": aw_val, "entry.1007263974": p1 if not matches.empty else v1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.cache_data.clear()
            st.rerun()
