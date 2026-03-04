import matplotlib.pyplot as plt
import akshare as ak
import pandas as pd
import numpy as np
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

load_dotenv()

# ---------- 1. 从数据库读取收盘价数据 ----------
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset='utf8mb4'
)
query = "SELECT code, trade_date, close FROM stock_daily ORDER BY code, trade_date"
df = pd.read_sql(query, conn)
df['trade_date'] = pd.to_datetime(df['trade_date'])
conn.close()

# 转换为宽表格式：index=日期，columns=股票代码，values=收盘价
pivot = df.pivot(index='trade_date', columns='code', values='close')
pivot.index = pd.to_datetime(pivot.index)
pivot = pivot.sort_index()
print(f"数据日期范围：{pivot.index[0]} 至 {pivot.index[-1]}，共 {len(pivot)} 个交易日，{len(pivot.columns)} 只股票")

# ---------- 2. 获取沪深300指数数据作为基准 ----------

index_df = ak.stock_zh_index_daily(symbol="sh000300")  # 沪深300
index_df['date'] = pd.to_datetime(index_df['date'])
index_df.set_index('date', inplace=True)
index_df.sort_index(inplace=True)
# 与股票日期对齐
common_dates = pivot.index.intersection(index_df.index)
pivot = pivot.loc[common_dates]
benchmark = index_df.loc[common_dates, 'close']
benchmark_ret = benchmark.pct_change()


# ---------- 3. 定义动量策略回测函数 ----------
def momentum_backtest(prices, lookback=30, top_n=20, rebalance_freq='ME', cost=0.0025):
    """
    prices: DataFrame, 行=日期, 列=股票代码, 值=收盘价
    返回：策略每日收益率序列（Series, index=日期）
    """

    # 计算每日收益率
    returns = prices.pct_change()

    # 计算调仓日收益率（用于选股）
    # 注意：用 lookback 天前的价格计算区间收益，需确保数据足够
    momentum = prices.pct_change(lookback)  # 第 t 天的 momentum 是 t 相对于 t-lookback 的收益

    # 生成调仓信号：每月最后一个交易日
    rebalance_dates = prices.resample(rebalance_freq).last().index

    # 初始化持仓权重矩阵（每日）
    weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

    for date in rebalance_dates:
        if date not in prices.index:
            continue
        # 选股日期：调仓日的前一天（确保使用收盘价，避免未来函数）
        signal_date = prices.index[prices.index < date][-1] if len(prices.index[prices.index < date]) > 0 else None
        if signal_date is None:
            continue

        # 获取 signal_date 当天的动量值
        if signal_date not in momentum.index:
            continue
        signal = momentum.loc[signal_date].dropna()
        if len(signal) < top_n:
            continue

        # 选取动量最高的 top_n 只
        selected = signal.nlargest(top_n).index

        # 等权重配置
        weight = 1.0 / top_n
        # 从调仓日开始，持有到下一次调仓日（或到最后）
        next_date_idx = prices.index.get_loc(date)
        if next_date_idx + 1 < len(prices.index):
            end_date = rebalance_dates[rebalance_dates.get_loc(date) + 1] if date != rebalance_dates[-1] else \
            prices.index[-1]
        else:
            end_date = prices.index[-1]
        weights.loc[date:end_date, selected] = weight

        # 在 momentum_backtest 函数中，生成 weights 之后添加：
        if date == rebalance_dates[5]:  # 打印第6个月的持仓
            print(f"{date} 持仓股票: {selected.tolist()}")

    # 计算每日组合收益率 = (今日持仓 * 今日个股收益率).sum(axis=1)
    # 注意：需用前一天的持仓权重乘以今天的个股收益率
    portfolio_ret = (returns * weights.shift(1)).sum(axis=1)
    return portfolio_ret.dropna()


# ---------- 4. 运行回测 ----------
strategy_ret = momentum_backtest(pivot, lookback=30, top_n=20, rebalance_freq='ME', cost=0.0025)

# 对齐基准和策略的日期
common = strategy_ret.index.intersection(benchmark_ret.index)
strategy_ret = strategy_ret.loc[common]
benchmark_ret = benchmark_ret.loc[common]


# ---------- 5. 计算绩效指标 ----------
def performance(returns, benchmark_returns=None, rf=0.03):
    # 累计收益率
    cum_ret = (1 + returns).cumprod()
    total_ret = cum_ret.iloc[-1] - 1
    # 年化收益率（假设252个交易日）
    years = len(returns) / 252
    annual_ret = (1 + total_ret) ** (1 / years) - 1
    # 年化波动率
    annual_vol = returns.std() * np.sqrt(252)
    # 夏普比率
    sharpe = (annual_ret - rf) / annual_vol if annual_vol != 0 else 0
    # 最大回撤
    rolling_max = cum_ret.cummax()
    drawdown = (cum_ret / rolling_max - 1)
    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()

    # 相对基准的指标
    if benchmark_returns is not None:
        # 超额收益
        excess_ret = returns - benchmark_returns
        cum_excess = (1 + excess_ret).cumprod()
        total_excess = cum_excess.iloc[-1] - 1
        # 信息比率
        tracking_error = excess_ret.std() * np.sqrt(252)
        info_ratio = (excess_ret.mean() * 252) / tracking_error if tracking_error != 0 else 0
        # 胜率
        win_rate = (excess_ret > 0).mean()
    else:
        total_excess = info_ratio = win_rate = None

    return {
        '总收益率': f"{total_ret:.2%}",
        '年化收益率': f"{annual_ret:.2%}",
        '年化波动率': f"{annual_vol:.2%}",
        '夏普比率': round(sharpe, 2),
        '最大回撤': f"{max_dd:.2%}",
        '最大回撤日期': max_dd_date.strftime("%Y-%m-%d"),
        '超额收益': f"{total_excess:.2%}" if total_excess is not None else None,
        '信息比率': round(info_ratio, 2) if info_ratio is not None else None,
        '胜率': f"{win_rate:.2%}" if win_rate is not None else None,
    }


perf = performance(strategy_ret, benchmark_ret)

# ---------- 6. 输出结果 ----------
print("\n========== 动量策略回测结果 ==========")
for k, v in perf.items():
    print(f"{k}: {v}")

# 可选：绘制净值曲线
try:

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
    plt.rcParams['axes.unicode_minus'] = False

    nav_strategy = (1 + strategy_ret).cumprod()
    nav_benchmark = (1 + benchmark_ret).cumprod()

    plt.figure(figsize=(12, 6))
    plt.plot(nav_strategy.index, nav_strategy, label='策略净值')
    plt.plot(nav_benchmark.index, nav_benchmark, label='沪深300净值')
    plt.legend()
    plt.title('动量策略回测净值曲线')
    plt.grid(True)
    plt.show()
    print("\n策略净值序列（前5行）：")
    print(strategy_ret.head())
except:
    print("\n（未安装matplotlib，跳过绘图）")