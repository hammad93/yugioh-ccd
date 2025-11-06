## Convert CSV to SQLite3 Database
```python
import pandas as pd
import sqlite3

# read in CSV into DataFrame
df = pd.read_csv('yugioh-ccd-2025SEP12-163128.csv')
# create database and its Python interface
conn = sqlite3.connect('ygo_inventory.db')
# export DataFrame into database using SQL
df.to_sql('products', conn, index=False)
# without closing, the db file might get corrupted
conn.close()
```