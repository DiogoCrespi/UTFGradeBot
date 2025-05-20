import psycopg2

conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="1597",
    database="turing_bot"
)

cur = conn.cursor()
cur.execute("SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'turmas'::regclass;")
constraints = cur.fetchall()
for conname, contype, condef in constraints:
    print(f"Constraint: {conname}, Type: {contype}, Definition: {condef}")

cur.close()
conn.close() 