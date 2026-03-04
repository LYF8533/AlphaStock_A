import pymysql
from dotenv import load_dotenv
import os
import akshare as ak

load_dotenv()

conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset='utf8mb4'
)
cursor = conn.cursor()

# 获取沪深300成分股列表（包含名称）
print("正在获取成分股列表...")
stock_df = ak.index_stock_cons_csindex("000300")
codes = stock_df['成分券代码'].astype(str).str.zfill(6).tolist()
names = stock_df['成分券名称'].tolist()
code_name_map = dict(zip(codes, names))

# 插入或更新 stock_info
for code, name in code_name_map.items():
    cursor.execute("""
        INSERT INTO stock_info (code, name) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name)
    """, (code, name))

conn.commit()
cursor.close()
conn.close()
print(f"✅ stock_info 表已更新，共 {len(code_name_map)} 条记录")