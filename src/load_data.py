import pandas as pd
from sqlalchemy import create_engine
import pymysql

# ── 1. Load the Excel file ──────────────────────────────────────────
print("Reading Excel file... this may take 30-60 seconds")
df1 = pd.read_excel('data/online_retail_II.xlsx', sheet_name='Year 2009-2010')
df2 = pd.read_excel('data/online_retail_II.xlsx', sheet_name='Year 2010-2011')

# ── 2. Combine both sheets ───────────────────────────────────────────
df = pd.concat([df1, df2], ignore_index=True)
print(f"Total rows loaded: {len(df)}")
print(f"Columns: {list(df.columns)}")

# ── 3. Basic cleaning ────────────────────────────────────────────────
print("\nCleaning data...")

# Rename columns to be SQL friendly (lowercase, no spaces)
df.columns = ['invoice', 'stock_code', 'description', 'quantity',
              'invoice_date', 'price', 'customer_id', 'country']

# Drop rows where customer_id is missing (we need it for segmentation later)
df = df.dropna(subset=['customer_id'])

# Remove cancelled orders (invoices starting with C)
df = df[~df['invoice'].astype(str).str.startswith('C')]

# Remove rows with negative or zero quantity/price
df = df[df['quantity'] > 0]
df = df[df['price'] > 0]

# Add a total_amount column (quantity x price)
df['total_amount'] = df['quantity'] * df['price']

# Convert customer_id to integer
df['customer_id'] = df['customer_id'].astype(int)

print(f"Rows after cleaning: {len(df)}")
print(f"\nSample data:")
print(df.head())

# ── 4. Connect to MySQL ──────────────────────────────────────────────
print("\nConnecting to MySQL...")
engine = create_engine('mysql+pymysql://root:@localhost/retail_analytics')

# ── 5. Load into MySQL ───────────────────────────────────────────────
print("Loading data into MySQL... this may take a minute")
df.to_sql('transactions', con=engine, if_exists='replace', index=False)
print(f"\nDone! {len(df)} rows loaded into MySQL table 'transactions'")