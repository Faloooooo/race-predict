import streamlit as st
import pandas as pd
import requests

# الإعدادات المحدثة بناءً على الرابط الذي أرسلته
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
# رابط القراءة من الجدول (CSV)
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1pVaMxKMDACIetLbLUkZzpOifSIQZCRVFwOzI8Wsj1eA/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Race Intelligence Pro", page_icon="🏎️")

st.title("🏎️ محلل الأنماط الذكي (L-C-R)")

# دالة لجلب البيانات التاريخية
def fetch_data():
    try:
        return pd.read_csv(SHEET_READ_URL)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- قسم التوقع ---
with st.container(border=True):
    st.subheader("🔮 التوقع قبل السباق")
    col_v = st.columns(3)
    c1 = col_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
    c2 = col_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
    c3 = col_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
    
    if st.button("🚀 تحليل الاحتمالات", use_container_width=True):
        if not df.empty and 'Winner' in df.columns:
            winners = df[df['Winner'].isin([c1, c2, c3])]['Winner'].value_counts()
            if not winners.empty:
                st.success(f"الأكثر فوزاً تاريخياً في هذه المواجهة: {winners.idxmax()}")
            else:
                st.info("لا توجد سجلات سابقة، اعتمد على الحساب الرياضي.")
        else:
            st.warning("ابدأ بتسجيل الجولات لبناء الذاكرة.")

# --- قسم تسجيل البيانات (المعاير يدوياً) ---
with st.expander("💾 تسجيل جولة منتهية"):
    c_r = st.columns(3)
    rl = c_r[0].selectbox("شمال (L)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
    rc = c_r[1].selectbox("وسط (C)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
    rr = c_r[2].selectbox("يمين (R)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
    
    lp = st.radio("أين كان الطريق الأطول؟", ["L", "C", "R"], horizontal=True)
    win = st.selectbox("من فاز فعلياً؟", [c1, c2, c3], key="actual_win")

    if st.button("✅ حفظ البيانات", use_container_width=True):
        # تم تحديث الأكواد بناءً على الرابط الذي أرسلته بدقة
        payload = {
            "entry.1815594157": c1,   # Car1
            "entry.1382952591": c2,   # Car2
            "entry.734801074": c3,    # Car3
            "entry.189628538": rl,    # Road_L
            "entry.725223032": rc,    # Road_C
            "entry.1054834699": rr,   # Road_R
            "entry.21622378": lp,     # Long_Pos
            "entry.77901429": win     # Winner
        }
        
        try:
            response = requests.post(FORM_URL, data=payload)
            if response.status_code == 200:
                st.success("تم الحفظ وتعبئة الأعمدة بنجاح!")
                st.balloons()
            else:
                st.error("فشل في إرسال البيانات للنموذج.")
        except:
            st.error("خطأ في الاتصال، تأكد من الإنترنت.")
