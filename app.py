import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V33.6 - Full Console", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- محرك الحسم المتطور ---
def logic_v33_6(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, "تحليل.."
    current_cars = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    recent_data = data.tail(100)
    
    scores = {v: 0.0 for v in current_cars}
    for car in current_cars:
        r_match = recent_data[(recent_data.iloc[:, pos_map[vp]] == vt) & (recent_data.iloc[:, 8] == car)]
        scores[car] += len(r_match) * 15.0
        o_match = data[(data.iloc[:, pos_map[vp]] == vt) & (data.iloc[:, 8] == car)]
        scores[car] += len(o_match) * 2.0

    last_3 = data.tail(3).iloc[:, 8].tolist()
    sorted_res = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    p1, p2 = sorted_res[0][0], sorted_res[1][0]

    status = "⚡ نمط هجومي"
    if last_3.count(p1) >= 2:
        p1, p2 = p2, p1
        status = "🛡️ وضع الحماية (تبديل ذكي)"
    
    return p1, p2, status

# --- واجهة المستخدم الرئيسية ---
st.title("🚀 كونسول السباق المتكامل V33.6")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    c1, c2 = st.columns(2)
    c1.metric("الجولات في المفاعل", len(df))
    c2.metric("دقة النظام الحالية", f"{rate:.1f}%")

st.divider()

# القسم الأول: مدخلات ما قبل السباق والتوقع
st.subheader("🏁 1. بيانات ما قبل السباق")
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    c_p = st.columns([1, 2])
    vp = c_p[0].radio("الموقع المرئي", ["L", "C", "R"], horizontal=True)
    vt = c_p[1].selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, status = logic_v33_6(v1, v2, v3, vp, vt, df)
    
    st.markdown(f"**الحالة:** `{status}`")
    res_col = st.columns(2)
    res_col[0].success(f"🥇 الخيار الأول: **{p1}**")
    res_col[1].warning(f"🥈 الخيار الثاني: **{p2}**")

# القسم الثاني: بيانات ما بعد السباق (ظاهرة دائماً)
st.subheader("📊 2. نتائج ما بعد السباق (تغذية الداتا)")
with st.container(border=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_h = st.columns(2)
    h1 = c_h[0].selectbox(f"طريق {others[0]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h2 = c_h[1].selectbox(f"طريق {others[1]} (المخفي)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    
    c_f = st.columns(2)
    lp = c_f[0].radio("المسار الأطول الفعلي", ["L", "C", "R"], horizontal=True, key="lp")
    aw = c_f[1].selectbox("الفائز الفعلي في الجولة", [v1, v2, v3], key="aw")
    
    if st.button("🚀 ترحيل وحفظ البيانات الآن", use_container_width=True):
        r_map = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        try:
            r = requests.post(FORM_URL, data=payload, timeout=10)
            if r.ok:
                st.balloons()
                st.success("✅ تم ترحيل البيانات بنجاح! سيتم تحديث الصفحة...")
                time.sleep(2)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("فشل في الترحيل، جرب مرة أخرى.")
        except:
            st.error("حدث خطأ في الاتصال.")
