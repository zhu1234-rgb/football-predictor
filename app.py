import streamlit as st
import datetime
import re

# ---------- PWA 配置 ----------
st.set_page_config(
    page_title="卦象+数据·足球胜平负",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================== 传统文化核心库 ==================
BAGUA_WUXING = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土"
}
BAGUA_LEIXIANG = {
    "乾": "天", "兑": "泽", "离": "火", "震": "雷",
    "巽": "风", "坎": "水", "艮": "山", "坤": "地"
}
LIUYAO_WEI = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
LIUYAO_GONG = ["震（足）", "离（眼/心）", "艮（手/肩）", "巽（股/财）", "坎（耳/肾）", "兑（口/肺）"]
LIUQIN_MAP = {
    "父母": "教练组/战术体系/文书",
    "官鬼": "中场控制/裁判/领导",
    "妻财": "前锋/射手/资金",
    "兄弟": "队友/对手/竞争",
    "子孙": "替补/年轻球员/福神"
}

def get_wuxing(gua):
    return BAGUA_WUXING.get(gua, "土")

def get_liuqin(body_wuxing, yao_wuxing):
    relations = {
        ("金","木"): "官鬼", ("金","火"): "妻财", ("金","土"): "父母", ("金","金"): "兄弟",
        ("木","金"): "妻财", ("木","火"): "子孙", ("木","土"): "官鬼", ("木","木"): "兄弟",
        ("水","金"): "父母", ("水","火"): "官鬼", ("水","土"): "妻财", ("水","木"): "子孙",
        ("火","金"): "官鬼", ("火","木"): "父母", ("火","土"): "子孙", ("火","火"): "兄弟",
        ("土","金"): "子孙", ("土","木"): "妻财", ("土","水"): "官鬼", ("土","火"): "父母",
    }
    return relations.get((body_wuxing, yao_wuxing), "比和")

