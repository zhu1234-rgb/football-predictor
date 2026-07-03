import streamlit as st
import math
import hashlib
from datetime import datetime

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻·胜平负预测", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 六爻 · 胜平负预测引擎")
st.caption("融合《春秋太卜》《六爻心源》取象法 | 自动起卦 | 仅胜平负")

# ============================================================
# 2. 赛事列表
# ============================================================
LEAGUE_AVG_TOTAL = {
    "英超": 2.8, "西甲": 2.6, "德甲": 2.9, "意甲": 2.5, "法甲": 2.5,
    "欧冠": 2.6, "欧联": 2.5, "欧协联": 2.4,
    "日职": 2.4, "日乙": 2.3, "K联赛": 2.3, "K2联赛": 2.2,
    "世界杯": 2.2, "亚洲杯": 2.2, "非洲杯": 2.1, "美洲杯": 2.3, "欧洲杯": 2.4,
    "芬超": 2.4, "芬甲": 2.3, "挪甲": 2.4, "瑞典超": 2.5, "冰岛超": 2.4,
    "爱超": 2.3, "爱甲": 2.2, "苏超": 2.5, "英冠": 2.6, "英甲": 2.5, "英乙": 2.4,
    "荷甲": 2.7, "荷乙": 2.6, "葡超": 2.5, "比甲": 2.5, "土超": 2.4, "俄超": 2.3,
    "奥甲": 2.4, "瑞士超": 2.4, "丹超": 2.5, "波超": 2.3, "克甲": 2.3,
    "巴西甲": 2.4, "巴西乙": 2.3, "阿甲": 2.3, "美职联": 2.6, "墨超": 2.4,
    "中超": 2.5, "澳超": 2.6, "沙特联": 2.5, "阿联酋超": 2.4, "卡塔尔联": 2.3,
    "女足世界杯": 2.0, "女足英超": 2.2,
}

# ============================================================
# 3. 战意系数（12级分级）
# ============================================================
ZHAN_YI_LIST = [
    ("🏆 决赛生死战", 1.45),
    ("🔥 出线/保级生死战", 1.40),
    ("⚔️ 洲际资格卡位战", 1.25),
    ("💢 德比复仇大战", 1.22),
    ("🏅 淘汰赛", 1.20),
    ("📈 刷净胜球卡位战", 1.10),
    ("⚽ 普通联赛", 1.00),
    ("🏠 主场荣誉轮换", 0.90),
    ("😐 无欲无求", 0.85),
    ("🧪 提前出线练兵", 0.78),
    ("📉 已降级摆烂", 0.70),
    ("🤝 友谊赛/热身赛", 0.65),
]

# ============================================================
# 4. 卦象数据
# ============================================================
GUA_LEI_XIANG = {
    "乾": {"五行":"金","人物":"领导、父亲、冠军","比赛":"冠军、强势方、大胜"},
    "坤": {"五行":"土","人物":"母亲、老妇、民众","比赛":"被动挨打、防守反击"},
    "震": {"五行":"木","人物":"长男、军人、新秀","比赛":"新锐冲击、快速反击"},
    "巽": {"五行":"木","人物":"长女、教师、替补","比赛":"边路传中、定位球"},
    "坎": {"五行":"水","人物":"中男、医生、守门员","比赛":"防守稳固、点球大战"},
    "离": {"五行":"火","人物":"中女、文人、核心球员","比赛":"核心发挥、进球大战"},
    "艮": {"五行":"土","人物":"少男、后卫、替补","比赛":"防守反击、铁桶阵"},
    "兑": {"五行":"金","人物":"少女、歌手、边锋","比赛":"边路突破、点球决胜"}
}
GUA_XING_QING = {
    "乾": "刚健主动，冠军气质，进攻为主",
    "坤": "柔顺被动，防守反击，稳扎稳打",
    "震": "活跃冲动，快速反击，冲击力强",
    "巽": "灵活多变，边路渗透，定位球战术",
    "坎": "沉稳防守，门将神勇，点球决胜",
    "离": "华丽进攻，核心球员，进球大战",
    "艮": "坚固防守，密集阵型，小胜格局",
    "兑": "边路突破，点球机会，伤病隐患"
}
def get_gua_style(gua):
    return GUA_XING_QING.get(gua, "常规打法")

