import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Race Intelligence Pro", layout="wide", page_icon="🏎️")

def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية ---
st.sidebar.title("🎮 التحكم والنظام")
if not df.empty:
    total_races = len(df)
    st.sidebar.success(f"✅ متصل: {total_races} جولة")
else:
    total_races = 0

page = st.sidebar.radio("انتقل إلى:", ["🔮 التوقع والتسجيل", "📊 لوحة الإحصائيات"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع والتسجيل (مع دمج الطريق)
# ---------------------------------------------------------
if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محرك التوقع الذكي (Advanced)")
    
    with st.container(border=True):
        st.subheader("🔍 إدخال بيانات السباق القادم")
        c_v = st.columns(3)
        c1 = c_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = c_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = c_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        st.divider()
        c_t = st.columns(2)
        current_road = c_t[0].selectbox("نوع الطريق الظاهر الآن", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        road_pos = c_t[1].radio("موقع هذا الطريق", ["L", "C", "R"], horizontal=True)
        
        if st.button("🚀 تحليل الاحتمالات المتقدمة", use_container_width=True):
            if not df.empty:
                # تحديد رقم العمود بناءً على الموقع (L=3, C=4, R=5 في ترتيب الإندكس)
                pos_map = {"L": 3, "C": 4, "R": 5}
                road_col_idx = pos_map[road_pos]
                
                # فلترة البيانات: الطريق يطابق + السيارات من ضمن المختارة
                match = df[(df.iloc[:, road_col_idx] == current_road) & (df.iloc[:, 8].isin([c1, c2, c3]))]
                
                if not match.empty:
                    best_car = match.iloc[:, 8].value_counts().idxmax()
                    wins_count = match.iloc[:, 8].value_counts().max()
                    st.success(f"المرشح الأقوى: **{best_car}** (فاز {wins_count} مرة في ظروف مشابهة)")
                else:
                    # فحص الأداء العام للسيارات إذا لم يوجد تطابق للطريق
                    general_wins = df[df.iloc[:, 8].isin([c1, c2, c3])].iloc[:, 8]
                    if not general_wins.empty:
                        best_gen = general_wins.value_counts().idxmax()
                        st.info(f"لا توجد بيانات لهذا الطريق، لكن تاريخياً الأفضل بين الثلاثة هو: **{best_gen}**")
                    else:
                        st.warning("لا توجد بيانات سابقة لهذه السيارات إطلاقاً.")
            else:
                st.error("قاعدة البيانات فارغة.")

    with st.expander("💾 تسجيل جولة منتهية"):
        c_r = st.columns(3)
        rl = c_r[0].selectbox("L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp = st.radio("الطريق الأطول", ["L", "C", "R"], horizontal=True, key="lp_reg")
        win = st.selectbox("الفائز الفعلي", [c1, c2, c3], key="win_reg")

        if st.button("✅ حفظ البيانات"):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp, "entry.77901429": win
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success("تم الحفظ وتحديث القاعدة!")
            except:
                st.error("خطأ في الاتصال.")

# ---------------------------------------------------------
# الصفحة الثانية: الإحصائيات
# ---------------------------------------------------------
elif page == "📊 لوحة الإحصائيات":
    st.title("📊 لوحة الإحصائيات")
    if not df.empty:
        win_col = df.iloc[:, 8]
        win_counts = win_col.value_counts()
        
        st.subheader("🏁 أداء السيارات الكلي")
        st.bar_chart(win_counts)
        
        st.divider()
        cols = st.columns(3)
        for i, (car, count) in enumerate(win_counts.items()):
            percent = (float(count) / len(df)) * 100
            with cols[i % 3]:
                st.metric(f"🚗 {car}", f"{round(percent, 1)}%", f"{count} فوز")
                
        st.divider()
        st.subheader("📋 مراجعة البيانات")
        st.dataframe(df.tail(10), use_container_width=True)
