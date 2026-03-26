#!/usr/bin/env python3
"""
功德服务层
核心业务逻辑，整合功德计算、数据存储和等级系统
"""

import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .merit_calculator import MeritCalculator, HealthData, HealthCategory
from .achievement_enhancer import AchievementEnhancer
from data.database import DatabaseManager
from data.models import User, DailyRecord, MeritLevel, ModelFactory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeritService:
    """功德服务"""
    
    def __init__(self, db_path: str = "merit_health.db"):
        """
        初始化功德服务
        
        Args:
            db_path: 数据库文件路径
        """
        self.db = DatabaseManager(db_path)
        self.calculator = MeritCalculator()
        self.achievements = self._init_default_achievements()
        self.achievement_enhancer = AchievementEnhancer(self.db)
        
        logger.info("功德服务初始化完成")
    
    def _init_default_achievements(self) -> Dict[str, Dict]:
        """初始化默认成就"""
        return {
            # 里程碑成就
            "first_10000": {
                "name": "初积功德",
                "description": "累计获得10,000功德",
                "requirement_type": "total_merit",
                "requirement_value": 10000,
                "reward_merit": 1000
            },
            "first_100km": {
                "name": "百里行者",
                "description": "累计跑步100公里",
                "requirement_type": "running_merit",
                "requirement_value": 100000,  # 100km * 1000
                "reward_merit": 5000
            },
            "first_100k_steps": {
                "name": "万步达人",
                "description": "累计步行100,000步",
                "requirement_type": "walking_merit",
                "requirement_value": 10000,  # 100,000步 / 100 * 10
                "reward_merit": 2000
            },
            "first_100h_sleep": {
                "name": "安睡百年",
                "description": "累计睡眠100小时",
                "requirement_type": "sleep_merit",
                "requirement_value": 50000,  # 100小时 * 500
                "reward_merit": 3000
            },
            
            # 连续成就
            "streak_7": {
                "name": "持之以恒",
                "description": "连续7天有健康数据记录",
                "requirement_type": "daily_streak",
                "requirement_value": 7,
                "reward_merit": 5000
            },
            "streak_30": {
                "name": "月行一善",
                "description": "连续30天有健康数据记录",
                "requirement_type": "daily_streak",
                "requirement_value": 30,
                "reward_merit": 30000
            },
            
            # 单日成就
            "daily_5000": {
                "name": "日行一善",
                "description": "单日获得5,000功德",
                "requirement_type": "daily_merit",
                "requirement_value": 5000,
                "reward_merit": 1000
            },
            "daily_10000": {
                "name": "功德无量",
                "description": "单日获得10,000功德",
                "requirement_type": "daily_merit",
                "requirement_value": 10000,
                "reward_merit": 3000
            },
        }
    
    # ========== 用户管理 ==========
    
    def register_user(self, user_id: str, nickname: str, avatar_url: str = None) -> bool:
        """
        注册新用户
        
        Args:
            user_id: 用户ID
            nickname: 昵称
            avatar_url: 头像URL
            
        Returns:
            bool: 是否成功
        """
        success = self.db.create_user(user_id, nickname, avatar_url)
        if success:
            # 初始化用户成就
            for achievement_id in self.achievements.keys():
                self.db.update_user_achievement(user_id, achievement_id, progress=0.0)
        
        return success
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        获取用户完整资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 用户资料
        """
        user = self.db.get_user(user_id)
        if not user:
            return None
        
        # 获取用户成就
        achievements = self.db.get_user_achievements(user_id)
        
        # 获取今日记录
        today = date.today()
        daily_record = self.db.get_daily_record(user_id, today)
        
        # 获取连续天数
        streak = self._calculate_streak(user_id)
        
        # 获取各项功德等级
        category_levels = {}
        for category in HealthCategory:
            category_name = category.value
            merit_key = f"{category_name}_merit"
            if merit_key in user:
                merit = user[merit_key]
                level_info = self.calculator.get_category_level(category, merit)
                category_levels[category_name] = level_info
        
        # 获取总等级
        total_level_info = self.calculator.get_total_level(user["total_merit"])
        
        return {
            "user_info": {
                "user_id": user["user_id"],
                "nickname": user["nickname"],
                "avatar_url": user["avatar_url"],
                "created_at": user["created_at"]
            },
            "merit_info": {
                "total_merit": user["total_merit"],
                "total_level": total_level_info,
                "category_merits": {
                    "running": user["running_merit"],
                    "walking": user["walking_merit"],
                    "standing": user["standing_merit"],
                    "exercise": user["exercise_merit"],
                    "heart_rate": user["heart_rate_merit"],
                    "sleep": user["sleep_merit"],
                    "meditation": user["meditation_merit"],
                    "stairs": user["stairs_merit"],
                    "swimming": user["swimming_merit"]
                },
                "category_levels": category_levels
            },
            "daily_info": {
                "today": daily_record,
                "streak_days": streak
            },
            "achievements": self.get_enhanced_achievements(user_id)
        }
    
    def get_enhanced_achievements(self, user_id: str) -> Dict[str, Any]:
        """
        获取增强的成就数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            增强成就数据
        """
        try:
            # 获取用户原始成就数据
            user_achievements = self.db.get_user_achievements(user_id)
            
            # 获取增强成就定义
            enhanced_achievements_def = self.achievement_enhancer.get_all_enhanced_achievements()
            
            enhanced_list = []
            
            for achievement_id, achievement_def in enhanced_achievements_def.items():
                # 查找用户进度
                user_achievement = next(
                    (a for a in user_achievements 
                     if a.get("achievement_id") == achievement_id),
                    {"progress": 0.0, "is_achieved": False}
                )
                
                # 格式化成就数据
                formatted_achievement = self.achievement_enhancer.format_achievement_for_display(
                    {"achievement_id": achievement_id, **achievement_def},
                    user_achievement
                )
                
                enhanced_list.append(formatted_achievement)
            
            # 获取成就摘要
            summary = self.achievement_enhancer.get_achievement_summary(user_id)
            
            # 获取动态成就
            user = self.db.get_user(user_id)
            user_history = {}  # 可以扩展为用户历史数据
            dynamic_achievements = self.achievement_enhancer.generate_dynamic_achievements(user_id, user_history)
            
            return {
                "total": summary["total"],
                "achieved": summary["achieved"],
                "progress_percentage": summary["progress_percentage"],
                "total_boost": summary["total_boost"],
                "rarity_stats": summary["rarity_stats"],
                "list": enhanced_list,
                "dynamic_achievements": dynamic_achievements,
                "next_boost_target": summary.get("next_boost_target")
            }
        except Exception as e:
            logger.error(f"获取增强成就数据失败: {e}")
            # 返回基础数据作为回退
            user_achievements = self.db.get_user_achievements(user_id)
            return {
                "total": len(user_achievements),
                "achieved": len([a for a in user_achievements if a.get("is_achieved")]),
                "list": user_achievements
            }
    
    def _calculate_streak(self, user_id: str) -> int:
        """计算连续天数"""
        try:
            # 获取最近30天的记录
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            records = self.db.get_user_daily_records(user_id, start_date, end_date)
            if not records:
                return 0
            
            # 按日期排序
            record_dates = {datetime.strptime(r["record_date"], "%Y-%m-%d").date() for r in records}
            
            # 计算连续天数
            streak = 0
            current_date = end_date
            
            while current_date >= start_date:
                if current_date in record_dates:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return streak
        except Exception as e:
            logger.error(f"计算连续天数失败: {e}")
            return 0
    
    # ========== 健康数据处理 ==========
    
    def process_health_data(self, user_id: str, health_data_list: List[HealthData]) -> Dict[str, Any]:
        """
        处理健康数据并计算功德
        
        Args:
            user_id: 用户ID
            health_data_list: 健康数据列表
            
        Returns:
            Dict: 处理结果
        """
        # 获取用户当前功德
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "error": "用户不存在"}
        
        # 获取今日记录或创建新记录
        today = date.today()
        daily_record = self.db.get_daily_record(user_id, today)
        
        if not daily_record:
            # 创建新记录
            record_id = str(uuid.uuid4())
            self.db.create_daily_record(record_id, user_id, today)
            daily_record = self.db.get_daily_record(user_id, today)
        
        # 初始化数据字典
        current_health_data = {
            "steps": daily_record.get("steps", 0),
            "running_distance": daily_record.get("running_distance", 0.0),
            "standing_hours": daily_record.get("standing_hours", 0.0),
            "exercise_minutes": daily_record.get("exercise_minutes", 0),
            "heart_rate_minutes": daily_record.get("heart_rate_minutes", 0),
            "sleep_hours": daily_record.get("sleep_hours", 0.0),
            "meditation_minutes": daily_record.get("meditation_minutes", 0),
            "stairs_count": daily_record.get("stairs_count", 0),
            "swimming_distance": daily_record.get("swimming_distance", 0.0)
        }
        
        current_merit_data = {
            "running": daily_record.get("running_merit", 0),
            "walking": daily_record.get("walking_merit", 0),
            "standing": daily_record.get("standing_merit", 0),
            "exercise": daily_record.get("exercise_merit", 0),
            "heart_rate": daily_record.get("heart_rate_merit", 0),
            "sleep": daily_record.get("sleep_merit", 0),
            "meditation": daily_record.get("meditation_merit", 0),
            "stairs": daily_record.get("stairs_merit", 0),
            "swimming": daily_record.get("swimming_merit", 0)
        }
        
        # 计算用户功德加成百分比
        user_boost_percentage = self.achievement_enhancer.calculate_user_boost(user_id)
        
        # 处理每个健康数据
        results = []
        total_merit_earned = 0
        total_merit_earned_before_boost = 0
        
        for health_data in health_data_list:
            # 获取该类别的累计功德
            category_key = f"{health_data.category.value}_merit"
            cumulative_merit = user.get(category_key, 0)
            
            # 计算基础功德
            result = self.calculator.calculate_merit(health_data, cumulative_merit)
            
            # 应用功德加成
            base_merit = result.merit_points
            boosted_merit = self.achievement_enhancer.apply_boost_to_merit(base_merit, user_id)
            
            # 创建增强的结果对象
            enhanced_result = type('EnhancedMeritResult', (), {
                'category': result.category,
                'raw_value': result.raw_value,
                'merit_points': boosted_merit,  # 使用加成后的功德
                'level_name': result.level_name,
                'level_number': result.level_number,
                'progress': result.progress,
                'next_level_merit': result.next_level_merit,
                'base_merit': base_merit,  # 基础功德
                'boost_percentage': user_boost_percentage,  # 加成百分比
                'boosted_amount': boosted_merit - base_merit  # 加成量
            })()
            
            results.append(enhanced_result)
            
            # 更新累计数据（使用加成后的功德）
            if health_data.category == HealthCategory.RUNNING:
                current_health_data["running_distance"] += health_data.value
                current_merit_data["running"] += boosted_merit
            elif health_data.category == HealthCategory.WALKING:
                current_health_data["steps"] += int(health_data.value)
                current_merit_data["walking"] += boosted_merit
            elif health_data.category == HealthCategory.STANDING:
                current_health_data["standing_hours"] += health_data.value
                current_merit_data["standing"] += boosted_merit
            elif health_data.category == HealthCategory.EXERCISE:
                current_health_data["exercise_minutes"] += int(health_data.value)
                current_merit_data["exercise"] += boosted_merit
            elif health_data.category == HealthCategory.HEART_RATE:
                current_health_data["heart_rate_minutes"] += int(health_data.value)
                current_merit_data["heart_rate"] += boosted_merit
            elif health_data.category == HealthCategory.SLEEP:
                current_health_data["sleep_hours"] += health_data.value
                current_merit_data["sleep"] += boosted_merit
            elif health_data.category == HealthCategory.MEDITATION:
                current_health_data["meditation_minutes"] += int(health_data.value)
                current_merit_data["meditation"] += boosted_merit
            elif health_data.category == HealthCategory.STAIRS:
                current_health_data["stairs_count"] += int(health_data.value)
                current_merit_data["stairs"] += boosted_merit
            elif health_data.category == HealthCategory.SWIMMING:
                current_health_data["swimming_distance"] += health_data.value
                current_merit_data["swimming"] += boosted_merit
            
            total_merit_earned_before_boost += base_merit
            total_merit_earned += boosted_merit
            
            # 记录功德事件
            event_id = str(uuid.uuid4())
            self.db.create_merit_event(
                event_id=event_id,
                user_id=user_id,
                event_type="health_data",
                category=health_data.category.value,
                merit_earned=result.merit_points,
                description=f"{health_data.category.value}: {health_data.value}{health_data.unit}",
                metadata={
                    "raw_value": health_data.value,
                    "unit": health_data.unit,
                    "category_level": result.level_name,
                    "category_level_number": result.level_number
                }
            )
            
            # 更新用户功德
            self.db.update_user_merit(user_id, health_data.category.value, result.merit_points)
        
        # 更新每日记录
        self.db.update_daily_record(
            user_id, today,
            current_health_data,
            current_merit_data
        )
        
        # 检查成就
        self._check_achievements(user_id)
        
        return {
            "success": True,
            "total_merit_earned": total_merit_earned,
            "total_merit_earned_before_boost": total_merit_earned_before_boost,
            "boost_percentage": user_boost_percentage,
            "boost_amount": total_merit_earned - total_merit_earned_before_boost,
            "results": [{
                "category": r.category.value,
                "raw_value": r.raw_value,
                "merit_points": r.merit_points,
                "base_merit": getattr(r, 'base_merit', r.merit_points),
                "boost_percentage": getattr(r, 'boost_percentage', 0),
                "boosted_amount": getattr(r, 'boosted_amount', 0),
                "level_name": r.level_name,
                "level_number": r.level_number,
                "progress": r.progress
            } for r in results],
            "daily_summary": {
                "date": today.isoformat(),
                "total_merit": sum(current_merit_data.values())
            }
        }
    
    def process_health_data_dict(self, user_id: str, health_data_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        使用字典格式处理健康数据
        
        Args:
            user_id: 用户ID
            health_data_dict: 健康数据字典 {category: value}
            
        Returns:
            Dict: 处理结果
        """
        # 转换为HealthData对象
        health_data_list = []
        
        for category_str, value in health_data_dict.items():
            if value <= 0:
                continue
            
            try:
                category = HealthCategory(category_str)
                
                if category == HealthCategory.RUNNING:
                    data = HealthData.create_running(value)
                elif category == HealthCategory.WALKING:
                    data = HealthData.create_walking(int(value))
                elif category == HealthCategory.STANDING:
                    data = HealthData.create_standing(value)
                elif category == HealthCategory.EXERCISE:
                    data = HealthData.create_exercise(int(value))
                elif category == HealthCategory.SLEEP:
                    data = HealthData.create_sleep(value)
                else:
                    # 其他类别使用通用构造函数
                    data = HealthData(
                        category=category,
                        value=value,
                        unit="",
                        timestamp=datetime.now()
                    )
                
                health_data_list.append(data)
            except ValueError:
                logger.warning(f"未知的健康数据类别: {category_str}")
                continue
        
        return self.process_health_data(user_id, health_data_list)
    
    # ========== 成就系统 ==========
    
    def _check_achievements(self, user_id: str):
        """检查用户成就"""
        user = self.db.get_user(user_id)
        if not user:
            return
        
        # 检查每个成就
        for achievement_id, achievement in self.achievements.items():
            requirement_type = achievement["requirement_type"]
            requirement_value = achievement["requirement_value"]
            
            progress = 0.0
            is_achieved = False
            
            if requirement_type == "total_merit":
                current_value = user["total_merit"]
                progress = min(current_value / requirement_value, 1.0)
                is_achieved = current_value >= requirement_value
                
            elif requirement_type.startswith("_"):  # 类别功德，如 running_merit
                category = requirement_type.replace("_merit", "")
                current_value = user.get(f"{category}_merit", 0)
                progress = min(current_value / requirement_value, 1.0)
                is_achieved = current_value >= requirement_value
                
            elif requirement_type == "daily_streak":
                streak = self._calculate_streak(user_id)
                progress = min(streak / requirement_value, 1.0)
                is_achieved = streak >= requirement_value
                
            elif requirement_type == "daily_merit":
                # 获取今日功德
                today = date.today()
                daily = self.db.get_daily_record(user_id, today)
                current_value = daily["total_merit"] if daily else 0
                progress = min(current_value / requirement_value, 1.0)
                is_achieved = current_value >= requirement_value
            
            # 更新成就进度
            self.db.update_user_achievement(
                user_id, achievement_id,
                progress=progress,
                is_achieved=is_achieved
            )
            
            # 如果成就刚刚达成，发放奖励
            if is_achieved:
                # 检查是否之前已经达成
                user_achievements = self.db.get_user_achievements(user_id)
                existing = next(
                    (a for a in user_achievements 
                     if a.get("achievement_id") == achievement_id and a.get("is_achieved")),
                    None
                )
                
                if not existing:
                    # 发放奖励功德
                    reward = achievement.get("reward_merit", 0)
                    if reward > 0:
                        self.db.update_user_merit(user_id, "achievement", reward)
                        
                        # 记录功德事件
                        event_id = str(uuid.uuid4())
                        self.db.create_merit_event(
                            event_id=event_id,
                            user_id=user_id,
                            event_type="achievement",
                            merit_earned=reward,
                            description=f"成就奖励: {achievement['name']}",
                            metadata={
                                "achievement_id": achievement_id,
                                "achievement_name": achievement["name"],
                                "reward_merit": reward
                            }
                        )
    
    # ========== 排行榜 ==========
    
    def get_leaderboard(self, board_type: str = "total", limit: int = 100) -> List[Dict]:
        """
        获取排行榜
        
        Args:
            board_type: 排行榜类型 (total, daily, weekly, monthly)
            limit: 返回数量
            
        Returns:
            List[Dict]: 排行榜数据
        """
        if board_type == "daily":
            return self.db.get_daily_leaderboard(date.today(), limit)
        else:
            return self.db.get_leaderboard(limit)
    
    def get_user_rank(self, user_id: str, board_type: str = "total") -> Optional[Dict]:
        """
        获取用户排名
        
        Args:
            user_id: 用户ID
            board_type: 排行榜类型
            
        Returns:
            Optional[Dict]: 排名信息
        """
        leaderboard = self.get_leaderboard(board_type, limit=1000)
        
        for entry in leaderboard:
            if entry["user_id"] == user_id:
                total_users = len(leaderboard)
                percentile = (entry["rank"] / total_users) * 100
                
                return {
                    "rank": entry["rank"],
                    "total_users": total_users,
                    "percentile": round(percentile, 1),
                    "merit_value": entry.get("total_merit") or entry.get("daily_merit"),
                    "level": entry.get("current_level_name")
                }
        
        return None
    
    # ========== 统计报告 ==========
    
    def get_user_report(self, user_id: str, period: str = "weekly") -> Dict[str, Any]:
        """
        获取用户统计报告
        
        Args:
            user_id: 用户ID
            period: 报告周期 (daily, weekly, monthly, yearly)
            
        Returns:
            Dict: 统计报告
        """
        end_date = date.today()
        
        if period == "daily":
            start_date = end_date
        elif period == "weekly":
            start_date = end_date - timedelta(days=6)
        elif period == "monthly":
            start_date = end_date - timedelta(days=29)
        elif period == "yearly":
            start_date = end_date - timedelta(days=364)
        else:
            start_date = end_date - timedelta(days=6)  # 默认周报
        
        # 获取数据库统计
        stats = self.db.get_user_statistics(user_id, start_date, end_date)
        
        # 获取用户资料
        profile = self.get_user_profile(user_id)
        
        # 获取趋势数据
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            daily = self.db.get_daily_record(user_id, current_date)
            trend_data.append({
                "date": current_date.isoformat(),
                "merit": daily["total_merit"] if daily else 0,
                "steps": daily["steps"] if daily else 0,
                "running_km": daily["running_distance"] if daily else 0.0,
                "sleep_hours": daily["sleep_hours"] if daily else 0.0
            })
            current_date += timedelta(days=1)
        
        # 获取功德事件
        events = self.db.get_user_merit_events(
            user_id, limit=50,
            start_date=start_date, end_date=end_date
        )
        
        return {
            "period": {
                "type": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days + 1
            },
            "profile_summary": {
                "nickname": profile["user_info"]["nickname"],
                "total_merit": profile["merit_info"]["total_merit"],
                "total_level": profile["merit_info"]["total_level"]["name"],
                "streak_days": profile["daily_info"]["streak_days"]
            } if profile else {},
            "statistics": stats.get("statistics", {}),
            "trend_data": trend_data,
            "recent_events": events[:10],  # 最近10个事件
            "achievements_progress": {
                "total": len(profile["achievements"]["list"]) if profile else 0,
                "achieved": len([a for a in profile["achievements"]["list"] if a.get("is_achieved")]) if profile else 0
            } if profile else {},
            "best_day": stats.get("best_day", {})
        }
    
    # ========== 工具方法 ==========
    
    def close(self):
        """关闭服务"""
        self.db.close()
        logger.info("功德服务已关闭")