GUA_DICT = {
    "乾乾": {"name": "乾为天", "gua_ci": "元亨利贞。", "xiang_ci": "天行健，君子以自强不息。"},
    "坤坤": {"name": "坤为地", "gua_ci": "元亨，利牝马之贞。君子有攸往，先迷后得主，利西南得朋，东北丧朋，安贞吉。", "xiang_ci": "地势坤，君子以厚德载物。"},
    "坎震": {"name": "水雷屯", "gua_ci": "元亨利贞。勿用有攸往，利建侯。", "xiang_ci": "云雷屯，君子以经纶。"},
    "艮坎": {"name": "山水蒙", "gua_ci": "亨。匪我求童蒙，童蒙求我。初筮告，再三渎，渎则不告。利贞。", "xiang_ci": "山下出泉，蒙，君子以果行育德。"},
    "坎乾": {"name": "水天需", "gua_ci": "有孚，光亨贞吉，利涉大川。", "xiang_ci": "云上于天，需，君子以饮食宴乐。"},
    "乾坎": {"name": "天水讼", "gua_ci": "有孚，窒惕，中吉，终凶。利见大人，不利涉大川。", "xiang_ci": "天与水违行，讼，君子以作事谋始。"},
    "坤坎": {"name": "地水师", "gua_ci": "贞，丈人吉，无咎。", "xiang_ci": "地中有水，师，君子以容民畜众。"},
    "坎坤": {"name": "水地比", "gua_ci": "吉，原筮，元永贞，无咎。不宁方来，后夫凶。", "xiang_ci": "地上有水，比，先王以建万国，亲诸侯。"},
    "巽乾": {"name": "风天小畜", "gua_ci": "亨，密云不雨，自我西郊。", "xiang_ci": "风行天上，小畜，君子以懿文德。"},
    "乾兑": {"name": "天泽履", "gua_ci": "履虎尾，不咥人，亨。", "xiang_ci": "上天下泽，履，君子以辩上下，定民志。"},
    "坤乾": {"name": "地天泰", "gua_ci": "小往大来，吉亨。", "xiang_ci": "天地交，泰，后以财成天地之道，辅相天地之宜，以左右民。"},
    "乾坤": {"name": "天地否", "gua_ci": "之匪人，不利君子贞，大往小来。", "xiang_ci": "天地不交，否，君子以俭德辟难，不可荣以禄。"},
    "乾离": {"name": "天火同人", "gua_ci": "于野，亨，利涉大川，利君子贞。", "xiang_ci": "天与火，同人，君子以类族辨物。"},
    "离乾": {"name": "火天大有", "gua_ci": "元亨。", "xiang_ci": "火在天上，大有，君子以遏恶扬善，顺天休命。"},
    "坤艮": {"name": "地山谦", "gua_ci": "亨，君子有终。", "xiang_ci": "地中有山，谦，君子以裒多益寡，称物平施。"},
    "震坤": {"name": "雷地豫", "gua_ci": "利建侯行师。", "xiang_ci": "雷出地奋，豫，先王以作乐崇德，殷荐之上帝，以配祖考。"},
    "兑震": {"name": "泽雷随", "gua_ci": "元亨利贞，无咎。", "xiang_ci": "泽中有雷，随，君子以向晦入宴息。"},
    "艮巽": {"name": "山风蛊", "gua_ci": "元亨，利涉大川。先甲三日，后甲三日。", "xiang_ci": "山下有风，蛊，君子以振民育德。"},
    "坤兑": {"name": "地泽临", "gua_ci": "元亨，利贞。至于八月有凶。", "xiang_ci": "泽上有地，临，君子以教思无穷，容保民无疆。"},
    "巽坤": {"name": "风地观", "gua_ci": "盥而不荐，有孚颙若。", "xiang_ci": "风行地上，观，先王以省方观民设教。"},
    "离震": {"name": "火雷噬嗑", "gua_ci": "亨，利用狱。", "xiang_ci": "雷电，噬嗑，先王以明罚敕法。"},
    "艮离": {"name": "山火贲", "gua_ci": "亨，小利有攸往。", "xiang_ci": "山下有火，贲，君子以明庶政，无敢折狱。"},
    "艮坤": {"name": "山地剥", "gua_ci": "不利有攸往。", "xiang_ci": "山附于地，剥，上以厚下安宅。"},
    "坤震": {"name": "地雷复", "gua_ci": "亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。", "xiang_ci": "雷在地中，复，先王以至日闭关，商旅不行，后不省方。"},
    "乾震": {"name": "天雷无妄", "gua_ci": "元亨，利贞。其匪正有眚，不利有攸往。", "xiang_ci": "天下雷行，物与无妄，先王以茂对时育万物。"},
    "艮乾": {"name": "山天大畜", "gua_ci": "利贞，不家食吉，利涉大川。", "xiang_ci": "天在山中，大畜，君子以多识前言往行，以畜其德。"},
    "艮震": {"name": "山雷颐", "gua_ci": "贞吉，观颐，自求口实。", "xiang_ci": "山下有雷，颐，君子以慎言语，节饮食。"},
    "兑巽": {"name": "泽风大过", "gua_ci": "栋桡，利有攸往，亨。", "xiang_ci": "泽灭木，大过，君子以独立不惧，遁世无闷。"},
    "坎坎": {"name": "坎为水", "gua_ci": "习坎，有孚，维心亨，行有尚。", "xiang_ci": "水洊至，习坎，君子以常德行，习教事。"},
    "离离": {"name": "离为火", "gua_ci": "利贞，亨。畜牝牛，吉。", "xiang_ci": "明两作，离，大人以继明照于四方。"},
    "兑艮": {"name": "泽山咸", "gua_ci": "亨，利贞，取女吉。", "xiang_ci": "山上有泽，咸，君子以虚受人。"},
    "震巽": {"name": "雷风恒", "gua_ci": "亨，无咎，利贞，利有攸往。", "xiang_ci": "雷风，恒，君子以立不易方。"},
    "乾艮": {"name": "天山遁", "gua_ci": "亨，小利贞。", "xiang_ci": "天下有山，遁，君子以远小人，不恶而严。"},
    "震乾": {"name": "雷天大壮", "gua_ci": "利贞。", "xiang_ci": "雷在天上，大壮，君子以非礼弗履。"},
    "离坤": {"name": "火地晋", "gua_ci": "康侯用锡马蕃庶，昼日三接。", "xiang_ci": "明出地上，晋，君子以自昭明德。"},
    "坤离": {"name": "地火明夷", "gua_ci": "利艰贞。", "xiang_ci": "明入地中，明夷，君子以莅众，用晦而明。"},
    "巽离": {"name": "风火家人", "gua_ci": "利女贞。", "xiang_ci": "风自火出，家人，君子以言有物，而行有恒。"},
    "离兑": {"name": "火泽睽", "gua_ci": "小事吉。", "xiang_ci": "上火下泽，睽，君子以同而异。"},
    "坎艮": {"name": "水山蹇", "gua_ci": "利西南，不利东北，利见大人，贞吉。", "xiang_ci": "山上有水，蹇，君子以反身修德。"},
    "震坎": {"name": "雷水解", "gua_ci": "利西南，无所往，其来复吉，有攸往，夙吉。", "xiang_ci": "雷雨作，解，君子以赦过宥罪。"},
    "艮兑": {"name": "山泽损", "gua_ci": "有孚，元吉，无咎，可贞，利有攸往。曷之用，二簋可用享。", "xiang_ci": "山下有泽，损，君子以惩忿窒欲。"},
    "巽震": {"name": "风雷益", "gua_ci": "利有攸往，利涉大川。", "xiang_ci": "风雷，益，君子以见善则迁，有过则改。"},
    "兑乾": {"name": "泽天夬", "gua_ci": "扬于王庭，孚号有厉。告自邑，不利即戎，利有攸往。", "xiang_ci": "泽上于天，夬，君子以施禄及下，居德则忌。"},
    "乾巽": {"name": "天风姤", "gua_ci": "女壮，勿用取女。", "xiang_ci": "天下有风，姤，后以施命诰四方。"},
    "兑坤": {"name": "泽地萃", "gua_ci": "亨，王假有庙，利见大人，亨，利贞。用大牲吉，利有攸往。", "xiang_ci": "泽上于地，萃，君子以除戎器，戒不虞。"},
    "坤巽": {"name": "地风升", "gua_ci": "元亨，用见大人，勿恤，南征吉。", "xiang_ci": "地中生木，升，君子以顺德，积小以高大。"},
    "兑坎": {"name": "泽水困", "gua_ci": "亨，贞大人吉，无咎，有言不信。", "xiang_ci": "泽无水，困，君子以致命遂志。"},
    "坎巽": {"name": "水风井", "gua_ci": "改邑不改井，无丧无得，往来井井。汔至亦未繘井，羸其瓶，凶。", "xiang_ci": "木上有水，井，君子以劳民劝相。"},
    "兑离": {"name": "泽火革", "gua_ci": "已日乃孚，元亨，利贞，悔亡。", "xiang_ci": "泽中有火，革，君子以治历明时。"},
    "离巽": {"name": "火风鼎", "gua_ci": "元吉，亨。", "xiang_ci": "木上有火，鼎，君子以正位凝命。"},
    "震震": {"name": "震为雷", "gua_ci": "亨，震来虩虩，笑言哑哑，震惊百里，不丧匕鬯。", "xiang_ci": "洊雷，震，君子以恐惧修省。"},
    "艮艮": {"name": "艮为山", "gua_ci": "其背，不获其身，行其庭，不见其人，无咎。", "xiang_ci": "兼山，艮，君子以思不出其位。"},
    "巽艮": {"name": "风山渐", "gua_ci": "女归吉，利贞。", "xiang_ci": "山上有木，渐，君子以居贤德善俗。"},
    "震兑": {"name": "雷泽归妹", "gua_ci": "征凶，无攸利。", "xiang_ci": "泽上有雷，归妹，君子以永终知敝。"},
    "震离": {"name": "雷火丰", "gua_ci": "亨，王假之，勿忧，宜日中。", "xiang_ci": "雷电皆至，丰，君子以折狱致刑。"},
    "离艮": {"name": "火山旅", "gua_ci": "小亨，旅贞吉。", "xiang_ci": "山上有火，旅，君子以明慎用刑，而不留狱。"},
    "巽巽": {"name": "巽为风", "gua_ci": "小亨，利有攸往，利见大人。", "xiang_ci": "随风，巽，君子以申命行事。"},
    "兑兑": {"name": "兑为泽", "gua_ci": "亨，利贞。", "xiang_ci": "丽泽，兑，君子以朋友讲习。"},
    "巽坎": {"name": "风水涣", "gua_ci": "亨，王假有庙，利涉大川，利贞。", "xiang_ci": "风行水上，涣，先王以享于帝立庙。"},
    "坎兑": {"name": "水泽节", "gua_ci": "亨，苦节不可贞。", "xiang_ci": "泽上有水，节，君子以制数度，议德行。"},
    "巽兑": {"name": "风泽中孚", "gua_ci": "豚鱼吉，利涉大川，利贞。", "xiang_ci": "泽上有风，中孚，君子以议狱缓死。"},
    "震艮": {"name": "雷山小过", "gua_ci": "亨，利贞，可小事，不可大事。飞鸟遗之音，不宜上宜下，大吉。", "xiang_ci": "山上有雷，小过，君子以行过乎恭，丧过乎哀，用过乎俭。"},
    "坎离": {"name": "水火既济", "gua_ci": "亨小，利贞，初吉，终乱。", "xiang_ci": "水在火上，既济，君子以思患而豫防之。"},
    "离坎": {"name": "火水未济", "gua_ci": "亨，小狐汔济，濡其尾，无攸利。", "xiang_ci": "火在水上，未济，君子以慎辨物居方。"}
}

