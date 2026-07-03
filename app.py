import streamlit as st
import requests
import math

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 足球预测引擎", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 足球预测引擎")
st.caption("所有参数都在主页面，滑动即可调整")

# ============================================================
# 2. 所有输入控件（无侧边栏）
# ============================================================

# ---- 2.1 比赛基本信息 ----
with st.expander("📌 比赛基本信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("🏠 主队", value="利物浦")
        league = st.selectbox("🏆 联赛", ["英超", "西甲", "德甲", "意甲", "法甲", "日职", "K联赛", "世界杯"])
    with col2:
        away_team = st.text_input("✈️ 客队", value="曼城")

# ---- 2.2 核心数据 ----
with st.expander("📊 核心数据（必发 / xG / ELO）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        bf_big = st.number_input("📈 必发大球指数", min_value=0, max_value=100, value=55, step=1)
        xg_home = st.number_input("⚽ 主队xG", min_value=0.0, max_value=5.0, value=1.8, step=0.1)
        elo_home = st.number_input("📊 主队ELO", min_value=1000, max_value=2500, value=1900, step=10)
    with col2:
        bf_small = st.number_input("📉 必发小球指数", min_value=0, max_value=100, value=45, step=1)
        xg_away = st.number_input("⚽ 客队xG", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
        elo_away = st.number_input("📊 客队ELO", min_value=1000, max_value=2500, value=1850, step=10)

# ---- 2.3 六爻参数（二十八法） ----
with st.expander("🔮 六爻参数（二十八法）", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        yong_shen = st.selectbox("取用神", ["世应（主客实力）", "子孙（进球）", "妻财（收益）", "官鬼（裁判/防守）", "兄弟（竞争）"])
        shi_ying = st.selectbox("世应关系", ["世克应（主胜）", "应克世（客胜）", "世生应（主让）", "应生世（客让）", "比和（平局）"])
        liu_chong_he = st.selectbox("卦局", ["六冲（快速分胜负）", "六合（僵持拉锯）", "无特殊"])
        kong_wang = st.selectbox("用神空亡", ["无空亡", "假空（出空应验）", "真空（事难成）"])
        san_he = st.selectbox("三合局", ["无", "子孙局（大球）", "官鬼局（小球）", "财局（收益）"])
    with col2:
        fan_yin = st.selectbox("卦象反复", ["无", "伏吟（拉锯反复）", "反吟（局势逆转）"])
        liu_shen = st.selectbox("六神主象", ["青龙（顺攻）", "白虎（强攻）", "朱雀（波动）", "腾蛇（变数）", "勾陈（僵持）", "玄武（偷袭）"])
        wang_shuai = st.selectbox("用神旺衰", ["旺", "相", "休", "囚", "死"])
        moving_yao = st.selectbox("动爻位置", ["无动爻", "初爻", "二爻", "三爻", "四爻", "五爻", "上爻", "多动"])
    
    # 战意系数放在六爻下面
    zhan_yi = st.selectbox("⚔️ 战意系数", 
                           options=[("保级/争冠关键战", 1.4), ("淘汰赛", 1.2), ("普通联赛", 1.0), ("无欲无求", 0.85), ("友谊赛", 0.7)],
                           format_func=lambda x: x[0])
    zhan_yi_value = zhan_yi[1]

# ---- 2.4 赔率与API ----
with st.expander("🌐 赔率数据 & API", expanded=False):
    use_manual_odds = st.checkbox("手动输入赔率（开启后忽略API）")
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
        api_key = st.text_input("API-Football Key (免费)", type="password", help="不填则使用默认赔率")
        fixture_id = st.number_input("比赛ID", min_value=1, value=123456, step=1)

# ============================================================
# 3. 核心函数（不变）
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
            current = initial
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
                   shi_ying, liu_chong_he, kong_wang, san_he, 
                   fan_yin, liu_shen, wang_shuai, moving_yao, 
                   yong_shen, bf_big, bf_small):
    # 将文字选择转为系数（与之前一致）
    shi_ying_map = {"世克应（主胜）": 1.15, "应克世（客胜）": 0.85, "世生应（主让）": 0.95, "应生世（客让）": 1.05, "比和（平局）": 1.0}
    liu_map = {"六冲（快速分胜负）": 1.2, "六合（僵持拉锯）": 0.8, "无特殊": 1.0}
    kong_map = {"无空亡": 1.0, "假空（出空应验）": 0.9, "真空（事难成）": 0.6}
    san_map = {"无": 1.0, "子孙局（大球）": 1.25, "官鬼局（小球）": 0.75, "财局（收益）": 1.0}
    fan_map = {"无": 1.0, "伏吟（拉锯反复）": 0.9, "反吟（局势逆转）": 1.3}
    liu_shen_map = {"青龙（顺攻）": 1.1, "白虎（强攻）": 1.2, "朱雀（波动）": 1.0, "腾蛇（变数）": 1.15, "勾陈（僵持）": 0.8, "玄武（偷袭）": 0.9}
    wang_map = {"旺": 1.3, "相": 1.1, "休": 1.0, "囚": 0.8, "死": 0.6}
    yao_map = {"无动爻":1.0, "初爻":0.8, "二爻":0.9, "三爻":1.0, "四爻":1.1, "五爻":1.15, "上爻":1.2, "多动":1.05}
    yong_map = {"世应（主客实力）":1.0, "子孙（进球）":1.2, "妻财（收益）":0.9, "官鬼（裁判/防守）":0.8, "兄弟（竞争）":0.7}

    shi_coef = shi_ying_map[shi_ying]
    liu_coef = liu_map[liu_chong_he]
    kong_coef = kong_map[kong_wang]
    san_coef = san_map[san_he]
    fan_coef = fan_map[fan_yin]
    shen_coef = liu_shen_map[liu_shen]
    wang_coef = wang_map[wang_shuai]
    yao_coef = yao_map[moving_yao]
    yong_coef = yong_map[yong_shen]

    # ELO修正
    elo_diff = elo_h - elo_a
    elo_factor_h = 1 + (elo_diff / 400) * 0.1
    elo_factor_a = 1 - (elo_diff / 400) * 0.1

    # 必发修正
    if bf_big > 65 and bf_small < 35:
        xg_h *= 1.2
        xg_a *= 1.2
    elif bf_big > 60:
        xg_h *= 1.08
        xg_a *= 1.08
    elif bf_small > 60 and bf_big < 40:
        xg_h *= 0.9
        xg_a *= 0.9

    # 六爻综合因子
    liu_yao_factor = (shi_coef * liu_coef * kong_coef * san_coef * 
                      fan_coef * shen_coef * wang_coef * yao_coef * yong_coef)
    
    lam_h = xg_h * elo_factor_h * zhan_yi * liu_yao_factor
    lam_a = xg_a * elo_factor_a * zhan_yi * (1 / max(liu_yao_factor, 0.1))

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
# 4. 预测按钮与结果展示
# ============================================================
if st.button("🚀 开始预测", type="primary", use_container_width=True):
    # ---- 4.1 获取赔率 ----
    if use_manual_odds and initial_odds:
        initial = initial_odds
        current = current_odds
        st.info("📝 使用手动赔率")
    else:
        if api_key:
            with st.spinner("拉取赔率数据..."):
                initial, current = fetch_odds_from_api(api_key, fixture_id)
                if initial:
                    st.success("✅ API获取成功")
                else:
                    st.warning("⚠️ API获取失败，使用默认赔率")
                    initial = [1.80, 3.50, 4.00]
                    current = [1.80, 3.50, 4.00]
        else:
            initial = [1.80, 3.50, 4.00]
            current = [1.80, 3.50, 4.00]
            st.info("📝 未提供API Key，使用默认赔率")

    # ---- 4.2 变盘预警 ----
    alerts = check_alert(initial, current)
    if alerts:
        st.error("🚨 变盘预警！")
        for a in alerts:
            st.warning(a)
    else:
        st.success("✅ 赔率稳定，无剧烈变盘")

    # ---- 4.3 预测 ----
    # 从selectbox获取的值传入函数
    top_scores, lam_h, lam_a = predict_scores(
        xg_home, xg_away, elo_home, elo_away, zhan_yi_value,
        shi_ying, liu_chong_he, kong_wang, san_he,
        fan_yin, liu_shen, wang_shuai, moving_yao,
        yong_shen, bf_big, bf_small
    )

    # ---- 4.4 结果显示 ----
    st.subheader(f"📊 {home_team} vs {away_team}")
    col1, col2 = st.columns(2)
    col1.metric(f"{home_team} λ", f"{lam_h:.2f}")
    col2.metric(f"{away_team} λ", f"{lam_a:.2f}")

    st.subheader("🏆 最可能比分")
    for score, prob in top_scores:
        st.progress(min(int(prob), 100), text=f"{score}  →  {prob:.2f}%")

    # ---- 4.5 凯利 ----
    if top_scores:
        max_prob = top_scores[0][1] / 100
        current_win_odds = current[0] if current and len(current)>0 else 1.80
        kelly_val = kelly_calc(current_win_odds, max_prob)
        st.subheader("💰 凯利风控")
        if kelly_val > 0.7:
            st.error(f"🚨 凯利值 {kelly_val:.2f}，风险高")
        elif kelly_val > 0.4:
            st.warning(f"⚠️ 凯利值 {kelly_val:.2f}")
        else:
            st.success(f"✅ 凯利值 {kelly_val:.2f}，稳定")

st.caption("💡 所有参数都在上方折叠面板中，调整后点击预测。")
