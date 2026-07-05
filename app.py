import streamlit as st
import math
import hashlib
from datetime import datetime

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻·纯卦象预测 V9.3.7", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 六爻 · 纯卦象预测引擎 V9.3.7")
st.caption("V9.3.7 最终优化：赛季末无欲强队权重、澳超/芬超大球、亚冠客场、美职方差等全面修正")

# ============================================================
# 2. 赛事列表（含所有联赛及杯赛）
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
    "巴西乙": 2.3, "阿甲": 2.3, "美职联": 2.6, "墨超": 2.4,
    "中超": 2.5, "澳超": 2.6, "沙特联": 2.5, "阿联酋超": 2.4,
    "卡塔尔联": 2.3, "女足世界杯": 2.0, "女足英超": 2.2,
    "意乙": 2.3, "亚冠": 2.4, "英足总杯": 2.6, "解放者杯": 2.3,
    "亚冠乙": 2.4,
    "国王杯": 2.4, "荷兰杯": 2.5, "德国杯": 2.6, "意大利杯": 2.4,
    "法国杯": 2.5, "足总杯": 2.6,
}

# ============================================================
# 3. 战意系数
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
# 4. 球队实力分层（V9.3.7 最终校准）
# ============================================================
TEAM_STRENGTH = {
    # 超级强队 (5档)
    "巴西": 5, "阿根廷": 5, "法国": 5, "英格兰": 5, "西班牙": 5,
    "德国": 5, "葡萄牙": 5, "比利时": 5, "荷兰": 5, "意大利": 5,
    "拜仁慕尼黑": 5, "巴黎圣日耳曼": 5, "皇家马德里": 5, "巴塞罗那": 5,
    "曼城": 5, "利物浦": 5, "阿森纳": 5, "国际米兰": 5,
    "马德里竞技": 5, "勒沃库森": 4, "多特蒙德": 4,
    "博德闪耀": 5, "本菲卡": 5,
    # 强队 (4档)
    "尤文图斯": 4, "AC米兰": 4, "那不勒斯": 4, "亚特兰大": 4,
    "莱比锡红牛": 4, "塞维利亚": 3,
    "毕尔巴鄂竞技": 4, "比利亚雷亚尔": 4, "阿斯顿维拉": 3,
    "切尔西": 3, "曼联": 4, "热刺": 4, "纽卡斯尔联": 4,
    "西汉姆联": 4, "布伦特福德": 4,
    "克罗地亚": 4, "乌拉圭": 4, "瑞士": 4, "瑞典": 4, "丹麦": 4,
    "墨西哥": 4, "美国": 4, "塞内加尔": 4, "摩洛哥": 4, "日本": 4,
    "韩国": 4, "澳大利亚": 4, "尼日利亚": 4, "哥伦比亚": 4,
    "蔚山现代": 4, "全北现代": 3,
    "浦项制铁": 4, "马尔默": 3,
    "赫尔辛基": 3,
    "莫尔德": 4, "利雅得胜利": 4, "吉达国民": 4, "吉达联合": 4,
    "水晶宫": 4, "利雅得新月": 4, "大阪钢巴": 4, "神户胜利船": 4,
    "皇家社会": 3,
    "里尔": 4, "波尔图": 4, "里斯本竞技": 4, "罗马": 4,
    "拉齐奥": 4, "佛罗伦萨": 4, "科林蒂安": 4, "帕尔梅拉斯": 4,
    "弗拉门戈": 4, "弗鲁米嫩塞": 4, "博卡青年": 4, "河床": 4,
    "弗赖堡": 4, "布拉加": 4, "诺丁汉森林": 4, "雅典AEK": 4,
    "斯特拉斯": 3,
    "霍芬海姆": 4, "奥格斯堡": 4, "洛里昂": 4, "伯恩茅斯": 4,
    "里昂": 4, "布兰": 4,
    "拉斯决心": 4,
    "新未来城": 3, "通德拉": 3, "伊普斯": 3,
    "浦和红钻": 3, "仁川联": 4, "江原FC": 4, "福冈黄蜂": 4,
    "天狼星": 4, "赫塔费": 4, "尼斯": 4, "布赖合作": 4,
    "艾禾斯堡": 3, "勒芒": 3, "阿尔梅勒": 3, "圣保利": 3,
    "克莱蒙": 3, "阿维SAD": 3, "夏洛特FC": 3, "圣何塞地震": 3,
    "安养FC": 3, "利勒斯特": 3,
    "麦克阿瑟": 3, "芬洛": 3, "不伦瑞克": 3, "阿拉维斯": 3,
    "埃尔切": 3, "莱万特": 3, "科莫": 3, "敦刻尔克": 3,
    "海登海姆": 4,
    # 中游队 (3档)
    "厄瓜多尔": 3, "巴拉圭": 3, "智利": 3, "秘鲁": 3, "土耳其": 3,
    "奥地利": 3, "苏格兰": 3, "挪威": 3, "乌克兰": 3, "伊朗": 3,
    "沙特阿拉伯": 3, "卡塔尔": 3, "阿联酋": 3, "阿尔及利亚": 3,
    "科特迪瓦": 3, "加纳": 3, "埃及": 3, "突尼斯": 3,
    "匈牙利": 3, "罗马尼亚": 3, "威尔士": 3, "希腊": 3, "黑山": 3,
    "斯洛文尼亚": 3, "塞尔维亚": 3,
    "塞尔塔": 3, "贝蒂斯": 3, "巴列卡诺": 3, "美因茨": 3,
    "水晶体育": 3, "麦德林": 3, "阿维SAD": 3,
    # 弱队 (2档)
    "新西兰": 2, "加拿大": 2, "佛得角": 2, "库拉索": 2,
    "波黑": 2, "斯洛伐克": 2, "捷克": 2, "南非": 2,
    "伊拉克": 2, "约旦": 2, "乌兹别克斯坦": 2, "巴拿马": 2,
    "海地": 2, "刚果(金)": 2, "富川FC": 2,
    "拉赫蒂": 2, "玛丽港": 2, "哈卡": 2,
    "桑德兰": 2, "利兹联": 2, "伯恩利": 2, "沃特福德": 2,
    "莱万特": 2, "西班牙人": 2, "马略卡": 2, "阿拉维斯": 2,
    "加的斯": 2, "奥维耶多": 2, "科莫": 2, "莱切": 2,
    "比萨": 2, "恩波利": 2, "赫尔城": 2, "牛津联": 2,
    "米尔沃尔": 2, "朴次茅斯": 2, "布莱克本": 2,
    "西布朗": 2, "雷克斯汉姆": 2, "斯旺西": 2, "伯明翰": 2,
    "诺维奇": 2, "考文垂": 2, "女王巡游": 2, "米堡": 2,
    "麦克阿瑟": 2, "纽卡斯托": 2, "阿德莱德联": 2, "西悉尼": 2,
    "珀斯光荣": 2, "中央海岸": 2, "布里斯班": 2, "惠灵顿凤凰": 2,
    "墨尔本胜利": 2, "奥克兰FC": 2, "悉尼FC": 2, "墨尔本城": 2,
    "清水鼓动": 2, "町田泽维亚": 2, "京都不死鸟": 2, "名古屋鲸": 2,
    "浦和红钻": 2, "鹿岛鹿角": 2, "金泉尚武": 2,
    "基多大学": 2,
}
# 确保新添加的覆盖默认值（若字典中有冲突，已在上方明确）

