# 功德健康游戏 🏃‍♂️📱

将Apple Watch健康数据转化为修行功德的游戏化系统，通过九个单项功德等级和十个总功德等级激励用户保持健康习惯。

## 🌟 核心特性

### 🏆 功德等级系统
- **单项功德九重境界**：每个健康数据类别分为9个等级（如跑步：初涉尘世 → 健步如飞 → ... → 咫尺天涯）
- **总功德十层天梯**：综合所有健康数据分为10个层级（凡夫俗子 → 初窥门径 → ... → 大罗金仙）
- **实时进度追踪**：显示距离下一等级还需多少功德

### 📊 健康数据支持
- **跑步距离**：每公里1000功德
- **步行步数**：每100步10功德  
- **站立时间**：每小时300功德
- **锻炼分钟**：每分钟50功德
- **心率达标**：每分钟5功德
- **睡眠时长**：每小时500功德
- **冥想时间**：每分钟100功德
- **爬楼层数**：每层200功德
- **游泳距离**：每100米800功德

### 🎮 游戏化激励
- **每日任务**：晨间修行、午间休憩、晚间冥想等
- **成就系统**：里程碑成就、连续成就、特殊成就
- **排行榜**：日榜、周榜、月榜、总榜、好友榜
- **修行流派**：武僧流、禅僧流、行僧流、全僧流（不同加成）

### 🌐 现代化Web界面
- **响应式设计**：适配桌面和移动设备
- **实时数据可视化**：图表展示功德分布和历史趋势
- **交互式仪表板**：实时更新功德、等级、进度
- **模拟数据生成**：一键生成测试数据
- **功德计算器**：实时计算输入数据的功德值

## 🏗️ 系统架构

```
merit-health-game/
├── core/                    # 核心逻辑
│   ├── merit_calculator.py  # 功德计算引擎
│   ├── merit_service.py     # 功德服务层
│   └── __init__.py
├── data/                    # 数据层
│   ├── models.py           # 数据模型
│   ├── database.py         # 数据库管理
│   └── __init__.py
├── api/                    # API层
│   ├── app.py             # FastAPI应用（纯API）
│   ├── app_web.py         # FastAPI应用（含Web界面）
│   └── __init__.py
├── web/                    # Web界面层
│   ├── static/            # 静态文件
│   │   ├── css/          # 样式表
│   │   └── js/           # JavaScript
│   └── templates/         # HTML模板
├── cli.py                  # 命令行工具
├── run.py                  # 应用启动器
├── requirements.txt        # 依赖包
└── README.md              # 本文档
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 使用命令行工具
```bash
# 查看帮助
python cli.py --help

# 注册用户
python cli.py user register --user-id user001 --nickname "张三"

# 提交健康数据
python cli.py health submit --user-id user001 --category running --value 5.2

# 查看用户资料
python cli.py user profile --user-id user001

# 查看排行榜
python cli.py leaderboard get --type total --limit 10

# 运行完整演示
python cli.py demo run
```

### 3. 启动完整Web应用（推荐）
```bash
# 启动完整应用（包含Web界面和API）
python run.py

# 或指定端口和主机
python run.py --host 0.0.0.0 --port 8080

# 启动但不自动打开浏览器
python run.py --no-browser

# 重置演示数据
python run.py --reset
```

启动后访问: http://localhost:8000

### 4. 启动纯API服务
```bash
# 启动FastAPI服务（仅API，无Web界面）
python -m api.app

# 访问API文档
# http://localhost:8000/docs
```

## 📱 iOS集成方案

### HealthKit数据采集
```swift
import HealthKit

class HealthDataCollector {
    let healthStore = HKHealthStore()
    
    func requestAuthorization() {
        let typesToRead: Set<HKObjectType> = [
            HKObjectType.quantityType(forIdentifier: .stepCount)!,
            HKObjectType.quantityType(forIdentifier: .distanceWalkingRunning)!,
            HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!,
            HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!,
            // ... 其他数据类型
        ]
        
        healthStore.requestAuthorization(toShare: nil, read: typesToRead) { success, error in
            if success {
                self.startCollectingData()
            }
        }
    }
    
    func collectDailyData(completion: @escaping ([String: Any]) -> Void) {
        var healthData: [String: Any] = [:]
        let group = DispatchGroup()
        
        // 收集步数
        group.enter()
        fetchSteps { steps in
            healthData["walking"] = steps
            group.leave()
        }
        
        // 收集跑步距离
        group.enter()
        fetchRunningDistance { distance in
            healthData["running"] = distance
            group.leave()
        }
        
        // 收集睡眠数据
        group.enter()
        fetchSleepData { sleepHours in
            healthData["sleep"] = sleepHours
            group.leave()
        }
        
        group.notify(queue: .main) {
            completion(healthData)
        }
    }
}
```

### API数据上传
```swift
struct MeritAPIClient {
    let baseURL = "http://localhost:8000"
    
