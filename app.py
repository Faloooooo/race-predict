import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V66.2 - Ultimate Stability", layout="wide")

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

# العدادات العلوية
if not df.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 سجل الجولات", len(df))
    c2.metric("🎯 الدقة", f"{(len(df[df.iloc[:, 8] == df.iloc[:, 9]])/len(df))*100:.1f}%")
    c3.info(f"آخر تحديث: {time.strftime('%H:%M:%S')}")

st.divider()

tab1, tab2 = st.tabs(["🚀 الرادار والترحيل", "🔬 مختبر البحث"])

with tab1:
    # --- الجزء الأول: إدخال المعطيات ---
    st.subheader("🏁 معطيات ما قبل السباق")
    cars = ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"]
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        v1 = col1.selectbox("السيارة L", cars, index=0, key="v1")
        v2 = col2.selectbox("السيارة C", cars, index=1, key="v2")
        v3 = col3.selectbox("السيارة R", cars, index=2, key="v3")
        
        col4, col5 = st.columns([1, 2])
        vp = col4.radio("الموقع الظاهر", ["L", "C", "R"], horizontal=True, key="vp")
        vt = col5.selectbox("طريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="vt")
        
        # كبسة القفل لمنع قفز الشاشة
        lock_btn = st.checkbox("🔓 قفل المعطيات وتحليل النمط", key="lock")

    if lock_btn:
        # --- الجزء الثاني: التوقعات (تظهر فقط بعد القفل) ---
        pos_map = {"L": 4, "C": 5, "R": 6}
        matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
        
        p1 = matches.iloc[:, 8].value_counts().index[0] if not matches.empty else v1
        p2 = matches.iloc[-1, 8] if not matches.empty else v2
        
        st.write("### 🎯 التوقعات الاستراتيجية")
        res1, res2 = st.columns(2)
        res1.info(f"🥇 أساسي: **{p1}**")
        res2.warning(f"🥈 ثانوي: **{p2}**")

        st.divider()

        # --- الجزء الثالث: الترحيل (داخل Form لثبات مطلق) ---
        with st.form("final_save_form"):
            st.subheader("📥 ترحيل الداتا بعد نهاية الجولة")
            others = [p for p in ["L", "C", "R"] if p != vp]
            h_col1, h_col2 = st.columns(2)
            h1 = h_col1.selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
            h2 = h_col2.selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
            
            f_col1, f_col2 = st.columns(2)
            lp = f_col1.radio("المسار الأطول LP", ["L", "C", "R"], horizontal=True)
            aw = f_col2.selectbox("الفائز الفعلي", [v1, v2, v3])
            
            submit = st.form_submit_button("🚀 ترحيل البيانات الآن", use_container_width=True)

        if submit:
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {
                "entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3,
                "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"],
                "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": p1
            }
            try:
                res = requests.post(FORM_URL, data=payload)
                if res.ok:
                    st.success(f"✅ تم التأكيد: تم ترحيل الجولة رقم {len(df)+1} بنجاح في تمام {time.strftime('%H:%M:%S')}")
                    st.balloons()
                    time.sleep(2)
                    st.cache_data.clear()
                    # لا نقوم بعمل rerun تلقائي للسماح للمستخدم برؤية الرسالة
                else:
                    st.error("❌ فشل الترحيل: خطأ في السيرفر")
            except:
                st.error("❌ فشل الترحيل: تأكد من الاتصال بالإنترنت")

with tab2:
    st.subheader("🔬 مختبر البحث التاريخي")
    # مدخلات بحث مستقلة
    sa, sb, sc = st.columns(3)
    search_df = df[(df.iloc[:, 1] == sa.selectbox("L", cars, key="s1")) & 
                   (df.iloc[:, 2] == sb.selectbox("C", cars, key="s2")) & 
                   (df.iloc[:, 3] == sc.selectbox("R", cars, key="s3"))]
    st.dataframe(search_df, use_container_width=True)
