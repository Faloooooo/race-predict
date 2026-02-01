import streamlit as st
import pandas as pd
import requests
import time

# الروابط الرسمية لضمان استمرارية البيانات
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

st.set_page_config(page_title="Race AI V33.2 - Cluster Hierarchy", layout="wide")

@st.cache_data(ttl=1)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&cache_buster={time.time()}"
        df = pd.read_csv(url)
        return df.dropna(subset=[df.columns[1], df.columns[8]])
    except: return pd.DataFrame()

df = fetch_data()

# --- محرك التراتبية العنقودية (Hierarchical Cluster Engine) ---
def cluster_hierarchy_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, 0, "بدء التوليد.."
    
    # تعريف التراتبية الحالية
    current_order = [v1, v2, v3]
    pos_map = {"L": 4, "C": 5, "R": 6}
    
    # 1. البحث عن تطابق التراتبية (نفس الترتيب ونفس الطريق)
    hierarchy_match = data[
        (data.iloc[:, 1] == v1) & 
        (data.iloc[:, 2] == v2) & 
        (data.iloc[:, 3] == v3) & 
        (data.iloc[:, pos_map[vp]] == vt)
    ]
    
    if not hierarchy_match.empty:
        # إذا وجد تطابقاً كاملاً في التراتبية، يأخذ النتيجة فوراً
        p1 = hierarchy_match.iloc[-1, 8]
        p2 = hierarchy_match.iloc[-1, 9] # التوقع السابق كخيار ثانٍ
        return p1, p2, 95, "💎 قالب تطابق تراتبي كامل!"

    # 2. الانتقال للتطابق العنقودي (إذا لم يجد تطابقاً كاملاً)
    # يبحث عن جولات فيها 2 من 3 بنفس الترتيب
    cluster_match = data[
        ((data.iloc[:, 1] == v1) & (data.iloc[:, 2] == v2)) |
        ((data.iloc[:, 2] == v2) & (data.iloc[:, 3] == v3)) |
        ((data.iloc[:, 1] == v1) & (data.iloc[:, 3] == v3))
    ]
    
    if not cluster_match.empty:
        p1 = cluster_match.iloc[:, 8].mode()[0] # الأكثر تكراراً في هذا العنقود
        remaining = [v for v in current_order if v != p1]
        p2 = remaining[0] if remaining else v2
        return p1, p2, 70, "🔍 قالب عنقودي مرجح"

    # 3. تحليل الفئات العام (الخيار الأخير)
    return v1, v2, 40, "⚠️ تحليل فئة (بيانات جديدة)"

# --- واجهة المفاعل ---
st.title("🛡️ محرك التراتبية العنقودية V33.2")

if not df.empty:
    valid = df.dropna(subset=[df.columns[8], df.columns[9]])
    rate = (len(valid[valid.iloc[:, 8] == valid.iloc[:, 9]]) / len(valid) * 100) if len(valid) > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("الجولات في الشيت", len(df))
    c2.metric("دقة القوالب", f"{rate:.1f}%")
    c3.metric("توليد الطاقة", "عالي ⚡")

st.divider()

# المدخلات
with st.container(border=True):
    col = st.columns(3)
    v1 = col[0].selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = col[1].selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = col[2].selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    vp = st.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vt = st.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, conf, status = cluster_hierarchy_logic(v1, v2, v3, vp, vt, df)
    
    st.write(f"**الحالة:** {status}")
    st.progress(conf/100)
    
    res = st.columns(2)
    res[0].success(f"🥇 التوقع المعتمد:\n**{p1}**")
    res[1].info(f"🥈 التوقع المساند:\n**{p2}**")

# تسجيل معلومات ما بعد السباق
with st.expander("📥 سجل معلومات ما بعد السباق", expanded=True):
    others = [p for p in ["L", "C", "R"] if p != vp]
    c_road = st.columns(2)
    h_road1 = c_road[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h1")
    h_road2 = c_road[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="h2")
    lp = st.radio("المسار الأطول (يقيناً)", ["L", "C", "R"], horizontal=True, key="lp")
    aw = st.selectbox("الفائز الفعلي", [v1, v2, v3], key="aw")
    
    if st.button("🚀 تفجير البيانات والحفظ"):
        r_map = {vp: vt, others[0]: h_road1, others[1]: h_road2}
        payload = {
            "entry.159051415": str(v1), "entry.1682422047": str(v2), "entry.918899545": str(v3),
            "entry.401576858": str(r_map["L"]), "entry.658789827": str(r_map["C"]), "entry.1738752946": str(r_map["R"]),
            "entry.1719787271": str(lp), "entry.1625798960": str(aw), "entry.1007263974": str(p1)
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.cache_data.clear()
            st.rerun()
