# 📈 AlphaStock - A股动量选股系统

![版本](https://img.shields.io/badge/版本-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.13-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)
![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

一个基于 A股 动量因子的量化选股与回测系统。  
从沪深 300 成分股获取历史数据，通过动量因子筛选股票，并提供策略回测与可视化分析。

---

## ✨ 功能特性

- ✅ **数据自动获取**：使用 baostock + akshare 获取沪深300历史日线数据
- ✅ **动量选股**：按指定天数计算涨幅，实时选出排名靠前的股票
- ✅ **策略回测**：支持调整动量天数、选股数量、调仓频率、交易成本
- ✅ **绩效指标**：自动计算总收益率、年化收益率、夏普比率、最大回撤
- ✅ **可视化**：K线图展示个股走势，净值曲线对比策略表现
- ✅ **全栈分离**：FastAPI 后端 + Vue3 前端 + MySQL 数据库

---
## 🎬 演示视频

由于 GitHub 视频渲染不稳定，请直接下载或点击下方链接观看：

[📥 下载演示视频 (18MB)](./assets/demo-video.mp4)
<video src="https://github.com/LYF8533/AlphaStock_A/raw/main/assets/demo-video.mp4" controls width="800"></video>





## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue3 + Vite + ECharts | 交互式选股/回测界面 |
| 后端 | FastAPI + SQLAlchemy | RESTful API，自动文档 |
| 数据库 | MySQL 8.0 | 存储日线行情、股票信息 |
| 数据源 | baostock / akshare | 稳定获取A股数据 |

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- MySQL 8.0

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
3.  数据库初始化
    ```sql
    CREATE DATABASE stock_db;
    USE stock_db;

    CREATE TABLE stock_daily (
       id INT AUTO_INCREMENT PRIMARY KEY,
       code VARCHAR(10) NOT NULL,
       trade_date DATE NOT NULL,
       open DECIMAL(10,2),
       close DECIMAL(10,2),
       high DECIMAL(10,2),
       low DECIMAL(10,2),
       volume BIGINT,
       UNIQUE KEY uk_code_date (code, trade_date)
    );

    CREATE TABLE stock_info (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL
    );
4. 获取数据
    ```bash
   python app/scripts/fetch_csi300_all.py
5. 启动后端
    ```bash
   uvicorn main:app --reload
6. 前端设置
    ```bash
   cd frontend
   npm install
   npm run dev
7. ### 🌐 访问地址
- 前端：`http://localhost:5173`
- 后端 API 文档：`http://localhost:8000/docs`

## 📊 使用示例

### 动量选股
访问首页，调整“动量天数”和“选股数量”，点击查询即可看到涨幅榜和K线图。

### 策略回测
点击顶部“回测”按钮，设置参数后运行，可查看净值曲线和绩效指标。

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
├── main.py # FastAPI 后端入口
├── app/
│ └── scripts/ # 数据获取与回测脚本
│ ├── fetch_csi300_all.py
│ └── backtest_momentum.py
├── frontend/ # Vue3 前端
│ ├── src/
│ │ ├── components/
│ │ │ ├── SelectPage.vue
│ │ │ ├── Backtest.vue
│ │ │ └── StockChart.vue
│ │ └── App.vue
│ └── package.json
├── .env.example # 环境变量示例
├── .gitignore # Git 忽略文件
├── requirements.txt # Python 依赖
└── README.md # 项目说明
```
## 🔜 后续计划

- [ ] v1.1：加入更多因子（成交量、基本面）
- [ ] v1.2：实现参数扫描与自动优化
- [ ] v1.3：加入止损规则，控制最大回撤
- [ ] v2.0：样本外测试与滚动回测
- [ ] 部署上线

## 📝 开发日志

- **v1.0**（2026-03-03）：基础动量选股 + 回测可视化，完成全栈闭环

## 📄 许可证

[MIT](LICENSE)

## 👤 作者

- GitHub：[@LYF8533](https://github.com/LYF8533)

## ⭐ 支持

如果这个项目对你有帮助，欢迎点个 ⭐ 支持一下！

