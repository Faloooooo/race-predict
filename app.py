import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك (تم التأكد منها)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
# الرابط المباشر لقراءة ملفك كـ CSV
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro", layout="wide", page_icon="🏎️")

# دالة جلب البيانات
@st.cache_data(ttl=10) # تحديث البيانات كل 10 ثوانٍ
def fetch_data():
    try:
        df_read = pd.read_csv(SHEET_READ_URL)
        return df_read
    except Exception as e:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية ---
st.sidebar.title("📊 حالة النظام")
if not df.empty:
    total_races = len(df)
    st.sidebar.success(f"✅ متصل: تم العثور على {total_races} جولة")
else:
    st.sidebar.warning("⚠️ جاري الاتصال بالبيانات...")
    total_races = 0

page = st.sidebar.radio("التنقل:", ["🔮 التوقع والتسجيل", "📊 لوحة الإحصائيات"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع والتسجيل
# ---------------------------------------------------------
if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محرك التوقع الذكي")
    
    with st.container(border=True):
        st.subheader("🔮 توقع الفائز")
        col_v = st.columns(3)
        c1 = col_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = col_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = col_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        if st.button("🚀 تحليل البيانات التاريخية", use_container_width=True):
            if not df.empty:
                # البحث في عمود الفائز (العمود التاسع)
                winners = df[df.iloc[:, 8].isin([c1, c2, c3])].iloc[:, 8]
                if not winners.empty:
                    top_car = winners.value_counts().idxmax()
                    st.success(f"الخيار الأرجح بناءً على السجلات: {top_car}")
                else:
                    st.info("لا توجد مواجهات سابقة لهذه السيارات في الذاكرة.")
            else:
                st.error("لا توجد بيانات متاحة حالياً.")

    with st.expander("💾 تسجيل جولة جديدة"):
        st.write("أدخل بيانات الجولة فور انتهائها:")
        c_r = st.columns(3)
        rl = c_r[0].selectbox("طريق L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("طريق C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("طريق R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp = st.radio("موقع الطريق الأطول", ["L", "C", "R"], horizontal=True)
        win = st.selectbox("السيارة الفائزة فعلياً", [c1, c2, c3])

        if st.button("✅ حفظ وإرسال", use_container_width=True):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp, "entry.77901429": win
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success("تم التحديث! سيظهر العداد الجديد خلال ثوانٍ.")
                st.balloons()
            except:
                st.error("حدث خطأ أثناء الإرسال.")

# ---------------------------------------------------------
# الصفحة الثانية: الإحصائيات
# ---------------------------------------------------------
elif page == "📊 لوحة الإحصائيات":
    st.title("📊 تحليل أداء السيارات")
    
    if not df.empty:
        # استهداف العمود التاسع (الفائز)
        win_col_data = df.iloc[:, 8]
        win_counts = win_col_data.value_counts()
        
        st.subheader("🏁 ترتيب السيارات الأكثر فوزاً")
        st.bar_chart(win_counts)
        
        st.divider()
        st.subheader("📈 نسب الربح لكل سيارة")
        cols = st.columns(3)
        for i, (car, count) in enumerate(win_counts.items()):
            percentage = (count / len(df) * 100).round(1)
            cols[i % 3].metric(car, f"{percentage}%", f"{count} فوز")
            
        st.divider()
        st.subheader("📝 مراجعة آخر الجولات")
        st.dataframe(df.tail(10))
    else:
        st.warning("البيانات قيد التحميل أو الجدول فارغ.")
