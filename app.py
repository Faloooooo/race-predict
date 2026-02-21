import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Race Master V78.0 - Final Layout", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_db()

# --- العدادات الثابتة في القمة ---
if not df.empty:
    m1, m2 = st.columns(2)
    m1.metric("📊 سجل الجولات الكلي", len(df))
    recent_100 = df.tail(100)
    acc = (len(recent_100[recent_100.iloc[:, 8] == recent_100.iloc[:, 9]]) / len(recent_100)) * 100 if len(recent_100) > 0 else 0
    m2.metric("📈 نسبة الربح %", f"{acc:.1f}%")
st.divider()

tab1, tab2 = st.tabs(["🚀 غرفة التوقع والترحيل", "🔬 مختبر البحث الرئيسي"])

# --- التاب الأول: غرفة التوقع (كاملة المعلومات) ---
with tab1:
    with st.container(border=True):
        st.subheader("🏁 مدخلات النمط")
        c_cols = st.columns(3)
        v1 = c_cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
        v2 = c_cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
        v3 = c_cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
        ir = st.columns([1, 2])
        vp = ir[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
        vt = ir[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

    pos_map = {"L": 4, "C": 5, "R": 6}
    matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
    
    if not matches.empty:
        last_winner = matches.iloc[-1, 8]
        # المربع الكبير للتوقع
        st.markdown(f"""<div style="text-align: center; border: 2px solid #00FFCC; border-radius: 10px; padding: 15px; background-color: #0E1117; margin-bottom:10px;">
        <h3 style="margin:0;">🎯 أحدث جولة فازت بها:</h3><h1 style="color:#00FFCC; font-size:50px; margin:5px;">{last_winner}</h1></div>""", unsafe_allow_html=True)
        
        # معلومات التكرار التفصيلية التي طلبتها
        st.write("📊 **تحليل النمط (كم مرة فازت كل سيارة):**")
        counts = matches.iloc[:, 8].value_counts()
        c_stats = st.columns(len(counts))
        for i, (car, count) in enumerate(counts.items()):
            c_stats[i].warning(f"**{car}** ربحت: {count}")
    else:
        st.info("🆕 نمط جديد كلياً في قاعدة البيانات.")

    st.divider()
    # نموذج الترحيل الثابت مع البالونات
    with st.form("save_v78"):
        st.subheader("📥 ترحيل وحفظ")
        others = [p for p in ["L", "C", "R"] if p != vp]
        h_cols = st.columns(2)
        h1 = h_cols[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        h2 = h_cols[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        lp = st.radio("المسار الأطول (LP)", ["L", "C", "R"], horizontal=True)
        aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
        if st.form_submit_button("🚀 حفظ الجولة وتحديث البيانات", use_container_width=True):
            roads = {vp: vt, others[0]: h1, others[1]: h2}
            payload = {"entry.159051415": v1, "entry.1682422047": v2, "entry.918899545": v3, "entry.401576858": roads["L"], "entry.658789827": roads["C"], "entry.1738752946": roads["R"], "entry.1719787271": lp, "entry.1625798960": aw, "entry.1007263974": last_winner if not matches.empty else v1}
            if requests.post(FORM_URL, data=payload).ok:
                st.balloons()
                st.success("✅ تم الحفظ بنجاح!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()

# --- التاب الثاني: واجهة البحث (ترتيب الصورة المرفقة) ---
with tab2:
    st.header("🔬 مختبر البحث الرئيسي")
    if not df.empty:
        with st.container(border=True):
            st.write("🔎 اختيار التشكيلة للبحث:")
            sf = st.columns(3)
            sv1 = sf[0].selectbox("Car 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='sf1')
            sv2 = sf[1].selectbox("Car 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='sf2')
            sv3 = sf[2].selectbox("Car 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='sf3')
        
        # البحث والفلترة
        search_res = df[(df.iloc[:, 1] == sv1) & (df.iloc[:, 2] == sv2) & (df.iloc[:, 3] == sv3)].copy()
        
        if not search_res.empty:
            st.write(f"🔎 الجولات المطابقة: **{len(search_res)}**")
            
            # --- إعادة ترتيب الأعمدة حسب طلبك الصارم ---
            # الأعمدة الأصلية في الشيت: 0:Timestamp, 1:Car1, 2:Car2, 3:Car3, 4:RoadL, 5:RoadC, 6:RoadR, 7:LP, 8:Winner
            # سنقوم هنا بعرض نوع الطريق بناءً على أنه "الظاهر" في مكان ما
            
            final_display = search_res.iloc[:, [1, 2, 3, 4, 5, 6, 7, 8]].copy()
            final_display.columns = ['Car 1', 'Car 2', 'Car 3', 'Road L', 'Road C', 'Road R', 'LP الأطول', 'الفائز']
            
            st.dataframe(final_display, use_container_width=True)
            st.info("💡 ترتيب البحث: السيارات الثلاث أولاً، ثم تفاصيل الطرق الثلاث، ثم المسار الأطول والفائز.")
