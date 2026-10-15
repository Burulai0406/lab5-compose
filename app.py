from flask import Flask, request, jsonify
import os
import psycopg2
import redis

app = Flask(__name__)

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'labdb'),
        user=os.getenv('DB_USER', 'labuser'),
        password=os.getenv('DB_PASSWORD', 'labpassword123'),
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', 5432)
    )

# Таблицаны автоматтык түрдө түзүп алуу
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            )
        ''')
    conn.commit()

@app.route('/health')
def health():
    return {"status": "healthy", "message": "API is working!"}

@app.route('/db-test')
def db_test():
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "Connected to PostgreSQL successfully!"
    except Exception as e:
        db_status = f"PostgreSQL connection failed: {str(e)}"

    try:
        redis_client.ping()
        redis_status = "Connected to Redis successfully!"
    except Exception as e:
        redis_status = f"Redis connection failed: {str(e)}"

    return {
        "database": db_status,
        "redis": redis_status
    }

@app.route('/cache-test')
def cache_test():
    try:
        redis_client.set('test_key', 'Hello from Redis Cache!')
        value = redis_client.get('test_key')
        return {
            "status": "success",
            "cached_value": value
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;", (name, email))
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "id": user_id, "name": name, "email": email}), 201
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    elif request.method == 'GET':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, email FROM users;")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            users_list = []
            for row in rows:
                users_list.append({"id": row[0], "name": row[1], "email": row[2]})
                
            return jsonify(users_list), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users WHERE id = %s;", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({"id": row[0], "name": row[1], "email": row[2]}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
