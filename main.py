"""
股票数据查询API - FastAPI主入口
兼容本地运行 + Vercel Serverless部署
"""
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware  # 新增这行
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings
import os
import sys

# 解决Vercel部署时的模块导入问题（确保能找到stock_data_query）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from stock_data_query import StockQuery

# ==================== 配置类（从环境变量读取，避免硬编码） ====================
class Settings(BaseSettings):
    # 数据库连接配置（Vercel部署时通过环境变量注入）
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", 0))
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "defaultdb")

    # API元信息
    API_TITLE: str = "股票数据查询API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = """
    基于FastAPI的股票数据查询接口服务，支持：
    1. 按行业/地域分页查询股票
    2. 按页码查询全量股票列表
    3. 通过股票代码/名称查询单只股票
    4. 获取单只股票最近7天日线数据
    5. 获取股票最新技术指标
    6. 获取Top3预测股票数据
    7. 获取当天股票预测数据
    """

# 初始化配置
settings = Settings()

# ==================== FastAPI应用初始化 ====================
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",  # Swagger文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# ==================== CORS 配置（新增部分）====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue 3 Vite 默认端口
        "http://localhost:3000",  # Create React App 默认端口
        "http://localhost:8080",  # Vue CLI 默认端口
        "*"  # 开发阶段允许所有，生产环境建议指定具体域名
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # 预检请求缓存时间（秒）
)

# ==================== 数据库连接初始化（容错处理） ====================
stock_query: Optional[StockQuery] = None
try:
    # 仅当所有数据库配置都存在时初始化
    if all([settings.DB_HOST, settings.DB_PORT, settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME]):
        stock_query = StockQuery(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        print("✅ 数据库连接初始化成功")
    else:
        print("⚠️  数据库配置不完整，跳过初始化（仅本地调试时生效）")
except Exception as e:
    print(f"❌ 数据库连接初始化失败: {str(e)}")
    stock_query = None

# ==================== 通用依赖校验（装饰器替代，简化代码） ====================
def check_db_connection():
    """检查数据库连接是否可用"""
    if not stock_query:
        raise HTTPException(
            status_code=500,
            detail="数据库连接未初始化，请检查环境变量配置或数据库服务状态"
        )

# ==================== 核心接口定义 ====================
@app.get("/", summary="健康检查", tags=["基础功能"])
def health_check():
    """API健康检查接口"""
    return {
        "status": "success",
        "message": "股票数据查询API运行正常",
        "api_docs": "/docs"
    }

# 新增：按页码查询全量股票列表
@app.get("/stocks/page/{page_num}", 
         response_model=List[Dict], 
         summary="按页码查询全量股票列表",
         tags=["股票列表查询"])
def get_stocks_by_page(
    page_num: int = Path(..., ge=1, description="页码，从1开始")
):
    """获取全量股票的第n页数据（每页20条）"""
    check_db_connection()
    try:
        return stock_query.get_stocks_by_page_number(page_num)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

# 新增：通过股票代码查询单只股票
@app.get("/stocks/symbol/{symbol}", 
         response_model=Optional[Dict], 
         summary="通过股票代码查询股票",
         tags=["单只股票数据"])
def get_stock_by_symbol(
    symbol: str = Path(..., description="股票代码，如：1")
):
    """通过股票代码查询单只股票详情"""
    check_db_connection()
    try:
        result = stock_query.get_stock_by_symbol(symbol)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到代码为{symbol}的股票")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

# 新增：通过股票名称查询单只股票
@app.get("/stocks/name/{name}", 
         response_model=Optional[Dict], 
         summary="通过股票名称查询股票",
         tags=["单只股票数据"])
def get_stock_by_name(
    name: str = Path(..., description="股票名称，如：平安银行")
):
    """通过股票名称查询单只股票详情"""
    check_db_connection()
    try:
        result = stock_query.get_stock_by_name(name)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到名称为{name}的股票")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/stocks/industry/{industry}/page/{page_num}", 
         response_model=List[Dict], 
         summary="按行业分页查询股票",
         tags=["股票列表查询"])
def get_stocks_by_industry(
    industry: str = Path(..., description="行业名称，如：科技、金融、医药"),
    page_num: int = Path(..., ge=1, description="页码，从1开始")
):
    """获取指定行业的第n页股票数据（每页20条）"""
    check_db_connection()
    try:
        return stock_query.get_stocks_by_page_and_industry(page_num, industry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/stocks/area/{area}/page/{page_num}", 
         response_model=List[Dict], 
         summary="按地域分页查询股票",
         tags=["股票列表查询"])
def get_stocks_by_area(
    area: str = Path(..., description="地域名称，如：北京、上海、广东"),
    page_num: int = Path(..., ge=1, description="页码，从1开始")
):
    """获取指定地域的第n页股票数据（每页20条）"""
    check_db_connection()
    try:
        return stock_query.get_stocks_by_page_and_area(page_num, area)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/stocks/{ts_code}/recent-7days", 
         response_model=List[Dict], 
         summary="获取股票最近7天日线数据",
         tags=["单只股票数据"])
def get_recent_7_days_data(
    ts_code: str = Path(..., description="股票唯一代码，如：000001.SZ、600000.SH")
):
    """获取指定股票最近7个交易日的日线数据（跳过周末）"""
    check_db_connection()
    try:
        result = stock_query.get_recent_7_days_data(ts_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到{ts_code}的最近7天数据")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/stocks/{ts_code}/technical-indicators/latest", 
         response_model=Optional[Dict], 
         summary="获取股票最新技术指标",
         tags=["单只股票数据"])
def get_latest_technical_indicators(
    ts_code: str = Path(..., description="股票唯一代码，如：000001.SZ")
):
    """获取指定股票最新的技术指标数据（MACD、RSI、KDJ等）"""
    check_db_connection()
    try:
        result = stock_query.get_latest_technical_indicators(ts_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到{ts_code}的技术指标数据")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/stocks/predictions/top3", 
         response_model=List[Dict], 
         summary="获取Top3预测股票数据",
         tags=["预测数据"])
def get_top3_stock_predictions():
    """获取ai_predictions_top3表中的三支股票预测数据（按ID升序）"""
    check_db_connection()
    try:
        result = stock_query.get_top3_predictions()
        if not result:
            raise HTTPException(status_code=404, detail="ai_predictions_top3表中未找到数据")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/stocks/{ts_code}/predictions/today", 
         response_model=List[Dict], 
         summary="获取股票当天预测数据",
         tags=["预测数据"])
def get_today_predictions(
    ts_code: str = Path(..., description="股票唯一代码，如：000001.SZ")
):
    """获取指定股票当天的预测数据（从ai_predictions表查询）"""
    check_db_connection()
    try:
        result = stock_query.get_today_predictions_by_ts_code(ts_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到{ts_code}当天的预测数据")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    
@app.get("/debug/env", summary="环境变量检查")
def debug_env():
    """检查 Vercel 环境变量"""
    import os
    
    # 安全地显示环境变量（隐藏密码）
    def safe_get(key):
        value = os.getenv(key, "NOT_SET")
        if "PASSWORD" in key or "SECRET" in key:
            return "***HIDDEN***" if value != "NOT_SET" else "NOT_SET"
        return value
    
    return {
        "vercel_env": {
            "VERCEL_REGION": os.getenv("VERCEL_REGION", "NOT_SET"),
            "VERCEL_ENV": os.getenv("VERCEL_ENV", "NOT_SET"),
            "VERCEL_URL": os.getenv("VERCEL_URL", "NOT_SET"),
        },
        "database_env": {
            "DB_HOST": safe_get("DB_HOST"),
            "DB_PORT": safe_get("DB_PORT"),
            "DB_USER": safe_get("DB_USER"),
            "DB_PASSWORD": safe_get("DB_PASSWORD"),
            "DB_NAME": safe_get("DB_NAME"),
        },
        "python_env": {
            "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "NOT_SET"),
            "PYTHONPATH": os.getenv("PYTHONPATH", "NOT_SET"),
        }
    }
@app.get("/debug/ip", summary="查看服务器IP")
def debug_ip():
    """查看 Vercel 服务器的实际 IP"""
    import socket
    import requests
    
    try:
        # 获取本机信息
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 获取外部看到的IP
        external_ip_response = requests.get("https://api.ipify.org?format=json", timeout=5)
        external_ip = external_ip_response.json()["ip"] if external_ip_response.ok else "unknown"
        
        # 获取 IP 地理位置（可选）
        location_response = requests.get(f"https://ipapi.co/{external_ip}/json/", timeout=5)
        location = location_response.json() if location_response.ok else {}
        
        return {
            "server_info": {
                "hostname": hostname,
                "local_ip": local_ip,
                "external_ip": external_ip,
                "vercel_region": os.getenv("VERCEL_REGION", "unknown"),
                "timestamp": datetime.now().isoformat()
            },
            "location": {
                "city": location.get("city"),
                "region": location.get("region"),
                "country": location.get("country_name"),
                "org": location.get("org"),
                "asn": location.get("asn")
            },
            "instructions": "请将此 IP 添加到 Aiven 的白名单中: " + external_ip
        }
    except Exception as e:
        return {"error": str(e)}
# ==================== 本地运行入口（Vercel部署时不会执行） ====================
if __name__ == "__main__":
    import uvicorn
    # 本地运行时优先加载.env文件（需安装python-dotenv）
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ 加载.env文件成功（本地调试）")
    except ImportError:
        pass

    # 本地运行配置
    uvicorn.run(
        app=__name__ + ":app",
        host="0.0.0.0",  # 允许外部访问
        port=8000,       # 本地端口
        reload=True      # 热重载（开发模式）
    )