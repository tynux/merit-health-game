# 🎮 功德健康游戏 (Merit Health Game)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/fastapi-0.104+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/github/last-commit/tynux/merit-health-game" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/tynux/merit-health-game" alt="Repo Size">
</p>

**将健康数据转化为修行功德的游戏化系统** - 通过有趣的"功德"概念激励用户保持健康习惯，支持Apple Watch/健康数据接入。

## ✨ 核心特性

### 🏆 **增强成就系统** (新!)
- **四大稀有度**: 普通(灰) → 稀有(蓝) → 史诗(紫) → 传奇(金)
- **六种成就类型**: 里程碑、挑战、隐藏、季节、社交、组合
- **功德加成机制**: 成就解锁提供1-25%永久功德加成
- **动态成就生成**: 基于用户历史生成个性化成就

### 📊 **功德计算引擎**
- **9大健康类别**: 跑步、步行、站立、锻炼、心率、睡眠、冥想、爬楼、游泳
- **实时功德加成**: 成就系统提供加成效果，实时计算显示
- **等级系统**: 单项九重境界 + 总功德十层天梯
- **进度追踪**: 距离下一等级所需功德实时显示

### 🎨 **现代化Web界面**
- **响应式设计**: 完美适配桌面、平板、手机
- **实时数据可视化**: Chart.js图表展示功德分布和历史趋势
- **交互式仪表板**: 实时更新功德、等级、成就进度
- **功德计算器**: 输入数据时实时显示加成后功德

### 🔧 **完整技术栈**
- **后端**: Python 3.11 + FastAPI + SQLite
- **前端**: HTML5 + CSS3 + JavaScript + Chart.js
- **认证**: JWT令牌 + 密码哈希 (python-jose + passlib)
- **工具**: 完整CLI命令行管理工具

## 🚀 快速开始

### 前置要求
- Python 3.8+
- pip (Python包管理器)
- Git

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/tynux/merit-health-game.git
cd merit-health-game

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python run.py

# 4. 访问应用
# Web界面: http://localhost:8000
# API文档: http://localhost:8000/api/docs
```

### Docker方式 (可选)
```bash
# 构建镜像
docker build -t merit-health-game .

# 运行容器
docker run -p 8000:8000 merit-health-game
```

## 📖 使用指南

### Web界面使用
1. **访问仪表板**: `http://localhost:8000/`
2. **查看成就**: 点击导航栏"成就殿堂"
3. **提交健康数据**: 在"提交数据"页面输入各项数据
4. **查看排行榜**: 查看总榜、日榜、周榜排名

### CLI命令行工具
```bash
# 查看帮助
python cli.py --help

# 用户管理
python cli.py user register --user-id demo_user --nickname "演示用户"
python cli.py user profile --user-id demo_user

# 健康数据提交
python cli.py health submit --user-id demo_user --category running --value 3.5
python cli.py health submit-dict --user-id demo_user --data '{"running": 3.5, "walking": 8500}'

# 查看成就和加成
python cli.py user achievements --user-id demo_user
python cli.py user boost --user-id demo_user

# 演示功能
python cli.py demo testdata --users 3 --days 5
python cli.py demo run
```

### API接口使用
```python
import requests

# 用户注册
response = requests.post("http://localhost:8000/api/users/register", json={
    "user_id": "test_user",
    "nickname": "测试用户"
})

# 提交健康数据
response = requests.post("http://localhost:8000/api/health/dict", json={
    "user_id": "test_user",
    "data": {
        "running": 5.2,      # 跑步5.2公里
        "walking": 12000,    # 步行12000步
        "sleep": 7.5,        # 睡眠7.5小时
        "exercise": 45       # 锻炼45分钟
    }
})

# 获取用户资料（包含成就和加成信息）
response = requests.get("http://localhost:8000/api/users/test_user/profile")
```

## 🏗️ 项目结构

```
merit-health-game/
├── api/                    # API服务层
│   ├── app.py             # RESTful API (纯API)
│   ├── app_web.py         # Web界面API (包含模板修复)
│   └── __init__.py
├── core/                   # 核心业务逻辑
│   ├── merit_calculator.py # 功德计算引擎
│   ├── merit_service.py    # 功德服务层（集成成就加成）
│   ├── achievement_enhancer.py # 成就增强系统（新增）
│   ├── auth.py            # 认证模块（新增）
│   └── __init__.py
├── data/                   # 数据层
│   ├── models.py          # 数据模型定义
│   ├── database.py        # 数据库管理
│   └── __init__.py
├── web/                    # 前端界面
│   ├── static/
│   │   ├── css/style.css  # 样式表（含成就稀有度样式）
│   │   └── js/app.js      # 前端逻辑（含加成计算）
│   └── templates/
│       └── index.html     # 主页面模板
├── cli.py                  # 命令行工具
├── run.py                  # 应用启动器
├── requirements.txt        # Python依赖包
├── LICENSE                 # MIT许可证
└── README.md              # 项目文档
```

## 🎯 成就系统详解

