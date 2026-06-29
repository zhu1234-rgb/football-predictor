# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import math
import datetime
import re
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import xgboost as xgb

st.set_page_config(page_title="V6.0 足球预测 · 2026 xG版", page_icon="⚽", layout="centered", initial_sidebar_state="collapsed")

if 'predict_history' not in st.session_state:
    st.session_state.predict_history = []

@st.cache_data
def load_team_data():
    return {
        "阿根廷": {"elo": 2148, "xg": 1.43, "form": 0.67, "group_goals": 7, "group_rank": 1},
        "巴西": {"elo": 2099, "xg": 1.64, "form": 0.67, "group_goals": 6, "group_rank": 1},
        "哥伦比亚": {"elo": 2004, "xg": 2.00, "form": 0.67, "group_goals": 5, "group_rank": 1},
        "厄瓜多尔": {"elo": 1902, "xg": 1.97, "form": 0.67, "group_goals": 6, "group_rank": 2},
        "巴拉圭": {"elo": 1815, "xg": 0.87, "form": 0.33, "group_goals": 2, "group_rank": 2},
        "乌拉圭": {"elo": 1841, "xg": 1.96, "form": 0.33, "group_goals": 3, "group_rank": 2},
        "西班牙": {"elo": 2144, "xg": 2.28, "form": 0.67, "group_goals": 8, "group_rank": 1},
        "法国": {"elo": 2123, "xg": 2.06, "form": 0.67, "group_goals": 10, "group_rank": 1},
        "英格兰": {"elo": 2038, "xg": 2.10, "form": 0.67, "group_goals": 8, "group_rank": 1},
        "葡萄牙": {"elo": 1990, "xg": 1.53, "form": 0.33, "group_goals": 4, "group_rank": 2},
        "荷兰": {"elo": 1980, "xg": 1.89, "form": 0.67, "group_goals": 10, "group_rank": 1},
        "挪威": {"elo": 1918, "xg": 1.47, "form": 0.67, "group_goals": 8, "group_rank": 1},
        "德国": {"elo": 1916, "xg": 2.19, "form": 0.67, "group_goals": 10, "group_rank": 1},
        "瑞士": {"elo": 1914, "xg": 1.92, "form": 0.67, "group_goals": 7, "group_rank": 1},
        "克罗地亚": {"elo": 1905, "xg": 1.14, "form": 0.33, "group_goals": 3, "group_rank": 2},
        "比利时": {"elo": 1884, "xg": 2.33, "form": 0.67, "group_goals": 8, "group_rank": 1},
        "奥地利": {"elo": 1836, "xg": 1.25, "form": 0.33, "group_goals": 4, "group_rank": 2},
        "瑞典": {"elo": 1742, "xg": 1.74, "form": 0.33, "group_goals": 4, "group_rank": 2},
        "波黑": {"elo": 1622, "xg": 1.17, "form": 0.33, "group_goals": 2, "group_rank": 3},
        "摩洛哥": {"elo": 1877, "xg": 1.78, "form": 0.67, "group_goals": 5, "group_rank": 1},
        "塞内加尔": {"elo": 1842, "xg": 1.93, "form": 0.67, "group_goals": 6, "group_rank": 1},
        "科特迪瓦": {"elo": 1743, "xg": 1.38, "form": 0.33, "group_goals": 3, "group_rank": 2},
        "阿尔及利亚": {"elo": 1785, "xg": 1.54, "form": 0.33, "group_goals": 4, "group_rank": 2},
        "埃及": {"elo": 1742, "xg": 1.50, "form": 0.33, "group_goals": 4, "group_rank": 2},
        "加纳": {"elo": 1575, "xg": 0.68, "form": 0.33, "group_goals": 2, "group_rank": 3},
        "南非": {"elo": 1575, "xg": 1.13, "form": 0.33, "group_goals": 2, "group_rank": 2},
        "民主刚果": {"elo": 1712, "xg": 1.27, "form": 0.33, "group_goals": 1, "group_rank": 3},
        "佛得角": {"elo": 1622, "xg": 1.07, "form": 0.33, "group_goals": 1, "group_rank": 3},
        "日本": {"elo": 1910, "xg": 1.27, "form": 0.67, "group_goals": 4, "group_rank": 2},
        "澳大利亚": {"elo": 1800, "xg": 1.17, "form": 0.33, "group_goals": 2, "group_rank": 2},
        "墨西哥": {"elo": 1912, "xg": 1.36, "form": 0.33, "group_goals": 4, "group_rank": 2},
        "美国": {"elo": 1781, "xg": 1.78, "form": 0.67, "group_goals": 6, "group_rank": 1},
        "加拿大": {"elo": 1748, "xg": 2.35, "form": 0.67, "group_goals": 9, "group_rank": 1},
    }
TEAM_DATA = load_team_data()

BAGUA_WUXING = {"乾": "金", "兑": "金", "离": "火", "震": "木", "巽": "木", "坎": "水", "艮": "土", "坤": "土"}
BAGUA_LEIXIANG = {"乾": "天", "兑": "泽", "离": "火", "震": "雷", "巽": "风", "坎": "水", "艮": "山", "坤": "地"}
LIUYAO_WEI = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
LIUYAO_GONG = ["震（足）", "离（眼/心）", "艮（手/肩）", "巽（股/财）", "坎（耳/肾）", "兑（口/肺）"]
LIUQIN_MAP = {"父母": "教练组/战术体系/文书", "官鬼": "中场控制/裁判/领导", "妻财": "前锋/射手/资金", "兄弟": "队友/对手/竞争", "子孙": "替补/年轻球员/福神"}
SHICHEN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

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

MIAN_RE = {"子": "主喜庆事，主得财。", "丑": "主有烦恼、忧愁之事。", "寅": "主有客来，大吉。", "卯": "主有酒食及外人至。",
           "辰": "主有远客喜相逢，吉。", "巳": "主有急事人来见。", "午": "主有亲人相见。", "未": "主有词讼口舌是非。",
           "申": "主有高人来会相见。", "酉": "主有高人来会相见。", "戌": "主有酒食事。", "亥": "主有词讼不宁之事。"}
YAN_TIAO = {"子": {"左": "有贵人", "右": "有酒食"}, "丑": {"左": "有犹疑", "右": "有人思"}, "寅": {"左": "远人来", "右": "喜庆事"},
            "卯": {"左": "贵人来", "右": "平安吉"}, "辰": {"左": "客人来", "右": "损害事"}, "巳": {"左": "主酒食", "右": "主凶事"},
            "午": {"左": "主饮食", "右": "主凶事"}, "未": {"左": "主吉昌", "右": "主小喜"}, "申": {"左": "有财利", "右": "有女思"},
            "酉": {"左": "有客至", "右": "主亲来"}, "戌": {"左": "主酒食", "右": "主聚会"}, "亥": {"左": "有客来", "右": "主官非"}}