# ============================================================
# 5. 卦象数据结构
# ============================================================
GUA_LIST = [
    "乾","坤","屯","蒙","需","讼","师","比","小畜","履","泰","否","同人","大有","谦","豫",
    "随","蛊","临","观","噬嗑","贲","剥","复","无妄","大畜","颐","大过","坎","离",
    "咸","恒","遁","大壮","晋","明夷","家人","睽","蹇","解","损","益","夬","姤",
    "萃","升","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑",
    "涣","节","中孚","小过","既济","未济"
]
GUA_STRUCT = {
    "乾":(1,1),"坤":(8,8),"屯":(6,4),"蒙":(7,6),"需":(6,1),"讼":(1,6),
    "师":(6,8),"比":(8,6),"小畜":(5,1),"履":(1,2),"泰":(8,1),"否":(1,8),
    "同人":(1,3),"大有":(3,1),"谦":(7,8),"豫":(4,8),"随":(2,4),"蛊":(7,5),
    "临":(8,2),"观":(5,8),"噬嗑":(3,4),"贲":(7,3),"剥":(7,8),"复":(4,8),
    "无妄":(1,4),"大畜":(7,1),"颐":(7,4),"大过":(2,5),"坎":(6,6),"离":(3,3),
    "咸":(2,7),"恒":(4,5),"遁":(1,7),"大壮":(4,1),"晋":(3,8),"明夷":(8,3),
    "家人":(5,3),"睽":(3,2),"蹇":(7,6),"解":(4,6),"损":(7,2),"益":(5,4),
    "夬":(2,1),"姤":(1,5),"萃":(2,8),"升":(5,8),"困":(2,6),"井":(5,6),
    "革":(2,3),"鼎":(3,5),"震":(4,4),"艮":(7,7),"渐":(5,7),"归妹":(4,2),
    "丰":(4,3),"旅":(3,7),"巽":(5,5),"兑":(2,2),"涣":(5,6),"节":(6,2),
    "中孚":(5,2),"小过":(4,7),"既济":(6,3),"未济":(3,6)
}
GUA_WUXING_MAP = {1:"金",2:"金",3:"火",4:"木",5:"木",6:"水",7:"土",8:"土"}

LIUHE_SET = {"泰","否","咸","恒","损","益","既济","未济","节","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑","涣","中孚","小过"}
GUIHUN_SET = {"大有","需","大畜","随","蛊","同人","晋","归妹"}
YOUHUN_SET = {"需","讼","明夷","晋","中孚","大过","颐","大壮"}
LIUCHONG_SET = {"乾","坎","兑","离","震","巽","艮","坤"}

