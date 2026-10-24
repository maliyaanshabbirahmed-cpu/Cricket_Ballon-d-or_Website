# Cricket Ballon d’Or — Streamlit starter application

A black-and-gold Streamlit app for men's cricket player profiles, annual performance, yearly OVR ratings, trophies, individual awards, teams, competitions, and a demo Cricket AI panel.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload the contents of this folder to the repository root (not just the ZIP file).
3. Open Streamlit Community Cloud and create an app from the repository.
4. Select `app.py` as the main file.
5. Deploy.

## Included files

- `app.py`: working Streamlit UI and data import/export screens.
- `data/players.csv`: 244 men's cricket player starter records.
- `data/yearly_performance.csv`: starter rows and columns for annual stats, runs, MOM, trophies, OVR and source verification.
- `data/player_trophies.csv`: player trophy association template.
- `data/individual_awards.csv`: awards and Ballon d’Or result template.
- `data/competitions.csv`: competition-season and winner template.
- `data/teams.csv`: team history template.

## Important data and deployment limits

The starter CSV includes player names, not a complete verified cricket history. Annual runs, MOM counts, OVRs, trophies, and awards are blank until sourced and entered. The app does not fabricate those facts.

This version is a functional starter application, not a fully researched historical cricket database. It includes player browsing, player performance views, a custom Ballon d’Or entry form, trophy/award tables, teams/competitions tables, CSV import/export, and a demo-mode Cricket AI lookup.

Streamlit Community Cloud's local filesystem is not a reliable permanent database. Changes written to CSV during a session may be lost after restart, redeploy, or environment replacement. Before treating this as a public production website, connect a managed PostgreSQL database, add admin authentication, and store image assets externally. The current admin page is not protected and should not be used to expose sensitive data.

## Data model guidance

- One yearly performance row should represent a player + year + format/competition.
- Enter Test, ODI, T20I, IPL, PSL and other competitions as separate records where applicable.
- Record yearly runs, matches, MOM awards, OVR, and attributes in that row.
- Record trophies in `player_trophies.csv` and team-season winners in `competitions.csv`.
- Only associate a player with a trophy when the player's participation/eligibility is supported.
- Use `verification_status` and `source_url` to track evidence.
- Never overwrite a finalized historic rating silently; retain a revision history when you introduce a persistent database.

## Suggested verification status values

`Draft`, `Verified`, `Disputed`, `Superseded`, `Needs research and verification`.

## Scope

Men's cricket only. The included player list is a starter list and is not exhaustive of every international, domestic, or franchise cricketer.
