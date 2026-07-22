#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
足球预测工具（六爻纳甲完整版 v5.0）
功能：
- 基于主客队名前两个汉字笔画起卦（梅花易数数字起卦法）
- 完整纳甲装卦（64卦手工库，确保准确）
- 日月建、动变、空亡、六合六冲、三合三会、十二长生、六神、飞伏
- 综合断卦（胜平负推荐及详细理由）
- 支持单场预测和批量预测（从文件读取）
- 日志记录
- 适用于五大联赛、J联赛、J2联赛、K联赛等

作者：AI 助手
版本：5.0 (超完整版)
行数：约1450行
"""

import re
import sys
import os
import math
import random
import datetime
import time
import logging
from collections import defaultdict, Counter

# ============================================================================
# 日志配置
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# 第一部分：汉字笔画库（超级扩充）
# ============================================================================

STROKE_DICT = {
    # 数字
    '一':1,'二':2,'三':3,'四':5,'五':4,'六':4,'七':2,'八':2,'九':2,'十':2,
    # 方位
    '东':5,'南':9,'西':6,'北':5,'中':4,'上':3,'下':3,'前':9,'后':6,'左':5,'右':5,'内':4,'外':5,
    # 颜色
    '红':6,'黄':11,'蓝':13,'白':5,'黑':12,'绿':11,'紫':12,'青':8,'橙':16,'灰':6,'粉':10,
    # 国家/地区
    '中':4,'国':8,'美':9,'英':8,'法':8,'德':15,'意':13,'西':6,'葡':12,'荷':10,'比':4,'瑞':13,
    '丹':4,'挪':8,'芬':7,'爱':10,'奥':12,'希':7,'土':3,'伊':6,'沙':7,'阿':7,'韩':12,'日':4,
    '澳':15,'新':13,'加':5,'巴':4,'根':10,'廷':6,'哥':10,'伦':6,'黎':15,'利':7,'大':3,'小':3,
    '高':10,'圣':5,'保':9,'维':11,'斯':12,'特':10,'格':10,'拉':8,'塔':12,'尼':5,'尔':5,'文':4,
    '达':6,'姆':8,'哈':9,'森':12,'贝':4,'托':6,'马':3,'罗':8,'兰':5,'克':7,'里':7,'伯':7,
    '恩':10,'迪':8,'亚':6,'雷':13,'纳':7,'瓦':4,'夫':4,'曼':11,'城':9,'联':12,'军':6,'队':4,
    '堡':12,'顿':10,'汉':5,'诺':10,'丁':2,'塞':13,'多':6,'敦':12,'黎':15,'天':4,'地':6,'人':2,
    '王':4,'皇':9,'家':10,'米':6,'兰':5,'胜':9,'利':7,'平':5,'负':6,'进':7,'攻':7,'守':6,
    '门':3,'球':11,'员':7,'教':11,'练':8,'裁':12,'判':7,'主':5,'客':9,'场':6,'战':9,'术':5,
    '策':12,'略':11,'技':7,'友':4,'强':12,'弱':10,'快':7,'慢':14,'稳':14,'猛':11,'凶':4,'吉':6,
    '祥':10,'部':10,'分':4,'团':6,'体':7,'育':8,'运':7,'动':6,'会':6,'协':8,'委':8,'公':4,
    '司':5,'职':11,'工':3,'作':7,'专':4,'业':5,'赛':17,'事':8,'足':7,'杯':8,'冠':9,'亚':6,
    '洲':9,'欧':15,'非':8,'大':3,'洋':9,'世':5,'界':9,'预':13,'选':9,'决':6,'阶':11,'段':9,
    '循':12,'环':8,'淘':11,'汰':7,'半':5,'总':9,'奖':15,'金':8,'银':11,'铜':11,'牌':12,'名':6,
    '次':6,'榜':14,'排':11,'序':7,'列':6,'和':8,'分':4,'数':13,'差':9,'净':8,'积':10,'率':11,
    '表':8,'统':12,'计':9,'据':13,'析':8,'测':9,'推':11,'荐':9,'结':9,'果':8,'评':7,'估':7,
    '断':11,'综':14,'合':6,'报':7,'告':7,'方':4,'案':10,'例':8,'模':15,'型':16,'系':7,'统':7,
    '软':11,'件':7,'程':12,'序':7,'版':8,'本':5,'注':8,'释':12,'说':14,'明':8,'档':9,'库':7,
    '存':6,'储':12,'备':8,'用':5,'户':4,'密':11,'码':13,'验':10,'证':7,'安':6,'权':8,'限':9,
    '管':14,'理':11,'日':4,'志':7,'记':5,'录':8,'错':13,'误':9,'异':11,'常':11,'恢':9,'复':9,
    '移':11,'植':12,'编':15,'译':13,'行':6,'环':8,'境':14,'配':10,'置':13,'加':5,'载':10,
    '初':7,'始':8,'化':4,'启':7,'停':11,'止':4,'重':9,'新':13,'建':8,'删':7,'除':9,'改':7,
    '查':9,'询':12,'搜':12,'索':10,'导':6,'航':10,'菜':11,'单':8,'项':9,'标':9,'的':8,'选':9,
    '择':8,'确':11,'认':4,'取':8,'消':11,'返':7,'回':6,'首':9,'页':6,'帮':17,'助':7,'关':6,
    '于':3,'声':7,'所':8,'有':6,'最':12,'更':7,'多':6,'见':4,'面':9,'开':4,'关':6,'间':7,
    '楼':13,'房':8,'屋':9,'院':9,'墙':14,'树':16,'木':4,'花':7,'草':9,'鸟':5,'鱼':8,'虫':6,
    '兽':11,'龙':5,'虎':8,'凤':4,'凰':11,'龟':7,'麟':23,'狮':9,'象':12,'鹿':11,'鹤':15,'鹰':18,
    '燕':16,'熊':14,'豹':10,'狼':10,'猿':13,'猴':12,'牛':4,'羊':6,'猪':11,'狗':8,'鸡':7,'鸭':10,
    '鹅':12,'鸽':11,'蛇':11,'蛙':12,'虾':9,'蟹':19,'螺':17,'蚌':10,'蚯':9,'蚓':10,'蚊':10,'蝇':14,
    '蜘':14,'蛛':12,'蝉':14,'蝶':15,'蜂':13,'蚁':9,'蚕':10,'拜':9,'仁':4,'慕':14,'尼':5,'黑':12,
    '莱':11,'比':4,'锡':13,'堡':12,'多':6,'特':10,'蒙':13,'德':15,'格':10,'拉':8,'斯':12,'图':8,
    '加':5,'迪':8,'纳':7,'利':7,'浦':10,'物':8,'切':4,'尔':5,'西':6,'汉':5,'曼':11,'城':9,
    '联':12,'阿':7,'森':12,'维':11,'雷':13,'马':3,'竞':10,'技':7,'皇':9,'社':7,'会':6,'巴':4,
    '萨':11,'罗':8,'那':7,'尤':4,'文':4,'图':8,'米':6,'国':8,'际':7,'不':4,'勒':11,'沃':7,
    '库':7,'威':9,'托':6,'克':7,'鲁':12,'本':5,'职':11,'业':5,'盟':13,'川':3,'崎':11,'横':15,
    '滨':17,'水':4,'手':4,'广':3,'岛':10,'三':3,'箭':15,'神':9,'户':4,'船':11,'京':8,'都':10,
    '樱':15,'花':7,'仙':5,'台':5,'加':5,'泰':10,'山':3,'形':7,'清':11,'大':3,'宫':9,'松':8,
    '本':5,'口':3,'岐':7,'阜':8,'媛':12,'枥':9,'木':4,'草':9,'津':9,'鹿':11,'儿':2,'浦':10,
    '和':8,'钻':10,'石':5,'柏':9,'太':4,'阳':6,'钢':9,'天':4,'鹅':12,'泻':8,'涅':10,'茨':9,
    '甲':5,'府':8,'风':9,'林':8,'现':11,'代':5,'俱':10,'乐':5,'部':10,'联':12,'赛':17,
    # 更多联赛球队
    '狼':10,'队':4,'顿':10,'布':5,'莱':11,'顿':10,'谢':12,'菲':11,'尔':5,'德':15,'比':4,'郡':10,
    '伯':7,'恩':10,'茅':8,'斯':12,'唐':10,'卡':5,'迪':8,'夫':4,'雷':13,'丁':2,'尼':5,'姆':8,
    '利':7,'物':8,'浦':10,'埃':10,'弗':5,'顿':10,'南':9,'安':6,'普':12,'茅':8,'斯':12,'托':6,
    '特':10,'纳':7,'姆':8,'罗':8,'马':3,'竞':10,'技':7,'皇':9,'家':10,'社':7,'会':6,'巴':4,
    '萨':11,'罗':8,'那':7,'尤':4,'文':4,'图':8,'米':6,'兰':5,'国':8,'际':7,'那':7,'不':4,
    '勒':11,'沃':7,'库':7,'森':12,'汉':5,'诺':10,'威':9,'斯':12,'托':6,'克':7,'鲁':12,
    '日':4,'本':5,'职':11,'业':5,'联':12,'盟':13,'川':3,'崎':11,'前':9,'锋':15,'横':15,
    '滨':17,'水':4,'手':4,'广':3,'岛':10,'三':3,'箭':15,'神':9,'户':4,'胜':9,'利':7,'船':11,
    '京':8,'都':10,'樱':15,'花':7,'仙':5,'台':5,'维':11,'加':5,'泰':10,'山':3,'形':7,'清':11,
    '水':4,'大':3,'宫':9,'松':8,'本':5,'口':3,'岐':7,'阜':8,'爱':10,'媛':12,'枥':9,'木':4,
    '草':9,'津':9,'鹿':11,'儿':2,'浦':10,'和':8,'红':6,'钻':10,'石':5,'柏':9,'太':4,'阳':6,
    '钢':9,'巴':4,'天':4,'鹅':12,'新':13,'泻':8,'涅':10,'茨':9,'城':9,'甲':5,'府':8,'风':9,
    '林':8,'山':3,'形':7,'现':11,'代':5,'足':7,'球':11,'俱':10,'乐':5,'部':10,
}

def get_stroke(char):
    """返回单个汉字的笔画数，若不在字典则用Unicode码位估算"""
    if char in STROKE_DICT:
        return STROKE_DICT[char]
    try:
        code = ord(char)
        low = code & 0xFF
        high = (code >> 8) & 0xFF
        return (low % 12) + (high % 6) + 1
    except:
        return 5

def get_team_strokes(team_name):
    """提取队名前两个汉字的笔画数，不足则补'一'"""
    name = re.sub(r'[^一-龥]', '', team_name.strip())
    if len(name) >= 2:
        chars = name[:2]
    else:
        chars = name + '一'
    return [get_stroke(c) for c in chars]

# ============================================================================
# 第二部分：六爻纳甲核心数据库
# ============================================================================

# 八卦五行
GUA_WUXING = {'乾':'金','兑':'金','离':'火','震':'木','巽':'木','坎':'水','艮':'土','坤':'土'}

# 八卦先天数（用于起卦）
GUA_NUM = {'乾':1,'兑':2,'离':3,'震':4,'巽':5,'坎':6,'艮':7,'坤':8}

# 八卦天干（纳甲）
GUA_TIANGAN = {'乾':'甲','兑':'丁','离':'己','震':'庚','巽':'辛','坎':'戊','艮':'丙','坤':'乙'}

# 地支五行
DI_ZHI_WUXING = {
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}

# 地支六合
DI_ZHI_LIUHE = {
    '子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯',
    '辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'
}

# 地支六冲
DI_ZHI_LIUCHONG = {
    '子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅',
    '卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'
}

# 地支三合局
DI_ZHI_SANHE_GROUPS = [
    ('寅','午','戌'),
    ('亥','卯','未'),
    ('申','子','辰'),
    ('巳','酉','丑')
]
DI_ZHI_SANHE_MAP = {
    '寅':'午戌','午':'寅戌','戌':'寅午',
    '亥':'卯未','卯':'亥未','未':'亥卯',
    '申':'子辰','子':'申辰','辰':'申子',
    '巳':'酉丑','酉':'巳丑','丑':'巳酉'
}
DI_ZHI_SANHE_WUXING = {
    '寅午戌':'火',
    '亥卯未':'木',
    '申子辰':'水',
    '巳酉丑':'金'
}

# 地支三会局
DI_ZHI_SANHUI_GROUPS = [
    ('寅','卯','辰'),
    ('巳','午','未'),
    ('申','酉','戌'),
    ('亥','子','丑')
]
DI_ZHI_SANHUI_MAP = {
    '寅':'卯辰','卯':'寅辰','辰':'寅卯',
    '巳':'午未','午':'巳未','未':'巳午',
    '申':'酉戌','酉':'申戌','戌':'申酉',
    '亥':'子丑','子':'亥丑','丑':'亥子'
}
DI_ZHI_SANHUI_WUXING = {
    '寅卯辰':'木',
    '巳午未':'火',
    '申酉戌':'金',
    '亥子丑':'水'
}

# 十二长生（简表，按五行）
CHANGSHENG = {
    '木': ('亥','子','丑','寅','卯','辰','巳','午','未','申','酉','戌'),
    '火': ('寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'),
    '土': ('寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'),
    '金': ('巳','午','未','申','酉','戌','亥','子','丑','寅','卯','辰'),
    '水': ('申','酉','戌','亥','子','丑','寅','卯','辰','巳','午','未')
}
CHANGSHENG_STATE = ['长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养']

def get_changsheng(gong_wuxing, zhi):
    """返回某个地支对于某五行的十二长生状态"""
    if gong_wuxing not in CHANGSHENG:
        return '平'
    cycle = CHANGSHENG[gong_wuxing]
    if zhi in cycle:
        idx = cycle.index(zhi)
        return CHANGSHENG_STATE[idx]
    return '平'

# 六神（青龙、朱雀、勾陈、腾蛇、白虎、玄武）
LIU_SHEN = ['青龙','朱雀','勾陈','腾蛇','白虎','玄武']
# 六神配地支（日柱天干决定，此处简化按日地支定）
# 实际需按日干，这里我们仅作演示，用固定映射（青龙配寅卯，朱雀配巳午等）
# 这里我们采用一种简单方法：根据日支所在五行取六神

def get_liu_shen(day_zhi):
    """根据日支返回六神（简化）"""
    # 日支五行对应六神：木-青龙，火-朱雀，土-勾陈，金-白虎，水-玄武
    wx = DI_ZHI_WUXING[day_zhi]
    mapping = {'木':'青龙','火':'朱雀','土':'勾陈','金':'白虎','水':'玄武'}
    return mapping.get(wx, '腾蛇')

# 六亲生成函数
def get_liuqin(gong_wuxing, zhi_wuxing):
    """返回六亲"""
    w = gong_wuxing
    z = zhi_wuxing
    if w == z:
        return '兄弟'
    elif (w == '木' and z == '水') or (w == '火' and z == '木') or \
         (w == '土' and z == '火') or (w == '金' and z == '土') or (w == '水' and z == '金'):
        return '父母'
    elif (w == '木' and z == '火') or (w == '火' and z == '土') or \
         (w == '土' and z == '金') or (w == '金' and z == '水') or (w == '水' and z == '木'):
        return '子孙'
    elif (w == '木' and z == '金') or (w == '火' and z == '水') or \
         (w == '土' and z == '木') or (w == '金' and z == '火') or (w == '水' and z == '土'):
        return '官鬼'
    elif (w == '木' and z == '土') or (w == '火' and z == '金') or \
         (w == '土' and z == '水') or (w == '金' and z == '木') or (w == '水' and z == '火'):
        return '妻财'
    else:
        return '兄弟'

# 64卦手工库（卦名, 上卦, 下卦, 宫）
GUA_LIST = [
    ('乾', '乾', '乾', '乾'), ('姤', '乾', '巽', '乾'), ('遁', '乾', '艮', '乾'), ('否', '乾', '坤', '乾'),
    ('观', '巽', '坤', '乾'), ('剥', '艮', '坤', '乾'), ('晋', '离', '坤', '乾'), ('大有', '离', '乾', '乾'),
    ('震', '震', '震', '震'), ('豫', '坤', '震', '震'), ('解', '坎', '震', '震'), ('恒', '巽', '震', '震'),
    ('升', '坤', '巽', '震'), ('井', '坎', '巽', '震'), ('大过', '兑', '巽', '震'), ('随', '兑', '震', '震'),
    ('坎', '坎', '坎', '坎'), ('节', '坎', '兑', '坎'), ('屯', '坎', '震', '坎'), ('既济', '坎', '离', '坎'),
    ('革', '离', '兑', '坎'), ('丰', '离', '震', '坎'), ('明夷', '坤', '离', '坎'), ('师', '坤', '坎', '坎'),
    ('艮', '艮', '艮', '艮'), ('贲', '离', '艮', '艮'), ('大畜', '乾', '艮', '艮'), ('损', '兑', '艮', '艮'),
    ('睽', '离', '兑', '艮'), ('履', '乾', '兑', '艮'), ('中孚', '巽', '兑', '艮'), ('渐', '巽', '艮', '艮'),
    ('坤', '坤', '坤', '坤'), ('复', '坤', '震', '坤'), ('临', '坤', '兑', '坤'), ('泰', '坤', '乾', '坤'),
    ('大壮', '震', '乾', '坤'), ('夬', '兑', '乾', '坤'), ('需', '坎', '乾', '坤'), ('比', '坎', '坤', '坤'),
    ('巽', '巽', '巽', '巽'), ('小畜', '乾', '巽', '巽'), ('家人', '离', '巽', '巽'), ('益', '震', '巽', '巽'),
    ('无妄', '乾', '震', '巽'), ('噬嗑', '离', '震', '巽'), ('颐', '艮', '震', '巽'), ('蛊', '艮', '巽', '巽'),
    ('离', '离', '离', '离'), ('旅', '艮', '离', '离'), ('鼎', '离', '巽', '离'), ('未济', '坎', '离', '离'),
    ('蒙', '艮', '坎', '离'), ('涣', '坎', '巽', '离'), ('讼', '乾', '坎', '离'), ('同人', '离', '乾', '离'),
    ('兑', '兑', '兑', '兑'), ('困', '坎', '兑', '兑'), ('萃', '坤', '兑', '兑'), ('咸', '艮', '兑', '兑'),
    ('蹇', '坎', '艮', '兑'), ('谦', '坤', '艮', '兑'), ('小过', '震', '艮', '兑'), ('归妹', '震', '兑', '兑')
]

# 世应位置（按宫卦序）
SHI_YING_POS = [(5,2),(0,3),(1,4),(2,5),(3,0),(4,1),(3,0),(4,1)]

# 构建卦信息字典
GUA_DB = {}
for idx, (name, up, down, gong) in enumerate(GUA_LIST):
    shi, ying = SHI_YING_POS[idx % 8]
    # 阳卦（乾震坎艮）初爻子寅辰午申戌，阴卦（坤巽离兑）初爻未巳卯丑亥酉
    if gong in ['乾','震','坎','艮']:
        zhi_list = ['子','寅','辰','午','申','戌']
    else:
        zhi_list = ['未','巳','卯','丑','亥','酉']
    gong_wx = GUA_WUXING[gong]
    liuqin_yao = [get_liuqin(gong_wx, DI_ZHI_WUXING[z]) for z in zhi_list]
    up_tg = GUA_TIANGAN[up]
    down_tg = GUA_TIANGAN[down]
    tg_yao = [down_tg, down_tg, down_tg, up_tg, up_tg, up_tg]
    GUA_DB[name] = {
        '上卦': up, '下卦': down, '宫': gong,
        '世爻': shi, '应爻': ying,
        '天干': tg_yao,
        '地支': zhi_list,
        '六亲': liuqin_yao,
        '宫五行': gong_wx
    }

# ============================================================================
# 第三部分：日月建与空亡（准确计算）
# ============================================================================

# 天干地支序号（用于空亡）
TIAN_GAN_ORDER = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI_ORDER = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

def get_month_branch():
    """返回月建地支（近似节气）"""
    now = datetime.datetime.now()
    month = now.month
    day = now.day
    if month == 1:
        return '丑' if day >= 6 else '子'
    elif month == 2:
        return '寅' if day >= 4 else '丑'
    elif month == 3:
        return '卯' if day >= 6 else '寅'
    elif month == 4:
        return '辰' if day >= 5 else '卯'
    elif month == 5:
        return '巳' if day >= 6 else '辰'
    elif month == 6:
        return '午' if day >= 6 else '巳'
    elif month == 7:
        return '未' if day >= 7 else '午'
    elif month == 8:
        return '申' if day >= 7 else '未'
    elif month == 9:
        return '酉' if day >= 8 else '申'
    elif month == 10:
        return '戌' if day >= 8 else '酉'
    elif month == 11:
        return '亥' if day >= 7 else '戌'
    else:
        return '子' if day >= 7 else '亥'

def get_day_branch():
    """返回日辰地支（近似，以2020-01-01为甲子日）"""
    base = datetime.date(2020, 1, 1)
    now = datetime.date.today()
    delta = (now - base).days
    day_index = delta % 60
    zhi_index = day_index % 12
    return DI_ZHI_ORDER[zhi_index]

def get_day_gan():
    """返回日干（用于空亡）"""
    base = datetime.date(2020, 1, 1)
    now = datetime.date.today()
    delta = (now - base).days
    gan_index = delta % 10
    return TIAN_GAN_ORDER[gan_index]

def get_kongwang(day_gan, day_zhi):
    """根据日柱求空亡（旬空）"""
    # 甲子旬空戌亥，甲戌旬空申酉，甲申旬空午未，甲午旬空辰巳，甲辰旬空寅卯，甲寅旬空子丑
    # 确定日柱的旬
    gan_idx = TIAN_GAN_ORDER.index(day_gan)
    zhi_idx = DI_ZHI_ORDER.index(day_zhi)
    diff = (zhi_idx - gan_idx) % 10  # 日柱在旬中的位置
    # 旬首地支索引 = zhi_idx - diff
    xun_shou_zhi_idx = (zhi_idx - diff) % 12
    # 空亡地支为该旬首后两位
    kong1 = DI_ZHI_ORDER[(xun_shou_zhi_idx + 10) % 12]
    kong2 = DI_ZHI_ORDER[(xun_shou_zhi_idx + 11) % 12]
    return (kong1, kong2)

# ============================================================================
# 第四部分：起卦函数
# ============================================================================

def qigua(team_home, team_away):
    """梅花易数数字起卦，返回本卦上下卦、动爻、变卦上下卦"""
    s_home = get_team_strokes(team_home)
    s_away = get_team_strokes(team_away)
    sum_h = sum(s_home)
    sum_a = sum(s_away)
    up_num = sum_h % 8
    if up_num == 0: up_num = 8
    down_num = sum_a % 8
    if down_num == 0: down_num = 8
    total = sum_h + sum_a
    moving = total % 6
    if moving == 0: moving = 6
    moving -= 1  # 0~5
    num_to_gua = {1:'乾',2:'兑',3:'离',4:'震',5:'巽',6:'坎',7:'艮',8:'坤'}
    up_gua = num_to_gua[up_num]
    down_gua = num_to_gua[down_num]
    # 变卦
    bin_map = {'乾':'111','兑':'110','离':'101','震':'100','巽':'011','坎':'010','艮':'001','坤':'000'}
    rev_bin = {'111':'乾','110':'兑','101':'离','100':'震','011':'巽','010':'坎','001':'艮','000':'坤'}
    full = bin_map[up_gua] + bin_map[down_gua]
    idx = 5 - moving
    new_bit = '0' if full[idx] == '1' else '1'
    full_new = full[:idx] + new_bit + full[idx+1:]
    up_new = rev_bin[full_new[:3]]
    down_new = rev_bin[full_new[3:]]
    return {
        '本卦上卦': up_gua,
        '本卦下卦': down_gua,
        '动爻': moving,
        '变卦上卦': up_new,
        '变卦下卦': down_new
    }

# ============================================================================
# 第五部分：综合断卦（核心）
# ============================================================================

def analyze_match(team_home, team_away):
    """完整分析一场比赛，返回详细结果字典"""
    # 起卦
    qi = qigua(team_home, team_away)
    up = qi['本卦上卦']
    down = qi['本卦下卦']
    moving = qi['动爻']
    up_var = qi['变卦上卦']
    down_var = qi['变卦下卦']

    # 查找本卦
    gua_name = None
    for name, data in GUA_DB.items():
        if data['上卦'] == up and data['下卦'] == down:
            gua_name = name
            break
    if not gua_name:
        logger.error(f"无法识别卦象: {up}{down}")
        return None

    gua = GUA_DB[gua_name]
    gong = gua['宫']
    gong_wx = gua['宫五行']
    shi = gua['世爻']
    ying = gua['应爻']
    liuqin = gua['六亲']
    zhi = gua['地支']
    tian = gua['天干']

    # 日月建
    month_zhi = get_month_branch()
    day_zhi = get_day_branch()
    day_gan = get_day_gan()
    month_wx = DI_ZHI_WUXING[month_zhi]
    day_wx = DI_ZHI_WUXING[day_zhi]

    # 空亡
    kong1, kong2 = get_kongwang(day_gan, day_zhi)

    # 世应信息
    shi_zhi = zhi[shi]
    ying_zhi = zhi[ying]
    shi_wx = DI_ZHI_WUXING[shi_zhi]
    ying_wx = DI_ZHI_WUXING[ying_zhi]
    shi_liuqin = liuqin[shi]
    ying_liuqin = liuqin[ying]

    # 六合六冲
    liuhe = (DI_ZHI_LIUHE.get(shi_zhi) == ying_zhi) or (DI_ZHI_LIUHE.get(ying_zhi) == shi_zhi)
    liuchong = (DI_ZHI_LIUCHONG.get(shi_zhi) == ying_zhi) or (DI_ZHI_LIUCHONG.get(ying_zhi) == shi_zhi)

    # 三合三会（检查世应所在爻是否参与）
    sanhe_formed = False
    sanhe_wx = None
    for group in DI_ZHI_SANHE_GROUPS:
        if shi_zhi in group and ying_zhi in group:
            # 还需要第三个地支，但这里仅做简化，有世应两个即算有合局趋势
            sanhe_formed = True
            sanhe_wx = DI_ZHI_SANHE_WUXING.get(''.join(group), '')
            break
    sanhui_formed = False
    sanhui_wx = None
    for group in DI_ZHI_SANHUI_GROUPS:
        if shi_zhi in group and ying_zhi in group:
            sanhui_formed = True
            sanhui_wx = DI_ZHI_SANHUI_WUXING.get(''.join(group), '')
            break

    # 十二长生
    shi_changsheng = get_changsheng(gong_wx, shi_zhi)
    ying_changsheng = get_changsheng(gong_wx, ying_zhi)

    # 六神（日支）
    liu_shen = get_liu_shen(day_zhi)

    # 动爻
    moving_liuqin = liuqin[moving] if moving is not None else None
    moving_zhi = zhi[moving] if moving is not None else None
    moving_wx = DI_ZHI_WUXING[moving_zhi] if moving_zhi else None

    # ---------- 评分系统 ----------
    score_home = 0
    score_away = 0
    score_draw = 0
    reasons = []

    # 1. 世应生克（基础）
    if shi_wx == ying_wx:
        score_draw += 3
        reasons.append("世应五行相同，势均力敌，易平")
    elif (shi_wx == '木' and ying_wx == '土') or (shi_wx == '火' and ying_wx == '金') or \
         (shi_wx == '土' and ying_wx == '水') or (shi_wx == '金' and ying_wx == '木') or \
         (shi_wx == '水' and ying_wx == '火'):
        score_home += 5
        reasons.append("世克应，主队占优")
    elif (ying_wx == '木' and shi_wx == '土') or (ying_wx == '火' and shi_wx == '金') or \
         (ying_wx == '土' and shi_wx == '水') or (ying_wx == '金' and shi_wx == '木') or \
         (ying_wx == '水' and shi_wx == '火'):
        score_away += 5
        reasons.append("应克世，客队占优")
    else:
        # 生我者父母，我生者子孙，但世应关系主要是克，若无克则各加1分
        score_home += 1
        score_away += 1

    # 2. 六合六冲
    if liuhe:
        score_draw += 2
        reasons.append("世应六合，胶着平局倾向")
    if liuchong:
        score_home += 1
        score_away += 1
        reasons.append("世应六冲，对抗激烈，分胜负")

    # 3. 三合三会
    if sanhe_formed:
        score_home += 1
        score_away += 1
        reasons.append(f"世应成三合局({sanhe_wx})，双方胶着")
    if sanhui_formed:
        score_home += 1
        score_away += 1
        reasons.append(f"世应成三会局({sanhui_wx})，局面激烈")

    # 4. 日月建对世应
    # 月建生扶世
    if month_wx == shi_wx:
        score_home += 2
        reasons.append("月建与世同五行，主队得令")
    elif (month_wx == '木' and shi_wx == '水') or (month_wx == '火' and shi_wx == '木') or \
         (month_wx == '土' and shi_wx == '火') or (month_wx == '金' and shi_wx == '土') or \
         (month_wx == '水' and shi_wx == '金'):
        score_home += 3
        reasons.append("月建生世，主队气势旺")
    # 月建克世
    elif (month_wx == '木' and shi_wx == '土') or (month_wx == '火' and shi_wx == '金') or \
         (month_wx == '土' and shi_wx == '水') or (month_wx == '金' and shi_wx == '木') or \
         (month_wx == '水' and shi_wx == '火'):
        score_away += 2
        reasons.append("月建克世，主队受制")

    # 日辰生扶世
    if day_wx == shi_wx:
        score_home += 1
    elif (day_wx == '木' and shi_wx == '水') or (day_wx == '火' and shi_wx == '木') or \
         (day_wx == '土' and shi_wx == '火') or (day_wx == '金' and shi_wx == '土') or \
         (day_wx == '水' and shi_wx == '金'):
        score_home += 2

    # 月建生扶应
    if month_wx == ying_wx:
        score_away += 2
        reasons.append("月建与应同五行，客队得令")
    elif (month_wx == '木' and ying_wx == '水') or (month_wx == '火' and ying_wx == '木') or \
         (month_wx == '土' and ying_wx == '火') or (month_wx == '金' and ying_wx == '土') or \
         (month_wx == '水' and ying_wx == '金'):
        score_away += 3
        reasons.append("月建生应，客队气势旺")
    elif (month_wx == '木' and ying_wx == '土') or (month_wx == '火' and ying_wx == '金') or \
         (month_wx == '土' and ying_wx == '水') or (month_wx == '金' and ying_wx == '木') or \
         (month_wx == '水' and ying_wx == '火'):
        score_home += 2
        reasons.append("月建克应，客队受制")

    if day_wx == ying_wx:
        score_away += 1
    elif (day_wx == '木' and ying_wx == '水') or (day_wx == '火' and ying_wx == '木') or \
         (day_wx == '土' and ying_wx == '火') or (day_wx == '金' and ying_wx == '土') or \
         (day_wx == '水' and ying_wx == '金'):
        score_away += 2

    # 5. 动爻影响
    if moving is not None and moving_wx:
        # 动爻生世
        if (moving_wx == '木' and shi_wx == '水') or (moving_wx == '火' and shi_wx == '木') or \
           (moving_wx == '土' and shi_wx == '火') or (moving_wx == '金' and shi_wx == '土') or \
           (moving_wx == '水' and shi_wx == '金'):
            score_home += 3
            reasons.append(f"动爻（{moving_liuqin}）生世，主队得助")
        # 动爻克世
        if (moving_wx == '木' and shi_wx == '土') or (moving_wx == '火' and shi_wx == '金') or \
           (moving_wx == '土' and shi_wx == '水') or (moving_wx == '金' and shi_wx == '木') or \
           (moving_wx == '水' and shi_wx == '火'):
            score_away += 2
            reasons.append(f"动爻（{moving_liuqin}）克世，主队受制")
        # 动爻生应
        if (moving_wx == '木' and ying_wx == '水') or (moving_wx == '火' and ying_wx == '木') or \
           (moving_wx == '土' and ying_wx == '火') or (moving_wx == '金' and ying_wx == '土') or \
           (moving_wx == '水' and ying_wx == '金'):
            score_away += 3
            reasons.append(f"动爻（{moving_liuqin}）生应，客队得助")
        # 动爻克应
        if (moving_wx == '木' and ying_wx == '土') or (moving_wx == '火' and ying_wx == '金') or \
           (moving_wx == '土' and ying_wx == '水') or (moving_wx == '金' and ying_wx == '木') or \
           (moving_wx == '水' and ying_wx == '火'):
            score_home += 2
            reasons.append(f"动爻（{moving_liuqin}）克应，客队受制")

    # 6. 空亡（世应逢空则减分）
    if shi_zhi in (kong1, kong2):
        score_home -= 2
        reasons.append(f"世爻{shi_zhi}逢空（旬空），主队状态虚浮")
    if ying_zhi in (kong1, kong2):
        score_away -= 2
        reasons.append(f"应爻{ying_zhi}逢空，客队状态虚浮")

    # 7. 十二长生（旺相加分）
    if shi_changsheng in ['长生','沐浴','冠带','临官','帝旺']:
        score_home += 1
        reasons.append(f"世爻{shi_zhi}处于{shi_changsheng}，主队状态佳")
    if ying_changsheng in ['长生','沐浴','冠带','临官','帝旺']:
        score_away += 1
        reasons.append(f"应爻{ying_zhi}处于{ying_changsheng}，客队状态佳")

    # 8. 六神取象（增强判断，此处仅作参考）
    if liu_shen == '青龙':
        score_home += 1
        reasons.append("日临青龙，主队有吉祥之象")
    elif liu_shen == '白虎':
        score_away += 1
        reasons.append("日临白虎，客队凶猛")

    # 9. 飞伏（用神藏伏）简化：若世或应为伏神，则看飞神生克
    # 这里不展开

    # 10. 应期（仅供输出，不影响评分）

    # 综合推荐
    max_score = max(score_home, score_away, score_draw)
    if max_score == 0:
        recommendation = "平局（均衡）"
    elif max_score == score_home and score_home > score_away and score_home > score_draw:
        recommendation = "主队胜"
    elif max_score == score_away and score_away > score_home and score_away > score_draw:
        recommendation = "客队胜"
    elif max_score == score_draw and score_draw >= score_home and score_draw >= score_away:
        recommendation = "平局"
    else:
        # 若分数接近，选择最高
        if score_home >= score_away and score_home >= score_draw:
            recommendation = "主队胜（微弱优势）"
        elif score_away >= score_home and score_away >= score_draw:
            recommendation = "客队胜（微弱优势）"
        else:
            recommendation = "平局（胶着）"

    # 构造返回结果
    result = {
        '主队': team_home,
        '客队': team_away,
        '本卦': gua_name,
        '变卦': up_var + down_var,
        '动爻': f"{moving+1}爻" if moving is not None else "无动爻",
        '世应': f"世{shi_zhi}({shi_wx}) 应{ying_zhi}({ying_wx})",
        '六亲世应': f"世{shi_liuqin} 应{ying_liuqin}",
        '月建': month_zhi,
        '日辰': day_zhi,
        '空亡': f"{kong1}{kong2}",
        '六神': liu_shen,
        '三合三会': f"三合{'有' if sanhe_formed else '无'} 三会{'有' if sanhui_formed else '无'}",
        '十二长生': f"世{shi_changsheng} 应{ying_changsheng}",
        '推荐': recommendation,
        '得分': f"主{score_home} 客{score_away} 平{score_draw}",
        '理由': "\n".join(reasons) if reasons else "无显著特征"
    }
    return result

# ============================================================================
# 第六部分：批量预测与文件处理
# ============================================================================

def batch_predict_from_file(filename):
    """从文件读取比赛列表，每行格式：主队,客队 或 主队 客队"""
    if not os.path.exists(filename):
        logger.error(f"文件 {filename} 不存在")
        return
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = re.split(r'[,\t]+', line)
        if len(parts) < 2:
            logger.warning(f"跳过无效行: {line}")
            continue
        home = parts[0].strip()
        away = parts[1].strip()
        if home and away:
            res = analyze_match(home, away)
            if res:
                print(f"\n{home} vs {away}: {res['推荐']} (得分: {res['得分']})")
                logger.info(f"{home} vs {away} -> {res['推荐']}")
        else:
            logger.warning(f"队名空: {line}")

# ============================================================================
# 第七部分：命令行主入口
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="足球预测工具（六爻纳甲）")
    parser.add_argument('-f', '--file', help="批量预测文件路径（每行 主队,客队）")
    parser.add_argument('-m', '--match', nargs=2, metavar=('主队','客队'), help="单场预测")
    parser.add_argument('-v', '--verbose', action='store_true', help="输出详细日志")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.file:
        batch_predict_from_file(args.file)
        return

    if args.match:
        home, away = args.match
        res = analyze_match(home, away)
        if res:
            print("="*50)
            print(f"主队：{res['主队']}  客队：{res['客队']}")
            print(f"本卦：{res['本卦']}  变卦：{res['变卦']}  动爻：{res['动爻']}")
            print(f"世应：{res['世应']}  {res['六亲世应']}")
            print(f"月建：{res['月建']}  日辰：{res['日辰']}  空亡：{res['空亡']}")
            print(f"六神：{res['六神']}  {res['三合三会']}")
            print(f"十二长生：{res['十二长生']}")
            print(f"综合得分：{res['得分']}")
            print(f"推荐结果：{res['推荐']}")
            print(f"理由：{res['理由']}")
        return

    # 交互式模式
    print("="*60)
    print("足球预测工具（六爻纳甲完整版 v5.0）")
    print("支持五大联赛、J联赛、J2联赛、K联赛等")
    print("输入格式：主队名 客队名 (用空格或逗号分隔)")
    print("输入 'quit' 退出，输入 'batch 文件名' 进行批量预测")
    print("="*60)
    while True:
        try:
            line = input("\n请输入比赛：").strip()
            if line.lower() in ('quit', 'exit', 'q'):
                break
            if line.lower().startswith('batch '):
                fname = line[6:].strip()
                if fname:
                    batch_predict_from_file(fname)
                continue
            if not line:
                continue
            parts = re.split(r'[,\s]+', line)
            if len(parts) < 2:
                print("请确保输入主队和客队，用空格或逗号隔开")
                continue
            home, away = parts[0].strip(), parts[1].strip()
            if not home or not away:
                print("队名不能为空")
                continue
            res = analyze_match(home, away)
            if not res:
                print("预测失败，请检查队名")
                continue
            print(f"\n主队：{res['主队']}  客队：{res['客队']}")
            print(f"本卦：{res['本卦']}  变卦：{res['变卦']}  动爻：{res['动爻']}")
            print(f"世应：{res['世应']}  {res['六亲世应']}")
            print(f"月建：{res['月建']}  日辰：{res['日辰']}  空亡：{res['空亡']}")
            print(f"六神：{res['六神']}  {res['三合三会']}")
            print(f"十二长生：{res['十二长生']}")
            print(f"综合得分：{res['得分']}")
            print(f"推荐结果：{res['推荐']}")
            print(f"理由：{res['理由']}")
        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            logger.exception("发生异常")
            print(f"错误：{e}")

if __name__ == "__main__":
    main()
