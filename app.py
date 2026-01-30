import streamlit as st
import pandas as pd
import requests

# الإعدادات
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1pVaMxKMDACIetLbLUkZzpOifSIQZCRVFwOzI8Wsj1eA/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Race Intelligence Pro", page_icon="🏎️", layout="wide")

# دالة جلب البيانات
def fetch_data():
    try:
        data = pd.read_csv(SHEET_READ_URL)
        # تنظيف البيانات من الأسطر الفارغة
        return data.dropna(subset=['Winner'])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("🎮 القائمة الرئيسية")
page = st.sidebar.radio("انتقل إلى:", ["🔮 التوقع والتسجيل", "📊 لوحة الإحصائيات"])

# ---------------------------------------------------------
# الصفحة الأولى: التوقع والتسجيل
# ---------------------------------------------------------
if page == "🔮 التوقع والتسجيل":
    st.title("🏎️ محلل الأنماط الذكي")
    
    with st.container(border=True):
        st.subheader("🔮 التوقع قبل السباق")
        col_v = st.columns(3)
        c1 = col_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
        c2 = col_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
        c3 = col_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
        
        current_road = st.selectbox("الطريق الظاهر الآن", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        road_pos = st.radio("موقع الطريق الظاهر", ["L", "C", "R"], horizontal=True)
        
        if st.button("🚀 تحليل الاحتمالات", use_container_width=True):
            if not df.empty:
                road_col = f"Road_{road_pos}"
                filtered_df = df[(df[road_col] == current_road) & (df['Winner'].isin([c1, c2, c3]))]
                
                if not filtered_df.empty:
                    best_car = filtered_df['Winner'].value_counts().idxmax()
                    st.success(f"السيارة المرشحة بناءً على حالات مشابهة: {best_car}")
                else:
                    st.info("لا توجد جولات مطابقة تماماً، سجل المزيد من البيانات.")
            else:
                st.warning("قاعدة البيانات فارغة.")

    with st.expander("💾 تسجيل جولة منتهية"):
        c_r = st.columns(3)
        rl = c_r[0].selectbox("شمال (L)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
        rc = c_r[1].selectbox("وسط (C)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
        rr = c_r[2].selectbox("يمين (R)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
        lp = st.radio("الطريق الأطول", ["L", "C", "R"], horizontal=True)
        win = st.selectbox("الفائز الفعلي", [c1, c2, c3], key="actual_win")

        if st.button("✅ حفظ البيانات", use_container_width=True):
            payload = {
                "entry.1815594157": c1, "entry.1382952591": c2, "entry.734801074": c3,
                "entry.189628538": rl, "entry.725223032": rc, "entry.1054834699": rr,
                "entry.21622378": lp, "entry.77901429": win
            }
            try:
                requests.post(FORM_URL, data=payload)
                st.success("تم الحفظ!")
                st.balloons()
            except:
                st.error("خطأ في الاتصال.")

# ---------------------------------------------------------
# الصفحة الثانية: الإحصائيات (الصفحة المستقلة)
# ---------------------------------------------------------
elif page == "📊 لوحة الإحصائيات":
    st.title("📊 تحليل أداء الخوارزمية")
    
    if not df.empty:
        total_races = len(df)
        st.metric("إجمالي الجولات المسجلة", total_races)
        
        st.divider()
        
        # 1. نسبة فوز كل سيارة (بشكل عام)
        st.subheader("📈 نسبة فوز كل سيارة")
        win_counts = df['Winner'].value_counts()
        win_percentages = (win_counts / total_races * 100).round(1)
        
        cols = st.columns(len(win_percentages))
        for i, (car, percent) in enumerate(win_percentages.items()):
            cols[i%3].metric(car, f"{percent}%", f"{int(win_counts[car])} فوز")

        st.divider()

        # 2. تحليل الطرق (أي طريق يربح فيه من؟)
        st.subheader("🛣️ تحليل أداء السيارات حسب نوع الطريق")
        selected_road = st.selectbox("اختر نوع الطريق للتحليل:", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
        
        # البحث في كل المسارات (L, C, R) عن هذا الطريق
        road_analysis = df[(df['Road_L'] == selected_road) | (df['Road_C'] == selected_road) | (df['Road_R'] == selected_road)]
        
        if not road_analysis.empty:
            road_wins = road_analysis['Winner'].value_counts()
            st.bar_chart(road_wins)
            st.write(f"في طريق الـ **{selected_road}**، أكثر السيارات فوزاً هي **{road_wins.idxmax()}**.")
        else:
            st.info("لا توجد بيانات كافية لهذا النوع من الطرق بعد.")
            
    else:
        st.info("لا توجد بيانات كافية لعرض الإحصائيات. قم بتسجيل بعض الجولات أولاً.")
