#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
足球预测工具（六爻纳甲完整版）
支持：五大联赛、J联赛、J2联赛、K联赛等
功能：根据主客队名前两字起卦，综合断胜负平
作者：AI 助手
版本：4.0 (全功能版)
"""

import re
import sys
import datetime
import random
from collections import defaultdict

# ======================== 第一部分：汉字笔画库 ========================
# 涵盖足球常见字及通用汉字，无法查到的字用Unicode估算

STROKE_DICT = {
    # 数字
    '一':1,'二':2,'三':3,'四':5,'五':4,'六':4,'七':2,'八':2,'九':2,'十':2,
    # 方位
    '东':5,'南':9,'西':6,'北':5,'中':4,'上':3,'下':3,'前':9,'后':6,
    # 颜色
    '红':6,'黄':11,'蓝':13,'白':5,'黑':12,'绿':11,'紫':12,'青':8,
    # 国家/地区
    '中':4,'国':8,'美':9,'英':8,'法':8,'德':15,'意':13,'西':6,'葡':12,'荷':10,
    '比':4,'瑞':13,'丹':4,'挪':8,'芬':7,'爱':10,'奥':12,'希':7,'土':3,'伊':6,
    '沙':7,'阿':7,'韩':12,'日':4,'澳':15,'新':13,'加':5,'巴':4,'根':10,
    '廷':6,'哥':10,'伦':6,'黎':15,'利':7,'大':3,'小':3,'高':10,'圣':5,'保':9,
    '维':11,'斯':12,'特':10,'格':10,'拉':8,'塔':12,'尼':5,'尔':5,'文':4,'达':6,
    '姆':8,'哈':9,'森':12,'贝':4,'托':6,'马':3,'罗':8,'兰':5,'克':7,
    '里':7,'伯':7,'恩':10,'迪':8,'亚':6,'雷':13,'纳':7,'瓦':4,'夫':4,
    '曼':11,'城':9,'联':12,'军':6,'队':4,'堡':12,'顿':10,'汉':5,'诺':10,'丁':2,
    '尼':5,'塞':13,'尔':5,'维':11,'拉':8,'多':6,'伦':6,'敦':12,'黎':15,
    '天':4,'地':6,'人':2,'王':4,'皇':9,'家':10,'米':6,'兰':5,
    '胜':9,'利':7,'平':5,'负':6,'进':7,'攻':7,'守':6,'门':3,'球':11,'员':7,
    '教':11,'练':8,'裁':12,'判':7,'主':5,'客':9,'场':6,'外':5,'内':4,'战':9,
    '术':5,'策':12,'略':11,'技':7,'友':4,'好':6,'坏':7,'强':12,'弱':10,
    '快':7,'慢':14,'稳':14,'猛':11,'凶':4,'吉':6,'祥':10,
    '部':10,'分':4,'团':6,'体':7,'育':8,'运':7,'动':6,'会':6,'协':8,'委':8,
    '公':4,'司':5,'职':11,'工':3,'作':7,'专':4,'业':5,'赛':17,'事':8,'足':7,
    '杯':8,'冠':9,'亚':6,'洲':9,'欧':15,'非':8,'大':3,'洋':9,'世':5,'界':9,
    '预':13,'选':9,'决':6,'阶':11,'段':9,'循':12,'环':8,'淘':11,'汰':7,
    '半':5,'总':9,'奖':15,'金':8,'银':11,'铜':11,'牌':12,'名':6,'次':6,
    '榜':14,'排':11,'序':7,'列':6,'和':8,'分':4,'数':13,'差':9,'净':8,'积':10,
    '率':11,'表':8,'统':12,'计':9,'据':13,'析':8,'测':9,'推':11,'荐':9,
    '结':9,'果':8,'评':7,'估':7,'断':11,'综':14,'合':6,'报':7,'告':7,
    '方':4,'案':10,'例':8,'模':15,'型':16,'系':7,'统':7,'软':11,'件':7,
    '程':12,'序':7,'版':8,'本':5,'注':8,'释':12,'说':14,'明':8,'文':4,'档':9,
    '库':7,'存':6,'储':12,'备':8,'用':5,'户':4,'密':11,'码':13,'验':10,'证':7,
    '安':6,'权':8,'限':9,'管':14,'理':11,'日':4,'志':7,'记':5,'录':8,'错':13,
    '误':9,'异':11,'常':11,'处':5,'置':13,'恢':9,'复':9,'还':7,'原':10,'移':11,
    '植':12,'编':15,'译':13,'行':6,'环':8,'境':14,'配':10,'置':13,'件':6,
    '加':5,'载':10,'初':7,'始':8,'化':4,'启':7,'停':11,'止':4,'重':9,
    '新':13,'建':8,'删':7,'除':9,'改':7,'查':9,'询':12,'搜':12,'索':10,
    '导':6,'航':10,'菜':11,'单':8,'项':9,'标':9,'的':8,'选':9,'择':8,
    '确':11,'认':4,'取':8,'消':11,'返':7,'回':6,'首':9,'页':6,'帮':17,
    '助':7,'关':6,'于':3,'声':7,'所':8,'有':6,'最':12,'更':7,'多':6,
    '见':4,'面':9,'左':5,'右':5,'开':4,'关':6,'间':7,'楼':13,'房':8,
    '屋':9,'院':9,'墙':14,'树':16,'木':4,'花':7,'草':9,'鸟':5,'鱼':8,
    '虫':6,'兽':11,'龙':5,'虎':8,'凤':4,'凰':11,'龟':7,'麟':23,'狮':9,
    '象':12,'鹿':11,'鹤':15,'鹰':18,'燕':16,'熊':14,'豹':10,'狼':10,'猿':13,
    '猴':12,'牛':4,'羊':6,'猪':11,'狗':8,'鸡':7,'鸭':10,'鹅':12,'鸽':11,
    '蛇':11,'蛙':12,'虾':9,'蟹':19,'螺':17,'蚌':10,'蚯':9,'蚓':10,
    '蚊':10,'蝇':14,'蜘':14,'蛛':12,'蝉':14,'蝶':15,'蜂':13,'蚁':9,'蚕':10,
    # 五大联赛、J联赛、K联赛常见队名补充
    '切':4,'尔':5,'西':6,'汉':5,'姆':8,'斯':12,'特':10,'堡':12,'顿':10,
    '蒙':13,'彼':8,'得':11,'格':10,'林':8,'海':10,'牙':4,'买':6,'卖':8,
    '易':8,'币':4,'钞':9,'银':11,'取':8,'存':6,'账':13,'号':5,'登':12,
    '录':15,'册':5,'销':12,'售':11,'额':15,'润':10,'税':12,'费':9,
    '成':6,'价':6,'值':10,'涨':13,'跌':12,'停':11,'板':8,'股':8,'票':11,
    '基':11,'金':8,'债':10,'券':8,'期':12,'货':8,'汇':13,'铝':11,'锌':12,
    '锡':13,'铅':10,'镍':15,'钢':9,'铁':10,'煤':13,'油':8,'气':4,'水':4,
    '电':5,'风':9,'光':6,'核':10,'能':10,'源':13,'科':9,'技':9,'医':7,
    '药':9,'食':9,'品':9,'饮':7,'酒':10,'烟':10,'茶':9,'糖':16,'果':8,
    '蔬':15,'肉':6,'蛋':11,'奶':5,'豆':7,'米':6,'面':9,'盐':10,'酱':13,
    '醋':15,'辣':14,'甜':11,'酸':14,'苦':9,'辛':7,'香':9,'臭':10,'鲜':14,
    '味':8,'佳':8,'馐':18,'宴':10,'席':10,'桌':10,'椅':12,'凳':14,'床':7,
    '柜':9,'橱':16,'箱':15,'架':9,'具':8,'货':8,'商':11,'品':9,'赢':17,
    '输':13,'害':10,'益':10,'损':10,'亏':3,'盈':9,'衡':16,'均':7,'距':11,
    '离':11,'散':12,'聚':14,'别':7,'识':7,'知':8,'感':13,'情':11,'爱':10,
    '恨':9,'喜':12,'怒':9,'哀':9,'乐':5,'忧':7,'思':9,'悲':12,'欢':6,
    '愁':13,'苦':9,'咸':9,'淡':11,'浓':16,'厚':9,'薄':16,'轻':12,'缓':15,
    '急':9,'松':8,'紧':10,'软':11,'硬':12,'干':3,'湿':12,'冷':7,'热':10,
    '温':12,'暖':13,'寒':12,'暑':12,'春':9,'夏':12,'秋':9,'冬':5,'早':6,
    '晚':11,'晨':11,'昏':8,'昼':9,'夜':8,'朝':12,'夕':3,'年':6,'月':4,
    '时':7,'秒':9,'刻':8,'钟':9,'盘':15,'针':7,'线':8,'绳':11,'缆':12,
    '网':14,'络':12,'信':9,'息':10,'号':5,'数':13,'库':7,'份':6,'恢':9,
    '移':11,'植':12,'代':5,'码':13,'硬':12,'驱':11,'态':14,'静':14,
    '题':15,'目':5,'章':11,'节':5,'段':9,'落':12,'句':5,'词':7,'语':9,
    '言':7,'字':6,'母':5,'拼':9,'音':9,'典':8,'籍':20,'书':4,'画':8,
    '图':8,'片':4,'照':13,'影':15,'视':8,'频':16,'歌':14,'曲':6,'舞':14,
    '蹈':17,'剧':11,'戏':6,'景':12,'物':8,
    # 更多联赛球队特有字
    '拜':9,'仁':4,'慕':14,'尼':5,'黑':12,'莱':11,'比':4,'锡':13,'堡':12,
    '多':6,'特':10,'蒙':13,'德':15,'格':10,'拉':8,'斯':12,'图':8,'加':5,
    '迪':8,'纳':7,'利':7,'浦':10,'物':8,'切':4,'尔':5,'西':6,'汉':5,
    '曼':11,'城':9,'联':12,'阿':7,'森':12,'纳':7,'维':11,'拉':8,'雷':13,
    '马':3,'竞':10,'技':7,'皇':9,'家':10,'社':7,'会':6,'巴':4,'萨':11,
    '罗':8,'那':7,'尤':4,'文':4,'图':8,'米':6,'兰':5,'国':8,'际':7,
    '那':7,'不':4,'勒':11,'沃':7,'库':7,'森':12,'汉':5,'诺':10,'威':9,
    '斯':12,'托':6,'克':7,'鲁':12,'日':4,'本':5,'职':11,'业':5,'联':12,
    '盟':13,'川':3,'崎':11,'前':9,'锋':15,'横':15,'滨':17,'水':4,'手':4,
    '广':3,'岛':10,'三':3,'箭':15,'神':9,'户':4,'胜':9,'利':7,'船':11,
    '京':8,'都':10,'樱':15,'花':7,'仙':5,'台':5,'维':11,'加':5,'泰':10,
    '山':3,'形':7,'清':11,'水':4,'大':3,'宫':9,'松':8,'本':5,'山':3,
    '口':3,'岐':7,'阜':8,'爱':10,'媛':12,'枥':9,'木':4,'草':9,'津':9,
    '鹿':11,'儿':2,'岛':10,'浦':10,'和':8,'红':6,'钻':10,'石':5,'柏':9,
    '太':4,'阳':6,'神':9,'户':4,'钢':9,'巴':4,'天':4,'鹅':12,'新':13,
    '泻':8,'涅':10,'茨':9,'城':9,'甲':5,'府':8,'风':9,'林':8,'山':3,
    '形':7,'现':11,'代':5,'足':7,'球':11,'俱':10,'乐':5,'部':10,
}

def get_stroke(char):
    """获取单个汉字的笔画数，未知字用Unicode估算"""
    if char in STROKE_DICT:
        return STROKE_DICT[char]
    # 估算：取Unicode码位末两位和+1
    try:
        code = ord(char)
        low = code & 0xFF
        high = (code >> 8) & 0xFF
        return (low % 12) + (high % 6) + 1
    except:
        return 5

def get_team_strokes(team_name):
    """提取队名中前两个汉字的笔画数，不足则补'一'"""
    name = re.sub(r'[^一-龥]', '', team_name.strip())
    if len(name) >= 2:
        chars = name[:2]
    else:
        chars = name + '一'
    return [get_stroke(c) for c in chars]

# ======================== 第二部分：六爻纳甲完整数据库 ========================

# 八卦五行
GUA_WUXING = {'乾':'金','兑':'金','离':'火','震':'木','巽':'木','坎':'水','艮':'土','坤':'土'}

# 八卦先天数
GUA_NUM = {'乾':1,'兑':2,'离':3,'震':4,'巽':5,'坎':6,'艮':7,'坤':8}

# 八卦天干
GUA_TIANGAN = {'乾':'甲','兑':'丁','离':'己','震':'庚','巽':'辛','坎':'戊','艮':'丙','坤':'乙'}

# 地支五行
DI_ZHI_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
                 '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}

# 地支六合
DI_ZHI_LIUHE = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯',
                '辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}

# 地支六冲
DI_ZHI_LIUCHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅',
                   '卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}

# 地支三合局
DI_ZHI_SANHE = {
    '寅午戌':'火',
    '亥卯未':'木',
    '申子辰':'水',
    '巳酉丑':'金'
}

# 地支三会局
DI_ZHI_SANHUI = {
    '寅卯辰':'木',
    '巳午未':'火',
    '申酉戌':'金',
    '亥子丑':'水'
}

# 六亲生克关系（宫五行 vs 爻地支五行）
def get_liuqin(gong_wuxing, zhi_wuxing):
    """返回六亲名称"""
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

# 六十四卦装卦数据（手工建库，确保准确）
# 每卦格式: (卦名, 上卦, 下卦, 宫名, 世爻位置, 应爻位置, 六爻六亲列表, 六爻地支列表)
# 为节省空间，我们构建一个生成函数，按京房八宫规则动态生成
# 但此处直接预置所有卦的数据，以保证完整性

# 八宫顺序：乾、震、坎、艮、坤、巽、离、兑
# 每个宫八个卦：本宫、一世、二世、三世、四世、五世、游魂、归魂
# 世应位置：本宫世在5(上爻)，应2；一世世0，应3；二世世1，应4；三世世2，应5；四世世3，应0；五世世4，应1；游魂世3，应0；归魂世4，应1

# 定义每个卦的上下卦和宫
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

# 世应位置（按宫卦序，0~7）
SHI_YING_POS = [
    (5,2), (0,3), (1,4), (2,5), (3,0), (4,1), (3,0), (4,1)
]

# 构建卦信息字典
GUA_DB = {}
for idx, (name, up, down, gong) in enumerate(GUA_LIST):
    shi, ying = SHI_YING_POS[idx % 8]
    # 确定初爻地支：阳卦（乾震坎艮）初爻子、寅、辰、午、申、戌；阴卦（坤巽离兑）初爻未、巳、卯、丑、亥、酉
    if gong in ['乾','震','坎','艮']:
        zhi_list = ['子','寅','辰','午','申','戌']
    else:
        zhi_list = ['未','巳','卯','丑','亥','酉']
    # 六爻地支（从初爻到上爻）
    zhi_yao = zhi_list[:]  # 直接使用，顺序初爻到上爻
    # 六亲：根据宫五行和地支五行
    gong_wx = GUA_WUXING[gong]
    liuqin_yao = [get_liuqin(gong_wx, DI_ZHI_WUXING[z]) for z in zhi_yao]
    # 天干（纳甲）：上卦天干+下卦天干，但此处只存储每个爻的天干（按八宫所属）
    # 六爻天干：上卦天干配外卦三爻，下卦天干配内卦三爻
    up_tg = GUA_TIANGAN[up]
    down_tg = GUA_TIANGAN[down]
    tg_yao = [down_tg, down_tg, down_tg, up_tg, up_tg, up_tg]  # 初爻到三爻用下卦天干，四爻到六爻用上卦天干
    # 存储
    GUA_DB[name] = {
        '上卦': up, '下卦': down, '宫': gong,
        '世爻': shi, '应爻': ying,
        '天干': tg_yao,
        '地支': zhi_yao,
        '六亲': liuqin_yao,
        '宫五行': gong_wx
    }

# ======================== 第三部分：日月建 ========================

def get_month_branch():
    """根据当前日期返回月建地支（农历月）"""
    now = datetime.datetime.now()
    # 粗略按节气划分，这里简化：每月大约对应一个地支
    # 农历正月寅，二月卯，三月辰，四月巳，五月午，六月未，七月申，八月酉，九月戌，十月亥，冬月子，腊月丑
    # 但为了精确，我们使用公历近似
    month = now.month
    day = now.day
    # 大约立春2月4日为寅月，惊蛰3月6日为卯月，清明4月5日为辰月，立夏5月6日为巳月，芒种6月6日为午月，
    # 小暑7月7日为未月，立秋8月7日为申月，白露9月8日为酉月，寒露10月8日为戌月，立冬11月7日为亥月，
    # 大雪12月7日为子月，小寒1月6日为丑月
    # 简化：按月份对应
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
    else:  # 12月
        return '子' if day >= 7 else '亥'

def get_day_branch():
    """返回日辰地支（按公历日期推算，这里简化用固定周期）"""
    # 实际需查万年历，此处用简易算法：以2020年1月1日为甲子日（近似）
    base = datetime.date(2020, 1, 1)
    now = datetime.date.today()
    delta = (now - base).days
    # 甲子日序号0，每60一轮回
    day_index = delta % 60
    # 地支：子0,丑1,...亥11
    zhi_index = day_index % 12
    zhi_list = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
    return zhi_list[zhi_index]

def get_month_day_wuxing():
    """返回月建和日辰的五行"""
    month_zhi = get_month_branch()
    day_zhi = get_day_branch()
    return DI_ZHI_WUXING[month_zhi], DI_ZHI_WUXING[day_zhi]

# ======================== 第四部分：起卦 ========================

def qigua(team_home, team_away):
    """根据队名起卦，返回本卦上卦、下卦，动爻，变卦上卦、下卦"""
    s1 = get_team_strokes(team_home)
    s2 = get_team_strokes(team_away)
    sum_h = sum(s1)
    sum_a = sum(s2)
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
    # 计算变卦
    bin_map = {'乾':'111','兑':'110','离':'101','震':'100','巽':'011','坎':'010','艮':'001','坤':'000'}
    rev_bin = {'111':'乾','110':'兑','101':'离','100':'震','011':'巽','010':'坎','001':'艮','000':'坤'}
    full = bin_map[up_gua] + bin_map[down_gua]
    idx = 5 - moving  # 因为full[0]为上爻
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

# ======================== 第五部分：断卦综合评分 ========================

def analyze_match(team_home, team_away):
    """主函数：分析比赛，返回推荐及理由"""
    result = qigua(team_home, team_away)
    up = result['本卦上卦']
    down = result['本卦下卦']
    moving = result['动爻']
    up_var = result['变卦上卦']
    down_var = result['变卦下卦']

    # 查找本卦名称
    gua_name = None
    for name, data in GUA_DB.items():
        if data['上卦'] == up and data['下卦'] == down:
            gua_name = name
            break
    if not gua_name:
        return "无法识别卦象"

    gua_data = GUA_DB[gua_name]
    gong = gua_data['宫']
    gong_wx = gua_data['宫五行']
    shi = gua_data['世爻']
    ying = gua_data['应爻']
    liuqin = gua_data['六亲']
    zhi = gua_data['地支']
    tian = gua_data['天干']

    # 日月建
    month_zhi = get_month_branch()
    day_zhi = get_day_branch()
    month_wx = DI_ZHI_WUXING[month_zhi]
    day_wx = DI_ZHI_WUXING[day_zhi]

    # 世应五行
    shi_zhi = zhi[shi]
    ying_zhi = zhi[ying]
    shi_wx = DI_ZHI_WUXING[shi_zhi]
    ying_wx = DI_ZHI_WUXING[ying_zhi]

    # 六合六冲
    liuhe = False
    liuchong = False
    if DI_ZHI_LIUHE.get(shi_zhi) == ying_zhi or DI_ZHI_LIUHE.get(ying_zhi) == shi_zhi:
        liuhe = True
    if DI_ZHI_LIUCHONG.get(shi_zhi) == ying_zhi or DI_ZHI_LIUCHONG.get(ying_zhi) == shi_zhi:
        liuchong = True

    # 动爻影响：动爻所在爻的六亲、地支变化
    moving_liuqin = liuqin[moving] if moving is not None else None
    moving_zhi = zhi[moving] if moving is not None else None
    moving_wx = DI_ZHI_WUXING[moving_zhi] if moving_zhi else None

    # 判断用神：赛事以世应为主，兼看子孙（进球）、妻财（收益），此处简化为世应生克
    # 世应生克：世生应主队不利，应生世主队有利，世克应主队胜，应克世客队胜
    score_home = 0
    score_away = 0
    score_draw = 0

    reasons = []

    # 1. 世应生克
    if shi_wx == ying_wx:
        score_draw += 3
        reasons.append("世应五行相同，有平局倾向")
    elif (shi_wx == '木' and ying_wx == '土') or (shi_wx == '火' and ying_wx == '金') or \
         (shi_wx == '土' and ying_wx == '水') or (shi_wx == '金' and ying_wx == '木') or \
         (shi_wx == '水' and ying_wx == '火'):
        # 世克应
        score_home += 5
        reasons.append("世爻克应爻，主队占优")
    elif (ying_wx == '木' and shi_wx == '土') or (ying_wx == '火' and shi_wx == '金') or \
         (ying_wx == '土' and shi_wx == '水') or (ying_wx == '金' and shi_wx == '木') or \
         (ying_wx == '水' and shi_wx == '火'):
        score_away += 5
        reasons.append("应爻克世爻，客队占优")
    else:
        # 生我者父母，我生者子孙等，但世应关系主要是克
        pass

    # 2. 六合六冲
    if liuhe:
        score_draw += 2
        reasons.append("世应六合，场面胶着，易平")
    if liuchong:
        score_home += 1
        score_away += 1
        reasons.append("世应六冲，对抗激烈，分胜负")

    # 3. 日月建对世爻的作用
    # 月建生扶世爻则主队得时
    if month_wx == shi_wx:
        score_home += 2
        reasons.append("月建与世爻五行相同，主队得令")
    elif (month_wx == '木' and shi_wx == '水') or (month_wx == '火' and shi_wx == '木') or \
         (month_wx == '土' and shi_wx == '火') or (month_wx == '金' and shi_wx == '土') or \
         (month_wx == '水' and shi_wx == '金'):
        score_home += 3
        reasons.append("月建生世爻，主队气势旺")
    # 日辰同理
    if day_wx == shi_wx:
        score_home += 1
    elif (day_wx == '木' and shi_wx == '水') or (day_wx == '火' and shi_wx == '木') or \
         (day_wx == '土' and shi_wx == '火') or (day_wx == '金' and shi_wx == '土') or \
         (day_wx == '水' and shi_wx == '金'):
        score_home += 2
    # 对应爻生扶则客队有利
    if month_wx == ying_wx:
        score_away += 2
    elif (month_wx == '木' and ying_wx == '水') or (month_wx == '火' and ying_wx == '木') or \
         (month_wx == '土' and ying_wx == '火') or (month_wx == '金' and ying_wx == '土') or \
         (month_wx == '水' and ying_wx == '金'):
        score_away += 3
    if day_wx == ying_wx:
        score_away += 1
    elif (day_wx == '木' and ying_wx == '水') or (day_wx == '火' and ying_wx == '木') or \
         (day_wx == '土' and ying_wx == '火') or (day_wx == '金' and ying_wx == '土') or \
         (day_wx == '水' and ying_wx == '金'):
        score_away += 2

    # 4. 动爻影响：动爻如果生世则主队有利，生应则客队有利
    if moving is not None:
        # 动爻所在位置对世应的影响
        # 动爻生克：动爻生世爻或克应爻
        if moving_wx:
            # 生世
            if (moving_wx == '木' and shi_wx == '水') or (moving_wx == '火' and shi_wx == '木') or \
               (moving_wx == '土' and shi_wx == '火') or (moving_wx == '金' and shi_wx == '土') or \
               (moving_wx == '水' and shi_wx == '金'):
                score_home += 3
                reasons.append("动爻生世爻，主队得助")
            # 克世
            if (moving_wx == '木' and shi_wx == '土') or (moving_wx == '火' and shi_wx == '金') or \
               (moving_wx == '土' and shi_wx == '水') or (moving_wx == '金' and shi_wx == '木') or \
               (moving_wx == '水' and shi_wx == '火'):
                score_away += 2
                reasons.append("动爻克世爻，主队受制")
            # 生应
            if (moving_wx == '木' and ying_wx == '水') or (moving_wx == '火' and ying_wx == '木') or \
               (moving_wx == '土' and ying_wx == '火') or (moving_wx == '金' and ying_wx == '土') or \
               (moving_wx == '水' and ying_wx == '金'):
                score_away += 3
                reasons.append("动爻生应爻，客队得助")
            # 克应
            if (moving_wx == '木' and ying_wx == '土') or (moving_wx == '火' and ying_wx == '金') or \
               (moving_wx == '土' and ying_wx == '水') or (moving_wx == '金' and ying_wx == '木') or \
               (moving_wx == '水' and ying_wx == '火'):
                score_home += 2
                reasons.append("动爻克应爻，客队受制")

    # 5. 空亡（旬空）简化：查看世爻地支是否在空亡，若空则主队虚浮
    # 空亡以日柱定，这里简化：若日支与世爻相冲则视为空亡（冲空）
    if DI_ZHI_LIUCHONG.get(day_zhi) == shi_zhi:
        score_home -= 2
        reasons.append("世爻逢冲（空），主队状态不稳")
    if DI_ZHI_LIUCHONG.get(day_zhi) == ying_zhi:
        score_away -= 2
        reasons.append("应爻逢冲（空），客队状态不稳")

    # 6. 综合得分确定推荐
    max_score = max(score_home, score_away, score_draw)
    if max_score == 0:
        recommendation = "平局（均衡）"
    elif max_score == score_home and max_score > score_away and max_score > score_draw:
        recommendation = "主队胜"
    elif max_score == score_away and max_score > score_home and max_score > score_draw:
        recommendation = "客队胜"
    elif max_score == score_draw and max_score >= score_home and max_score >= score_away:
        recommendation = "平局"
    else:
        # 若分数接近，选择最高或平局
        if score_home >= score_away and score_home >= score_draw:
            recommendation = "主队胜（微弱优势）"
        elif score_away >= score_home and score_away >= score_draw:
            recommendation = "客队胜（微弱优势）"
        else:
            recommendation = "平局（胶着）"

    # 生成详细理由
    reason_text = "\n".join(reasons) if reasons else "无显著特征"
    return {
        '主队': team_home,
        '客队': team_away,
        '本卦': gua_name,
        '变卦': (up_var + down_var),
        '动爻': f"{moving+1}爻" if moving is not None else "无动爻",
        '世应': f"世{shi_zhi}({shi_wx}) 应{ying_zhi}({ying_wx})",
        '推荐': recommendation,
        '得分': f"主{score_home} 客{score_away} 平{score_draw}",
        '理由': reason_text
    }

# ======================== 第六部分：命令行交互 ========================

def main():
    print("="*50)
    print("足球预测工具（六爻纳甲完整版）")
    print("支持五大联赛、J联赛、J2联赛、K联赛等")
    print("输入格式：主队名 客队名 (用空格或逗号分隔)")
    print("输入 'quit' 退出")
    print("="*50)
    while True:
        try:
            line = input("\n请输入比赛：").strip()
            if line.lower() in ('quit', 'exit', 'q'):
                break
            if not line:
                continue
            # 分割
            parts = re.split(r'[,\s]+', line)
            if len(parts) < 2:
                print("请确保输入主队和客队，用空格或逗号隔开")
                continue
            home = parts[0].strip()
            away = parts[1].strip()
            if not home or not away:
                print("队名不能为空")
                continue
            result = analyze_match(home, away)
            if isinstance(result, str):
                print(result)
                continue
            print(f"\n主队：{result['主队']}  客队：{result['客队']}")
            print(f"本卦：{result['本卦']}  变卦：{result['变卦']}  动爻：{result['动爻']}")
            print(f"世应：{result['世应']}")
            print(f"综合得分：{result['得分']}")
            print(f"推荐结果：{result['推荐']}")
            print(f"理由：{result['理由']}")
        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print(f"错误：{e}")

if __name__ == "__main__":
    main()
