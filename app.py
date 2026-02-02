import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية لبيانات الـ 728 جولة
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V33.4 - 700+ Data Power", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- محرك الحسم التراكمي (Cumulative Decision Engine) ---
def advanced_700_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "تحليل.."
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # 1. فحص التناقض التاريخي العميق
    exact_matches = data[(data.iloc[:, 1] == v1) & (data.iloc[:, 2] == v2) & (data.iloc[:, 3] == v3)]
    
    if not exact_matches.empty:
        # إذا وجدنا تناقضاً، نبحث عن السيارة التي فازت في "آخر" ظهور لهذا القالب
        # لأن اللعبة غالباً ما تكرر آخر نمط ناجح
        p1 = exact_matches.iloc[-1, 8]
        status = "💎 نمط مكرر (محسوم من الـ 700 جولة)"
    else:
        # 2. التحليل العنقودي بناءً على الطريق والتراتبية
        scores = {v: 0.0 for v in current_cars}
        for car in current_cars:
            road_wins = len(data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)])
            scores[car] += road_wins * 7.0 # وزن عالي للطريق المرئي
            
        sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        p1 = sorted_res[0][0]
        status = "🔍 استنتاج عنقودي مطور"

    p2 = [v for v in current_cars if v != p1][0]
    return p1, p2, status

# --- واجهة المفاعل ---
st.title("🔋 مفاعل البيانات العظمى V33.4")
st.write(f"المحرك يعمل الآن بكامل طاقة الـ **{len(df)}** جولة.")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي القوالب", len(df))
    c2.metric("دقة الحسم", f"{rate:.1f}%")
    c3.metric("استقرار النمط", "ممتاز ✨")

st.divider()

with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status = advanced_700_logic(v1, v2, v3, vp, vt, df)
    
    st.info(f"الحالة: {status}")
    res = st.columns(2)
    res[0].success(f"🥇 التوقع الأول (حسم):\n**{p1}**")
    res[1].warning(f"🥈 التوقع البديل:\n**{p2}**")

# نموذج الترحيل المطور
with st.expander("📥 ترحيل بيانات الجولة (نظام 700+)", expanded=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    st.write("أدخل تفاصيل ما بعد السباق:")
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل وحفظ بنظام الحسم", use_container_width=True):
        r_map = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.success("✅ تم الحفظ وتحديث المفاعل!")
            time.sleep(1.5)
            st.cache_data.clear()
            st.rerun()