ER_RE = {"子": "主有僧道来相议事。", "丑": "主有喜事临身，大吉。", "寅": "主有酒食相会，大吉。", "卯": "主有远人来相见，吉。",
         "辰": "主有财喜大通达，吉。", "巳": "主有失财物事，不利。", "午": "主有喜气事来，大吉。", "未": "主有客来相求之事。",
         "申": "主有酒食宴乐事，吉。", "酉": "主有人来言婚姻事。", "戌": "主有争讼口舌之事。", "亥": "主有官非词讼之事。"}
ER_MING = {"子": {"左": "女思", "右": "失财"}, "丑": {"左": "口舌", "右": "争讼"}, "寅": {"左": "失财", "右": "心急"},
           "卯": {"左": "坎坷", "右": "客至"}, "辰": {"左": "远行", "右": "客至"}, "巳": {"左": "凶事", "右": "大吉"},
           "午": {"左": "远信", "右": "亲来"}, "未": {"左": "饮食", "右": "人来"}, "申": {"左": "行人", "右": "大吉"},
           "酉": {"左": "失财", "右": "大吉"}, "戌": {"左": "酒食", "右": "客至"}, "亥": {"左": "大吉", "右": "酒食"}}
JIN_MING = {"子": "主六畜平安，大吉。", "丑": "主家宅定、富贵，大吉。", "寅": "主家宅凶、怪事，大凶。", "卯": "主家门祸事至，大凶。",
            "辰": "主有田蚕收成，大吉。", "巳": "主福至财来，大吉。", "午": "主官事消散，大吉昌。", "未": "主凶祸不祥之事，不利。",
            "申": "主远客行人来，大吉。", "酉": "主远客行人来，大吉。", "戌": "主小喜、亨通，大吉。", "亥": "主官非词讼有理，吉。"}
HUO_YI = {"子": "妻有外思、烦闷之事。", "丑": "主女心向外，大不吉利。", "寅": "主得小喜，平安，大吉利。", "卯": "主得财帛、亨通之兆。",
          "辰": "主忧心、损男小口，灾。", "巳": "主喜事，酒食相逢。", "午": "主相争、官非、大灾事。", "未": "主财喜昌盛之兆。",
          "申": "主财帛、会合事，吉。", "酉": "主凶灾、丧服之兆。", "戌": "主忧心、终得理之兆。", "亥": "主身疾病、不祥之兆。"}
QUAN_OU = {"子": "主妇人不时争斗。", "丑": "主有忧心烦闷之事。", "寅": "望天嘔，主进财，大吉利。", "卯": "望天嘔，必得财，大吉。",
           "辰": "主喜事至，大亨通，吉。", "巳": "主亲人想念，信至。", "午": "主逢酒食宴会，大吉。", "未": "主家中内外破财。",
           "申": "主家宅有小口之忧。", "酉": "主加官进禄，得财，吉。", "戌": "主口舌之事，大凶。", "亥": "主官非词讼之事。"}
YI_LIU = {"子": "男主酒食，女主亲事。", "丑": "主愁思破财之事。", "寅": "主进财，大吉利。", "卯": "主酒食，交友，相会，吉。",
          "辰": "主失财、忧灾、疾病。", "巳": "女外思，男无凶。", "午": "主远人至，得利，大吉。", "未": "主血光之灾，化凶为吉。",
          "申": "主得外财，出入大吉。", "酉": "主客至、破财，不利。", "戌": "主词讼、得财，大吉。", "亥": "主见官、得财，大吉。"}
PEN_KE = {"子": "主逢吉人，酒食相会。", "丑": "主女人思，客来求事。", "寅": "主女人相遇，有酒食。", "卯": "主有财、喜，有客来。",
          "辰": "主有酒食，大吉利。", "巳": "主吉人来求财，喜。", "午": "主客来、酒会、宴饮。", "未": "主酒食相会合之事。",
          "申": "主夜梦惊恐，酒食不利。", "酉": "主妇人来求请问事。", "戌": "主妇人思会和合事。", "亥": "主虚惊，反得吉利。"}
ROU_CHAN = {"子": "主尊长人来，大吉。", "丑": "主吉祥临身，大吉。", "寅": "主凶事，化凶为吉。", "卯": "主得财事，大吉利。",
            "辰": "主凶恶临身，大凶。", "巳": "主宾友相见，大吉利。", "午": "主忧疑事，自身吉。", "未": "主喜事，自身大吉。",
            "申": "主口舌，解之则吉。", "酉": "主因财起祸事，大凶。", "戌": "主行人远来，大吉。", "亥": "主大吉利、喜之事。"}
XIN_JING = {"子": "主有女子思喜事至。", "丑": "主有恶事临门，大凶。", "寅": "主有客来饮食，大吉。", "卯": "主有酒食事及外人来。",
            "辰": "主有成合喜事，大吉利。", "巳": "主有女思及喜事至。", "午": "主有酒食自来，大吉。", "未": "主有女思念，大吉。",
            "申": "主有大喜之事至，大吉。", "酉": "主有喜信至，大吉庆。", "戌": "主有贵人即至，大吉。", "亥": "主有恶梦，大凶。"}
QUE_ZAO = {"子": "主有远亲人至，大吉。", "丑": "主有喜庆之事，大吉。", "寅": "主有词讼之事，小吉。", "卯": "主有酒食财喜，大吉。",
           "辰": "主有远行人回家，吉。", "巳": "主有喜事降临，大吉。", "午": "主有疾病，求神安，吉。", "未": "主有六畜不见之事。",
           "申": "主有喜庆事，大吉昌。", "酉": "主有坎坷不安之事。", "戌": "主有财帛亨通，大吉。", "亥": "主有口舌争斗之事。"}

def get_wuxing(gua):
    return BAGUA_WUXING.get(gua, "土")

def get_liuqin(body_wuxing, yao_wuxing):
    r = {("金", "木"): "官鬼", ("金", "火"): "妻财", ("金", "土"): "父母", ("金", "金"): "兄弟",
         ("木", "金"): "妻财", ("木", "火"): "子孙", ("木", "土"): "官鬼", ("木", "木"): "兄弟",
         ("水", "金"): "父母", ("水", "火"): "官鬼", ("水", "土"): "妻财", ("水", "木"): "子孙",
         ("火", "金"): "官鬼", ("火", "木"): "父母", ("火", "土"): "子孙", ("火", "火"): "兄弟",
         ("土", "金"): "子孙", ("土", "木"): "妻财", ("土", "水"): "官鬼", ("土", "火"): "父母"}
    return r.get((body_wuxing, yao_wuxing), "比和")

