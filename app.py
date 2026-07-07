import streamlit as st
import math
import hashlib
from datetime import datetime

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻预测 V9.3.12（修正版）", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 六爻 · 纯卦象预测引擎 V9.3.12")
st.caption("基于07-07赛果修正：巴西乙主场加成、平局溢价收窄、强队客场减值精准化")

# ============================================================
# 2. 联赛基准进球（V9.3.12 校准）
# ============================================================
LEAGUE_AVG_TOTAL = {
    "英超": 2.8, "西甲": 2.6, "德甲": 2.9, "意甲": 2.5, "法甲": 2.5,
    "欧冠": 2.6, "欧联": 2.6, "欧协联": 2.5,
    "日职": 2.4, "日乙": 2.3, "K联赛": 2.3, "K2联赛": 2.2,
    "世界杯": 2.2, "亚洲杯": 2.2, "非洲杯": 2.1, "美洲杯": 2.3, "欧洲杯": 2.4,
    "国际友谊赛": 2.8, "芬超": 2.4, "芬甲": 2.3, "挪甲": 2.4,
    "瑞典超": 2.5, "冰岛超": 2.4, "爱超": 2.3, "爱甲": 2.2,
    "苏超": 2.5, "英冠": 2.6, "英甲": 2.5, "英乙": 2.4,
    "荷甲": 2.7, "荷乙": 2.6, "葡超": 2.5, "比甲": 2.5,
    "土超": 2.4, "俄超": 2.3, "奥甲": 2.4, "瑞士超": 2.4,
    "丹超": 2.5, "波超": 2.3, "克甲": 2.3, "巴西甲": 2.4,
    "巴西乙": 2.6,  # 提升至2.6，匹配实际进球
    "阿甲": 2.3, "美职联": 2.6, "墨超": 2.4,
    "中超": 2.5, "澳超": 2.6, "沙特联": 2.5, "阿联酋超": 2.4,
    "卡塔尔联": 2.3, "女足世界杯": 2.0, "女足英超": 2.2,
    "意乙": 2.3, "亚冠": 2.4, "英足总杯": 2.6, "解放者杯": 2.3,
    "亚冠乙": 2.4, "国王杯": 2.4, "荷兰杯": 2.5, "德国杯": 2.6,
    "意大利杯": 2.4, "法国杯": 2.5, "足总杯": 2.6,
}

