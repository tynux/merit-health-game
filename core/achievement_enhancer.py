#!/usr/bin/env python3
"""
成就系统增强模块
提供动态成就生成、功德加成、稀有度系统等功能
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import random
import logging

logger = logging.getLogger(__name__)


class AchievementRarity:
    """成就稀有度"""
    COMMON = "common"      # 普通
    RARE = "rare"          # 稀有
    EPIC = "epic"          # 史诗
    LEGENDARY = "legendary"  # 传奇
    
    @staticmethod
    def get_color(rarity: str) -> str:
        """获取稀有度对应的颜色"""
        colors = {
            "common": "#868e96",      # 灰色
            "rare": "#339af0",        # 蓝色
            "epic": "#9c36b5",        # 紫色
            "legendary": "#f59f00"    # 金色
        }
        return colors.get(rarity, "#868e96")
    
    @staticmethod
    def get_icon(rarity: str) -> str:
        """获取稀有度对应的图标"""
        icons = {
            "common": "fa-medal",
            "rare": "fa-trophy",
            "epic": "fa-crown",
            "legendary": "fa-gem"
        }
        return icons.get(rarity, "fa-medal")


class AchievementType:
    """成就类型"""
    MILESTONE = "milestone"      # 里程碑
    CHALLENGE = "challenge"      # 挑战
    HIDDEN = "hidden"            # 隐藏
    SEASONAL = "seasonal"        # 季节性
    SOCIAL = "social"            # 社交
    COMBO = "combo"              # 组合


class AchievementEnhancer:
    """成就增强器"""
    
    def __init__(self, db_manager):
        """
        初始化成就增强器
        
        Args:
            db_manager: 数据库管理器
        """
        self.db = db_manager
        self.enhanced_achievements = self._init_enhanced_achievements()
    
    def _init_enhanced_achievements(self) -> Dict[str, Dict]:
        """初始化增强成就定义"""
        return {
            # ========== 普通成就 (灰色) ==========
            "first_10000": {
                "name": "初积功德",
                "description": "累计获得10,000功德",
                "requirement_type": "total_merit",
                "requirement_value": 10000,
                "reward_merit": 1000,
                "rarity": AchievementRarity.COMMON,
                "type": AchievementType.MILESTONE,
                "icon": "fa-seedling",
                "boost_percentage": 1.0,  # 1% 永久功德加成
                "unlock_order": 1
            },
            "first_100km": {
                "name": "百里行者",
                "description": "累计跑步100公里",
                "requirement_type": "running_merit",
                "requirement_value": 100000,
                "reward_merit": 5000,
                "rarity": AchievementRarity.COMMON,
                "type": AchievementType.MILESTONE,
                "icon": "fa-running",
                "boost_percentage": 2.0,
                "unlock_order": 2
            },
            
            # ========== 稀有成就 (蓝色) ==========
            "streak_30": {
                "name": "月行一善",
                "description": "连续30天有健康数据记录",
                "requirement_type": "daily_streak",
                "requirement_value": 30,
                "reward_merit": 30000,
                "rarity": AchievementRarity.RARE,
                "type": AchievementType.CHALLENGE,
                "icon": "fa-calendar-check",
                "boost_percentage": 5.0,
                "unlock_order": 10
            },
            "daily_10000": {
                "name": "功德无量",
                "description": "单日获得10,000功德",
                "requirement_type": "daily_merit",
                "requirement_value": 10000,
                "reward_merit": 3000,
                "rarity": AchievementRarity.RARE,
                "type": AchievementType.CHALLENGE,
                "icon": "fa-bolt",
                "boost_percentage": 3.0,
                "unlock_order": 8
            },
            
            # ========== 史诗成就 (紫色) ==========
            "total_500000": {
                "name": "功德深厚",
                "description": "累计获得500,000功德",
                "requirement_type": "total_merit",
                "requirement_value": 500000,
                "reward_merit": 50000,
                "rarity": AchievementRarity.EPIC,
                "type": AchievementType.MILESTONE,
                "icon": "fa-mountain",
                "boost_percentage": 10.0,
                "unlock_order": 15
            },
            "streak_100": {
                "name": "百日筑基",
                "description": "连续100天有健康数据记录",
                "requirement_type": "daily_streak",
                "requirement_value": 100,
                "reward_merit": 100000,
                "rarity": AchievementRarity.EPIC,
                "type": AchievementType.CHALLENGE,
                "icon": "fa-fire",
                "boost_percentage": 15.0,
                "unlock_order": 20
            },
            
            # ========== 传奇成就 (金色) ==========
            "total_5000000": {
                "name": "功德圆满",
                "description": "累计获得5,000,000功德",
                "requirement_type": "total_merit",
                "requirement_value": 5000000,
                "reward_merit": 500000,
                "rarity": AchievementRarity.LEGENDARY,
                "type": AchievementType.MILESTONE,
                "icon": "fa-sun",
                "boost_percentage": 25.0,
                "unlock_order": 30
            },
            "all_categories_master": {
                "name": "全知全能",
                "description": "所有健康类别都达到大师级",
                "requirement_type": "all_categories_master",
                "requirement_value": 1,
                "reward_merit": 250000,
                "rarity": AchievementRarity.LEGENDARY,
                "type": AchievementType.COMBO,
                "icon": "fa-star",
                "boost_percentage": 20.0,
                "unlock_order": 25
            },
            
            # ========== 社交成就 (蓝色) ==========
            "first_friend": {
                "name": "结伴同行",
                "description": "添加第一位好友",
                "requirement_type": "friend_count",
                "requirement_value": 1,
                "reward_merit": 1000,
                "rarity": AchievementRarity.RARE,
                "type": AchievementType.SOCIAL,
                "icon": "fa-user-friends",
                "boost_percentage": 2.0,
                "unlock_order": 5,
                "hidden": False
            },
            "friend_streak_7": {
                "name": "同修七日",
                "description": "与好友连续7天互相监督",
                "requirement_type": "friend_streak",
                "requirement_value": 7,
                "reward_merit": 5000,
                "rarity": AchievementRarity.EPIC,
                "type": AchievementType.SOCIAL,
                "icon": "fa-hands-helping",
                "boost_percentage": 5.0,
                "unlock_order": 12,
                "hidden": False
            },
            
            # ========== 隐藏成就 (解锁后显示) ==========
            "midnight_cultivator": {
                "name": "子夜修行",
                "description": "在凌晨0点到3点之间提交健康数据",
                "requirement_type": "midnight_submission",
                "requirement_value": 1,
                "reward_merit": 7777,
                "rarity": AchievementRarity.RARE,
                "type": AchievementType.HIDDEN,
                "icon": "fa-moon",
                "boost_percentage": 3.0,
                "unlock_order": 999,
                "hidden": True
            },
            "perfect_week": {
                "name": "完美一周",
                "description": "连续7天每天都达到所有健康目标",
                "requirement_type": "perfect_week",
                "requirement_value": 1,
                "reward_merit": 15000,
                "rarity": AchievementRarity.EPIC,
                "type": AchievementType.HIDDEN,
                "icon": "fa-check-circle",
                "boost_percentage": 8.0,
                "unlock_order": 998,
                "hidden": True
            }
        }
    
    def get_enhanced_achievement(self, achievement_id: str) -> Optional[Dict]:
        """获取增强成就定义"""
        return self.enhanced_achievements.get(achievement_id)
    
    def get_all_enhanced_achievements(self) -> Dict[str, Dict]:
        """获取所有增强成就"""
        return self.enhanced_achievements
    
    def calculate_user_boost(self, user_id: str) -> float:
        """
        计算用户的总功德加成百分比
        
        Args:
            user_id: 用户ID
            
        Returns:
            总加成百分比
        """
        user_achievements = self.db.get_user_achievements(user_id)
        total_boost = 0.0
        
        for user_achievement in user_achievements:
            if user_achievement.get("is_achieved"):
                achievement_id = user_achievement.get("achievement_id")
                achievement_def = self.get_enhanced_achievement(achievement_id)
                
                if achievement_def:
                    total_boost += achievement_def.get("boost_percentage", 0.0)
        
        return total_boost
    
    def apply_boost_to_merit(self, base_merit: int, user_id: str) -> int:
        """
        应用功德加成
        
        Args:
            base_merit: 基础功德值
            user_id: 用户ID
            
        Returns:
            加成后的功德值
        """
        boost_percentage = self.calculate_user_boost(user_id)
        boosted_merit = int(base_merit * (1 + boost_percentage / 100))
        
        logger.info(f"用户 {user_id} 功德加成: {boost_percentage}%, 基础功德: {base_merit}, 加成后: {boosted_merit}")
        
        return boosted_merit
    
    def generate_dynamic_achievements(self, user_id: str, user_history: Dict) -> List[Dict]:
        """
        基于用户历史生成动态成就
        
        Args:
            user_id: 用户ID
            user_history: 用户历史数据
            
        Returns:
            动态成就列表
        """
        dynamic_achievements = []
        
        # 分析用户习惯
        user = self.db.get_user(user_id)
        if not user:
            return dynamic_achievements
        
        total_merit = user.get("total_merit", 0)
        daily_records = self.db.get_user_daily_records(user_id, limit=30)
        
        # 1. 基于总功德的动态成就
        if total_merit > 0:
            # 寻找最近的里程碑
            milestones = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
            for milestone in milestones:
                if total_merit >= milestone:
                    achievement_id = f"dynamic_milestone_{milestone}"
                    dynamic_achievements.append({
                        "achievement_id": achievement_id,
                        "name": f"功德里程碑 - {milestone:,}",
                        "description": f"累计获得 {milestone:,} 功德",
                        "requirement_type": "total_merit",
                        "requirement_value": milestone,
                        "reward_merit": milestone // 10,  # 10%奖励
                        "rarity": "rare" if milestone >= 100000 else "common",
                        "type": "milestone",
                        "icon": "fa-flag",
                        "is_dynamic": True
                    })
        
        # 2. 基于连续天数的动态成就
        if daily_records:
            streak_days = len(daily_records)
            if streak_days >= 3:
                achievement_id = f"dynamic_streak_{streak_days}"
                dynamic_achievements.append({
                    "achievement_id": achievement_id,
                    "name": f"连续修行 {streak_days} 天",
                    "description": f"连续 {streak_days} 天记录健康数据",
                    "requirement_type": "daily_streak",
                    "requirement_value": streak_days,
                    "reward_merit": streak_days * 100,
                    "rarity": "common",
                    "type": "challenge",
                    "icon": "fa-calendar-alt",
                    "is_dynamic": True
                })
        
        # 3. 基于活跃时段的动态成就
        # TODO: 分析用户最活跃的时段
        
        # 4. 基于健康类别的动态成就
        category_merits = user.get("category_merits", {})
        for category, merit in category_merits.items():
            if merit > 10000:  # 如果某个类别功德超过10,000
                achievement_id = f"dynamic_category_{category}"
                category_names = {
                    "running": "跑步",
                    "walking": "步行",
                    "sleep": "睡眠",
                    "exercise": "锻炼"
                }
                category_name = category_names.get(category, category)
                
                dynamic_achievements.append({
                    "achievement_id": achievement_id,
                    "name": f"{category_name}达人",
                    "description": f"累计 {category_name} 功德超过10,000",
                    "requirement_type": f"{category}_merit",
                    "requirement_value": 10000,
                    "reward_merit": 2000,
                    "rarity": "rare",
                    "type": "milestone",
                    "icon": "fa-running" if category == "running" else "fa-walking",
                    "is_dynamic": True
                })
        
        return dynamic_achievements
    
    def check_special_achievements(self, user_id: str, health_data: Dict) -> List[Dict]:
        """
        检查特殊成就（如时间、组合等）
        
        Args:
            user_id: 用户ID
            health_data: 健康数据
            
        Returns:
            新解锁的特殊成就列表
        """
        special_achievements = []
        current_time = datetime.now()
        
        # 检查子夜修行成就
        if 0 <= current_time.hour < 3:
            # 凌晨0-3点提交数据
            special_achievements.append("midnight_cultivator")
        
        # 检查完美日成就
        # 需要所有主要类别都有数据
        main_categories = ["walking", "sleep", "standing"]
        if all(cat in health_data for cat in main_categories):
            # 检查是否达到目标值
            if health_data.get("walking", 0) >= 10000:  # 10000步
                if health_data.get("sleep", 0) >= 7.0:  # 7小时睡眠
                    if health_data.get("standing", 0) >= 8.0:  # 8小时站立
                        special_achievements.append("perfect_day")
        
        return special_achievements
    
    def format_achievement_for_display(self, achievement_def: Dict, user_progress: Dict) -> Dict:
        """
        格式化成就用于显示
        
        Args:
            achievement_def: 成就定义
            user_progress: 用户进度
            
        Returns:
            格式化后的成就数据
        """
        is_achieved = user_progress.get("is_achieved", False)
        progress = user_progress.get("progress", 0.0)
        
        return {
            "id": achievement_def.get("achievement_id", ""),
            "name": achievement_def.get("name", ""),
            "description": achievement_def.get("description", ""),
            "rarity": achievement_def.get("rarity", "common"),
            "type": achievement_def.get("type", "milestone"),
            "icon": achievement_def.get("icon", "fa-medal"),
            "progress": progress,
            "is_achieved": is_achieved,
            "reward_merit": achievement_def.get("reward_merit", 0),
            "boost_percentage": achievement_def.get("boost_percentage", 0.0),
            "color": AchievementRarity.get_color(achievement_def.get("rarity", "common")),
            "display_icon": AchievementRarity.get_icon(achievement_def.get("rarity", "common"))
        }
    
    def get_achievement_summary(self, user_id: str) -> Dict:
        """
        获取用户成就摘要
        
        Args:
            user_id: 用户ID
            
        Returns:
            成就摘要
        """
        user_achievements = self.db.get_user_achievements(user_id)
        enhanced_achievements = self.get_all_enhanced_achievements()
        
        total_count = len(enhanced_achievements)
        achieved_count = sum(1 for a in user_achievements if a.get("is_achieved"))
        
        # 按稀有度统计
        rarity_stats = {
            "common": {"total": 0, "achieved": 0},
            "rare": {"total": 0, "achieved": 0},
            "epic": {"total": 0, "achieved": 0},
            "legendary": {"total": 0, "achieved": 0}
        }
        
        for achievement_id, achievement_def in enhanced_achievements.items():
            rarity = achievement_def.get("rarity", "common")
            rarity_stats[rarity]["total"] += 1
            
            # 查找用户进度
            user_achievement = next(
                (a for a in user_achievements 
                 if a.get("achievement_id") == achievement_id and a.get("is_achieved")),
                None
            )
            if user_achievement:
                rarity_stats[rarity]["achieved"] += 1
        
        # 计算总加成
        total_boost = self.calculate_user_boost(user_id)
        
        return {
            "total": total_count,
            "achieved": achieved_count,
            "progress_percentage": achieved_count / total_count * 100 if total_count > 0 else 0,
            "rarity_stats": rarity_stats,
            "total_boost": total_boost,
            "next_boost_target": self._get_next_boost_target(user_id)
        }
    
    def _get_next_boost_target(self, user_id: str) -> Optional[Dict]:
        """
        获取下一个功德加成目标
        
        Args:
            user_id: 用户ID
            
        Returns:
            下一个加成目标信息
        """
        user_achievements = self.db.get_user_achievements(user_id)
        enhanced_achievements = self.get_all_enhanced_achievements()
        
        # 找到未完成且提供加成的成就
        unachieved_with_boost = []
        
        for achievement_id, achievement_def in enhanced_achievements.items():
            # 检查是否已达成
            is_achieved = any(
                a.get("achievement_id") == achievement_id and a.get("is_achieved")
                for a in user_achievements
            )
            
            if not is_achieved and achievement_def.get("boost_percentage", 0) > 0:
                unachieved_with_boost.append({
                    "achievement_id": achievement_id,
                    "name": achievement_def.get("name"),
                    "boost_percentage": achievement_def.get("boost_percentage", 0),
                    "description": achievement_def.get("description"),
                    "rarity": achievement_def.get("rarity", "common")
                })
        
        # 按加成百分比排序
        unachieved_with_boost.sort(key=lambda x: x["boost_percentage"], reverse=True)
        
        return unachieved_with_boost[0] if unachieved_with_boost else None