### 稀有度与加成效果
| 稀有度 | 颜色 | 图标 | 功德加成 | 描述 |
|--------|------|------|----------|------|
| **普通** | `#868e96` | 🥉 `fa-medal` | 1-5% | 基础成就，易于达成 |
| **稀有** | `#339af0` | 🏆 `fa-trophy` | 6-12% | 有一定难度，需要持续努力 |
| **史诗** | `#9c36b5` | 👑 `fa-crown` | 13-20% | 高难度挑战，代表卓越成就 |
| **传奇** | `#f59f00` | 💎 `fa-gem` | 21-25% | 顶级成就，需要非凡表现 |

### 成就类型徽章
- **里程碑** (`type-milestone`): 蓝色背景，累计类成就
- **挑战** (`type-challenge`): 橙色背景，难度挑战类
- **隐藏** (`type-hidden`): 灰色背景，秘密成就
- **社交** (`type-social`): 绿色背景，社交互动类
- **季节** (`type-seasonal`): 红色背景，限时成就
- **组合** (`type-combo`): 紫色背景，复合条件类

### 功德加成计算
```python
# 示例：用户有15%功德加成
基础功德 = 1000
加成后功德 = 基础功德 × (1 + 0.15) = 1150
加成功德 = 150

# 实时显示在功德计算器中
```

## 🔧 开发指南

### 环境设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8  # 开发工具
```

### 添加新的健康数据类别
1. 在 `core/merit_calculator.py` 的 `HealthCategory` 枚举中添加新类别
2. 在 `MERIT_RATES` 字典中设置功德转化率
3. 在 `CATEGORY_LEVELS` 中定义该类别的9个等级
4. 更新数据模型 (`data/models.py`) 和数据库 (`data/database.py`)

### 扩展成就系统
```python
# 在 core/achievement_enhancer.py 中添加新成就
def generate_dynamic_achievements(self, user_id: str) -> List[Dict]:
    """基于用户历史生成动态成就"""
    user_history = self.db.get_user_history(user_id)
    
    # 分析用户习惯，生成个性化成就
    if user_history.get("avg_running") > 5:
        return [{
            "name": "晨跑达人",
            "description": "连续7天晨跑超过5公里",
            "rarity": "rare",
            "type": "challenge",
            "boost_percentage": 8.0,
            "icon": "fa-sun",
            "color": "#ff922b"
        }]
```

### 数据库迁移
当前使用SQLite，可轻松迁移到PostgreSQL/MySQL：
```python
# 修改 database.py 中的连接字符串
# SQLite
db_path = "merit_health.db"

# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/merit_health"
```

## 📊 API文档

启动服务后访问 `http://localhost:8000/api/docs` 查看完整的Swagger UI文档。

### 主要API端点
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 系统健康检查 |
| `/api/users/register` | POST | 用户注册 |
| `/api/users/{user_id}/profile` | GET | 获取用户资料（含成就） |
| `/api/health/submit` | POST | 提交健康数据（对象格式） |
| `/api/health/dict` | POST | 提交健康数据（字典格式） |
| `/api/leaderboard/{type}` | GET | 获取排行榜 |
| `/api/reports/{period}` | GET | 获取统计报告 |

## 🧪 测试

```bash
# 运行单元测试
pytest tests/

# 测试API端点
python -m pytest tests/test_api.py

# 测试CLI工具
python -m pytest tests/test_cli.py
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！请按以下步骤操作：

1. **Fork 项目仓库**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 贡献规范
- 遵循现有的代码风格
- 添加适当的测试用例
- 更新相关文档
- 确保所有测试通过

### 开发流程
```bash
# 1. 同步主仓库
git remote add upstream https://github.com/tynux/merit-health-game.git
git fetch upstream

# 2. 创建开发分支
git checkout -b feature/new-achievement-system

# 3. 开发并测试
# ... 开发代码 ...
python -m pytest

# 4. 提交更改
git add .
git commit -m "feat: 添加新的成就系统"

# 5. 推送到您的fork
git push origin feature/new-achievement-system
```

## 🐛 问题反馈

如果您遇到问题或有功能建议：

1. **搜索现有问题**: 先查看 [Issues](https://github.com/tynux/merit-health-game/issues) 是否已存在
2. **创建新Issue**: 提供详细描述、复现步骤、预期行为等
3. **紧急问题**: 标明 `[紧急]` 前缀

## 📄 许可证

本项目采用 **MIT 许可证** - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **FastAPI** - 现代化的Python Web框架
- **Chart.js** - 简单灵活的JavaScript图表库
- **Font Awesome** - 精美的图标库
- **所有贡献者** - 感谢每一位为此项目做出贡献的人

## 📞 联系

- **GitHub Issues**: [问题反馈](https://github.com/tynux/merit-health-game/issues)
- **GitHub Discussions**: [功能讨论](https://github.com/tynux/merit-health-game/discussions)
- **项目主页**: [https://github.com/tynux/merit-health-game](https://github.com/tynux/merit-health-game)

---

<p align="center">
  <b>让健康修行成为一种乐趣，让功德积累成为一种习惯！</b> 🎯
</p>

<p align="center">
  <sub>如果这个项目对您有帮助，请给个 ⭐️ Star 支持！</sub>
</p>