# ================== 笔画字典 ==================
def count_strokes(name):
    stroke_dict = {
        "德": 15, "国": 8, "西": 6, "班": 10, "牙": 4,
        "南": 9, "非": 8, "加": 5, "拿": 10, "大": 3,
        "巴": 4, "阿": 7, "根": 10, "廷": 6,
        "法": 8, "意": 13, "利": 7, "英": 8, "格": 10, "兰": 5,
        "葡": 12, "萄": 11, "荷": 10, "比": 4,
        "瑞": 13, "士": 3, "丹": 4, "麦": 7, "挪": 10, "威": 9,
        "捷": 11, "克": 7, "奥": 12, "地": 6, "匈": 6,
        "希": 7, "腊": 12, "俄": 9, "罗": 8, "马": 3, "尼": 5,
        "日": 4, "本": 5, "韩": 12, "伊": 6, "朗": 10,
        "沙": 7, "特": 10, "拉": 8, "伯": 7,
        "墨": 15, "哥": 10, "美": 9,
        "乌": 4, "圭": 6, "卡": 5, "塔": 12, "尔": 5,
        "塞": 13, "内": 4, "亚": 6,
        "洪": 9, "都": 10, "斯": 12,
        "厄": 4, "瓜": 5, "多": 6,
        "智": 12, "秘": 10, "鲁": 12,
        "委": 8,
        "新": 13, "澳": 15,
        "中": 4, "台": 5, "港": 12, "门": 3,
        "朝": 12, "鲜": 14, "越": 12, "泰": 10, "印": 5, "度": 9,
        "菲": 11, "律": 9, "宾": 10, "坡": 8,
        "来": 7, "黎": 15, "嫩": 14, "以": 4, "色": 6, "列": 6,
        "约": 6, "旦": 5, "叙": 9, "伊": 6, "克": 7,
        "曼": 11, "苏": 7, "丹": 4,
        "联": 12, "邦": 7, "共": 6, "和": 8, "民": 5, "主": 5, "义": 3,
        "刚": 6, "果": 8, "佛": 7, "得": 11, "角": 7, "维": 11,
        "摩": 15, "洛": 9, "哥": 10, "塞": 13, "内": 4, "加": 5, "尔": 5,
        "科": 9, "特": 10, "迪": 8, "瓦": 4,
        "埃": 10, "及": 3,
        "纳": 7,
        "刚": 6, "果": 8, "佛": 7, "角": 7,
        "切": 4, "城": 9, "军": 6, "冠": 9,
        "竞": 10, "那": 6, "不": 4, "勒": 11,
        "沃": 7, "库": 7, "森": 12, "蒙": 13,
        "兴": 6, "圣": 5, "耳": 6, "里": 7, "昂": 8, "赛": 14,
        "索": 10, "莫": 10, "雷": 13, "伦": 10, "皇": 9, "家": 10,
        "社": 8, "会": 6, "贝": 7, "蒂": 12, "赫": 14,
        "布": 5, "莱": 11, "顿": 10, "富": 12, "姆": 8,
        "狼": 10, "队": 4, "诺": 10, "丁": 2, "汉": 5, "林": 8,
        "兹": 9, "弗": 5, "热": 10, "刺": 8, "纽": 7,
        "安": 6, "普": 12, "水": 4, "晶": 12, "宫": 9,
        "伯": 7, "恩": 10, "冈": 4, "米": 6, "堡": 12, "谢": 12,
        "旺": 8, "托": 6, "尤": 4, "文": 4, "图": 8, "际": 8,
        "齐": 6, "桑": 10, "博": 12, "拜": 9, "仁": 4, "慕": 14, "黑": 12,
        "川": 3, "崎": 11, "前": 9, "锋": 12, "横": 15, "滨": 13, "手": 4,
        "湘": 12, "鹿": 11, "岛": 7, "神": 9, "户": 4, "胜": 9, "船": 11,
        "桥": 10, "浦": 10, "红": 6, "钻": 10, "石": 5, "垣": 9, "太": 4,
        "阳": 6, "东": 5, "京": 8, "绿": 11, "茵": 9, "樱": 15, "花": 7, "阪": 7, "钢": 9,
        "全": 6, "北": 5, "现": 11, "代": 5, "蔚": 14, "山": 3,
        "项": 9, "制": 8, "铁": 10, "仁": 4,
        "原": 10, "三": 3, "星": 9, "蓝": 13, "翼": 17, "釜": 10, "邱": 7, "庆": 6,
        "道": 12, "养": 9, "光": 6, "州": 6,
        "市": 5, "政": 9, "府": 8, "忠": 8, "清": 11,
        "田": 5, "首": 9,
        "富": 12,
    }
    total = 0
    for char in name:
        if char in stroke_dict:
            total += stroke_dict[char]
        else:
            total += 5
    return total

