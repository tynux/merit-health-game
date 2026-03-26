#!/usr/bin/env python3
"""
数据模型定义
用户、健康记录、功德记录等数据结构
"""

from datetime import datetime, date
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import json


class MeritLevel(Enum):
    """总功德十层天梯"""
    MORTAL = ("凡夫俗子", 1, 0, 100000)
    BEGINNER = ("初窥门径", 2, 100000, 500000)
    CULTIVATOR = ("修身养性", 3, 500000, 2000000)
    APPRENTICE = ("小有所成", 4, 2000000, 5000000)
    PILLAR = ("中流砥柱", 5, 5000000, 10000000)
    MASTER = ("登堂入室", 6, 10000000, 20000000)
    EXPERT = ("炉火纯青", 7, 20000000, 50000000)
    PERFECT = ("出神入化", 8, 50000000, 100000000)
    COMPLETE = ("功德圆满", 9, 100000000, 200000000)
    IMMORTAL = ("大罗金仙", 10, 200000000, float('inf'))
    
    def __init__(self, chinese_name, level, min_merit, max_merit):
        self.chinese_name = chinese_name
        self.level = level
        self.min_merit = min_merit
        self.max_merit = max_merit
    
    @classmethod
    def from_merit(cls, total_merit: int):
        """根据总功德获取等级"""
        for level in cls:
            if level.min_merit <= total_merit < level.max_merit:
                return level
        return cls.IMMORTAL
    
    @property
    def progress(self, total_merit: int) -> float:
        """计算当前等级进度"""
        if self.max_merit == float('inf'):
            return 1.0
        range_size = self.max_merit - self.min_merit
        current = total_merit - self.min_merit
        return min(current / range_size, 1.0)
    
    @property
    def next_level_merit(self, total_merit: int) -> int:
        """计算距离下一等级所需功德"""
        if self == self.IMMORTAL:
            return 0
        return max(0, self.max_merit - total_merit)


@dataclass
class User:
    """用户模型"""
    user_id: str
    nickname: str
    avatar_url: Optional[str] = None
    total_merit: int = 0
    current_level: MeritLevel = MeritLevel.MORTAL
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 各项累计功德
    running_merit: int = 0
    walking_merit: int = 0
    standing_merit: int = 0
    exercise_merit: int = 0
    heart_rate_merit: int = 0
    sleep_merit: int = 0
    meditation_merit: int = 0
    stairs_merit: int = 0
    swimming_merit: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "total_merit": self.total_merit,
            "current_level": {
                "name": self.current_level.chinese_name,
                "level": self.current_level.level,
                "progress": self.current_level.progress(self.total_merit),
                "next_level_merit": self.current_level.next_level_merit(self.total_merit)
            },
            "category_merits": self.get_category_merits(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_category_merits(self) -> Dict[str, int]:
        """获取各项功德字典"""
        return {
            "running": self.running_merit,
            "walking": self.walking_merit,
            "standing": self.standing_merit,
            "exercise": self.exercise_merit,
            "heart_rate": self.heart_rate_merit,
            "sleep": self.sleep_merit,
            "meditation": self.meditation_merit,
            "stairs": self.stairs_merit,
            "swimming": self.swimming_merit
        }
    
    def update_merit(self, category: str, merit: int):
        """更新某项功德"""
        category = category.lower()
        
        # 更新对应字段
        if category == "running":
            self.running_merit += merit
        elif category == "walking":
            self.walking_merit += merit
        elif category == "standing":
            self.standing_merit += merit
        elif category == "exercise":
            self.exercise_merit += merit
        elif category == "heart_rate":
            self.heart_rate_merit += merit
        elif category == "sleep":
            self.sleep_merit += merit
        elif category == "meditation":
            self.meditation_merit += merit
        elif category == "stairs":
            self.stairs_merit += merit
        elif category == "swimming":
            self.swimming_merit += merit
        else:
            raise ValueError(f"未知的功德类别: {category}")
        
        # 更新总功德
        self.total_merit += merit
        
        # 更新等级
        self.current_level = MeritLevel.from_merit(self.total_merit)
        
        # 更新修改时间
        self.updated_at = datetime.now()


@dataclass
class DailyRecord:
    """每日健康记录"""
    record_id: str
    user_id: str
    record_date: date
    
    # 健康数据
    steps: int = 0
    running_distance: float = 0.0  # 公里
    standing_hours: float = 0.0
    exercise_minutes: int = 0
    heart_rate_minutes: int = 0
    sleep_hours: float = 0.0
    meditation_minutes: int = 0
    stairs_count: int = 0
    swimming_distance: float = 0.0  # 米
    
    # 计算出的功德
    total_merit: int = 0
    running_merit: int = 0
    walking_merit: int = 0
    standing_merit: int = 0
    exercise_merit: int = 0
    heart_rate_merit: int = 0
    sleep_merit: int = 0
    meditation_merit: int = 0
    stairs_merit: int = 0
    swimming_merit: int = 0
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "record_date": self.record_date.isoformat(),
            "health_data": self.get_health_data(),
            "merit_data": self.get_merit_data(),
            "total_merit": self.total_merit,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_health_data(self) -> Dict[str, float]:
        """获取健康数据字典"""
        return {
            "steps": self.steps,
            "running_distance": self.running_distance,
            "standing_hours": self.standing_hours,
            "exercise_minutes": self.exercise_minutes,
            "heart_rate_minutes": self.heart_rate_minutes,
            "sleep_hours": self.sleep_hours,
            "meditation_minutes": self.meditation_minutes,
            "stairs_count": self.stairs_count,
            "swimming_distance": self.swimming_distance
        }
    
    def get_merit_data(self) -> Dict[str, int]:
        """获取功德数据字典"""
        return {
            "running": self.running_merit,
            "walking": self.walking_merit,
            "standing": self.standing_merit,
            "exercise": self.exercise_merit,
            "heart_rate": self.heart_rate_merit,
            "sleep": self.sleep_merit,
            "meditation": self.meditation_merit,
            "stairs": self.stairs_merit,
            "swimming": self.swimming_merit
        }


@dataclass
class Achievement:
    """成就模型"""
    achievement_id: str
    name: str
    description: str
    requirement_type: str  # "total_merit", "category_merit", "daily_streak", etc.
    requirement_value: int
    icon_url: Optional[str] = None
    reward_merit: int = 0
    is_hidden: bool = False
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "requirement_type": self.requirement_type,
            "requirement_value": self.requirement_value,
            "icon_url": self.icon_url,
            "reward_merit": self.reward_merit,
            "is_hidden": self.is_hidden
        }


