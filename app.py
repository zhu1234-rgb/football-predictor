# V6.0 足球预测 · 最终完整版
# 笔画起卦 · 补丁融合 · 比赛时间 · 四层推演 · 让球选项清晰标注

import streamlit as st
import math
import datetime
import re

# ---------- PWA 配置 ----------
st.markdown(
    '<link rel="manifest" href="manifest.json">',
    unsafe_allow_html=True
)
st.markdown("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://img.icons8.com/color/96/000000/football2.png">
    <link rel="icon" type="image/png" sizes="32x32" href="https://img.icons8.com/color/96/000000/football2.png">
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="V6.0 足球预测",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================== 核心库 ==================

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

# ---------- 六十四卦完整辞象 ----------
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

# ---------- 工具函数 ----------
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

# ================== 古代杂占（完整） ==================

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

def get_shichen_from_time(match_time):
    hour = match_time.hour
    shichen_index = (hour + 1) // 2 % 12
    return SHICHEN[shichen_index]

# ================== 笔画起卦函数 ==================

def count_strokes(name):
    stroke_dict = {
        "德": 15, "国": 8, "西": 6, "班": 10, "牙": 4,
        "南": 9, "非": 8, "加": 5, "拿": 10, "大": 3,
        "巴": 4, "西": 6, "阿": 7, "根": 10, "廷": 6,
        "法": 8, "意": 13, "利": 7, "英": 8, "格": 10, "兰": 5,
        "葡": 12, "萄": 11, "牙": 4, "荷": 10, "比": 4,
        "瑞": 13, "士": 3, "丹": 4, "麦": 7, "挪": 10, "威": 9,
        "捷": 11, "克": 7, "奥": 12, "地": 6, "匈": 6,
        "希": 7, "腊": 12, "俄": 9, "罗": 8, "马": 3, "尼": 5,
        "日": 4, "本": 5, "韩": 12, "伊": 6, "朗": 10,
        "沙": 7, "特": 10, "阿": 7, "拉": 8, "伯": 7,
        "墨": 15, "哥": 10, "美": 9, "加": 5, "拿": 10, "大": 3,
        "乌": 4, "拉": 8, "圭": 6, "卡": 5, "塔": 12, "尔": 5,
        "塞": 13, "内": 4, "加": 5, "尔": 5, "尼": 5, "亚": 6,
        "洪": 9, "都": 10, "拉": 8, "斯": 12, "哥": 10,
        "厄": 4, "瓜": 5, "多": 6, "尔": 5,
        "智": 12, "利": 7, "秘": 10, "鲁": 12,
        "委": 8, "内": 4, "瑞": 13, "拉": 8,
        "新": 13, "西": 6, "兰": 5, "澳": 15, "大": 3,
        "中": 4, "台": 5, "港": 12, "澳": 15, "门": 3,
        "朝": 12, "鲜": 14, "越": 12, "泰": 10, "印": 5, "度": 9,
        "菲": 11, "律": 9, "宾": 10, "新": 13, "加": 5, "坡": 8,
        "马": 3, "来": 7, "西": 6, "亚": 6,
        "哥": 10, "斯": 12, "达": 6, "黎": 15, "巴": 4,
        "嫩": 14, "以": 4, "色": 6, "列": 6, "约": 6, "旦": 5,
        "叙": 9, "利": 7, "亚": 6, "伊": 6, "拉": 8, "克": 7,
        "阿": 7, "曼": 11, "苏": 7, "丹": 4, "南": 9, "苏": 7,
        "南": 9, "非": 8, "中": 4, "国": 8,
    }
    total = 0
    for char in name:
        if char in stroke_dict:
            total += stroke_dict[char]
        else:
            total += 5
    return total

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
    body = upper; use = lower
    body_wuxing = get_wuxing(body); use_wuxing = get_wuxing(use)
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

# ================== 爻辞分析 ==================

def analyze_yao(gua_info, match_type, home, away):
    body_wuxing = gua_info["body_wuxing"]
    wuxing_cycle = ["木", "火", "土", "金", "水", "木"]
    yao_details = []
    for i in range(6):
        yao_wuxing = wuxing_cycle[i]
        liuqin = get_liuqin(body_wuxing, yao_wuxing)
        if liuqin == "父母":
            jixiong = "吉（得生）" if body_wuxing in ["火","土"] else "中"
        elif liuqin == "官鬼":
            jixiong = "凶（受克）" if body_wuxing in ["金","木"] else "凶"
        elif liuqin == "妻财":
            jixiong = "吉（得财）"
        elif liuqin == "兄弟":
            jixiong = "中（竞争）"
        else:
            jixiong = "平（比和）"

        if i == 0:
            text = f"**初爻（根基）**：{home}的初始战术部署与防守稳固性。"
            text += " 此爻为全卦之基，主队开局状态与第一道防线。宜静不宜动，静则稳，动则生变。"
        elif i == 1:
            text = f"**二爻（节奏）**：中场控制权与比赛节奏。"
            text += f" 二爻为内卦之中，主中场调度。若此爻得位，则{home}能掌控比赛节奏；若失位，则易被{away}反制。"
        elif i == 2:
            text = f"**三爻（攻势）**：{home}的前锋线效率与威胁球能力。"
            text += " 三爻为内卦之极，主攻端。此爻发动则攻势凌厉，然亦需防急于求成反被偷袭。"
        elif i == 3:
            text = f"**四爻（防守）**：{home}的防线稳固性及门将发挥。"
            text += " 四爻为外卦之始，主守端。此爻旺相则后卫线滴水不漏，衰弱则恐有闪失。"
        elif i == 4:
            text = f"**五爻（气势）**：{home}的球队士气与教练临场调度。"
            text += " 五爻为君位，主主教练与核心球员。此爻当权则全队气势如虹，受克则军心涣散。"
        else:
            text = f"**上爻（终局）**：比赛最终走向与运气成分。"
            text += " 上爻为天位，主结果与偶然因素。此爻临吉则好运相伴，临凶则恐有意外变数。"
            if match_type in ["final", "knockout"]:
                text += " 加时赛或点球大战的可能性需纳入考虑。"

        if liuqin == "官鬼":
            if match_type == "knockout":
                text += " 官鬼在淘汰赛主压力，宜有子孙解忧。"
            elif match_type == "final":
                text += " 官鬼在决赛主心理压力，谁先放下包袱谁占优。"
            else:
                text += f" 官鬼临爻，{away}的中场施压或裁判尺度可能成为关键变量。"
        elif liuqin == "妻财":
            text += f" 妻财临爻，{home}的锋线终结能力将直接决定比分。"
        elif liuqin == "兄弟":
            text += f" 兄弟临爻，两队中场绞杀激烈，第二落点的争夺至关重要。"
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

def get_bing_yao(match_type):
    if match_type == "knockout":
        bing = "淘汰赛官鬼为病，宜有子孙制之。"
    elif match_type == "final":
        bing = "决赛双方皆谨慎，比和为主，病在谁先犯错。"
    elif match_type == "draw":
        bing = "平局相，比和为主，病在攻守失衡。"
    elif match_type == "slaughter":
        bing = "屠杀局，妻财过旺为病，宜有兄弟制财。"
    else:
        bing = "卦中无动爻克用，病药不显。"
    return {
        "用神": "世爻（主队）",
        "忌神": "克用者",
        "元神": "生用者",
        "仇神": "克元神者",
        "病药": bing
    }

def full_gua_analysis(home, away, match_type):
    gua_info = generate_gua_info(home, away)
    yao_details = analyze_yao(gua_info, match_type, home, away)
    bing_yao = get_bing_yao(match_type)
    return {
        "gua_info": gua_info,
        "yao_details": yao_details,
        "bing_yao": bing_yao
    }

# ================== 量化计算 ==================

def compute_lam(home_elo, away_elo, home_xg, away_xg, home_form, away_form, patches, match_type):
    elo_factor = (home_elo - away_elo) / 2000 * 0.4
    xg_factor = (home_xg / (home_xg + away_xg + 0.01)) * 0.4
    form_factor = (home_form - away_form) * 0.1 + 0.5
    lam_h = max(0.3, elo_factor + xg_factor + form_factor)
    lam_a = max(0.3, -elo_factor + (away_xg / (home_xg + away_xg + 0.01)) * 0.4 + (away_form - home_form) * 0.1 + 0.5)

    if patches.get("home_rotation", 0) >= 4:
        lam_h *= 0.5
    if patches.get("away_rotation", 0) >= 4:
        lam_a *= 0.5

    if home_xg >= 2.5 and away_xg <= 0.8:
        if match_type in ["final", "knockout"]:
            lam_h *= 1.5
        else:
            lam_h *= 2.0
        lam_a *= 0.6

    return round(lam_h, 2), round(lam_a, 2)

def poisson_prob(lam, goals):
    return (math.exp(-lam) * (lam ** goals)) / math.factorial(goals)

# ================== 四层推演（精确让球匹配） ==================

def four_step_predict(home, away, match_type, home_elo, away_elo, home_xg, away_xg, home_form, away_form,
                      handicap_num, patches):
    elo_diff = home_elo - away_elo
    xg_sum = home_xg + away_xg

    if patches.get("draw_to_advance") == "home":
        draw_boost = 0.15
        xg_sum = xg_sum * 0.9
    elif patches.get("draw_to_advance") == "away":
        draw_boost = 0.15
        xg_sum = xg_sum * 0.9
    else:
        draw_boost = 0.0

    if patches.get("odds_up", False):
        xg_sum = max(0.5, xg_sum - 0.5)

    if match_type == "final":
        xg_sum = xg_sum * 0.85
    elif match_type == "knockout":
        xg_sum = xg_sum * 0.9
    elif match_type == "slaughter":
        xg_sum = xg_sum * 1.1

    # ----- 第一步：胜平负 -----
    if abs(elo_diff) > 150:
        if elo_diff > 0:
            dir_primary = "主胜"; dir_secondary = "平局"
        else:
            dir_primary = "客胜"; dir_secondary = "平局"
    elif abs(elo_diff) >= 50:
        if home_xg > away_xg and home_form >= away_form:
            dir_primary = "主胜"; dir_secondary = "平局"
        elif away_xg > home_xg and away_form >= home_form:
            dir_primary = "客胜"; dir_secondary = "平局"
        else:
            dir_primary = "平局"
            dir_secondary = "主胜" if home_xg > away_xg else "客胜"
    else:
        dir_primary = "平局"
        dir_secondary = "主胜" if home_xg > away_xg else "客胜"

    if draw_boost > 0:
        if dir_primary != "平局" and abs(home_xg - away_xg) < 0.3:
            dir_primary, dir_secondary = "平局", dir_primary

    if match_type in ["final", "knockout"]:
        if dir_primary == "主胜" and abs(home_xg - away_xg) < 0.5:
            dir_primary, dir_secondary = "平局", dir_primary

    # ----- 第三步：总进球 -----
    if xg_sum >= 3.5:
        goal_primary = "3"; goal_secondary = "4"
    elif xg_sum >= 2.5:
        goal_primary = "2"; goal_secondary = "3"
    elif xg_sum >= 1.5:
        goal_primary = "1"; goal_secondary = "2"
    else:
        goal_primary = "0"; goal_secondary = "1"
    if xg_sum >= 4.0 and goal_primary == "3":
        goal_secondary = "4"
    if xg_sum >= 5.0 and goal_primary == "4":
        goal_secondary = "5"
    if xg_sum >= 6.5:
        goal_primary = "5"; goal_secondary = "7+"

    # ----- 第四步：生成比分首推和次推（严格匹配让球结果） -----
    # 将 goals 转为整数
    goal_prim_int = int(goal_primary) if goal_primary.isdigit() else 0
    goal_sec_int = int(goal_secondary) if goal_secondary.isdigit() else 0

    def generate_score(dir, goals_int, hc_num, is_primary=True):
        # 根据方向和让球数生成符合净胜要求的比分
        if dir == "主胜":
            if hc_num >= 0:  # 主队让球
                if hc_num == 1:
                    if goals_int >= 2:
                        return "2:0" if goals_int == 2 else "3:0" if goals_int == 3 else "3:1"
                    else:
                        return "1:0"
                elif hc_num == 2:
                    if goals_int >= 3:
                        return "3:0" if goals_int == 3 else "4:0" if goals_int == 4 else "4:1"
                    else:
                        return "2:0" if goals_int == 2 else "1:0"
                else:  # 其他让球数，简化
                    return "2:0" if goals_int >= 2 else "1:0"
            else:  # 主队受让
                if goals_int >= 2:
                    return "2:1" if goals_int == 2 else "3:1" if goals_int == 3 else "3:2"
                else:
                    return "1:0"
        elif dir == "平局":
            return "1:1" if goals_int >= 2 else "0:0" if goals_int == 0 else "1:1"
        else:  # 客胜
            if hc_num >= 0:  # 主队让球
                # 客胜时，让负需要净胜≥2
                if goals_int >= 2:
                    return "0:2" if goals_int == 2 else "0:3" if goals_int == 3 else "1:3"
                else:
                    # 若进球太少，强制2球
                    return "0:2"
            else:  # 主队受让
                if goals_int >= 2:
                    return "0:2" if goals_int == 2 else "0:3" if goals_int == 3 else "1:3"
                else:
                    return "0:1"  # 客胜1球，让平

    score_primary = generate_score(dir_primary, goal_prim_int, handicap_num, True)
    score_secondary = generate_score(dir_primary, goal_sec_int, handicap_num, False)

    # 调整次推比分与方向次推一致
    def adjust_score_by_dir(score, dir, hc_num):
        h, a = map(int, score.split(':'))
        if dir == "主胜":
            if h <= a:
                return "1:0" if a == 0 else "2:1"
        elif dir == "客胜":
            if h >= a:
                return "0:1" if a == 1 else "0:2"
        elif dir == "平局":
            if h != a:
                return "1:1"
        return score
    score_secondary = adjust_score_by_dir(score_secondary, dir_secondary, handicap_num)

    # 根据比分计算让球结果
    def calc_handicap(score, handicap):
        h, a = map(int, score.split(':'))
        if handicap >= 0:
            virtual_h = h - handicap
            virtual_a = a
        else:
            virtual_h = h + (-handicap)
            virtual_a = a
        if virtual_h > virtual_a:
            return "让胜"
        elif virtual_h == virtual_a:
            return "让平"
        else:
            return "让负"

    handicap_primary = calc_handicap(score_primary, handicap_num)
    handicap_secondary = calc_handicap(score_secondary, handicap_num)

    # 更新总进球为实际比分总和
    g_prim = str(sum(map(int, score_primary.split(':'))))
    g_sec = str(sum(map(int, score_secondary.split(':'))))

    return {
        "direction_primary": dir_primary,
        "direction_secondary": dir_secondary,
        "handicap_primary": handicap_primary,
        "handicap_secondary": handicap_secondary,
        "goal_primary": g_prim,
        "goal_secondary": g_sec,
        "score_primary": score_primary,
        "score_secondary": score_secondary,
        "lam_h": home_xg,
        "lam_a": away_xg,
    }

# ================== 界面UI ==================

st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .result-box { background-color:#ffffff; border-radius:10px; padding:15px; margin:10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .yao-box { background-color:#f8f9fa; border-left: 4px solid #2e86c1; padding:10px; margin:5px 0; }
    .four-step { background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; border-radius: 10px; padding: 20px; margin: 10px 0; }
    .step-card { background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin: 8px 0; }
    .step-number { font-size: 20px; font-weight: bold; color: #f1c40f; }
    .step-primary { font-size: 22px; font-weight: bold; color: #2ecc71; }
    .step-secondary { font-size: 18px; color: #f39c12; }
</style>
""", unsafe_allow_html=True)

st.image("https://img.icons8.com/color/96/000000/football2.png", width=80)
st.title("⚽ V6.0 足球预测 · 最终版")
st.caption("卦象由队伍笔画决定 · 比赛性质影响状态 · 让球/比分/总进球严格统一")

# ---------- 输入区 ----------
with st.expander("📋 球队与赔率基础数据", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("主队")
        home = st.text_input("球队名称", placeholder="如：巴西", key="home")
        home_elo = st.number_input("ELO", value=2000, step=10, key="home_elo")
        home_xg = st.number_input("xG", value=1.5, step=0.1, key="home_xg")
        home_form = st.number_input("近5场胜率", value=0.6, step=0.05, key="home_form")
    with col2:
        st.subheader("客队")
        away = st.text_input("球队名称", placeholder="如：日本", key="away")
        away_elo = st.number_input("ELO", value=1900, step=10, key="away_elo")
        away_xg = st.number_input("xG", value=1.2, step=0.1, key="away_xg")
        away_form = st.number_input("近5场胜率", value=0.5, step=0.05, key="away_form")

    match_date = st.date_input("比赛日期", value=datetime.date.today())
    match_time_sel = st.time_input("比赛时间（开球时刻）", value=datetime.time(0, 0))
    match_time = datetime.datetime.combine(match_date, match_time_sel)

    st.subheader("赔率数据（可选）")
    col_odds = st.columns(3)
    with col_odds[0]:
        st.caption("胜平负")
        odds_h = st.number_input("主胜", value=2.0, step=0.1, min_value=1.0, key="odds_h")
        odds_d = st.number_input("平局", value=3.2, step=0.1, min_value=1.0, key="odds_d")
        odds_a = st.number_input("客胜", value=3.5, step=0.1, min_value=1.0, key="odds_a")
    with col_odds[1]:
        st.caption("让球胜平负")
        # 使用 format_func 显示清晰的主队让/受让
        handicap_num = st.selectbox(
            "让球数",
            options=[-3, -2, -1, 0, 1, 2, 3],
            format_func=lambda x: f"主队{'+' if x < 0 else '-'}{abs(x)}" if x != 0 else "平手",
            index=2,  # 默认为主队-1
            key="handicap"
        )
        st.caption(f"当前选择：{'主队让' + str(handicap_num) + '球' if handicap_num > 0 else '主队受让' + str(-handicap_num) + '球' if handicap_num < 0 else '平手'}")
        odds_hc_h = st.number_input("让胜赔率", value=3.5, step=0.1, min_value=1.0, key="hc_h")
        odds_hc_d = st.number_input("让平赔率", value=3.4, step=0.1, min_value=1.0, key="hc_d")
        odds_hc_a = st.number_input("让负赔率", value=2.0, step=0.1, min_value=1.0, key="hc_a")
    with col_odds[2]:
        st.caption("总进球/比分（已内嵌）")

# ---------- 补丁和比赛性质 ----------
with st.expander("🔧 补丁设置 & 比赛性质", expanded=False):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        home_rotation = st.number_input("主队轮换人数（≥4触发补丁①）", min_value=0, max_value=11, value=0, step=1)
        away_rotation = st.number_input("客队轮换人数（≥4触发补丁①）", min_value=0, max_value=11, value=0, step=1)
        draw_to_advance = st.selectbox("打平即可出线（补丁②）", options=["无", "主队", "客队"], index=0)
        odds_up = st.checkbox("大小球盘口升盘（补丁③诱大警报）", value=False)
    with col_p2:
        st.caption("补丁④（半场落后≥2球）需临场数据，暂不设开关。")
        st.caption("补丁⑤（屠杀局）根据xG和比赛性质自动调整。")

match_type = st.selectbox("比赛性质（影响状态参数）", ["常规", "淘汰赛", "决赛", "保级/出线生死战", "强弱悬殊"])

if st.button("🔮 开始推演", use_container_width=True):
    if not home or not away:
        st.warning("请填写主客队名称")
    else:
        match_type_map = {
            "常规": "general", "淘汰赛": "knockout", "决赛": "final",
            "保级/出线生死战": "draw", "强弱悬殊": "slaughter"
        }
        mt_key = match_type_map[match_type]

        patches = {
            "home_rotation": home_rotation,
            "away_rotation": away_rotation,
            "draw_to_advance": "none" if draw_to_advance == "无" else ("home" if draw_to_advance == "主队" else "away"),
            "odds_up": odds_up,
        }

        # ========== 第一阶段：卦象分析 ==========
        st.divider()
        st.markdown("## 🔮 第一阶段：卦象分析（笔画起卦）")
        
        gua_analysis = full_gua_analysis(home, away, mt_key)
        gua_info = gua_analysis["gua_info"]
        yao_details = gua_analysis["yao_details"]
        bing_yao = gua_analysis["bing_yao"]

        st.caption(f"起卦依据：主队“{home}”笔画数 {gua_info['home_strokes']}，客队“{away}”笔画数 {gua_info['away_strokes']}，总笔画 {gua_info['total_strokes']}，动爻 {gua_info['moving_yao']}")

        col_g1, col_g2, col_g3 = st.columns(3)
        col_g1.metric("本卦", f"{gua_info['base'][0]}{gua_info['base'][1]}（{gua_info['base_name']}）")
        col_g2.metric("变卦", f"{gua_info['change'][0]}{gua_info['change'][1]}（{gua_info['change_name']}）")
        col_g3.metric("互卦", f"{gua_info['inter'][0]}{gua_info['inter'][1]}（{gua_info['inter_name']}）")

        st.write(f"**体用生克**：{gua_info['ti_yong']}  （体卦{gua_info['body']}五行{gua_info['body_wuxing']}，用卦{gua_info['use']}五行{gua_info['use_wuxing']}）")
        st.write(f"**世应**：世爻在{LIUYAO_WEI[gua_info['shi_yao']]}（主队），应爻在{LIUYAO_WEI[gua_info['ying_yao']]}（客队）")

        base_key = gua_info["base_key"]
        if base_key in GUA_DICT:
            g = GUA_DICT[base_key]
            st.markdown(f"**📖 本卦【{g['name']}】卦辞**：{g['gua_ci']}")
            st.markdown(f"**象辞**：{g['xiang_ci']}")

        st.write("**💊 病药体系**：" + bing_yao['病药'])
        st.write(f"用神：{bing_yao['用神']} | 忌神：{bing_yao['忌神']} | 元神：{bing_yao['元神']} | 仇神：{bing_yao['仇神']}")

        # ========== 第二阶段：古代杂占 ==========
        st.divider()
        st.markdown("## 📜 第二阶段：古代杂占")
        
        shichen = get_shichen_from_time(match_time)
        shichen_time = ['23-1','1-3','3-5','5-7','7-9','9-11','11-13','13-15','15-17','17-19','19-21','21-23']
        st.write(f"**比赛时辰**：{shichen}时（{shichen_time[SHICHEN.index(shichen)]}）")
        
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

        # ========== 第三阶段：量化计算 ==========
        st.divider()
        st.markdown("## 📊 第三阶段：量化计算")

        lam_h, lam_a = compute_lam(home_elo, away_elo, home_xg, away_xg, home_form, away_form, patches, mt_key)
        home_prob = 0
        draw_prob = 0
        away_prob = 0
        for h in range(0, 5):
            for a in range(0, 5):
                prob = poisson_prob(lam_h, h) * poisson_prob(lam_a, a)
                if h > a: home_prob += prob
                elif h == a: draw_prob += prob
                else: away_prob += prob
        st.write(f"**λ主**：{lam_h:.2f}，**λ客**：{lam_a:.2f}")
        st.write(f"**主胜概率**：{home_prob:.1%} | **平局概率**：{draw_prob:.1%} | **客胜概率**：{away_prob:.1%}")

        if odds_h > 0 and odds_d > 0 and odds_a > 0:
            ev_h = (home_prob * odds_h) - 1
            ev_d = (draw_prob * odds_d) - 1
            ev_a = (away_prob * odds_a) - 1
            st.caption(f"主胜EV：{ev_h:.2f} | 平局EV：{ev_d:.2f} | 客胜EV：{ev_a:.2f}")

        # ========== 第四阶段：四层推演 ==========
        st.divider()
        st.markdown("## 🎯 第四阶段：四层推演结论")

        result = four_step_predict(
            home, away, mt_key,
            home_elo, away_elo,
            home_xg, away_xg,
            home_form, away_form,
            handicap_num,
            patches
        )

        # 让球显示文字（与下拉框一致）
        if handicap_num > 0:
            handicap_desc = f"主队-{handicap_num}（主队让{handicap_num}球）"
        elif handicap_num < 0:
            handicap_desc = f"主队+{-handicap_num}（主队受让{-handicap_num}球）"
        else:
            handicap_desc = "平手"

        st.markdown(f"""
        <div class="four-step">
            <div class="step-card">
                <span class="step-number">① 胜平负</span><br>
                <span class="step-primary">首推：{result['direction_primary']}</span><br>
                <span class="step-secondary">次推：{result['direction_secondary']}</span>
            </div>
            <div class="step-card">
                <span class="step-number">② 让球胜平负（{handicap_desc}）</span><br>
                <span class="step-primary">首推：{result['handicap_primary']}</span><br>
                <span class="step-secondary">次推：{result['handicap_secondary']}</span>
            </div>
            <div class="step-card">
                <span class="step-number">③ 总进球数</span><br>
                <span class="step-primary">首推：{result['goal_primary']}球</span><br>
                <span class="step-secondary">次推：{result['goal_secondary']}球</span>
            </div>
            <div class="step-card">
                <span class="step-number">④ 比分（精准）</span><br>
                <span class="step-primary">首推：{result['score_primary']}</span><br>
                <span class="step-secondary">次推：{result['score_secondary']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 补丁状态
        st.caption("补丁状态：")
        if home_rotation >= 4 or away_rotation >= 4:
            st.caption("✅ 补丁①（轮换）触发")
        if draw_to_advance != "无":
            st.caption("✅ 补丁②（打平即可出线）触发")
        if odds_up:
            st.caption("✅ 补丁③（诱大警报）触发")
        if home_xg >= 2.5 and away_xg <= 0.8:
            st.caption("✅ 补丁⑤（屠杀局）触发")

        # ========== 六爻逐爻详解 ==========
        with st.expander("🔎 六爻逐爻详解（点击展开）", expanded=True):
            for i, yao in enumerate(yao_details):
                st.markdown(f"**{yao['position']}**  (爻位：{yao['gong']})")
                st.caption(f"五行：{yao['wuxing']}，六亲：{yao['liuqin']}（{LIUQIN_MAP.get(yao['liuqin'], '')}），吉凶：{yao['jixiong']}")
                st.write(yao['text'])
                st.markdown("---")

        st.divider()
        st.caption("心源心法：爻象定真，共振取象，三象合一。V6.0 最终版")
