from utils_db import get_conn

def reset_tables():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS prices")
        cursor.execute("DROP TABLE IF EXISTS features")
        cursor.execute("DROP TABLE IF EXISTS rss_news")
        conn.commit()
    print("✅ Dropped old tables: prices, features, rss_news")

if __name__ == "__main__":
    reset_tables()
