import streamlit as st
import pandas as pd
import requests

# الرابط المحدث - تأكد من النشر على الويب كـ CSV
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv&gid=0"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"

st.set_page_config(page_title="Race Intelligence Pro", layout="wide")

def fetch_data():
    try:
        # إضافة parameter عشوائي لمنع جوجل من إعطائنا نسخة قديمة (Cache)
        url = f"{SHEET_READ_URL}&cache={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        # إزالة الأسطر التي ليس بها فائز
        return df_read.dropna(subset=[df_read.columns[8]]) if len(df_read.columns) > 8 else df_read
    except Exception as e:
        st.sidebar.error(f"فشل الاتصال: {e}")
        return pd.DataFrame()

df = fetch_data()

# --- واجهة التطبيق ---
st.sidebar.title("📊 حالة النظام")
if not df.empty:
    st.sidebar.success(f"✅ متصل بالبيانات: {len(df)} جولة")
else:
    st.sidebar.warning("⚠️ غير متصل بالبيانات - تأكد من 'النشر على الويب'")

page = st.sidebar.radio("التنقل:", ["🔮 التوقع والتسجيل", "📊 الإحصائيات"])

if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محرك التنبؤ")
    # (بقية كود التوقع والتسجيل الذي أرسلته سابقاً...)
    # ملاحظة: سيعمل التوقع فور ظهور عدد الجولات في القائمة الجانبية

elif page == "📊 الإحصائيات":
    st.title("📊 تحليل البيانات")
    if not df.empty:
        # استخدام رقم العمود بدلاً من الاسم لتفادي مشاكل اللغة
        winner_col = df.columns[8] # عمود Winner هو التاسع عادة
        win_counts = df[winner_col].value_counts()
        st.bar_chart(win_counts)
        
        # عرض البيانات للتأكد
        st.subheader("آخر البيانات التي قرأها النظام:")
        st.dataframe(df.tail(5))
    else:
        st.error("لا توجد بيانات لعرضها. تأكد أن الجدول يحتوي على بيانات وأنك قمت بعمل 'Publish to web'.")
