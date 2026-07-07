# -*- coding: utf-8 -*-
"""
원료 대체재 추천기 - Streamlit 버전
원본 HTML(원료대체재추천기.html)의 기능을 Streamlit으로 재구현
"""

import streamlit as st
from raw_materials import DB

# --------------------------------------------------------------------------
# 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="원료 대체재 추천기",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

BY_ID = {item["id"]: item for item in DB}

CATEGORIES = ["전체", "유화제", "점증제", "보습제", "방부제", "계면활성제",
              "오일/에몰리언트", "자외선차단제", "산화방지제", "실리콘", "pH조절제"]

STATUS_LABEL = {"active": "정상 공급", "outofstock": "품절", "discontinued": "단종"}
STATUS_COLOR = {
    "active": ("#2c6e5c", "#dcebe3"),
    "outofstock": ("#9a6420", "#f3e6d1"),
    "discontinued": ("#a23b33", "#f5ded9"),
}
CATEGORY_EMOJI = {
    "유화제": "🧴", "점증제": "🍯", "보습제": "💧", "방부제": "🛡️", "계면활성제": "🧼",
    "오일/에몰리언트": "🌿", "자외선차단제": "☀️", "산화방지제": "🍃", "실리콘": "⚙️", "pH조절제": "⚗️",
}

QUICK_QUERIES = [
    "Ceteareth-20",
    "Acrylates/C10-30 Alkyl Acrylate Crosspolymer",
    "PEG-8",
    "Methylisothiazolinone",
    "Chlorphenesin",
]

ACCENT = "#2c6e5c"
ACCENT_STRONG = "#1f5245"
ACCENT_SOFT = "#dcebe3"
SECONDARY = "#4e6c8c"
MUTED = "#616b5f"
BORDER = "#dbdecf"
SURFACE_2 = "#ecede4"

