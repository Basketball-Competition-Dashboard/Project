import sqlite3

DATABASE_PATH = f'data/nbaDB.db'

def create_games_status(data,home_team_city,home_team_id,away_team_id):
    try:
        data_dict = dict(data)
        data = data_dict
        date = data.get('date')
        
        conn = sqlite3.connect(DATABASE_PATH, isolation_level='IMMEDIATE')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Game (Date, SID, Place) VALUES (?, ?, ?)", (date, 12005, home_team_city))
        game_id = cursor.lastrowid
     
        home_score = data.get('home_score', 0)
        away_score = data.get('away_score', 0)
        
        if home_score > away_score:
            is_home_winner = True
        else:
            is_home_winner = False

        is_away_winner = not is_home_winner

        attend_query = "INSERT INTO Attend (GID, TID, Is_home_team, Score, Is_win_team) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(attend_query, (game_id, home_team_id, 1, home_score, is_home_winner))
        cursor.execute(attend_query, (game_id, away_team_id, 0, away_score, is_away_winner))
        sql = """
            SELECT 
                away_team.NameAbbr AS away_abbr,
                away_team.TID AS away_id,
                away_team.Nickname AS away_name,
                away_attend.Score AS away_score,
                strftime('%Y-%m-%d', g.Date) AS date,
                home_team.NameAbbr AS home_abbr,
                home_team.TID AS home_id,
                home_team.Nickname AS home_name,
                home_attend.Score AS home_score,
                g.GID AS id,
                CASE WHEN home_attend.Score > away_attend.Score THEN 1 ELSE 0 END AS is_home_winner
            FROM 
                Game AS g
            JOIN 
                Attend AS home_attend ON g.GID = home_attend.GID AND home_attend.is_home_team = 1
            JOIN 
                Attend AS away_attend ON g.GID = away_attend.GID AND away_attend.is_home_team = 0
            JOIN 
                Team AS home_team ON home_attend.TID = home_team.TID
            JOIN 
                Team AS away_team ON away_attend.TID = away_team.TID
            WHERE
                id = ? AND home_team.TID = ? AND away_team.TID = ?
            ORDER BY g.Date DESC
        """
        cursor.execute(sql, (game_id,home_team_id, away_team_id))
        conn.commit()

        cols = [col[0] for col in cursor.description]
        response = []
        for row in cursor.fetchall():
            response.append(dict(zip(cols, row)))
        conn.close() 
        response = response[0]
        return response,201

    except sqlite3.Error as e:
        print("SQLite error:", e.args[0])
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
    except Exception as e:
        print("General error:", str(e))
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
            
def create_teams_status(data):
    try:
        data_dict = dict(data)
        data = data_dict
        
        NameAbbr = data.get('abbr')
        City = data.get('city')
        Nickname = data.get('name')
        YearFounded = data.get('year_founded')
        CoachName = data.get('coach')

        conn = sqlite3.connect(DATABASE_PATH, isolation_level='IMMEDIATE')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Team (Nickname, City, NameAbbr, CoachName, YearFounded) VALUES (?, ?, ?, ?, ?)",(Nickname, City, NameAbbr, CoachName, YearFounded))
        team_id = cursor.lastrowid
       
        sql = """
            SELECT 
                t.Nickname AS team,
                t.City AS city,
                t.NameAbbr AS abbr,
                t.CoachName AS coach,
                t.YearFounded AS year_founded
            FROM 
                Team AS t
            WHERE
                t.TID = ?
        """
        cursor.execute(sql,(team_id,))
        conn.commit()

        cols = [col[0] for col in cursor.description]
        response = []
        for row in cursor.fetchall():
            response.append(dict(zip(cols, row)))
        conn.close() 
        response = response[0]
        
        return response,201

    except sqlite3.Error as e:
        print("SQLite error:", e.args[0])
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
    except Exception as e:
        print("General error:", str(e))
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
            


def get_team_id_and_city(team_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT TID, City FROM Team WHERE Nickname = ?", (team_name,))
    team_data = cursor.fetchone()
    conn.close()
    if team_data:
        return team_data[0], team_data[1]
    return None, None

def fetch_games_details(page_offset, page_length, sort_field, sort_order):
    try:
        sort_order_sql = 'ASC' if sort_order == 'ascending' else 'DESC'
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        query = f"""
            SELECT 
                away_team.NameAbbr AS away_abbr,
                away_team.TID AS away_id,
                away_team.Nickname AS away_name,
                away_attend.Score AS away_score,
                strftime('%Y-%m-%d', g.Date) AS date,
                home_team.NameAbbr AS home_abbr,
                home_team.TID AS home_id,
                home_team.Nickname AS home_name,
                home_attend.Score AS home_score,
                g.GID AS id,
                CASE WHEN home_attend.Score > away_attend.Score THEN 1 ELSE 0 END AS is_home_winner
            FROM 
                Game AS g
            JOIN 
                Attend AS home_attend ON g.GID = home_attend.GID AND home_attend.is_home_team = 1
            JOIN 
                Attend AS away_attend ON g.GID = away_attend.GID AND away_attend.is_home_team = 0
            JOIN 
                Team AS home_team ON home_attend.TID = home_team.TID
            JOIN 
                Team AS away_team ON away_attend.TID = away_team.TID
            ORDER BY
                CASE 
                    WHEN '{sort_field}' = 'away_abbr' THEN away_abbr
                    WHEN '{sort_field}' = 'away_id' THEN away_id
                    WHEN '{sort_field}' = 'away_name' THEN away_name
                    WHEN '{sort_field}' = 'away_score' THEN away_score
                    WHEN '{sort_field}' = 'date' THEN date
                    WHEN '{sort_field}' = 'home_abbr' THEN home_abbr
                    WHEN '{sort_field}' = 'home_id' THEN home_id
                    WHEN '{sort_field}' = 'home_name' THEN home_name
                    WHEN '{sort_field}' = 'home_score' THEN home_score
                    WHEN '{sort_field}' = 'is_home_winner' THEN is_home_winner
                    ELSE g.Date
                END {sort_order_sql}
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(query, (page_length, page_offset))
        conn.commit()

        cols = [col[0] for col in cursor.description]
        response = []
        for row in cursor.fetchall():
            response.append(dict(zip(cols, row)))
        conn.close() 

        return response, 201
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return {'error': str(e)}, 500
    
def update_games_status(id,team_id,data):
    try:
        
        is_winner = data["is_winner"]
        score = data["score"]
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE Attend SET is_win_team = ?, Score = ? WHERE GID =? AND TID =?", (is_winner,score,id,team_id))
        conn.commit()
        conn.close()
        return {'message': 'Game status updated'}, 201
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return {'error': str(e)}, 500