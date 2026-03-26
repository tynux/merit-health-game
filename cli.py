#!/usr/bin/env python3
"""
功德健康游戏命令行工具
提供命令行界面进行数据管理和测试
"""

import argparse
import sys
import json
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.merit_service import MeritService
from core.merit_calculator import HealthCategory, HealthData
from data.database import DatabaseManager


class MeritCLI:
    """功德健康游戏命令行界面"""
    
    def __init__(self, db_path: str = "merit_health.db"):
        """初始化CLI"""
        self.db_path = db_path
        self.service = MeritService(db_path)
        
    def run(self):
        """运行命令行界面"""
        parser = argparse.ArgumentParser(
            description="功德健康游戏命令行工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  %(prog)s user register --user-id user001 --nickname "张三"
  %(prog)s health submit --user-id user001 --category running --value 5.2
  %(prog)s leaderboard get --type daily --limit 10
  %(prog)s report get --user-id user001 --period weekly
            """
        )
        
        # 子命令
        subparsers = parser.add_subparsers(dest="command", help="命令")
        
        # ===== 用户管理命令 =====
        user_parser = subparsers.add_parser("user", help="用户管理")
        user_subparsers = user_parser.add_subparsers(dest="user_command")
        
        # 注册用户
        register_parser = user_subparsers.add_parser("register", help="注册新用户")
        register_parser.add_argument("--user-id", required=True, help="用户ID")
        register_parser.add_argument("--nickname", required=True, help="昵称")
        register_parser.add_argument("--avatar-url", help="头像URL")
        
        # 查看用户资料
        profile_parser = user_subparsers.add_parser("profile", help="查看用户资料")
        profile_parser.add_argument("--user-id", required=True, help="用户ID")
        
        # ===== 健康数据命令 =====
        health_parser = subparsers.add_parser("health", help="健康数据管理")
        health_subparsers = health_parser.add_subparsers(dest="health_command")
        
        # 提交健康数据
        submit_parser = health_subparsers.add_parser("submit", help="提交健康数据")
        submit_parser.add_argument("--user-id", required=True, help="用户ID")
        submit_parser.add_argument("--category", required=True, 
                                 choices=[c.value for c in HealthCategory],
                                 help="健康数据类别")
        submit_parser.add_argument("--value", type=float, required=True, help="数值")
        submit_parser.add_argument("--unit", help="单位")
        
        # 批量提交
        batch_parser = health_subparsers.add_parser("batch", help="批量提交健康数据")
        batch_parser.add_argument("--user-id", required=True, help="用户ID")
        batch_parser.add_argument("--file", help="JSON文件路径")
        batch_parser.add_argument("--data", help="JSON格式数据")
        
        # ===== 排行榜命令 =====
        leaderboard_parser = subparsers.add_parser("leaderboard", help="排行榜")
        leaderboard_subparsers = leaderboard_parser.add_subparsers(dest="leaderboard_command")
        
        # 获取排行榜
        get_lb_parser = leaderboard_subparsers.add_parser("get", help="获取排行榜")
        get_lb_parser.add_argument("--type", default="total", 
                                  choices=["total", "daily", "weekly", "monthly"],
                                  help="排行榜类型")
        get_lb_parser.add_argument("--limit", type=int, default=10, help="返回数量")
        
        # 获取用户排名
        rank_parser = leaderboard_subparsers.add_parser("rank", help="获取用户排名")
        rank_parser.add_argument("--user-id", required=True, help="用户ID")
        rank_parser.add_argument("--type", default="total", 
                                choices=["total", "daily", "weekly", "monthly"],
                                help="排行榜类型")
        
        # ===== 报告命令 =====
        report_parser = subparsers.add_parser("report", help="统计报告")
        report_subparsers = report_parser.add_subparsers(dest="report_command")
        
        # 获取报告
        get_report_parser = report_subparsers.add_parser("get", help="获取报告")
        get_report_parser.add_argument("--user-id", required=True, help="用户ID")
        get_report_parser.add_argument("--period", default="weekly",
                                      choices=["daily", "weekly", "monthly", "yearly"],
                                      help="报告周期")
        
        # ===== 数据库命令 =====
        db_parser = subparsers.add_parser("db", help="数据库管理")
        db_subparsers = db_parser.add_subparsers(dest="db_command")
        
        # 初始化数据库
        db_subparsers.add_parser("init", help="初始化数据库")
        
        # 查看数据库状态
        db_subparsers.add_parser("status", help="查看数据库状态")
        
        # ===== 系统命令 =====
        system_parser = subparsers.add_parser("system", help="系统管理")
        system_subparsers = system_parser.add_subparsers(dest="system_command")
        
        # 系统信息
        system_subparsers.add_parser("info", help="系统信息")
        
        # 重置系统
        reset_parser = system_subparsers.add_parser("reset", help="重置系统（清空数据）")
        reset_parser.add_argument("--confirm", action="store_true", 
                                 help="确认重置")
        
        # ===== 演示命令 =====
        demo_parser = subparsers.add_parser("demo", help="演示功能")
        demo_subparsers = demo_parser.add_subparsers(dest="demo_command")
        
        # 运行完整演示
        demo_subparsers.add_parser("run", help="运行完整演示")
        
        # 创建测试数据
        testdata_parser = demo_subparsers.add_parser("testdata", help="创建测试数据")
        testdata_parser.add_argument("--users", type=int, default=5, help="用户数量")
        testdata_parser.add_argument("--days", type=int, default=7, help="数据天数")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # 执行命令
        try:
            if args.command == "user":
                self.handle_user_command(args)
            elif args.command == "health":
                self.handle_health_command(args)
            elif args.command == "leaderboard":
                self.handle_leaderboard_command(args)
            elif args.command == "report":
                self.handle_report_command(args)
            elif args.command == "db":
                self.handle_db_command(args)
            elif args.command == "system":
                self.handle_system_command(args)
            elif args.command == "demo":
                self.handle_demo_command(args)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            self.service.close()
    
    # ===== 命令处理器 =====
    
    def handle_user_command(self, args):
        """处理用户命令"""
        if args.user_command == "register":
            success = self.service.register_user(
                args.user_id, args.nickname, args.avatar_url
            )
            if success:
                print(f"✅ 用户注册成功: {args.nickname} ({args.user_id})")
            else:
                print(f"❌ 用户注册失败，用户ID可能已存在")
        
        elif args.user_command == "profile":
            profile = self.service.get_user_profile(args.user_id)
            if profile:
                self.print_user_profile(profile)
            else:
                print(f"❌ 用户不存在: {args.user_id}")
    
    def handle_health_command(self, args):
        """处理健康数据命令"""
        if args.health_command == "submit":
            # 确定单位
            unit = args.unit
            if not unit:
                # 根据类别推断单位
                category_map = {
                    "running": "km",
                    "walking": "steps",
                    "standing": "hours",
                    "exercise": "minutes",
                    "heart_rate": "minutes",
                    "sleep": "hours",
                    "meditation": "minutes",
                    "stairs": "count",
                    "swimming": "meters"
                }
                unit = category_map.get(args.category, "")
            
            # 创建健康数据
            try:
                category = HealthCategory(args.category)
                
                if category == HealthCategory.RUNNING:
                    health_data = HealthData.create_running(args.value)
                elif category == HealthCategory.WALKING:
                    health_data = HealthData.create_walking(int(args.value))
                elif category == HealthCategory.SLEEP:
                    health_data = HealthData.create_sleep(args.value)
                elif category == HealthCategory.EXERCISE:
                    health_data = HealthData.create_exercise(int(args.value))
                elif category == HealthCategory.STANDING:
                    health_data = HealthData.create_standing(args.value)
                else:
                    health_data = HealthData(
                        category=category,
                        value=args.value,
                        unit=unit,
                        timestamp=datetime.now()
                    )
                
                # 提交数据
                result = self.service.process_health_data(args.user_id, [health_data])
                
                if result["success"]:
                    print(f"✅ 健康数据提交成功")
                    print(f"   获得功德: {result['total_merit_earned']:,}")
                    
                    for item in result["results"]:
                        print(f"   {item['category']}: {item['merit_points']:,}功德 ({item['level_name']})")
                else:
                    print(f"❌ 提交失败: {result.get('error', '未知错误')}")
                    
            except ValueError as e:
                print(f"❌ 无效的健康数据类别: {args.category}")
        
        elif args.health_command == "batch":
            data = {}
            
            if args.file:
                # 从文件读取
                try:
                    with open(args.file, 'r') as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"❌ 读取文件失败: {e}")
                    return
            elif args.data:
                # 从参数读取
                try:
                    data = json.loads(args.data)
                except Exception as e:
                    print(f"❌ 解析JSON失败: {e}")
                    return
            else:
                print("❌ 必须提供 --file 或 --data 参数")
                return
            
            # 处理数据
            result = self.service.process_health_data_dict(args.user_id, data)
            
            if result["success"]:
                print(f"✅ 批量提交成功")
                print(f"   获得功德: {result['total_merit_earned']:,}")
                print(f"   今日总功德: {result['daily_summary']['total_merit']:,}")
            else:
                print(f"❌ 提交失败: {result.get('error', '未知错误')}")
    
    def handle_leaderboard_command(self, args):
        """处理排行榜命令"""
        if args.leaderboard_command == "get":
            leaderboard = self.service.get_leaderboard(args.type, args.limit)
            
            print(f"🏆 {args.type}排行榜 (前{len(leaderboard)}名):")
            print("-" * 80)
            
            for entry in leaderboard:
                merit_key = "total_merit" if args.type == "total" else "daily_merit"
                merit_value = entry.get(merit_key, 0)
                
                print(f"#{entry['rank']:3d} {entry['nickname'][:20]:20s} "
                      f"{merit_value:12,d}功德 "
                      f"({entry.get('current_level_name', '未知')})")
            
            print("-" * 80)
        
        elif args.leaderboard_command == "rank":
            rank_info = self.service.get_user_rank(args.user_id, args.type)
            
            if rank_info:
                print(f"📊 用户排名信息 ({args.type}榜):")
                print(f"   排名: 第{rank_info['rank']}名")
                print(f"   总人数: {rank_info['total_users']}人")
                print(f"   排名百分比: 前{rank_info['percentile']:.1f}%")
                print(f"   功德值: {rank_info['merit_value']:,}")
                print(f"   等级: {rank_info['level']}")
            else:
                print(f"ℹ️  用户未上榜: {args.user_id}")
    
    def handle_report_command(self, args):
        """处理报告命令"""
        if args.report_command == "get":
            report = self.service.get_user_report(args.user_id, args.period)
            
            if not report.get("profile_summary"):
                print(f"❌ 用户不存在或没有数据: {args.user_id}")
                return
            
            profile = report["profile_summary"]
            stats = report["statistics"]
            
            print(f"📈 {args.period}报告 - {profile['nickname']}")
            print("=" * 60)
            
            # 基本信息
            print(f"👤 用户信息:")
            print(f"   总功德: {profile['total_merit']:,}")
            print(f"   等级: {profile['total_level']}")
            print(f"   连续天数: {profile['streak_days']}天")
            
            print()
            
            # 统计信息
            print(f"📊 统计信息 ({report['period']['days']}天):")
            print(f"   活跃天数: {stats.get('days_active', 0)}天")
            print(f"   总功德: {stats.get('period_merit', 0):,}")
            print(f"   平均每日: {stats.get('avg_daily_merit', 0):.0f}功德")
            print(f"   总步数: {stats.get('total_steps', 0):,}")
            print(f"   总跑步: {stats.get('total_running_km', 0):.1f}km")
            print(f"   总睡眠: {stats.get('total_sleep_hours', 0):.1f}小时")
            
            # 最佳单日
            best_day = report.get("best_day", {})
            if best_day.get("date"):
                print(f"   最佳单日: {best_day['date']} ({best_day['merit']:,}功德)")
            
            print()
            
            # 成就进度
            achievements = report.get("achievements_progress", {})
            if achievements.get("total", 0) > 0:
                achieved = achievements.get("achieved", 0)
                total = achievements.get("total", 1)
                progress = achieved / total * 100
                
                print(f"🏅 成就进度: {achieved}/{total} ({progress:.1f}%)")
    
    def handle_db_command(self, args):
        """处理数据库命令"""
        if args.db_command == "init":
            # 重新初始化数据库
            db = DatabaseManager(self.db_path)
            db.close()
            print(f"✅ 数据库初始化完成: {self.db_path}")
        
        elif args.db_command == "status":
            db = DatabaseManager(self.db_path)
            
            # 查询各表记录数
            tables = ["users", "daily_records", "achievements", "user_achievements", "merit_events"]
            
            print("📊 数据库状态:")
            print("-" * 40)
            
            for table in tables:
                try:
                    db.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = db.cursor.fetchone()[0]
                    print(f"{table:20s}: {count:6d} 条记录")
                except:
                    print(f"{table:20s}: 表不存在")
            
            db.close()
    
    def handle_system_command(self, args):
        """处理系统命令"""
        if args.system_command == "info":
            print("🤖 系统信息:")
            print(f"   项目名称: 功德健康游戏")
            print(f"   数据库路径: {self.db_path}")
            print(f"   健康数据类别: 9种")
            print(f"   功德等级: 单项9重境界，总功德10层天梯")
            print(f"   成就系统: 已内置{len(self.service.achievements)}个成就")
        
        elif args.system_command == "reset":
            if not args.confirm:
                print("⚠️  警告: 此操作将清空所有数据!")
                print("请使用 --confirm 参数确认重置")
                return
            
            # 关闭现有连接
            self.service.close()
            
            # 删除数据库文件
            import os
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print(f"✅ 数据库文件已删除: {self.db_path}")
            
            # 重新初始化
            self.service = MeritService(self.db_path)
            print("✅ 系统已重置")
    
    def handle_demo_command(self, args):
        """处理演示命令"""
        if args.demo_command == "run":
            self.run_demo()
        
        elif args.demo_command == "testdata":
            self.create_test_data(args.users, args.days)
    
    # ===== 工具方法 =====
    
    def print_user_profile(self, profile: Dict):
        """打印用户资料"""
        user_info = profile["user_info"]
        merit_info = profile["merit_info"]
        daily_info = profile["daily_info"]
        achievements = profile["achievements"]
        
        print(f"👤 用户资料: {user_info['nickname']}")
        print("=" * 60)
        
        # 基本信息
        print(f"📝 基本信息:")
        print(f"   用户ID: {user_info['user_id']}")
        print(f"   注册时间: {user_info['created_at']}")
        
        print()
        
        # 功德信息
        total_level = merit_info["total_level"]
        print(f"💰 功德信息:")
        print(f"   总功德: {merit_info['total_merit']:,}")
        print(f"   总等级: {total_level['name']} (Lv.{total_level['level']})")
        print(f"   等级进度: {total_level['progress']:.1%}")
        print(f"   距离下一等级: {total_level['next_level_merit']:,}功德")
        
        print()
        
        # 单项功德
        print(f"🎯 单项功德:")
        category_merits = merit_info["category_merits"]
        for category, merit in category_merits.items():
            if merit > 0:
                level_info = merit_info["category_levels"].get(category, {})
                level_name = level_info.get("name", "未入门")
                print(f"   {category}: {merit:10,d}功德 ({level_name})")
        
        print()
        
        # 每日信息
        print(f"📅 每日信息:")
        print(f"   连续活跃: {daily_info['streak_days']}天")
        
        today = daily_info.get("today")
        if today:
            print(f"   今日功德: {today.get('total_merit', 0):,}")
            print(f"   今日步数: {today.get('steps', 0):,}")
        
        print()
        
        # 成就信息
        print(f"🏅 成就信息:")
        print(f"   总成就数: {achievements['total']}")
        print(f"   已达成: {achievements['achieved']}")
        print(f"   进度: {achievements['achieved']}/{achievements['total']}")
    
    def run_demo(self):
        """运行完整演示"""
        print("🚀 开始功德健康游戏演示")
        print("=" * 60)
        
        # 1. 注册用户
        print("\n1. 注册用户...")
        success = self.service.register_user("demo_user", "演示用户", "https://example.com/avatar.jpg")
        if success:
            print("   ✅ 用户注册成功")
        else:
            print("   ℹ️  用户已存在，继续演示...")
        
        # 2. 提交健康数据
        print("\n2. 提交健康数据...")
        
        health_data = [
            HealthData.create_running(5.2),      # 跑步5.2公里
            HealthData.create_walking(12500),    # 步行12500步
            HealthData.create_sleep(7.8),        # 睡眠7.8小时
            HealthData.create_exercise(60),      # 锻炼60分钟
        ]
        
        result = self.service.process_health_data("demo_user", health_data)
        
        if result["success"]:
            print(f"   ✅ 获得功德: {result['total_merit_earned']:,}")
            for item in result["results"]:
                print(f"      {item['category']}: {item['merit_points']:,}功德")
        else:
            print(f"   ❌ 提交失败")
        
        # 3. 查看用户资料
        print("\n3. 查看用户资料...")
        profile = self.service.get_user_profile("demo_user")
        if profile:
            print(f"   ✅ 总功德: {profile['merit_info']['total_merit']:,}")
            print(f"   ✅ 总等级: {profile['merit_info']['total_level']['name']}")
        else:
            print("   ❌ 获取资料失败")
        
        # 4. 查看排行榜
        print("\n4. 查看排行榜...")
        leaderboard = self.service.get_leaderboard("total", limit=3)
        if leaderboard:
            print(f"   🏆 排行榜 (前{len(leaderboard)}名):")
            for entry in leaderboard:
                print(f"      第{entry['rank']}名: {entry['nickname']} - {entry['total_merit']:,}功德")
        else:
            print("   ℹ️  排行榜为空")
        
        # 5. 获取周报
        print("\n5. 获取周报...")
        report = self.service.get_user_report("demo_user", "weekly")
        if report.get("profile_summary"):
            stats = report["statistics"]
            print(f"   📈 本周统计:")
            print(f"      活跃天数: {stats.get('days_active', 0)}天")
            print(f"      总功德: {stats.get('period_merit', 0):,}")
            print(f"      平均每日: {stats.get('avg_daily_merit', 0):.0f}功德")
        
        print("\n" + "=" * 60)
        print("🎉 演示完成!")
    
    def create_test_data(self, user_count: int, days: int):
        """创建测试数据"""
        import random
        from datetime import date, timedelta
        
        print(f"📊 创建测试数据: {user_count}个用户，{days}天数据")
        
        # 创建用户
        users = []
        for i in range(user_count):
            user_id = f"test_user_{i+1:03d}"
            nickname = f"测试用户{i+1}"
            
            success = self.service.register_user(user_id, nickname)
            if success:
                users.append(user_id)
        
        print(f"   创建了 {len(users)} 个用户")
        
        # 为每个用户创建多天数据
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        total_records = 0
        
        for user_id in users:
            current_date = start_date
            
            while current_date <= end_date:
                # 随机生成健康数据
                health_data_dict = {}
                
                # 每天有70%的概率有数据
                if random.random() < 0.7:
                    # 步数: 2000-15000
                    if random.random() < 0.8:
                        health_data_dict["walking"] = random.randint(2000, 15000)
                    
                    # 跑步: 0-10公里
                    if random.random() < 0.4:
                        health_data_dict["running"] = round(random.uniform(0.5, 10.0), 1)
                    
                    # 睡眠: 4-9小时
                    if random.random() < 0.9:
                        health_data_dict["sleep"] = round(random.uniform(4.0, 9.0), 1)
                    
                    # 锻炼: 0-90分钟
                    if random.random() < 0.3:
                        health_data_dict["exercise"] = random.randint(10, 90)
                    
                    # 提交数据
                    if health_data_dict:
                        # 注意：这里简化处理，实际应该按日期处理
                        self.service.process_health_data_dict(user_id, health_data_dict)
                        total_records += 1
                
                current_date += timedelta(days=1)
        
        print(f"   创建了 {total_records} 条健康记录")
        print("✅ 测试数据创建完成")


def main():
    """主函数"""
    cli = MeritCLI()
    cli.run()


if __name__ == "__main__":
    main()