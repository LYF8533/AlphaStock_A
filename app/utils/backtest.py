"""
回测引擎模块 - 提供动量策略回测和绩效计算功能
"""

import pandas as pd
import numpy as np

def prepare_pivot_data(df):
    """
    准备回测用的pivot表

    将原始DataFrame转换为行=日期、列=股票代码的矩阵格式

    Args:
        df: 包含股票数据的DataFrame（必须有code、trade_date、close字段）

    Returns:
        DataFrame: pivot表，index=日期，columns=股票代码，values=收盘价
    """
    # 只保留需要的字段，避免后续处理出错
    df = df[['code', 'trade_date', 'close']].copy()
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.drop_duplicates(subset=['code', 'trade_date'], keep='last')

    # 转换为宽表格式
    pivot = df.pivot(index='trade_date', columns='code', values='close')
    pivot.sort_index(inplace=True)
    return pivot


def momentum_backtest(prices, lookback=30, top_n=20, freq='ME', cost=0.0025):
    """
    动量策略回测核心引擎

    每月/每周/每日调仓，计算过去lookback天的涨幅，选出top_n只等权重配置

    Args:
        prices: DataFrame, index=日期, columns=股票代码, values=收盘价
        lookback: 动量计算天数（默认30）
        top_n: 每期选股数量（默认20）
        freq: 调仓频率，'ME'=月末，'W'=每周，'D'=每日（默认'ME'）
        cost: 单边交易成本（默认0.0025，即0.25%）

    Returns:
        Series: 每日策略收益率序列，index=日期
    """
    # 计算每日收益率
    returns = prices.pct_change()

    # 计算动量（过去lookback天涨幅）
    momentum = prices.pct_change(lookback)

    # 生成调仓日期序列
    rebalance_dates = prices.resample(freq).last().index

    # 初始化持仓权重矩阵（每日）
    weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

    for date in rebalance_dates:
        # 如果调仓日不在交易日期中，跳过
        if date not in prices.index:
            continue

        # 选股日期：调仓日的前一天（避免未来函数）
        # 找到所有小于调仓日的日期，取最后一个
        dates_before = prices.index[prices.index < date]
        if len(dates_before) == 0:
            continue
        signal_date = dates_before[-1]

        # 如果信号日不在动量数据中，跳过
        if signal_date not in momentum.index:
            continue

        # 获取 signal_date 当天的动量值，去掉缺失值
        signal = momentum.loc[signal_date].dropna()

        # 如果可选的股票数量不足，跳过本次调仓
        if len(signal) < top_n:
            continue

        # 选取动量最高的 top_n 只股票
        # 方法：排序后取前 top_n 个的索引
        signal_sorted = signal.sort_values(ascending=False)
        selected = signal_sorted.head(top_n).index
        weight = 1.0 / top_n

        # 确定本次持仓的结束日期
        # 找到当前调仓日在价格索引中的位置
        next_date_idx = prices.index.get_loc(date)

        # 如果不是最后一天，结束日期为下一次调仓日或数据末尾
        if next_date_idx + 1 < len(prices.index):
            if date != rebalance_dates[-1]:
                # 找到下一个调仓日
                end_date = rebalance_dates[rebalance_dates.get_loc(date) + 1]
            else:
                end_date = prices.index[-1]
        else:
            end_date = prices.index[-1]

        # 从调仓日到结束日，持仓选中的股票
        weights.loc[date:end_date, selected] = weight

    # 计算每日组合收益率 = (前一日持仓 × 今日个股收益率).sum()
    # shift(1) 表示使用前一天的持仓权重
    portfolio_ret = (returns * weights.shift(1)).sum(axis=1)

    # 扣除交易成本
    # 简化模型：每次调仓换手率 = top_n/总股票数
    total_stocks = len(prices.columns)
    turnover = top_n / total_stocks
    portfolio_ret = portfolio_ret - turnover * cost

    # 删除缺失值
    portfolio_ret = portfolio_ret.dropna()

    return portfolio_ret


def calculate_performance(returns):
    """
    计算策略绩效指标

    根据每日收益率序列计算各项绩效指标

    Args:
        returns: Series, 每日收益率序列

    Returns:
        dict: 包含nav净值序列和metrics绩效指标的字典
            {
                "nav": [{"date": "2023-01-01", "value": 1.05}, ...],
                "metrics": {
                    "总收益率": "5.31%",
                    "年化收益率": "1.08%",
                    "年化波动率": "26.37%",
                    "夏普比率": -0.07,
                    "最大回撤": "-50.67%"
                }
            }
    """
    # 计算净值曲线
    nav = (1 + returns).cumprod()

    # 计算总收益率
    final_nav = nav.iloc[-1]
    total_return = (final_nav - 1) * 100

    # 计算年化收益率（假设252个交易日）
    trading_days = len(returns)
    years = trading_days / 252
    if years > 0:
        annual_return = (final_nav ** (1 / years) - 1) * 100
    else:
        annual_return = 0

    # 计算年化波动率
    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252) * 100

    # 计算夏普比率（假设无风险利率3%）
    risk_free_rate = 3
    if annual_vol != 0:
        sharpe = (annual_return - risk_free_rate) / annual_vol
    else:
        sharpe = 0

    # 计算最大回撤
    # 滚动最高净值
    rolling_max = nav.cummax()
    # 每日回撤 = 当前净值 / 历史最高 - 1
    drawdown = nav / rolling_max - 1
    max_drawdown = drawdown.min() * 100

    # 格式化净值序列为前端需要的格式
    nav_list = []
    for date, value in nav.items():
        # 处理日期格式
        if hasattr(date, 'date'):
            date_str = date.date().strftime("%Y-%m-%d")
        else:
            date_str = str(date)
        nav_list.append({
            "date": date_str,
            "value": float(value)
        })

    return {
        "nav": nav_list,
        "metrics": {
            "总收益率": f"{float(total_return):.2f}%",
            "年化收益率": f"{float(annual_return):.2f}%",
            "年化波动率": f"{float(annual_vol):.2f}%",
            "夏普比率": round(float(sharpe), 2),
            "最大回撤": f"{float(max_drawdown):.2f}%"
        }
    }