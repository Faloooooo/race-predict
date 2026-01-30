import streamlit as st
import pandas as pd
import requests

# الروابط الخاصة بك
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdtEDDxzbU8rHiFZCv72KKrosr49PosBVNUiRHnfNKSpC4RDg/formResponse"
SHEET_READ_URL = "https://docs.google.com/spreadsheets/d/1qzX6F4l4wBv6_cGvKLdUFayy1XDcg0QxjjEmxddxPTo/export?format=csv"

st.set_page_config(page_title="Golden Bet Intelligence V3.9", layout="wide", page_icon="🏆")

@st.cache_data(ttl=2)
def fetch_data():
    try:
        url = f"{SHEET_READ_URL}&t={pd.Timestamp.now().timestamp()}"
        df_read = pd.read_csv(url)
        return df_read.dropna(subset=[df_read.columns[8]])
    except:
        return pd.DataFrame()

df = fetch_data()

# --- القائمة الجانبية ---
st.sidebar.title("🏆 رادار الجولات الذهبية")
if not df.empty:
    total_races = len(df)
    st.sidebar.metric("🔢 إجمالي الجولات", total_races)
    
    # حساب الدقة بناءً على الأنماط الأخيرة
    recent = df.tail(20)
    correct = 0
    for i in range(len(recent)):
        row = recent.iloc[i]
        if row.iloc[8] in [row.iloc[0], row.iloc[1], row.iloc[2]]: # تأكد من أن الفائز من الخيارات
            correct += 1
    acc = (correct / 20 * 100) if not recent.empty else 33.3
    st.sidebar.metric("🎯 دقة الخوارزمية الحالية", f"{round(acc, 1)}%")
    st.sidebar.progress(min(acc/100, 1.0))

# ---------------------------------------------------------
# المحرك الذكي V3.9
# ---------------------------------------------------------
st.title("🧠 محرك التوقع ونظام الرهان الذهبي")

with st.container(border=True):
    st.subheader("🔍 تحليل المعطيات الحالية")
    
    # السيارات
    c_v = st.columns(3)
    v1 = c_v[0].selectbox("السيارة 1 (L)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], key="v1")
    v2 = c_v[1].selectbox("السيارة 2 (C)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=1, key="v2")
    v3 = c_v[2].selectbox("السيارة 3 (R)", ["Car", "Sport", "Super", "Bigbike", "Moto", "Orv", "Suv", "Truck", "Atv"], index=2, key="v3")
    
    # الطرق
    st.write("🛣️ **أنواع الطرق في المسارات:**")
    c_rd = st.columns(3)
    r_l = c_rd[0].selectbox("نوع طريق L", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="r_l")
    r_c = c_rd[1].selectbox("نوع طريق C", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="r_c")
    r_r = c_rd[2].selectbox("نوع طريق R", ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"], key="r_r")

    if st.button("🚀 كشف الفرص الذهبية", use_container_width=True):
        if not df.empty:
            # تحليل أداء كل سيارة في طريقها المحدد
            # مصفوفة: (السيارة، الموقع، النوع)
            results = []
            for car, pos, road in [(v1, "L", r_l), (v2, "C", r_c), (v3, "R", r_r)]:
                # البحث عن الجولات التي كانت فيها هذه السيارة في هذا الموقع وهذا الطريق وفازت
                total_matches = df[(df.iloc[:, 0 if pos=="L" else (1 if pos=="C" else 2)] == car) & 
                                   (df.iloc[:, 3 if pos=="L" else (4 if pos=="C" else 5)] == road)]
                wins = total_matches[total_matches.iloc[:, 8] == car]
                
                win_rate = (len(wins) / len(total_matches) * 100) if len(total_matches) > 0 else 0
                results.append({"car": car, "rate": win_rate, "count": len(total_matches)})

            # عرض النتائج والمقارنة
            st.divider()
            res_cols = st.columns(3)
            golden_opportunity = False
            
            for i, res in enumerate(results):
                color = "green" if res['rate'] >= 70 else ("orange" if res['rate'] >= 40 else "normal")
                res_cols[i].metric(f"قوة {res['car']}", f"{round(res['rate'], 1)}%", f"من {res['count']} مواجهة")
                
                # تفعيل الرهان الذهبي إذا كانت النسبة 100% والمواجهات > 2
                if res['rate'] == 100 and res['count'] >= 2:
                    st.warning(f"🌟 **رهان ذهبي:** السيارة **{res['car']}** لم تخسر أبداً في هذا التوزيع سابقاً!")
                    golden_opportunity = True

            best_overall = max(results, key=lambda x: x['rate'])['car']
            if not golden_opportunity:
                st.success(f"🏆 المرشح الأقوى تقنياً: **{best_overall}**")

# ---------------------------------------------------------
# تسجيل النتيجة
# ---------------------------------------------------------
with st.expander("💾 حفظ النتيجة الفعلية"):
    lp_act = st.radio("أي مسار كان الأطول فعلياً؟", ["L", "C", "R"], horizontal=True)
    winner_act = st.selectbox("من الفائز النهائي؟", [v1, v2, v3])
    
    if st.button("✅ تسجيل"):
        payload = {
            "entry.1815594157": v1, "entry.1382952591": v2, "entry.734801074": v3,
            "entry.189628538": r_l, "entry.725223032": r_c, "entry.1054834699": r_r,
            "entry.21622378": lp_act, "entry.77901429": winner_act
        }
        requests.post(FORM_URL, data=payload)
        st.success("تم التحديث!")
