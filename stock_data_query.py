"""股票查询器"""
from typing import List, Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class StockQuery:
    """股票查询器"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """初始化数据库连接"""
        self.connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.connection_url)

    def get_stocks_by_page_number(self, n: int, check_total: bool = True) -> List[Dict]:
        """获取第n页的股票数据（每页20条）"""
        if n < 1:
            raise ValueError("页码n必须大于等于1")
    
        if check_total:
            total_pages = self.get_total_pages()
            if n > total_pages:
                raise ValueError(f"页码{n}超过最大页数{total_pages}")
    
        offset = 20 * (n - 1)
        limit = 20
    
        query = text("""
            SELECT id, ts_code, symbol, name, area, industry, list_date
            FROM stocks
            ORDER BY id ASC
            LIMIT :limit OFFSET :offset
        """)
    
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit, "offset": offset})
                rows = result.fetchall()
            
                if not rows and n > 1 and check_total:
                    actual_total = self.get_total_records()
                    if actual_total <= offset:
                        raise ValueError(f"页码{n}超出数据范围，总记录数仅{actual_total}条")
            
                return [dict(row._mapping) for row in rows]
                
        except SQLAlchemyError as e:
            raise Exception(f"数据库查询错误: {str(e)}")

    def get_total_records(self) -> int:
        """获取总记录数"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) as total FROM stocks"))
                return result.fetchone().total
        except SQLAlchemyError as e:
            raise Exception(f"查询总记录数错误: {str(e)}")

    def get_total_pages(self) -> int:
        """获取总页数"""
        total_count = self.get_total_records()
        return (total_count + 20 - 1) // 20 if total_count > 0 else 0

    def get_stock_by_symbol(self, symbol: str) -> Optional[Dict]:
        """通过股票代码查询股票"""
        if not symbol:
            raise ValueError("股票代码不能为空")
            
        query = text("""
            SELECT id, ts_code, symbol, name, area, industry, list_date
            FROM stocks
            WHERE symbol = :symbol
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"symbol": symbol})
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_stock_by_name(self, name: str) -> Optional[Dict]:
        """通过股票名称查询股票"""
        if not name:
            raise ValueError("股票名称不能为空")
            
        query = text("""
            SELECT id, ts_code, symbol, name, area, industry, list_date
            FROM stocks
            WHERE name = :name
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"name": name})
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_stocks_by_page_and_area(self, n: int, area: str) -> List[Dict]:
        """获取指定地域的第n页股票数据"""
        if n < 1:
            raise ValueError("页码n必须大于等于1")
        if not area:
            raise ValueError("地域参数不能为空")
        
        area_total = self.get_area_total_records(area)
        if area_total == 0:
            return []
            
        total_pages = self.get_area_total_pages(area)
        if n > total_pages:
            raise ValueError(f"页码{n}超过最大页数{total_pages}")
        
        offset = 20 * (n - 1)
        limit = 20 if n < total_pages else (area_total - offset)
        
        query = text("""
            SELECT id, ts_code, symbol, name, area, industry, list_date
            FROM stocks
            WHERE area = :area
            ORDER BY id ASC
            LIMIT :limit OFFSET :offset
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"area": area, "limit": limit, "offset": offset})
                return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_area_total_records(self, area: str) -> int:
        """获取指定地域的总记录数"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) as total FROM stocks WHERE area = :area"),
                    {"area": area}
                )
                return result.fetchone().total
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_area_total_pages(self, area: str) -> int:
        """获取指定地域的总页数"""
        total = self.get_area_total_records(area)
        return (total + 20 - 1) // 20 if total > 0 else 0

    def get_stocks_by_page_and_industry(self, n: int, industry: str) -> List[Dict]:
        """获取指定行业的第n页股票数据"""
        if n < 1:
            raise ValueError("页码n必须大于等于1")
        if not industry:
            raise ValueError("行业参数不能为空")
        
        total = self.get_industry_total_records(industry)
        if total == 0:
            return []
            
        total_pages = self.get_industry_total_pages(industry)
        if n > total_pages:
            raise ValueError(f"页码{n}超过最大页数{total_pages}")
        
        offset = 20 * (n - 1)
        limit = 20 if n < total_pages else (total - offset)
        
        query = text("""
            SELECT id, ts_code, symbol, name, area, industry, list_date
            FROM stocks
            WHERE industry = :industry
            ORDER BY id ASC
            LIMIT :limit OFFSET :offset
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"industry": industry, "limit": limit, "offset": offset})
                return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_industry_total_records(self, industry: str) -> int:
        """获取指定行业的总记录数"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) as total FROM stocks WHERE industry = :industry"),
                    {"industry": industry}
                )
                return result.fetchone().total
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_industry_total_pages(self, industry: str) -> int:
        """获取指定行业的总页数"""
        total = self.get_industry_total_records(industry)
        return (total + 20 - 1) // 20 if total > 0 else 0

    def get_recent_7_days_data(self, ts_code: str) -> List[Dict]:
        """获取最近7个交易日的日线数据（跳过周末）"""
        if not ts_code:
            raise ValueError("股票唯一代码不能为空")
            
        query = text("""
            SELECT * FROM stock_daily_data
            WHERE ts_code = :ts_code
              AND trade_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
              AND WEEKDAY(trade_date) < 5
            ORDER BY trade_date DESC
            LIMIT 7
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"ts_code": ts_code})
                return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_latest_technical_indicators(self, ts_code: str) -> Optional[Dict]:
        """获取最新的技术指标"""
        if not ts_code:
            raise ValueError("股票唯一代码不能为空")
            
        query = text("""
            SELECT * FROM stock_technical_indicators_clean
            WHERE ts_code = :ts_code
            ORDER BY id DESC
            LIMIT 1
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"ts_code": ts_code})
                row = result.fetchone()
                return dict(row._mapping) if row else None
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")

    def get_today_predictions_by_ts_code(self, ts_code: str) -> List[Dict]:
        """获取当天的预测数据（修正为ai_predictions表）"""
        if not ts_code:
            raise ValueError("股票唯一代码不能为空")
            
        # ✅ 正确表名：ai_predictions
        query = text("""
            SELECT * FROM ai_predictions
            WHERE ts_code = :ts_code AND predict_date = CURDATE()
            ORDER BY id DESC
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"ts_code": ts_code})
                return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")
    def get_top3_predictions(self) -> List[Dict]:
        """获取ai_predictions_top3表中的所有三支股票预测数据"""
        query = text("""
            SELECT id, ts_code, predict_date, for_date, prediction_score
            FROM ai_predictions_top3
            ORDER BY id ASC
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise Exception(f"查询ai_predictions_top3错误: {str(e)}")