# 强制加载 Manifest（放在最最前面）
import streamlit as st
import math
import random
from datetime import datetime

st.markdown(
    '<link rel="manifest" href="manifest.json">',
    unsafe_allow_html=True
)

# ⚽ 强制设置浏览器标签图标
st.markdown("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://img.icons8.com/color/96/000000/football2.png">
    <link rel="icon" type="image/png" sizes="32x32" href="https://img.icons8.com/color/96/000000/football2.png">
""", unsafe_allow_html=True)

# 页面配置
st.set_page_config(
    page_title="V14.9 预测器",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 核心模型函数 ---
def get_gua(home, away, match_type="general"):
    """模拟起卦（据事取卦）"""
    gua_pool = {
        "general": ("火天大有", "体克用，强者胜"),
        "draw": ("地山谦", "比和，平局相"),
        "knockout": ("火雷噬嗑", "激烈胶着"),
        "slaughter": ("雷天大壮", "大胜之象")
    }
    if "德" in home or "巴" in away:
        return gua_pool["slaughter"]
    if "加纳" in away or "奥地利" in away:
        return gua_pool["draw"]
    return gua_pool["general"]

def compute_lam(home_elo, away_elo, home_xg, away_xg, home_form, away_form, patches):
    """计算进攻λ"""
    elo_factor = (home_elo - away_elo) / 2000 * 0.4
    xg_factor = (home_xg / (home_xg + away_xg + 0.01)) * 0.4
    form_factor = (home_form - away_form) * 0.1 + 0.5
    lam_h = max(0.3, elo_factor + xg_factor + form_factor)
    lam_a = max(0.3, -elo_factor + (away_xg / (home_xg + away_xg + 0.01)) * 0.4 + (away_form - home_form) * 0.1 + 0.5)
    if patches.get("away_travel", 0) >= 10:
        lam_a *= 0.75
    if patches.get("rotation_home", 0) >= 4:
        lam_h *= 0.75
    if home_xg >= 2.5 and away_xg <= 0.8:
        lam_h *= 1.8
        lam_a *= 0.7
    return round(lam_h, 2), round(lam_a, 2)

def poisson_prob(lam, goals):
    return (math.exp(-lam) * (lam ** goals)) / math.factorial(goals)

def predict_match(home, away, match_type, home_elo, away_elo, home_xg, away_xg, home_form, away_form, patches):
    gua_name, gua_desc = get_gua(home, away, match_type)
    lam_h, lam_a = compute_lam(home_elo, away_elo, home_xg, away_xg, home_form, away_form, patches)
    score_probs = {}
    for h in range(0, 5):
        for a in range(0, 5):
            prob = poisson_prob(lam_h, h) * poisson_prob(lam_a, a)
            score_probs[(h, a)] = prob
    best_score = max(score_probs, key=score_probs.get)
    best_prob = score_probs[best_score]
    home_win_prob = sum(prob for (h, a), prob in score_probs.items() if h > a)
    draw_prob = sum(prob for (h, a), prob in score_probs.items() if h == a)
    away_win_prob = sum(prob for (h, a), prob in score_probs.items() if h < a)
    if home_win_prob > draw_prob and home_win_prob > away_win_prob:
        direction = "主胜"
    elif away_win_prob > draw_prob:
        direction = "客胜"
    else:
        direction = "平局"
    if direction == "主胜" and best_score[0] - best_score[1] >= 2:
        handicap = "让胜"
    elif direction == "主胜" and best_score[0] - best_score[1] == 1:
        handicap = "让平"
    else:
        handicap = "让负"
    total_goals = best_score[0] + best_score[1]
    if total_goals <= 1:
        total_goal_desc = "小球（0-1球）"
    elif total_goals == 2:
        total_goal_desc = "中球（2球）"
    else:
        total_goal_desc = "大球（3球+）"
    return {
        "gua": gua_name,
        "gua_desc": gua_desc,
        "lam_h": lam_h,
        "lam_a": lam_a,
        "direction": direction,
        "handicap": handicap,
        "total_goals": total_goal_desc,
        "best_score": f"{best_score[0]}-{best_score[1]}",
        "best_prob": best_prob,
        "home_win_prob": home_win_prob,
        "draw_prob": draw_prob,
        "away_win_prob": away_win_prob
    }

# ---------- 界面布局 ----------
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .big-font { font-size:24px !important; font-weight:bold; }
    .result-box { background-color:#ffffff; border-radius:10px; padding:15px; margin:10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.image("https://img.icons8.com/color/96/000000/football2.png", width=80)
st.title("⚽ V14.9 梅花观象预测")
st.caption("输入比赛信息，获取四步预测报告")

col1, col2 = st.columns(2)
with col1:
    home = st.text_input("🏠 主队名称", placeholder="如：巴西")
    home_elo = st.number_input("主队ELO", value=2000, step=10)
    home_xg = st.number_input("主队xG", value=1.5, step=0.1)
    home_form = st.number_input("主队近5场胜率", value=0.6, step=0.05)
    rotation = st.number_input("主队轮换人数（预估）", value=0, step=1, min_value=0)
with col2:
    away = st.text_input("✈️ 客队名称", placeholder="如：日本")
    away_elo = st.number_input("客队ELO", value=1900, step=10)
    away_xg = st.number_input("客队xG", value=1.2, step=0.1)
    away_form = st.number_input("客队近5场胜率", value=0.5, step=0.05)
    away_travel = st.number_input("客队飞行距离（小时）", value=0, step=1, min_value=0)

match_type = st.selectbox("比赛性质", ["常规", "淘汰赛", "保级/出线生死战", "强弱悬殊"])

if st.button("🔮 开始推演", use_container_width=True):
    if not home or not away:
        st.warning("请填写主客队名称")
    else:
        patches = {"rotation_home": rotation, "away_travel": away_travel}
        match_type_map = {"常规": "general", "淘汰赛": "knockout", "保级/出线生死战": "draw", "强弱悬殊": "slaughter"}
        result = predict_match(
            home, away, match_type_map[match_type],
            home_elo, away_elo,
            home_xg, away_xg,
            home_form, away_form,
            patches
        )
        st.divider()
        st.subheader("📋 四步预测报告")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**① 方向预测**")
            st.success(f"**{result['direction']}**")
            st.caption(f"卦象：{result['gua']}（{result['gua_desc']}）")
            st.caption(f"主胜 {result['home_win_prob']:.1%} | 平 {result['draw_prob']:.1%} | 客胜 {result['away_win_prob']:.1%}")
        with col_b:
            st.markdown("**② 让球预测**（主队-1）")
            st.info(f"**{result['handicap']}**")
            st.caption(f"λ主={result['lam_h']}，λ客={result['lam_a']}")
        st.markdown("**③ 总进球预测**")
        st.metric("预期总进球", result['total_goals'])
        st.markdown("**④ 唯一比分**")
        st.markdown(f"<div style='font-size:48px; text-align:center;'>{result['best_score']}</div>", unsafe_allow_html=True)
        st.caption(f"模型置信度：{result['best_prob']:.2%}")
        st.subheader("📊 比分概率分布（前5）")
        sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:5]
        for (h, a), prob in sorted_scores:
            st.progress(prob, text=f"{h}-{a} : {prob:.2%}")
