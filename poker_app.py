import streamlit as st

st.set_page_config(page_title="Poker Tracker", layout="wide")

DEFAULT_BUYIN = 5000

# -----------------------------
# Session State
# -----------------------------
if "players" not in st.session_state:
    st.session_state.players = {}

if "initial" not in st.session_state:
    st.session_state.initial = {}

if "total_buyin" not in st.session_state:
    st.session_state.total_buyin = {}

if "history" not in st.session_state:
    st.session_state.history = []

if "game_started" not in st.session_state:
    st.session_state.game_started = False

# -----------------------------
# Title
# -----------------------------
st.title("🃏 Poker Tracker")

# -----------------------------
# Sidebar History
# -----------------------------
st.sidebar.title("📜 History")

for h in reversed(st.session_state.history):
    winners = ", ".join(h["winners"])
    st.sidebar.write(f"🏆 {winners} | ₹{h['pot']}")

# -----------------------------
# Add Players
# -----------------------------
st.subheader("➕ Add Player")

with st.form("add_player", clear_on_submit=True):
    col1, col2 = st.columns(2)

    name = col1.text_input("Name")

    balance = col2.number_input(
        "Initial Balance",
        min_value=0,
        value=DEFAULT_BUYIN,
        step=100
    )

    if st.form_submit_button("Add"):
        if name:
            if name in st.session_state.players:
                st.warning("Player exists")
            else:
                st.session_state.players[name] = balance
                st.session_state.initial[name] = balance
                st.session_state.total_buyin[name] = balance

# -----------------------------
# Balances + Rebuy
# -----------------------------
st.subheader("💰 Balances")

players = list(st.session_state.players.keys())

for p in players:

    bal = st.session_state.players[p]
    total = st.session_state.total_buyin[p]

    net = bal - total

    color = "green" if net >= 0 else "red"

    st.markdown(
        f"**{p}** | Balance: ₹{bal} | Total Buyin: ₹{total} | Net: :{color}[₹{net}]"
    )

    # Edit initial before game starts
    if not st.session_state.game_started:
        new_val = st.number_input(
            f"Edit {p}",
            value=st.session_state.initial[p],
            key=f"init_{p}"
        )
        st.session_state.initial[p] = new_val
        st.session_state.players[p] = new_val
        st.session_state.total_buyin[p] = new_val

    # 🔥 REBUY (CUSTOM)
    if bal <= 0:
        st.write(f"Rebuy for {p}")

        col1, col2 = st.columns([2,1])

        with col1:
            rebuy_amt = st.number_input(
                f"Amount {p}",
                min_value=0,
                step=100,
                key=f"rebuy_{p}"
            )

        with col2:
            if st.button("Rebuy", key=f"btn_{p}"):
                if rebuy_amt > 0:
                    st.session_state.players[p] += rebuy_amt
                    st.session_state.total_buyin[p] += rebuy_amt
                    st.rerun()

# -----------------------------
# Round Section
# -----------------------------
if players:

    st.subheader("🎲 Round")

    winners = st.multiselect("Winner(s)", players)

    contributions = {}
    pot = 0

    # Handle ALL-IN trigger
    for p in players:
        if st.session_state.get(f"allin_{p}", False):
            st.session_state[f"bet_{p}"] = st.session_state.players[p]
            st.session_state[f"allin_{p}"] = False

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
            if st.button("ALL-IN", key=f"a_{p}"):
                st.session_state[f"allin_{p}"] = True
                st.rerun()

        contributions[p] = amt
        pot += amt

    st.write(f"💰 Pot: ₹{pot}")

    # -----------------------------
    # Play Round
    # -----------------------------
    if st.button("▶ Play"):

        if not winners:
            st.warning("Select winner")
            st.stop()

        st.session_state.game_started = True

        # Deduct contributions
        for p in players:
            st.session_state.players[p] -= contributions[p]

        # Split pot
        share = pot // len(winners)

        for w in winners:
            st.session_state.players[w] += share

        # Save history
        st.session_state.history.append({
            "winners": winners,
            "pot": pot
        })

        # Reset bets
        for p in players:
            st.session_state.pop(f"bet_{p}", None)

        st.rerun()

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Poker Tracker • Correct Accounting System ♠️")
