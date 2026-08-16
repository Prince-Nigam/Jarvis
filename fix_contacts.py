import sqlite3, sys
sys.path.insert(0, '.')

con = sqlite3.connect('jarvis.db')
cur = con.cursor()
cur.execute('DELETE FROM contacts')
con.commit()
con.close()
print('Cleared old contacts')

from engine.init_db import init_database
init_database()
print('Re-imported from contacts.csv')

con = sqlite3.connect('jarvis.db')
cur = con.cursor()
cur.execute('SELECT COUNT(*) FROM contacts')
total = cur.fetchone()[0]
print(f'Total contacts in DB: {total}')
print('\nSample contacts:')
cur.execute('SELECT name, mobile_no FROM contacts LIMIT 10')
for name, mobile in cur.fetchall():
    print(f'  {name} → {mobile}')
con.close()
