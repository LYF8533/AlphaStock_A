"""
示例数据加载模块 - 带全局缓存，避免重复读文件
"""

import pandas as pd
from pathlib import Path

# 全局缓存，只在第一次加载时读文件
_SAMPLE_DATA_CACHE = None

def load_sample_data(force_reload=False):
    """
    加载示例数据（带缓存）

    从 seed-data/HS300_full.csv 读取沪深300全量历史数据
    包含 300 只股票近 3 年日线行情，以及股票名称

    Args:
        force_reload: 是否强制重新加载（默认False）

    Returns:
        DataFrame: 包含以下字段的股票数据
            - code: 股票代码（字符串，6位）
            - name: 股票名称
            - trade_date: 交易日期
            - open: 开盘价
            - close: 收盘价
            - high: 最高价
            - low: 最低价
            - volume: 成交量
    """
    global _SAMPLE_DATA_CACHE

    # 如果有缓存且不强制重载，直接返回
    if _SAMPLE_DATA_CACHE is not None and not force_reload:
        print("使用缓存的示例数据")
        return _SAMPLE_DATA_CACHE

    # 获取项目根目录
    # current_file = Path(__file__).resolve()  # 当前文件绝对路径
    # root_dir = current_file.parent.parent.parent  # 项目根目录
    # csv_path = root_dir / 'seed-data' / 'HS300_full.csv'
    csv_path = Path("E:/fastApiProject/seed-data/HS300_full.csv")
    print(f"尝试读取文件: {csv_path}")

    if not csv_path.exists():
        raise FileNotFoundError(
            f"示例数据文件不存在: {csv_path}\n"
            f"请确保文件放在: {root_dir}/seed-data/HS300_full.csv"
        )

    print(f"首次加载数据文件: {csv_path}")

    # 读取 CSV
    df = pd.read_csv(csv_path)

    # 转换日期格式
    if 'trade_date' in df.columns:
        df['trade_date'] = pd.to_datetime(df['trade_date'])

    print(f"成功加载 {len(df)} 条记录")
    print(f"数据时间范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")
    print(f"包含股票: {df['code'].nunique()} 只")
    print(f"列名: {df.columns.tolist()}")

    # 存入缓存
    _SAMPLE_DATA_CACHE = df
    return df


def clear_cache():
    """
    清空示例数据缓存（调试用）

    调用后，下次 load_sample_data() 会重新读取文件
    """
    global _SAMPLE_DATA_CACHE
    _SAMPLE_DATA_CACHE = None
    print("示例数据缓存已清空")