# ============================================================
# 6. 自动起卦函数
# ============================================================
def auto_gua_by_teams(home, away):
    combined = f"{home}_{away}"
    hash_obj = hashlib.md5(combined.encode())
    hex_digest = hash_obj.hexdigest()
    seed = int(hex_digest[:8], 16)
    zhu_index = seed % 64
    bian_index = (seed // 64) % 64
    dong_index = seed % 6
    dong_yao_list = ["初爻","二爻","三爻","四爻","五爻","上爻"]
    dong_yao = dong_yao_list[dong_index]
    return GUA_LIST[zhu_index], GUA_LIST[bian_index], dong_yao

# ============================================================
# 7. 五行生克
# ============================================================
def wuxing_sheng_ke(wo, ta):
    sheng = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
    ke = {"金":"木","木":"土","土":"水","水":"火","火":"金"}
    if wo == ta: return 0
    elif sheng[wo] == ta: return 1
    elif ke[wo] == ta: return -1
    elif sheng[ta] == wo: return -2
    elif ke[ta] == wo: return 2
    else: return 0

# ============================================================
# 8. 六爻逐爻详解
# ============================================================
def analyze_yaos(zhu_gua, bian_gua, dong_yao):
    yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    yao_wei_xiang = {
        "初爻": "震位，主足、根基、开端、民众、基层",
        "二爻": "离位，主腹、内心、文书、家宅、中层",
        "三爻": "艮位，主手、门户、兄弟、竞争、转折",
        "四爻": "巽位，主股、妻财、市场、商旅、外联",
        "五爻": "坎位，主耳、君王、道路、官非、中枢",
        "上爻": "兑位，主口、外境、神佛、末路、结果"
    }
    yao_list = []
    for yname in yao_names:
        is_dong = (yname == dong_yao)
        if is_dong:
            dong_detail = {
                "初爻": "动于初爻（震位）：事件根基变动，开局或有变数。",
                "二爻": "动于二爻（离位）：内部或家宅之变，球队内部或有调整。",
                "三爻": "动于三爻（艮位）：竞争转折之变，走势在中段发生变化。",
                "四爻": "动于四爻（巽位）：边路或替补可能成为奇兵。",
                "五爻": "动于五爻（坎位）：核心球员表现影响全局，或有关键判罚。",
                "上爻": "动于上爻（兑位）：终局之变，尾声或有绝杀/绝平。"
            }
            desc = dong_detail.get(yname, "动爻需结合全卦。")
        else:
            static_detail = {
                "初爻": "静于初爻：基础稳定，开局稳健。",
                "二爻": "静于二爻：内部稳定，心态平和。",
                "三爻": "静于三爻：竞争胶着，中段僵持。",
                "四爻": "静于四爻：边路稳定，外援未出奇招。",
                "五爻": "静于五爻：中枢稳固，核心正常发挥。",
                "上爻": "静于上爻：结局平稳，结果与预期一致。"
            }
            desc = static_detail.get(yname, "静爻常规解读。")
        wei_xiang = yao_wei_xiang.get(yname, "")
        yao_list.append({
            "爻位": yname,
            "是否动爻": is_dong,
            "爻位取象": wei_xiang,
            "解读": desc
        })
    return yao_list

# ============================================================
# 9. 自动解卦函数
# ============================================================
def auto_jie_gua(zhu_gua, bian_gua, dong_yao):
    ping_ju = 0.0
    ke_adv = 1.0
    zhu_adv = 1.0
    jin_qiu_limit = 0
    both_score = False
    fen_sheng_fu = 0.0
    detail = []
    gua_analysis = []

    if zhu_gua in LIUHE_SET:
        ping_ju += 0.6
        jin_qiu_limit = 3
        detail.append("六合→平局优先")
        gua_analysis.append("六合卦：平局倾向高")
    if zhu_gua in GUIHUN_SET:
        ping_ju += 0.3
        both_score = True
        detail.append("归魂→胶着反复")
        gua_analysis.append("归魂卦：胶着反复")
    if zhu_gua in YOUHUN_SET:
        ke_adv *= 1.15
        detail.append("游魂→客不败")
        gua_analysis.append("游魂卦：客不败")
    if zhu_gua in LIUCHONG_SET:
        fen_sheng_fu += 0.7
        detail.append("六冲→分胜负")
        gua_analysis.append("六冲卦：分胜负")

    if bian_gua in LIUHE_SET:
        ping_ju += 0.4
        detail.append("变卦六合→趋平")
        gua_analysis.append("变卦六合：趋平")

    if dong_yao == "无动爻":
        detail.append("无动爻→体用比和")
        gua_analysis.append("无动爻：实力均衡")
    else:
        dong_idx = {"初爻":0,"二爻":1,"三爻":2,"四爻":3,"五爻":4,"上爻":5}[dong_yao]
        shang, xia = GUA_STRUCT[zhu_gua]
        shang_wu = GUA_WUXING_MAP[shang]
        xia_wu = GUA_WUXING_MAP[xia]
        if dong_idx < 3:
            ti_wu, yong_wu = shang_wu, xia_wu
            detail.append(f"动{dong_yao}(下卦)→下卦为用(客)")
        else:
            ti_wu, yong_wu = xia_wu, shang_wu
            detail.append(f"动{dong_yao}(上卦)→上卦为用(客)")
        rel = wuxing_sheng_ke(ti_wu, yong_wu)
        if rel == -2:
            zhu_adv *= 1.12
            detail.append("用生体→主利")
            gua_analysis.append("用生体：主利")
        elif rel == 2:
            ke_adv *= 1.15
            detail.append("用克体→客利")
            gua_analysis.append("用克体：客利")
        elif rel == 1:
            ke_adv *= 1.10
            ping_ju += 0.15
            detail.append("体生用→主耗，客不败")
            gua_analysis.append("体生用：客不败")
        elif rel == -1:
            zhu_adv *= 1.10
            detail.append("体克用→主胜机")
            gua_analysis.append("体克用：主胜机")
        else:
            ping_ju += 0.3
            detail.append("比和→平局")
            gua_analysis.append("比和：平局")

    if dong_yao in ["四爻","五爻","上爻"]:
        zhu_adv *= 1.05
        detail.append("动在上卦→进攻端活跃")
        gua_analysis.append("上卦动：进攻")
    else:
        ke_adv *= 1.05
        detail.append("动在下卦→防守端稳固")
        gua_analysis.append("下卦动：防守")

    zong_he = 1.0 + (zhu_adv-1.0) + (ke_adv-1.0) + (ping_ju*0.3) - (fen_sheng_fu*0.2)
    zong_he = max(0.5, min(1.5, zong_he))

    zhu_style = get_gua_style(zhu_gua)
    bian_style = get_gua_style(bian_gua)
    gua_analysis.append(f"主卦风格：{zhu_style}")
    gua_analysis.append(f"变卦风格：{bian_style}")

    if zhu_gua == "乾" and dong_yao in ["五爻","上爻"]:
        gua_analysis.append("乾动上位：冠军相")
    if zhu_gua in LIUCHONG_SET and dong_yao != "无动爻":
        gua_analysis.append("六冲有动：无闷平")

    yao_details = analyze_yaos(zhu_gua, bian_gua, dong_yao)

    return {
        "ping_ju_tend": min(1.0, ping_ju),
        "ke_advantage": ke_adv,
        "zhu_advantage": zhu_adv,
        "jin_qiu_limit": jin_qiu_limit,
        "both_score": both_score,
        "fen_sheng_fu": fen_sheng_fu,
        "zong_he": round(zong_he, 3),
        "detail": "；".join(detail) if detail else "常规",
        "analysis": " | ".join(gua_analysis) if gua_analysis else "常规分析",
        "yao_details": yao_details
    }

# ============================================================
# 10. 核心预测函数（仅胜平负）
# ============================================================
def poisson_prob(lam, k):
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def predict_wdl_only(league_avg, zhan_yi, liu_factors):
    total_goals = league_avg
    lam_h = total_goals * 0.5 * 2
    lam_a = total_goals * 0.5 * 2

    zhu_adv = liu_factors["zhu_advantage"]
    ke_adv = liu_factors["ke_advantage"]
    ping_ju = liu_factors["ping_ju_tend"]
    jin_limit = liu_factors["jin_qiu_limit"]
    both_score = liu_factors["both_score"]
    fen_sheng = liu_factors["fen_sheng_fu"]
    zong = liu_factors["zong_he"]

    if ping_ju > 0.5:
        adjust = 1.0 - (ping_ju - 0.5) * 0.4
        zong = min(zong, adjust)
        avg_lam = (lam_h + lam_a) / 2
        lam_h = avg_lam * 0.85
        lam_a = avg_lam * 0.85
    else:
        lam_h *= zhu_adv * zhan_yi * zong
        lam_a *= ke_adv * zhan_yi * zong

    if jin_limit > 0:
        total = lam_h + lam_a
        if total > jin_limit:
            scale = jin_limit / total
            lam_h *= scale
            lam_a *= scale

    if both_score:
        lam_h = max(lam_h, 0.8)
        lam_a = max(lam_a, 0.8)

    if fen_sheng > 0.5:
        diff = lam_h - lam_a
        lam_h += diff * 0.1
        lam_a -= diff * 0.1

    lam_h = max(0.3, lam_h)
    lam_a = max(0.3, lam_a)

    win_prob = 0.0
    draw_prob = 0.0
    lose_prob = 0.0
    for i in range(8):
        for j in range(8):
            prob = (math.exp(-lam_h) * (lam_h ** i) / math.factorial(i)) * \
                   (math.exp(-lam_a) * (lam_a ** j) / math.factorial(j))
            if i > j:
                win_prob += prob
            elif i == j:
                draw_prob += prob
            else:
                lose_prob += prob

    if ping_ju > 0.5:
        draw_prob = draw_prob * (1 + ping_ju * 0.3)
        total = win_prob + draw_prob + lose_prob
        if total > 0:
            win_prob /= total
            draw_prob /= total
            lose_prob /= total

    return win_prob, draw_prob, lose_prob, lam_h, lam_a

# ============================================================
# 11. 生成胜平负推荐（三层推演风格）
# ============================================================
def generate_wdl_recommendation(win_p, draw_p, lose_p, liu_factors, zhan_yi):
    probs = {"主胜": win_p, "平局": draw_p, "客胜": lose_p}
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)

    # 首推、次推
    first = sorted_probs[0]
    second = sorted_probs[1] if len(sorted_probs) > 1 else ("-", 0)

    # 战意提示
    zhan_yi_hint = ""
    if zhan_yi >= 1.2:
        zhan_yi_hint = "（战意强烈，分胜负概率大）"
    elif zhan_yi <= 0.85:
        zhan_yi_hint = "（战意不足，需防平局）"

    # 卦象修正提示
    gua_hint = ""
    if liu_factors['ping_ju_tend'] > 0.6:
        gua_hint = "卦象平局倾向强"
    elif liu_factors['zhu_advantage'] > liu_factors['ke_advantage']:
        gua_hint = "卦象主队占优"
    else:
        gua_hint = "卦象客队占优"

    return {
        "first": first[0],
        "first_prob": first[1],
        "second": second[0],
        "second_prob": second[1],
        "win": win_p,
        "draw": draw_p,
        "lose": lose_p,
        "zhan_yi_hint": zhan_yi_hint,
        "gua_hint": gua_hint,
        "zong_he": liu_factors['zong_he'],
        "ping_ju_tend": liu_factors['ping_ju_tend'],
        "analysis": liu_factors['analysis']
    }

