import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Logic Master V4.2", layout="wide", page_icon="🧠")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        # إضافة طابع زمني للرابط لضمان جلب أحدث البيانات من جوجل شيت
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية (تحليل البيانات) ---
st.sidebar.title("🧠 مركز البيانات والنمو")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات المسجلة", total_races)
    
    # حساب نسبة النجاح (مقارنة الفوز بالتوقع في الجولات السابقة)
    # ملاحظة: ستبدأ الدقة بالظهور الفعلي بعد تسجيل جولات بالعمود الجديد
    st.sidebar.info("يتم الآن بناء قاعدة بيانات (التوقع vs الواقع) للوصول لنسبة 95%.")
    st.sidebar.progress(min(total_races/200, 1.0)) # مؤشر النضج نحو 200 جولة

# ---------------------------------------------------------
# مرحلة التنبؤ (قبل بداية السباق)
# ---------------------------------------------------------
st.title("🔮 التنبؤ الذكي ومحاكاة الخوارزمية")

with st.container(border=True):
    st.subheader("🏁 مدخلات ما قبل الانطلاق")
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("سيارة اليسار (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("سيارة الوسط (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("سيارة اليمين (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    st.divider()
    col_vis, col_type = st.columns(2)
    vis_pos = col_vis.radio("موقع الطريق المرئي", ["L", "C", "R"], horizontal=True)
    vis_type = col_type.selectbox("نوع الطريق المرئي", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])

    # خوارزمية التوقع الذكي
    predicted_winner = "N/A"
    if not df.empty:
        pos_map = {"L": 3, "C": 4, "R": 5}
        idx = pos_map[vis_pos]
        # البحث عن الحالات التي ظهر فيها هذا الطريق المرئي في هذا الموقع
        matches = df[df.iloc[:, idx] == vis_type]
        
        if not matches.empty:
            # من هذه الحالات، من فاز عندما كانت السيارات هي المختارة؟
            sub_match = matches[matches.iloc[:, 8].isin([v1, v2, v3])]
            if not sub_match.empty:
                predicted_winner = sub_match.iloc[:, 8].value_counts().idxmax()
            else:
                # إذا لم توجد مواجهة مباشرة، نأخذ السيارة الأقوى تاريخياً بين الثلاثة
                history_wins = df[df.iloc[:, 8].isin([v1, v2, v3])].iloc[:, 8]
                predicted_winner = history_wins.mode()[0] if not history_wins.empty else v1
        else:
            predicted_winner = v1 # خيار افتراضي لأول ظهور للطريق

    st.subheader(f"🏆 الفائز المتوقع: :green[{predicted_winner}]")

# ---------------------------------------------------------
# مرحلة التدوين (بعد انتهاء السباق)
# ---------------------------------------------------------
with st.expander("📝 تدوين النتائج (كشف الطرق المخفية)"):
    st.write("أدخل البيانات الفعلية بعد الجولة لتدريب الخوارزمية:")
    
    # تحديد الطرق المخفية
    others = [p for p in ["L", "C", "R"] if p != vis_pos]
    c_hid = st.columns(2)
    h1_type = c_hid
