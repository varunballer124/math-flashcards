#!/usr/bin/env python3
"""
TTP Visual Math Flashcards — a spaced-repetition study app.

Learning design (grounded in cognitive-science of memory):
  • Active recall   — you see only the topic, try to remember the rule, THEN flip.
  • Spaced repetition (SM-2-lite) — cards you find hard come back soon; easy ones
                       drift far into the future. You only ever review what's due.
  • Interleaving    — due cards are shuffled across topics, which beats blocking.
  • Desirable difficulty — four honest self-ratings drive the schedule.
  • Progress made visible — streak, due count and a per-section mastery bar.

Progress is saved in your browser (localStorage), so it sticks between visits on
this device. Use the Backup buttons in the sidebar to move progress to another one.
"""
from __future__ import annotations
import json, os, random, datetime as dt
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
TODAY = dt.date.today()

st.set_page_config(page_title="Math Flashcards 💗", page_icon="💗", layout="wide",
                   initial_sidebar_state="expanded")

# ────────────────────────────────────────────────────────────────────────────
# data
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_cards():
    data = json.loads((ROOT / "cards.json").read_text())
    return data["cards"], data["sections"]

CARDS, SECTIONS = load_cards()
BY_GID = {c["gid"]: c for c in CARDS}

# ────────────────────────────────────────────────────────────────────────────
# persistence  (browser localStorage, with a graceful in-session fallback)
# ────────────────────────────────────────────────────────────────────────────
LS_KEY = "ttp_flashcards_v1"
try:
    from streamlit_local_storage import LocalStorage
    _ls = LocalStorage()
except Exception:
    _ls = None


def load_progress() -> dict:
    if "srs" in st.session_state:
        return st.session_state.srs
    raw = None
    if _ls is not None:
        try:
            raw = _ls.getItem(LS_KEY)
        except Exception:
            raw = None
    try:
        st.session_state.srs = json.loads(raw) if raw else {}
    except Exception:
        st.session_state.srs = {}
    return st.session_state.srs


def save_progress():
    if _ls is not None:
        try:
            _ls.setItem(LS_KEY, json.dumps(st.session_state.srs), key="ls_save")
        except Exception:
            pass


SRS = load_progress()


def card_state(gid):
    return SRS.get(str(gid))


def is_due(gid):
    s = card_state(gid)
    if not s:
        return True  # never seen → always available as "new"
    return s["due"] <= TODAY.isoformat()


def is_new(gid):
    return str(gid) not in SRS


# SM-2-lite scheduler — grades: 0 Again · 1 Hard · 2 Good · 3 Easy
def schedule(gid, grade):
    gid = str(gid)
    s = SRS.get(gid, {"ease": 2.5, "interval": 0, "reps": 0, "lapses": 0})
    ease, interval, reps = s["ease"], s["interval"], s["reps"]
    if grade == 0:            # Again
        reps, interval = 0, 0
        ease = max(1.3, ease - 0.2)
        s["lapses"] = s.get("lapses", 0) + 1
    elif grade == 1:          # Hard
        interval = max(1, round(interval * 1.2)) if interval else 1
        ease = max(1.3, ease - 0.15)
        reps += 1
    elif grade == 2:          # Good
        interval = 1 if reps == 0 else (3 if reps == 1 else round(interval * ease))
        reps += 1
    else:                     # Easy
        base = max(interval, 1)
        interval = round(base * ease * 1.35) + 1
        ease = min(3.2, ease + 0.15)
        reps += 1
    due = TODAY + dt.timedelta(days=interval)
    s.update(ease=round(ease, 2), interval=interval, reps=reps,
             due=due.isoformat(), last=TODAY.isoformat())
    SRS[gid] = s
    save_progress()


# ────────────────────────────────────────────────────────────────────────────
# session / queue
# ────────────────────────────────────────────────────────────────────────────
def pool_for(section):
    if section == "All sections":
        return [c for c in CARDS]
    return [c for c in CARDS if c["section"] == section]


def build_queue(section, mode, new_limit, shuffle):
    pool = pool_for(section)
    if mode == "Browse / Cram":
        q = [c["gid"] for c in pool]
    else:  # Spaced repetition
        seen_due = [c["gid"] for c in pool if not is_new(c["gid"]) and is_due(c["gid"])]
        new = [c["gid"] for c in pool if is_new(c["gid"])][:new_limit]
        q = seen_due + new
    if shuffle:
        random.shuffle(q)
    return q


def ensure_session(section, mode, new_limit, shuffle):
    sig = (section, mode, new_limit, shuffle)
    if st.session_state.get("sig") != sig or "queue" not in st.session_state:
        st.session_state.sig = sig
        st.session_state.queue = build_queue(section, mode, new_limit, shuffle)
        st.session_state.pos = 0
        st.session_state.revealed = False
        st.session_state.session_done = 0


