#!/usr/bin/env python3
"""
功德健康游戏 - 启动脚本
启动完整的Web应用，包含API和用户界面
"""

import sys
import os
import subprocess
import webbrowser
from datetime import datetime

def check_dependencies():
    """检查依赖"""
    required_packages = ['fastapi', 'uvicorn', 'pydantic', 'jinja2']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    return missing

def install_dependencies(missing_packages):
    """安装缺失的依赖"""
    if not missing_packages:
        return True
    
    print(f"安装缺失的依赖: {', '.join(missing_packages)}")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_demo_data():
    """创建演示数据"""
    print("创建演示数据...")
    
    # 导入服务
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from core.merit_service import MeritService
        
        # 初始化服务
        service = MeritService("merit_health.db")
        
        # 注册演示用户
        service.register_user("demo_user", "修行者", "https://example.com/avatar.jpg")
        
        # 模拟一些数据
        import random
        from datetime import date, timedelta
        
        user_id = "demo_user"
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # 最近7天
        
        current_date = start_date
        days_with_data = 0
        
        print(f"生成最近7天的演示数据...")
        
        while current_date <= end_date:
            # 每天有80%的概率有数据
            if random.random() < 0.8:
                # 生成随机健康数据
                health_data = {}
                
                # 步数: 3000-12000
                health_data["walking"] = random.randint(3000, 12000)
                
                # 跑步: 0-8公里 (40%概率)
                if random.random() < 0.4:
                    health_data["running"] = round(random.uniform(0.5, 8.0), 1)
                
                # 睡眠: 5-9小时
                health_data["sleep"] = round(random.uniform(5.0, 9.0), 1)
                
                # 锻炼: 0-60分钟 (30%概率)
                if random.random() < 0.3:
                    health_data["exercise"] = random.randint(15, 60)
                
                # 站立: 6-12小时
                health_data["standing"] = round(random.uniform(6.0, 12.0), 1)
                
                # 提交数据
                service.process_health_data_dict(user_id, health_data)
                days_with_data += 1
            
            current_date += timedelta(days=1)
        
        service.close()
        print(f"✅ 演示数据创建完成: {days_with_data}天数据")
        return True
        
    except Exception as e:
        print(f"❌ 创建演示数据失败: {e}")
        return False

def start_server(host='127.0.0.1', port=8000, open_browser=True):
    """启动服务器"""
    print(f"\n🚀 启动功德健康游戏服务器...")
    print(f"   地址: http://{host}:{port}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   演示用户: demo_user")
    print(f"   数据库: merit_health.db")
    
    # 构建启动命令
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'api.app_web:app',
        '--host', host,
        '--port', str(port),
        '--reload'
    ]
    
    print(f"\n启动命令: {' '.join(cmd)}")
    print("\n按 Ctrl+C 停止服务器\n")
    
    if open_browser:
        # 等待服务器启动，然后打开浏览器
        import threading
        import time
        
        def open_browser_delayed():
            time.sleep(2)  # 等待服务器启动
            webbrowser.open(f'http://{host}:{port}')
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    # 启动服务器
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("""
    ========================================
      功德健康游戏 - 启动器
      版本: 1.0.0
      
      功能:
      - 健康数据功德化系统
      - 九重境界 + 十层天梯
      - 实时排行榜和成就
      - 现代化Web界面
    ========================================
    """)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"发现缺失的依赖: {', '.join(missing)}")
        if not install_dependencies(missing):
            print("\n❌ 请手动安装依赖:")
            print(f"   pip install {' '.join(missing)}")
            sys.exit(1)
    
    # 检查数据库和演示数据
    db_path = "merit_health.db"
    if not os.path.exists(db_path):
        print("数据库不存在，创建演示数据...")
        if not create_demo_data():
            print("❌ 无法创建演示数据，继续启动...")
    else:
        print("✅ 数据库已存在")
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='启动功德健康游戏服务器')
    parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--reset', action='store_true', help='重置数据库')
    
    args = parser.parse_args()
    
    # 重置数据库
    if args.reset:
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ 数据库已重置")
        create_demo_data()
    
    # 启动服务器
    start_server(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser
    )

if __name__ == '__main__':
    main()