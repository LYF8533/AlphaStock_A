import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine

# 加载 .env 文件中的环境变量
load_dotenv()

app = FastAPI(title="A股动量选股 API")

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境可替换为具体域名
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接函数
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "123456"),
        database=os.getenv("DB_NAME", "stock_db"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/")
def root():
    return {"message": "A股动量选股系统后端运行中"}

@app.get("/stock/{code}")
async def get_stock_data(code: str, limit: int = Query(60, description="返回最近多少条数据")):
    """
    获取单只股票的历史日线数据，按日期倒序返回。
    """
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT trade_date, open, close, high, low, volume
            FROM stock_daily
            WHERE code = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """, (code, limit))
        result = cursor.fetchall()
    conn.close()
    return {"code": code, "data": result}

@app.get("/select/momentum")
async def select_momentum(
    top_n: int = Query(10, description="选出前几只股票"),
    days: int = Query(20, description="计算涨幅的天数")
):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # 获取所有股票的最新交易日期，并关联名称
        cursor.execute("""
            SELECT d.code, i.name, MAX(d.trade_date) as last_date
            FROM stock_daily d
            LEFT JOIN stock_info i ON d.code = i.code
            GROUP BY d.code, i.name
        """)
        stocks = cursor.fetchall()

        results = []
        for s in stocks:
            code = s['code']
            name = s['name'] or ''
            last_date = s['last_date']

            # 获取最新收盘价
            cursor.execute("SELECT close FROM stock_daily WHERE code=%s AND trade_date=%s", (code, last_date))
            row = cursor.fetchone()
            if not row:
                continue
            last_close = float(row['close'])

            # 获取 days 天前的收盘价
            cursor.execute("""
                SELECT close, trade_date FROM stock_daily
                WHERE code=%s AND trade_date <= DATE_SUB(%s, INTERVAL %s DAY)
                ORDER BY trade_date DESC LIMIT 1
            """, (code, last_date, days))
            past = cursor.fetchone()
            if not past:
                continue
            past_close = float(past['close'])
            past_date = past['trade_date']

            # 剔除数据稀疏
            if (last_date - past_date).days > days * 1.2:
                continue
            if past_close == 0:
                continue

            gain = (last_close - past_close) / past_close
            results.append({
                "code": code,
                "name": name,
                "last_date": last_date.strftime("%Y-%m-%d"),
                "last_close": round(last_close, 2),
                "past_date": past_date.strftime("%Y-%m-%d"),
                "past_close": round(past_close, 2),
                f"gain_{days}d": round(gain * 100, 2)
            })

    conn.close()
    results.sort(key=lambda x: x[f"gain_{days}d"], reverse=True)
    return {"top": results[:top_n]}




@app.get("/backtest")
async def backtest(
        lookback: int = Query(30, description="动量计算天数"),
        top_n: int = Query(20, description="选股数量"),
        rebalance_freq: str = Query("ME", description="调仓频率 (ME=月末)"),
        cost: float = Query(0.0025, description="单边交易成本")
):
    try:
        engine = create_engine(
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
        )
        query = "SELECT code, trade_date, close FROM stock_daily ORDER BY code, trade_date"
        df = pd.read_sql(query, engine)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.drop_duplicates(subset=['code', 'trade_date'], keep='last')
        pivot = df.pivot(index='trade_date', columns='code', values='close')
        pivot.sort_index(inplace=True)

        # 动量回测函数（与脚本完全一致）
        def momentum_backtest(prices, lookback, top_n, freq, cost):
            returns = prices.pct_change()
            momentum = prices.pct_change(lookback)
            rebalance_dates = prices.resample(freq).last().index
            weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

            for date in rebalance_dates:
                if date not in prices.index:
                    continue
                signal_date = prices.index[prices.index < date][-1] if len(prices.index[prices.index < date]) > 0 else None
                if signal_date is None:
                    continue
                if signal_date not in momentum.index:
                    continue
                signal = momentum.loc[signal_date].dropna()
                if len(signal) < top_n:
                    continue
                selected = signal.nlargest(top_n).index
                weight = 1.0 / top_n

                # 确定本次持仓的结束日期（下一次调仓日或数据末尾）
                next_date_idx = prices.index.get_loc(date)
                if next_date_idx + 1 < len(prices.index):
                    end_date = rebalance_dates[rebalance_dates.get_loc(date) + 1] if date != rebalance_dates[-1] else prices.index[-1]
                else:
                    end_date = prices.index[-1]
                weights.loc[date:end_date, selected] = weight

            portfolio_ret = (returns * weights.shift(1)).sum(axis=1)
            turnover = top_n / len(prices.columns)
            portfolio_ret -= turnover * cost
            return portfolio_ret.dropna()

        ret = momentum_backtest(pivot, lookback, top_n, rebalance_freq, cost)
        nav = (1 + ret).cumprod()
        total_ret = (nav.iloc[-1] - 1) * 100
        years = len(ret) / 252
        annual_ret = (nav.iloc[-1] ** (1 / years) - 1) * 100 if years > 0 else 0
        annual_vol = ret.std() * np.sqrt(252) * 100
        sharpe = (annual_ret - 3) / annual_vol if annual_vol != 0 else 0
        max_dd = ((nav / nav.cummax() - 1).min()) * 100

        return {
            "nav": [{"date": str(d.date()), "value": float(v)} for d, v in nav.items()],
            "metrics": {
                "总收益率": f"{float(total_ret):.2f}%",
                "年化收益率": f"{float(annual_ret):.2f}%",
                "年化波动率": f"{float(annual_vol):.2f}%",
                "夏普比率": round(float(sharpe), 2),
                "最大回撤": f"{float(max_dd):.2f}%"
            }
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}