@dataclass
class UserAchievement:
    """用户成就关联"""
    user_id: str
    achievement_id: str
    achieved_at: datetime = field(default_factory=datetime.now)
    progress: float = 0.0  # 0.0-1.0，未达成时为进度，达成时为1.0
    is_achieved: bool = False
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "achieved_at": self.achieved_at.isoformat() if self.is_achieved else None,
            "progress": self.progress,
            "is_achieved": self.is_achieved
        }


@dataclass
class LeaderboardEntry:
    """排行榜条目"""
    rank: int
    user_id: str
    nickname: str
    avatar_url: Optional[str]
    merit_value: int
    level: MeritLevel
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "rank": self.rank,
            "user_id": self.user_id,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "merit_value": self.merit_value,
            "level": {
                "name": self.level.chinese_name,
                "level": self.level.level
            }
        }


class LeaderboardType(Enum):
    """排行榜类型"""
    DAILY = "daily"      # 日榜
    WEEKLY = "weekly"    # 周榜
    MONTHLY = "monthly"  # 月榜
    TOTAL = "total"      # 总榜
    FRIENDS = "friends"  # 好友榜


@dataclass
class MeritEvent:
    """功德事件记录"""
    event_id: str
    user_id: str
    event_type: str  # "health_data", "achievement", "daily_bonus", etc.
    category: Optional[str] = None
    merit_earned: int = 0
    description: str = ""
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "category": self.category,
            "merit_earned": self.merit_earned,
            "description": self.description,
            "metadata": json.dumps(self.metadata) if self.metadata else None,
            "created_at": self.created_at.isoformat()
        }


# 数据库模型（SQLAlchemy风格）
"""
# 示例SQLAlchemy模型定义
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    nickname = Column(String)
    avatar_url = Column(String)
    total_merit = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    
    # 各项功德
    running_merit = Column(Integer, default=0)
    walking_merit = Column(Integer, default=0)
    standing_merit = Column(Integer, default=0)
    exercise_merit = Column(Integer, default=0)
    heart_rate_merit = Column(Integer, default=0)
    sleep_merit = Column(Integer, default=0)
    meditation_merit = Column(Integer, default=0)
    stairs_merit = Column(Integer, default=0)
    swimming_merit = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
"""


# 工厂函数
class ModelFactory:
    """模型工厂"""
    
    @staticmethod
    def create_user(user_id: str, nickname: str, avatar_url: str = None) -> User:
        """创建用户"""
        return User(
            user_id=user_id,
            nickname=nickname,
            avatar_url=avatar_url
        )
    
    @staticmethod
    def create_daily_record(user_id: str, record_date: date = None) -> DailyRecord:
        """创建每日记录"""
        from uuid import uuid4
        
        if record_date is None:
            record_date = date.today()
        
        return DailyRecord(
            record_id=str(uuid4()),
            user_id=user_id,
            record_date=record_date
        )
    
    @staticmethod
    def create_merit_event(user_id: str, event_type: str, merit_earned: int, 
                          category: str = None, description: str = "") -> MeritEvent:
        """创建功德事件"""
        from uuid import uuid4
        
        return MeritEvent(
            event_id=str(uuid4()),
            user_id=user_id,
            event_type=event_type,
            category=category,
            merit_earned=merit_earned,
            description=description
        )


if __name__ == "__main__":
    # 演示数据模型使用
    print("=== 数据模型演示 ===")
    
    # 创建用户
    user = ModelFactory.create_user("user_001", "修行者张三", "https://example.com/avatar.jpg")
    user.total_merit = 1250000
    user.current_level = MeritLevel.from_merit(user.total_merit)
    
    print(f"\n用户信息:")
    print(f"  ID: {user.user_id}")
    print(f"  昵称: {user.nickname}")
    print(f"  总功德: {user.total_merit:,}")
    print(f"  当前等级: {user.current_level.chinese_name} (Lv.{user.current_level.level})")
    print(f"  等级进度: {user.current_level.progress(user.total_merit):.1%}")
    
    # 创建每日记录
    daily = ModelFactory.create_daily_record("user_001")
    daily.steps = 8500
    daily.running_distance = 3.2
    daily.sleep_hours = 7.5
    daily.exercise_minutes = 45
    
    print(f"\n每日记录:")
    print(f"  日期: {daily.record_date}")
    print(f"  步数: {daily.steps}")
    print(f"  跑步: {daily.running_distance}km")
    print(f"  睡眠: {daily.sleep_hours}小时")
    print(f"  锻炼: {daily.exercise_minutes}分钟")
    
    # 转换为字典
    print(f"\n用户字典表示:")
    user_dict = user.to_dict()
    print(f"  等级: {user_dict['current_level']['name']}")
    print(f"  各项功德: {json.dumps(user_dict['category_merits'], indent=4, ensure_ascii=False)}")