# ---------- 杂占数据 ----------
SHICHEN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

MIAN_RE = {
    "子": "主喜庆事，主得财。", "丑": "主有烦恼、忧愁之事。",
    "寅": "主有客来，大吉。", "卯": "主有酒食及外人至。",
    "辰": "主有远客喜相逢，吉。", "巳": "主有急事人来见。",
    "午": "主有亲人相见。", "未": "主有词讼口舌是非。",
    "申": "主有高人来会相见。", "酉": "主有高人来会相见。",
    "戌": "主有酒食事。", "亥": "主有词讼不宁之事。"
}
YAN_TIAO = {
    "子": {"左": "有贵人", "右": "有酒食"}, "丑": {"左": "有犹疑", "右": "有人思"},
    "寅": {"左": "远人来", "右": "喜庆事"}, "卯": {"左": "贵人来", "右": "平安吉"},
    "辰": {"左": "客人来", "右": "损害事"}, "巳": {"左": "主酒食", "右": "主凶事"},
    "午": {"左": "主饮食", "右": "主凶事"}, "未": {"左": "主吉昌", "右": "主小喜"},
    "申": {"左": "有财利", "右": "有女思"}, "酉": {"左": "有客至", "右": "主亲来"},
    "戌": {"左": "主酒食", "右": "主聚会"}, "亥": {"左": "有客来", "右": "主官非"}
}
ER_RE = {
    "子": "主有僧道来相议事。", "丑": "主有喜事临身，大吉。",
    "寅": "主有酒食相会，大吉。", "卯": "主有远人来相见，吉。",
    "辰": "主有财喜大通达，吉。", "巳": "主有失财物事，不利。",
    "午": "主有喜气事来，大吉。", "未": "主有客来相求之事。",
    "申": "主有酒食宴乐事，吉。", "酉": "主有人来言婚姻事。",
    "戌": "主有争讼口舌之事。", "亥": "主有官非词讼之事。"
}
ER_MING = {
    "子": {"左": "女思", "右": "失财"}, "丑": {"左": "口舌", "右": "争讼"},
    "寅": {"左": "失财", "右": "心急"}, "卯": {"左": "坎坷", "右": "客至"},
    "辰": {"左": "远行", "右": "客至"}, "巳": {"左": "凶事", "右": "大吉"},
    "午": {"左": "远信", "右": "亲来"}, "未": {"左": "饮食", "右": "人来"},
    "申": {"左": "行人", "右": "大吉"}, "酉": {"左": "失财", "右": "大吉"},
    "戌": {"左": "酒食", "右": "客至"}, "亥": {"左": "大吉", "右": "酒食"}
}
JIN_MING = {
    "子": "主六畜平安，大吉。", "丑": "主家宅定、富贵，大吉。",
    "寅": "主家宅凶、怪事，大凶。", "卯": "主家门祸事至，大凶。",
    "辰": "主有田蚕收成，大吉。", "巳": "主福至财来，大吉。",
    "午": "主官事消散，大吉昌。", "未": "主凶祸不祥之事，不利。",
    "申": "主远客行人来，大吉。", "酉": "主远客行人来，大吉。",
    "戌": "主小喜、亨通，大吉。", "亥": "主官非词讼有理，吉。"
}
HUO_YI = {
    "子": "妻有外思、烦闷之事。", "丑": "主女心向外，大不吉利。",
    "寅": "主得小喜，平安，大吉利。", "卯": "主得财帛、亨通之兆。",
    "辰": "主忧心、损男小口，灾。", "巳": "主喜事，酒食相逢。",
    "午": "主相争、官非、大灾事。", "未": "主财喜昌盛之兆。",
    "申": "主财帛、会合事，吉。", "酉": "主凶灾、丧服之兆。",
    "戌": "主忧心、终得理之兆。", "亥": "主身疾病、不祥之兆。"
}
QUAN_OU = {
    "子": "主妇人不时争斗。", "丑": "主有忧心烦闷之事。",
    "寅": "望天嘔，主进财，大吉利。", "卯": "望天嘔，必得财，大吉。",
    "辰": "主喜事至，大亨通，吉。", "巳": "主亲人想念，信至。",
    "午": "主逢酒食宴会，大吉。", "未": "主家中内外破财。",
    "申": "主家宅有小口之忧。", "酉": "主加官进禄，得财，吉。",
    "戌": "主口舌之事，大凶。", "亥": "主官非词讼之事。"
}
YI_LIU = {
    "子": "男主酒食，女主亲事。", "丑": "主愁思破财之事。",
    "寅": "主进财，大吉利。", "卯": "主酒食，交友，相会，吉。",
    "辰": "主失财、忧灾、疾病。", "巳": "女外思，男无凶。",
    "午": "主远人至，得利，大吉。", "未": "主血光之灾，化凶为吉。",
    "申": "主得外财，出入大吉。", "酉": "主客至、破财，不利。",
    "戌": "主词讼、得财，大吉。", "亥": "主见官、得财，大吉。"
}
PEN_KE = {
    "子": "主逢吉人，酒食相会。", "丑": "主女人思，客来求事。",
    "寅": "主女人相遇，有酒食。", "卯": "主有财、喜，有客来。",
    "辰": "主有酒食，大吉利。", "巳": "主吉人来求财，喜。",
    "午": "主客来、酒会、宴饮。", "未": "主酒食相会合之事。",
    "申": "主夜梦惊恐，酒食不利。", "酉": "主妇人来求请问事。",
    "戌": "主妇人思会和合事。", "亥": "主虚惊，反得吉利。"
}
ROU_CHAN = {
    "子": "主尊长人来，大吉。", "丑": "主吉祥临身，大吉。",
    "寅": "主凶事，化凶为吉。", "卯": "主得财事，大吉利。",
    "辰": "主凶恶临身，大凶。", "巳": "主宾友相见，大吉利。",
    "午": "主忧疑事，自身吉。", "未": "主喜事，自身大吉。",
    "申": "主口舌，解之则吉。", "酉": "主因财起祸事，大凶。",
    "戌": "主行人远来，大吉。", "亥": "主大吉利、喜之事。"
}
XIN_JING = {
    "子": "主有女子思喜事至。", "丑": "主有恶事临门，大凶。",
    "寅": "主有客来饮食，大吉。", "卯": "主有酒食事及外人来。",
    "辰": "主有成合喜事，大吉利。", "巳": "主有女思及喜事至。",
    "午": "主有酒食自来，大吉。", "未": "主有女思念，大吉。",
    "申": "主有大喜之事至，大吉。", "酉": "主有喜信至，大吉庆。",
    "戌": "主有贵人即至，大吉。", "亥": "主有恶梦，大凶。"
}
QUE_ZAO = {
    "子": "主有远亲人至，大吉。", "丑": "主有喜庆之事，大吉。",
    "寅": "主有词讼之事，小吉。", "卯": "主有酒食财喜，大吉。",
    "辰": "主有远行人回家，吉。", "巳": "主有喜事降临，大吉。",
    "午": "主有疾病，求神安，吉。", "未": "主有六畜不见之事。",
    "申": "主有喜庆事，大吉昌。", "酉": "主有坎坷不安之事。",
    "戌": "主有财帛亨通，大吉。", "亥": "主有口舌争斗之事。"
}

