import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V62.5 - Instant Predict", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=1) # تحديث فوري جداً
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_data()

# 1. العداد العلوي (ثابت وواضح)
if not df.empty:
    st.markdown(f"""<div style='text-align: center; background-color: #0E1117; padding: 10px; border-radius: 10px; border: 1px solid #00FFCC;'>
    <h2 style='margin:0; color: #00FFCC;'>📊 جولات السيرفر: {len(df)}</h2></div>""", unsafe_allow_html=True)

# --- منطقة التوقع اللحظي (خارج أي فورم لتعمل فوراً) ---
st.subheader("🏁 مدخلات النمط (التوقع يظهر هنا فوراً)")
c1, c2, c3 = st.columns(3)
v1 = c1.selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=0)
v2 = c2.selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1)
v3 = c3.selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2)

ci = st.columns([1, 2])
vp = ci[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True)
vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

# حساب التوقعات الثلاثة لحظياً
pos_map = {"L": 4, "C": 5, "R": 6}
matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]

if not matches.empty:
    counts = matches.iloc[:, 8].value_counts()
    p1 = counts.index[0] if len(counts) > 0 else v1
    p2 = counts.index[1] if len(counts) > 1 else v2
    p3 = counts.index[2] if len(counts) > 2 else v3
    
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin: 15px 0; background-color: #1a1c24; padding: 15px; border-radius: 15px;">
        <div style="flex:1; text-align:center; border:2px solid #00FFCC; border-radius:10px; padding:10px;"><h4 style="margin:0;">🥇 الأول</h4><h2 style="margin:0; color:#00FFCC;">{p1}</h2></div>
        <div style="flex:1; text-align:center; border:2px solid #FFCC00; border-radius:10px; padding:10px;"><h4 style="margin:0;">🥈 الثاني</h4><h2 style="margin:0; color:#FFCC00;">{p2}</h2></div>
        <div style="flex:1; text-align:center; border:2px solid #FF4B4B; border-radius:10px; padding:10px;"><h4 style="margin:0;">🥉 الثالث</h4><h2 style="margin:0; color:#FF4B4B;">{p3}</h2></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ نمط جديد لم يسجل من قبل.")

st.divider()

# --- منطقة الترحيل (في أسفل الصفحة لعدم التشتيت) ---
with st.form("save_result"):
    st.subheader("📥 حفظ نتيجة الجولة بعد الانتهاء")
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_cols = st.columns(2)
    h1 = h_cols[0].selectbox(f"طريق {others[0]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    h2 = h_cols[1].selectbox(f"طريق {others[1]} (مخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    f_cols = st.columns(2)
    lp = f_cols[0].radio("الأطول LP", ["L", "C", "R"], horizontal=True)
    aw = f_cols[1].selectbox("الفائز الفعلي", [v1, v2, v3])
    
    if st.form_submit_button("🚀 ترحيل البيانات وحفظ الجولة", use_container_width=True):
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1 if not matches.empty else v1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الحفظ! جاري تحديث العداد...")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
