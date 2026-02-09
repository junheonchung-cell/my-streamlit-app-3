# app.py
import streamlit as st
import requests
import random
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="AI 습관 트래커 (포켓몬)",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 AI 습관 트래커 (포켓몬 에디션)")
st.caption("🔓 API Key 없이 동작하는 무료 버전")

# ---------------------------
# PokeAPI 연동
# ---------------------------
def get_pokemon():
    """
    PokeAPI 사용
    https://pokeapi.co/api/v2/pokemon/{number}
    """
    try:
        number = random.randint(1, 151)
        url = f"https://pokeapi.co/api/v2/pokemon/{number}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        return {
            "id": data["id"],
            "name": data["name"].capitalize(),
            "types": [t["type"]["name"] for t in data["types"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            "image": data["sprites"]["other"]["official-artwork"]["front_default"]
        }
    except Exception:
        return None

# ---------------------------
# 데모용 날씨
# ---------------------------
def get_weather(city):
    weather_map = {
        "Seoul": "☀️ 맑음",
        "Busan": "🌊 바람 많은 날",
        "Incheon": "🌤️ 구름 조금",
        "Daegu": "🔥 더움",
        "Daejeon": "🌥️ 흐림",
        "Gwangju": "🌦️ 비",
        "Suwon": "❄️ 쌀쌀",
        "Ulsan": "💨 강풍",
        "Jeju": "🌴 휴양 날씨",
        "Sejong": "🌤️ 쾌청",
    }
    return weather_map.get(city, "🌍 평범한 날")

# ---------------------------
# 로컬 AI 코치 (규칙 기반)
# ---------------------------
def generate_local_report(habits, mood, weather, pokemon, style):
    completed = sum(habits.values())

    # 컨디션 등급
    if completed >= 5 and mood >= 8:
        grade = "S"
    elif completed >= 4:
        grade = "A"
    elif completed >= 3:
        grade = "B"
    elif completed >= 2:
        grade = "C"
    else:
        grade = "D"

    habit_list = ", ".join([k for k, v in habits.items() if v]) or "아직 없음"

    style_text = {
        "스파르타 코치": "🔥 변명은 없다. 결과가 전부다.",
        "따뜻한 멘토": "💖 오늘도 충분히 잘했어.",
        "게임 마스터": "🧙‍♂️ 새로운 퀘스트가 열렸다!"
    }

    return f"""
### 🏆 컨디션 등급: **{grade}**

**습관 분석**
- 오늘 달성한 습관: {habit_list}

**날씨 코멘트**
- 오늘 날씨는 {weather}. 컨디션 관리에 영향을 줬을 수 있어.

**내일 미션**
- 최소 **3개 이상의 습관**을 반드시 달성해보자!

**오늘의 파트너 포켓몬**
- **{pokemon['name']}** ({', '.join(pokemon['types'])})
- 스탯 중 가장 강한 능력치는 **{max(pokemon['stats'], key=pokemon['stats'].get)}**
- 이 포켓몬처럼 꾸준함이 핵심이다!

{style_text[style]}
"""

# ---------------------------
# 습관 체크인 UI
# ---------------------------
st.subheader("✅ 오늘의 습관 체크인")

col1, col2 = st.columns(2)

with col1:
    wake = st.checkbox("⏰ 기상 미션")
    water = st.checkbox("💧 물 마시기")
    study = st.checkbox("📚 공부/독서")

with col2:
    exercise = st.checkbox("🏃 운동하기")
    sleep = st.checkbox("😴 수면")

habits = {
    "기상 미션": wake,
    "물 마시기": water,
    "공부/독서": study,
    "운동하기": exercise,
    "수면": sleep,
}

mood = st.slider("🙂 오늘 기분 점수", 1, 10, 5)

city = st.selectbox(
    "📍 도시 선택",
    ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
     "Gwangju", "Suwon", "Ulsan", "Jeju", "Sejong"]
)

coach_style = st.radio(
    "🎤 코치 스타일",
    ["스파르타 코치", "따뜻한 멘토", "게임 마스터"],
    horizontal=True
)

# ---------------------------
# 달성률 + 메트릭
# ---------------------------
completed = sum(habits.values())
rate = int((completed / 5) * 100)

m1, m2, m3 = st.columns(3)
m1.metric("📈 달성률", f"{rate}%")
m2.metric("✅ 달성 습관", f"{completed}/5")
m3.metric("🙂 기분", mood)

# ---------------------------
# 주간 차트
# ---------------------------
st.subheader("📊 주간 기록")

days = [(datetime.now() - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]
demo = [40, 60, 50, 70, 80, 65, rate]

df = pd.DataFrame({"날짜": days, "달성률": demo}).set_index("날짜")
st.bar_chart(df)

# ---------------------------
# 결과 표시
# ---------------------------
st.divider()
st.subheader("🧠 컨디션 리포트")

if st.button("🚀 컨디션 리포트 생성"):
    pokemon = get_pokemon()
    weather = get_weather(city)

    if pokemon is None:
        st.error("포켓몬 정보를 불러오지 못했어요 😢")
    else:
        report = generate_local_report(habits, mood, weather, pokemon, coach_style)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### 🌦️ 오늘의 날씨")
            st.info(f"{city} — {weather}")

        with c2:
            st.markdown("### 🎮 오늘의 포켓몬")
            st.image(pokemon["image"], width=250)
            st.write(f"**{pokemon['name']}**")
            st.write("타입:", ", ".join(pokemon["types"]))

            stat_df = pd.DataFrame(
                pokemon["stats"].values(),
                index=pokemon["stats"].keys(),
                columns=["Stat"]
            )
            st.bar_chart(stat_df, color="#ff0000")

        st.markdown("### 📝 코치 리포트")
        st.markdown(report)

        st.markdown("### 📢 공유용 텍스트")
        st.code(
            f"🎮 오늘의 습관 리포트\n"
            f"달성률: {rate}%\n"
            f"기분: {mood}/10\n"
            f"파트너 포켓몬: {pokemon['name']}"
        )

# ---------------------------
# 하단 안내
# ---------------------------
with st.expander("ℹ️ 사용 API"):
    st.markdown("""
- **PokeAPI**  
  https://pokeapi.co/api/v2/pokemon/{number}

✔ 무료  
✔ API Key 불필요  
✔ 상업적 사용 가능
""")
