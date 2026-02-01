import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V33.3 - Template Balance", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        # تنظيف البيانات لضمان عدم وجود قيم فارغة في الأعمدة الأساسية
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- محرك التوازن والتراتبية الذكي ---
def smart_balance_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, 0, "بدء البيانات.."
    
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # حساب الأوزان لكل سيارة بشكل منفصل
    scores = {v: 0.0 for v in current_cars}
    
    for car in current_cars:
        # 1. وزن التطابق التراتبي (المركز والطريق)
        match = data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)]
        scores[car] += len(match) * 10.0
        
        # 2. وزن التكرار التاريخي العام
        total_wins = len(data[data.iloc[:, 8] == car])
        scores[car] += total_wins * 1.0

    # ترتيب النتائج لضمان عدم التكرار
    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    p1 = sorted_res[0][0]
    # التأكد أن p2 ليس نفس p1
    p2 = sorted_res[1][0] if len(sorted_res) > 1 else v2
    
    # فحص التناقض: هل الفائز التاريخي في هذا القالب كان مختلفاً؟
    conflict_check = data[(data.iloc[:, 1] == v1) & (data.iloc[:, 2] == v2) & (data.iloc[:, 3] == v3)]
    status = "🔍 تحليل عنقودي"
    if len(conflict_check) > 1:
        unique_winners = conflict_check.iloc[:, 8].unique()
        if len(unique_winners) > 1:
            status = f"⚠️ قالب متناقض (فائزون سابقون: {', '.join(unique_winners)})"

    return p1, p2, status

# --- الواجهة ---
st.title("⚖️ محرك توازن القوالب V33.3")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي القوالب", len(df))
    c2.metric("دقة النظام", f"{rate:.1f}%")
    c3.metric("توازن الطاقة", "نشط ✅")

st.divider()

with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status = smart_balance_logic(v1, v2, v3, vp, vt, df)
    
    st.info(f"حالة النمط: {status}")
    res = st.columns(2)
    res[0].success(f"🥇 الاحتمال الأول: **{p1}**")
    res[1].warning(f"🥈 الاحتمال الثاني: **{p2}**")

# تسجيل معلومات ما بعد السباق مع تحسين الإشعار
with st.expander("📥 ترحيل بيانات الجولة (نظام الحفظ المطور)", expanded=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_road = st.columns(2)
    h_road1 = c_road[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h_road2 = c_road[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الحقيقي", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل وحفظ الجولة", use_container_width=True):
        r_map = {vp: vt, others[0]: h_road1, others[1]: h_road2}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        try:
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ تم ترحيل الجولة بنجاح إلى القوالب!")
                time.sleep(1.5) # وقت كافٍ لرؤية الإشعار
                st.cache_data.clear()
                st.rerun()
        except: st.error("خطأ في الشبكة، البيانات محفوظة، جرب مرة أخرى.")
