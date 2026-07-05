import streamlit as st
import math
import hashlib
from datetime import datetime

# ============================================================
# 1. 页面配置
# ============================================================
st.set_page_config(page_title="⚽ 六爻·纯卦象预测 V8.7", layout="centered", initial_sidebar_state="collapsed")
st.title("⚽ 六爻 · 纯卦象预测引擎 V8.7")
st.caption("V8.7最终优化：欧战主场-25% | K联赛主场-18% | 挪超平局+15% | 解放者杯客场修正")

# ============================================================
# 2. 赛事列表
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
# 4. 球队实力分层（V8.7校准）
# ============================================================
TEAM_STRENGTH = {
    # 超级强队 (5档)
    "巴西": 5, "阿根廷": 5, "法国": 5, "英格兰": 5, "西班牙": 5,
    "德国": 5, "葡萄牙": 5, "比利时": 5, "荷兰": 5, "意大利": 5,
    "拜仁慕尼黑": 5, "巴黎圣日耳曼": 5, "皇家马德里": 5, "巴塞罗那": 5,
    "曼城": 5, "利物浦": 5, "阿森纳": 5, "国际米兰": 5,
    "马德里竞技": 5, "勒沃库森": 5, "多特蒙德": 5,
    "博德闪耀": 5,
    # 强队 (4档)
    "尤文图斯": 4, "AC米兰": 4, "那不勒斯": 4, "亚特兰大": 4,
    "莱比锡红牛": 4, "塞维利亚": 4, "毕尔巴鄂竞技": 4,
    "比利亚雷亚尔": 4, "阿斯顿维拉": 4, "切尔西": 4, "曼联": 4,
    "热刺": 4, "纽卡斯尔联": 4, "西汉姆联": 4, "布伦特福德": 4,
    "克罗地亚": 4, "乌拉圭": 4, "瑞士": 4, "瑞典": 4, "丹麦": 4,
    "墨西哥": 4, "美国": 4, "塞内加尔": 4, "摩洛哥": 4, "日本": 4,
    "韩国": 4, "澳大利亚": 4, "尼日利亚": 4, "哥伦比亚": 4,
    "蔚山现代": 4, "全北现代": 4, "浦项制铁": 4,
    "马尔默": 4, "赫尔辛基": 4, "莫尔德": 4,
    "利雅得胜利": 4, "吉达国民": 4, "吉达联合": 4, "水晶宫": 4,
    "利雅得新月": 4, "大阪钢巴": 4, "神户胜利船": 4,
    "皇家社会": 4, "里尔": 4, "波尔图": 4, "本菲卡": 4,
    "里斯本竞技": 4, "罗马": 4, "拉齐奥": 4, "佛罗伦萨": 4,
    "科林蒂安": 4, "帕尔梅拉斯": 4, "弗拉门戈": 4, "弗鲁米嫩塞": 4,
    "博卡青年": 4, "河床": 4,
    # 中游队 (3档)
    "厄瓜多尔": 3, "巴拉圭": 3, "智利": 3, "秘鲁": 3, "土耳其": 3,
    "奥地利": 3, "苏格兰": 3, "挪威": 3, "乌克兰": 3, "伊朗": 3,
    "沙特阿拉伯": 3, "卡塔尔": 3, "阿联酋": 3, "阿尔及利亚": 3,
    "科特迪瓦": 3, "加纳": 3, "埃及": 3, "突尼斯": 3,
    "匈牙利": 3, "罗马尼亚": 3, "威尔士": 3, "希腊": 3, "黑山": 3,
    "斯洛文尼亚": 3, "塞尔维亚": 3,
    "弗赖堡": 3, "布拉加": 3, "法兰克福": 3, "科隆": 3,
    "巴列卡诺": 3, "阿尔克马尔": 3,
    "首尔FC": 3, "江原FC": 3, "光州FC": 3, "釜山偶像": 3,
    "大田市民": 3, "水原三星": 3, "仁川联": 3,
    "韦斯特罗斯": 3, "天狼星": 3, "哥德堡": 3, "AIK索尔纳": 3,
    "布兰": 3, "特罗姆瑟": 3, "奥卢": 3, "瓦萨": 3, "萨普斯堡": 3,
    "哈尔姆斯塔德": 3, "卡尔马": 3, "埃尔夫斯堡": 3, "赫根": 3,
    "佐加顿斯": 3, "索尔纳": 3, "哈马比": 3,
    "瓦勒伦加": 3, "维京": 3, "利勒斯特": 3, "奥勒松": 3,
    "沙尔克": 3, "汉诺威": 3, "卡尔斯鲁厄": 3, "杜塞尔多夫": 3,
    "特温特": 3, "乌德勒支": 3, "阿尔克马": 3, "前进之鹰": 3,
    "伯恩茅斯": 3, "富勒姆": 3, "狼队": 3, "埃弗顿": 3,
    "奥萨苏纳": 3, "赫塔费": 3, "巴伦西亚": 3, "埃尔切": 3,
    "蒙彼利埃": 3, "兰斯": 3, "巴黎FC": 3,
    "克雷莫纳": 3, "博洛尼亚": 3, "都灵": 3, "热那亚": 3,
    "卡利亚里": 3, "萨索洛": 3, "乌迪内斯": 3, "帕尔马": 3,
    "维罗纳": 3,
    "水晶体育": 3, "麦德林": 3, "圣菲独立": 3, "门多萨独立": 3,
    "瓜亚基尔": 3, "迈拉索尔": 3, "基多大学": 3,
    # 弱队 (2档)
    "新西兰": 2, "加拿大": 2, "佛得角": 2, "库拉索": 2,
    "波黑": 2, "斯洛伐克": 2, "捷克": 2, "南非": 2,
    "伊拉克": 2, "约旦": 2, "乌兹别克斯坦": 2, "巴拿马": 2,
    "海地": 2, "刚果(金)": 2, "安养FC": 2, "富川FC": 2,
    "拉赫蒂": 2, "玛丽港": 2, "哈卡": 2,
    "桑德兰": 2, "利兹联": 2, "伯恩利": 2, "沃特福德": 2,
    "莱万特": 2, "西班牙人": 2, "马略卡": 2, "阿拉维斯": 2,
    "加的斯": 2, "奥维耶多": 2,
    "科莫": 2, "莱切": 2, "比萨": 2, "恩波利": 2,
    "赫尔城": 2, "牛津联": 2, "米尔沃尔": 2, "朴次茅斯": 2,
    "伊普斯": 2, "布莱克本": 2, "西布朗": 2, "雷克斯汉姆": 2,
    "斯旺西": 2, "伯明翰": 2, "诺维奇": 2, "考文垂": 2,
    "赫尔城": 2, "女王巡游": 2, "米堡": 2,
    "麦克阿瑟": 2, "纽卡斯托": 2, "阿德莱德联": 2, "西悉尼": 2,
    "珀斯光荣": 2, "中央海岸": 2, "布里斯班": 2, "惠灵顿凤凰": 2,
    "墨尔本胜利": 2, "奥克兰FC": 2, "悉尼FC": 2, "墨尔本城": 2,
    "清水鼓动": 2, "町田泽维亚": 2, "京都不死鸟": 2, "名古屋鲸": 2,
    "浦和红钻": 2, "鹿岛鹿角": 2,
    "金泉尚武": 2, "安养FC": 2,
}

