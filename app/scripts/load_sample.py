import pandas as pd
import os
from pathlib import Path


def load_sample_data(return_df=True):
    """
    加载示例数据到内存（快速测试用）
    参数:
        return_df: 是否返回 DataFrame（始终为 True，保留参数是为了向后兼容）
    返回:
        pandas.DataFrame: 包含示例数据的 DataFrame
    """
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    csv_path = root_dir / 'seed-data' / 'HS300_sample.csv'

    if not csv_path.exists():
        raise FileNotFoundError(
            f"示例数据文件不存在: {csv_path}\n"
            f"请确保文件放在 seed-data/HS300_sample.csv"
        )

    print(f"正在加载数据文件: {csv_path}")

    # 读取 CSV
    df = pd.read_csv(csv_path)

    # 转换日期格式
    if 'trade_date' in df.columns:
        df['trade_date'] = pd.to_datetime(df['trade_date'])

    print(f"成功加载 {len(df)} 条记录")
    print(f"数据时间范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")
    print(f"包含股票: {df['code'].nunique()} 只")

    return df


if __name__ == '__main__':
    # 测试：加载到内存
    data = load_sample_data()
    print("\n前5行数据预览：")
    print(data.head())
    print("\n数据统计信息：")
    print(data.describe())