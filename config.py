from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DB_HOST: str = "mysql-10fed60c-project-manonghezuoshe.g.aivencloud.com"
    DB_PORT: int = 23966
    DB_USER: str = "avnadmin"
    DB_PASSWORD: str = ""  # 请填写实际密码
    DB_NAME: str = "defaultdb"
    
    # API配置
    API_TITLE: str = "股票数据查询API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "基于FastAPI的股票数据查询接口服务"

settings = Settings()