def build_stroke_dict():
    b = {"德": 15, "国": 8, "西": 6, "班": 10, "牙": 4, "南": 9, "非": 8, "加": 5, "拿": 10, "大": 3,
         "巴": 4, "阿": 7, "根": 10, "廷": 6, "法": 8, "意": 13, "利": 7, "英": 8, "格": 10, "兰": 5,
         "葡": 12, "萄": 11, "荷": 10, "比": 4, "瑞": 13, "士": 3, "丹": 4, "麦": 7, "挪": 10, "威": 9,
         "捷": 11, "克": 7, "奥": 12, "地": 6, "匈": 6, "希": 7, "腊": 12, "俄": 9, "罗": 8, "马": 3, "尼": 5,
         "日": 4, "本": 5, "韩": 12, "伊": 6, "朗": 10, "沙": 7, "特": 10, "拉": 8, "伯": 7, "墨": 15, "哥": 10,
         "美": 9, "乌": 4, "圭": 6, "卡": 5, "塔": 12, "尔": 5, "塞": 13, "内": 4, "亚": 6, "洪": 9, "都": 10,
         "斯": 12, "厄": 4, "瓜": 5, "多": 6, "智": 12, "秘": 10, "鲁": 12, "委": 8, "新": 13, "澳": 15,
         "台": 5, "港": 12, "门": 3, "朝": 12, "鲜": 14, "越": 12, "泰": 10, "印": 5, "度": 9, "菲": 11,
         "律": 9, "宾": 10, "坡": 8, "来": 7, "达": 6, "黎": 15, "嫩": 14, "以": 4, "色": 6, "列": 6, "约": 6,
         "旦": 5, "叙": 9, "曼": 11, "苏": 7, "中": 4, "刚": 6, "果": 8, "佛": 7, "角": 7, "克": 7,
         "罗": 8, "地": 6, "尼": 5, "亚": 6, "利": 7, "比": 4, "时": 7, "间": 7, "赛": 17, "预": 13,
         "测": 10, "优": 6, "化": 4, "版": 8, "队": 4, "员": 7, "教": 11, "练": 8, "裁": 12, "判": 7,
         "门": 3, "将": 9, "前": 9, "锋": 12, "中": 4, "后": 6, "卫": 3, "守": 6, "攻": 7, "防": 6,
         "战": 9, "术": 5, "体": 7, "能": 10, "心": 4, "理": 11, "气": 4, "势": 8}
    return b
STROKE_DICT = build_stroke_dict()

def count_strokes(name):
    total = 0
    for c in name:
        total += STROKE_DICT.get(c, 5)
    return total

def get_inter_gua(upper, lower):
    gm = {"乾": [1, 1, 1], "兑": [0, 1, 1], "离": [1, 0, 1], "震": [0, 0, 1],
          "巽": [1, 1, 0], "坎": [0, 1, 0], "艮": [1, 0, 0], "坤": [0, 0, 0]}
    ub = gm[upper]
    lb = gm[lower]
    full = lb + ub
    li = full[1:4]
    ui = full[2:5]
    rev = {tuple(v): k for k, v in gm.items()}
    return rev[tuple(ui)], rev[tuple(li)]

def generate_gua_info(home, away):
    ch = re.sub(r'[^\u4e00-\u9fa5]', '', home)
    ca = re.sub(r'[^\u4e00-\u9fa5]', '', away)
    hs = count_strokes(ch)
    as_ = count_strokes(ca)
    ts = hs + as_
    un = hs % 8
    if un == 0:
        un = 8
    ln = as_ % 8
    if ln == 0:
        ln = 8
    my = ts % 6
    if my == 0:
        my = 6
    ntg = {1: "乾", 2: "兑", 3: "离", 4: "震", 5: "巽", 6: "坎", 7: "艮", 8: "坤"}
    upper = ntg[un]
    lower = ntg[ln]
    rev = {"乾": "坤", "坤": "乾", "震": "巽", "巽": "震", "坎": "离", "离": "坎", "艮": "兑", "兑": "艮"}
    cu = rev.get(upper, upper)
    cl = rev.get(lower, lower)
    iu, il = get_inter_gua(upper, lower)
    body = upper
    use = lower
    bw = get_wuxing(body)
    uw = get_wuxing(use)
    if bw == uw:
        ty = "比和（平局相）"
    elif (bw == "木" and uw == "土") or (bw == "火" and uw == "金") or (bw == "土" and uw == "水") or (bw == "金" and uw == "木") or (bw == "水" and uw == "火"):
        ty = "体克用（主队制胜）"
    elif (uw == "木" and bw == "土") or (uw == "火" and bw == "金") or (uw == "土" and bw == "水") or (uw == "金" and bw == "木") or (uw == "水" and bw == "火"):
        ty = "用克体（客队制胜）"
    else:
        ty = "相生（平和）"
    sy = my - 1
    ey = (sy + 4) % 6
    return {"base": (upper, lower), "base_key": upper + lower, "base_name": f"{BAGUA_LEIXIANG[upper]}{BAGUA_LEIXIANG[lower]}",
            "change": (cu, cl), "change_name": f"{BAGUA_LEIXIANG[cu]}{BAGUA_LEIXIANG[cl]}",
            "inter": (iu, il), "inter_name": f"{BAGUA_LEIXIANG[iu]}{BAGUA_LEIXIANG[il]}",
            "body": body, "use": use, "body_wuxing": bw, "use_wuxing": uw, "ti_yong": ty,
            "shi_yao": sy, "ying_yao": ey, "moving_yao": my,
            "home_strokes": hs, "away_strokes": as_, "total_strokes": ts}

def analyze_yao(gua_info, match_type, home, away):
    bw = gua_info["body_wuxing"]
    wc = ["木", "火", "土", "金", "水", "木"]
    details = []
    for i in range(6):
        yw = wc[i]
        lq = get_liuqin(bw, yw)
        if lq == "父母":
            jx = "吉（得生）" if bw in ["火", "土"] else "中"
        elif lq == "官鬼":
            jx = "凶（受克）" if bw in ["金", "木"] else "凶"
        elif lq == "妻财":
            jx = "吉（得财）"
        elif lq == "兄弟":
            jx = "中（竞争）"
        else:
            jx = "平（比和）"
        if i == 0:
            txt = f"**初爻（根基）**：{home}的初始战术部署与防守稳固性。此爻为全卦之基，主队开局状态与第一道防线。宜静不宜动，静则稳，动则生变。"
        elif i == 1:
            txt = f"**二爻（节奏）**：中场控制权与比赛节奏。二爻为内卦之中，主中场调度。若此爻得位，则{home}能掌控比赛节奏；若失位，则易被{away}反制。"
        elif i == 2:
            txt = f"**三爻（攻势）**：{home}的前锋线效率与威胁球能力。三爻为内卦之极，主攻端。此爻发动则攻势凌厉，然亦需防急于求成反被偷袭。"
        elif i == 3:
            txt = f"**四爻（防守）**：{home}的防线稳固性及门将发挥。四爻为外卦之始，主守端。此爻旺相则后卫线滴水不漏，衰弱则恐有闪失。"
        elif i == 4:
            txt = f"**五爻（气势）**：{home}的球队士气与教练临场调度。五爻为君位，主主教练与核心球员。此爻当权则全队气势如虹，受克则军心涣散。"
        else:
            txt = f"**上爻（终局）**：比赛最终走向与运气成分。上爻为天位，主结果与偶然因素。此爻临吉则好运相伴，临凶则恐有意外变数。"
            if match_type in ["final", "knockout"]:
                txt += " 加时赛或点球大战的可能性需纳入考虑。"
        if lq == "官鬼":
            if match_type == "knockout":
                txt += " 官鬼在淘汰赛主压力，宜有子孙解忧。"
            elif match_type == "final":
                txt += " 官鬼在决赛主心理压力，谁先放下包袱谁占优。"
            else:
                txt += f" 官鬼临爻，{away}的中场施压或裁判尺度可能成为关键变量。"
        elif lq == "妻财":
            txt += f" 妻财临爻，{home}的锋线终结能力将直接决定比分。"
        elif lq == "兄弟":
            txt += f" 兄弟临爻，两队中场绞杀激烈，第二落点的争夺至关重要。"
        elif lq == "子孙":
            txt += f" 子孙临爻，{home}的替补席或年轻球员可能成为奇兵。"
        elif lq == "父母":
            txt += f" 父母临爻，{home}的战术纪律性将主导比赛走向。"
        details.append({"position": LIUYAO_WEI[i], "wuxing": yw, "liuqin": lq, "gong": LIUYAO_GONG[i], "jixiong": jx, "text": txt})
    return details