# ============================================================
# 3. 球队实力分层（完整版，同前）
# ============================================================
TEAM_STRENGTH = {
    "巴西":5, "阿根廷":5, "法国":5, "英格兰":5, "西班牙":5,
    "德国":5, "葡萄牙":5, "比利时":5, "荷兰":5, "意大利":5,
    "拜仁慕尼黑":5, "巴黎圣日耳曼":5, "皇家马德里":5, "巴塞罗那":5,
    "曼城":5, "利物浦":5, "阿森纳":5, "国际米兰":5,
    "马德里竞技":5, "勒沃库森":4, "多特蒙德":4,
    "博德闪耀":5, "本菲卡":5,
    "尤文图斯":4, "AC米兰":4, "那不勒斯":4, "亚特兰大":4,
    "莱比锡红牛":4, "塞维利亚":3, "毕尔巴鄂竞技":4, "比利亚雷亚尔":4,
    "阿斯顿维拉":3, "切尔西":3, "曼联":4, "热刺":4,
    "纽卡斯尔联":4, "西汉姆联":4, "布伦特福德":4,
    "克罗地亚":4, "乌拉圭":4, "瑞士":4, "瑞典":4, "丹麦":4,
    "墨西哥":4, "美国":4, "塞内加尔":4, "摩洛哥":4, "日本":4,
    "韩国":4, "澳大利亚":4, "尼日利亚":4, "哥伦比亚":4,
    "蔚山现代":4, "全北现代":3, "浦项制铁":4, "马尔默":3,
    "赫尔辛基":3, "莫尔德":4, "利雅得胜利":4, "吉达国民":4,
    "吉达联合":4, "水晶宫":4, "利雅得新月":4, "大阪钢巴":4,
    "神户胜利船":4, "皇家社会":3, "里尔":4, "波尔图":4,
    "里斯本竞技":4, "罗马":4, "拉齐奥":4, "佛罗伦萨":4,
    "科林蒂安":4, "帕尔梅拉斯":4, "弗拉门戈":4, "弗鲁米嫩塞":4,
    "博卡青年":4, "河床":4, "弗赖堡":4, "布拉加":4,
    "诺丁汉森林":4, "雅典AEK":4, "斯特拉斯":3, "霍芬海姆":4,
    "奥格斯堡":4, "洛里昂":4, "伯恩茅斯":4, "里昂":4,
    "布兰":4, "拉斯决心":4, "新未来城":3, "通德拉":3,
    "伊普斯":3, "浦和红钻":3, "仁川联":4, "江原FC":4,
    "福冈黄蜂":4, "天狼星":4, "赫塔费":4, "尼斯":4,
    "布赖合作":4, "艾禾斯堡":3, "勒芒":3, "阿尔梅勒":3,
    "圣保利":3, "克莱蒙":3, "阿维SAD":3, "夏洛特FC":3,
    "圣何塞地震":3, "安养FC":3, "利勒斯特":3, "麦克阿瑟":3,
    "芬洛":3, "不伦瑞克":3, "阿拉维斯":3, "埃尔切":3,
    "莱万特":3, "科莫":3, "敦刻尔克":3, "海登海姆":4,
    "厄瓜多尔":3, "巴拉圭":3, "智利":3, "秘鲁":3, "土耳其":3,
    "奥地利":3, "苏格兰":3, "挪威":3, "乌克兰":3, "伊朗":3,
    "沙特阿拉伯":3, "卡塔尔":3, "阿联酋":3, "阿尔及利亚":3,
    "科特迪瓦":3, "加纳":3, "埃及":3, "突尼斯":3,
    "匈牙利":3, "罗马尼亚":3, "威尔士":3, "希腊":3, "黑山":3,
    "斯洛文尼亚":3, "塞尔维亚":3, "塞尔塔":3, "贝蒂斯":3,
    "巴列卡诺":3, "美因茨":3, "水晶体育":3, "麦德林":3,
    "新西兰":2, "加拿大":2, "佛得角":2, "库拉索":2,
    "波黑":2, "斯洛伐克":2, "捷克":2, "南非":2,
    "伊拉克":2, "约旦":2, "乌兹别克斯坦":2, "巴拿马":2,
    "海地":2, "刚果(金)":2, "富川FC":2, "拉赫蒂":2,
    "玛丽港":2, "哈卡":2, "桑德兰":2, "利兹联":2,
    "伯恩利":2, "沃特福德":2, "莱万特":2, "西班牙人":2,
    "马略卡":2, "阿拉维斯":2, "加的斯":2, "奥维耶多":2,
    "科莫":2, "莱切":2, "比萨":2, "恩波利":2,
    "赫尔城":2, "牛津联":2, "米尔沃尔":2, "朴次茅斯":2,
    "布莱克本":2, "西布朗":2, "雷克斯汉姆":2, "斯旺西":2,
    "伯明翰":2, "诺维奇":2, "考文垂":2, "女王巡游":2,
    "米堡":2, "麦克阿瑟":2, "纽卡斯托":2, "阿德莱德联":2,
    "西悉尼":2, "珀斯光荣":2, "中央海岸":2, "布里斯班":2,
    "惠灵顿凤凰":2, "墨尔本胜利":2, "奥克兰FC":2, "悉尼FC":2,
    "墨尔本城":2, "清水鼓动":2, "町田泽维亚":2, "京都不死鸟":2,
    "名古屋鲸":2, "浦和红钻":2, "鹿岛鹿角":2, "金泉尚武":2,
    "基多大学":2,
    # 补全
    "尤文图德":2, "埃尔夫斯堡":3, "哈马比":3, "海于格松":3,
    "奥德":3, "MP米克":3, "哈卡":3, "累西腓航海":2,
}

def get_strength(team):
    clean = team.split('(')[0].strip()
    return TEAM_STRENGTH.get(clean, TEAM_STRENGTH.get(team, 3))

