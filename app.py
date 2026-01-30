import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro", layout="wide", page_icon="🏎️")

# دالة جلب البيانات مع تنظيفها
def fetch_data():
    try:
        # إضافة طابع زمني لمنع التخزين المؤقت القديم
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        # إزالة الأسطر التي لا تحتوي على سيارة فائزة (العمود التاسع)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية ---
st.sidebar.title("🎮 لوحة التحكم")
if not df.empty:
    total_races = len(df)
    st.sidebar.success(f"✅ متصل: {total_races} جولة")
    # شريط تقدم للوصول إلى 100 جولة (مرحلة الإتقان)
    progress = min(total_races / 100, 1.0)
    st.sidebar.write(f"مستوى دقة الذكاء: {int(progress*100)}%")
    st.sidebar.progress(progress)
else:
    st.sidebar.warning("⚠️ جاري تحديث البيانات...")
    total_races = 0

page = st.sidebar.radio("انتقل إلى:", ["🔮 التوقع والتسجيل", "📊 لوحة الإحصائيات"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع والتسجيل
# ---------------------------------------------------------
if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محرك التوقع الذكي")
    
    with st.container(border=True):
        st.subheader("🔮 التوقع المعتمد على التاريخ")
        col_v = st.columns(3)
        c1 = col_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = col_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = col_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        if st.button("🚀 تحليل الاحتمالات", use_container_width=True):
            if not df.empty:
                # فلترة السيارات المتنافسة من عمود الفائز (Index 8)
                winners = df[df.iloc[:, 8].isin([c1, c2, c3])].iloc[:, 8]
                if not winners.empty:
                    top_car = winners.value_counts().idxmax()
                    st.success(f"بناءً على {len(winners)} مواجهة سابقة: السيارة الأكثر حظاً هي **{top_car}**")
                else:
                    st.info("هذه المجموعة من السيارات لم تتواجه مسبقاً في سجلاتنا.")
            else:
                st.error("قاعدة البيانات لا تزال فارغة.")

    with st.expander("💾 تسجيل جولة منتهية"):
        st.write("سجل البيانات لزيادة دقة النظام:")
        c_r = st.columns(3)
        rl = c_r[0].selectbox("L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp = st.radio("الطريق الأطول", ["L", "C", "R"], horizontal=True)
        win = st.selectbox("الفائز الفعلي", [c1, c2, c3])

        if st.button("✅ حفظ في السجل", use_container_width=True):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp, "entry.77901429": win
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success("تم الحفظ بنجاح!")
                st.balloons()
            except:
                st.error("فشل الاتصال بالخادم.")

# ---------------------------------------------------------
# الصفحة الثانية: الإحصائيات (النسخة المصححة)
# ---------------------------------------------------------
elif page == "📊 لوحة الإحصائيات":
    st.title("📊 لوحة الأداء والنسب المئوية")
    
    if not df.empty:
        # استهداف العمود التاسع (الفائز)
        win_col_data = df.iloc[:, 8]
        win_counts = win_col_data.value_counts()
        
        st.subheader("🏁 ترتيب السيارات حسب عدد مرات الفوز")
        st.bar_chart(win_counts)
        
        st.divider()
        st.subheader("📈 نسبة الربح الكلية (Profit Probability)")
        
        # عرض النسب المئوية في مربعات (Metrics)
        cols = st.columns(3)
        for i, (car, count) in enumerate(win_counts.items()):
            # حساب النسبة المئوية بشكل آمن
            percentage = (float(count) / len(df)) * 100
            
            with cols[i % 3]:
                st.metric(
                    label=f"🚗 {car}", 
                    value=f"{round(percentage, 1)}%", 
                    delta=f"{count} انتصار"
                )
            
        st.divider()
        st.subheader("📋 مراجعة البيانات الخام")
        st.dataframe(df.tail(15), use_container_width=True)
    else:
        st.warning("لا توجد بيانات مسجلة لعرض الإحصائيات.")
