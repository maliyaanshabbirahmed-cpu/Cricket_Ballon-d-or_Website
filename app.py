from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
FILES = {
    "players": DATA_DIR / "players.csv",
    "yearly": DATA_DIR / "yearly_performance.csv",
    "competitions": DATA_DIR / "competitions.csv",
    "trophies": DATA_DIR / "player_trophies.csv",
    "awards": DATA_DIR / "individual_awards.csv",
    "teams": DATA_DIR / "teams.csv",
}
st.set_page_config(page_title="Cricket Ballon d’Or", page_icon="🏏", layout="wide")

GOLD = "#D8B45A"
DARK = "#0B0C0F"
PANEL = "#15171C"
st.markdown(f"""
<style>
.stApp {{background: linear-gradient(135deg, #08090B 0%, #111318 55%, #17130B 100%); color:#F5F2E9;}}
[data-testid="stSidebar"] {{background:#0A0B0D; border-right:1px solid #5C4922;}}
h1,h2,h3 {{color:#E6C875 !important;}}
div[data-testid="stMetric"] {{background:#15171C; border:1px solid #514322; padding:16px; border-radius:12px;}}
div[data-testid="stDataFrame"] {{border:1px solid #514322; border-radius:10px;}}
.stButton>button, .stDownloadButton>button {{border:1px solid #D8B45A; border-radius:8px;}}
.hero {{padding:28px; border:1px solid #6D5726; border-radius:18px; background:linear-gradient(120deg,#17191E,#201A0D);}}
.small-note {{color:#B8B8B8; font-size:0.88rem;}}
</style>
""", unsafe_allow_html=True)

def load_csv(key):
    path = FILES[key]
    try:
        return pd.read_csv(path, keep_default_na=False)
    except Exception:
        return pd.DataFrame()

def save_csv(key, df):
    df.to_csv(FILES[key], index=False, encoding="utf-8-sig")

def nonempty(df, col):
    if df.empty or col not in df.columns:
        return df
    return df[df[col].astype(str).str.strip().ne("")]

players = load_csv("players")
yearly = load_csv("yearly")
competitions = load_csv("competitions")
trophies = load_csv("trophies")
awards = load_csv("awards")
teams = load_csv("teams")

if "flash_message" in st.session_state:
    st.info(st.session_state.pop("flash_message"))

with st.sidebar:
    st.markdown("## 🏏 CRICKET")
    st.markdown("### **BALLON D’OR**")
    st.caption("Men’s cricket • Black & Gold")
    page = st.radio("Navigation", [
        "Home", "Players", "Individual Performance", "Ballon d’Or",
        "Trophies & Awards", "Teams & Competitions", "Cricket AI", "Admin / Data"
    ])
    st.divider()
    st.caption("Historical values are only authoritative when marked Verified.")

st.markdown('<div class="hero"><h1>CRICKET BALLON D’OR</h1><p>THE GREATEST PLAYERS. THE BIGGEST STAGES. ONE AWARD.</p><p class="small-note">Men’s cricket • Year-by-year ratings • Career performance • Trophies and honours</p></div>', unsafe_allow_html=True)

if page == "Home":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Player records", f"{len(players):,}")
    c2.metric("Yearly performance rows", f"{len(yearly):,}")
    c3.metric("Trophy records", f"{len(nonempty(trophies, 'player_name')):,}")
    c4.metric("Individual awards", f"{len(nonempty(awards, 'player_name')):,}")
    st.subheader("Explore the archive")
    a,b,c = st.columns(3)
    with a:
        st.markdown("### Player profiles")
        st.write("Find a player and review available career information, team association, and season records.")
    with b:
        st.markdown("### Annual performance")
        st.write("Track yearly runs, match awards, statistics, and manually assigned OVR ratings.")
    with c:
        st.markdown("### Trophies and honours")
        st.write("Record competition winners, player trophy associations, and individual awards.")
    st.warning("Starter dataset: player names are seeded, but historical statistics, trophies, MOM totals, and OVR ratings are not yet populated. Add verified records in Admin / Data.")
    st.subheader("Featured players")
    if not players.empty:
        st.dataframe(players[["player_name","country_or_primary_association","primary_role","verification_status"]].head(12), use_container_width=True, hide_index=True)

