# -*- coding: utf-8 -*-
"""
六爻足球预测（完整无删减版）
基于主客队名前两字 + 比赛时间起卦，预测胜平负
包含：完整64卦映射、五行生克、体用判定、Streamlit界面
"""

import streamlit as st
import datetime

# ============================================================
# 第一部分：数据层（六十四卦完整数据）
# ============================================================

NUM_TO_GUA = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤"
}

GUA_MAP = {
    ("乾", "乾"): "乾", ("乾", "坤"): "否", ("乾", "震"): "无妄",
    ("乾", "巽"): "姤", ("乾", "坎"): "讼", ("乾", "离"): "同人",
    ("乾", "艮"): "遁", ("乾", "兑"): "履",
    ("坤", "乾"): "泰", ("坤", "坤"): "坤", ("坤", "震"): "复",
    ("坤", "巽"): "升", ("坤", "坎"): "师", ("坤", "离"): "明夷",
    ("坤", "艮"): "谦", ("坤", "兑"): "临",
    ("震", "乾"): "大壮", ("震", "坤"): "豫", ("震", "震"): "震",
    ("震", "巽"): "恒", ("震", "坎"): "解", ("震", "离"): "丰",
    ("震", "艮"): "小过", ("震", "兑"): "归妹",
    ("巽", "乾"): "小畜", ("巽", "坤"): "观", ("巽", "震"): "益",
    ("巽", "巽"): "巽", ("巽", "坎"): "涣", ("巽", "离"): "家人",
    ("巽", "艮"): "渐", ("巽", "兑"): "中孚",
    ("坎", "乾"): "需", ("坎", "坤"): "比", ("坎", "震"): "屯",
    ("坎", "巽"): "井", ("坎", "坎"): "坎", ("坎", "离"): "既济",
    ("坎", "艮"): "蹇", ("坎", "兑"): "节",
    ("离", "乾"): "大有", ("离", "坤"): "晋", ("离", "震"): "噬嗑",
    ("离", "巽"): "鼎", ("离", "坎"): "未济", ("离", "离"): "离",
    ("离", "艮"): "旅", ("离", "兑"): "睽",
    ("艮", "乾"): "大畜", ("艮", "坤"): "剥", ("艮", "震"): "颐",
    ("艮", "巽"): "蛊", ("艮", "坎"): "蒙", ("艮", "离"): "贲",
    ("艮", "艮"): "艮", ("艮", "兑"): "损",
    ("兑", "乾"): "夬", ("兑", "坤"): "萃", ("兑", "震"): "随",
    ("兑", "巽"): "大过", ("兑", "坎"): "困", ("兑", "离"): "革",
    ("兑", "艮"): "咸", ("兑", "兑"): "兑"
}

GUA_WUXING = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土"
}

GUA_JI_XIONG = {
    "乾": "主队有利", "坤": "平局倾向", "屯": "主队有利", "蒙": "客队有利",
    "需": "主队有利", "讼": "客队有利", "师": "主队有利", "比": "主队有利",
    "小畜": "主队有利", "履": "主队有利", "泰": "主队有利", "否": "客队有利",
    "同人": "主队有利", "大有": "主队有利", "谦": "主队有利", "豫": "主队有利",
    "随": "主队有利", "蛊": "客队有利", "临": "主队有利", "观": "平局倾向",
    "噬嗑": "客队有利", "贲": "主队有利", "剥": "客队有利", "复": "主队有利",
    "无妄": "主队有利", "大畜": "主队有利", "颐": "平局倾向", "大过": "客队有利",
    "坎": "客队有利", "离": "主队有利", "咸": "主队有利", "恒": "平局倾向",
    "遁": "客队有利", "大壮": "主队有利", "晋": "主队有利", "明夷": "客队有利",
    "家人": "主队有利", "睽": "客队有利", "蹇": "客队有利", "解": "主队有利",
    "损": "客队有利", "益": "主队有利", "夬": "主队有利", "姤": "平局倾向",
    "萃": "主队有利", "升": "主队有利", "困": "客队有利", "井": "平局倾向",
    "革": "客队有利", "鼎": "主队有利", "震": "平局倾向", "艮": "平局倾向",
    "渐": "主队有利", "归妹": "客队有利", "丰": "主队有利", "旅": "客队有利",
    "巽": "平局倾向", "兑": "主队有利", "涣": "客队有利", "节": "平局倾向",
    "中孚": "主队有利", "小过": "客队有利", "既济": "主队有利", "未济": "客队有利"
}

def wuxing_sheng_ke(wo, ta):
    """五行生克，正=主队有利，负=客队有利"""
    sheng = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
    ke = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
    if wo == ta:
        return 0.0
    elif sheng[wo] == ta:
        return -0.2   # 体生用，耗损
    elif ke[wo] == ta:
        return 0.3    # 体克用，有利
    elif sheng[ta] == wo:
        return 0.25   # 用生体，有利
    elif ke[ta] == wo:
        return -0.3   # 用克体，不利
    else:
        return 0.0

# ============================================================
# 第二部分：起卦与预测逻辑
# ============================================================

