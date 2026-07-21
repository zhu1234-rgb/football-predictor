import streamlit as st
import pandas as pd
import numpy as np
import math
import hashlib
from datetime import datetime
from scipy.stats import poisson

# ===================== 页面基础配置 =====================
st.set_page_config(page_title="FUSIONAPP 赛事融合预测", layout="wide", initial_sidebar_state="expanded")
st.title("⚽ FUSIONAPP 足球融合预测模型")
st.caption("数理统计模型 + 六爻模拟铜钱卦 双引擎融合｜支持五大联赛/K1/K2/J1/J2")


# =========================================================
# 模块1：数理统计模型（泊松分布）
# =========================================================
LEAGUE_AVG_TOTAL = {
    "英超": 2.8, "西甲": 2.6, "德甲": 2.9,
    "意甲": 2.6, "法甲": 2.5,
    "K1联赛": 2.3, "K2联赛": 2.2,
    "J1联赛": 2.4, "J2联赛": 2.3,
}

def predict_match_stat(home_team, away_team, league="K1联赛",
                       home_attack=1.0, away_attack=1.0,
                       home_defense=1.0, away_defense=1.0):
    """基于泊松分布计算胜平负概率"""
    league_avg = LEAGUE_AVG_TOTAL.get(league, 2.5)
    home_goals_avg = (league_avg / 2) * home_attack / away_defense
    away_goals_avg = (league_avg / 2) * away_attack / home_defense

    max_goals = 6
    probs = {}
    for hg in range(max_goals + 1):
        for ag in range(max_goals + 1):
            p = poisson.pmf(hg, home_goals_avg) * poisson.pmf(ag, away_goals_avg)
            probs[(hg, ag)] = p

    home_win = sum(p for (h, a), p in probs.items() if h > a)
    draw = sum(p for (h, a), p in probs.items() if h == a)
    away_win = sum(p for (h, a), p in probs.items() if h < a)

    total = home_win + draw + away_win
    return {
        "主胜概率": round(home_win / total, 4),
        "平局概率": round(draw / total, 4),
        "客胜概率": round(away_win / total, 4)
    }


# =========================================================
# 模块2：六爻模拟铜钱起卦
# =========================================================
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
ZHI_WUXING = {'寅': '木', '卯': '木', '巳': '火', '午': '火', '申': '金', '酉': '金',
              '亥': '水', '子': '水', '辰': '土', '戌': '土', '丑': '土', '未': '土'}

def get_liuqin(shi_zhi, target_zhi):
    wx_order = {'木': 0, '火': 1, '土': 2, '金': 3, '水': 4}
    s = wx_order[ZHI_WUXING[shi_zhi]]
    t = wx_order[ZHI_WUXING[target_zhi]]
    if s == t:
        return '兄弟'
    if (s + 1) % 5 == t:
        return '子孙'
    if (t + 1) % 5 == s:
        return '父母'
    if (s + 2) % 5 == t:
        return '妻财'
    if (t + 2) % 5 == s:
        return '官鬼'
    return '兄弟'

