#!/usr/bin/env python3
"""
数据库管理模块
使用SQLite + SQLAlchemy进行数据存储
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "merit_health.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # 启用外键约束
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # 创建用户表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                avatar_url TEXT,
                total_merit INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                current_level_name TEXT DEFAULT '凡夫俗子',
                
                -- 各项功德
                running_merit INTEGER DEFAULT 0,
                walking_merit INTEGER DEFAULT 0,
                standing_merit INTEGER DEFAULT 0,
                exercise_merit INTEGER DEFAULT 0,
                heart_rate_merit INTEGER DEFAULT 0,
                sleep_merit INTEGER DEFAULT 0,
                meditation_merit INTEGER DEFAULT 0,
                stairs_merit INTEGER DEFAULT 0,
                swimming_merit INTEGER DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建每日记录表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_records (
                record_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                record_date DATE NOT NULL,
                
                -- 健康数据
                steps INTEGER DEFAULT 0,
                running_distance REAL DEFAULT 0.0,
                standing_hours REAL DEFAULT 0.0,
                exercise_minutes INTEGER DEFAULT 0,
                heart_rate_minutes INTEGER DEFAULT 0,
                sleep_hours REAL DEFAULT 0.0,
                meditation_minutes INTEGER DEFAULT 0,
                stairs_count INTEGER DEFAULT 0,
                swimming_distance REAL DEFAULT 0.0,
                
                -- 功德数据
                total_merit INTEGER DEFAULT 0,
                running_merit INTEGER DEFAULT 0,
                walking_merit INTEGER DEFAULT 0,
                standing_merit INTEGER DEFAULT 0,
                exercise_merit INTEGER DEFAULT 0,
                heart_rate_merit INTEGER DEFAULT 0,
                sleep_merit INTEGER DEFAULT 0,
                meditation_merit INTEGER DEFAULT 0,
                stairs_merit INTEGER DEFAULT 0,
                swimming_merit INTEGER DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(user_id, record_date),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # 创建成就表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                requirement_type TEXT NOT NULL,
                requirement_value INTEGER NOT NULL,
                icon_url TEXT,
                reward_merit INTEGER DEFAULT 0,
                is_hidden BOOLEAN DEFAULT FALSE,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建用户成就表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                achieved_at TIMESTAMP,
                progress REAL DEFAULT 0.0,
                is_achieved BOOLEAN DEFAULT FALSE,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id)
            )
        """)
        
        # 创建功德事件表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS merit_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                category TEXT,
                merit_earned INTEGER DEFAULT 0,
                description TEXT,
                metadata TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # 创建索引以提高查询性能
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_records_user_date ON daily_records(user_id, record_date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_records_date ON daily_records(record_date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_merit_events_user ON merit_events(user_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_merit_events_created ON merit_events(created_at)")
        
        self.conn.commit()
        logger.info(f"数据库初始化完成: {self.db_path}")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    # ========== 用户操作 ==========
    
    def create_user(self, user_id: str, nickname: str, avatar_url: str = None) -> bool:
        """
        创建用户
        
        Args:
            user_id: 用户ID
            nickname: 昵称
            avatar_url: 头像URL
            
        Returns:
            bool: 是否成功
        """
        try:
            self.cursor.execute("""
                INSERT INTO users (user_id, nickname, avatar_url)
                VALUES (?, ?, ?)
            """, (user_id, nickname, avatar_url))
            self.conn.commit()
            logger.info(f"用户创建成功: {nickname} ({user_id})")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"用户已存在: {user_id}")
            return False
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 用户信息字典
        """
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = self.cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def update_user_merit(self, user_id: str, category: str, merit: int) -> bool:
        """
        更新用户功德
        
        Args:
            user_id: 用户ID
            category: 功德类别
            merit: 功德值
            
        Returns:
            bool: 是否成功
        """
        try:
            # 构建SQL更新语句
            category_column = f"{category}_merit"
            
            # 首先检查用户是否存在
            user = self.get_user(user_id)
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                return False
            
            # 更新对应类别的功德和总功德
            self.cursor.execute(f"""
                UPDATE users 
                SET {category_column} = {category_column} + ?, 
                    total_merit = total_merit + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (merit, merit, user_id))
            
            # 更新等级（这里简化处理，实际应该调用等级计算逻辑）
            # TODO: 实现等级更新逻辑
            
            self.conn.commit()
            logger.info(f"用户功德更新: {user_id} {category} +{merit}")
            return True
        except Exception as e:
            logger.error(f"更新用户功德失败: {e}")
            return False
    
    # ========== 每日记录操作 ==========
    
    def create_daily_record(self, record_id: str, user_id: str, record_date: date = None) -> bool:
        """
        创建每日记录
        
        Args:
            record_id: 记录ID
            user_id: 用户ID
            record_date: 记录日期
            
        Returns:
            bool: 是否成功
        """
        if record_date is None:
            record_date = date.today()
        
        try:
            self.cursor.execute("""
                INSERT INTO daily_records (record_id, user_id, record_date)
                VALUES (?, ?, ?)
            """, (record_id, user_id, record_date.isoformat()))
            self.conn.commit()
            logger.info(f"每日记录创建成功: {record_id} ({record_date})")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"每日记录已存在: {user_id} {record_date}")
            return False
        except Exception as e:
            logger.error(f"创建每日记录失败: {e}")
            return False
    
    def get_daily_record(self, user_id: str, record_date: date = None) -> Optional[Dict]:
        """
        获取每日记录
        
        Args:
            user_id: 用户ID
            record_date: 记录日期
            
        Returns:
            Optional[Dict]: 每日记录字典
        """
        if record_date is None:
            record_date = date.today()
        
        try:
            self.cursor.execute("""
                SELECT * FROM daily_records 
                WHERE user_id = ? AND record_date = ?
            """, (user_id, record_date.isoformat()))
            row = self.cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"获取每日记录失败: {e}")
            return None
    
    def update_daily_record(self, user_id: str, record_date: date, 
                           health_data: Dict[str, Any], merit_data: Dict[str, int]) -> bool:
        """
        更新每日记录
        
        Args:
            user_id: 用户ID
            record_date: 记录日期
            health_data: 健康数据字典
            merit_data: 功德数据字典
            
        Returns:
            bool: 是否成功
        """
        try:
            # 计算总功德
            total_merit = sum(merit_data.values())
            
            # 构建更新SQL
            update_fields = []
            update_values = []
            
            # 健康数据字段
            health_mapping = {
                "steps": "steps",
                "running_distance": "running_distance",
                "standing_hours": "standing_hours",
                "exercise_minutes": "exercise_minutes",
                "heart_rate_minutes": "heart_rate_minutes",
                "sleep_hours": "sleep_hours",
                "meditation_minutes": "meditation_minutes",
                "stairs_count": "stairs_count",
                "swimming_distance": "swimming_distance"
            }
            
            for key, db_key in health_mapping.items():
                if key in health_data:
                    update_fields.append(f"{db_key} = ?")
                    update_values.append(health_data[key])
            
            # 功德数据字段
            merit_mapping = {
                "running": "running_merit",
                "walking": "walking_merit",
                "standing": "standing_merit",
                "exercise": "exercise_merit",
                "heart_rate": "heart_rate_merit",
                "sleep": "sleep_merit",
                "meditation": "meditation_merit",
                "stairs": "stairs_merit",
                "swimming": "swimming_merit"
            }
            
            for key, db_key in merit_mapping.items():
                if key in merit_data:
                    update_fields.append(f"{db_key} = ?")
                    update_values.append(merit_data[key])
            
            # 添加总功德和更新时间
            update_fields.append("total_merit = ?")
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(total_merit)
            
            # 添加WHERE条件
            update_values.append(user_id)
            update_values.append(record_date.isoformat())
            
            # 执行更新
            update_sql = f"""
                UPDATE daily_records 
                SET {', '.join(update_fields)}
                WHERE user_id = ? AND record_date = ?
            """
            
            self.cursor.execute(update_sql, tuple(update_values))
            self.conn.commit()
            
            logger.info(f"每日记录更新成功: {user_id} {record_date}")
            return True
        except Exception as e:
            logger.error(f"更新每日记录失败: {e}")
            return False
    
    def get_user_daily_records(self, user_id: str, start_date: date, end_date: date) -> List[Dict]:
        """
        获取用户一段时间内的每日记录
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 每日记录列表
        """
        try:
            self.cursor.execute("""
                SELECT * FROM daily_records 
                WHERE user_id = ? AND record_date BETWEEN ? AND ?
                ORDER BY record_date DESC
            """, (user_id, start_date.isoformat(), end_date.isoformat()))
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"获取用户每日记录失败: {e}")
            return []
    
    # ========== 排行榜操作 ==========
    
    def get_leaderboard(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取总功德排行榜
        
        Args:
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            List[Dict]: 排行榜列表
        """
        try:
            self.cursor.execute("""
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY total_merit DESC) as rank,
                    user_id,
                    nickname,
                    avatar_url,
                    total_merit,
                    current_level,
                    current_level_name
                FROM users
                ORDER BY total_merit DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}")
            return []
    
    def get_daily_leaderboard(self, target_date: date = None, limit: int = 100) -> List[Dict]:
        """
        获取单日功德排行榜
        
        Args:
            target_date: 目标日期
            limit: 返回数量
            
        Returns:
            List[Dict]: 排行榜列表
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            self.cursor.execute("""
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY dr.total_merit DESC) as rank,
                    u.user_id,
                    u.nickname,
                    u.avatar_url,
                    dr.total_merit as daily_merit,
                    u.current_level,
                    u.current_level_name
                FROM daily_records dr
                JOIN users u ON dr.user_id = u.user_id
                WHERE dr.record_date = ?
                ORDER BY dr.total_merit DESC
                LIMIT ?
            """, (target_date.isoformat(), limit))
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"获取单日排行榜失败: {e}")
            return []
    
    # ========== 成就操作 ==========
    
    def create_achievement(self, achievement_id: str, name: str, description: str,
                          requirement_type: str, requirement_value: int,
                          icon_url: str = None, reward_merit: int = 0,
                          is_hidden: bool = False) -> bool:
        """
        创建成就
        
        Args:
            achievement_id: 成就ID
            name: 成就名称
            description: 成就描述
            requirement_type: 要求类型
            requirement_value: 要求值
            icon_url: 图标URL
            reward_merit: 奖励功德
            is_hidden: 是否隐藏
            
        Returns:
            bool: 是否成功
        """
        try:
            self.cursor.execute("""
                INSERT INTO achievements (
                    achievement_id, name, description, requirement_type, 
                    requirement_value, icon_url, reward_merit, is_hidden
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (achievement_id, name, description, requirement_type,
                  requirement_value, icon_url, reward_merit, is_hidden))
            
            self.conn.commit()
            logger.info(f"成就创建成功: {name} ({achievement_id})")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"成就已存在: {achievement_id}")
            return False
        except Exception as e:
            logger.error(f"创建成就失败: {e}")
            return False
    
    def get_achievements(self, include_hidden: bool = False) -> List[Dict]:
        """
        获取成就列表
        
        Args:
            include_hidden: 是否包含隐藏成就
            
        Returns:
            List[Dict]: 成就列表
        """
        try:
            if include_hidden:
                self.cursor.execute("SELECT * FROM achievements ORDER BY created_at")
            else:
                self.cursor.execute("SELECT * FROM achievements WHERE is_hidden = FALSE ORDER BY created_at")
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"获取成就列表失败: {e}")
            return []
    
    def update_user_achievement(self, user_id: str, achievement_id: str, 
                               progress: float = None, is_achieved: bool = False) -> bool:
        """
        更新用户成就进度
        
        Args:
            user_id: 用户ID
            achievement_id: 成就ID
            progress: 进度 (0.0-1.0)
            is_achieved: 是否已达成
            
        Returns:
            bool: 是否成功
        """
        try:
            if is_achieved:
                # 如果已达成，记录达成时间
                self.cursor.execute("""
                    INSERT OR REPLACE INTO user_achievements 
                    (user_id, achievement_id, achieved_at, progress, is_achieved, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP, 1.0, TRUE, CURRENT_TIMESTAMP)
                """, (user_id, achievement_id))
            else:
                # 更新进度
                self.cursor.execute("""
                    INSERT OR REPLACE INTO user_achievements 
                    (user_id, achievement_id, progress, is_achieved, updated_at)
                    VALUES (?, ?, ?, FALSE, CURRENT_TIMESTAMP)
                """, (user_id, achievement_id, progress))
            
            self.conn.commit()
            logger.info(f"用户成就更新: {user_id} {achievement_id} progress={progress}")
            return True
        except Exception as e:
            logger.error(f"更新用户成就失败: {e}")
            return False
    
    def get_user_achievements(self, user_id: str) -> List[Dict]:
        """
        获取用户成就
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 用户成就列表
        """
        try:
            self.cursor.execute("""
                SELECT 
                    a.*,
                    ua.progress,
                    ua.is_achieved,
                    ua.achieved_at
                FROM achievements a
                LEFT JOIN user_achievements ua ON a.achievement_id = ua.achievement_id 
                    AND ua.user_id = ?
                ORDER BY a.created_at
            """, (user_id,))
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"获取用户成就失败: {e}")
            return []
    
    # ========== 功德事件操作 ==========
    
    def create_merit_event(self, event_id: str, user_id: str, event_type: str,
                          merit_earned: int, category: str = None,
                          description: str = "", metadata: Dict = None) -> bool:
        """
        创建功德事件
        
        Args:
            event_id: 事件ID
            user_id: 用户ID
            event_type: 事件类型
            merit_earned: 获得的功德
            category: 功德类别
            description: 事件描述
            metadata: 元数据
            
        Returns:
            bool: 是否成功
        """
        try:
            metadata_str = json.dumps(metadata) if metadata else None
            
            self.cursor.execute("""
                INSERT INTO merit_events 
                (event_id, user_id, event_type, category, merit_earned, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event_id, user_id, event_type, category, merit_earned, description, metadata_str))
            
            self.conn.commit()
            logger.info(f"功德事件创建: {event_type} +{merit_earned}功德")
            return True
        except Exception as e:
            logger.error(f"创建功德事件失败: {e}")
            return False
    
    def get_user_merit_events(self, user_id: str, limit: int = 100, 
                             start_date: date = None, end_date: date = None) -> List[Dict]:
        """
        获取用户功德事件
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 功德事件列表
        """
        try:
            query = """
                SELECT * FROM merit_events 
                WHERE user_id = ?
            """
            params = [user_id]
            
            if start_date and end_date:
                query += " AND DATE(created_at) BETWEEN ? AND ?"
                params.extend([start_date.isoformat(), end_date.isoformat()])
            elif start_date:
                query += " AND DATE(created_at) >= ?"
                params.append(start_date.isoformat())
            elif end_date:
                query += " AND DATE(created_at) <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            self.cursor.execute(query, tuple(params))
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            # 解析metadata字段
            result = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                if row_dict.get('metadata'):
                    try:
                        row_dict['metadata'] = json.loads(row_dict['metadata'])
                    except:
                        row_dict['metadata'] = {}
                result.append(row_dict)
            
            return result
        except Exception as e:
            logger.error(f"获取用户功德事件失败: {e}")
            return []
    
    # ========== 统计操作 ==========
    
    def get_user_statistics(self, user_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 统计信息
        """
        try:
            # 获取总功德和等级
            self.cursor.execute("""
                SELECT total_merit, current_level, current_level_name
                FROM users WHERE user_id = ?
            """, (user_id,))
            
            user_row = self.cursor.fetchone()
            if not user_row:
                return {}
            
            user_info = {
                "total_merit": user_row[0],
                "current_level": user_row[1],
                "current_level_name": user_row[2]
            }
            
            # 获取每日记录统计
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as days_active,
                    SUM(total_merit) as period_merit,
                    AVG(total_merit) as avg_daily_merit,
                    SUM(steps) as total_steps,
                    SUM(running_distance) as total_running_km,
                    SUM(sleep_hours) as total_sleep_hours,
                    SUM(exercise_minutes) as total_exercise_minutes
                FROM daily_records
                WHERE user_id = ? AND record_date BETWEEN ? AND ?
            """, (user_id, start_date.isoformat(), end_date.isoformat()))
            
            stats_row = self.cursor.fetchone()
            stats_info = {
                "days_active": stats_row[0] or 0,
                "period_merit": stats_row[1] or 0,
                "avg_daily_merit": float(stats_row[2] or 0),
                "total_steps": stats_row[3] or 0,
                "total_running_km": float(stats_row[4] or 0),
                "total_sleep_hours": float(stats_row[5] or 0),
                "total_exercise_minutes": stats_row[6] or 0
            }
            
            # 获取最佳单日功德
            self.cursor.execute("""
                SELECT record_date, total_merit
                FROM daily_records
                WHERE user_id = ? AND record_date BETWEEN ? AND ?
                ORDER BY total_merit DESC
                LIMIT 1
            """, (user_id, start_date.isoformat(), end_date.isoformat()))
            
            best_day_row = self.cursor.fetchone()
            best_day_info = {
                "date": best_day_row[0] if best_day_row else None,
                "merit": best_day_row[1] if best_day_row else 0
            }
            
            # 合并结果
            return {
                "user_info": user_info,
                "statistics": stats_info,
                "best_day": best_day_info,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {}


# 使用示例
if __name__ == "__main__":
    print("=== 数据库管理模块演示 ===")
    
    # 创建数据库管理器
    db = DatabaseManager(":memory:")  # 使用内存数据库进行测试
    
    try:
        # 创建用户
        db.create_user("test_user_001", "测试用户", "https://example.com/avatar.jpg")
        
        # 获取用户
        user = db.get_user("test_user_001")
        print(f"\n创建的用户: {user['nickname']} (ID: {user['user_id']})")
        
        # 更新用户功德
        db.update_user_merit("test_user_001", "running", 5000)
        
        # 再次获取用户查看更新
        user_updated = db.get_user("test_user_001")
        print(f"跑步功德: {user_updated['running_merit']}")
        print(f"总功德: {user_updated['total_merit']}")
        
        # 创建每日记录
        from uuid import uuid4
        record_id = str(uuid4())
        db.create_daily_record(record_id, "test_user_001")
        
        # 更新每日记录
        health_data = {
            "steps": 8500,
            "running_distance": 3.2,
            "sleep_hours": 7.5
        }
        
        merit_data = {
            "running": 3200,  # 3.2km * 1000
            "walking": 850,   # 8500步 / 100 * 10
            "sleep": 3750     # 7.5小时 * 500
        }
        
        db.update_daily_record("test_user_001", date.today(), health_data, merit_data)
        
        # 获取每日记录
        daily = db.get_daily_record("test_user_001")
        if daily:
            print(f"\n今日记录:")
            print(f"  步数: {daily['steps']}")
            print(f"  跑步距离: {daily['running_distance']}km")
            print(f"  睡眠: {daily['sleep_hours']}小时")
            print(f"  今日功德: {daily['total_merit']}")
        
        # 创建功德事件
        event_id = str(uuid4())
        db.create_merit_event(
            event_id=event_id,
            user_id="test_user_001",
            event_type="health_data",
            category="running",
            merit_earned=3200,
            description="跑步3.2公里"
        )
        
        # 获取排行榜
        leaderboard = db.get_leaderboard(limit=10)
        print(f"\n排行榜 (共{len(leaderboard)}人):")
        for entry in leaderboard:
            print(f"  第{entry['rank']}名: {entry['nickname']} - {entry['total_merit']}功德")
        
        # 关闭数据库
        db.close()
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
        db.close()