def get_unicode_sum(text):
    """取前两字的Unicode码点之和"""
    if not text:
        return 0
    chars = list(text.strip())[:2]
    return sum(ord(ch) for ch in chars)

def get_ben_gua_from_names(home, away):
    shang = get_unicode_sum(home) % 8
    xia = get_unicode_sum(away) % 8
    shang = 8 if shang == 0 else shang
    xia = 8 if xia == 0 else xia
    return GUA_MAP.get((NUM_TO_GUA[shang], NUM_TO_GUA[xia]), "未知")

def get_dong_yao(dt):
    return (dt.year + dt.month + dt.day + dt.hour + dt.minute) % 6

def get_zhi_gua(ben, dong):
    """通过本卦和动爻位置推变卦（错卦法）"""
    CUO = {"乾": "坤", "坤": "乾", "兑": "艮", "艮": "兑",
           "离": "坎", "坎": "离", "震": "巽", "巽": "震"}
    rev_map = {v: k for k, v in GUA_MAP.items()}
    if ben not in rev_map:
        return ben
    shang, xia = rev_map[ben]
    if dong < 3:
        new_xia = CUO.get(xia, xia)
        new_shang = shang
    else:
        new_shang = CUO.get(shang, shang)
        new_xia = xia
    return GUA_MAP.get((new_shang, new_xia), ben)

def get_ti_yong(ben, dong):
    rev_map = {v: k for k, v in GUA_MAP.items()}
    if ben not in rev_map:
        return "乾", "坤"
    shang, xia = rev_map[ben]
    return (shang, xia) if dong < 3 else (xia, shang)

def predict_football(home, away, dt):
    # 起卦
    shang_num = get_unicode_sum(home) % 8
    xia_num = get_unicode_sum(away) % 8
    shang_num = 8 if shang_num == 0 else shang_num
    xia_num = 8 if xia_num == 0 else xia_num
    shang = NUM_TO_GUA[shang_num]
    xia = NUM_TO_GUA[xia_num]
    ben = GUA_MAP.get((shang, xia), "未知")
    dong = get_dong_yao(dt)
    zhi = get_zhi_gua(ben, dong)
    ti, yong = get_ti_yong(ben, dong)
    ji = GUA_JI_XIONG.get(ben, "平局倾向")
    ti_w = GUA_WUXING.get(ti, "土")
    yong_w = GUA_WUXING.get(yong, "土")
    shengke = wuxing_sheng_ke(ti_w, yong_w)

    # 综合决策
    base = 1 if "主队有利" in ji else (-1 if "客队有利" in ji else 0)
    adjust = 1 if shengke > 0.1 else (-1 if shengke < -0.1 else 0)
    if base == 0:
        result = adjust
    else:
        result = base if (base == adjust or adjust == 0) else 0

    final = "主胜" if result > 0 else ("客胜" if result < 0 else "平局")

    info = {
        "本卦": ben,
        "变卦": zhi,
        "动爻": f"第{dong+1}爻",
        "体卦": ti,
        "用卦": yong,
        "体五行": ti_w,
        "用五行": yong_w,
        "体用关系": "生" if shengke > 0.1 else ("克" if shengke < -0.1 else "比和"),
        "卦象吉凶": ji,
        "五行权重": shengke
    }
    return final, info

# ============================================================
# 第三部分：Streamlit 界面
# ============================================================

def main():
    st.set_page_config(page_title="六爻足球预测", layout="centered")
    st.title("⚽ 六爻 · 足球胜平负预测")
    st.markdown("基于主客队名前两字 + 比赛时间起卦，纯卦象推演")

    col1, col2 = st.columns(2)
    with col1:
        home = st.text_input("主队名称", value="")
    with col2:
        away = st.text_input("客队名称", value="")

    # 修正点：此处 value 必须为 datetime 对象，而非函数
    dt = st.datetime_input(
        "比赛时间",
        value=datetime.datetime.now(),   # 注意加括号调用
        format="YYYY-MM-DD HH:mm"
    )

    if st.button("🔮 预测"):
        if not home.strip() or not away.strip():
            st.warning("请完整输入主队和客队名称")
            return
        if home.strip() == away.strip():
            st.warning("主队和客队不能相同")
            return

        result, info = predict_football(home.strip(), away.strip(), dt)

        st.subheader("预测结果")
        if result == "主胜":
            st.success(f"🏆 {home} 胜")
        elif result == "客胜":
            st.success(f"🏆 {away} 胜")
        else:
            st.warning("🤝 平局")

        with st.expander("📊 查看卦象详情"):
            col_a, col_b = st.columns(2)
            col_a.metric("本卦", info["本卦"])
            col_b.metric("变卦", info["变卦"])
            st.write(f"**动爻**：{info['动爻']}")
            st.write(f"**体卦**：{info['体卦']}（{info['体五行']}）  **用卦**：{info['用卦']}（{info['用五行']}）")
            st.write(f"**体用关系**：{info['体用关系']}")
            st.write(f"**卦象吉凶**：{info['卦象吉凶']}")
            st.caption(f"五行权重系数：{info['五行权重']:.2f}")

if __name__ == "__main__":
    main()