def get_strength(team):
    clean_name = team.split('(')[0].strip()
    return TEAM_STRENGTH.get(clean_name, TEAM_STRENGTH.get(team, 3))

def get_strength_label(score):
    labels = {5: "超级强队", 4: "强队", 3: "中游", 2: "弱队", 1: "鱼腩"}
    return labels.get(score, "中游")

# ============================================================
# 5. 卦象数据
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

# ============================================================
# 6. 卦象数据结构
# ============================================================
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

# ============================================================
# 7. 卦名吉凶评级
# ============================================================
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
# 8. 自动起卦函数
# ============================================================
def auto_gua_by_teams(home, away):
    combined = f"{home}_{away}"
    hash_obj = hashlib.md5(combined.encode())
    hex_digest = hash_obj.hexdigest()
    seed = int(hex_digest[:8], 16)
    zhu_index = seed % 64
    bian_index = (seed // 64) % 64
    dong_index = seed % 6
    dong_yao_list = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    dong_yao = dong_yao_list[dong_index]
    return GUA_LIST[zhu_index], GUA_LIST[bian_index], dong_yao

# ============================================================
# 9. 五行生克
# ============================================================
def wuxing_sheng_ke(wo, ta):
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    if wo == ta:
        return 0
    elif sheng[wo] == ta:
        return 1
    elif ke[wo] == ta:
        return -1
    elif sheng[ta] == wo:
        return -2
    elif ke[ta] == wo:
        return 2
    else:
        return 0

# ============================================================
# 10. 六爻逐爻详解
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
                "初爻": "动于初爻：开局或有变数，从低位起步。",
                "二爻": "动于二爻：球队内部或有调整，中场控制关键。",
                "三爻": "动于三爻：走势在中段发生变化。",
                "四爻": "动于四爻：边路或替补可能成为奇兵。",
                "五爻": "动于五爻：核心球员或关键判罚影响全局。",
                "上爻": "动于上爻：尾声或有绝杀/绝平。"
            }
            desc = dong_detail.get(yname, "动爻需结合全卦。")
        else:
            static_detail = {
                "初爻": "静于初爻：基础稳定，开局稳健。",
                "二爻": "静于二爻：内部稳定，心态平和。",
                "三爻": "静于三爻：中段僵持。",
                "四爻": "静于四爻：边路稳定。",
                "五爻": "静于五爻：中枢稳固，核心正常发挥。",
                "上爻": "静于上爻：结局平稳。"
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
# 11. 五维推演 + 实力修正 + 联赛专属修正（V8.7最终版）
# ============================================================
def five_dimension_analysis(zhu_gua, bian_gua, dong_yao, home_team, away_team,
                            league, match_time=None, zhan_yi=1.0):
    score = 0.0
    details = []
    scores_detail = {}

    ti_ke_result = None
    is_liuhe = False

    # 维度1：体用生克（权重30%）
    if dong_yao == "无动爻":
        details.append("体用生克：无动爻，体用比和，主客均衡")
        scores_detail["体用生克"] = 0
        ti_ke_result = "比和"
    else:
        dong_idx = {"初爻": 0, "二爻": 1, "三爻": 2, "四爻": 3, "五爻": 4, "上爻": 5}[dong_yao]
        shang, xia = GUA_STRUCT[zhu_gua]
        shang_wu = GUA_WUXING_MAP[shang]
        xia_wu = GUA_WUXING_MAP[xia]
        if dong_idx < 3:
            ti_wu, yong_wu = shang_wu, xia_wu
            detail_add = "（下卦为用，上卦为体）"
        else:
            ti_wu, yong_wu = xia_wu, shang_wu
            detail_add = "（上卦为用，下卦为体）"
        rel = wuxing_sheng_ke(ti_wu, yong_wu)
        if rel == -2:
            score += 0.30
            details.append(f"体用生克：用生体，客生主，主队得利 {detail_add}")
            scores_detail["体用生克"] = 0.30
            ti_ke_result = "用生体"
        elif rel == 2:
            score -= 0.30
            details.append(f"体用生克：用克体，客克主，客队占优 {detail_add}")
            scores_detail["体用生克"] = -0.30
            ti_ke_result = "用克体"
        elif rel == 1:
            score -= 0.15
            details.append(f"体用生克：体生用，主生客，主队消耗大，客队不败 {detail_add}")
            scores_detail["体用生克"] = -0.15
            ti_ke_result = "体生用"
        elif rel == -1:
            score += 0.20
            details.append(f"体用生克：体克用，主克客，主队胜机更大 {detail_add}")
            scores_detail["体用生克"] = 0.20
            ti_ke_result = "体克用"
        else:
            details.append(f"体用生克：比和，主客均衡 {detail_add}")
            scores_detail["体用生克"] = 0
            ti_ke_result = "比和"

    # 维度2：卦象属性（权重25%）
    attr_score = 0
    attr_detail = []

    if zhu_gua in LIUHE_SET:
        is_liuhe = True
        if ti_ke_result in ["体生用", "用克体"]:
            attr_score += 0.08
            attr_detail.append("六合卦（体生用/用克体→加成减半）")
        else:
            attr_score += 0.15
            attr_detail.append("六合卦→平局倾向高")

    if bian_gua in LIUHE_SET:
        attr_score += 0.08
        attr_detail.append("变卦六合→趋平")
    if zhu_gua in LIUCHONG_SET:
        attr_score -= 0.20
        attr_detail.append("六冲卦→分胜负")
    if zhu_gua in GUIHUN_SET:
        attr_score += 0.08
        attr_detail.append("归魂卦→胶着反复")
    if zhu_gua in YOUHUN_SET:
        attr_score -= 0.15
        attr_detail.append("游魂卦→客不败")
    if zhu_gua == "明夷" or bian_gua == "明夷":
        attr_score -= 0.10
        attr_detail.append("明夷卦→客队有利")

    score += attr_score * 0.8
    details.append(f"卦象属性：{attr_detail[0] if attr_detail else '常规卦象'}")
    scores_detail["卦象属性"] = attr_score

    # 维度3：动爻位置（权重20%）
    dong_score = 0
    if dong_yao == "无动爻":
        details.append("动爻位置：无动爻，局势稳定")
    else:
        yao_effect = {"初爻": 0.1, "二爻": 0.05, "三爻": 0, "四爻": -0.05, "五爻": -0.1, "上爻": -0.15}
        dong_score = yao_effect.get(dong_yao, 0)
        yao_desc = {"初爻": "开局定势", "二爻": "内部调整", "三爻": "中段转折",
                    "四爻": "替补变量", "五爻": "核心关键", "上爻": "终局之变"}
        details.append(f"动爻位置：{yao_desc.get(dong_yao, '')}")
    score += dong_score * 0.4
    scores_detail["动爻位置"] = dong_score

    # 维度4：卦气旺衰（权重15%）
    if match_time:
        month = match_time.month
    else:
        month = datetime.now().month
    if month in [1, 2]:
        month_wuxing = "木"
    elif month in [4, 5]:
        month_wuxing = "火"
    elif month in [7, 8]:
        month_wuxing = "金"
    elif month in [10, 11]:
        month_wuxing = "水"
    else:
        month_wuxing = "土"

    shang, xia = GUA_STRUCT[zhu_gua]
    gua_wuxing = GUA_WUXING_MAP[shang]
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    qi_score = 0
    if month_wuxing == gua_wuxing:
        qi_score = 0.05
        details.append(f"卦气旺衰：卦气与月建同五行")
    elif sheng.get(month_wuxing) == gua_wuxing:
        qi_score = 0.10
        details.append(f"卦气旺衰：月建生卦气，主队得势")
    elif ke.get(month_wuxing) == gua_wuxing:
        qi_score = -0.10
        details.append(f"卦气旺衰：月建克卦气，主队受压")
    else:
        details.append(f"卦气旺衰：月建与卦气无生克")
    score += qi_score * 0.5
    scores_detail["卦气旺衰"] = qi_score

    # 维度5：卦名吉凶（权重10%）
    ji_xiong = get_gua_ji_xiong(zhu_gua)
    jx_score = 0
    if "大吉" in ji_xiong or "吉" in ji_xiong:
        jx_score = 0.15
    elif "大凶" in ji_xiong or "凶" in ji_xiong:
        jx_score = -0.15
    else:
        jx_score = 0
    score += jx_score * 0.3
    details.append(f"卦名吉凶：{ji_xiong}")
    scores_detail["卦名吉凶"] = jx_score

    # ============================================================
    # V8.7：实力修正 + 联赛专属修正
    # ============================================================
    strength_h = get_strength(home_team)
    strength_a = get_strength(away_team)
    strength_h_label = get_strength_label(strength_h)
    strength_a_label = get_strength_label(strength_a)

    details.append(f"实力对比：主队{strength_h_label}({strength_h}) vs 客队{strength_a_label}({strength_a})")

    correction = 0
    correction_reason = ""

    # 实力修正
    if strength_a - strength_h >= 2:
        correction = -0.40
        correction_reason = "客队实力强2档以上→卦象向客队修正"
    elif strength_a - strength_h >= 1:
        correction = -0.20
        correction_reason = "客队实力强1档→温和修正"
    elif strength_h - strength_a >= 2:
        correction = 0.30
        correction_reason = "主队实力强2档以上→向主队修正"
    elif strength_h - strength_a >= 1:
        correction = 0.15
        correction_reason = "主队实力强1档→温和修正"
    else:
        details.append("实力修正：双方实力接近，无需修正")

    if abs(correction) > 0.1:
        details.append(f"实力修正：{correction_reason}")

    # 特殊规则：用生体+客强 → 反转
    if ti_ke_result == "用生体" and strength_a - strength_h >= 1:
        score = -0.20
        details.append("特殊修正：用生体+客队更强 → 反转为主队消耗，客队有利")
        ti_ke_result_modified = "体生用(客强修正)"
    else:
        ti_ke_result_modified = ti_ke_result

    # ============================================================
    # V8.7：联赛专属修正
    # ============================================================
    event_correction = 0
    home_advantage_mod = 1.0

    # --- 国际友谊赛 ---
    if league == "国际友谊赛":
        event_correction = 0.15
        home_advantage_mod = 1.20
        if strength_h - strength_a >= 2:
            correction = correction * 0.7
        details.append("国际友谊赛(+0.15平局，强队优势打折)")

    # --- K联赛（V8.7：主场优势进一步减弱）---
    elif league == "K联赛":
        event_correction = 0.15
        home_advantage_mod = 0.75  # 原0.82
        details.append("K联赛(+0.15平局，主场优势进一步减弱)")

    # --- 英冠 ---
    elif league == "英冠":
        event_correction = 0.12
        details.append("英冠(+0.12平局)")

    # --- 英超 ---
    elif league == "英超":
        event_correction = 0.08
        if 3 <= strength_h <= 4 and strength_a >= strength_h:
            home_advantage_mod = 1.20
            details.append("英超中游球队主场优势增强")
        if strength_h >= 4 and strength_a >= 4:
            event_correction = 0.15
        details.append(f"英超(+{event_correction:.2f}平局)")

    # --- 西甲 ---
    elif league == "西甲":
        event_correction = 0.05
        home_advantage_mod = 1.30
        if strength_h <= 3 and strength_a >= 5:
            if away_team in ["皇家马德里", "巴塞罗那"]:
                score = score * 0.75
                details.append("西甲超级强队客场修正：爆冷风险增加")
        details.append("西甲(主场优势大幅增强)")

    # --- 德甲 ---
    elif league == "德甲":
        event_correction = 0.05
        home_advantage_mod = 1.10
        if strength_h <= 3 and strength_a >= 5:
            if away_team in ["拜仁慕尼黑", "多特蒙德", "勒沃库森"]:
                score = score * 0.85
                details.append("德甲超级强队客场修正")
        details.append("德甲(主场优势增强)")

    # --- 意甲 ---
    elif league == "意甲":
        event_correction = 0.08
        home_advantage_mod = 1.10
        details.append("意甲(+0.08平局)")

    # --- 法甲 ---
    elif league == "法甲":
        event_correction = 0.05
        home_advantage_mod = 1.10
        details.append("法甲(主场优势增强)")

    # --- 荷甲 ---
    elif league == "荷甲":
        event_correction = 0.05
        home_advantage_mod = 1.10
        details.append("荷甲(主场优势增强)")

    # --- 荷乙 ---
    elif league == "荷乙":
        event_correction = 0.15
        details.append("荷乙(+0.15平局)")

    # --- 葡超 ---
    elif league == "葡超":
        home_advantage_mod = 0.95
        details.append("葡超(主场优势减弱)")

    # --- 法乙 ---
    elif league == "法乙":
        event_correction = 0.15
        details.append("法乙(+0.15平局)")

    # --- 澳超 ---
    elif league == "澳超":
        event_correction = 0.10
        details.append("澳超(+0.10平局)")

    # --- 挪超（V8.7：平局权重提升，主场优势减弱）---
    elif league == "挪超":
        event_correction = 0.15  # 原0.08
        home_advantage_mod = 0.85  # 原0.90
        details.append("挪超(+0.15平局，主场优势减弱)")

    # --- 瑞典超 ---
    elif league == "瑞典超":
        event_correction = 0.08
        details.append("瑞典超(+0.08平局)")

    # --- 芬超 ---
    elif league == "芬超":
        event_correction = -0.05
        home_advantage_mod = 1.35
        details.append("芬超(主场优势大幅增强)")

    # --- 亚冠/亚冠乙 ---
    elif league in ["亚冠", "亚冠乙"]:
        event_correction = 0.12
        details.append("亚冠(+0.12平局，冷门风险高)")

    # --- 沙特联（V8.7：平局权重提升）---
    elif league == "沙特联":
        event_correction = 0.12
        details.append("沙特联(+0.12平局)")

    # --- 解放者杯（V8.7：主场优势增强，客场强队修正）---
    elif league == "解放者杯":
        event_correction = 0.10
        home_advantage_mod = 1.25
        if strength_a - strength_h >= 2:
            correction = correction * 0.6
            details.append("解放者杯客场强队修正：客场难度大")
        details.append("解放者杯(主场优势增强)")

    # --- 欧冠淘汰赛（V8.7：主场优势下调）---
    elif league == "欧冠" and zhan_yi >= 1.2:
        event_correction = 0.12
        home_advantage_mod = 1.10  # 原1.30
        details.append("欧冠淘汰赛(主场优势减弱，客场强队需重视)")

    # --- 欧联/欧协联淘汰赛（V8.7：主场优势大幅下调）---
    elif league in ["欧联", "欧协联"] and zhan_yi >= 1.2:
        home_advantage_mod = 1.05  # 原1.30
        event_correction = 0.15
        details.append("欧联/欧协联淘汰赛(主场优势大幅减弱，客场强队更可靠)")

    # --- 世界杯淘汰赛 ---
    elif league == "世界杯" and zhan_yi >= 1.2:
        event_correction += 0.10
        details.append("世界杯淘汰赛(+0.10平局)")

    # 应用赛事属性修正
    score = score - event_correction * 0.3

    # ============================================================
    # V8.7：淘汰赛预警
    # ============================================================
    penalty_warning = ""
    is_knockout = zhan_yi >= 1.2 and league in ["欧冠", "欧联", "欧协联", "世界杯", "亚冠"]
    if is_knockout and abs(strength_h - strength_a) <= 1 and is_liuhe:
        penalty_warning = "⚠️ 淘汰赛+实力接近+六合卦 → 90分钟平局概率高，需防范加时/点球！"

    # ============================================================
    # 综合判断
    # ============================================================
    abs_score = abs(score)
    if abs_score > 0.3:
        ping_ju_base = 0.25
    elif abs_score > 0.15:
        ping_ju_base = 0.35
    elif abs_score > 0.05:
        ping_ju_base = 0.45
    else:
        ping_ju_base = 0.55

    liuhe_bonus = 0.0
    if is_liuhe:
        if ti_ke_result in ["体生用", "用克体"]:
            liuhe_bonus = 0.10
        else:
            liuhe_bonus = 0.20
    elif bian_gua in LIUHE_SET:
        liuhe_bonus = 0.08

    # 赛事属性修正平局倾向
    if league == "国际友谊赛":
        liuhe_bonus += 0.15
    if league in ["K联赛", "英冠", "荷乙", "法乙", "亚冠", "亚冠乙", "沙特联"]:
        liuhe_bonus += 0.12
    if league == "挪超":
        liuhe_bonus += 0.15
    if league == "英超" and strength_h >= 4 and strength_a >= 4:
        liuhe_bonus += 0.15
    if league in ["欧联", "欧协联"] and zhan_yi >= 1.2:
        liuhe_bonus += 0.15
    if is_knockout and abs(strength_h - strength_a) <= 1:
        liuhe_bonus += 0.10

    ping_ju_tend = min(ping_ju_base + liuhe_bonus, 0.92)
    ping_ju_tend = max(0.10, ping_ju_tend)

    # 首推判断
    # 联赛主场优势修正
    if home_advantage_mod != 1.0 and score < 0.15 and score > -0.15:
        if home_advantage_mod > 1.0:
            score += 0.10
        else:
            score -= 0.10

    if ti_ke_result_modified in ["用克体", "体生用(客强修正)"]:
        first = "客胜"
        second = "平局"
    elif ti_ke_result_modified in ["体克用", "用生体(主强修正)"]:
        first = "主胜"
        second = "平局"
    elif ti_ke_result_modified == "用生体":
        if strength_h - strength_a >= 1:
            first = "主胜"
            second = "平局"
        else:
            first = "平局"
            second = "客胜"
    elif ti_ke_result_modified == "体生用":
        first = "客胜"
        second = "平局"
    else:
        if ping_ju_tend > 0.55:
            first = "平局"
            second = "主胜" if score > 0 else "客胜"
        elif score > 0:
            first = "主胜"
            second = "平局" if ping_ju_tend > 0.4 else "客胜"
        else:
            first = "客胜"
            second = "平局" if ping_ju_tend > 0.4 else "主胜"

    # 比分参考
    if first == "平局":
        score_hint = "0-0 / 1-1"
    elif first == "主胜":
        if strength_h - strength_a >= 2:
            score_hint = "3-0 / 2-0"
        else:
            score_hint = "2-1 / 1-0"
    else:
        if strength_a - strength_h >= 2:
            score_hint = "0-3 / 0-2"
        else:
            score_hint = "0-1 / 1-2"

    # 置信度
    strength_gap = abs(strength_h - strength_a)
    if strength_gap >= 2 and abs(score) > 0.2:
        confidence = "高"
        conf_detail = "实力差距+卦象双重确认"
    elif strength_gap >= 1 or abs(score) > 0.3:
        confidence = "中高"
        conf_detail = "实力或卦象单方面确认"
    elif abs(score) > 0.15:
        confidence = "中等"
        conf_detail = "卦象略占优势"
    else:
        confidence = "低"
        conf_detail = "卦象胶着，建议观望"

    return {
        "first": first,
        "second": second,
        "score": round(score, 2),
        "score_original": round(score_original, 2),
        "correction": round(correction, 2),
        "correction_reason": correction_reason,
        "ping_ju_tend": round(ping_ju_tend, 2),
        "details": details,
        "scores_detail": scores_detail,
        "month_wuxing": month_wuxing,
        "gua_wuxing": gua_wuxing,
        "ji_xiong": ji_xiong,
        "ti_ke_result": ti_ke_result,
        "ti_ke_result_modified": ti_ke_result_modified,
        "is_liuhe": is_liuhe,
        "liuhe_bonus": liuhe_bonus,
        "strength_h": strength_h,
        "strength_a": strength_a,
        "strength_h_label": strength_h_label,
        "strength_a_label": strength_a_label,
        "score_hint": score_hint,
        "confidence": confidence,
        "conf_detail": conf_detail,
        "event_correction": event_correction,
        "penalty_warning": penalty_warning,
        "league": league,
        "is_knockout": is_knockout,
        "home_advantage_mod": home_advantage_mod
    }


# ============================================================
# 12. 自动解卦函数
# ============================================================
def auto_jie_gua(zhu_gua, bian_gua, dong_yao):
    gua_analysis = []
    if zhu_gua in LIUHE_SET:
        gua_analysis.append("六合卦：平局倾向高")
    if zhu_gua in GUIHUN_SET:
        gua_analysis.append("归魂卦：胶着反复")
    if zhu_gua in YOUHUN_SET:
        gua_analysis.append("游魂卦：客不败")
    if zhu_gua in LIUCHONG_SET:
        gua_analysis.append("六冲卦：分胜负")
    if bian_gua in LIUHE_SET:
        gua_analysis.append("变卦六合：趋平")
    if bian_gua == "明夷" or zhu_gua == "明夷":
        gua_analysis.append("明夷卦：客队有利")
    zhu_style = get_gua_style(zhu_gua)
    bian_style = get_gua_style(bian_gua)
    gua_analysis.append(f"主卦风格：{zhu_style}")
    gua_analysis.append(f"变卦风格：{bian_style}")
    yao_details = analyze_yaos(zhu_gua, bian_gua, dong_yao)
    return {
        "analysis": " | ".join(gua_analysis) if gua_analysis else "常规卦象",
        "yao_details": yao_details
    }


# ============================================================
# 13. 界面布局
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
        home_team = st.text_input("主队名", placeholder="请输入主队名", value="")
        league = st.selectbox("请选择赛事", list(LEAGUE_AVG_TOTAL.keys()))
    with col2:
        away_team = st.text_input("客队名", placeholder="请输入客队名", value="")
        match_time = st.datetime_input("比赛时间", value=datetime.now())

zhan_yi_opt = st.selectbox("⚔️ 战意系数", ZHAN_YI_LIST, format_func=lambda x: x[0])
zhan_yi = zhan_yi_opt[1]

# ============================================================
# 14. 预测按钮
# ============================================================
if st.button("🚀 纯卦象预测 V8.7", type="primary", use_container_width=True):
    if not home_team.strip() or not away_team.strip():
        st.warning("⚠️ 请输入主队名和客队名！")
    else:
        zhu, bian, dong = auto_gua_by_teams(home_team, away_team)
        st.session_state.zhu_gua = zhu
        st.session_state.bian_gua = bian
        st.session_state.dong_yao = dong

        five_dim = five_dimension_analysis(zhu, bian, dong, home_team, away_team,
                                           league, match_time, zhan_yi)

        liu_factors = auto_jie_gua(zhu, bian, dong)
        st.session_state.liu_result = liu_factors

        zhan_yi_name = zhan_yi_opt[0]
        s = five_dim['scores_detail']
        time_str = match_time.strftime("%Y-%m-%d %H:%M") if match_time else "未设置"

        st.markdown("---")
        st.markdown(f"### 📊 {home_team} vs {away_team}")
        st.caption(f"{league} | {time_str} | {zhan_yi_name}")
        st.caption(f"实力评级：主队{five_dim['strength_h_label']}({five_dim['strength_h']}) vs 客队{five_dim['strength_a_label']}({five_dim['strength_a']})")

        st.markdown("---")
        st.markdown("### ✅ 推演结果如下")
        st.markdown("")

        st.markdown(f"**首推：{five_dim['first']}**" + (" ⭐" if five_dim['first'] in ["主胜", "客胜"] else ""))
        st.markdown(f"**次推：{five_dim['second']}**")
        st.markdown(f"**比分参考：{five_dim['score_hint']}**")
        st.markdown(f"**置信度：{five_dim['confidence']}（{five_dim['conf_detail']}）**")

        if five_dim['penalty_warning']:
            st.warning(five_dim['penalty_warning'])

        st.markdown("")
        st.markdown("**关键点：**")

        key_points = []

        if five_dim['strength_h'] - five_dim['strength_a'] >= 2:
            key_points.append(f"主队实力碾压（{five_dim['strength_h']}档 vs {five_dim['strength_a']}档）")
        elif five_dim['strength_a'] - five_dim['strength_h'] >= 2:
            key_points.append(f"客队实力碾压（{five_dim['strength_a']}档 vs {five_dim['strength_h']}档）")
        elif five_dim['strength_h'] > five_dim['strength_a']:
            key_points.append(f"主队实力占优（{five_dim['strength_h']}档 > {five_dim['strength_a']}档）")
        elif five_dim['strength_a'] > five_dim['strength_h']:
            key_points.append(f"客队实力占优（{five_dim['strength_a']}档 > {five_dim['strength_h']}档）")
        else:
            key_points.append("双方实力接近")

        if five_dim['ti_ke_result'] in ["体克用", "用生体"] and five_dim['score'] > 0:
            key_points.append(f"卦象{ti_ke_result} → 主队有利")
        elif five_dim['ti_ke_result'] in ["用克体", "体生用"] and five_dim['score'] < 0:
            key_points.append(f"卦象{ti_ke_result} → 客队有利")
        elif five_dim['ping_ju_tend'] > 0.55:
            key_points.append(f"平局倾向较高（{five_dim['ping_ju_tend']:.2f}），需防平局")
        else:
            key_points.append("卦象显示分胜负格局")

        if abs(five_dim['correction']) > 0.1:
            key_points.append(f"实力修正 {five_dim['correction']:+.2f}：{five_dim['correction_reason']}")

        if five_dim['is_liuhe']:
            if five_dim['liuhe_bonus'] <= 0.10:
                key_points.append("六合卦加成减半（体生用/用克体）")
            else:
                key_points.append(f"六合卦提示平局可能（加成{five_dim['liuhe_bonus']:.2f}）")

        if five_dim['event_correction'] > 0:
            key_points.append(f"赛事属性修正：平局倾向 +{five_dim['event_correction']:.2f}")

        if five_dim['home_advantage_mod'] > 1.0:
            key_points.append(f"主场优势增强（{five_dim['league']}）")
        elif five_dim['home_advantage_mod'] < 1.0:
            key_points.append(f"主场优势减弱（{five_dim['league']}）")

        for kp in key_points:
            st.markdown(f"  • {kp}")

        st.markdown("---")

        with st.expander("🔮 五维推演详情"):
            st.markdown(f"**综合倾向**：{five_dim['score']:+.2f}（正=主胜） | **平局倾向**：{five_dim['ping_ju_tend']:.2f}")
            st.markdown(f"**原始卦象分**：{five_dim['score_original']:+.2f} | **实力修正**：{five_dim['correction']:+.2f}")

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("体用", f"{s.get('体用生克', 0):+.2f}")
            with col2:
                st.metric("卦象", f"{s.get('卦象属性', 0):+.2f}")
            with col3:
                st.metric("动爻", f"{s.get('动爻位置', 0):+.2f}")
            with col4:
                st.metric("卦气", f"{s.get('卦气旺衰', 0):+.2f}")
            with col5:
                st.metric("卦名", f"{s.get('卦名吉凶', 0):+.2f}")

            st.markdown("**推演详情**：")
            for d in five_dim['details']:
                st.caption(f"• {d}")

        with st.expander("🔮 六爻逐爻详解"):
            for yao in liu_factors['yao_details']:
                dong_tag = "🔥 动爻" if yao['是否动爻'] else "静爻"
                st.write(f"**{yao['爻位']}** ({dong_tag})")
                st.write(f"  - 爻位取象：{yao['爻位取象']}")
                st.write(f"  - 解读：{yao['解读']}")

st.caption("💡 V8.7最终优化：欧战主场-25% | K联赛主场-18% | 挪超平局+15% | 解放者杯客场修正")
