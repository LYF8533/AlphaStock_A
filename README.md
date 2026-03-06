# 📈 AlphaStock - A股动量选股系统

![版本](https://img.shields.io/badge/版本-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.13-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)
![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

一个基于 A股 动量因子的量化选股与回测系统。  
从沪深 300 成分股获取历史数据，通过动量因子筛选股票，并提供策略回测与可视化分析。

---

## 📦 版本说明

| 版本 | 数据源 | 特点 | 适用场景 |
|------|--------|------|----------|
| **v1.0.4** | CSV（推荐） | 无数据库、启动快、部署简单 | 个人研究、快速体验 |
| **v1.0.3** | MySQL | 支持实时更新、复杂查询 | 需要最新数据的用户 |

> 💡 默认使用 **v1.0.4（CSV 模式）**，无需安装 MySQL，clone 即可运行。

---

## ✨ 功能特性

- ✅ **数据自动获取**：使用 baostock + akshare 获取沪深300历史日线数据
- ✅ **动量选股**：按指定天数计算涨幅，实时选出排名靠前的股票
- ✅ **策略回测**：支持调整动量天数、选股数量、调仓频率、交易成本
- ✅ **绩效指标**：自动计算总收益率、年化收益率、夏普比率、最大回撤
- ✅ **可视化**：K线图展示个股走势，净值曲线对比策略表现
- ✅ **全栈分离**：FastAPI 后端 + Vue3 前端 + MySQL 数据库
- ✅ **无数据库依赖**：开箱即用，无需配置 MySQL
---
## 🎬 演示视频

由于 GitHub 视频渲染不稳定，请直接下载或点击下方链接观看：

[📥 下载演示视频 (18MB)](./assets/demo-video.mp4)
<video src="https://github.com/LYF8533/AlphaStock_A/raw/main/assets/demo-video.mp4" controls width="800"></video>





## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|:---:|:---:|:---|
| 前端 | Vue3 + Vite + ECharts | 交互式选股/回测界面，深色模式 |
| 后端 | FastAPI | RESTful API，自动文档 |
| 数据源 | CSV（内置） | 沪深 300 成分股近 3 年日线数据 |

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- MySQL 8.0(弃用)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/LYF8533/AlphaStock_A.git
   cd AlphaStock_A
   
2. **后端设置**
   ```bash
   # 创建虚拟环境
    python -m venv .venv

    # Windows 激活
    .venv\Scripts\activate

    # Mac/Linux 激活
    # source .venv/bin/activate

    # 安装依赖
    pip install -r requirements.txt

    # 配置环境变量
    cp .env.example .env
    # 编辑 .env 文件，修改数据库密码

3. 启动后端
    ```bash
   uvicorn main:app --reload
4. 前端设置
    ```bash
   cd frontend
   npm install
   npm run dev
5### 🌐 访问地址
- 前端：`http://localhost:5173`
- 后端 API 文档：`http://localhost:8000/docs`
## 🗄️ 如果想用 MySQL（v1.0.3）

切换到 v1.0.3 标签：

```bash
git checkout v1.0.3
```

## ⚡ 性能表现

| 指标 | v1.0.3（MySQL） | v1.0.4（CSV） | 提升 |
|------|-----------------|---------------|------|
| 首次启动时间 | ~6.8秒 | **~5.8秒** | 快 1 秒 |
| 选股接口耗时 | ~6.5秒 | **~0.1秒** | 快 65 倍 |
| K线接口耗时 | ~0.15秒 | **~0.1秒** | 基本持平 |
| 回测接口耗时 | ~8秒 | **~0.5秒** | 快 16 倍 |
| 依赖项 | MySQL + 5个库 | **纯 Python** | 无数据库依赖 |
| 部署复杂度 | ⭐⭐⭐⭐ | ⭐ | 开箱即用 |

> 💡 **为什么选股接口快了 65 倍？**  
> v1.0.3 每次请求都要查数据库，即使有索引也要 6 秒；  
> v1.0.4 数据全在内存里，查询只需 0.1 秒。

> 💡 **启动时间只快了 1 秒？**  
> 因为 CSV 文件有 20MB，pandas 读文件需要时间。  
> 但 **一旦加载完成，后续所有请求都是毫秒级**，而 MySQL 每次请求都要重新查。
> **同时，代码数量优化明显，整体基本优化50%，后续扩展性提高**
> 💡 **结论**：v1.0.4（CSV模式）在个人使用场景下，性能远超 MySQL 版本，且无需配置数据库，推荐默认使用。
## 📊 使用示例

### 动量选股
访问首页，调整“动量天数”和“选股数量”，点击查询即可看到涨幅榜和K线图。

### 策略回测
点击顶部“回测”按钮，设置参数后运行，可查看净值曲线和绩效指标。


### 深色模式
页面默认采用深色主题，所有组件均已适配

### 参数与结果示例

| 参数 | 值 |
|------|-----|
| 动量天数 | 365 |
| 选股数量 | 10 |
| 调仓频率 | 每月 |
| 交易成本 | 0.25% |

| 指标 | 结果 |
|------|------|
| 总收益率 | 30.82% |
| 年化收益率 | 5.75% |
| 最大回撤 | -36.55% |
| 夏普比率 | 0.10 |
## 🗺️ 项目结构
   ```AlphaStock_A/
├── main.py                 # FastAPI 后端入口
├── app/
│   ├── scripts/            # 数据获取脚本
│   │   ├── fetch_csi300_all.py    # 拉取全量数据（MySQL 版本用）
│   │   └── load_sample.py         # 加载示例 CSV
│   └── utils/               # 核心工具模块
│       ├── data_source.py   # 数据源管理（CSV/MySQL）
│       ├── data_tools.py    # 选股计算
│       ├── backtest.py      # 回测核心算法
│       ├── backtest_service.py # 回测业务逻辑
│       └── kline_service.py # K线数据服务
├── seed-data/               # 示例数据
│   └── HS300_sample.csv     # 沪深 300 近 3 年数据
├── frontend/                # Vue3 前端
└── README.md
```
## 🔜 后续计划

- [ ] v1.1：加入更多因子（成交量、基本面）
- [ ] v1.2：实现参数扫描与自动优化
- [ ] v1.3：加入止损规则，控制最大回撤
- [ ] v2.0：样本外测试与滚动回测
- [ ] 部署上线

## 📝 开发日志

- **v1.0.0**（2026-03-03）：基础动量选股 + 回测可视化，完成全栈闭环
- **v1.0.1**（2026-03-04）：添加示例数据降级机制，深色模式，优化前端体验
- **v1.0.2**（2026-03-05）：优化示例数据降级机制，完善数据源切换逻辑
- **v1.0.3**（2026-03-06）：性能优化 + 缓存独立，MySQL 版本最后迭代
- **v1.0.4**（2026-03-06）：永久切换至 CSV 模式，移除 MySQL 依赖，性能大幅提升
## 📄 许可证

[MIT](LICENSE)

## 👤 作者

- GitHub：[@LYF8533](https://github.com/LYF8533)

## ⭐ 支持

如果这个项目对你有帮助，欢迎点个 ⭐ 支持一下！

