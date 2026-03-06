import traceback
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.utils.data_source import DataSource, FullDataDataSource
from app.utils.data_tools import calculate_momentum_from_df
from app.utils.kline_service import get_kline_data
from app.utils.backtest_service import run_backtest

print("test")
load_dotenv()
app = FastAPI(title="A股动量选股 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 依赖项 ----------
def get_data_source(use_sample: bool = False):
    print("准备创建 DataSource 实例")
    ds = DataSource(use_sample)
    print("DataSource 实例创建完成")
    yield ds

def get_full_data_source(use_sample: bool = False):
    ds = FullDataDataSource(use_sample)
    try:
        yield ds
    finally:
        pass

# ---------- 根路径 ----------
@app.get("/")
def root():
    print("a股动量选股系统后端启动")
    return {"message": "A股动量选股系统后端运行中"}

# ---------- K线数据 ----------
@app.get("/stock/{code}")
async def get_stock_data(
        code: str,
        limit: int = Query(60),
        use_sample: bool = Query(False)
):
    try:
        result = await get_kline_data(code, limit, use_sample)
        return result
    except Exception as e:
        print(f"K线接口异常: {e}")
        traceback.print_exc()
        return {"code": code, "data": [], "error": str(e)}

# ---------- 选股 ----------
@app.get("/select/momentum")
async def select_momentum(
        top_n: int = Query(10),
        days: int = Query(20),
        use_sample: bool = Query(False),
        ds: DataSource = Depends(get_data_source)
):
    try:
        results = calculate_momentum_from_df(ds.data, days, top_n)
        return {"top": results, "data_source": ds.source, "count": len(results)}
    except Exception as e:
        print(f"选股接口异常: {e}")
        traceback.print_exc()
        return {"top": [], "error": str(e)}

# ---------- 数据库探测 ----------
@app.get("/check_db")
async def check_db():
    return {"db_available": False, "message": "使用 CSV 数据"}
# ---------- 回测 ----------
@app.get("/backtest")
async def backtest(
        lookback: int = Query(30),
        top_n: int = Query(20),
        rebalance_freq: str = Query("ME"),
        cost: float = Query(0.0025),
        use_sample: bool = Query(False),
        ds: DataSource = Depends(get_data_source)
):
    try:
        result = run_backtest(ds.data, lookback, top_n, rebalance_freq, cost)
        result["data_source"] = ds.source
        return result
    except Exception as e:
        print(f"回测接口异常: {e}")
        traceback.print_exc()
        return {"error": str(e)}

