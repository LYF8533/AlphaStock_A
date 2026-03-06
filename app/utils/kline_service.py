import pandas as pd
from app.utils.data_source import get_db_engine
from app.scripts.load_sample import load_sample_data


async def get_kline_data(code: str, limit: int, use_sample: bool):
    """获取K线数据（独立服务）"""
    if use_sample:
        df = load_sample_data()
        return extract_kline_from_df(df, code, limit, "示例数据")

    # 直接查数据库
    engine = get_db_engine()
    query = """
        SELECT trade_date, open, close, high, low, volume
        FROM stock_daily
        WHERE code = %s
        ORDER BY trade_date DESC
        LIMIT %s
    """
    df = pd.read_sql(query, engine, params=(code, limit))
    df['trade_date'] = pd.to_datetime(df['trade_date'])

    result = []
    for _, row in df.iterrows():
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
        "data_source": "全量数据库",
        "count": len(result)
    }


def extract_kline_from_df(df, code, limit, source):
    """从DataFrame提取K线数据"""
    df['code'] = df['code'].astype(str).str.zfill(6)
    code = str(code).zfill(6)

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
        "data_source": source,
        "count": len(result)
    }