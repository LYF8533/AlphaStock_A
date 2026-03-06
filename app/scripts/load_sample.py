"""
加载示例数据模块 - 带全局缓存，避免重复读文件
"""

import pandas as pd
from pathlib import Path

# 全局缓存，只在第一次加载时读文件
_SAMPLE_DATA_CACHE = None


def load_sample_data(force_reload=False):
    """
    加载示例数据（带缓存）

    Args:
        force_reload: 是否强制重新加载（默认False）

    Returns:
        DataFrame: 示例数据
    """
    global _SAMPLE_DATA_CACHE

    # 如果有缓存且不强制重载，直接返回
    if _SAMPLE_DATA_CACHE is not None and not force_reload:
        return _SAMPLE_DATA_CACHE

    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    csv_path = root_dir / 'seed-data' / 'HS300_sample.csv'

    if not csv_path.exists():
        raise FileNotFoundError(f"示例数据文件不存在: {csv_path}")

    print(f"首次加载数据文件: {csv_path}")

    # 读取 CSV
    df = pd.read_csv(csv_path)

    # 转换日期格式
    if 'trade_date' in df.columns:
        df['trade_date'] = pd.to_datetime(df['trade_date'])

    print(f"成功加载 {len(df)} 条记录")
    print(f"数据时间范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")
    print(f"包含股票: {df['code'].nunique()} 只")

    # 存入缓存
    _SAMPLE_DATA_CACHE = df
    return df


def clear_cache():
    """清空缓存（调试用）"""
    global _SAMPLE_DATA_CACHE
    _SAMPLE_DATA_CACHE = None
    print("示例数据缓存已清空")