def get_shichen(match_time):
    hour = match_time.hour
    shichen_index = (hour + 1) // 2 % 12
    return SHICHEN[shichen_index]

# ---------- 起卦函数 ----------
def generate_gua_info(home, away):
    clean_home = re.sub(r'[^\u4e00-\u9fa5]', '', home)
    clean_away = re.sub(r'[^\u4e00-\u9fa5]', '', away)
    home_strokes = count_strokes(clean_home)
    away_strokes = count_strokes(clean_away)
    total_strokes = home_strokes + away_strokes
    upper_num = home_strokes % 8
    if upper_num == 0: upper_num = 8
    lower_num = away_strokes % 8
    if lower_num == 0: lower_num = 8
    moving_yao = total_strokes % 6
    if moving_yao == 0: moving_yao = 6
    num_to_gua = {1:"乾",2:"兑",3:"离",4:"震",5:"巽",6:"坎",7:"艮",8:"坤"}
    upper = num_to_gua.get(upper_num, "乾")
    lower = num_to_gua.get(lower_num, "乾")
    reverse = {"乾":"坤","坤":"乾","震":"巽","巽":"震","坎":"离","离":"坎","艮":"兑","兑":"艮"}
    change_upper = reverse.get(upper, upper)
    change_lower = reverse.get(lower, lower)
    inter_upper = "坎" if upper != "坤" else "坤"
    inter_lower = "离" if lower != "坤" else "坤"
    body = upper
    use = lower
    body_wuxing = BAGUA_WUXING.get(body, "土")
    use_wuxing = BAGUA_WUXING.get(use, "土")
    if body_wuxing == use_wuxing:
        ti_yong = "比和（平局相）"
    elif (body_wuxing == "木" and use_wuxing == "土") or (body_wuxing == "火" and use_wuxing == "金") or (body_wuxing == "土" and use_wuxing == "水") or (body_wuxing == "金" and use_wuxing == "木") or (body_wuxing == "水" and use_wuxing == "火"):
        ti_yong = "体克用（主队制胜）"
    elif (use_wuxing == "木" and body_wuxing == "土") or (use_wuxing == "火" and body_wuxing == "金") or (use_wuxing == "土" and body_wuxing == "水") or (use_wuxing == "金" and body_wuxing == "木") or (use_wuxing == "水" and body_wuxing == "火"):
        ti_yong = "用克体（客队制胜）"
    else:
        ti_yong = "相生（平和）"
    shi_yao = moving_yao - 1
    ying_yao = (shi_yao + 4) % 6
    return {
        "base": (upper, lower),
        "base_key": upper + lower,
        "base_name": f"{BAGUA_LEIXIANG[upper]}{BAGUA_LEIXIANG[lower]}",
        "change": (change_upper, change_lower),
        "change_name": f"{BAGUA_LEIXIANG[change_upper]}{BAGUA_LEIXIANG[change_lower]}",
        "inter": (inter_upper, inter_lower),
        "inter_name": f"{BAGUA_LEIXIANG[inter_upper]}{BAGUA_LEIXIANG[inter_lower]}",
        "body": body, "use": use,
        "body_wuxing": body_wuxing, "use_wuxing": use_wuxing,
        "ti_yong": ti_yong,
        "shi_yao": shi_yao, "ying_yao": ying_yao,
        "moving_yao": moving_yao,
        "home_strokes": home_strokes,
        "away_strokes": away_strokes,
        "total_strokes": total_strokes
    }

