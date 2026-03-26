#!/usr/bin/env python3
"""
功德计算核心引擎
将Apple Watch健康数据转化为修行功德
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, date


class HealthCategory(Enum):
    """健康数据类型枚举"""
    RUNNING = "running"        # 跑步
    WALKING = "walking"        # 步行
    STANDING = "standing"      # 站立
    EXERCISE = "exercise"      # 锻炼
    HEART_RATE = "heart_rate"  # 心率
    SLEEP = "sleep"            # 睡眠
    MEDITATION = "meditation"  # 冥想
    STAIRS = "stairs"          # 爬楼
    SWIMMING = "swimming"      # 游泳


@dataclass
class HealthData:
    """健康数据输入"""
    category: HealthCategory
    value: float  # 原始数值
    unit: str     # 单位
    timestamp: datetime
    
    @classmethod
    def create_running(cls, distance_km: float, timestamp: datetime = None):
        """创建跑步数据"""
        return cls(
            category=HealthCategory.RUNNING,
            value=distance_km,
            unit="km",
            timestamp=timestamp or datetime.now()
        )
    
    @classmethod
    def create_walking(cls, steps: int, timestamp: datetime = None):
        """创建步行数据"""
        return cls(
            category=HealthCategory.WALKING,
            value=float(steps),
            unit="steps",
            timestamp=timestamp or datetime.now()
        )
    
    @classmethod
    def create_sleep(cls, hours: float, timestamp: datetime = None):
        """创建睡眠数据"""
        return cls(
            category=HealthCategory.SLEEP,
            value=hours,
            unit="hours",
            timestamp=timestamp or datetime.now()
        )
    
    @classmethod
    def create_exercise(cls, minutes: int, timestamp: datetime = None):
        """创建锻炼数据"""
        return cls(
            category=HealthCategory.EXERCISE,
            value=float(minutes),
            unit="minutes",
            timestamp=timestamp or datetime.now()
        )
    
    @classmethod
    def create_standing(cls, hours: float, timestamp: datetime = None):
        """创建站立数据"""
        return cls(
            category=HealthCategory.STANDING,
            value=hours,
            unit="hours",
            timestamp=timestamp or datetime.now()
        )


@dataclass
class MeritResult:
    """功德计算结果"""
    category: HealthCategory
    raw_value: float
    merit_points: int
    level_name: str
    level_number: int
    progress: float  # 当前等级进度 0.0-1.0
    next_level_merit: int  # 下一等级所需功德


class MeritCalculator:
    """功德计算器"""
    
    # 功德转化率 (每单位原始数据获得的功德)
    MERIT_RATES = {
        HealthCategory.RUNNING: 1000,    # 每公里1000功德
        HealthCategory.WALKING: 0.1,     # 每步0.1功德 (每100步10功德)
        HealthCategory.STANDING: 300,    # 每小时300功德
        HealthCategory.EXERCISE: 50,     # 每分钟50功德
        HealthCategory.HEART_RATE: 5,    # 每分钟达标心率5功德
        HealthCategory.SLEEP: 500,       # 每小时500功德
        HealthCategory.MEDITATION: 100,  # 每分钟100功德
        HealthCategory.STAIRS: 200,      # 每层200功德
        HealthCategory.SWIMMING: 8,      # 每米8功德 (每100米800功德)
    }
    
    # 单项功德九重境界 (每个类别的9个等级)
    CATEGORY_LEVELS = {
        HealthCategory.RUNNING: [
            (0, 50000, "初涉尘世", 1),
            (50000, 200000, "健步如飞", 2),
            (200000, 500000, "日行百里", 3),
            (500000, 1000000, "踏雪无痕", 4),
            (1000000, 2000000, "凌波微步", 5),
            (2000000, 5000000, "缩地成寸", 6),
            (5000000, 10000000, "御风而行", 7),
            (10000000, 20000000, "八步赶蝉", 8),
            (20000000, float('inf'), "咫尺天涯", 9),
        ],
        HealthCategory.WALKING: [
            (0, 10000, "步履蹒跚", 1),
            (10000, 50000, "闲庭信步", 2),
            (50000, 200000, "稳步前行", 3),
            (200000, 500000, "疾步如风", 4),
            (500000, 1000000, "健步流星", 5),
            (1000000, 2000000, "追风逐日", 6),
            (2000000, 5000000, "缩地神行", 7),
            (5000000, 10000000, "千里独行", 8),
            (10000000, float('inf'), "逍遥游", 9),
        ],
        HealthCategory.SLEEP: [
            (0, 50000, "辗转反侧", 1),
            (50000, 200000, "安然入梦", 2),
            (200000, 500000, "深度睡眠", 3),
            (500000, 1000000, "黄粱美梦", 4),
            (1000000, 2000000, "庄周梦蝶", 5),
            (2000000, 5000000, "梦游仙境", 6),
            (5000000, 10000000, "大梦初醒", 7),
            (10000000, 20000000, "梦中悟道", 8),
            (20000000, float('inf'), "长生梦境", 9),
        ],
        # 其他类别的等级定义类似...
    }
    
    # 总功德十层天梯
    TOTAL_LEVELS = [
        (0, 100000, "凡夫俗子", 1),
        (100000, 500000, "初窥门径", 2),
        (500000, 2000000, "修身养性", 3),
        (2000000, 5000000, "小有所成", 4),
        (5000000, 10000000, "中流砥柱", 5),
        (10000000, 20000000, "登堂入室", 6),
        (20000000, 50000000, "炉火纯青", 7),
        (50000000, 100000000, "出神入化", 8),
        (100000000, 200000000, "功德圆满", 9),
        (200000000, float('inf'), "大罗金仙", 10),
    ]
    
    def __init__(self):
        """初始化功德计算器"""
        # 初始化所有类别的等级定义
        for category in HealthCategory:
            if category not in self.CATEGORY_LEVELS:
                # 为未定义等级的类别生成默认等级
                self.CATEGORY_LEVELS[category] = self._generate_default_levels(category.name)
    
    def _generate_default_levels(self, category_name: str) -> List[Tuple]:
        """为未定义等级的类别生成默认等级"""
        base_multipliers = [1, 5, 20, 50, 100, 200, 500, 1000, 2000]
        level_names = [
            f"{category_name}入门",
            f"{category_name}熟练",
            f"{category_name}精通",
            f"{category_name}专家",
            f"{category_name}大师",
            f"{category_name}宗师",
            f"{category_name}传奇",
            f"{category_name}神话",
            f"{category_name}至高",
        ]
        
        levels = []
        prev = 0
        for i, multiplier in enumerate(base_multipliers):
            min_merit = prev
            max_merit = 10000 * multiplier
            levels.append((min_merit, max_merit, level_names[i], i + 1))
            prev = max_merit
        
        # 最后一个等级无上限
        levels[-1] = (levels[-2][1], float('inf'), level_names[-1], len(base_multipliers))
        return levels
    
    def calculate_merit(self, health_data: HealthData, cumulative_merit: int = 0) -> MeritResult:
        """
        计算单次健康数据对应的功德
        
        Args:
            health_data: 健康数据
            cumulative_merit: 该类别累计功德
            
        Returns:
            MeritResult: 功德计算结果
        """
        # 计算本次功德
        rate = self.MERIT_RATES[health_data.category]
        
        if health_data.category == HealthCategory.WALKING:
            # 步行按每100步计算
            merit_points = int(health_data.value // 100 * 10)
        elif health_data.category == HealthCategory.SWIMMING:
            # 游泳按每100米计算
            merit_points = int(health_data.value // 100 * 800)
        else:
            merit_points = int(health_data.value * rate)
        
        # 更新累计功德
        total_merit = cumulative_merit + merit_points
        
        # 获取等级信息
        level_info = self.get_category_level(health_data.category, total_merit)
        
        return MeritResult(
            category=health_data.category,
            raw_value=health_data.value,
            merit_points=merit_points,
            level_name=level_info["name"],
            level_number=level_info["level"],
            progress=level_info["progress"],
            next_level_merit=level_info["next_level_merit"]
        )
    
    def get_category_level(self, category: HealthCategory, total_merit: int) -> Dict:
        """
        获取单项功德等级信息
        
        Args:
            category: 健康数据类型
            total_merit: 累计功德
            
        Returns:
            Dict: 等级信息
        """
        levels = self.CATEGORY_LEVELS[category]
        
        for i, (min_merit, max_merit, name, level) in enumerate(levels):
            if min_merit <= total_merit < max_merit:
                # 计算进度
                progress = (total_merit - min_merit) / (max_merit - min_merit)
                
                # 下一等级所需功德
                next_level_merit = max_merit - total_merit if i < len(levels) - 1 else 0
                
                return {
                    "name": name,
                    "level": level,
                    "progress": progress,
                    "next_level_merit": next_level_merit,
                    "min_merit": min_merit,
                    "max_merit": max_merit
                }
        
        # 如果超过最高等级
        last_level = levels[-1]
        return {
            "name": last_level[2],
            "level": last_level[3],
            "progress": 1.0,
            "next_level_merit": 0,
            "min_merit": last_level[0],
            "max_merit": last_level[1]
        }
    
    def get_total_level(self, total_merit: int) -> Dict:
        """
        获取总功德等级信息
        
        Args:
            total_merit: 总功德
            
        Returns:
            Dict: 总等级信息
        """
        for i, (min_merit, max_merit, name, level) in enumerate(self.TOTAL_LEVELS):
            if min_merit <= total_merit < max_merit:
                # 计算进度
                progress = (total_merit - min_merit) / (max_merit - min_merit)
                
                # 下一等级所需功德
                next_level_merit = max_merit - total_merit if i < len(self.TOTAL_LEVELS) - 1 else 0
                
                return {
                    "name": name,
                    "level": level,
                    "progress": progress,
                    "next_level_merit": next_level_merit,
                    "min_merit": min_merit,
                    "max_merit": max_merit
                }
        
        # 如果超过最高等级
        last_level = self.TOTAL_LEVELS[-1]
        return {
            "name": last_level[2],
            "level": last_level[3],
            "progress": 1.0,
            "next_level_merit": 0,
            "min_merit": last_level[0],
            "max_merit": last_level[1]
        }
    
    def calculate_daily_merit(self, daily_data: Dict[HealthCategory, float], 
                             cumulative_merits: Dict[HealthCategory, int] = None) -> Dict:
        """
        计算单日各项功德
        
        Args:
            daily_data: 单日健康数据 {category: value}
            cumulative_merits: 各类别累计功德
            
        Returns:
            Dict: 计算结果
        """
        if cumulative_merits is None:
            cumulative_merits = {cat: 0 for cat in HealthCategory}
        
        results = {}
        daily_total = 0
        
        for category, value in daily_data.items():
            if value > 0:
                # 创建健康数据
                if category == HealthCategory.RUNNING:
                    health_data = HealthData.create_running(value)
                elif category == HealthCategory.WALKING:
                    health_data = HealthData.create_walking(int(value))
                elif category == HealthCategory.SLEEP:
                    health_data = HealthData.create_sleep(value)
                elif category == HealthCategory.EXERCISE:
                    health_data = HealthData.create_exercise(int(value))
                elif category == HealthCategory.STANDING:
                    health_data = HealthData.create_standing(value)
                else:
                    health_data = HealthData(category=category, value=value, unit="", timestamp=datetime.now())
                
                # 计算功德
                result = self.calculate_merit(health_data, cumulative_merits.get(category, 0))
                results[category] = result
                daily_total += result.merit_points
        
        # 计算总等级
        total_cumulative = sum(cumulative_merits.values()) + daily_total
        total_level_info = self.get_total_level(total_cumulative)
        
        return {
            "daily_results": results,
            "daily_total": daily_total,
            "total_level": total_level_info,
            "total_merit": total_cumulative
        }


# 使用示例
if __name__ == "__main__":
    # 创建功德计算器
    calculator = MeritCalculator()
    
    # 示例数据
    print("=== 功德计算器演示 ===")
    
    # 单项计算示例
    running_data = HealthData.create_running(5.0)  # 跑步5公里
    result = calculator.calculate_merit(running_data, cumulative_merit=45000)
    
    print(f"\n跑步5公里功德计算:")
    print(f"  本次获得功德: {result.merit_points:,}")
    print(f"  当前等级: {result.level_name} (Lv.{result.level_number})")
    print(f"  等级进度: {result.progress:.1%}")
    print(f"  距离下一等级还需: {result.next_level_merit:,} 功德")
    
    # 单日计算示例
    daily_data = {
        HealthCategory.RUNNING: 3.2,    # 3.2公里
        HealthCategory.WALKING: 8500,   # 8500步
        HealthCategory.SLEEP: 7.5,      # 7.5小时睡眠
        HealthCategory.EXERCISE: 45,    # 45分钟锻炼
        HealthCategory.STANDING: 10,    # 10小时站立
    }
    
    cumulative = {
        HealthCategory.RUNNING: 125000,
        HealthCategory.WALKING: 85000,
        HealthCategory.SLEEP: 320000,
        HealthCategory.EXERCISE: 150000,
        HealthCategory.STANDING: 90000,
    }
    
    daily_result = calculator.calculate_daily_merit(daily_data, cumulative)
    
    print(f"\n单日功德汇总:")
    print(f"  今日总功德: {daily_result['daily_total']:,}")
    
    for category, result in daily_result["daily_results"].items():
        print(f"  {category.value}: {result.merit_points:,} 功德")
    
    print(f"\n总功德等级:")
    total_level = daily_result["total_level"]
    print(f"  当前等级: {total_level['name']} (Lv.{total_level['level']})")
    print(f"  总功德: {daily_result['total_merit']:,}")
    print(f"  等级进度: {total_level['progress']:.1%}")
    print(f"  距离下一等级还需: {total_level['next_level_merit']:,} 功德")