# ────────────────────────────────────────────────────────────────────────────
# styling
# ────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container {padding-top:1.6rem; padding-bottom:2rem; max-width:1150px;}
#MainMenu, footer {visibility:hidden;}
.hero {text-align:center; margin-bottom:.4rem;}
.hero h1 {font-size:1.55rem; margin:0; font-weight:800; letter-spacing:.2px;}
.hero p  {color:#8b95a7; margin:.15rem 0 0; font-size:.9rem;}
.badge {display:inline-block; padding:5px 14px; border-radius:999px; font-weight:700;
        font-size:.8rem; background:#eef2ff; color:#4f46e5; letter-spacing:.4px;}
.front {border:1px solid #e6e8ef; border-radius:22px; padding:52px 26px;
        background:linear-gradient(180deg,#fafbff,#f1f4ff);
        box-shadow:0 10px 40px rgba(79,70,229,.07); text-align:center;}
.front .topic {font-size:2.0rem; font-weight:800; color:#1e293b; line-height:1.2;
               margin:18px auto 6px; max-width:760px;}
.front .cue {color:#7c8598; font-size:.98rem; margin-top:14px;}
.cardimg img {border-radius:18px; box-shadow:0 12px 46px rgba(15,23,42,.16);
              border:1px solid #e9ecf3;}
.stProgress > div > div > div {background-image:linear-gradient(90deg,#a855f7,#22c55e);}
div.stButton > button {border-radius:14px; font-weight:700; padding:.55rem 0;}
.smallcap {color:#9aa3b2; font-size:.82rem; text-align:center; margin-top:.3rem;}
.done {text-align:center; padding:46px 20px; border-radius:22px;
       background:linear-gradient(180deg,#f0fdf4,#ecfeff); border:1px solid #bbf7d0;}
.done h2 {margin:0; font-size:1.7rem;}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# sidebar
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### I love you Rasya ❤️")
    sec_options = ["All sections"] + SECTIONS
    section = st.selectbox("Topic", sec_options, index=0)
    mode = st.radio("Mode", ["Spaced repetition", "Browse / Cram"], index=0,
                    help="Spaced repetition = smart review of what's due + a few new each time. "
                         "Browse = flip through everything to preview.")
    new_limit = st.slider("New cards per session", 5, 60, 20, step=5,
                          disabled=(mode == "Browse / Cram"),
                          help="How many never-seen cards to introduce this round. "
                               "Smaller = less overwhelming; the rest wait for next time.")
    shuffle = st.toggle("Shuffle (interleave)", value=True,
                        help="Mixing topics is proven to beat studying them in blocks.")

    st.divider()
    # progress snapshot
    total = len(CARDS)
    learned = sum(1 for c in CARDS if (s := card_state(c["gid"])) and s["interval"] >= 7)
    seen = sum(1 for c in CARDS if not is_new(c["gid"]))
    due_now = sum(1 for c in CARDS if not is_new(c["gid"]) and is_due(c["gid"]))
    st.markdown("### 📈 Your progress")
    st.progress(learned / total, text=f"{learned}/{total} cards locked in (7+ day interval)")
    a, b = st.columns(2)
    a.metric("Seen", f"{seen}/{total}")
    b.metric("Due to review", due_now)

    st.divider()
    st.markdown("### 💾 Backup progress")
    st.download_button("⬇️ Export", data=json.dumps(SRS),
                       file_name="flashcard_progress.json", mime="application/json",
                       use_container_width=True)
    up = st.file_uploader("⬆️ Import", type="json", label_visibility="collapsed")
    if up is not None and st.button("Restore from file", use_container_width=True):
        try:
            st.session_state.srs = json.loads(up.read())
            save_progress()
            st.success("Progress restored!")
            st.rerun()
        except Exception as e:
            st.error(f"Couldn't read that file: {e}")
    if st.button("🗑️ Reset all progress", use_container_width=True):
        st.session_state.confirm_reset = True
    if st.session_state.get("confirm_reset"):
        st.warning("This erases all your review history.")
        if st.button("Yes, erase everything", type="primary", use_container_width=True):
            st.session_state.srs = {}
            save_progress()
            st.session_state.confirm_reset = False
            st.rerun()

# ────────────────────────────────────────────────────────────────────────────
# search jump
# ────────────────────────────────────────────────────────────────────────────
ensure_session(section, mode, new_limit, shuffle)

st.markdown('<div class="hero"><h1>💗 Visual Math Flashcards</h1>'
            '<p>See the topic → recall the rule in your head → flip to check.</p></div>',
            unsafe_allow_html=True)

with st.expander("🔎 Jump to a specific card"):
    q = st.text_input("Search topics", "", placeholder="e.g. quadratic, remainder, slope…")
    if q:
        hits = [c for c in CARDS if q.lower() in (c["title"] + " " + c["section"]).lower()][:25]
        st.caption(f"{len(hits)} match(es)")
        for c in hits:
            if st.button(f"{c['section']} — {c['title'] or 'card '+str(c['lid'])}",
                         key=f"jump{c['gid']}", use_container_width=True):
                st.session_state.queue = [c["gid"]]
                st.session_state.pos = 0
                st.session_state.revealed = False
                st.session_state.sig = ("__jump__",)
                st.rerun()

queue = st.session_state.queue
pos = st.session_state.pos

# ── session complete ────────────────────────────────────────────────────────
if not queue:
    st.info("No cards match. Pick another topic, or switch on more new cards.")
    st.stop()

if pos >= len(queue):
    done = st.session_state.get("session_done", 0)
    st.markdown(f'<div class="done"><h2>🎉 Session complete!</h2>'
                f'<p style="color:#15803d;font-size:1.05rem;margin-top:6px;">'
                f'You reviewed <b>{done}</b> card(s). Come back tomorrow and the ones you '
                f'found tricky will be waiting — that spacing is what builds memory.</p></div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    if c2.button("🔁 Study more now", type="primary", use_container_width=True):
        st.session_state.sig = None  # force rebuild
        st.rerun()
    st.stop()

# ── current card ────────────────────────────────────────────────────────────
gid = queue[pos]
card = BY_GID[gid]
state = card_state(gid)

top = st.columns([1, 2, 1])
with top[0]:
    st.markdown(f'<span class="badge">{card["section"]}</span>', unsafe_allow_html=True)
with top[2]:
    tag = "🆕 new" if is_new(gid) else f"🔁 rep {state['reps']} · {state['interval']}d"
    st.markdown(f'<div style="text-align:right;color:#9aa3b2;font-weight:600;">{tag}</div>',
                unsafe_allow_html=True)
st.progress((pos) / len(queue), text=f"Card {pos+1} of {len(queue)} this session")

if not st.session_state.revealed:
    # FRONT — recall cue (the card's own title strip = always accurate)
    st.markdown('<div class="cardimg" style="display:flex;justify-content:center;margin:8px 0;">',
                unsafe_allow_html=True)
    st.image(str(ROOT / card["front"]), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<p class="front cue" style="border:none;background:none;box-shadow:none;padding:0;">'
                'Try to recall the rule, the method, and a quick example — '
                '<b>then flip.</b></p>', unsafe_allow_html=True)
    sp = st.columns([1, 2, 1])
    if sp[1].button("👀  Show the answer  (Space)", type="primary", use_container_width=True):
        st.session_state.revealed = True
        st.rerun()
else:
    # BACK — full worked card
    st.markdown('<div class="cardimg" style="display:flex;justify-content:center;margin:8px 0;">',
                unsafe_allow_html=True)
    st.image(str(ROOT / card["full"]), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if mode == "Browse / Cram":
        nav = st.columns([1, 1, 1])
        if nav[0].button("◀ Back", use_container_width=True, disabled=(pos == 0)):
            st.session_state.pos -= 1
            st.session_state.revealed = False
            st.rerun()
        if nav[2].button("Next ▶", type="primary", use_container_width=True):
            st.session_state.pos += 1
            st.session_state.revealed = False
            st.rerun()
    else:
        st.markdown('<p class="smallcap">How well did you remember it?</p>', unsafe_allow_html=True)
        g = st.columns(4)
        grades = [("😵 Again", 0, "blank — see it again soon"),
                  ("😅 Hard", 1, "recalled with effort"),
                  ("🙂 Good", 2, "got it"),
                  ("😎 Easy", 3, "too easy")]
        for col, (label, grade, _help) in zip(g, grades):
            if col.button(label, key=f"g{grade}", use_container_width=True, help=_help):
                schedule(gid, grade)
                st.session_state.session_done = st.session_state.get("session_done", 0) + 1
                if grade == 0:           # Again → see again later this session
                    st.session_state.queue.append(gid)
                st.session_state.pos += 1
                st.session_state.revealed = False
                st.rerun()

# ── keyboard shortcuts (Space = flip / advance; 1-4 = grade) ────────────────
import streamlit.components.v1 as components
components.html("""
<script>
const doc = window.parent.document;
function click(txt){
  const b=[...doc.querySelectorAll('button')].find(e=>e.innerText.trim().startsWith(txt));
  if(b) b.click();
}
doc.onkeydown = function(e){
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA') return;
  if(e.code==='Space'){e.preventDefault(); click('👀'); click('Next');}
  if(e.key==='1') click('😵');
  if(e.key==='2') click('😅');
  if(e.key==='3') click('🙂');
  if(e.key==='4') click('😎');
};
</script>
""", height=0)