def analyze_yao(gua_info, home, away):
    body_wuxing = gua_info["body_wuxing"]
    wuxing_cycle = ["木", "火", "土", "金", "水", "木"]
    yao_details = []
    for i in range(6):
        yao_wuxing = wuxing_cycle[i]
        liuqin = get_liuqin(body_wuxing, yao_wuxing)
        if liuqin == "官鬼":
            jixiong = "凶（受克）"
        elif liuqin == "妻财":
            jixiong = "吉（得财）"
        elif liuqin == "父母":
            jixiong = "吉（得生）" if body_wuxing in ["火","土"] else "中"
        elif liuqin == "兄弟":
            jixiong = "中（竞争）"
        else:
            jixiong = "平（比和）"

        if i == 0:
            text = f"**初爻（根基）**：{home}的初始战术部署与防守稳固性。"
        elif i == 1:
            text = f"**二爻（节奏）**：中场控制权与比赛节奏。"
        elif i == 2:
            text = f"**三爻（攻势）**：{home}的前锋线效率与威胁球能力。"
        elif i == 3:
            text = f"**四爻（防守）**：{home}的防线稳固性及门将发挥。"
        elif i == 4:
            text = f"**五爻（气势）**：{home}的球队士气与教练临场调度。"
        else:
            text = f"**上爻（终局）**：比赛最终走向与运气成分。"

        if liuqin == "官鬼":
            text += f" 官鬼临爻，{away}的中场施压或裁判尺度可能成为关键变量。"
        elif liuqin == "妻财":
            text += f" 妻财临爻，{home}的锋线终结能力将直接决定比分。"
        elif liuqin == "兄弟":
            text += f" 兄弟临爻，两队中场绞杀激烈。"
        elif liuqin == "子孙":
            text += f" 子孙临爻，{home}的替补席或年轻球员可能成为奇兵。"
        elif liuqin == "父母":
            text += f" 父母临爻，{home}的战术纪律性将主导比赛走向。"

        yao_details.append({
            "position": LIUYAO_WEI[i],
            "wuxing": yao_wuxing,
            "liuqin": liuqin,
            "gong": LIUYAO_GONG[i],
            "jixiong": jixiong,
            "text": text
        })
    return yao_details

def get_bing_yao():
    return {
        "用神": "世爻（主队）",
        "忌神": "克用者",
        "元神": "生用者",
        "仇神": "克元神者",
        "病药": "卦中无动爻克用，病药不显。"
    }

