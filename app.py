import streamlit as st
import random

# السرعات الأصلية
data = {
    "Car": {"desert": 132, "highway": 290.4, "bumpy": 98.4, "expressway": 264, "dirt": 153.6, "potholes": 67.2},
    "Sport": {"desert": 96, "highway": 480, "bumpy": 168, "expressway": 432, "dirt": 360, "potholes": 57.6},
    "Super": {"desert": 62.4, "highway": 528, "bumpy": 151.2, "expressway": 480, "dirt": 264, "potholes": 52.8},
    "Bigbike": {"desert": 132, "highway": 230.4, "bumpy": 259.2, "expressway": 264, "dirt": 165.6, "potholes": 187.2},
    "Moto": {"desert": 72, "highway": 225.6, "bumpy": 108, "expressway": 220.8, "dirt": 144, "potholes": 96},
    "Orv": {"desert": 58.08, "highway": 240, "bumpy": 218.4, "expressway": 286, "dirt": 220.8, "potholes": 134.4},
    "Suv": {"desert": 139.2, "highway": 360, "bumpy": 213.6, "expressway": 348, "dirt": 336, "potholes": 110.4},
    "Truck": {"desert": 98.28, "highway": 276, "bumpy": 216, "expressway": 240, "dirt": 87.6, "potholes": 108},
    "Atv": {"desert": 168, "highway": 115.2, "bumpy": 187.2, "expressway": 115.2, "dirt": 187.2, "potholes": 144}
}

road_types = ["desert", "highway", "bumpy", "expressway", "dirt", "potholes"]

st.title("🏎️ المحلل الذكي: التوقع الاستباقي")

# إدخال المعطيات المتوفرة فقط
st.subheader("📝 المعطيات المتاحة قبل السباق")
col1, col2, col3 = st.columns(3)
with col1: v1 = st.selectbox("السيارة 1", list(data.keys()), index=0)
with col2: v2 = st.selectbox("السيارة 2", list(data.keys()), index=1)
with col3: v3 = st.selectbox("السيارة 3", list(data.keys()), index=2)

known_road = st.selectbox("ما هو الطريق الظاهر أمامك؟", road_types)

if st.button("🔮 تحليل احتمالات الفوز"):
    participants = [v1, v2, v3]
    scores = {v1: 0, v2: 0, v3: 0}
    
    # محاكاة لـ 500 سيناريو مختلف للطرق المخفية
    for _ in range(500):
        r2 = random.choice(road_types)
        r3 = random.choice(road_types)
        roads = [known_road, r2, r3]
        long_idx = random.randint(0, 2) # احتمال عشوائي لمكان الطريق الطويل
        
        dists = [100, 100, 100]
        dists[long_idx] = 200
        
        temp_results = []
        for p in participants:
            time = sum(dists[i] / data[p][roads[i]] for i in range(3))
            temp_results.append((p, time))
        
        temp_results.sort(key=lambda x: x[1])
        winner = temp_results[0][0]
        scores[winner] += 1
    
    st.write("### 📊 نسبة احتمال فوز كل سيارة:")
    for p in participants:
        prob = (scores[p] / 500) * 100
        st.write(f"**{p}**: {prob:.1f}%")
        st.progress(prob / 100)
