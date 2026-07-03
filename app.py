import streamlit as st
import requests
import math
from datetime import datetime

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻·足球预测", layout="centered", initial_sidebar_state="expanded")
st.title("⚽ 六爻纳甲 · 足球预测引擎")
st.caption("融合京房纳甲、野鹤实战、黄金策、28断法 | 支持五大联赛、日韩、世界杯")

# ============================================================
# 2. 侧边栏：所有输入参数
# ============================================================
with st.sidebar:
    st.header("📌 比赛基本信息")
    home_team = st.text_input("🏠 主队名称", value="利物浦")
    away_team = st.text_input("✈️ 客队名称", value="曼城")
    league = st.selectbox("🏆 联赛/赛事", ["英超", "西甲", "德甲", "意甲", "法甲", "日职", "K联赛", "世界杯"])

    st.divider()
    st.header("📊 核心数据（手动输入）")
    bf_big = st.number_input("📈 必发大球指数 (0-100)", min_value=0, max_value=100, value=55, step=1)
    bf_small = st.number_input("📉 必发小球指数 (0-100)", min_value=0, max_value=100, value=45, step=1)
    xg_home = st.number_input("⚽ 主队xG (预期进球)", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
    xg_away = st.number_input("⚽ 客队xG (预期进球)", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
    elo_home = st.number_input("📊 主队ELO评分", min_value=1000, max_value=2500, value=1900, step=10)
    elo_away = st.number_input("📊 客队ELO评分", min_value=1000, max_value=2500, value=1850, step=10)

    st.divider()
    st.header("🔮 六爻参数（二十八法量化）")
    
    # ---- 用神定位 ----
    st.subheader("① 用神定位")
    yong_shen = st.selectbox("取用神", ["世应（主客实力）", "子孙（进球）", "妻财（收益）", "官鬼（裁判/防守）", "兄弟（竞争）"])
    # 转换为系数影响
    yong_shen_factor = {"世应（主客实力）": 1.0, "子孙（进球）": 1.2, "妻财（收益）": 0.9, "官鬼（裁判/防守）": 0.8, "兄弟（竞争）": 0.7}.get(yong_shen, 1.0)
    
    # ---- 世应主客 ----
    shi_ying = st.selectbox("世应关系", ["世克应（主胜）", "应克世（客胜）", "世生应（主让）", "应生世（客让）", "比和（平局）"])
    shi_ying_map = {"世克应（主胜）": 1.15, "应克世（客胜）": 0.85, "世生应（主让）": 0.95, "应生世（客让）": 1.05, "比和（平局）": 1.0}
    shi_ying_coef = shi_ying_map[shi_ying]
    
    # ---- 六冲六合 ----
    liu_chong_he = st.selectbox("卦局", ["六冲（快速分胜负）", "六合（僵持拉锯）", "无特殊"])
    liu_chong_he_map = {"六冲（快速分胜负）": 1.2, "六合（僵持拉锯）": 0.8, "无特殊": 1.0}
    liu_coef = liu_chong_he_map[liu_chong_he]
    
    # ---- 空亡 ----
    kong_wang = st.selectbox("用神空亡", ["无空亡", "假空（出空应验）", "真空（事难成）"])
    kong_wang_map = {"无空亡": 1.0, "假空（出空应验）": 0.9, "真空（事难成）": 0.6}
    kong_coef = kong_wang_map[kong_wang]
    
    # ---- 三合局 ----
    san_he = st.selectbox("三合局", ["无", "子孙局（大球）", "官鬼局（小球）", "财局（收益）"])
    san_he_map = {"无": 1.0, "子孙局（大球）": 1.25, "官鬼局（小球）": 0.75, "财局（收益）": 1.0}
    san_he_coef = san_he_map[san_he]
    
    # ---- 反吟伏吟 ----
    fan_yin = st.selectbox("卦象反复", ["无", "伏吟（拉锯反复）", "反吟（局势逆转）"])
    fan_yin_map = {"无": 1.0, "伏吟（拉锯反复）": 0.9, "反吟（局势逆转）": 1.3}
    fan_yin_coef = fan_yin_map[fan_yin]
    
    # ---- 六神主象 ----
    liu_shen = st.selectbox("六神主象", ["青龙（顺攻）", "白虎（强攻）", "朱雀（波动）", "腾蛇（变数）", "勾陈（僵持）", "玄武（偷袭）"])
    liu_shen_map = {"青龙（顺攻）": 1.1, "白虎（强攻）": 1.2, "朱雀（波动）": 1.0, "腾蛇（变数）": 1.15, "勾陈（僵持）": 0.8, "玄武（偷袭）": 0.9}
    liu_shen_coef = liu_shen_map[liu_shen]
    
    # ---- 用神旺衰 ----
    wang_shuai = st.selectbox("用神旺衰", ["旺", "相", "休", "囚", "死"])
    wang_shuai_map = {"旺": 1.3, "相": 1.1, "休": 1.0, "囚": 0.8, "死": 0.6}
    wang_shuai_coef = wang_shuai_map[wang_shuai]
    
    # ---- 综合爻位动变 ----
    moving_yao = st.selectbox("动爻位置", ["无动爻", "初爻", "二爻", "三爻", "四爻", "五爻", "上爻", "多动"])
    yao_effect = {"无动爻":1.0, "初爻":0.8, "二爻":0.9, "三爻":1.0, "四爻":1.1, "五爻":1.15, "上爻":1.2, "多动":1.05}.get(moving_yao, 1.0)

    st.divider()
    st.header("⚔️ 战意系数")
    zhan_yi = st.selectbox("比赛阶段战意", 
                           options=[("保级/争冠关键战", 1.4), ("淘汰赛", 1.2), ("普通联赛", 1.0), ("无欲无求", 0.85), ("友谊赛", 0.7)],
                           format_func=lambda x: x[0])
    zhan_yi_value = zhan_yi[1]

    st.divider()
    st.header("🌐 数据源（可选）")
    api_key = st.text_input("API-Football Key (免费)", type="password", help="不填则纯手动模式")
    fixture_id = st.number_input("比赛ID (用于自动抓取)", min_value=1, value=123456, step=1)
    use_manual_odds = st.checkbox("手动输入赔率 (否则尝试自动抓取)")
    if use_manual_odds:
        col1, col2, col3 = st.columns(3)
        with col1:
            init_h = st.number_input("初盘主胜", value=1.80, step=0.05)
            curr_h = st.number_input("变盘主胜", value=1.75, step=0.05)
        with col2:
            init_d = st.number_input("初盘平局", value=3.50, step=0.05)
            curr_d = st.number_input("变盘平局", value=3.60, step=0.05)
        with col3:
            init_a = st.number_input("初盘客胜", value=4.00, step=0.05)
            curr_a = st.number_input("变盘客胜", value=4.20, step=0.05)
        initial_odds = [init_h, init_d, init_a]
        current_odds = [curr_h, curr_d, curr_a]
    else:
        initial_odds = current_odds = None

# ============================================================
# 3. 核心算法函数
# ============================================================
def poisson_prob(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def fetch_odds_from_api(api_key, fixture_id):
    if not api_key:
        return None, None
    headers = {"x-rapidapi-key": api_key}
    try:
        resp = requests.get(f"https://v3.football.api-sports.io/odds", 
                            headers=headers, 
                            params={"fixture": fixture_id}, timeout=8)
        data = resp.json()
        if data.get("response"):
            bookie = data["response"][0]["bookmakers"][0]
            bets = bookie["bets"][0]["values"]
            initial = []
            current = []
            for item in bets:
                if "value" in item:
                    if item["value"] == "Home":
                        initial.append(float(item.get("odd", 1.80)))
                    elif item["value"] == "Draw":
                        initial.append(float(item.get("odd", 3.50)))
                    elif item["value"] == "Away":
                        initial.append(float(item.get("odd", 4.00)))
            if len(initial) != 3:
                return None, None
            current = initial  # 简化，实际应用应获取即时赔率
            return initial, current
        else:
            return None, None
    except:
        return None, None

def check_alert(initial, current):
    alerts = []
    labels = ["主胜", "平局", "客胜"]
    if initial and current:
        for i in range(3):
            drop = initial[i] - current[i]
            if drop > 0.2:
                alerts.append(f"⚠️ {labels[i]} 赔率骤降 {drop:.2f} (初盘 {initial[i]:.2f} → 现盘 {current[i]:.2f})")
    return alerts

def predict_scores(xg_h, xg_a, elo_h, elo_a, zhan_yi, 
                   shi_ying_coef, liu_coef, kong_coef, san_he_coef, 
                   fan_yin_coef, liu_shen_coef, wang_shuai_coef, 
                   yao_effect, yong_shen_factor, bf_big, bf_small):
    """融合六爻二十八法的预测模型"""
    # 1. ELO修正
    elo_diff = elo_h - elo_a
    elo_factor_h = 1 + (elo_diff / 400) * 0.1
    elo_factor_a = 1 - (elo_diff / 400) * 0.1

    # 2. 必发修正
    if bf_big > 65 and bf_small < 35:
        xg_h *= 1.2
        xg_a *= 1.2
    elif bf_big > 60:
        xg_h *= 1.08
        xg_a *= 1.08
    elif bf_small > 60 and bf_big < 40:
        xg_h *= 0.9
        xg_a *= 0.9

    # 3. 六爻二十八法综合系数（乘积作用于λ）
    liu_yao_factor = (shi_ying_coef * liu_coef * kong_coef * san_he_coef * 
                      fan_yin_coef * liu_shen_coef * wang_shuai_coef * yao_effect * yong_shen_factor)
    
    # 4. 主客队分别应用（主队用全系数，客队用部分反向）
    lam_h = xg_h * elo_factor_h * zhan_yi * liu_yao_factor
    lam_a = xg_a * elo_factor_a * zhan_yi * (1 / max(liu_yao_factor, 0.1))

    # 5. 泊松分布
    scores = {}
    for i in range(5):
        for j in range(5):
            prob = poisson_prob(lam_h, i) * poisson_prob(lam_a, j)
            scores[f"{i}-{j}"] = prob * 100
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_scores, lam_h, lam_a

def kelly_calc(odds, prob):
    if odds <= 1:
        return 0
    return (odds * prob - (1 - prob)) / odds

# ============================================================
# 4. 主界面
# ============================================================
if st.button("🚀 开始预测", type="primary", use_container_width=True):
    # 获取赔率
    initial, current = None, None
    if api_key and not use_manual_odds:
        with st.spinner("正在拉取实时赔率数据..."):
            initial, current = fetch_odds_from_api(api_key, fixture_id)
            if initial:
                st.success("✅ 自动获取赔率成功")
            else:
                st.warning("⚠️ 自动获取失败，使用默认赔率")
                initial = [1.80, 3.50, 4.00]
                current = [1.80, 3.50, 4.00]
    elif use_manual_odds and initial_odds:
        initial = initial_odds
        current = current_odds
        st.info("📝 使用手动输入的赔率")
    else:
        initial = [1.80, 3.50, 4.00]
        current = [1.80, 3.50, 4.00]
        st.info("📝 使用默认赔率（无变盘预警）")

    # 变盘预警
    if initial and current:
        alerts = check_alert(initial, current)
        if alerts:
            st.error("🚨 变盘预警触发！")
            for a in alerts:
                st.warning(a)
        else:
            st.success("✅ 无剧烈变盘，数据平稳")

    # 预测
    top_scores, lam_h, lam_a = predict_scores(
        xg_home, xg_away, elo_home, elo_away, zhan_yi_value,
        shi_ying_coef, liu_coef, kong_coef, san_he_coef,
        fan_yin_coef, liu_shen_coef, wang_shuai_coef,
        yao_effect, yong_shen_factor, bf_big, bf_small
    )

    # 显示结果
    st.subheader(f"📊 {home_team} vs {away_team} 预测详情")
    col1, col2 = st.columns(2)
    col1.metric(f"{home_team} 预期进球 λ", f"{lam_h:.2f}")
    col2.metric(f"{away_team} 预期进球 λ", f"{lam_a:.2f}")

    st.subheader("🏆 最可能比分 (概率%)")
    for score, prob in top_scores:
        st.progress(min(int(prob), 100), text=f"{score}  →  {prob:.2f}%")

    # 凯利
    if top_scores:
        max_prob = top_scores[0][1] / 100
        current_win_odds = current[0] if current and len(current)>0 else 1.80
        kelly_val = kelly_calc(current_win_odds, max_prob)
        st.subheader("💰 凯利风控指标")
        if kelly_val > 0.7:
            st.error(f"🚨 凯利值 {kelly_val:.2f}，庄家赔付风险高！")
        elif kelly_val > 0.4:
            st.warning(f"⚠️ 凯利值 {kelly_val:.2f}，存在一定风险")
        else:
            st.success(f"✅ 凯利值 {kelly_val:.2f}，模型信心稳定")

    # 显示六爻参数摘要
    with st.expander("🔮 六爻参数摘要（二十八法量化）"):
        st.write(f"- **用神**：{yong_shen}（系数 {yong_shen_factor:.2f}）")
        st.write(f"- **世应**：{shi_ying}（系数 {shi_ying_coef:.2f}）")
        st.write(f"- **卦局**：{liu_chong_he}（系数 {liu_coef:.2f}）")
        st.write(f"- **空亡**：{kong_wang}（系数 {kong_coef:.2f}）")
        st.write(f"- **三合**：{san_he}（系数 {san_he_coef:.2f}）")
        st.write(f"- **反吟/伏吟**：{fan_yin}（系数 {fan_yin_coef:.2f}）")
        st.write(f"- **六神**：{liu_shen}（系数 {liu_shen_coef:.2f}）")
        st.write(f"- **旺衰**：{wang_shuai}（系数 {wang_shuai_coef:.2f}）")
        st.write(f"- **动爻**：{moving_yao}（系数 {yao_effect:.2f}）")
        st.write(f"**综合六爻因子**：{shi_ying_coef * liu_coef * kong_coef * san_he_coef * fan_yin_coef * liu_shen_coef * wang_shuai_coef * yao_effect * yong_shen_factor:.2f}")

st.divider()
st.caption("💡 左侧边栏调整六爻参数，融合二十八断法，点击预测即得结果。")
