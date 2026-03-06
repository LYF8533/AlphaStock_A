"""
数据处理工具 - 提供从DataFrame提取数据的通用函数
"""

import pandas as pd


def extract_kline_data(df, code, limit=60):
    """从DataFrame提取单只股票的K线数据"""
    # 把DataFrame中的code列转成字符串（补零到6位）
    df['code'] = df['code'].astype(str).str.zfill(6)

    # 确保传入的code也是字符串
    code = str(code).zfill(6)

    stock_df = df[df['code'] == code].sort_values('trade_date', ascending=False).head(limit)

    if stock_df.empty:
        print(f"没有找到股票 {code} 的数据")
        return []

    result = []
    for _, row in stock_df.iterrows():
        date_str = row['trade_date'].strftime("%Y-%m-%d") if hasattr(row['trade_date'], 'strftime') else str(
            row['trade_date'])
        result.append({
            "trade_date": date_str,
            "open": float(row['open']),
            "close": float(row['close']),
            "high": float(row['high']),
            "low": float(row['low']),
            "volume": int(row['volume'])
        })
    return result


def calculate_momentum_from_df(df, days, top_n):
    """
    从DataFrame计算动量选股结果

    对每只股票计算指定天数内的涨幅，返回涨幅最高的前top_n只

    Args:
        df: 包含股票数据的DataFrame（必须有code、trade_date、close字段）
        days: 动量计算天数（如20日涨幅）
        top_n: 返回前多少只股票

    Returns:
        list: 选股结果列表，每个元素格式：
            {
                "code": "000001",
                "name": "平安银行",
                "last_date": "2023-01-01",
                "last_close": 13.5,
                "past_date": "2022-12-12",
                "past_close": 12.0,
                "gain_20d": 12.5
            }
    """
    # 获取每只股票的最新交易日期
    latest_dates = df.groupby('code')['trade_date'].max().reset_index()
    latest_dates.columns = ['code', 'last_date']
    print(f"处理股票 {'code'}, 类型 {type('code')}")
    print(f"最新日期 {'last_date'}, 往前 {days} 天是 {'past_date'}")
    results = []
    for _, row in latest_dates.iterrows():
        code = row['code']
        last_date = row['last_date']

        # 获取该股票的所有数据，按日期排序
        stock_data = df[df['code'] == code].sort_values('trade_date')

        # 最新收盘价和名称
        latest = stock_data[stock_data['trade_date'] == last_date].iloc[0]
        last_close = latest['close']
        name = latest['name'] if 'name' in df.columns else ''

        # 计算 days 天前的日期，并找到最接近的交易日
        past_date = last_date - pd.Timedelta(days=days)
        past_data = stock_data[stock_data['trade_date'] <= past_date]

        past_row = past_data.iloc[-1]
        past_close = past_row['close']
        past_date_actual = past_row['trade_date']

        # 如果没有足够的历史数据，跳过该股票
        if past_data.empty:
            continue




        if (last_date - past_date_actual).days > days * 1.2:
            print(f"剔除 {code}: 实际间隔 {(last_date - past_date_actual).days} 天，理论 {days} 天")
            continue
        # 计算涨幅
        gain = (last_close - past_close) / past_close
        results.append({
            "code": code,
            "name": name,
            "last_date": last_date.strftime("%Y-%m-%d"),
            "last_close": round(last_close, 2),
            "past_date": past_date_actual.strftime("%Y-%m-%d"),
            "past_close": round(past_close, 2),
            f"gain_{days}d": round(gain * 100, 2)
        })

    # 按涨幅降序排序，返回前top_n只
    results.sort(key=lambda x: x[f"gain_{days}d"], reverse=True)
    return results[:top_n]