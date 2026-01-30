import streamlit as st
import pandas as pd
import requests

# إعدادات الروابط الخاصة بنموذجك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
# رابط القراءة من جدول جوجل (تأكد من تفعيل "Anyone with the link can view")
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1pVaMxKMDACIetLbLUkZzpOifSIQZCRVFwOzI8Wsj1eA/gviz/tq?tqx=out:csv"

st.set_page_config(page_title="Race Analysis Pro", page_icon="🏎️")

st.title("🏎️ محلل الأنماط الذكي (L-C-R)")

# دالة لجلب البيانات التاريخية من الجدول لغرض التوقع
def fetch_data():
    try:
        # نقرأ البيانات من الجدول مباشرة
        return pd.read_csv(SHEET_READ_URL)
    except:
        return pd.DataFrame()

df = fetch_data()

# --- 1. قسم التوقع الاستباقي ---
with st.container(border=True):
    st.subheader("🔮 التوقع قبل السباق")
    col_v = st.columns(3)
    c1 = col_v[0].selectbox("السيارة 1", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="p1")
    c2 = col_v[1].selectbox("السيارة 2", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="p2")
    c3 = col_v[2].selectbox("السيارة 3", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="p3")
    
    known_road = st.selectbox("الطريق الظاهر الآن", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"])
    
    if st.button("🚀 تحليل الاحتمالات التاريخية", use_container_width=True):
        if not df.empty and 'Winner' in df.columns:
            # نبحث عن الحالات التي ظهر فيها نفس الطريق وكان الفائز أحد هؤلاء الثلاثة
            similar_cases = df[df['Winner'].isin([c1, c2, c3])]
            if not similar_cases.empty:
                best_car = similar_cases['Winner'].value_counts().idxmax()
                st.success(f"بناءً على {len(similar_cases)} جولة سابقة، السيارة الأكثر فوزاً هي: {best_car}")
            else:
                st.info("لا توجد سجلات سابقة لهذه المجموعة، اعتمد على قوة السيارات العامة.")
        else:
            st.warning("قاعدة البيانات فارغة حالياً. ابدأ بتسجيل الجولات.")

# --- 2. قسم تسجيل البيانات (يرسل للنموذج تلقائياً) ---
with st.expander("💾 تسجيل جولة منتهية (تغذية الذكاء)"):
    st.write("أدخل تفاصيل الجولة التي انتهت لفك شفرة اللعبة:")
    
    c_r = st.columns(3)
    rl = c_r[0].selectbox("شمال (L)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rl")
    rc = c_r[1].selectbox("وسط (C)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rc")
    rr = c_r[2].selectbox("يمين (R)", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="rr")
    
    lp = st.radio("أين كان الطريق الأطول؟", ["L", "C", "R"], horizontal=True)
    win = st.selectbox("من الفائز الفعلي؟", [c1, c2, c3], key="actual_win")

    if st.button("✅ حفظ البيانات للأبد", use_container_width=True):
        # تم ربط الخانات بأسئلة النموذج الخاص بك
        payload = {
            "entry.1983088927": c1,   # Car1
            "entry.1592350812": c2,   # Car2
            "entry.303964593": c3,    # Car3
            "entry.2062602710": rl,   # Road_L
            "entry.1481269550": rc,   # Road_C
            "entry.1691459582": rr,   # Road_R
            "entry.614686419": lp,    # Long_Pos
            "entry.1697207604": win   # Winner
        }
        
        try:
            # إرسال البيانات بطريقة مخفية لنموذج جوجل
            response = requests.post(FORM_URL, data=payload)
            if response.status_code == 200:
                st.success("تم الحفظ وتحديث الذاكرة بنجاح!")
                st.balloons()
            else:
                st.error("حدث خطأ أثناء الاتصال بالنموذج.")
        except:
            st.error("خطأ في الشبكة، تأكد من اتصالك.")