# ---------- 核心预测函数（自动计算权重，融合胜平负数据）----------
def predict_by_gua(home, away, match_time,
                   home_goals=0, home_conceded=0, away_goals=0, away_conceded=0,
                   home_wins=0, home_draws=0, home_losses=0,
                   away_wins=0, away_draws=0, away_losses=0):
    """
    参数：
    home_wins, home_draws, home_losses: 主队近10场胜平负
    away_wins, away_draws, away_losses: 客队近10场胜平负
    """
    gua_info = generate_gua_info(home, away)
    yao_details = analyze_yao(gua_info, home, away)
    bing_yao = get_bing_yao()
    shichen = get_shichen(match_time)

    # ---- 卦象评分 ----
    score_home = 0
    score_away = 0
    score_draw = 0

    ti = gua_info["ti_yong"]
    if ti == "体克用（主队制胜）":
        score_home += 2
    elif ti == "用克体（客队制胜）":
        score_away += 2
    elif ti == "比和（平局相）":
        score_draw += 2
    else:
        score_draw += 1

    shi = gua_info["shi_yao"]
    ying = gua_info["ying_yao"]
    if shi < ying:
        score_home += 1
    elif shi > ying:
        score_away += 1
    else:
        score_draw += 1

    for yao in yao_details:
        if "吉" in yao["jixiong"]:
            if yao["liuqin"] in ["妻财", "父母", "子孙"]:
                score_home += 1
            elif yao["liuqin"] in ["官鬼"]:
                score_away += 1
        elif "凶" in yao["jixiong"]:
            if yao["liuqin"] in ["官鬼"]:
                score_home -= 1
            elif yao["liuqin"] in ["妻财"]:
                score_away -= 1

    za_items = [MIAN_RE[shichen], YAN_TIAO[shichen]['左'], YAN_TIAO[shichen]['右'],
                ER_RE[shichen], ER_MING[shichen]['左'], ER_MING[shichen]['右'],
                JIN_MING[shichen], HUO_YI[shichen], QUAN_OU[shichen],
                YI_LIU[shichen], PEN_KE[shichen], ROU_CHAN[shichen],
                XIN_JING[shichen], QUE_ZAO[shichen]]
    for text in za_items:
        if "吉" in text or "喜" in text or "利" in text or "财" in text:
            score_home += 0.5
        elif "凶" in text or "灾" in text or "祸" in text or "损" in text:
            score_away += 0.5

    # ---- 数据评分（综合净胜球和胜平负） ----
    data_home_score = 0
    data_away_score = 0
    data_draw_score = 0

    # 检查是否有任何数据输入
    has_goal_data = (home_goals + home_conceded + away_goals + away_conceded) > 0
    has_wdl_data = (home_wins + home_draws + home_losses + away_wins + away_draws + away_losses) > 0

    if has_goal_data or has_wdl_data:
        # 1. 净胜球分
        if has_goal_data:
            home_avg_goals = home_goals / 10
            home_avg_conceded = home_conceded / 10
            away_avg_goals = away_goals / 10
            away_avg_conceded = away_conceded / 10
            home_net = home_avg_goals - home_avg_conceded
            away_net = away_avg_goals - away_avg_conceded
            net_diff = home_net - away_net
            net_score = max(-2.0, min(2.0, net_diff * 1.5))
        else:
            net_score = 0.0

        # 2. 胜率分
        if has_wdl_data:
            # 确保总和为10（如果用户输入不全，则按比例计算）
            home_total = home_wins + home_draws + home_losses
            away_total = away_wins + away_draws + away_losses
            if home_total > 0:
                home_win_rate = home_wins / home_total
                home_loss_rate = home_losses / home_total
            else:
                home_win_rate = home_loss_rate = 0.5
            if away_total > 0:
                away_win_rate = away_wins / away_total
                away_loss_rate = away_losses / away_total
            else:
                away_win_rate = away_loss_rate = 0.5
            # 胜率差（主-客），范围 -1~1
            win_diff = home_win_rate - away_win_rate
            # 考虑负场差（负场多则不利）
            loss_diff = home_loss_rate - away_loss_rate
            # 综合状态分：胜率贡献0.7，负率贡献0.3（负率差负向影响）
            state_diff = win_diff * 0.7 - loss_diff * 0.3
            state_score = max(-2.0, min(2.0, state_diff * 2.0))
        else:
            state_score = 0.0

        # 综合数据分：净胜球分占0.6，状态分占0.4（可调）
        if has_goal_data and has_wdl_data:
            data_score = net_score * 0.6 + state_score * 0.4
        elif has_goal_data:
            data_score = net_score
        else:
            data_score = state_score

        # 将数据分映射到主胜/平/客胜的分数（直接使用正值为主队优势，负值为客队优势）
        if data_score > 0.3:
            data_home_score = data_score
            data_away_score = 0
            data_draw_score = 0
        elif data_score < -0.3:
            data_away_score = -data_score
            data_home_score = 0
            data_draw_score = 0
        else:
            data_draw_score = 2.0
            data_home_score = 0
            data_away_score = 0

        # ---- 自动计算权重 ----
        # 信息量：基于输入的数据项数
        info_count = 0
        if has_goal_data:
            info_count += 1
        if has_wdl_data:
            info_count += 1
        info_factor = min(1.0, info_count / 2)  # 最多2项，饱和为1

        # 差异度：净胜球差绝对值 + 状态差绝对值的平均
        if has_goal_data and has_wdl_data:
            diff_magnitude = (abs(net_diff) * 0.6 + abs(state_diff) * 0.4) / 1.5  # 归一化到0~1
        elif has_goal_data:
            diff_magnitude = abs(net_diff) / 1.5
        else:
            diff_magnitude = abs(state_diff) / 1.5
        diff_magnitude = min(1.0, diff_magnitude)
        # 差异因子映射到 0.2~0.8
        diff_factor = 0.2 + diff_magnitude * 0.6

        data_weight = info_factor * diff_factor
        data_weight = max(0.0, min(0.8, data_weight))
    else:
        data_weight = 0.0

    # ---- 加权合并 ----
    gua_weight = 1 - data_weight

    final_home = score_home * gua_weight + data_home_score * data_weight
    final_draw = score_draw * gua_weight + data_draw_score * data_weight
    final_away = score_away * gua_weight + data_away_score * data_weight

    scores = [("主胜", final_home), ("平局", final_draw), ("客胜", final_away)]
    scores.sort(key=lambda x: x[1], reverse=True)
    primary = scores[0][0]
    secondary = scores[1][0]

    return {
        "gua_info": gua_info,
        "yao_details": yao_details,
        "bing_yao": bing_yao,
        "shichen": shichen,
        "primary": primary,
        "secondary": secondary,
        "final_scores": scores,
        "data_weight": data_weight,
        "has_data": has_goal_data or has_wdl_data
    }

# ================== UI 界面 ==================
st.image("https://img.icons8.com/color/96/000000/football2.png", width=80)
st.title("⚽ 卦象+数据·足球胜平负")
st.caption("输入球队名称、比赛时间，及近10场数据（进球/失球/胜平负），系统自动融合")

