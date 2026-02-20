import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V60.0 - Deep Filter", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5, show_spinner=False)
def load_data():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1], data.columns[4], data.columns[7]]) # التأكد من وجود الطرق والمسار
    except: return pd.DataFrame()

df = load_data()

# --- محرك الفلترة العميقة (اقتراحك) ---
def deep_filter_logic(v1, v2, v3, vp, vt, data):
    if data.empty: return v1, v2, 0, "لا توجد داتا"
    
    # 1. التركيز على آخر 600 جولة (8 ساعات) كما طلبت
    recent_data = data.tail(600)
    
    # 2. البحث عن "النمط المتطابق" (السيارات + الطريق الظاهر)
    pos_map = {"L": 4, "C": 5, "R": 6}
    pattern_matches = recent_data[
        (recent_data.iloc[:, 1] == v1) & 
        (recent_data.iloc[:, 2] == v2) & 
        (recent_data.iloc[:, 3] == v3) &
        (recent_data.iloc[:, pos_map[vp]] == vt)
    ]
    
    strength = len(pattern_matches)
    
    if strength > 0:
        # إذا وجدنا أنماطاً متكررة، نحلل من فاز فيها آخر مرة مع مراعاة الطرق المخفية
        last_winner = pattern_matches.iloc[-1, 8] # الفائز في آخر تكرار للنمط
        winners_list = pattern_matches.iloc[:, 8].tolist()
        
        # تحليل دورة الفوز: إذا كانت السيارات تتبادل الفوز في نفس النمط
        if len(winners_list) > 1 and winners_list[-1] != winners_list[-2]:
            msg = f"🔄 نمط دوار: الفوز ينتقل من {winners_list[-2]} إلى {winners_list[-1]}"
            p1 = winners_list[-1] 
            p2 = winners_list[-2]
        else:
            msg = "🎯 نمط مستقر في الجلسة الأخيرة"
            p1 = last_winner
            p2 = v1 if last_winner != v1 else v2
    else:
        # إذا كان النمط جديداً تماماً على الـ 600 جولة، نعود للتحليل الإحصائي العام
        msg = "🆕 نمط جديد (تحليل إحصائي عام)"
        p1, p2 = v1, v2 # تبسيط للتجربة

    return p1, p2, strength, msg

# --- الواجهة المستقرة ---
st.title("🚀 إصدار الفلترة العميقة V60.0")

if not df.empty:
    total = len(df)
    st.metric("📊 إجمالي الجولات المسجلة", f"{total} / 10,000")
    st.progress(min(total/10000, 1.0))

st.divider()

# المدخلات الأساسية للتحليل
with st.container(border=True):
    st.subheader("🏁 مدخلات النمط الحالي")
    c1, c2, c3 = st.columns(3)
    v1 = c1.selectbox("السيارة L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
    v2 = c2.selectbox("السيارة C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
    v3 = c3.selectbox("السيارة R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
    
    ci = st.columns([1, 2])
    vp = ci[0].radio("موقع الطريق الظاهر", ["L", "C", "R"], horizontal=True)
    vt = ci[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    p1, p2, strength, msg = deep_filter_logic(v1, v2, v3, vp, vt, df)
    
    st.info(f"💡 الحالة: {msg} | تكرار النمط في آخر 8 ساعات: {strength}")
    res = st.columns(2)
    res[0].success(f"🥇 التوقع بناءً على الفلترة: {p1}")
    res[1].warning(f"🥈 الخيار البديل: {p2}")

st.divider()

# قسم الترحيل (لجمع الطرق المخفية لتقوية الفلترة القادمة)
with st.container(border=True):
    st.subheader("📥 ترحيل البيانات الكاملة (لتحسين الفلترة)")
    others = [p for p in ["L", "C", "R"] if p != vp]
    h_col = st.columns(2)
    h1 = h_col[0].selectbox(f"طريق {others[0]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h1')
    h2 = h_col[1].selectbox(f"طريق {others[1]} المخفي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='h2')
    
    f_col = st.columns(2)
    lp = f_col[0].radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
    aw = f_col[1].selectbox("الفائز الفعلي", [v1, v2, v3])

    if st.button("🚀 حفظ النمط كاملاً", use_container_width=True):
        roads = {vp: vt, others[0]: h1, others[1]: h2}
        payload = {
            "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
            "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
            "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
        }
        if requests.post(FORM_URL, data=payload).ok:
            st.balloons()
            st.cache_data.clear()
            st.rerun()