elif page == "Players":
    st.subheader("Men’s player archive")
    q = st.text_input("Search player or country")
    role_opts = sorted([x for x in players.get("primary_role", pd.Series(dtype=str)).astype(str).unique() if x.strip()])
    role = st.selectbox("Role", ["All roles"] + role_opts)
    view = players.copy()
    if q:
        mask = view.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
        view = view[mask]
    if role != "All roles" and "primary_role" in view:
        view = view[view["primary_role"] == role]
    show_cols = [c for c in ["player_name","country_or_primary_association","primary_role","batting_style","bowling_style","career_start_year","career_end_year","verification_status"] if c in view]
    st.dataframe(view[show_cols], use_container_width=True, hide_index=True)
    st.download_button("Download filtered players CSV", view.to_csv(index=False).encode("utf-8-sig"), "players_filtered.csv", "text/csv")

elif page == "Individual Performance":
    st.subheader("Individual player performance")
    if players.empty:
        st.info("Import a player list in Admin / Data first.")
    else:
        names = sorted(players["player_name"].dropna().astype(str).unique())
        chosen = st.selectbox("Select player", names)
        p = players[players["player_name"] == chosen].iloc[0]
        left,right = st.columns([1,2])
        with left:
            st.markdown(f"## {chosen}")
            st.markdown(f"**Country / association:** {p.get('country_or_primary_association','')}")
            st.markdown(f"**Role:** {p.get('primary_role','Not entered') or 'Not entered'}")
            st.markdown(f"**Career:** {p.get('career_start_year','') or 'Unknown'} – {p.get('career_end_year','') or 'Present/unknown'}")
            st.markdown(f"**Record status:** {p.get('verification_status','')}")
            st.markdown(f"**Career MOM total:** {p.get('career_total_MOM_all_formats','') or 'Not entered'}")
        with right:
            hist = yearly[yearly["player_name"] == chosen].copy() if "player_name" in yearly else pd.DataFrame()
            if not hist.empty:
                for col in ["year","runs","matches","player_of_the_match_awards_this_year","yearly_OVR"]:
                    if col in hist:
                        hist[col] = pd.to_numeric(hist[col], errors="coerce")
                valid_ovr = hist.dropna(subset=["year","yearly_OVR"]) if {"year","yearly_OVR"}.issubset(hist.columns) else pd.DataFrame()
                if not valid_ovr.empty:
                    st.plotly_chart(px.line(valid_ovr, x="year", y="yearly_OVR", markers=True, title="OVR by year", color_discrete_sequence=[GOLD]), use_container_width=True)
                else:
                    st.info("No yearly OVR values entered for this player yet.")
        st.markdown("### Yearly performance records")
        if "player_name" in yearly:
            hist = yearly[yearly["player_name"] == chosen].copy()
            st.dataframe(hist, use_container_width=True, hide_index=True)
        st.markdown("### Trophies")
        pt = trophies[trophies.get("player_name", pd.Series(dtype=str)).astype(str) == chosen] if not trophies.empty else trophies
        st.dataframe(pt, use_container_width=True, hide_index=True)
        st.markdown("### Individual awards")
        pa = awards[awards.get("player_name", pd.Series(dtype=str)).astype(str) == chosen] if not awards.empty else awards
        st.dataframe(pa, use_container_width=True, hide_index=True)

elif page == "Ballon d’Or":
    st.subheader("Cricket Ballon d’Or — annual awards")
    st.write("Use this section to maintain your custom annual award. It is not an official ICC award.")
    if not awards.empty:
        ba = awards[awards.get("award_name", pd.Series(dtype=str)).astype(str).str.contains("Ballon d'Or|Ballon d’Or", case=False, regex=True)]
        if not ba.empty:
            st.dataframe(ba, use_container_width=True, hide_index=True)
        else:
            st.info("No Ballon d’Or winners have been entered yet.")
    else:
        st.info("No award results have been entered yet. Add winners and nominees in Admin / Data.")
    st.markdown("### Add award results")
    with st.form("ballon_form"):
        year = st.number_input("Award year", min_value=1877, max_value=2100, value=2026)
        award_player = st.selectbox("Player", sorted(players["player_name"].astype(str).unique()) if not players.empty else [""])
        result = st.selectbox("Result", ["Winner","Nominee","Shortlisted"])
        source = st.text_input("Source URL (recommended)")
        submitted = st.form_submit_button("Save award result")
    if submitted and award_player:
        row = {"award_record_id": (pd.to_numeric(awards.get("award_record_id", pd.Series(dtype=float)), errors="coerce").max() if not awards.empty else 0) + 1,
               "player_id": int(players.loc[players.player_name == award_player, "player_id"].iloc[0]),
               "player_name": award_player, "year": int(year), "award_name": "Cricket Ballon d’Or",
               "competition_name": "", "result": result, "verification_status": "Needs verification",
               "source_url": source, "notes": ""}
        awards = pd.concat([awards, pd.DataFrame([row])], ignore_index=True)
        save_csv("awards", awards)
        st.session_state["flash_message"] = "Award result saved to the app data file for this runtime."
        st.rerun()

