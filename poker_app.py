import streamlit as st

st.set_page_config(page_title="Poker Tracker", layout="wide")

# -----------------------------
# Initialize session state
# -----------------------------
if "players" not in st.session_state:
    st.session_state.players = {}

if "initial" not in st.session_state:
    st.session_state.initial = {}

if "history" not in st.session_state:
    st.session_state.history = []

if "game_started" not in st.session_state:
    st.session_state.game_started = False

# -----------------------------
# Title
# -----------------------------
st.title("🃏 Poker Tracker")

# -----------------------------
# Sidebar (History)
# -----------------------------
st.sidebar.title("📜 Game History")

if st.session_state.history:
    for i, h in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.markdown(
            f"""
            <div style="background-color:#111;padding:10px;border-radius:8px;margin-bottom:8px">
            <b>Round {len(st.session_state.history)-i+1}</b><br>
            🏆 <span style="color:#00ff88">{h['winner']}</span><br>
            💰 Pot: ₹{h['pot']:.2f}
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.sidebar.info("No rounds played yet")

# -----------------------------
# Add Players
# -----------------------------
st.subheader("➕ Add Player")

with st.form("add_player_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    name = col1.text_input("Name")
    balance = col2.number_input(
        "Initial Balance",
        min_value=0.0,
        value=5000.0,
        step=100.0
    )

    submitted = st.form_submit_button("Add Player")

    if submitted:
        if name:
            if name in st.session_state.players:
                st.warning("Player already exists!")
            else:
                st.session_state.players[name] = balance
                st.session_state.initial[name] = balance
                st.success(f"{name} added!")

# -----------------------------
# Show Players
# -----------------------------
st.subheader("💰 Balances")

if st.session_state.players:

    players = list(st.session_state.players.keys())

    st.write("### 📊 Player Table")

    cols = st.columns(3)
    cols[0].markdown("**Player**")
    cols[1].markdown("**Balance**")
    cols[2].markdown("**Net Worth**")

    for p in players:
        c1, c2, c3 = st.columns(3)

        c1.write(p)

        # 🔥 Editable ONLY before game starts
        if not st.session_state.game_started:
            new_initial = c2.number_input(
                "",
                value=st.session_state.initial[p],
                key=f"init_{p}"
            )
            st.session_state.initial[p] = new_initial
            st.session_state.players[p] = new_initial
        else:
            c2.write(f"₹{st.session_state.players[p]:.2f}")

        # Net worth
        net = st.session_state.players[p] - st.session_state.initial[p]
        color = "#00ff88" if net >= 0 else "#ff4b4b"

        c3.markdown(
            f"<span style='color:{color}'>₹{net:.2f}</span>",
            unsafe_allow_html=True
        )

    if not st.session_state.game_started:
        st.info("You can edit initial balances before first round")

else:
    st.info("No players added yet")

# -----------------------------
# Round Section
# -----------------------------
if st.session_state.players:

    st.subheader("🎲 Play Round")

    players = list(st.session_state.players.keys())

    winner = st.selectbox("Select Winner", players)

    st.write("### 💸 Enter Contributions")

    contributions = {}
    total_pot = 0

    cols = st.columns(len(players))

    for i, p in enumerate(players):
        with cols[i]:
            amt = st.number_input(
                p,
                min_value=0.0,
                step=50.0,
                key=f"bet_{p}",
                value=0.0
            )
            contributions[p] = amt
            total_pot += amt

    st.markdown(f"### 💰 Pot: ₹{total_pot:.2f}")

    # -----------------------------
    # Play Round
    # -----------------------------
    if st.button("▶ Play Round"):

        # 🔥 Lock game after first round
        st.session_state.game_started = True

        # Deduct from all
        for p in players:
            st.session_state.players[p] -= contributions[p]

        # Add to winner
        st.session_state.players[winner] += total_pot

        # Save history
        st.session_state.history.append({
            "winner": winner,
            "pot": total_pot,
            "contributions": contributions.copy()
        })

        st.success(f"🏆 {winner} wins ₹{total_pot:.2f}!")

        # Reset inputs
        for p in players:
            st.session_state.pop(f"bet_{p}", None)

        st.rerun()

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Poker Tracker • Initial Edit Lock Enabled 🔒")
