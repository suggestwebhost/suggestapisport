import os
from flask import Flask, jsonify, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# Core endpoint targeting configuration
API_KEY = os.environ.get("SPORTS_DB_KEY", "3")
THE_SPORTS_DB_BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"

def fetch_team_data(team_name):
    search_url = f"{THE_SPORTS_DB_BASE_URL}/searchteams.php?t={team_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data.get('teams'), list) and len(data['teams']) > 0:
            return data['teams'][0] # Grab the first matched team safely
    except Exception:
        pass
    return None

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        search_query = request.form.get('team_name_input', '').strip()
        if search_query:
            return redirect(url_for('view_team_sprites', team_name=search_query))
            
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sports Sprite Finder</title>
        <style>
            body { font-family: sans-serif; background: #f4f6f9; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .search-box { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); text-align: center; max-width: 400px; width: 100%; }
            input[type="text"] { width: 80%; padding: 12px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px; outline: none; }
            button { background: #007bff; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="search-box">
            <h2>🔍 Sports Sprite Engine</h2>
            <p>Enter a team name to view graphics assets</p>
            <form method="POST">
                <input type="text" name="team_name_input" placeholder="e.g. Real Madrid, Lakers, Chelsea" required autocomplete="off">
                <br>
                <button type="submit">Search Assets</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route('/view-sprites/<team_name>', methods=['GET'])
def view_team_sprites(team_name):
    team_info = fetch_team_data(team_name)
    if not team_info:
        return f"""
        <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
            <h1>❌ Team '{team_name}' not found.</h1>
            <a href="/" style="color:#007bff; text-decoration:none;">← Return to Search Dashboard</a>
        </div>
        """, 404

    placeholder = "https://placehold.co"
    badge = team_info.get("strBadge") or placeholder
    jersey = team_info.get("strEquipment") or placeholder
    logo = team_info.get("strLogo") or placeholder
    banner = team_info.get("strBanner") or placeholder
    name = team_info.get("strTeam", team_name)

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{name} Sprites</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f6f9; text-align: center; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .nav-link {{ display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; font-weight: bold; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ background: #fafafa; border: 1px solid #eee; padding: 15px; border-radius: 8px; }}
            .card img {{ max-width: 100%; height: auto; max-height: 150px; object-fit: contain; }}
            .banner-box {{ margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
            .banner-box img {{ max-width: 100%; height: auto; max-height: 100px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a class="nav-link" href="/">← Back to Search</a>
            <h1>🎨 {name} Sprite Viewer</h1>
            <div class="grid">
                <div class="card"><h3>Official Badge</h3><img src="{badge}"></div>
                <div class="card"><h3>Team Jersey</h3><img src="{jersey}"></div>
                <div class="card"><h3>Brand Logo</h3><img src="{logo}"></div>
            </div>
            <div class="banner-box"><h3>Horizontal Banner</h3><img src="{banner}"></div>
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
