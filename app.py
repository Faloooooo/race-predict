import streamlit as st
import pandas as pd
import requests

# الإعدادات المحدثة لروابطك الفعلية
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
# رابط القراءة من جدولك الجديد
# الرابط المحدث للقراءة العامه
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv&gid=0"

st.set_page_config(page_title="Race Intelligence Pro", page_icon="🏎️", layout="wide")

# دالة جلب البيانات وتحديثها
def fetch_data():
    try:
        # قراءة البيانات مع إلغاء التخزين المؤقت لضمان التحديث اللحظي
        df_data = pd.read_csv(SHEET_READ_URL)
        return df_data.dropna(subset=['Winner']) # تجاهل الأسطر الفارغة
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية ---
st.sidebar.title("🎮 التحكم")
# عرض عدد الجولات في القائمة الجانبية بشكل دائم
total_races = len(df)
st.sidebar.metric("🔢 إجمالي الجولات المسجلة", total_races)

page = st.sidebar.radio("انتقل إلى:", ["🔮 التوقع والتسجيل", "📊 لوحة الإحصائيات"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع والتسجيل
# ---------------------------------------------------------
if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محلل الأنماط الذكي")
    
    # تنبيه في حال قلة البيانات
    if total_races < 30:
        st.info(f"💡 أنت حالياً في مرحلة التأسيس ({total_races}/30 جولة). استمر في التسجيل لزيادة دقة الذكاء الاصطناعي.")

    with st.container(border=True):
        st.subheader("🔮 التوقع الذكي")
        col_v = st.columns(3)
        c1 = col_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = col_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = col_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        current_road = st.selectbox("الطريق الظاهر الآن", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        road_pos = st.radio("موقع الطريق الظاهر", ["L", "C", "R"], horizontal=True)
        
        if st.button("🚀 تحليل الاحتمالات", use_container_width=True):
            if not df.empty:
                road_col = f"Road_{road_pos}"
                # فلترة بناءً على نوع الطريق والسيارات المختارة
                match = df[(df[road_col] == current_road) & (df['Winner'].isin([c1, c2, c3]))]
                if not match.empty:
                    best = match['Winner'].value_counts().idxmax()
                    st.success(f"الخيار الأفضل: {best}")
                else:
                    st.warning("لا توجد بيانات كافية لهذا الطريق بعد. التزم بالسيارة الأسرع عامة.")
            else:
                st.error("الجدول فارغ تماماً.")

    with st.expander("💾 تسجيل جولة جديدة"):
        c_r = st.columns(3)
        rl = c_r[0].selectbox("L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp = st.radio("الطريق الأطول", ["L", "C", "R"], horizontal=True, key="lp_act")
        win = st.selectbox("الفائز", [c1, c2, c3], key="win_act")

        if st.button("✅ حفظ في القاعدة", use_container_width=True):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp, "entry.77901429": win
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success("تم الحفظ وتحديث العداد!")
                st.rerun() # لإعادة تحميل الصفحة وتحديث العداد فوراً
            except:
                st.error("خطأ في الاتصال.")

# ---------------------------------------------------------
# الصفحة الثانية: الإحصائيات
# ---------------------------------------------------------
elif page == "📊 لوحة الإحصائيات":
    st.title("📊 الإحصائيات التحليلية")
    
    if not df.empty:
        st.write(f"### تم تحليل {total_races} جولة")
        
        # توزيع الانتصارات الكلي
        st.subheader("🏁 أداء السيارات")
        win_dist = df['Winner'].value_counts()
        st.bar_chart(win_dist)
        
        # تفصيل النسب المئوية
        cols = st.columns(3)
        for i, (car, count) in enumerate(win_dist.items()):
            percent = (count / total_races * 100).round(1)
            cols[i % 3].metric(car, f"{percent}%", f"{count} فوز")
            
        st.divider()
        st.subheader("📋 آخر البيانات المسجلة")
        st.dataframe(df.tail(10)) # عرض آخر 10 جولات
    else:
        st.info("سجل جولاتك الأولى لتظهر الرسوم البيانية هنا.")