    func uploadHealthData(userId: String, data: [String: Any], completion: @escaping (Bool) -> Void) {
        let url = URL(string: "\(baseURL)/api/health/dict")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "user_id": userId,
            "data": data
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            completion(false)
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let data = data,
               let result = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               result["success"] as? Bool == true {
                completion(true)
            } else {
                completion(false)
            }
        }.resume()
    }
}
```

## 🔧 开发指南

### 添加新的健康数据类别
1. 在 `core/merit_calculator.py` 的 `HealthCategory` 枚举中添加新类别
2. 在 `MERIT_RATES` 字典中设置功德转化率
3. 在 `CATEGORY_LEVELS` 中定义该类别的9个等级
4. 更新数据模型和API接口

### 自定义功德计算规则
修改 `core/merit_calculator.py` 中的 `MeritCalculator` 类：
```python
class MeritCalculator:
    # 修改功德转化率
    MERIT_RATES = {
        HealthCategory.RUNNING: 1500,  # 提高跑步功德
        HealthCategory.WALKING: 0.15,   # 提高步行功德
        # ... 其他类别
    }
    
    # 修改等级定义
    TOTAL_LEVELS = [
        (0, 50000, "凡人", 1),
        (50000, 200000, "修行者", 2),
        # ... 其他等级
    ]
```

### 扩展成就系统
在 `core/merit_service.py` 的 `_init_default_achievements` 方法中添加新成就：
```python
def _init_default_achievements(self):
    return {
        # ... 现有成就
        
        "custom_achievement": {
            "name": "自定义成就",
            "description": "达成特定条件",
            "requirement_type": "total_merit",  # 或 category_merit, daily_streak, daily_merit
            "requirement_value": 1000000,
            "reward_merit": 10000
        }
    }
```

## 📊 数据库设计

### 主要数据表
- **users**: 用户基本信息及各项功德累计
- **daily_records**: 每日健康数据及功德记录
- **achievements**: 成就定义
- **user_achievements**: 用户成就进度
- **merit_events**: 功德事件记录

### 数据关系
```sql
users (1) ──── (∞) daily_records
   └────────── (∞) user_achievements ──── (1) achievements
   └────────── (∞) merit_events
```

## 🎯 商业模式

### 免费功能
- 基础功德计算和等级系统
- 单项九重境界和总功德十层天梯
- 基础排行榜和成就系统

### 增值服务（示例）
- **功德Plus** (¥15/月): 详细健康分析、个性化修行计划
- **修行导师** (¥30/月): 一对一健康指导、定制修行流派
- **企业健康版**: 员工集体修行、团队健康管理

### 数据变现
- 匿名化健康数据分析报告
- 与保险公司合作（功德兑换保险优惠）
- 与运动品牌合作（功德兑换装备优惠）

## 🔒 隐私与安全

### 数据保护
1. **用户完全控制**: 明确告知收集哪些数据，用户可选择关闭
2. **匿名化处理**: 排行榜显示昵称，不泄露真实身份
3. **本地处理优先**: 敏感数据尽可能在设备端处理
4. **加密传输**: 所有数据传输使用HTTPS加密
5. **定期清理**: 超过一年的详细数据自动匿名化

### 健康安全
1. **安全提醒**: 避免过度运动提醒
2. **科学建议**: 基于医学研究的合理目标
3. **特殊情况处理**: 生病期间自动调整目标

## 📈 实施路线图

### 第一阶段：MVP (4-6周)
- [x] 功德计算核心引擎
- [x] 基础数据模型和数据库
- [x] RESTful API接口
- [ ] iOS原型应用（HealthKit集成）
- [ ] 基础Web管理后台

### 第二阶段：完整功能 (8-10周)
- [ ] 用户账户系统
- [ ] 完整的成就系统
- [ ] 社交分享功能
- [ ] 数据统计与分析
- [ ] Apple Watch独立应用

### 第三阶段：高级功能 (12-16周)
- [ ] AI个性化建议
- [ ] 修行流派系统
- [ ] 季节性活动
- [ ] 智能设备联动
- [ ] 企业健康管理版本

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系与支持

- 问题反馈: [GitHub Issues](https://github.com/yourusername/merit-health-game/issues)
- 功能建议: [GitHub Discussions](https://github.com/yourusername/merit-health-game/discussions)
- 商务合作: business@example.com

---

**让健康修行成为一种乐趣，让功德积累成为一种习惯！** 🎯

<p align="center">
  <img src="https://img.shields.io/badge/功德-健康游戏-blue" alt="功德健康游戏">
  <img src="https://img.shields.io/badge/版本-1.0.0-green" alt="版本">
  <img src="https://img.shields.io/badge/许可证-MIT-yellow" alt="许可证">
</p>