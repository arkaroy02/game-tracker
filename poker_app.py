import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="Poker Tracker", layout="wide")

DEFAULT_BUYIN = 5000

# -----------------------------
# 🎨 Poker Table Background
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #0f5132, #022c22);
    color: white;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background-color: #111;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State Init
# -----------------------------
for key, default in {
    "players": {},
    "initial": {},
    "total_buyin": {},
    "history": [],
    "matches": [],
    "game_started": False,
    "reset_bets": False,
    "buyin_confirmed": False,
    "reset_winners": False,
    "allin_trigger": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------
# Title
# -----------------------------
st.title("🃏 Poker Tracker")

# -----------------------------
# Sidebar Match Table
# -----------------------------
st.sidebar.title("📊 Saved Matches")

if st.session_state.matches:
    rows = []
    for i, m in enumerate(st.session_state.matches, 1):
        for p, bal in m["players"].items():
            rows.append({
                "Match": i,
                "Player": p,
                "Final Balance": bal
            })

    df = pd.DataFrame(rows)
    st.sidebar.dataframe(df, use_container_width=True)
else:
    st.sidebar.info("No matches saved")

# -----------------------------
# Add Players
# -----------------------------
if not st.session_state.buyin_confirmed:

    st.subheader("➕ Add Player")

    with st.form("add_player", clear_on_submit=True):
        col1, col2 = st.columns(2)

        name = col1.text_input("Name")
        balance = col2.number_input("Initial Balance", min_value=0, value=DEFAULT_BUYIN, step=100)

        if st.form_submit_button("Add"):
            if name and name not in st.session_state.players:
                st.session_state.players[name] = balance
                st.session_state.initial[name] = balance
                st.session_state.total_buyin[name] = balance

# -----------------------------
# Confirm Buy-in
# -----------------------------
if st.session_state.players and not st.session_state.buyin_confirmed:
    if st.button("✅ Confirm Buy-ins"):
        st.session_state.buyin_confirmed = True
        st.success("Buy-ins locked!")

# -----------------------------
# Balances
# -----------------------------
st.subheader("💰 Balances")

players = list(st.session_state.players.keys())

for p in players:
    bal = st.session_state.players[p]
    total = st.session_state.total_buyin[p]
    net = bal - total

    color = "lightgreen" if net >= 0 else "salmon"

    st.markdown(
        f"<div class='card'><b>{p}</b><br>₹{bal} | Net: <span style='color:{color}'>₹{net}</span></div>",
        unsafe_allow_html=True
    )

    if not st.session_state.buyin_confirmed:
        new_val = st.number_input(f"Edit {p}", value=st.session_state.initial[p], key=f"init_{p}")
        st.session_state.players[p] = new_val
        st.session_state.initial[p] = new_val
        st.session_state.total_buyin[p] = new_val

    if bal <= 0:
        col1, col2 = st.columns([2,1])

        with col1:
            rebuy_amt = st.number_input(f"Rebuy {p}", min_value=0, step=100, key=f"rebuy_{p}")

        with col2:
            if st.button("Rebuy", key=f"btn_{p}"):
                if rebuy_amt > 0:
                    st.session_state.players[p] += rebuy_amt
                    st.session_state.total_buyin[p] += rebuy_amt
                    st.rerun()

# -----------------------------
# Round Section
# -----------------------------
if players and st.session_state.buyin_confirmed:

    st.subheader("🎲 Round")

    # Reset winners BEFORE render
    if st.session_state.reset_winners:
        st.session_state["winners"] = []
        st.session_state.reset_winners = False

    winners = st.multiselect("Winner(s)", players, key="winners")

    contributions = {}
    pot = 0

    # Reset bets BEFORE render
    if st.session_state.reset_bets:
        for p in players:
            st.session_state[f"bet_{p}"] = 0
        st.session_state.reset_bets = False

    # ✅ APPLY ALL-IN BEFORE widgets render (FIXED)
    for p in players:
        if st.session_state.allin_trigger.get(p, False):
            st.session_state[f"bet_{p}"] = st.session_state.players[p]
            st.session_state.allin_trigger[p] = False

    for p in players:
        col1, col2 = st.columns([3,1])

        with col1:
            amt = st.number_input(
                p,
                min_value=0,
                max_value=st.session_state.players[p],
                step=100,
                key=f"bet_{p}",
                value=st.session_state.get(f"bet_{p}", 0)
            )

        with col2:
            # ✅ FIXED ALL-IN BUTTON
            if st.button("ALL-IN", key=f"a_{p}"):
                st.session_state.allin_trigger[p] = True
                st.rerun()

        contributions[p] = amt
        pot += amt

    st.markdown(f"### 💰 Pot: ₹{pot}")

    if st.button("▶ Play"):

        if not winners:
            st.warning("Select winner")
            st.stop()

        for p in players:
            st.session_state.players[p] -= contributions[p]

        share = pot // len(winners)

        for w in winners:
            st.session_state.players[w] += share

            # ✅ FIX: SAVE ROUND HISTORY
            st.session_state.history.append({
                "winners": winners.copy(),
                "pot": pot
            })

        st.session_state.reset_bets = True
        st.session_state.reset_winners = True

        st.rerun()
        
        
# -----------------------------
# 📜 Current Match History (Sidebar)
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.title("🎲 Current Match")

if st.session_state.history:

    rows = []
    for i, h in enumerate(reversed(st.session_state.history), 1):
        rows.append({
            "Round": len(st.session_state.history) - i + 1,
            "Winners": ", ".join(h["winners"]),
            "Pot": h["pot"]
        })

    df_hist = pd.DataFrame(rows)
    st.sidebar.dataframe(df_hist, use_container_width=True)

else:
    st.sidebar.info("No rounds yet")
    
    
# -----------------------------
# End Match
# -----------------------------
st.markdown("### 🏁 End Match")

if st.button("End Match"):

    st.session_state.matches.append({
        "players": st.session_state.players.copy()
    })

    st.session_state.players = {}
    st.session_state.initial = {}
    st.session_state.total_buyin = {}
    st.session_state.history = []
    st.session_state.game_started = False
    st.session_state.buyin_confirmed = False

    st.success("Match saved!")
    st.rerun()

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Poker Tracker ~ Arka ♠️🟢")
