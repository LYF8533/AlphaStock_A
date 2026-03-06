from app.utils.backtest import prepare_pivot_data, momentum_backtest, calculate_performance


def run_backtest(df, lookback, top_n, rebalance_freq, cost):
    """运行回测（独立服务）"""
    pivot = prepare_pivot_data(df)
    returns = momentum_backtest(pivot, lookback, top_n, rebalance_freq, cost)
    result = calculate_performance(returns)
    return result
