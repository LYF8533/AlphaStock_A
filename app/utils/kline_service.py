import pandas as pd
from app.scripts.load_sample import load_sample_data


async def get_kline_data(code: str, limit: int, use_sample: bool = False):
    """
    获取K线数据（从 CSV）
    use_sample 参数保留但不再使用
    """
    # 从 CSV 加载数据
    df = load_sample_data()

    # 统一 code 格式（补零到6位）
    df['code'] = df['code'].astype(str).str.zfill(6)
    code = str(code).zfill(6)

    # 筛选股票，按日期倒序
    stock_df = df[df['code'] == code].sort_values('trade_date', ascending=False).head(limit)

    result = []
    for _, row in stock_df.iterrows():
        result.append({
            "trade_date": row['trade_date'].strftime("%Y-%m-%d"),
            "open": float(row['open']),
            "close": float(row['close']),
            "high": float(row['high']),
            "low": float(row['low']),
            "volume": int(row['volume'])
        })

    return {
        "code": code,
        "data": result,
        "data_source": "示例数据（CSV）",
        "count": len(result)
    }