def coin_sim_gua(home_team, away_team, kick_time_str, league="K1联赛"):
    """模拟铜钱摇卦，返回六亲生克倾向"""
    seed_str = f"{home_team}|{away_team}|{kick_time_str}|{league}"
    hash_digest = hashlib.sha256(seed_str.encode('utf-8')).hexdigest()
    hex_part = hash_digest[:12]

    yao = [1 if int(hex_part[i*2:(i+1)*2], 16) / 255.0 > 0.5 else 0 for i in range(6)]

    move_idx = int(hash_digest[12], 16) % 6
    change_yao = yao.copy()
    change_yao[move_idx] = 1 - change_yao[move_idx]

    yang_pos = [i for i, v in enumerate(yao) if v == 1]
    shi_idx = yang_pos[len(yang_pos)//2] if len(yang_pos) % 2 == 1 else 2

    dt = datetime.strptime(kick_time_str.split()[0], "%m-%d")
    day_index = (dt.day + dt.month) % 12
    day_zhi = ZHI[day_index]
    shi_zhi = ZHI[(ZHI.index(day_zhi) + shi_idx) % 12]
    ying_zhi = ZHI[(ZHI.index(shi_zhi) + 4) % 12]

    shengke = get_liuqin(shi_zhi, ying_zhi)

    if shengke in ('妻财', '子孙'):
        return {"主胜概率": 0.70, "平局概率": 0.15, "客胜概率": 0.15}
    elif shengke in ('官鬼', '父母'):
        return {"主胜概率": 0.15, "平局概率": 0.15, "客胜概率": 0.70}
    else:
        return {"主胜概率": 0.25, "平局概率": 0.50, "客胜概率": 0.25}


# =========================================================
# 模块3：融合加权函数
# =========================================================
def fusion_calc(stat_data, gua_data, w1, w2):
    """加权融合并归一化"""
    home = stat_data["主胜概率"] * w1 + gua_data["主胜概率"] * w2
    draw = stat_data["平局概率"] * w1 + gua_data["平局概率"] * w2
    away = stat_data["客胜概率"] * w1 + gua_data["客胜概率"] * w2

    total = home + draw + away
    home = round(home / total, 4)
    draw = round(draw / total, 4)
    away = round(away / total, 4)

    best = max([("主胜", home), ("平局", draw), ("客胜", away)], key=lambda x: x[1])
    return {
        "主胜概率": home,
        "平局概率": draw,
        "客胜概率": away,
        "模型推荐": best[0],
        "置信分值": best[1]
    }


# =========================================================
# 模块4：比分 & 总进球 & 半全场预测（扩展）
# =========================================================
def poisson_score_matrix(home_avg, away_avg, max_goals=6):
    probs = {}
    for hg in range(max_goals + 1):
        for ag in range(max_goals + 1):
            p = poisson.pmf(hg, home_avg) * poisson.pmf(ag, away_avg)
            probs[(hg, ag)] = p
    return probs

def aggregate_from_matrix(probs_matrix):
    wdl = {'主胜': 0, '平局': 0, '客胜': 0}
    total_goals = {}
    for (hg, ag), p in probs_matrix.items():
        if hg > ag:
            wdl['主胜'] += p
        elif hg == ag:
            wdl['平局'] += p
        else:
            wdl['客胜'] += p
        tg = hg + ag
        total_goals[tg] = total_goals.get(tg, 0) + p
    return wdl, dict(sorted(total_goals.items()))

def most_likely_score(probs_matrix):
    best = max(probs_matrix, key=probs_matrix.get)
    return best, probs_matrix[best]

def half_full_prob(home_avg, away_avg, half_ratio=0.4, max_goals=4):
    home_half_avg = home_avg * half_ratio
    away_half_avg = away_avg * half_ratio
    half_probs = {'主胜': 0, '平局': 0, '客胜': 0}
    for hg in range(max_goals + 1):
        for ag in range(max_goals + 1):
            p = poisson.pmf(hg, home_half_avg) * poisson.pmf(ag, away_half_avg)
            if hg > ag:
                half_probs['主胜'] += p
            elif hg == ag:
                half_probs['平局'] += p
            else:
                half_probs['客胜'] += p
    full_probs, _ = aggregate_from_matrix(poisson_score_matrix(home_avg, away_avg, max_goals))
    hf_probs = {}
    for half_res in ['主胜', '平局', '客胜']:
        for full_res in ['主胜', '平局', '客胜']:
            key = f"{half_res}_{full_res}"
            hf_probs[key] = half_probs.get(half_res, 0) * full_probs.get(full_res, 0)
    total = sum(hf_probs.values())
    if total > 0:
        for k in hf_probs:
            hf_probs[k] /= total
    return hf_probs

def predict_extended(home, away, league, home_avg, away_avg):
    """比分、总进球、半全场预测（纯统计部分）"""
    matrix = poisson_score_matrix(home_avg, away_avg, max_goals=6)
    _, tg = aggregate_from_matrix(matrix)
    best_score, best_prob = most_likely_score(matrix)
    hf = half_full_prob(home_avg, away_avg, half_ratio=0.4, max_goals=4)
    sorted_hf = sorted(hf.items(), key=lambda x: -x[1])[:3]
    return {
        "最可能比分": f"{best_score[0]}:{best_score[1]}",
        "比分概率": round(best_prob, 4),
        "总进球分布": tg,
        "半全场Top3": sorted_hf
    }


# =========================================================
# Streamlit UI
# =========================================================

# ===== 侧边栏 =====
with st.sidebar:
    st.header("⚙️ 模型权重配置")
    stat_weight = st.slider("数理模型权重", min_value=0.4, max_value=0.9, value=0.7, step=0.05)
    gua_weight = round(1 - stat_weight, 2)
    st.info(f"当前配置：数理 {stat_weight} | 卦象 {gua_weight}")

    league_options = ["英超", "西甲", "意甲", "德甲", "法甲", "K1联赛", "K2联赛", "J1联赛", "J2联赛"]
    select_leagues = st.multiselect("筛选联赛", league_options, default=["K1联赛", "J1联赛"])

    run_mode = st.radio("运行模式", ["单场分析", "批量赛程预测"])

    st.divider()
    st.caption("【重要提示】模型仅作数据推演研究，购彩请理性。卦象仅作为趋势辅助，不存在百分百精准预测。")


# ===== 单场分析 =====
if run_mode == "单场分析":
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("主队名称")
        league = st.selectbox("联赛", league_options, index=5)
    with col2:
        away_team = st.text_input("客队名称")
        kick_time = st.text_input("开赛时间（格式：03-07 13:00）", value="03-07 13:00")

    col3, col4 = st.columns(2)
    with col3:
        home_attack = st.number_input("主队进攻系数", value=1.0, step=0.05)
        home_defense = st.number_input("主队防守系数", value=1.0, step=0.05)
    with col4:
        away_attack = st.number_input("客队进攻系数", value=1.0, step=0.05)
        away_defense = st.number_input("客队防守系数", value=1.0, step=0.05)

    if st.button("开始运算预测", type="primary"):
        if not home_team or not away_team:
            st.warning("请填写主客队名称！")
        else:
            with st.spinner("1. 数理模型计算中..."):
                stat_result = predict_match_stat(home_team, away_team, league,
                                                 home_attack, away_attack,
                                                 home_defense, away_defense)

            with st.spinner("2. 模拟铜钱起卦推演..."):
                gua_result = coin_sim_gua(home_team, away_team, kick_time, league)

            with st.spinner("3. 融合加权计算最终概率..."):
                final_result = fusion_calc(stat_result, gua_result, stat_weight, gua_weight)

            # 扩展预测
            league_avg = LEAGUE_AVG_TOTAL.get(league, 2.5)
            home_avg = (league_avg / 2) * home_attack / away_defense
            away_avg = (league_avg / 2) * away_attack / home_defense
            extended = predict_extended(home_team, away_team, league, home_avg, away_avg)

            st.divider()

            # 融合结果
            st.subheader("🎯 融合预测结果")
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("主胜", f"{final_result['主胜概率']:.1%}")
            col_res2.metric("平局", f"{final_result['平局概率']:.1%}")
            col_res3.metric("客胜", f"{final_result['客胜概率']:.1%}")
            st.success(f"✅ 模型推荐：**{final_result['模型推荐']}**（置信度 {final_result['置信分值']:.1%}）")

            # 比分 & 总进球 & 半全场
            st.subheader("📊 比分 & 总进球 & 半全场")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.metric("最可能比分", extended["最可能比分"], f"概率 {extended['比分概率']:.1%}")
                st.write("**总进球分布**")
                tg_df = pd.DataFrame([extended["总进球分布"]]).T.reset_index()
                tg_df.columns = ["进球数", "概率"]
                st.dataframe(tg_df, use_container_width=True, hide_index=True)
            with col_e2:
                st.write("**半全场 Top3**")
                for k, v in extended["半全场Top3"]:
                    st.write(f"• {k.replace('_', ' → ')}：{v:.1%}")

            # 分层详情
            with st.expander("📋 分层结果详情"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.subheader("数理模型")
                    st.dataframe(pd.DataFrame([stat_result]), use_container_width=True)
                with c2:
                    st.subheader("六爻卦象")
                    st.dataframe(pd.DataFrame([gua_result]), use_container_width=True)
                with c3:
                    st.subheader("融合结果")
                    st.dataframe(pd.DataFrame([final_result]), use_container_width=True)


# ===== 批量赛程 =====
elif run_mode == "批量赛程预测":
    st.info("上传赛程 CSV，表头：league,date,home,away")
    upload_file = st.file_uploader("上传赛程文件", type=["csv"])

    if upload_file:
        df_schedule = pd.read_csv(upload_file, encoding="utf-8-sig")
        df_filter = df_schedule[df_schedule["league"].isin(select_leagues)]
        st.dataframe(df_filter, use_container_width=True)

        if st.button("批量启动全部预测", type="primary"):
            output_list = []
            progress_bar = st.progress(0)
            total = len(df_filter)

            for idx, row in df_filter.iterrows():
                progress_bar.progress((idx + 1) / total)
                ht = row["home"]
                at = row["away"]
                dt = row["date"]
                lg = row["league"]

                stat_res = predict_match_stat(ht, at, lg)
                gua_res = coin_sim_gua(ht, at, dt, lg)
                final_res = fusion_calc(stat_res, gua_res, stat_weight, gua_weight)

                final_res["联赛"] = lg
                final_res["开赛时间"] = dt
                final_res["主队"] = ht
                final_res["客队"] = at
                output_list.append(final_res)

            result_df = pd.DataFrame(output_list)
            st.success("✅ 批量运算完成！")
            st.dataframe(result_df, use_container_width=True)

            csv_data = result_df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 下载预测结果 CSV", data=csv_data,
                               file_name="fusion_prediction.csv", mime="text/csv")