with st.expander("📋 输入比赛信息", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        home = st.text_input("主队名称", placeholder="如：富川")
    with col2:
        away = st.text_input("客队名称", placeholder="如：安养")

    match_date = st.date_input("比赛日期", value=datetime.date.today())
    match_time_sel = st.time_input("比赛时间（开球时刻）", value=datetime.time(0, 0))
    match_time = datetime.datetime.combine(match_date, match_time_sel)

    st.subheader("近10场进球/失球（选填）")
    col3, col4 = st.columns(2)
    with col3:
        home_goals = st.number_input("主队总进球", min_value=0, value=0, step=1)
        home_conceded = st.number_input("主队总失球", min_value=0, value=0, step=1)
    with col4:
        away_goals = st.number_input("客队总进球", min_value=0, value=0, step=1)
        away_conceded = st.number_input("客队总失球", min_value=0, value=0, step=1)

    st.subheader("近10场胜平负（选填）")
    st.caption("三项之和可为10，若不全填则按比例计算")
    col5, col6 = st.columns(2)
    with col5:
        home_wins = st.number_input("主队胜", min_value=0, max_value=10, value=0, step=1)
        home_draws = st.number_input("主队平", min_value=0, max_value=10, value=0, step=1)
        home_losses = st.number_input("主队负", min_value=0, max_value=10, value=0, step=1)
    with col6:
        away_wins = st.number_input("客队胜", min_value=0, max_value=10, value=0, step=1)
        away_draws = st.number_input("客队平", min_value=0, max_value=10, value=0, step=1)
        away_losses = st.number_input("客队负", min_value=0, max_value=10, value=0, step=1)

if st.button("🔮 起卦推演", use_container_width=True):
    if not home or not away:
        st.error("请输入主客队名称")
    else:
        result = predict_by_gua(
            home, away, match_time,
            home_goals, home_conceded, away_goals, away_conceded,
            home_wins, home_draws, home_losses,
            away_wins, away_draws, away_losses
        )
        gua = result["gua_info"]
        yao = result["yao_details"]
        bing = result["bing_yao"]
        shichen = result["shichen"]
        final_scores = result["final_scores"]
        data_weight = result["data_weight"]
        has_data = result["has_data"]

        st.divider()
        st.markdown(f"## 🎯 推演结论：首推 **{result['primary']}**，次推 **{result['secondary']}**")

        if has_data:
            st.caption(f"自动数据权重：{data_weight:.0%}（基于输入数据自动计算）")
        else:
            st.caption("未输入数据，权重为0（纯卦象）")

        st.caption(f"最终得分：主胜 {final_scores[0][1]:.2f}，平局 {final_scores[1][1]:.2f}，客胜 {final_scores[2][1]:.2f}")

        with st.expander("🔮 卦象、六爻、杂占详情（点击展开）", expanded=True):
            st.markdown("### 起卦依据")
            st.caption(f"主队“{home}”笔画数 {gua['home_strokes']}，客队“{away}”笔画数 {gua['away_strokes']}，总笔画 {gua['total_strokes']}，动爻 {gua['moving_yao']}")

            col_g1, col_g2, col_g3 = st.columns(3)
            col_g1.metric("本卦", f"{gua['base'][0]}{gua['base'][1]}（{gua['base_name']}）")
            col_g2.metric("变卦", f"{gua['change'][0]}{gua['change'][1]}（{gua['change_name']}）")
            col_g3.metric("互卦", f"{gua['inter'][0]}{gua['inter'][1]}（{gua['inter_name']}）")

            st.write(f"**体用生克**：{gua['ti_yong']}  （体卦{gua['body']}五行{get_wuxing(gua['body'])}，用卦{gua['use']}五行{get_wuxing(gua['use'])}）")
            st.write(f"**世应**：世爻在{LIUYAO_WEI[gua['shi_yao']]}（主队），应爻在{LIUYAO_WEI[gua['ying_yao']]}（客队）")

            base_key = gua["base_key"]
            if base_key in GUA_DICT:
                g = GUA_DICT[base_key]
                st.markdown(f"**📖 本卦【{g['name']}】卦辞**：{g['gua_ci']}")
                st.markdown(f"**象辞**：{g['xiang_ci']}")

            st.write("**💊 病药体系**：" + bing['病药'])
            st.write(f"用神：{bing['用神']} | 忌神：{bing['忌神']} | 元神：{bing['元神']} | 仇神：{bing['仇神']}")

            st.markdown("### 六爻逐爻详解")
            for i, y in enumerate(yao):
                st.markdown(f"**{y['position']}**  (爻位：{y['gong']})")
                st.caption(f"五行：{y['wuxing']}，六亲：{y['liuqin']}（{LIUQIN_MAP.get(y['liuqin'], '')}），吉凶：{y['jixiong']}")
                st.write(y['text'])
                st.markdown("---")

            st.markdown("### 杂占（时辰：" + shichen + "时）")
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                st.markdown(f"**面热**：{MIAN_RE[shichen]}")
                st.markdown(f"**眼跳**：左{YAN_TIAO[shichen]['左']}，右{YAN_TIAO[shichen]['右']}")
                st.markdown(f"**耳热**：{ER_RE[shichen]}")
                st.markdown(f"**耳鸣**：左{ER_MING[shichen]['左']}，右{ER_MING[shichen]['右']}")
                st.markdown(f"**金鸣**：{JIN_MING[shichen]}")
                st.markdown(f"**火逸**：{HUO_YI[shichen]}")
            with col_z2:
                st.markdown(f"**犬嘔**：{QUAN_OU[shichen]}")
                st.markdown(f"**衣留**：{YI_LIU[shichen]}")
                st.markdown(f"**喷嗑**：{PEN_KE[shichen]}")
                st.markdown(f"**肉颤**：{ROU_CHAN[shichen]}")
                st.markdown(f"**心惊**：{XIN_JING[shichen]}")
                st.markdown(f"**鹊噪**：{QUE_ZAO[shichen]}")

        if has_data:
            st.caption("已自动融合近10场进球/失球和胜平负数据。")
        else:
            st.caption("未输入近10场数据，预测仅基于卦象。")

        st.caption("注：本推演基于传统易学与杂占，结合球队近况数据，仅供娱乐参考。")
