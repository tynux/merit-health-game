#!/usr/bin/env python3
"""
基础测试用例 - 功德健康游戏
"""

import sys
import os
import pytest

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.merit_calculator import MeritCalculator, HealthData, HealthCategory


def test_merit_calculator_initialization():
    """测试功德计算器初始化"""
    calculator = MeritCalculator()
    assert calculator is not None
    assert hasattr(calculator, 'calculate_merit')
    assert hasattr(calculator, 'MERIT_RATES')


def test_health_category_enum():
    """测试健康类别枚举"""
    assert HealthCategory.RUNNING.value == 'running'
    assert HealthCategory.WALKING.value == 'walking'
    assert HealthCategory.SLEEP.value == 'sleep'
    
    # 测试所有类别都存在
    expected_categories = ['running', 'walking', 'standing', 'exercise', 
                          'heart_rate', 'sleep', 'meditation', 'stairs', 'swimming']
    
    for category in expected_categories:
        assert HealthCategory(category).value == category


def test_health_data_creation():
    """测试健康数据对象创建"""
    # 测试跑步数据
    running_data = HealthData.create_running(5.2)
    assert running_data.category == HealthCategory.RUNNING
    assert running_data.value == 5.2
    assert running_data.unit == 'km'
    
    # 测试步行数据
    walking_data = HealthData.create_walking(8500)
    assert walking_data.category == HealthCategory.WALKING
    assert walking_data.value == 8500
    assert walking_data.unit == 'steps'
    
    # 测试睡眠数据
    sleep_data = HealthData.create_sleep(7.5)
    assert sleep_data.category == HealthCategory.SLEEP
    assert sleep_data.value == 7.5
    assert sleep_data.unit == 'hours'


def test_basic_merit_calculation():
    """测试基础功德计算"""
    calculator = MeritCalculator()
    
    # 测试跑步功德计算
    running_data = HealthData.create_running(3.0)  # 3公里
    result = calculator.calculate_merit(running_data)
    assert result.merit_points == 3000  # 3公里 × 1000
    
    # 测试步行功德计算
    walking_data = HealthData.create_walking(10000)  # 10000步
    result = calculator.calculate_merit(walking_data)
    assert result.merit_points == 1000  # 10000步 ÷ 100 × 10


def test_category_levels():
    """测试类别等级计算"""
    calculator = MeritCalculator()
    
    # 测试不同功德值的等级
    test_cases = [
        (HealthCategory.RUNNING, 5000, 1),   # 5000功德 -> 等级1
        (HealthCategory.RUNNING, 50000, 2),  # 50000功德 -> 等级2
        (HealthCategory.WALKING, 1000, 1),   # 1000功德 -> 等级1
    ]
    
    for category, cumulative_merit, expected_level in test_cases:
        # 创建测试数据
        if category == HealthCategory.RUNNING:
            data = HealthData.create_running(1.0)
        elif category == HealthCategory.WALKING:
            data = HealthData.create_walking(100)
        else:
            continue
            
        result = calculator.calculate_merit(data, cumulative_merit)
        assert result.level_number == expected_level


if __name__ == '__main__':
    # 运行所有测试
    pytest.main([__file__, '-v'])