# ============================================================
# 5. 辅助函数
# ============================================================
def get_strength(team):
    clean_name = team.split('(')[0].strip()
    return TEAM_STRENGTH.get(clean_name, TEAM_STRENGTH.get(team, 3))

def get_strength_label(score):
    labels = {5: "超级强队", 4: "强队", 3: "中游", 2: "弱队", 1: "鱼腩"}
    return labels.get(score, "中游")

# ============================================================
# 6. 起卦函数（基于队名笔画 + Unicode 加权）
# ============================================================
def get_team_seed(team_name):
    """计算队名种子值：笔画数（模拟）+ Unicode 总和加权"""
    total = 0
    for ch in team_name:
        total += ord(ch)
    total = total * len(team_name) + len(team_name) * 31
    return total

def auto_gua_by_teams(home, away):
    """基于队名生成确定性卦象（种子 = 主队种子 + 客队种子）"""
    seed = get_team_seed(home) + get_team_seed(away)
    seed = max(seed, 1)
    zhu_index = seed % 64
    bian_index = (seed // 64) % 64
    dong_index = seed % 6
    dong_yao_list = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    dong_yao = dong_yao_list[dong_index]
    return GUA_LIST[zhu_index], GUA_LIST[bian_index], dong_yao

# ============================================================
# 7. 卦象数据（不变）
# ============================================================
GUA_LEI_XIANG = {
    "乾": {"五行": "金", "比赛": "冠军、强势方、大胜"},
    "坤": {"五行": "土", "比赛": "被动挨打、防守反击"},
    "震": {"五行": "木", "比赛": "新锐冲击、快速反击"},
    "巽": {"五行": "木", "比赛": "边路传中、定位球"},
    "坎": {"五行": "水", "比赛": "防守稳固、点球大战"},
    "离": {"五行": "火", "比赛": "核心发挥、进球大战"},
    "艮": {"五行": "土", "比赛": "防守反击、铁桶阵"},
    "兑": {"五行": "金", "比赛": "边路突破、点球决胜"}
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

GUA_LIST = [
    "乾", "坤", "屯", "蒙", "需", "讼", "师", "比", "小畜", "履", "泰", "否", "同人", "大有", "谦", "豫",
    "随", "蛊", "临", "观", "噬嗑", "贲", "剥", "复", "无妄", "大畜", "颐", "大过", "坎", "离",
    "咸", "恒", "遁", "大壮", "晋", "明夷", "家人", "睽", "蹇", "解", "损", "益", "夬", "姤",
    "萃", "升", "困", "井", "革", "鼎", "震", "艮", "渐", "归妹", "丰", "旅", "巽", "兑",
    "涣", "节", "中孚", "小过", "既济", "未济"
]
GUA_STRUCT = {
    "乾": (1, 1), "坤": (8, 8), "屯": (6, 4), "蒙": (7, 6), "需": (6, 1), "讼": (1, 6),
    "师": (6, 8), "比": (8, 6), "小畜": (5, 1), "履": (1, 2), "泰": (8, 1), "否": (1, 8),
    "同人": (1, 3), "大有": (3, 1), "谦": (7, 8), "豫": (4, 8), "随": (2, 4), "蛊": (7, 5),
    "临": (8, 2), "观": (5, 8), "噬嗑": (3, 4), "贲": (7, 3), "剥": (7, 8), "复": (4, 8),
    "无妄": (1, 4), "大畜": (7, 1), "颐": (7, 4), "大过": (2, 5), "坎": (6, 6), "离": (3, 3),
    "咸": (2, 7), "恒": (4, 5), "遁": (1, 7), "大壮": (4, 1), "晋": (3, 8), "明夷": (8, 3),
    "家人": (5, 3), "睽": (3, 2), "蹇": (7, 6), "解": (4, 6), "损": (7, 2), "益": (5, 4),
    "夬": (2, 1), "姤": (1, 5), "萃": (2, 8), "升": (5, 8), "困": (2, 6), "井": (5, 6),
    "革": (2, 3), "鼎": (3, 5), "震": (4, 4), "艮": (7, 7), "渐": (5, 7), "归妹": (4, 2),
    "丰": (4, 3), "旅": (3, 7), "巽": (5, 5), "兑": (2, 2), "涣": (5, 6), "节": (6, 2),
    "中孚": (5, 2), "小过": (4, 7), "既济": (6, 3), "未济": (3, 6)
}
GUA_WUXING_MAP = {1: "金", 2: "金", 3: "火", 4: "木", 5: "木", 6: "水", 7: "土", 8: "土"}

LIUHE_SET = {"泰", "否", "咸", "恒", "损", "益", "既济", "未济", "节", "困", "井", "革", "鼎", "震", "艮", "渐",
             "归妹", "丰", "旅", "巽", "兑", "涣", "中孚", "小过"}
GUIHUN_SET = {"大有", "需", "大畜", "随", "蛊", "同人", "晋", "归妹"}
YOUHUN_SET = {"需", "讼", "明夷", "晋", "中孚", "大过", "颐", "大壮"}
LIUCHONG_SET = {"乾", "坎", "兑", "离", "震", "巽", "艮", "坤"}

GUA_JI_XIONG = {
    "泰": "大吉，主队有利", "否": "大凶，客队有利", "谦": "大吉，主队有利",
    "豫": "吉，主队有利", "随": "吉，主队有利", "蛊": "凶，客队有利",
    "临": "吉，主队有利", "观": "中，平局倾向", "噬嗑": "中，客队有利",
    "贲": "中，主队有利", "剥": "凶，客队有利", "复": "吉，主队有利",
    "无妄": "吉，主队有利", "大畜": "吉，主队有利", "颐": "中，平局倾向",
    "大过": "凶，客队有利", "坎": "凶，客队有利", "离": "中，主队有利",
    "咸": "吉，主队有利", "恒": "中，平局倾向", "遁": "凶，客队有利",
    "大壮": "吉，主队有利", "晋": "吉，主队有利", "明夷": "凶，客队有利",
    "家人": "吉，主队有利", "睽": "凶，客队有利", "蹇": "凶，客队有利",
    "解": "吉，主队有利", "损": "凶，客队有利", "益": "吉，主队有利",
    "夬": "中，主队有利", "姤": "中，平局倾向", "萃": "吉，主队有利",
    "升": "吉，主队有利", "困": "凶，客队有利", "井": "中，平局倾向",
    "革": "中，客队有利", "鼎": "吉，主队有利", "震": "中，平局倾向",
    "艮": "中，平局倾向", "渐": "吉，主队有利", "归妹": "中，客队有利",
    "丰": "吉，主队有利", "旅": "凶，客队有利", "巽": "中，平局倾向",
    "兑": "吉，主队有利", "涣": "凶，客队有利", "节": "中，平局倾向",
    "中孚": "吉，主队有利", "小过": "中，客队有利", "既济": "吉，主队有利",
    "未济": "凶，客队有利", "乾": "大吉，主队有利", "坤": "中，平局倾向",
}

def get_gua_ji_xiong(gua):
    return GUA_JI_XIONG.get(gua, "中，常规卦象")

# ============================================================
# 8. 五行生克（V9.3.1 补全）
# ============================================================
def wuxing_sheng_ke(wo, ta):
    """返回微调系数：主生客-0.15，主克客+0.25，客生主-0.20，客克主+0.30"""
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    if wo == ta:
        return 0.0
    elif sheng[wo] == ta:   # 主生客（消耗）
        return -0.15
    elif ke[wo] == ta:       # 主克客（压制）
        return 0.25
    elif sheng[ta] == wo:   # 客生主（滋养）
        return -0.20
    elif ke[ta] == wo:       # 客克主（受迫）
        return 0.30
    else:
        return 0.0

# ============================================================
# 9. 核心预测函数（V9.3.7 全修正）
# ============================================================
def predict_match(league, date_time, home, away, zhan_yi_factor=1.0, extra_info=""):
    """
    输入：联赛，日期时间，主队，客队，战意系数（默认1.0），额外信息（如排名）
    输出：首推方向，次推方向，比分，置信度
    """
    # --- 9.1 基础数据 ---
    league_key = league.strip()
    avg_goals = LEAGUE_AVG_TOTAL.get(league_key, 2.5)
    home_strength = get_strength(home)
    away_strength = get_strength(away)
    strength_diff = home_strength - away_strength  # 正=主强

    # --- 9.2 起卦 ---
    zhu_gua, bian_gua, dong_yao = auto_gua_by_teams(home, away)
    gua_ji_xiong = get_gua_ji_xiong(zhu_gua)
    zhu_gua_wuxing = GUA_LEI_XIANG.get(zhu_gua, {"五行": "土"})["五行"]
    bian_gua_wuxing = GUA_LEI_XIANG.get(bian_gua, {"五行": "土"})["五行"]
    wuxing_effect = wuxing_sheng_ke(zhu_gua_wuxing, bian_gua_wuxing)

    # --- 9.3 三层漏斗进球期望 ---
    # 第一层：联赛基准
    expected_goals = avg_goals

    # 第二层：实力偏移 + 战意
    strength_offset = strength_diff * 0.18
    expected_goals += strength_offset
    expected_goals *= zhan_yi_factor

    # 第三层：卦象波动
    gua_bonus = 0.0
    if zhu_gua in ["乾", "离", "大壮", "大有", "同人"]:
        gua_bonus = 0.6
    elif zhu_gua in ["坎", "艮", "明夷", "蹇", "困"]:
        gua_bonus = -0.5
    elif zhu_gua in ["泰", "否", "咸", "恒", "损", "益", "既济", "未济"]:
        gua_bonus = -0.2  # 六合卦收束
    expected_goals += gua_bonus
    expected_goals += wuxing_effect * 0.2  # 微调

    # 特殊修正（执行顺序：联赛→客场减值→杯赛→卦象）
    if league_key == "荷甲":
        expected_goals *= 1.40
    elif league_key == "K联赛":
        expected_goals *= 0.65
    elif league_key in ["日职", "J联赛"]:
        expected_goals *= 0.70

    # 强队客场减值（西甲/沙特联）
    if league_key in ["西甲", "沙特联"] and away_strength >= 4 and "客场" in extra_info:
        expected_goals *= 0.75
    # 巴黎主场降权
    if league_key == "法甲" and home == "巴黎圣日耳曼":
        expected_goals *= 0.85
    # 杯赛修正
    if league_key in ["欧冠", "欧联", "欧协联"]:
        expected_goals += 0.2
    elif league_key == "解放者杯":
        expected_goals -= 0.3
    elif league_key == "亚冠乙":
        expected_goals -= 0.25

    # V9.3.2 英超保级队主场对TOP6平局溢价（方向处理）
    # V9.3.3 北欧强强对话主场-0.25
    if league_key in ["挪超", "瑞典超"] and home_strength >= 4 and away_strength >= 4:
        expected_goals -= 0.25

    # V9.3.3 澳超季后赛平局溢价（方向处理）
    # V9.3.3 德甲弱队主场偷分
    if league_key == "德甲" and away_strength == 5 and home_strength <= 3:
        expected_goals += 0.3

    # V9.3.3 超级客场平局保底（方向处理）

    # V9.3.4 全北现代主场特权
    if league_key == "K联赛" and home == "全北现代":
        expected_goals += 0.4

    # V9.3.4 J联赛升班马主场对强队
    if league_key in ["日职", "J联赛"] and home_strength <= 3 and away_strength >= 4:
        expected_goals += 0.3

    # V9.3.4 解放者杯客场强队减值
    if league_key == "解放者杯" and away_strength >= 4:
        expected_goals -= 0.2

    # V9.3.4 荷甲保级主场加成（5月）
    if league_key == "荷甲" and home_strength <= 3 and "05" in date_time:
        expected_goals += 0.25

    # V9.3.4 法甲中游对西甲跨联赛劣势
    if "跨联赛" in extra_info and league_key == "法甲" and home_strength <= 4:
        expected_goals -= 0.15

    # V9.3.4 欧冠次回合平局溢价（方向处理）

    # V9.3.5 芬超主场系数+0.30
    if league_key == "芬超" and "主场" in extra_info:
        expected_goals += 0.30

    # V9.3.5 美职主场方差预警（置信度处理）
    # V9.3.5 J联赛主场爆发冷却期
    if "上轮大胜" in extra_info and league_key in ["日职", "J联赛"]:
        expected_goals -= 0.2

    # V9.3.5 马竞主场对中游队（方向处理）
    # V9.3.5 意甲赛季末无欲强队（方向处理）
    # V9.3.5 沙特联中游主场系数+0.20
    if league_key == "沙特联" and home_strength == 3:
        expected_goals += 0.20

    # V9.3.6 西甲保级队主场加成
    if league_key == "西甲" and "保级" in extra_info and home_strength <= 2:
        expected_goals += 0.3

    # V9.3.6 西甲欧战直接对话客场加成
    if league_key == "西甲" and "欧战直接" in extra_info and away_strength >= 4:
        expected_goals += 0.1

    # V9.3.6 沙特联中游主场系数再提至+0.35
    if league_key == "沙特联" and home_strength == 3:
        expected_goals += 0.15  # 累计+0.35

    # V9.3.6 法甲保级队主场进球溢价
    if league_key == "法甲" and "保级" in extra_info and home_strength <= 3:
        expected_goals += 0.3

    # V9.3.7 澳超季后赛总进球+0.5
    if league_key == "澳超" and "季后赛" in extra_info:
        expected_goals += 0.5

    # V9.3.7 超级强队赛季末客场无欲权重
    if "无欲" in extra_info and away_strength == 5:
        expected_goals -= 0.3

    # V9.3.7 德甲弱队主场对欧战区强队（方向处理）
    # V9.3.7 法甲无欲强队主场权重-0.35
    if league_key == "法甲" and "无欲" in extra_info and home_strength >= 4:
        expected_goals -= 0.35

    # V9.3.7 西甲保级队客场保级加成
    if league_key == "西甲" and "保级客场" in extra_info and away_strength <= 2:
        expected_goals += 0.15

    # V9.3.7 亚冠淘汰赛主场系数-0.25
    if league_key in ["亚冠", "亚冠乙"] and "淘汰赛" in extra_info:
        expected_goals -= 0.25

    # V9.3.7 芬超赛季末总进球+0.4
    if league_key == "芬超" and "赛季末" in extra_info:
        expected_goals += 0.4

    # V9.3.7 意甲无欲强队主场权重-0.35
    if league_key == "意甲" and "无欲" in extra_info and home_strength >= 4:
        expected_goals -= 0.35

    # 确保非负
    expected_goals = max(expected_goals, 1.0)

    # --- 9.4 离散化为比分 ---
    total = expected_goals
    if total <= 0:
        total = 1.0
    home_ratio = 0.5 + strength_diff * 0.05
    home_ratio = max(0.3, min(0.7, home_ratio))
    home_expected = total * home_ratio
    away_expected = total * (1 - home_ratio)

    # 生成常见比分
    import random
    seed = int(home_expected * 100 + away_expected * 50) % 1000
    random.seed(seed)
    possible_scores = []
    for i in range(6):
        h = int(home_expected + random.uniform(-0.5, 0.5))
        a = int(away_expected + random.uniform(-0.5, 0.5))
        h = max(0, h)
        a = max(0, a)
        if h + a > 0:
            possible_scores.append((h, a))
    unique_scores = list(set(possible_scores))
    if len(unique_scores) < 2:
        common = [(1,1), (2,1), (1,0), (0,1), (2,0), (0,2)]
        for s in common:
            if s not in unique_scores:
                unique_scores.append(s)
                if len(unique_scores) >= 4:
                    break
    unique_scores = unique_scores[:4]

    scored_scores = []
    for (h, a) in unique_scores:
        score_expected = h + a
        diff = abs(score_expected - total)
        prob = 1.0 / (diff + 0.5)
        scored_scores.append((prob, h, a))
    scored_scores.sort(reverse=True)
    best_scores = [(h, a) for (p, h, a) in scored_scores[:4]]

    first_score = best_scores[0] if best_scores else (1, 1)
    second_score = best_scores[1] if len(best_scores) > 1 else first_score

    # --- 9.5 方向判断 ---
    def result_label(h, a):
        if h > a:
            return "主胜"
        elif h < a:
            return "客胜"
        else:
            return "平局"

    first_result = result_label(first_score[0], first_score[1])
    second_result = result_label(second_score[0], second_score[1])
    if first_result == second_result and len(best_scores) > 1:
        if len(best_scores) > 2:
            second_score = best_scores[2]
            second_result = result_label(second_score[0], second_score[1])
        else:
            if first_result == "主胜":
                second_result = "平局"
            elif first_result == "客胜":
                second_result = "平局"
            else:
                second_result = "主胜"

    # --- 9.6 置信度计算（三因子） ---
    if "大吉" in gua_ji_xiong or "吉" in gua_ji_xiong:
        gua_score = 0.9
    elif "凶" in gua_ji_xiong:
        gua_score = 0.5
    else:
        gua_score = 0.7

    if (first_result == "主胜" and strength_diff > 0) or (first_result == "客胜" and strength_diff < 0) or (first_result == "平局" and abs(strength_diff) <= 0.5):
        strength_score = 0.9
    elif (first_result == "主胜" and strength_diff <= -1) or (first_result == "客胜" and strength_diff >= 1):
        strength_score = 0.4
    else:
        strength_score = 0.7

    if wuxing_effect > 0:
        wuxing_score = 0.8
    elif wuxing_effect < 0:
        wuxing_score = 0.5
    else:
        wuxing_score = 0.6

    confidence = gua_score * 0.4 + strength_score * 0.35 + wuxing_score * 0.25

    # 超级大胜封顶
    if home_strength == 5 and away_strength <= 2 and first_result == "主胜" and first_score[0] - first_score[1] >= 2:
        confidence = min(confidence, 0.75)
    # 美职主场方差
    if league_key == "美职联" and abs(home_strength - away_strength) >= 2:
        confidence = min(confidence, 0.55)
    # V9.3.7 美职置信度再降
    if league_key == "美职联":
        confidence = min(confidence, 0.45)

    confidence = int(confidence * 100)
    if confidence > 100:
        confidence = 100

    # --- 9.7 方向概率修正（基于规则） ---
    # 英超保级主场对TOP6平局溢价
    if league_key == "英超" and home_strength <= 2 and away_strength >= 4:
        if first_result != "平局" and second_result != "平局":
            second_result = "平局"
    # 超级客场平局保底
    if away_strength == 5 and first_result != "平局" and second_result != "平局":
        second_result = "平局"
    # 意甲虐菜强制平局
    if league_key == "意甲" and home_strength >= away_strength + 2 and first_result != "平局":
        if second_result != "平局":
            second_result = "平局"
    # 马竞主场对中游
    if league_key == "西甲" and home == "马德里竞技" and away_strength <= 4:
        if first_result == "主胜" and confidence > 55:
            confidence -= 5
            second_result = "平局"
    # 德甲弱队主场对欧战区强队
    if league_key == "德甲" and home_strength <= 3 and away_strength >= 4:
        if first_result == "客胜":
            first_result = "平局"
            second_result = "主胜"
    # 西甲保级队客场保级加成
    if league_key == "西甲" and away_strength <= 2 and "保级客场" in extra_info:
        if first_result == "主胜":
            first_result = "平局"
            second_result = "客胜"

    return first_result, second_result, first_score, confidence, zhu_gua, bian_gua, gua_ji_xiong

# ============================================================
# 10. Streamlit 界面
# ============================================================
def main():
    st.markdown("""
    **使用说明**：  
    输入比赛信息（联赛，日期时间，主队 vs 客队），每行一场。  
    例如：`欧冠，05-02 03:00，巴黎圣曼 vs 拜仁`
    """)
    user_input = st.text_area("📝 粘贴比赛列表", height=300)
    if st.button("🚀 预测"):
        if not user_input.strip():
            st.warning("请至少输入一场比赛")
            return
        lines = user_input.strip().split('\n')
        results = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split('，')
            if len(parts) < 3:
                st.error(f"格式错误：{line}，请用中文逗号分隔")
                continue
            league = parts[0].strip()
            date_time = parts[1].strip()
            teams = parts[2].split(' vs ')
            if len(teams) != 2:
                st.error(f"球队格式错误：{line}，请使用 ' vs ' 分隔")
                continue
            home = teams[0].strip()
            away = teams[1].strip()
            # 简单判断战意（可根据需要扩展）
            zhan_yi = 1.0
            extra = ""
            if "决赛" in league or "杯" in league:
                zhan_yi = 1.2
            if "保级" in line.lower():
                extra += "保级 "
            if "季后赛" in league:
                extra += "季后赛 "
            if "淘汰赛" in league:
                extra += "淘汰赛 "
            # 其他extra逻辑可增加

            first, second, score, conf, zhu, bian, gua = predict_match(league, date_time, home, away, zhan_yi, extra)
            results.append({
                "league": league,
                "date": date_time,
                "home": home,
                "away": away,
                "first": first,
                "second": second,
                "score": f"{score[0]}-{score[1]}",
                "conf": conf,
                "zhu_gua": zhu,
                "bian_gua": bian,
                "gua_ji": gua
            })

        # 显示结果
        for r in results:
            st.markdown(f"**{r['league']} {r['date']} {r['home']} vs {r['away']}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("首推", r['first'])
            col2.metric("次推", r['second'])
            col3.metric("比分", r['score'])
            col4.metric("置信度", f"{r['conf']}%")
            st.caption(f"卦象：{r['zhu_gua']}→{r['bian_gua']}，{r['gua_ji']}")
            st.divider()

if __name__ == "__main__":
    main()
