import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race Intelligence V28.1", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- خوارزمية البصمة المستقلة ---
def fingerprint_logic(v1, v2, v3, v_pos, v_type, data):
    if data.empty: return v1
    current_cars = {v1, v2, v3}
    pos_map = {"L": 4, "C": 5, "R": 6}
    car_at_pos = v1 if v_pos == "L" else v2 if v_pos == "C" else v3
    
    # فلترة المواجهات المتشابهة
    mask_same_cars = data.apply(lambda row: {row.iloc[1], row.iloc[2], row.iloc[3]} == current_cars, axis=1)
    mask_specific = (data.iloc[:, pos_map[v_pos]] == v_type) & \
                    (data.iloc[:, 1 if v_pos=="L" else 2 if v_pos=="C" else 3] == car_at_pos)
    
    scores = {v1: 0, v2: 0, v3: 0}
    for _, row in data[mask_same_cars].iterrows(): scores[row.iloc[8]] += 2
    for _, row in data[mask_specific].iterrows(): scores[row.iloc[8]] += 5
    
    prediction = max(scores, key=scores.get)
    return prediction if scores[prediction] > 0 else v1

# --- عرض الإحصائيات (نسبة الربح) ---
st.title("🎯 نظام البصمة المستقلة (V28.1)")

if not df.empty:
    total_rounds = len(df)
    # حساب عدد المرات التي تطابق فيها التوقع مع الفائز الفعلي
    # العمود 9 هو التوقع والعمود 8 هو الفائز الفعلي
    correct_hits = len(df[df.iloc[:, 8] == df.iloc[:, 9]])
    win_rate = (correct_hits / total_rounds) * 100 if total_rounds > 0 else 0

    col1, col2 = st.columns(2)
    col1.metric("إجمالي الجولات المسجلة", f"{total_rounds}")
    col2.metric("دقة توقع النظام (Win Rate)", f"{win_rate:.1f}%", delta=f"{correct_hits} إصابة")
else:
    st.info("بانتظار تسجيل الجولات لبدء حساب نسبة الربح.")

st.divider()

# --- المدخلات والتوقع ---
with st.container(border=True):
    c = st.columns(3)
    v1 = c[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    prediction = fingerprint_logic(v1, v2, v3, vp, vt, df)
    st.subheader(f"🔮 التوقع المقترح: :green[{prediction}]")

# --- التسجيل ---
with st.expander("📥 تسجيل الجولة الحالية"):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1_t = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2_t = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])

if st.button("🚀 حفظ وتحديث البصمة", use_container_width=True):
    r_map = {vp: vt, others[0]: h1_t, others[1]: h2_t}
    payload = {
        "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
        "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
        "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(prediction)
    }
    if requests.post(FORM_URL, data=payload).ok:
        st.success("تم التحديث!")
        st.cache_data.clear()
        st.rerun()
