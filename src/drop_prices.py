from utils_db import get_conn

with get_conn() as conn:
    conn.execute("DROP TABLE IF EXISTS prices")
    conn.execute("DROP TABLE IF EXISTS features")
    conn.commit()

print("✅ Dropped old tables prices + features")
