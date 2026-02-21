import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Race Master V70.0 - Time Aware", layout="wide")

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTiFBlrWkSYGQmiNLaHT1ts4EpQoLaz6on_ovU1ngQROPmVA/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/18D0FRhBizVq_ipur_8fBSXjB2AAe49bZxKZ6-My4O9M/export?format=csv"

@st.cache_data(ttl=5)
def load_db():
    try:
        url = f"{SHEET_READ_URL}&cb={time.time()}"
        data = pd.read_csv(url, on_bad_lines='skip', engine='c')
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
        return data.dropna(subset=[data.columns[1]])
    except: return pd.DataFrame()

df = load_db()

# --- واجهة المستخدم ---
tab1, tab2 = st.tabs(["🚀 رادار الجلسة الحالية", "🔬 مختبر الأنماط الصلبة"])

with tab1:
    if not df.empty:
        # عرض الوقت الحالي لمقارنته بأخر جولة
        last_entry_time = df.iloc[-1]['Timestamp']
        time_diff = datetime.now() - last_entry_time
        
        st.markdown(f"### ⏱️ آخر تحديث للشيت منذ: `{time_diff.seconds // 60}` دقيقة")
        
        with st.container(border=True):
            c_cols = st.columns(3)
            v1 = c_cols[0].selectbox("L", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key='v1')
            v2 = c_cols[1].selectbox("C", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key='v2')
            v3 = c_cols[2].selectbox("R", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key='v3')
            
            ir_cols = st.columns([1, 2])
            vp = ir_cols[0].radio("موقع الظاهر", ["L", "C", "R"], horizontal=True, key='vp')
            vt = ir_cols[1].selectbox("نوع الطريق الظاهر", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key='vt')

        # --- منطق التنبؤ الذكي مع مراعاة الغياب ---
        pos_map = {"L": 4, "C": 5, "R": 6}
        matches = df[(df.iloc[:, 1] == v1) & (df.iloc[:, 2] == v2) & (df.iloc[:, 3] == v3) & (df.iloc[:, pos_map[vp]] == vt)]
        
        if not matches.empty:
            last_match = matches.iloc[-1]
            match_age = datetime.now() - last_match['Timestamp']
            
            # تحديد مدى الثقة
            confidence = "عالية 🟢" if match_age.total_seconds() < 3600 else "متوسطة 🟡 (بيانات قديمة)"
            
            st.markdown(f"""
            <div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border-left: 10px solid #00FFCC;">
                <h3 style="margin:0; color:#00FFCC;">🎯 التوقع الأساسي: {last_match['Actual Winner ']}</h3>
                <p style="margin:5px 0;">ثقة التوقع: <b>{confidence}</b></p>
                <small>آخر ظهور لهذا النمط كان منذ: {match_age.days} يوم و {match_age.seconds // 3600} ساعة</small>
            </div>
            """, unsafe_allow_html=True)
            
            # كاشف التناقض التاريخي
            winners = matches['Actual Winner '].unique()
            if len(winners) > 1:
                st.error(f"⚠️ انتبه: هذا النمط متناقض تاريخياً (فاز فيه: {', '.join(winners)})")
        else:
            st.info("🆕 نمط جديد كلياً على سجلاتك.")

        # ترحيل البيانات (Form)
        with st.form("entry_v70"):
            st.subheader("📥 ترحيل جولة جديدة")
            others = [p for p in ["L", "C", "R"] if p != vp]
            h_cols = st.columns(2)
            h1 = h_cols[0].selectbox(f"طريق {others[0]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
            h2 = h_cols[1].selectbox(f"طريق {others[1]}", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
            lp = st.radio("المسار الأطول", ["L", "C", "R"], horizontal=True)
            aw = st.selectbox("الفائز الفعلي", [v1, v2, v3])
            
            if st.form_submit_button("🚀 حفظ وتحديث", use_container_width=True):
                # (كود الترحيل لغوغل شيت)
                pass