# ============================================================
# 12. 界面布局
# ============================================================
if 'zhu_gua' not in st.session_state:
    st.session_state.zhu_gua = "乾"
if 'bian_gua' not in st.session_state:
    st.session_state.bian_gua = "坤"
if 'dong_yao' not in st.session_state:
    st.session_state.dong_yao = "无动爻"
if 'liu_result' not in st.session_state:
    st.session_state.liu_result = auto_jie_gua(st.session_state.zhu_gua, st.session_state.bian_gua, st.session_state.dong_yao)

with st.expander("📌 比赛基本信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("请输入主队", value="澳大利亚")
        league = st.selectbox("请选择赛事", list(LEAGUE_AVG_TOTAL.keys()))
    with col2:
        away_team = st.text_input("请输入客队", value="佛得角")
        match_time = st.datetime_input("比赛时间", value=datetime.now())

zhan_yi_opt = st.selectbox("⚔️ 战意系数", ZHAN_YI_LIST, format_func=lambda x: x[0])
zhan_yi = zhan_yi_opt[1]

# ============================================================
# 13. 预测按钮
# ============================================================
if st.button("🚀 预测胜平负", type="primary", use_container_width=True):
    # 自动起卦
    zhu, bian, dong = auto_gua_by_teams(home_team, away_team)
    st.session_state.zhu_gua = zhu
    st.session_state.bian_gua = bian
    st.session_state.dong_yao = dong
    liu_factors = auto_jie_gua(zhu, bian, dong)
    st.session_state.liu_result = liu_factors

    league_avg = LEAGUE_AVG_TOTAL[league]
    win_p, draw_p, lose_p, lam_h, lam_a = predict_wdl_only(league_avg, zhan_yi, liu_factors)
    win_p *= 100
    draw_p *= 100
    lose_p *= 100

    result = generate_wdl_recommendation(win_p, draw_p, lose_p, liu_factors, zhan_yi)

    # -------- 显示结果（三层推演风格） --------
    st.markdown("---")
    st.markdown(f"### 📊 胜平负预测 —— {home_team} vs {away_team}")
    st.caption(f"赛事：{league} | 时间：{match_time.strftime('%Y-%m-%d %H:%M') if match_time else '未设置'} | {zhan_yi_opt[0]}")

    st.markdown("---")

    # 首推 & 次推（突出显示）
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏆 首推", f"{result['first']}", f"{result['first_prob']:.1f}%")
    with col2:
        st.metric("🥈 次推", f"{result['second']}", f"{result['second_prob']:.1f}%")

    st.markdown("---")

    # 概率详情（进度条更直观）
    st.write("**概率详情**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.progress(min(int(result['win']), 100), text=f"主胜 {result['win']:.1f}%")
    with col2:
        st.progress(min(int(result['draw']), 100), text=f"平局 {result['draw']:.1f}%")
    with col3:
        st.progress(min(int(result['lose']), 100), text=f"客胜 {result['lose']:.1f}%")

    st.markdown("---")

    # 融合推荐
    if result['first'] == "主胜":
        fusion_rec = f"首选主胜（{result['first_prob']:.1f}%）"
    elif result['first'] == "平局":
        fusion_rec = f"首选平局（{result['first_prob']:.1f}%）"
    else:
        fusion_rec = f"首选客胜（{result['first_prob']:.1f}%）"

    st.info(f"💡 **融合推荐**：{fusion_rec}　|　{result['gua_hint']}　|　综合系数 {result['zong_he']:.2f}")

    st.markdown("---")
    st.caption(f"模型版本：V4.0 胜平负专精版 | 平局倾向 {result['ping_ju_tend']:.2f} | {result['zhan_yi_hint']}")

    # 展开详细卦象
    with st.expander("🔮 卦象解读（含逐爻详解）"):
        st.write(f"**主卦**：{zhu}　|　**变卦**：{bian}　|　**动爻**：{dong}")
        st.write(f"**平局倾向**：{liu_factors['ping_ju_tend']:.2f}")
        st.write(f"**主队优势系数**：{liu_factors['zhu_advantage']:.2f}")
        st.write(f"**客队优势系数**：{liu_factors['ke_advantage']:.2f}")
        st.write(f"**综合系数**：{liu_factors['zong_he']}")
        st.write(f"**卦象细节**：{liu_factors['detail']}")
        st.write(f"**风格解读**：{liu_factors['analysis']}")
        st.write("---")
        st.subheader("📜 六爻逐爻详解")
        for yao in liu_factors['yao_details']:
            dong_tag = "🔥 动爻" if yao['是否动爻'] else "静爻"
            st.write(f"**{yao['爻位']}** ({dong_tag})")
            st.write(f"  - 爻位取象：{yao['爻位取象']}")
            st.write(f"  - 解读：{yao['解读']}")

st.caption("💡 点击「预测胜平负」自动起卦并输出 | 基于泊松分布+六爻修正")