# 使用示例
if __name__ == "__main__":
    print("=== 功德服务演示 ===")
    
    # 创建服务实例
    service = MeritService(":memory:")  # 使用内存数据库
    
    try:
        # 注册用户
        service.register_user("demo_user_001", "演示用户", "https://example.com/avatar.jpg")
        
        # 获取用户资料
        profile = service.get_user_profile("demo_user_001")
        print(f"\n用户资料:")
        print(f"  昵称: {profile['user_info']['nickname']}")
        print(f"  总功德: {profile['merit_info']['total_merit']:,}")
        print(f"  总等级: {profile['merit_info']['total_level']['name']}")
        
        # 处理健康数据
        print(f"\n处理健康数据...")
        
        health_data = [
            HealthData.create_running(5.2),      # 跑步5.2公里
            HealthData.create_walking(12500),    # 步行12500步
            HealthData.create_sleep(7.8),        # 睡眠7.8小时
            HealthData.create_exercise(60),      # 锻炼60分钟
        ]
        
        result = service.process_health_data("demo_user_001", health_data)
        
        if result["success"]:
            print(f"  今日获得功德: {result['total_merit_earned']:,}")
            
            for item in result["results"]:
                print(f"  {item['category']}: {item['merit_points']:,}功德 ({item['level_name']})")
        
        # 再次获取用户资料查看更新
        updated_profile = service.get_user_profile("demo_user_001")
        print(f"\n更新后资料:")
        print(f"  总功德: {updated_profile['merit_info']['total_merit']:,}")
        print(f"  跑步功德: {updated_profile['merit_info']['category_merits']['running']:,}")
        print(f"  步行功德: {updated_profile['merit_info']['category_merits']['walking']:,}")
        
        # 获取排行榜
        print(f"\n排行榜:")
        leaderboard = service.get_leaderboard("total", limit=5)
        for entry in leaderboard:
            print(f"  第{entry['rank']}名: {entry['nickname']} - {entry['total_merit']:,}功德")
        
        # 获取用户排名
        user_rank = service.get_user_rank("demo_user_001")
        if user_rank:
            print(f"\n用户排名:")
            print(f"  第{user_rank['rank']}名 (前{user_rank['percentile']:.1f}%)")
        
        # 获取周报
        print(f"\n周报摘要:")
        weekly_report = service.get_user_report("demo_user_001", "weekly")
        stats = weekly_report.get("statistics", {})
        print(f"  活跃天数: {stats.get('days_active', 0)}天")
        print(f"  周期功德: {stats.get('period_merit', 0):,}")
        print(f"  平均每日: {stats.get('avg_daily_merit', 0):.0f}功德")
        
        # 关闭服务
        service.close()
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
        service.close()