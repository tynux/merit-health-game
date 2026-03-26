#!/usr/bin/env python3
"""
功德健康游戏API服务 + Web界面
基于FastAPI的完整应用，包含RESTful API和Web界面
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date, datetime
import uvicorn
import logging
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.merit_service import MeritService
from core.merit_calculator import HealthCategory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")

# 创建FastAPI应用
app = FastAPI(
    title="功德健康游戏",
    description="将Apple Watch健康数据转化为修行功德的游戏化系统",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=os.path.join(WEB_DIR, "static")), name="static")

# 设置模板
templates = Jinja2Templates(directory=os.path.join(WEB_DIR, "templates"))

# HTML文件读取辅助函数（临时修复模板问题）
def load_html_template(template_name="index.html", context=None):
    """直接加载HTML模板文件"""
    try:
        html_path = os.path.join(WEB_DIR, "templates", template_name)
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 简单的上下文变量替换（临时方案）
        if context and "active_section" in context:
            # 在body标签中添加active-section属性供前端JS使用
            html_content = html_content.replace('<body>', f'<body data-active-section="{context["active_section"]}">')
        
        return html_content
    except Exception as e:
        logger.error(f"Failed to load HTML template {template_name}: {e}")
        return f"<h1>功德健康游戏</h1><p>加载页面时出错: {str(e)}</p>"

# 全局服务实例
merit_service = None


def get_merit_service():
    """获取功德服务实例"""
    global merit_service
    if merit_service is None:
        merit_service = MeritService("merit_health.db")
    return merit_service


# ========== 数据模型 ==========

class UserRegister(BaseModel):
    """用户注册请求"""
    user_id: str = Field(..., description="用户ID")
    nickname: str = Field(..., description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像URL")


class HealthDataInput(BaseModel):
    """健康数据输入"""
    category: str = Field(..., description="健康数据类别")
    value: float = Field(..., description="数值")
    unit: str = Field(..., description="单位")
    timestamp: Optional[datetime] = Field(None, description="时间戳")


class BatchHealthData(BaseModel):
    """批量健康数据"""
    user_id: str = Field(..., description="用户ID")
    health_data: List[HealthDataInput] = Field(..., description="健康数据列表")


class HealthDataDict(BaseModel):
    """字典格式健康数据"""
    user_id: str = Field(..., description="用户ID")
    data: Dict[str, float] = Field(..., description="健康数据字典 {category: value}")


class LeaderboardQuery(BaseModel):
    """排行榜查询"""
    board_type: str = Field("total", description="排行榜类型: total, daily, weekly, monthly")
    limit: int = Field(100, description="返回数量", ge=1, le=1000)


class ReportQuery(BaseModel):
    """报告查询"""
    period: str = Field("weekly", description="报告周期: daily, weekly, monthly, yearly")


# ========== Web路由 ==========

@app.get("/", response_class=HTMLResponse)
async def web_home(request: Request):
    """Web首页"""
    html_content = load_html_template("index.html", {"active_section": "dashboard"})
    return HTMLResponse(content=html_content)


@app.get("/dashboard", response_class=HTMLResponse)
async def web_dashboard(request: Request):
    """仪表板页面"""
    html_content = load_html_template("index.html", {"active_section": "dashboard"})
    return HTMLResponse(content=html_content)


@app.get("/merit", response_class=HTMLResponse)
async def web_merit(request: Request):
    """功德记录页面"""
    html_content = load_html_template("index.html", {"active_section": "merit"})
    return HTMLResponse(content=html_content)


@app.get("/leaderboard", response_class=HTMLResponse)
async def web_leaderboard(request: Request):
    """排行榜页面"""
    html_content = load_html_template("index.html", {"active_section": "leaderboard"})
    return HTMLResponse(content=html_content)


@app.get("/submit", response_class=HTMLResponse)
async def web_submit(request: Request):
    """提交数据页面"""
    html_content = load_html_template("index.html", {"active_section": "submit"})
    return HTMLResponse(content=html_content)


@app.get("/achievements", response_class=HTMLResponse)
async def web_achievements(request: Request):
    """成就页面"""
    html_content = load_html_template("index.html", {"active_section": "achievements"})
    return HTMLResponse(content=html_content)


# ========== API路由 ==========

@app.get("/api/")
async def api_root():
    """API根路径"""
    return {
        "service": "功德健康游戏API",
        "version": "1.0.0",
        "status": "运行中",
        "web_interface": "/",
        "api_docs": "/api/docs",
        "endpoints": {
            "用户管理": {
                "注册用户": "POST /api/users/register",
                "获取资料": "GET /api/users/{user_id}/profile",
                "获取报告": "GET /api/users/{user_id}/report"
            },
            "健康数据处理": {
                "提交数据": "POST /api/health/submit",
                "批量提交": "POST /api/health/batch",
                "字典提交": "POST /api/health/dict"
            },
            "排行榜": {
                "获取排行榜": "GET /api/leaderboard",
                "获取用户排名": "GET /api/users/{user_id}/rank"
            },
            "系统状态": {
                "健康检查": "GET /api/health",
                "系统信息": "GET /api/system/info"
            }
        }
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/system/info")
async def system_info(service: MeritService = Depends(get_merit_service)):
    """系统信息"""
    return {
        "service": "功德健康游戏",
        "version": "1.0.0",
        "database": "SQLite",
        "status": "运行中",
        "web_interface": True,
        "timestamp": datetime.now().isoformat()
    }


# ========== 用户管理API ==========

@app.post("/api/users/register")
async def register_user(
    user_data: UserRegister,
    service: MeritService = Depends(get_merit_service)
):
    """
    注册新用户
    
    - **user_id**: 用户ID
    - **nickname**: 昵称
    - **avatar_url**: 头像URL (可选)
    """
    success = service.register_user(
        user_data.user_id,
        user_data.nickname,
        user_data.avatar_url
    )
    
    if success:
        return {
            "success": True,
            "message": "用户注册成功",
            "user_id": user_data.user_id,
            "nickname": user_data.nickname
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="用户注册失败，用户ID可能已存在"
        )


@app.get("/api/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    service: MeritService = Depends(get_merit_service)
):
    """
    获取用户完整资料
    
    - **user_id**: 用户ID
    """
    profile = service.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"用户不存在: {user_id}"
        )
    
    return {
        "success": True,
        "data": profile
    }


@app.get("/api/users/{user_id}/report")
async def get_user_report(
    user_id: str,
    period: str = Query("weekly", description="报告周期: daily, weekly, monthly, yearly"),
    service: MeritService = Depends(get_merit_service)
):
    """
    获取用户统计报告
    
    - **user_id**: 用户ID
    - **period**: 报告周期
    """
    report = service.get_user_report(user_id, period)
    
    if not report.get("profile_summary"):
        raise HTTPException(
            status_code=404,
            detail=f"用户不存在或没有数据: {user_id}"
        )
    
    return {
        "success": True,
        "period": period,
        "data": report
    }


# ========== 健康数据处理API ==========

@app.post("/api/health/submit")
async def submit_health_data(
    data: BatchHealthData,
    service: MeritService = Depends(get_merit_service)
):
    """
    提交健康数据
    
    - **user_id**: 用户ID
    - **health_data**: 健康数据列表
    """
    from ..core.merit_calculator import HealthData
    
    # 转换为HealthData对象
    health_data_list = []
    
    for item in data.health_data:
        try:
            category = HealthCategory(item.category)
            health_data = HealthData(
                category=category,
                value=item.value,
                unit=item.unit,
                timestamp=item.timestamp or datetime.now()
            )
            health_data_list.append(health_data)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的健康数据类别: {item.category}"
            )
    
    # 处理数据
    result = service.process_health_data(data.user_id, health_data_list)
    
    return {
        "success": result["success"],
        "data": result
    }


@app.post("/api/health/batch")
async def batch_submit_health_data(
    data: Dict[str, Any] = Body(...),
    service: MeritService = Depends(get_merit_service)
):
    """
    批量提交健康数据（简化版）
    
    请求体格式:
    ```json
    {
        "user_id": "user_001",
        "data": [
            {"category": "running", "value": 5.2},
            {"category": "walking", "value": 12500},
            {"category": "sleep", "value": 7.8}
        ]
    }
    ```
    """
    user_id = data.get("user_id")
    data_list = data.get("data", [])
    
    if not user_id:
        raise HTTPException(status_code=400, detail="缺少user_id")
    
    if not isinstance(data_list, list):
        raise HTTPException(status_code=400, detail="data必须是列表")
    
    # 构建健康数据字典
    health_data_dict = {}
    for item in data_list:
        if isinstance(item, dict) and "category" in item and "value" in item:
            health_data_dict[item["category"]] = item["value"]
    
    # 处理数据
    result = service.process_health_data_dict(user_id, health_data_dict)
    
    return {
        "success": result["success"],
        "data": result
    }


@app.post("/api/health/dict")
async def dict_submit_health_data(
    data: HealthDataDict,
    service: MeritService = Depends(get_merit_service)
):
    """
    使用字典格式提交健康数据
    
    - **user_id**: 用户ID
    - **data**: 健康数据字典 {category: value}
    """
    result = service.process_health_data_dict(data.user_id, data.data)
    
    return {
        "success": result["success"],
        "data": result
    }


# ========== 排行榜API ==========

@app.get("/api/leaderboard")
async def get_leaderboard(
    board_type: str = Query("total", description="排行榜类型: total, daily, weekly, monthly"),
    limit: int = Query(100, description="返回数量", ge=1, le=1000),
    service: MeritService = Depends(get_merit_service)
):
    """
    获取排行榜
    
    - **board_type**: 排行榜类型
    - **limit**: 返回数量
    """
    leaderboard = service.get_leaderboard(board_type, limit)
    
    return {
        "success": True,
        "board_type": board_type,
        "limit": limit,
        "count": len(leaderboard),
        "data": leaderboard
    }


@app.get("/api/users/{user_id}/rank")
async def get_user_rank(
    user_id: str,
    board_type: str = Query("total", description="排行榜类型: total, daily, weekly, monthly"),
    service: MeritService = Depends(get_merit_service)
):
    """
    获取用户排名
    
    - **user_id**: 用户ID
    - **board_type**: 排行榜类型
    """
    rank_info = service.get_user_rank(user_id, board_type)
    
    if not rank_info:
        raise HTTPException(
            status_code=404,
            detail=f"用户不存在或未上榜: {user_id}"
        )
    
    return {
        "success": True,
        "board_type": board_type,
        "data": rank_info
    }


# ========== 健康数据类别API ==========

@app.get("/api/categories")
async def get_categories():
    """获取所有健康数据类别"""
    categories = []
    
    for category in HealthCategory:
        categories.append({
            "name": category.value,
            "chinese_name": _get_category_chinese_name(category),
            "description": _get_category_description(category),
            "unit": _get_category_unit(category),
            "merit_rate": _get_category_merit_rate(category)
        })
    
    return {
        "success": True,
        "count": len(categories),
        "data": categories
    }


def _get_category_chinese_name(category: HealthCategory) -> str:
    """获取类别中文名"""
    mapping = {
        HealthCategory.RUNNING: "跑步",
        HealthCategory.WALKING: "步行",
        HealthCategory.STANDING: "站立",
        HealthCategory.EXERCISE: "锻炼",
        HealthCategory.HEART_RATE: "心率",
        HealthCategory.SLEEP: "睡眠",
        HealthCategory.MEDITATION: "冥想",
        HealthCategory.STAIRS: "爬楼",
        HealthCategory.SWIMMING: "游泳",
    }
    return mapping.get(category, category.value)


def _get_category_description(category: HealthCategory) -> str:
    """获取类别描述"""
    mapping = {
        HealthCategory.RUNNING: "跑步距离，每公里1000功德",
        HealthCategory.WALKING: "步行步数，每100步10功德",
        HealthCategory.STANDING: "站立时间，每小时300功德",
        HealthCategory.EXERCISE: "锻炼分钟，每分钟50功德",
        HealthCategory.HEART_RATE: "心率达标时间，每分钟5功德",
        HealthCategory.SLEEP: "睡眠时长，每小时500功德",
        HealthCategory.MEDITATION: "冥想时间，每分钟100功德",
        HealthCategory.STAIRS: "爬楼层数，每层200功德",
        HealthCategory.SWIMMING: "游泳距离，每100米800功德",
    }
    return mapping.get(category, "")


def _get_category_unit(category: HealthCategory) -> str:
    """获取类别单位"""
    mapping = {
        HealthCategory.RUNNING: "公里",
        HealthCategory.WALKING: "步",
        HealthCategory.STANDING: "小时",
        HealthCategory.EXERCISE: "分钟",
        HealthCategory.HEART_RATE: "分钟",
        HealthCategory.SLEEP: "小时",
        HealthCategory.MEDITATION: "分钟",
        HealthCategory.STAIRS: "层",
        HealthCategory.SWIMMING: "米",
    }
    return mapping.get(category, "")


def _get_category_merit_rate(category: HealthCategory) -> float:
    """获取类别功德转化率"""
    from ..core.merit_calculator import MeritCalculator
    calculator = MeritCalculator()
    return calculator.MERIT_RATES.get(category, 0)


# ========== 演示数据API ==========

@app.post("/api/demo/reset")
async def reset_demo_data(service: MeritService = Depends(get_merit_service)):
    """重置演示数据"""
    import os
    db_path = "merit_health.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
        service.close()
        global merit_service
        merit_service = MeritService(db_path)
        
        # 创建演示用户
        service.register_user("demo_user", "修行者", "https://example.com/avatar.jpg")
        
        return {
            "success": True,
            "message": "演示数据已重置"
        }
    
    return {
        "success": False,
        "message": "数据库文件不存在"
    }


@app.post("/api/demo/simulate/{days}")
async def simulate_demo_data(
    days: int = 7,
    service: MeritService = Depends(get_merit_service)
):
    """模拟多天数据"""
    import random
    from datetime import date, timedelta
    
    user_id = "demo_user"
    
    # 确保用户存在
    try:
        service.register_user(user_id, "修行者", "https://example.com/avatar.jpg")
    except:
        pass  # 用户可能已存在
    
    # 模拟多天数据
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    current_date = start_date
    total_merit = 0
    
    while current_date <= end_date:
        # 每天有70%的概率有数据
        if random.random() < 0.7:
            # 随机生成健康数据
            health_data = {}
            
            # 步数: 2000-15000
            if random.random() < 0.8:
                health_data["walking"] = random.randint(2000, 15000)
            
            # 跑步: 0-10公里
            if random.random() < 0.4:
                health_data["running"] = round(random.uniform(0.5, 10.0), 1)
            
            # 睡眠: 4-9小时
            if random.random() < 0.9:
                health_data["sleep"] = round(random.uniform(4.0, 9.0), 1)
            
            # 锻炼: 0-90分钟
            if random.random() < 0.3:
                health_data["exercise"] = random.randint(10, 90)
            
            # 提交数据
            if health_data:
                result = service.process_health_data_dict(user_id, health_data)
                if result["success"]:
                    total_merit += result["data"]["total_merit_earned"]
        
        current_date += timedelta(days=1)
    
    return {
        "success": True,
        "days_simulated": days,
        "total_merit_generated": total_merit,
        "message": f"成功模拟{days}天数据，生成{total_merit}功德"
    }


# ========== 启动函数 ==========

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """启动服务器"""
    print(f"""
    ========================================
      功德健康游戏 - 完整应用
      版本: 1.0.0
      
      Web界面: http://{host}:{port}
      API文档: http://{host}:{port}/api/docs
      
      演示用户: demo_user
      数据库: merit_health.db
      
      功能:
      - ✅ 功德计算引擎
      - ✅ 数据库存储
      - ✅ RESTful API
      - ✅ 现代Web界面
      - ✅ 排行榜系统
      - ✅ 成就系统
    ========================================
    """)
    
    uvicorn.run(
        "api.app_web:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()