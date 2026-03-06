"""
数据源模块 - 负责统一获取数据，支持自动降级到CSV
"""

import pandas as pd
from sqlalchemy import create_engine
import os


def get_db_engine():
    """
    创建数据库引擎连接

    从环境变量读取数据库配置，返回SQLAlchemy引擎对象
    用于后续的 pandas.read_sql 操作

    Returns:
        engine: SQLAlchemy 数据库引擎
    """
    print(f"DB_HOST: {os.getenv('DB_HOST')}")
    print(f"DB_USER: {os.getenv('DB_USER')}")
    print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
    print(f"DB_NAME: {os.getenv('DB_NAME')}")
    return create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )


def get_sample_data():
    """
    获取示例数据（CSV）

    从 seed-data/HS300_sample.csv 读取示例数据
    用于数据库不可用时的降级方案

    Returns:
        DataFrame: 包含股票日线数据的 DataFrame
    """
    from app.scripts.load_sample import load_sample_data
    return load_sample_data()


print("开始定义 DataSource 类")
class DataSource:
    """数据源管理器 - 带类级别缓存"""

    print("进入 DataSource 类体")
    _data_cache = None  # 类级别缓存，所有实例共享
    _source_cache = None

    def __init__(self, use_sample=False):
        print(f"DataSource.__init__, use_sample={use_sample}")
        self.use_sample = use_sample
        self._data = None
        self._source = None

    @property
    def data(self):
        if self._data is None:
            self._load()
        return self._data

    @property
    def source(self):
        if self._source is None:
            self._load()
        return self._source

    def _load(self):
        print("1. _load 开始")

        if DataSource._data_cache is not None:
            print("2. 使用缓存")
            self._data = DataSource._data_cache
            self._source = DataSource._source_cache
            return

        if self.use_sample:
            print("3. 使用示例数据")
            from app.scripts.load_sample import load_sample_data
            self._data = load_sample_data()
            self._source = "示例数据（用户强制）"
        else:
            try:
                print("4. 尝试连接数据库")
                engine = get_db_engine()
                print("5. 数据库引擎创建成功")

                query = """
                SELECT d.code, i.name, d.trade_date, d.close
                FROM stock_daily d
                LEFT JOIN stock_info i ON d.code = i.code
                ORDER BY d.code, d.trade_date
                """
                print("6. 开始执行 SQL")
                self._data = pd.read_sql(query, engine)
                print(f"7. SQL 执行成功，获取 {len(self._data)} 条数据")

                self._source = "全量数据库"
            except Exception as e:
                print(f"8. 数据库失败: {e}")
                from app.scripts.load_sample import load_sample_data
                self._data = load_sample_data()
                self._source = "示例数据（自动降级）"

        print("9. 存入缓存")
        DataSource._data_cache = self._data
        DataSource._source_cache = self._source
        print("10. _load 完成")

        # 存入类缓存
        DataSource._data_cache = self._data
        DataSource._source_cache = self._source


class FullDataDataSource(DataSource):
    """完整数据源 - 独立缓存"""

    _full_data_cache = None
    _full_source_cache = None

    def __init__(self, use_sample=False):
        super().__init__(use_sample)
        # 重设属性，不依赖父类缓存
        self._data = None
        self._source = None

    @property
    def data(self):
        if self._data is None:
            self._load_full()
        return self._data

    @property
    def source(self):
        if self._source is None:
            self._load_full()
        return self._source

    def _load_full(self):
        print("FullDataDataSource._load_full 开始")

        if FullDataDataSource._full_data_cache is not None:
            print("使用 FullDataDataSource 独立缓存")
            self._data = FullDataDataSource._full_data_cache
            self._source = FullDataDataSource._full_source_cache
            return

        if self.use_sample:
            from app.scripts.load_sample import load_sample_data
            self._data = load_sample_data()
            self._source = "示例数据（用户强制）"
        else:
            try:
                from app.utils.data_source import get_db_engine
                import pandas as pd
                engine = get_db_engine()
                query = """
                SELECT d.code, i.name, d.trade_date, 
                       d.open, d.close, d.high, d.low, d.volume
                FROM stock_daily d
                LEFT JOIN stock_info i ON d.code = i.code
                ORDER BY d.code, d.trade_date
                """
                self._data = pd.read_sql(query, engine)
                self._source = "全量数据库"
            except Exception as e:
                print(f"数据库连接失败，降级使用示例数据: {e}")
                from app.scripts.load_sample import load_sample_data
                self._data = load_sample_data()
                self._source = "示例数据（自动降级）"

        FullDataDataSource._full_data_cache = self._data
        FullDataDataSource._full_source_cache = self._source
        print("FullDataDataSource._load_full 完成")