# ============================================================
# 4. 卦象数据库（不变）
# ============================================================
GUA_LIST = [
    "乾","坤","屯","蒙","需","讼","师","比","小畜","履","泰","否","同人","大有","谦","豫",
    "随","蛊","临","观","噬嗑","贲","剥","复","无妄","大畜","颐","大过","坎","离",
    "咸","恒","遁","大壮","晋","明夷","家人","睽","蹇","解","损","益","夬","姤",
    "萃","升","困","井","革","鼎","震","艮","渐","归妹","丰","旅","巽","兑",
    "涣","节","中孚","小过","既济","未济"
]
GUA_LEI_XIANG = {
    "乾":{"五行":"金","比赛":"冠军"}, "坤":{"五行":"土","比赛":"防守"},
    "震":{"五行":"木","比赛":"冲击"}, "巽":{"五行":"木","比赛":"边路"},
    "坎":{"五行":"水","比赛":"防守"}, "离":{"五行":"火","比赛":"进攻"},
    "艮":{"五行":"土","比赛":"铁桶"}, "兑":{"五行":"金","比赛":"突破"}
}
GUA_JI_XIONG = {
    "泰":"大吉，主队有利","否":"大凶，客队有利","谦":"大吉，主队有利",
    "豫":"吉，主队有利","随":"吉，主队有利","蛊":"凶，客队有利",
    "临":"吉，主队有利","观":"中，平局倾向","噬嗑":"中，客队有利",
    "贲":"中，主队有利","剥":"凶，客队有利","复":"吉，主队有利",
    "无妄":"吉，主队有利","大畜":"吉，主队有利","颐":"中，平局倾向",
    "大过":"凶，客队有利","坎":"凶，客队有利","离":"中，主队有利",
    "咸":"吉，主队有利","恒":"中，平局倾向","遁":"凶，客队有利",
    "大壮":"吉，主队有利","晋":"吉，主队有利","明夷":"凶，客队有利",
    "家人":"吉，主队有利","睽":"凶，客队有利","蹇":"凶，客队有利",
    "解":"吉，主队有利","损":"凶，客队有利","益":"吉，主队有利",
    "夬":"中，主队有利","姤":"中，平局倾向","萃":"吉，主队有利",
    "升":"吉，主队有利","困":"凶，客队有利","井":"中，平局倾向",
    "革":"中，客队有利","鼎":"吉，主队有利","震":"中，平局倾向",
    "艮":"中，平局倾向","渐":"吉，主队有利","归妹":"中，客队有利",
    "丰":"吉，主队有利","旅":"凶，客队有利","巽":"中，平局倾向",
    "兑":"吉，主队有利","涣":"凶，客队有利","节":"中，平局倾向",
    "中孚":"吉，主队有利","小过":"中，客队有利","既济":"吉，主队有利",
    "未济":"凶，客队有利","乾":"大吉，主队有利","坤":"中，平局倾向",
}
def get_gua_ji_xiong(gua):
    return GUA_JI_XIONG.get(gua, "中，常规卦象")

def wuxing_sheng_ke(wo, ta):
    sheng = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
    ke = {"金":"木","木":"土","土":"水","水":"火","火":"金"}
    if wo == ta: return 0.0
    elif sheng[wo] == ta: return -0.15
    elif ke[wo] == ta: return 0.25
    elif sheng[ta] == wo: return -0.20
    elif ke[ta] == wo: return 0.30
    else: return 0.0

# ============================================================
# 5. 起卦函数（只依赖日期）
# ============================================================
def get_team_seed(team, league, date_str):
    date_only = date_str[:5] if len(date_str) >= 5 else date_str
    raw = f"{team}_{league}_{date_only}"
    return int(hashlib.md5(raw.encode()).hexdigest(), 16) % 1000000