elif page == "Trophies & Awards":
    st.subheader("Player trophies and individual awards")
    tab1,tab2,tab3 = st.tabs(["Player trophies","Individual awards","Competition winners"])
    with tab1:
        st.dataframe(trophies, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(awards, use_container_width=True, hide_index=True)
    with tab3:
        st.dataframe(competitions, use_container_width=True, hide_index=True)
    st.caption("Only add a player trophy association when participation or eligibility is supported by a reliable source.")

elif page == "Teams & Competitions":
    st.subheader("Teams and competitions")
    tab1,tab2 = st.tabs(["Teams","Competition seasons"])
    with tab1:
        st.dataframe(teams, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(competitions, use_container_width=True, hide_index=True)
    st.info("Import verified team and competition season records through Admin / Data.")

elif page == "Cricket AI":
    st.subheader("Cricket AI assistant")
    st.caption("DEMO MODE — no external AI API is configured. Answers use the local starter database and simple record lookup.")
    question = st.text_input("Ask about a player, yearly runs, MOM, OVR, trophies, or awards")
    if st.button("Ask Cricket AI", type="primary"):
        q = question.strip().lower()
        if not q:
            st.warning("Enter a question first.")
        else:
            matched = players[players["player_name"].astype(str).str.lower().apply(lambda n: n in q or q in n)] if not players.empty else pd.DataFrame()
            if not matched.empty:
                pname = matched.iloc[0]["player_name"]
                pp = matched.iloc[0]
                st.markdown(f"### {pname}")
                st.write(f"Country/association: {pp.get('country_or_primary_association','Not recorded')}")
                st.write(f"Role: {pp.get('primary_role','Not recorded') or 'Not recorded'}")
                st.write(f"Record status: {pp.get('verification_status','Not recorded')}")
                py = yearly[yearly["player_name"] == pname] if "player_name" in yearly else pd.DataFrame()
                if not py.empty:
                    st.dataframe(py, use_container_width=True, hide_index=True)
                else:
                    st.info("No yearly statistics have been recorded for this player yet.")
            elif any(word in q for word in ["how many players","player count","total players"]):
                st.write(f"The current starter database contains {len(players)} player records.")
            else:
                st.info("Demo mode cannot answer general cricket questions yet. Configure an AI API key and retrieval service to enable broader answers. Do not treat unverified starter data as factual.")

elif page == "Admin / Data":
    st.subheader("Admin / data management")
    st.warning("This starter deployment does not include user authentication. Do not expose an editable admin page publicly with sensitive data.")
    st.markdown("### Import CSV files")
    instructions = {
        "players": "players.csv",
        "yearly": "yearly_performance.csv",
        "trophies": "player_trophies.csv",
        "awards": "individual_awards.csv",
        "competitions": "competitions.csv",
        "teams": "teams.csv",
    }
    for key, filename in instructions.items():
        with st.expander(f"Import {filename}"):
            uploaded = st.file_uploader(f"Choose {filename}", type=["csv"], key=f"upload_{key}")
            if uploaded is not None:
                try:
                    incoming = pd.read_csv(uploaded, keep_default_na=False)
                    st.write(f"Preview: {len(incoming)} rows")
                    st.dataframe(incoming.head(10), use_container_width=True, hide_index=True)
                    mode = st.radio("Import mode", ["Replace existing file", "Append rows"], key=f"mode_{key}")
                    if st.button(f"Apply import for {filename}", key=f"apply_{key}"):
                        current = load_csv(key)
                        result = incoming if mode == "Replace existing file" else pd.concat([current, incoming], ignore_index=True)
                        save_csv(key, result)
                        st.session_state["flash_message"] = f"Imported {len(incoming)} rows into {filename}."
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not read CSV: {e}")
    st.markdown("### Download current data")
    for key, filename in instructions.items():
        current = load_csv(key)
        st.download_button(f"Download {filename}", current.to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"download_{key}")
    st.markdown("### Data quality")
    quality = []
    for key, filename in instructions.items():
        d = load_csv(key)
        quality.append({"file": filename, "rows": len(d), "columns": len(d.columns)})
    st.dataframe(pd.DataFrame(quality), use_container_width=True, hide_index=True)
    st.markdown("### Verification policy")
    st.write("Use status values such as Draft, Verified, Disputed, or Superseded. Include a source URL for each historical statistic, award, trophy, or season record. Never invent missing values.")