# --------------------------------------------------------------------------
# 스타일
# --------------------------------------------------------------------------
st.markdown(f"""
<style>
    .stApp {{
        background-color: #f5f4ef;
    }}
    .app-header {{
        background: linear-gradient(135deg, #dcebe3, #e0e7ef);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 18px;
    }}
    .app-header .eyebrow {{
        color: {SECONDARY};
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        margin-bottom: 4px;
    }}
    .app-header h1 {{
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 4px 0;
        color: #1e2a22;
    }}
    .app-header h1 span {{ color: {ACCENT}; }}
    .app-header p.sub {{
        color: {MUTED};
        margin: 6px 0 0 0;
        font-size: 0.98rem;
    }}
    .notice-box {{
        margin-top: 10px;
        border: 1px solid {BORDER};
        background: {SURFACE_2};
        color: {MUTED};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.82rem;
    }}
    .notice-box strong {{ color: #1e2a22; }}

    .pill {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 600;
        white-space: nowrap;
    }}
    .result-row-box {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        background: #f5f4ef;
    }}
    .result-row-box.selected {{
        border-color: {ACCENT};
        background: {ACCENT_SOFT};
    }}
    .name-text {{ font-weight: 700; font-size: 1.0rem; }}
    .codes-text {{ font-family: monospace; font-size: 0.78rem; color: {MUTED}; }}
    .cat-price-text {{ font-size: 0.8rem; color: {MUTED}; }}
    .detail-card {{
        border: 1px solid {BORDER};
        border-left: 4px solid {ACCENT};
        border-radius: 10px;
        padding: 18px 20px;
        margin: 6px 0 14px 0;
        background: #ffffff;
    }}
    .sub-card {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        background: #f5f4ef;
    }}
    .match-badge {{
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 999px;
        border: 1px solid {ACCENT};
        color: {ACCENT_STRONG};
        margin-left: 6px;
    }}
    .match-badge.same {{ background: {ACCENT}; color: #fff; }}
    .price-diff {{
        font-size: 0.76rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 999px;
        white-space: nowrap;
        margin-left: 6px;
    }}
    .sub-diff-box {{
        margin-top: 8px;
        font-size: 0.88rem;
        background: {SURFACE_2};
        border-radius: 8px;
        padding: 8px 10px;
    }}
    .sub-diff-box .label {{
        color: {MUTED}; font-weight: 700; font-size: 0.74rem;
        text-transform: uppercase; letter-spacing: 0.04em; display: block; margin-bottom: 3px;
    }}
    div[data-testid="stSidebarUserContent"] .stButton button {{
        width: 100%;
        text-align: left;
        border: none;
        background: transparent;
    }}
    .legend-item {{ font-size: 0.85rem; color: #4b6058; margin-bottom: 4px; }}
    .dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# 세션 상태 초기화
# --------------------------------------------------------------------------
def init_state():
    defaults = {
        "query": "",
        "category": "전체",
        "selected_id": None,
        "history": [],
        "search_input": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def add_to_history(q: str):
    if not q:
        return
    hist = [h for h in st.session_state.history if h != q]
    hist.insert(0, q)
    st.session_state.history = hist[:10]


def run_search(q: str):
    st.session_state.query = q
    st.session_state.search_input = q
    st.session_state.selected_id = None
    add_to_history(q)


def reset_search():
    st.session_state.query = ""
    st.session_state.category = "전체"
    st.session_state.selected_id = None
    st.session_state.search_input = ""


def matches_query(item, q):
    if not q:
        return True

    def norm(s):
        return s.lower().replace(" ", "").replace("-", "")

    nq = norm(q)
    return nq in norm(item["name"]) or nq in norm(item["inci"]) or nq in norm(item["cas"])


def get_filtered():
    return [
        item for item in DB
        if (st.session_state.category == "전체" or item["category"] == st.session_state.category)
        and matches_query(item, st.session_state.query)
    ]


def format_price(item):
    return f"{item['price']:,}원/kg"


def price_diff_html(base_item, target_item):
    pct = ((target_item["price"] - base_item["price"]) / base_item["price"]) * 100
    if pct <= -5:
        return f'<span class="price-diff" style="background:{STATUS_COLOR["active"][1]};color:{STATUS_COLOR["active"][0]}">원가 {round(pct)}%</span>'
    if pct >= 5:
        return f'<span class="price-diff" style="background:{STATUS_COLOR["outofstock"][1]};color:{STATUS_COLOR["outofstock"][0]}">원가 +{round(pct)}%</span>'
    return f'<span class="price-diff" style="background:{SURFACE_2};color:{MUTED}">원가 유사</span>'


def pill_html(status):
    color, bg = STATUS_COLOR[status]
    return (f'<span class="pill" style="background:{bg};color:{color}">'
            f'<span class="dot" style="background:{color}"></span>{STATUS_LABEL[status]}</span>')


# --------------------------------------------------------------------------
# 헤더
# --------------------------------------------------------------------------
st.markdown(f"""
<div class="app-header">
  <div class="eyebrow">원료 데이터베이스</div>
  <h1>원료 <span>대체재</span> 추천기</h1>
  <p class="sub">사용중단·품절 원료의 기능(유화제, 점증제 등)을 대체할 원료를 CAS No·INCI 정보와 함께 비교합니다.</p>
  <div class="notice-box"><strong>안내&nbsp;</strong>본 페이지의 원료 데이터 및 단가는 데모용 샘플입니다. 실제 배합·구매 전 원료사 최신 스펙시트, 견적 및 규제 현황을 확인하세요.</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# 사이드바 (기능 카테고리 / 공급 상태 범례)
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("##### 기능 카테고리")
    for cat in CATEGORIES:
        btn_type = "primary" if st.session_state.category == cat else "secondary"
        if st.button(cat, key=f"cat_{cat}", use_container_width=True, type=btn_type):
            st.session_state.category = cat
            st.session_state.selected_id = None

    st.markdown("---")
    st.markdown("##### 공급 상태")
    for status, label in STATUS_LABEL.items():
        color, _ = STATUS_COLOR[status]
        st.markdown(
            f'<div class="legend-item"><span class="dot" style="background:{color}"></span>{label}</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# 검색 영역
# --------------------------------------------------------------------------
search_col, btn_col1, btn_col2 = st.columns([5, 1, 1])
with search_col:
    query_input = st.text_input(
        "검색",
        key="search_input",
        placeholder="원료명 · INCI명 · CAS No 검색 (예: Ceteareth-20)",
        label_visibility="collapsed",
    )
with btn_col1:
    if st.button("검색", use_container_width=True, type="primary"):
        run_search(query_input.strip())
with btn_col2:
    if st.button("초기화", use_container_width=True):
        reset_search()

st.caption("단종/품절 예시:")
chip_cols = st.columns(len(QUICK_QUERIES))
for col, q in zip(chip_cols, QUICK_QUERIES):
    with col:
        if st.button(q, key=f"chip_{q}", use_container_width=True):
            run_search(q)

# --------------------------------------------------------------------------
# 검색 기록
# --------------------------------------------------------------------------
with st.expander("🕘 검색 기록", expanded=bool(st.session_state.history)):
    if not st.session_state.history:
        st.caption("아직 검색 기록이 없습니다.")
    else:
        for idx, term in enumerate(st.session_state.history):
            hc1, hc2 = st.columns([8, 1])
            with hc1:
                if st.button(term, key=f"hist_{idx}", use_container_width=True):
                    run_search(term)
            with hc2:
                if st.button("✕", key=f"histdel_{idx}"):
                    st.session_state.history.pop(idx)
                    st.rerun()

st.markdown("---")

# --------------------------------------------------------------------------
# 결과 목록
# --------------------------------------------------------------------------
filtered = get_filtered()
hint = "원료를 클릭하면 대체재 정보가 바로 아래에 표시됩니다."

if not st.session_state.query and st.session_state.category == "전체":
    st.caption(f"전체 원료 목록 ({len(filtered)}건) — {hint}")
elif not filtered:
    st.warning("검색 결과가 없습니다. 원료명, INCI명 또는 CAS No.를 확인해주세요.")
else:
    st.caption(f"검색 결과 {len(filtered)}건 — {hint}")


def build_sub_entry(sub, base_item):
    target = BY_ID.get(sub["id"])
    if not target:
        return
    match_class = "same" if sub["match"] == "same" else ""
    match_label = "동일 기능" if sub["match"] == "same" else "유사 기능"
    st.markdown(f"""
    <div class="sub-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap;">
        <div>
          <span class="name-text">{target['name']}</span>
          <span class="match-badge {match_class}">{match_label}</span>
          {price_diff_html(base_item, target)}
          <div class="codes-text" style="margin-top:4px;">INCI {target['inci']} · CAS {target['cas']} · {format_price(target)}</div>
        </div>
        <div>{pill_html(target['status'])}</div>
      </div>
      <div class="sub-diff-box"><span class="label">차이점</span>{sub['diff']}</div>
    </div>
    """, unsafe_allow_html=True)


def build_detail_panel(item):
    subs = item.get("subs")
    if not subs:
        subs = [
            {"id": o["id"], "match": "similar", "diff": "상세 비교 데이터 없음 · 원료사 스펙시트 확인 필요"}
            for o in DB if o["id"] != item["id"] and o["category"] == item["category"]
        ][:3]

    st.markdown(f"""
    <div class="detail-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
        <div>
          <div style="color:{ACCENT};font-size:0.8rem;font-weight:700;text-transform:uppercase;">{item['category']}</div>
          <h3 style="margin:2px 0 8px 0;">{item['name']}</h3>
        </div>
        <div>{pill_html(item['status'])}</div>
      </div>
      <div style="display:flex;gap:28px;flex-wrap:wrap;border-top:1px solid {BORDER};border-bottom:1px solid {BORDER};padding:12px 0;margin:10px 0;">
        <div><div style="font-size:0.72rem;color:{MUTED};text-transform:uppercase;">INCI명</div><div style="font-family:monospace;">{item['inci']}</div></div>
        <div><div style="font-size:0.72rem;color:{MUTED};text-transform:uppercase;">CAS No.</div><div style="font-family:monospace;">{item['cas']}</div></div>
        <div><div style="font-size:0.72rem;color:{MUTED};text-transform:uppercase;">참고 단가</div><div style="font-family:monospace;">{format_price(item)}</div></div>
      </div>
      <p style="color:{MUTED};font-size:0.92rem;margin:0;">{item['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🔁 추천 대체 원료**")
    for s in subs:
        build_sub_entry(s, item)


for item in filtered:
    is_selected = st.session_state.selected_id == item["id"]
    row_class = "selected" if is_selected else ""

    row_container = st.container()
    with row_container:
        c_icon, c_main, c_meta, c_pill = st.columns([0.6, 3.4, 2.2, 1.4])
        with c_icon:
            st.markdown(f"<div style='font-size:1.4rem;padding-top:4px;'>{CATEGORY_EMOJI.get(item['category'], '🧪')}</div>", unsafe_allow_html=True)
        with c_main:
            if st.button(f"{item['name']}", key=f"row_{item['id']}", use_container_width=True):
                st.session_state.selected_id = None if is_selected else item["id"]
                st.rerun()
            st.markdown(f"<div class='codes-text'>CAS {item['cas']}</div>", unsafe_allow_html=True)
        with c_meta:
            st.markdown(f"<div class='cat-price-text' style='padding-top:10px;'>{item['category']} · {format_price(item)}</div>", unsafe_allow_html=True)
        with c_pill:
            st.markdown(f"<div style='padding-top:8px;'>{pill_html(item['status'])}</div>", unsafe_allow_html=True)

    if is_selected:
        build_detail_panel(item)

    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)
