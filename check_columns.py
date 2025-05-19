import psycopg2

conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="1597",
    database="turing_bot"
)

cur = conn.cursor()
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'turmas';
""")
for column, dtype in cur.fetchall():
    print(f"Coluna: {column}, Tipo: {dtype}")

cur.close()
conn.close() 