def auto_gua(team1, team2, league, date_str):
    seed = get_team_seed(team1, league, date_str) + get_team_seed(team2, league, date_str)
    zhu = GUA_LIST[seed % 64]
    bian = GUA_LIST[(seed // 64) % 64]
    dong = ["初爻","二爻","三爻","四爻","五爻","上爻"][seed % 6]
    return zhu, bian, dong

# ============================================================
# 6. 核心预测函数（V9.3.12 修正版）
# ============================================================
def predict_match(league, date_time, home, away):
    league_key = league.strip()
    avg = LEAGUE_AVG_TOTAL.get(league_key, 2.5)
    home_str = get_strength(home)
    away_str = get_strength(away)
    diff = home_str - away_str

    # ---- 自动识别修正标签 ----
    extra = []
    if home_str <= 2 and "05" in date_time: extra.append("保级")
    if away_str <= 2 and "05" in date_time: extra.append("保级客场")
    if home_str >= 4 and "05" in date_time: extra.append("无欲")
    if away_str >= 5 and "05" in date_time: extra.append("无欲")
    if "季后赛" in league_key: extra.append("季后赛")
    if "淘汰赛" in league_key: extra.append("淘汰赛")
    if "05" in date_time: extra.append("赛季末")

    # ---- 起卦 ----
    zhu, bian, dong = auto_gua(home, away, league_key, date_time)
    gua_ji = get_gua_ji_xiong(zhu)
    wuxing = wuxing_sheng_ke(
        GUA_LEI_XIANG.get(zhu, {"五行":"土"})["五行"],
        GUA_LEI_XIANG.get(bian, {"五行":"土"})["五行"]
    )

    # ---- 期望进球 ----
    exp = avg
    exp += diff * 0.18

    # 卦象波动（放大）
    if zhu in ["乾","离","大壮","大有","同人"]:
        exp += 0.8
    elif zhu in ["坎","艮","明夷","蹇","困"]:
        exp -= 0.6
    elif zhu in ["泰","否","咸","恒","损","益","既济","未济"]:
        exp -= 0.2
    exp += wuxing * 0.2

    # 联赛系数
    if league_key == "荷甲": exp *= 1.40
    elif league_key == "K联赛": exp *= 0.65
    elif league_key in ["日职","J联赛"]: exp *= 0.70

    # 强队客场减值（仅针对5档球队，且需在赛季末）
    if "赛季末" in extra and away_str == 5:
        exp -= 0.8

    # 沙特联/西甲强队客场额外减值
    if league_key in ["西甲","沙特联"] and away_str >= 4 and "客场" in str(extra):
        exp *= 0.75
    if league_key == "法甲" and home == "巴黎圣日耳曼": exp *= 0.85

    # 杯赛修正
    if league_key in ["欧冠","欧联","欧协联"]: exp += 0.2
    elif league_key == "解放者杯": exp -= 0.3
    elif league_key == "亚冠乙": exp -= 0.25

    # 北欧强强对话
    if league_key in ["挪超","瑞典超"] and home_str >=4 and away_str>=4:
        exp -= 0.25
    # 德甲弱队主场偷分
    if league_key == "德甲" and away_str == 5 and home_str <=3:
        exp += 0.3
    # K联赛全北主场
    if league_key == "K联赛" and home == "全北现代": exp += 0.4
    # J联赛升班马主场对强队
    if league_key in ["日职","J联赛"] and home_str <=3 and away_str >=4:
        exp += 0.3
    # 解放者杯客场强队减值
    if league_key == "解放者杯" and away_str >=4:
        exp -= 0.2
    # 荷甲保级主场
    if league_key == "荷甲" and home_str <=3 and "05" in date_time:
        exp += 0.25
    # 沙特中游主场
    if league_key == "沙特联" and home_str == 3:
        exp += 0.35
    # 澳超季后赛
    if league_key == "澳超" and "季后赛" in extra:
        exp += 0.5
    # 亚冠淘汰赛
    if league_key in ["亚冠","亚冠乙"] and "淘汰赛" in extra:
        exp -= 0.25
    # 芬超赛季末
    if league_key == "芬超" and "05" in date_time:
        exp += 0.4
    # 芬甲主场加成
    if league_key == "芬甲": exp += 0.15

    # ---- V9.3.12 新增修正 ----
    # 巴西乙主场独立系数
    if league_key == "巴西乙":
        exp += 0.18  # 独立主场加成

    exp = max(exp, 1.0)

    # ---- 比分离散化 ----
    total = exp
    home_ratio = 0.5 + diff * 0.06  # 主场系数0.06
    home_ratio = max(0.3, min(0.7, home_ratio))

    # ---- 平局溢价（仅当 diff==0 且双方无保级/无欲标签） ----
    if diff == 0 and "保级" not in extra and "无欲" not in extra:
        home_ratio = 0.5

    # 低级别弱队平局溢价
    if league_key in ["巴西乙", "芬甲", "挪甲"] and home_str <= 2 and away_str <= 2:
        home_ratio = 0.5

    home_exp = total * home_ratio
    away_exp = total * (1 - home_ratio)

    # ---- 枚举比分 + 方向奖励 ----
    candidates = []
    for h in range(6):
        for a in range(6):
            if h + a == 0: continue
            diff_score = abs(h - home_exp) + abs(a - away_exp)
            reward = 0.0
            if diff > 0 and h > a:
                reward = diff * 0.30 * (h - a)
            elif diff < 0 and h < a:
                reward = abs(diff) * 0.30 * (a - h)
            score = diff_score - reward
            candidates.append((score, h, a))
    candidates.sort(key=lambda x: x[0])
    unique = []
    for _, h, a in candidates:
        if (h,a) not in unique:
            unique.append((h,a))
        if len(unique) >= 4: break
    if len(unique) < 4:
        common = [(1,1),(2,1),(1,0),(0,1),(2,0),(0,2)]
        for s in common:
            if s not in unique:
                unique.append(s)
            if len(unique) >= 4: break
    best = unique[:4]
    first_score = best[0]
    second_score = best[1] if len(best) > 1 else first_score

    # ---- 方向判定 ----
    def res(h,a):
        if h>a: return "主胜"
        elif h<a: return "客胜"
        else: return "平局"
    first_res = res(first_score[0], first_score[1])
    second_res = res(second_score[0], second_score[1])
    if first_res == second_res and len(best)>1:
        if len(best)>2:
            second_score = best[2]
            second_res = res(second_score[0], second_score[1])
        else:
            second_res = "平局" if first_res != "平局" else "客胜"

    # ---- 置信度 ----
    if "大吉" in gua_ji or "吉" in gua_ji: gua_score = 0.9
    elif "凶" in gua_ji: gua_score = 0.5
    else: gua_score = 0.7

    if (first_res=="主胜" and diff>0) or (first_res=="客胜" and diff<0) or (first_res=="平局" and abs(diff)<=0.5):
        str_score = 0.9
    else: str_score = 0.5

    wuxing_score = 0.8 if wuxing>0 else (0.5 if wuxing<0 else 0.6)
    conf = int((gua_score*0.4 + str_score*0.35 + wuxing_score*0.25)*100)

    if home_str==5 and away_str<=2 and first_res=="主胜" and first_score[0]-first_score[1]>=2:
        conf = min(conf, 75)
    if league_key == "美职联": conf = min(conf, 45)

    # ---- 方向强制修正（保留，但平局溢价已前置处理） ----
    if league_key=="英超" and home_str<=2 and away_str>=4:
        if first_res != "平局" and second_res != "平局": second_res = "平局"
    if away_str==5 and first_res!="平局" and second_res!="平局": second_res = "平局"
    if league_key=="意甲" and home_str >= away_str+2 and first_res!="平局":
        if second_res!="平局": second_res = "平局"
    if league_key=="西甲" and home=="马德里竞技" and away_str<=4:
        if first_res=="主胜" and conf>55:
            conf -= 5
            second_res = "平局"
    if league_key=="德甲" and home_str<=3 and away_str>=4:
        if first_res=="客胜":
            first_res = "平局"
            second_res = "主胜"
    if league_key=="西甲" and "保级客场" in extra and away_str<=2:
        if first_res=="主胜":
            first_res = "平局"
            second_res = "客胜"

    return first_res, second_res, first_score, conf, zhu, bian, gua_ji

# ============================================================
# 7. Streamlit 界面（单场输入版）
# ============================================================
def main():
    st.markdown("### 请输入单场比赛信息")
    league = st.text_input("联赛", placeholder="例如：瑞典超")
    date_time = st.text_input("日期时间", placeholder="例如：07-07 01:00")
    home = st.text_input("主队", placeholder="例如：赫根")
    away = st.text_input("客队", placeholder="例如：佐加顿斯")
    if st.button("🚀 预测"):
        if not league or not date_time or not home or not away:
            st.warning("请完整填写所有字段")
            return
        first, second, score, conf, zhu, bian, gua = predict_match(league, date_time, home, away)
        st.success("预测结果")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("首推方向", first)
        col2.metric("次推方向", second)
        col3.metric("预测比分", f"{score[0]}-{score[1]}")
        col4.metric("置信度", f"{conf}%")
        st.caption(f"卦象：{zhu}→{bian}，{gua}")

if __name__ == "__main__":
    main()