def get_bing_yao(match_type):
    if match_type == "knockout":
        b = "淘汰赛官鬼为病，宜有子孙制之。"
    elif match_type == "final":
        b = "决赛双方皆谨慎，比和为主，病在谁先犯错。"
    elif match_type == "draw":
        b = "平局相，比和为主，病在攻守失衡。"
    elif match_type == "slaughter":
        b = "屠杀局，妻财过旺为病，宜有兄弟制财。"
    else:
        b = "卦中无动爻克用，病药不显。"
    return {"用神": "世爻（主队）", "忌神": "克用者", "元神": "生用者", "仇神": "克元神者", "病药": b}

def full_gua_analysis(home, away, match_type):
    gi = generate_gua_info(home, away)
    yd = analyze_yao(gi, match_type, home, away)
    by = get_bing_yao(match_type)
    return {"gua_info": gi, "yao_details": yd, "bing_yao": by}

def get_shichen_from_time(match_time):
    hour = match_time.hour
    return SHICHEN[(hour + 1) // 2 % 12]

def compute_lam(he, ae, hx, ax, hf, af, patches, mt):
    ef = (he - ae) / 2000 * 0.4
    xf = (hx / (hx + ax + 0.01)) * 0.4
    ff = (hf - af) * 0.1 + 0.5
    lh = max(0.3, ef + xf + ff)
    la = max(0.3, -ef + (ax / (hx + ax + 0.01)) * 0.4 + (af - hf) * 0.1 + 0.5)
    if patches.get("home_rotation", 0) >= 4:
        lh *= 0.5
    if patches.get("away_rotation", 0) >= 4:
        la *= 0.5
    if hx >= 2.0 and ax <= 1.0:
        if mt in ["final", "knockout"]:
            lh *= 1.5
        else:
            lh *= 2.0
        la *= 0.7
    return round(lh, 2), round(la, 2)

def poisson_prob(l, g):
    return math.exp(-l) * (l ** g) / math.factorial(g)

def generate_dynamic_score(dp, gi, hc, he, ae, hx, ax, hf, af):
    ed = he - ae
    xd = hx - ax
    if ed >= 200:
        e = 3.0
    elif ed >= 150:
        e = 2.5
    elif ed >= 100:
        e = 2.0
    elif ed >= 50:
        e = 1.5
    else:
        e = 1.0
    if xd >= 1.5:
        e += 0.8
    elif xd >= 1.0:
        e += 0.5
    elif xd >= 0.5:
        e += 0.3
    if xd <= -1.0:
        e -= 0.5
    elif xd <= -0.5:
        e -= 0.3
    e = round(e)
    e = max(1, min(4, e))
    if dp == "主胜":
        if hc >= 0:
            if e >= 3:
                if gi >= 3:
                    return f"{e}:0" if e >= 3 else "3:0"
                else:
                    return "2:0"
            elif e >= 2:
                return "2:0"
            else:
                return "1:0"
        else:
            if gi >= 3:
                return "2:1"
            else:
                return "1:0"
    elif dp == "客胜":
        if hc <= 0:
            if e >= 2:
                return f"0:{e}" if e >= 2 else "0:2"
            else:
                return "0:1"
        else:
            return "0:1"
    else:
        if gi >= 2:
            return "1:1"
        else:
            return "0:0"

def four_step_predict(home, away, mt, he, ae, hx, ax, hf, af, hc, patches):
    ed = he - ae
    xs = hx + ax
    if patches.get("draw_to_advance") == "home":
        db = 0.15
        xs *= 0.9
    elif patches.get("draw_to_advance") == "away":
        db = 0.15
        xs *= 0.9
    else:
        db = 0.0
    if patches.get("odds_up", False):
        xs = max(0.5, xs - 0.5)
    if mt == "final":
        xs *= 0.85
    elif mt == "knockout":
        xs *= 0.9
    elif mt == "slaughter":
        xs *= 1.1
    if abs(ed) > 150:
        if ed > 0:
            dp = "主胜"
            ds = "平局"
        else:
            dp = "客胜"
            ds = "平局"
    elif abs(ed) >= 50:
        if hx > ax and hf >= af:
            dp = "主胜"
            ds = "平局"
        elif ax > hx and af >= hf:
            dp = "客胜"
            ds = "平局"
        else:
            dp = "平局"
            ds = "主胜" if hx > ax else "客胜"
    else:
        dp = "平局"
        ds = "主胜" if hx > ax else "客胜"
    if db > 0 and abs(hx - ax) < 0.3 and dp != "平局":
        dp, ds = "平局", dp
    if mt in ["final", "knockout"] and dp == "主胜" and abs(hx - ax) < 0.5:
        dp, ds = "平局", dp
    if xs >= 3.5:
        gp = "3"
        gs = "4"
    elif xs >= 2.5:
        gp = "2"
        gs = "3"
    elif xs >= 1.5:
        gp = "1"
        gs = "2"
    else:
        gp = "0"
        gs = "1"
    if xs >= 4.0 and gp == "3":
        gs = "4"
    if xs >= 5.0 and gp == "4":
        gs = "5"
    if xs >= 6.5:
        gp = "5"
        gs = "7+"
    gpi = int(gp) if gp.isdigit() else 0
    gsi = int(gs) if gs.isdigit() else 0
    sp = generate_dynamic_score(dp, gpi, hc, he, ae, hx, ax, hf, af)
    ss = generate_dynamic_score(dp, gsi, hc, he, ae, hx, ax, hf, af)

    def adj(s, d):
        hh, aa = map(int, s.split(':'))
        if d == "主胜" and hh <= aa:
            return "1:0" if aa == 0 else "2:1"
        elif d == "客胜" and hh >= aa:
            return "0:1" if aa == 1 else "0:2"
        elif d == "平局" and hh != aa:
            return "1:1"
        return s

    ss = adj(ss, ds)

    def calc(s, hc):
        hh, aa = map(int, s.split(':'))
        if hc >= 0:
            vh = hh - hc
            va = aa
        else:
            vh = hh + (-hc)
            va = aa
        if vh > va:
            return "让胜"
        elif vh == va:
            return "让平"
        else:
            return "让负"

    hcp = calc(sp, hc)
    hcs = calc(ss, hc)
    return {"direction_primary": dp, "direction_secondary": ds, "handicap_primary": hcp, "handicap_secondary": hcs,
            "goal_primary": str(sum(map(int, sp.split(':')))), "goal_secondary": str(sum(map(int, ss.split(':')))),
            "score_primary": sp, "score_secondary": ss, "lam_h": hx, "lam_a": ax}

@st.cache_resource
def train_models():
    files = ["international-fifa-world-cup-2018-russia-matches-2018-to-2018-stats.csv",
             "international-fifa-world-cup-2022-qatar-matches-2022-to-2022-stats.csv"]
    dfs = []
    for f in files:
        if os.path.exists(f):
            dfs.append(pd.read_csv(f))
    if not dfs:
        st.warning("未找到CSV文件")
        return None, None, None, None
    df_all = pd.concat(dfs, ignore_index=True)
    cmap = {}
    for col in df_all.columns:
        cl = col.lower().strip()
        if 'home_team_name' in cl:
            cmap['home_team_name'] = col
        elif 'away_team_name' in cl:
            cmap['away_team_name'] = col
        elif 'home_team_goal_count' in cl:
            cmap['home_team_goal_count'] = col
        elif 'away_team_goal_count' in cl:
            cmap['away_team_goal_count'] = col
        elif 'home_team_shots' in cl and 'on_target' not in cl:
            cmap['home_team_shots'] = col
        elif 'away_team_shots' in cl and 'on_target' not in cl:
            cmap['away_team_shots'] = col
        elif 'home_team_shots_on_target' in cl:
            cmap['home_team_shots_on_target'] = col
        elif 'away_team_shots_on_target' in cl:
            cmap['away_team_shots_on_target'] = col
        elif 'home_team_corner_count' in cl:
            cmap['home_team_corner_count'] = col
        elif 'away_team_corner_count' in cl:
            cmap['away_team_corner_count'] = col
        elif 'home_team_possession' in cl:
            cmap['home_team_possession'] = col
        elif 'away_team_possession' in cl:
            cmap['away_team_possession'] = col
        elif 'home_team_fouls' in cl:
            cmap['home_team_fouls'] = col
        elif 'away_team_fouls' in cl:
            cmap['away_team_fouls'] = col
        elif 'home_team_yellow_cards' in cl:
            cmap['home_team_yellow_cards'] = col
        elif 'away_team_yellow_cards' in cl:
            cmap['away_team_yellow_cards'] = col
        elif 'home team pre-match xg' in cl:
            cmap['Home Team Pre-Match xG'] = col
        elif 'away team pre-match xg' in cl:
            cmap['Away Team Pre-Match xG'] = col
    req = ['home_team_name', 'away_team_name', 'home_team_goal_count', 'away_team_goal_count']
    for r in req:
        if r not in cmap:
            st.error(f"❌ 找不到必需列：{r}")
            st.write("当前CSV列名：", df_all.columns.tolist())
            return None, None, None, None
    df = pd.DataFrame()
    for k, cn in cmap.items():
        df[k] = df_all[cn]
    df.dropna(inplace=True)
    df['goal_diff'] = df['home_team_goal_count'] - df['away_team_goal_count']
    df['shots_diff'] = df['home_team_shots'] - df['away_team_shots']
    df['shots_on_target_diff'] = df['home_team_shots_on_target'] - df['away_team_shots_on_target']
    df['corner_diff'] = df['home_team_corner_count'] - df['away_team_corner_count']
    df['possession_diff'] = df['home_team_possession'] - df['away_team_possession']
    df['foul_diff'] = df['home_team_fouls'] - df['away_team_fouls']
    df['yellow_diff'] = df['home_team_yellow_cards'] - df['away_team_yellow_cards']
    df['xG_diff'] = df['Home Team Pre-Match xG'] - df['Away Team Pre-Match xG']
    df['result'] = np.where(df['goal_diff'] > 0, 2, np.where(df['goal_diff'] == 0, 1, 0))
    df['total_goals'] = df['home_team_goal_count'] + df['away_team_goal_count']
    fcols = ['shots_diff', 'shots_on_target_diff', 'corner_diff', 'possession_diff', 'foul_diff', 'yellow_diff', 'xG_diff']
    X = df[fcols]
    y = df['result']
    yg = np.clip(df['total_goals'], 0, 5)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    clf = xgb.XGBClassifier(objective='multi:softprob', num_class=3, random_state=42)
    clf.fit(Xs, y)
    reg = RandomForestClassifier(n_estimators=100, random_state=42)
    reg.fit(Xs, yg)
    return clf, reg, scaler, fcols

def predict_match(clf, reg, scaler, fcols, home, away, hs, as_):
    if clf is None:
        return None
    d = {'shots_diff': hs.get('shots', 0) - as_.get('shots', 0),
         'shots_on_target_diff': hs.get('shots_on_target', 0) - as_.get('shots_on_target', 0),
         'corner_diff': hs.get('corners', 0) - as_.get('corners', 0),
         'possession_diff': hs.get('possession', 50) - as_.get('possession', 50),
         'foul_diff': hs.get('fouls', 0) - as_.get('fouls', 0),
         'yellow_diff': hs.get('yellow_cards', 0) - as_.get('yellow_cards', 0),
         'xG_diff': hs.get('xg', 0) - as_.get('xg', 0)}
    X = np.array([[d[c] for c in fcols]])
    Xs = scaler.transform(X)
    rp = clf.predict_proba(Xs)[0]
    rp_idx = np.argmax(rp)
    rl = {0: '客胜', 1: '平局', 2: '主胜'}[rp_idx]
    gp = reg.predict_proba(Xs)[0]
    gi = np.argmax(gp)
    gl = str(gi) if gi < 5 else '5+'
    return {'result': rl, 'result_prob': rp[rp_idx], 'goals': gl, 'goals_prob': gp[gi],
            'probs': {'主胜': rp[2], '平局': rp[1], '客胜': rp[0]}}

def run_backtest(df, clf, reg, scaler, fcols):
    df = df.copy()
    df['shots_diff'] = df['home_team_shots'] - df['away_team_shots']
    df['shots_on_target_diff'] = df['home_team_shots_on_target'] - df['away_team_shots_on_target']
    df['corner_diff'] = df['home_team_corner_count'] - df['away_team_corner_count']
    df['possession_diff'] = df['home_team_possession'] - df['away_team_possession']
    df['foul_diff'] = df['home_team_fouls'] - df['away_team_fouls']
    df['yellow_diff'] = df['home_team_yellow_cards'] - df['away_team_yellow_cards']
    df['xG_diff'] = df['Home Team Pre-Match xG'] - df['Away Team Pre-Match xG']
    X = df[fcols].fillna(0)
    Xs = scaler.transform(X)
    rp = clf.predict(Xs)
    rpp = clf.predict_proba(Xs)
    gp = reg.predict(Xs)
    rr = np.where(df['home_team_goal_count'] > df['away_team_goal_count'], 2,
                  np.where(df['home_team_goal_count'] == df['away_team_goal_count'], 1, 0))
    rg = np.clip(df['home_team_goal_count'] + df['away_team_goal_count'], 0, 5)
    rgl = rg.apply(lambda x: str(x) if x < 5 else '5+')
    rlm = {0: '客胜', 1: '平局', 2: '主胜'}
    pr = [rlm[x] for x in rp]
    rr_l = [rlm[x] for x in rr]
    glm = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5+'}
    pg = [glm[x] for x in gp]
    ps = []
    for i, row in df.iterrows():
        if pr[i] == '主胜':
            g = int(pg[i]) if pg[i] != '5+' else 4
            ps.append(f"{g}:0" if g > 0 else "1:0")
        elif pr[i] == '客胜':
            g = int(pg[i]) if pg[i] != '5+' else 4
            ps.append(f"0:{g}" if g > 0 else "0:1")
        else:
            g = int(pg[i]) if pg[i] != '5+' else 4
            ps.append(f"{g // 2}:{g - g // 2}")
    rs = df['home_team_goal_count'].astype(str) + ':' + df['away_team_goal_count'].astype(str)
    gw = df['Game Week'].fillna('KO').astype(str)
    stage = []
    for i, g in enumerate(gw):
        if g in ['1', '2', '3']:
            if g == '1':
                stage.append('小组赛（第1轮·试探）')
            elif g == '2':
                stage.append('小组赛（第2轮·关键战）')
            else:
                stage.append('小组赛（第3轮·生死战）')
        else:
            if ('Jul 15' in df.iloc[i]['date_GMT'] or 'Dec 18' in df.iloc[i]['date_GMT']):
                stage.append('决赛')
            else:
                stage.append('淘汰赛')
    res = pd.DataFrame({'主队': df['home_team_name'], '客队': df['away_team_name'],
                        '真实比分': rs, '预测比分': ps,
                        '真实结果': rr_l, '预测结果': pr,
                        '结果正确': np.array(rr_l) == np.array(pr),
                        '真实总进球': rgl, '预测总进球': pg,
                        '进球正确': np.array(rgl) == np.array(pg),
                        '战意': stage,
                        '主胜概率': [f"{p[2]:.1%}" for p in rpp],
                        '平局概率': [f"{p[1]:.1%}" for p in rpp],
                        '客胜概率': [f"{p[0]:.1%}" for p in rpp]})
    total = len(res)
    acc = res['结果正确'].mean()
    gacc = res['进球正确'].mean()
    sacc = (res['真实比分'] == res['预测比分']).mean()
    stage_stats = res.groupby('战意').agg(准确率=('结果正确', 'mean'),
                                          进球准确率=('进球正确', 'mean'),
                                          场次=('结果正确', 'count')).reset_index()
    cm = confusion_matrix(res['真实结果'], res['预测结果'], labels=['客胜', '平局', '主胜'])
    return res, {'总准确率': acc, '总进球准确率': gacc, '比分准确率': sacc, '总场次': total,
                 '阶段统计': stage_stats, '混淆矩阵': cm, '混淆矩阵标签': ['客胜', '平局', '主胜']}

# ==================== UI 界面 ====================
st.markdown("""<style>
.main{background:#f0f2f6}
.result-box{background:#fff;border-radius:10px;padding:15px;margin:10px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.yao-box{background:#f8f9fa;border-left:4px solid #2e86c1;padding:10px;margin:5px 0}
.four-step{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;border-radius:10px;padding:20px;margin:10px 0}
.step-card{background:rgba(255,255,255,0.1);border-radius:8px;padding:12px;margin:8px 0}
.step-number{font-size:20px;font-weight:bold;color:#f1c40f}
.step-primary{font-size:22px;font-weight:bold;color:#2ecc71}
.step-secondary{font-size:18px;color:#f39c12}
.ml-pred{background:#e8f5e9;padding:10px;border-radius:8px;border-left:5px solid #4caf50;margin:10px 0}
</style>""", unsafe_allow_html=True)

st.image("https://img.icons8.com/color/96/000000/football2.png", width=80)
st.title("⚽ V6.0 足球预测 · 2026 xG版")
st.caption("内置32强最新xG数据 + 2018/2022机器学习 + 易经占卜 + 杂占 + 回测 + 泊松分布 + 凯利公式")

with st.spinner("正在训练机器学习模型..."):
    clf, reg, scaler, fcols = train_models()
if clf:
    st.success("✅ 机器学习模型训练完成！")
else:
    st.info("ℹ️ 未加载历史数据，仅使用传统方法预测。")

with st.expander("📋 输入比赛信息", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        home = st.text_input("主队", placeholder="请输入球队名")
    with c2:
        away = st.text_input("客队", placeholder="请输入球队名")
    match_date = st.date_input("比赛日期", datetime.date.today())
    match_time = st.time_input("比赛时间", datetime.time(0, 0))
    match_dt = datetime.datetime.combine(match_date, match_time)
    st.subheader("赔率数据")
    co = st.columns(3)
    with co[0]:
        st.caption("胜平负")
        odds_h = st.number_input("主胜", value=2.0, step=0.1, min_value=1.0)
        odds_d = st.number_input("平局", value=3.2, step=0.1, min_value=1.0)
        odds_a = st.number_input("客胜", value=3.5, step=0.1, min_value=1.0)
    with co[1]:
        st.caption("让球")
        hc = st.selectbox("让球数", [-3, -2, -1, 0, 1, 2, 3],
                          format_func=lambda x: f"主队{'+' if x < 0 else '-'}{abs(x)}" if x else "平手", index=2)
        odds_hc_h = st.number_input("让胜", value=3.5, step=0.1, min_value=1.0)
        odds_hc_d = st.number_input("让平", value=3.4, step=0.1, min_value=1.0)
        odds_hc_a = st.number_input("让负", value=2.0, step=0.1, min_value=1.0)
    with co[2]:
        st.caption("总进球/比分（已内嵌）")

with st.expander("🔧 补丁设置 & 比赛性质", expanded=False):
    cp1, cp2 = st.columns(2)
    with cp1:
        home_rot = st.number_input("主队轮换人数(≥4触发补丁①)", min_value=0, max_value=11, value=0, step=1)
        away_rot = st.number_input("客队轮换人数(≥4触发补丁①)", min_value=0, max_value=11, value=0, step=1)
        dta = st.selectbox("打平即可出线（补丁②）", ["无", "主队", "客队"])
        odds_up = st.checkbox("大小球盘口升盘（补丁③诱大警报）")
    with cp2:
        st.caption("补丁④（半场落后≥2球）需临场数据，暂不设开关。")
        st.caption("补丁⑤（屠杀局）根据xG自动调整。")

match_type = st.selectbox("比赛性质", ["常规", "淘汰赛", "决赛", "保级/出线生死战", "强弱悬殊"])

if st.button("🔮 开始推演", use_container_width=True):
    if home not in TEAM_DATA or away not in TEAM_DATA:
        st.error("❌ 输入的球队不在32强数据池中，请检查名称（如：巴西、日本）")
    else:
        he = TEAM_DATA[home]["elo"]
        hx = TEAM_DATA[home]["xg"]
        hf = TEAM_DATA[home]["form"]
        ae = TEAM_DATA[away]["elo"]
        ax = TEAM_DATA[away]["xg"]
        af = TEAM_DATA[away]["form"]
        st.success(f"✅ 主队 {home}: ELO={he}, xG={hx}, 胜率={hf}")
        st.success(f"✅ 客队 {away}: ELO={ae}, xG={ax}, 胜率={af}")
        mt_map = {"常规": "general", "淘汰赛": "knockout", "决赛": "final",
                  "保级/出线生死战": "draw", "强弱悬殊": "slaughter"}
        mtk = mt_map[match_type]
        patches = {"home_rotation": home_rot, "away_rotation": away_rot,
                   "draw_to_advance": "none" if dta == "无" else ("home" if dta == "主队" else "away"),
                   "odds_up": odds_up}
        if clf:
            st.divider()
            st.markdown("## 🤖 机器学习预测")
            hs = {'shots': 12, 'shots_on_target': 5, 'corners': 6, 'possession': 50, 'fouls': 12, 'yellow_cards': 2,
                  'xg': hx}
            as_ = {'shots': 12, 'shots_on_target': 5, 'corners': 6, 'possession': 50, 'fouls': 12, 'yellow_cards': 2,
                   'xg': ax}
            ml = predict_match(clf, reg, scaler, fcols, home, away, hs, as_)
            if ml:
                st.markdown(
                    f"""<div class="ml-pred"><b>预测结果：</b>{ml['result']}（概率 {ml['result_prob']:.1%}）<br><b>总进球：</b>{ml['goals']}（概率 {ml['goals_prob']:.1%}）<br><b>详细：</b>主胜 {ml['probs']['主胜']:.1%}，平局 {ml['probs']['平局']:.1%}，客胜 {ml['probs']['客胜']:.1%}</div>""",
                    unsafe_allow_html=True)
        st.divider()
        st.markdown("## 🔮 第一阶段：卦象分析（笔画起卦）")
        ga = full_gua_analysis(home, away, mtk)
        gi = ga["gua_info"]
        yd = ga["yao_details"]
        by = ga["bing_yao"]
        st.caption(
            f"起卦依据：主队“{home}”笔画数 {gi['home_strokes']}，客队“{away}”笔画数 {gi['away_strokes']}，总笔画 {gi['total_strokes']}，动爻 {gi['moving_yao']}")
        cg1, cg2, cg3 = st.columns(3)
        cg1.metric("本卦", f"{gi['base'][0]}{gi['base'][1]}（{gi['base_name']}）")
        cg2.metric("变卦", f"{gi['change'][0]}{gi['change'][1]}（{gi['change_name']}）")
        cg3.metric("互卦", f"{gi['inter'][0]}{gi['inter'][1]}（{gi['inter_name']}）")
        st.write(
            f"**体用生克**：{gi['ti_yong']}  （体卦{gi['body']}五行{gi['body_wuxing']}，用卦{gi['use']}五行{gi['use_wuxing']}）")
        st.write(f"**世应**：世爻在{LIUYAO_WEI[gi['shi_yao']]}（主队），应爻在{LIUYAO_WEI[gi['ying_yao']]}（客队）")
        if gi["base_key"] in GUA_DICT:
            g = GUA_DICT[gi["base_key"]]
            st.markdown(f"**📖 本卦【{g['name']}】卦辞**：{g['gua_ci']}")
            st.markdown(f"**象辞**：{g['xiang_ci']}")
        st.write("**💊 病药体系**：" + by['病药'])
        st.write(f"用神：{by['用神']} | 忌神：{by['忌神']} | 元神：{by['元神']} | 仇神：{by['仇神']}")
        st.divider()
        st.markdown("## 📜 第二阶段：古代杂占")
        sc = get_shichen_from_time(match_dt)
        sc_time = ['23-1', '1-3', '3-5', '5-7', '7-9', '9-11', '11-13', '13-15', '15-17', '17-19', '19-21', '21-23']
        st.write(f"**比赛时辰**：{sc}时（{sc_time[SHICHEN.index(sc)]}）")
        cz1, cz2 = st.columns(2)
        with cz1:
            st.markdown(f"**面热**：{MIAN_RE[sc]}")
            st.markdown(f"**眼跳**：左{YAN_TIAO[sc]['左']}，右{YAN_TIAO[sc]['右']}")
            st.markdown(f"**耳热**：{ER_RE[sc]}")
            st.markdown(f"**耳鸣**：左{ER_MING[sc]['左']}，右{ER_MING[sc]['右']}")
            st.markdown(f"**金鸣**：{JIN_MING[sc]}")
            st.markdown(f"**火逸**：{HUO_YI[sc]}")
        with cz2:
            st.markdown(f"**犬嘔**：{QUAN_OU[sc]}")
            st.markdown(f"**衣留**：{YI_LIU[sc]}")
            st.markdown(f"**喷嗑**：{PEN_KE[sc]}")
            st.markdown(f"**肉颤**：{ROU_CHAN[sc]}")
            st.markdown(f"**心惊**：{XIN_JING[sc]}")
            st.markdown(f"**鹊噪**：{QUE_ZAO[sc]}")
        st.divider()
        st.markdown("## 📊 第三阶段：量化计算")
        lh, la = compute_lam(he, ae, hx, ax, hf, af, patches, mtk)
        hp = dp = ap = 0
        for h in range(5):
            for a in range(5):
                p = poisson_prob(lh, h) * poisson_prob(la, a)
                if h > a:
                    hp += p
                elif h == a:
                    dp += p
                else:
                    ap += p
        st.write(f"**λ主**：{lh:.2f}，**λ客**：{la:.2f}")
        st.write(f"**主胜概率**：{hp:.1%} | **平局概率**：{dp:.1%} | **客胜概率**：{ap:.1%}")
        if odds_h > 0 and odds_d > 0 and odds_a > 0:
            st.caption(f"主胜EV：{(hp * odds_h) - 1:.2f} | 平局EV：{(dp * odds_d) - 1:.2f} | 客胜EV：{(ap * odds_a) - 1:.2f}")
        st.markdown("### 📈 泊松分布明细")
        score_probs = {}
        for h in range(5):
            for a in range(5):
                prob = poisson_prob(lh, h) * poisson_prob(la, a)
                score_probs[f"{h}-{a}"] = prob
        sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:5]
        st.write(f"**预期进球**：主队 {lh:.2f}，客队 {la:.2f}")
        st.write("**最可能出现的比分（前5）**：")
        for score, prob in sorted_scores:
            st.write(f"  - {score}：{prob:.1%}")
        goal_probs = {}
        for total in range(9):
            prob = 0
            for h in range(max(0, total-4), min(4, total)+1):
                a = total - h
                if 0 <= a <= 4:
                    prob += poisson_prob(lh, h) * poisson_prob(la, a)
            goal_probs[total] = prob
        goal_probs_agg = {}
        for t, p in goal_probs.items():
            if t <= 4:
                goal_probs_agg[str(t)] = p
            else:
                goal_probs_agg["5+"] = goal_probs_agg.get("5+", 0) + p
        st.write("**总进球数概率分布**：")
        for g, p in sorted(goal_probs_agg.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
            st.write(f"  - {g} 球：{p:.1%}")
        st.markdown("### 💰 凯利公式投注建议")
        st.caption("凯利值 = (赔率 × 概率 - 1) / (赔率 - 1)，正值表示有投注价值，越大越值得。")
        if odds_h > 0 and odds_d > 0 and odds_a > 0:
            kelly_h = (odds_h * hp - 1) / (odds_h - 1) if odds_h > 1 else 0
            kelly_d = (odds_d * dp - 1) / (odds_d - 1) if odds_d > 1 else 0
            kelly_a = (odds_a * ap - 1) / (odds_a - 1) if odds_a > 1 else 0
            st.write(f"**主胜**：凯利值 = {kelly_h:.3f}（{'✅ 有投注价值' if kelly_h > 0 else '❌ 不建议'}）")
            st.write(f"**平局**：凯利值 = {kelly_d:.3f}（{'✅ 有投注价值' if kelly_d > 0 else '❌ 不建议'}）")
            st.write(f"**客胜**：凯利值 = {kelly_a:.3f}（{'✅ 有投注价值' if kelly_a > 0 else '❌ 不建议'}）")
            max_kelly = max(kelly_h, kelly_d, kelly_a)
            if max_kelly > 0:
                best_bet = ["主胜", "平局", "客胜"][[kelly_h, kelly_d, kelly_a].index(max_kelly)]
                st.success(f"🏆 最佳投注选项：**{best_bet}**（凯利值 {max_kelly:.3f}）")
            else:
                st.warning("⚠️ 所有选项的凯利值均为负或零，建议观望或跳过。")
        else:
            st.info("请先输入有效的胜平负赔率，凯利公式才能计算。")
        st.divider()
        st.markdown("## 🎯 第四阶段：四层推演结论")
        res = four_step_predict(home, away, mtk, he, ae, hx, ax, hf, af, hc, patches)
        hd = f"主队-{hc}（主队让{hc}球）" if hc > 0 else f"主队+{-hc}（主队受让{-hc}球）" if hc < 0 else "平手"
        st.markdown(f"""
        <div class="four-step">
            <div class="step-card"><span class="step-number">① 胜平负</span><br><span class="step-primary">首推：{res['direction_primary']}</span><br><span class="step-secondary">次推：{res['direction_secondary']}</span></div>
            <div class="step-card"><span class="step-number">② 让球胜平负（{hd}）</span><br><span class="step-primary">首推：{res['handicap_primary']}</span><br><span class="step-secondary">次推：{res['handicap_secondary']}</span></div>
            <div class="step-card"><span class="step-number">③ 总进球数</span><br><span class="step-primary">首推：{res['goal_primary']}球</span><br><span class="step-secondary">次推：{res['goal_secondary']}球</span></div>
            <div class="step-card"><span class="step-number">④ 比分（精准）</span><br><span class="step-primary">首推：{res['score_primary']}</span><br><span class="step-secondary">次推：{res['score_secondary']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("补丁状态：" + (
            "✅ 补丁①（轮换）触发 " if home_rot >= 4 or away_rot >= 4 else "") + (
            "✅ 补丁②（打平即可出线）触发 " if dta != "无" else "") + (
            "✅ 补丁③（诱大警报）触发 " if odds_up else "") + (
            "✅ 补丁⑤（屠杀局）触发" if hx >= 2.0 and ax <= 1.0 else ""))
        with st.expander("🔎 六爻逐爻详解（点击展开）", expanded=True):
            for y in yd:
                st.markdown(f"**{y['position']}**  (爻位：{y['gong']})")
                st.caption(f"五行：{y['wuxing']}，六亲：{y['liuqin']}（{LIUQIN_MAP.get(y['liuqin'], '')}），吉凶：{y['jixiong']}")
                st.write(y['text'])
                st.markdown("---")
        st.session_state.predict_history.append({
            "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "主队": home,
            "客队": away,
            "比赛性质": match_type,
            "首推方向": res['direction_primary'],
            "首推比分": res['score_primary'],
            "次推比分": res['score_secondary']
        })
        st.toast("✅ 预测已保存至历史记录！", icon="💾")
        st.divider()
        st.caption("心源心法：爻象定真，共振取象，三象合一。V6.0 2026 xG版 + 泊松分布 + 凯利公式")

st.divider()
st.markdown("## 📊 回测历史数据（2018+2022）")
if st.button("📊 执行回测", use_container_width=True):
    files = ["international-fifa-world-cup-2018-russia-matches-2018-to-2018-stats.csv",
             "international-fifa-world-cup-2022-qatar-matches-2022-to-2022-stats.csv"]
    dfs = []
    for f in files:
        if os.path.exists(f):
            dfs.append(pd.read_csv(f))
    if not dfs:
        st.error("❌ 未找到CSV文件，请将数据文件放在应用目录下。")
    else:
        df_all = pd.concat(dfs, ignore_index=True)
        if clf is None:
            st.warning("模型未训练，正在重新训练...")
            clf, reg, scaler, fcols = train_models()
            if clf is None:
                st.error("❌ 训练失败，无法回测。请检查CSV文件列名是否正确。")
                st.stop()
        with st.spinner("回测中，请稍候..."):
            results_df, stats = run_backtest(df_all, clf, reg, scaler, fcols)
        st.success("✅ 回测完成！")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("总场次", stats['总场次'])
        c2.metric("结果准确率", f"{stats['总准确率']:.1%}")
        c3.metric("总进球准确率", f"{stats['总进球准确率']:.1%}")
        c4.metric("比分准确率", f"{stats['比分准确率']:.1%}")
        st.subheader("📈 分阶段准确率")
        st.dataframe(stats['阶段统计'].style.format({'准确率': '{:.1%}', '进球准确率': '{:.1%}'}))
        st.subheader("📊 混淆矩阵")
        cm_df = pd.DataFrame(stats['混淆矩阵'], index=stats['混淆矩阵标签'], columns=stats['混淆矩阵标签'])
        st.dataframe(cm_df)
        with st.expander("📋 查看每场比赛详细预测对比", expanded=False):
            st.dataframe(results_df)
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 下载回测结果CSV", data=csv, file_name="backtest_results.csv", mime="text/csv")

st.divider()
st.markdown("## 📋 我的预测历史")
if st.session_state.predict_history:
    df_history = pd.DataFrame(st.session_state.predict_history)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
    col_clear1, col_clear2 = st.columns([1, 5])
    with col_clear1:
        if st.button("🗑️ 清空历史", use_container_width=True):
            st.session_state.predict_history = []
            st.rerun()
else:
    st.info("📭 暂无预测记录，点击「开始推演」后会自动保存。")
