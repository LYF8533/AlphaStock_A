import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
import pymysql
from dotenv import load_dotenv
import os
import time
import akshare as ak  # 用于获取成分股列表

# 加载环境变量
load_dotenv()

# 数据库连接
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "123456"),
    database=os.getenv("DB_NAME", "stock_db"),
    charset='utf8mb4'
)
cursor = conn.cursor()


# ---------- 1. 获取沪深300成分股列表 ----------
def get_csi300_stocks():
    """返回 (code, name) 列表"""
    print("正在获取沪深300成分股列表...")
    try:
        stock_df = ak.index_stock_cons_csindex("000300")
        # 提取代码和名称，并转为字符串格式
        codes = stock_df['成分券代码'].astype(str).str.zfill(6).tolist()
        names = stock_df['成分券名称'].tolist()
        print(f"成功获取 {len(codes)} 只成分股")
        return list(zip(codes, names))
    except Exception as e:
        print(f"获取成分股失败: {e}")
        print("使用备选测试列表（3只）")
        return [("000001", "平安银行"), ("000002", "万科A"), ("600519", "贵州茅台")]


# ---------- 2. 拉取单只股票数据并入库 ----------
def fetch_and_store_stock(code, name, start_date, end_date):
    """获取单只股票历史数据，存入数据库"""
    # 转换为 baostock 格式
    bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"

    print(f"  正在获取 {code} {name}...")
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,code,open,high,low,close,volume",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3"
    )

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    if not data_list:
        print(f"    {code} 无数据")
        return 0

    df = pd.DataFrame(data_list, columns=rs.fields)

    # 存入数据库
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO stock_daily (code, trade_date, open, close, high, low, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                open=VALUES(open), close=VALUES(close), high=VALUES(high), low=VALUES(low), volume=VALUES(volume)
            """, (
                code,
                row['date'],
                float(row['open']),
                float(row['close']),
                float(row['high']),
                float(row['low']),
                int(float(row['volume'])) if row['volume'] else 0
            ))
            inserted += 1
        except Exception as e:
            print(f"    插入失败: {e} 日期:{row['date']}")
    conn.commit()
    print(f"    {code} 完成，入库 {inserted} 条")
    return inserted


# ---------- 3. 主流程 ----------
def main():
    # 登录 baostock
    bs.login()

    # 设置时间范围：最近一年
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")
    print(f"时间范围: {start_date} 至 {end_date}")

    # 获取股票列表
    stocks = get_csi300_stocks()
    total = len(stocks)
    print(f"共 {total} 只股票，开始拉取...\n")

    # 循环拉取
    total_inserted = 0
    for idx, (code, name) in enumerate(stocks, 1):
        inserted = fetch_and_store_stock(code, name, start_date, end_date)
        total_inserted += inserted
        print(f"进度: [{idx}/{total}] 累计入库 {total_inserted} 条\n")
        time.sleep(0.5)  # 暂停半秒，避免请求过快

    bs.logout()
    cursor.close()
    conn.close()
    print(f"✅ 全部完成！共入库 {total_inserted} 条记录")


if __name__ == "__main__":
    main()