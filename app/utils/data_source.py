"""
数据源模块 - 永久使用 CSV，移除 MySQL 依赖
"""

import pandas as pd
from pathlib import Path

print("data_source.py")
def get_sample_data():
    """
    获取示例数据（CSV）
    从 seed-data/HS300_sample.csv 读取示例数据
    """
    from app.scripts.load_sample import load_sample_data
    return load_sample_data()


class DataSource:
    """数据源管理器 - 永远用 CSV"""

    _data_cache = None
    _source_cache = None

    def __init__(self, use_sample=False):
        # use_sample 参数保留但不再使用
        print("DataSource.__init__ 开始")
        self.use_sample = use_sample
        self._data = None
        self._source = None
        print("DataSource.__init__ 结束")

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
        print('csv is go')
        """永远从 CSV 加载数据"""
        if DataSource._data_cache is not None:
            self._data = DataSource._data_cache
            self._source = DataSource._source_cache
            return

        from app.scripts.load_sample import load_sample_data
        self._data = load_sample_data()
        self._source = "示例数据（CSV）"

        DataSource._data_cache = self._data
        DataSource._source_cache = self._source


class FullDataDataSource(DataSource):
    """完整数据源 - 也从 CSV 加载"""

    _full_data_cache = None
    _full_source_cache = None

    def _load(self):
        if FullDataDataSource._full_data_cache is not None:
            self._data = FullDataDataSource._full_data_cache
            self._source = FullDataDataSource._full_source_cache
            return

        from app.scripts.load_sample import load_sample_data
        self._data = load_sample_data()
        self._source = "示例数据（CSV）"

        FullDataDataSource._full_data_cache = self._data
        FullDataDataSource._full_source_cache = self._source
