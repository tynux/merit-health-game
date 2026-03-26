// 功德健康游戏 - 前端应用

const API_BASE_URL = 'http://localhost:8000/api';
let currentUser = 'demo_user'; // 默认用户ID
let meritDistributionChart = null;
let meritHistoryChart = null;
let userBoostPercentage = 0; // 用户功德加成百分比

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initFormCalculations();
    
    // 根据URL或data-active-section属性确定初始活动部分
    const body = document.body;
    const activeSectionAttr = body.getAttribute('data-active-section');
    
    if (activeSectionAttr) {
        // 根据data-active-section属性激活对应的部分
        activateSection(activeSectionAttr);
    } else {
        // 默认加载仪表板数据
        loadDashboardData();
    }
    
    // 为演示目的，自动注册默认用户
    registerDemoUser();
});

// 初始化导航
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            activateSection(targetId);
        });
    });
}

// 激活指定部分
function activateSection(sectionId) {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    // 更新活动链接
    navLinks.forEach(link => {
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // 显示对应部分
    sections.forEach(section => {
        if (section.id === sectionId) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
    
    // 加载对应数据
    switch(sectionId) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'merit':
            loadMeritHistory();
            break;
        case 'leaderboard':
            loadLeaderboard();
            break;
        case 'achievements':
            loadAchievements();
            break;
        case 'submit':
            // 提交页面不需要加载特殊数据
            break;
    }
}

// 注册演示用户
async function registerDemoUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUser,
                nickname: '修行者',
                avatar_url: 'https://example.com/avatar.jpg'
            })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('演示用户注册成功');
        }
    } catch (error) {
        console.log('用户可能已存在或API未启动');
    }
}

// 加载仪表板数据
async function loadDashboardData() {
    try {
        // 加载用户资料
        const profileResponse = await fetch(`${API_BASE_URL}/users/${currentUser}/profile`);
        const profileData = await profileResponse.json();
        
        if (profileData.success) {
            updateDashboard(profileData.data);
        }
        
        // 加载排行榜（获取用户排名）
        await loadLeaderboard();
        
    } catch (error) {
        console.error('加载数据失败:', error);
        showFallbackData();
    }
}

// 更新仪表板
function updateDashboard(data) {
    const userInfo = data.user_info;
    const meritInfo = data.merit_info;
    const dailyInfo = data.daily_info;
    
    // 更新用户信息
    document.getElementById('username').textContent = userInfo.nickname;
    document.getElementById('user-level').textContent = meritInfo.total_level.name;
    
    // 更新总功德
    document.getElementById('total-merit').textContent = formatNumber(meritInfo.total_merit);
    document.getElementById('total-level-name').textContent = meritInfo.total_level.name;
    document.getElementById('total-progress').style.width = `${meritInfo.total_level.progress * 100}%`;
    document.getElementById('next-level-merit').textContent = formatNumber(meritInfo.total_level.next_level_merit);
    
    // 更新今日数据
    if (dailyInfo.today) {
        const today = dailyInfo.today;
        document.getElementById('today-merit').textContent = formatNumber(today.total_merit);
        document.getElementById('today-steps').textContent = formatNumber(today.steps);
        document.getElementById('today-running').textContent = today.running_distance.toFixed(1);
        document.getElementById('today-sleep').textContent = today.sleep_hours.toFixed(1);
    }
    
    // 更新连续天数
    document.getElementById('streak-days').textContent = dailyInfo.streak_days;
    document.getElementById('streak-days-summary').textContent = dailyInfo.streak_days;
    
    // 更新功德分布图表
    updateMeritDistributionChart(meritInfo.category_merits);
    
    // 更新成就摘要（增强版）
    if (data.achievements) {
        updateAchievementsSummary(data.achievements);
        // 更新全局加成百分比
        userBoostPercentage = data.achievements.total_boost || 0;
        updateCalculatorBoost();
    }
}

// 更新功德分布图表
function updateMeritDistributionChart(categoryMerits) {
    const ctx = document.getElementById('merit-distribution-chart').getContext('2d');
    
    // 过滤出有功德值的类别
    const categories = [];
    const merits = [];
    const colors = [
        '#4a6fa5', '#ff922b', '#51cf66', '#ff6b6b', '#845ef7',
        '#20c997', '#f76707', '#339af0', '#ff922b'
    ];
    
    Object.entries(categoryMerits).forEach(([category, merit], index) => {
        if (merit > 0) {
            categories.push(getCategoryChineseName(category));
            merits.push(merit);
        }
    });
    
    // 如果没有数据，显示占位符
    if (categories.length === 0) {
        categories.push('暂无数据');
        merits.push(1);
    }
    
    if (meritDistributionChart) {
        meritDistributionChart.destroy();
    }
    
    meritDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: merits,
                backgroundColor: colors.slice(0, categories.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${formatNumber(value)}功德 (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// 加载功德历史
async function loadMeritHistory() {
    try {
        const days = document.getElementById('time-range').value;
        const response = await fetch(`${API_BASE_URL}/users/${currentUser}/report?period=weekly`);
        const data = await response.json();
        
        if (data.success) {
            updateMeritHistoryChart(data.data.trend_data);
            updateMeritCategories(data.data.profile_summary);
        }
    } catch (error) {
        console.error('加载历史数据失败:', error);
    }
}

// 更新功德历史图表
function updateMeritHistoryChart(trendData) {
    const ctx = document.getElementById('merit-history-chart').getContext('2d');
    
    const dates = trendData.map(item => item.date.substring(5)); // 只显示月-日
    const merits = trendData.map(item => item.merit);
    const steps = trendData.map(item => item.steps);
    
    if (meritHistoryChart) {
        meritHistoryChart.destroy();
    }
    
    meritHistoryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: '每日功德',
                    data: merits,
                    borderColor: '#4a6fa5',
                    backgroundColor: 'rgba(74, 111, 165, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: '步数',
                    data: steps,
                    borderColor: '#51cf66',
                    backgroundColor: 'rgba(81, 207, 102, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: '功德'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: '步数'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 0) {
                                label += formatNumber(context.raw) + '功德';
                            } else {
                                label += formatNumber(context.raw) + '步';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// 更新功德类别
function updateMeritCategories(profileSummary) {
    const container = document.querySelector('.merit-categories');
    if (!container) return;
    
    // 这里可以添加类别详细信息显示
    // 暂时留空，可以根据需要扩展
}

// 加载排行榜
async function loadLeaderboard() {
    try {
        const type = document.getElementById('leaderboard-type').value;
        const response = await fetch(`${API_BASE_URL}/leaderboard?board_type=${type}&limit=10`);
        const data = await response.json();
        
        if (data.success) {
            updateLeaderboardTable(data.data);
            loadUserRank(type);
        }
    } catch (error) {
        console.error('加载排行榜失败:', error);
    }
}

// 更新排行榜表格
function updateLeaderboardTable(leaderboardData) {
    const tbody = document.getElementById('leaderboard-body');
    tbody.innerHTML = '';
    
    leaderboardData.forEach((entry, index) => {
        const row = document.createElement('tr');
        
        const meritKey = entry.daily_merit !== undefined ? 'daily_merit' : 'total_merit';
        const meritValue = entry[meritKey] || 0;
        
        row.innerHTML = `
            <td>${entry.rank}</td>
            <td>
                <div class="leaderboard-user">
                    <i class="fas fa-user-circle"></i>
                    <span>${entry.nickname}</span>
                </div>
            </td>
            <td>${formatNumber(meritValue)}</td>
            <td>${entry.current_level_name || '未知'}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// 加载用户排名
async function loadUserRank(boardType) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUser}/rank?board_type=${boardType}`);
        const data = await response.json();
        
        if (data.success) {
            updateUserRankInfo(data.data);
        }
    } catch (error) {
        console.error('加载用户排名失败:', error);
        document.getElementById('user-rank-info').innerHTML = `
            <div class="rank-number">--</div>
            <div class="rank-details">
                <div class="rank-percentile">前 --%</div>
                <div class="rank-total">总人数: --</div>
            </div>
        `;
    }
}

// 更新用户排名信息
function updateUserRankInfo(rankInfo) {
    const rankNumber = document.querySelector('.rank-number');
    const rankPercentile = document.querySelector('.rank-percentile');
    const rankTotal = document.querySelector('.rank-total');
    
    if (rankNumber && rankPercentile && rankTotal) {
        rankNumber.textContent = rankInfo.rank;
        rankPercentile.textContent = `前${rankInfo.percentile}%`;
        rankTotal.textContent = `总人数: ${rankInfo.total_users}`;
    }
}

// 加载成就
async function loadAchievements() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUser}/profile`);
        const data = await response.json();
        
        if (data.success && data.data.achievements) {
            const achievements = data.data.achievements;
            updateAchievementsSummary(achievements);
            updateAchievementsGrid(achievements.list);
            
            // 显示动态成就（如果存在）
            if (achievements.dynamic_achievements && achievements.dynamic_achievements.length > 0) {
                updateDynamicAchievements(achievements.dynamic_achievements);
            }
        }
    } catch (error) {
        console.error('加载成就失败:', error);
    }
}

// 更新成就摘要
function updateAchievementsSummary(achievements) {
    // 更新基本统计
    document.getElementById('achieved-count').textContent = achievements.achieved || 0;
    document.getElementById('total-achievements').textContent = achievements.total || 0;
    document.getElementById('total-boost').textContent = achievements.total_boost ? achievements.total_boost.toFixed(1) : '0';
    
    // 更新下一个加成目标
    const nextBoostTarget = document.getElementById('next-boost-target');
    const nextBoostName = document.getElementById('next-boost-name');
    const nextBoostPercent = document.getElementById('next-boost-percent');
    
    if (achievements.next_boost_target) {
        nextBoostName.textContent = achievements.next_boost_target.name;
        nextBoostPercent.textContent = achievements.next_boost_target.boost_percentage;
        nextBoostTarget.style.display = 'block';
    } else {
        nextBoostTarget.style.display = 'none';
    }
}

// 更新成就网格（增强版）
function updateAchievementsGrid(achievements) {
    const grid = document.getElementById('achievements-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    // 按稀有度排序：传奇 > 史诗 > 稀有 > 普通
    const rarityOrder = { legendary: 4, epic: 3, rare: 2, common: 1 };
    const sortedAchievements = [...achievements].sort((a, b) => {
        const orderA = rarityOrder[a.rarity] || 0;
        const orderB = rarityOrder[b.rarity] || 0;
        return orderB - orderA || (b.progress || 0) - (a.progress || 0);
    });
    
    sortedAchievements.forEach(achievement => {
        const card = document.createElement('div');
        card.className = 'achievement-card';
        
        const isAchieved = achievement.is_achieved;
        const progress = achievement.progress || 0;
        const rarity = achievement.rarity || 'common';
        const type = achievement.type || 'milestone';
        const boost = achievement.boost_percentage || 0;
        const icon = achievement.icon || 'fa-medal';
        const displayIcon = achievement.display_icon || 'fa-medal';
        const color = achievement.color || '#868e96';
        
        // 构建成就类型徽章
        const typeBadge = `<span class="achievement-type-badge type-${type}">${getTypeChineseName(type)}</span>`;
        
        // 构建加成指示器（如果有加成）
        const boostIndicator = boost > 0 ? 
            `<span class="achievement-boost"><i class="fas fa-arrow-up"></i>+${boost}%</span>` : '';
        
        // 确定图标背景色
        let iconBackground;
        if (isAchieved) {
            // 已达成：使用稀有度颜色
            iconBackground = `linear-gradient(135deg, ${color}, ${darkenColor(color, 20)})`;
        } else {
            // 未达成：灰色渐变
            iconBackground = 'linear-gradient(135deg, #868e96, #495057)';
        }
        
        card.innerHTML = `
            <div class="achievement-header">
                <div class="achievement-icon" style="background: ${iconBackground}">
                    <i class="fas ${isAchieved ? displayIcon : 'fa-lock'}"></i>
                </div>
                <div class="achievement-title">
                    <span class="rarity-${rarity}">${achievement.name}</span>
                    ${typeBadge}
                    ${boostIndicator}
                </div>
            </div>
            <div class="achievement-description">${achievement.description}</div>
            <div class="achievement-meta">
                <span class="achievement-rarity rarity-${rarity}">
                    <i class="fas ${getRarityIcon(rarity)}"></i>
                    ${getRarityChineseName(rarity)}
                </span>
                ${isAchieved && achievement.reward_merit > 0 ? 
                    `<span class="achievement-reward">
                        <i class="fas fa-coins"></i>
                        奖励: ${formatNumber(achievement.reward_merit)}功德
                    </span>` : ''
                }
            </div>
            <div class="achievement-progress">
                <div class="progress-text-small">
                    <span>${isAchieved ? '✅ 已达成' : '🔄 进行中'}</span>
                    <span>${Math.round(progress * 100)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress * 100}%; background: ${color}"></div>
                </div>
            </div>
        `;
        
        // 添加悬停效果
        if (!isAchieved) {
            card.style.opacity = '0.8';
            card.style.filter = 'grayscale(20%)';
        }
        
        grid.appendChild(card);
    });
}

// 更新动态成就
function updateDynamicAchievements(dynamicAchievements) {
    const grid = document.getElementById('achievements-grid');
    if (!grid || !dynamicAchievements.length) return;
    
    // 添加动态成就标题
    const dynamicHeader = document.createElement('div');
    dynamicHeader.className = 'dynamic-achievements-header';
    dynamicHeader.innerHTML = `
        <h3><i class="fas fa-bolt"></i> 动态成就</h3>
        <p>基于您的修行习惯生成的个性化成就</p>
    `;
    grid.appendChild(dynamicHeader);
    
    // 添加动态成就
    dynamicAchievements.forEach(achievement => {
        const card = document.createElement('div');
        card.className = 'achievement-card dynamic-achievement';
        
        card.innerHTML = `
            <div class="achievement-header">
                <div class="achievement-icon" style="background: linear-gradient(135deg, #51cf66, #40c057)">
                    <i class="fas ${achievement.icon || 'fa-bolt'}"></i>
                </div>
                <div class="achievement-title">
                    <span style="color: #51cf66">${achievement.name}</span>
                    <span class="achievement-type-badge type-challenge">动态</span>
                </div>
            </div>
            <div class="achievement-description">${achievement.description}</div>
            <div class="achievement-meta">
                <span class="achievement-rarity" style="color: #51cf66">
                    <i class="fas fa-sync-alt"></i>
                    个性化生成
                </span>
                ${achievement.reward_merit > 0 ? 
                    `<span class="achievement-reward">
                        <i class="fas fa-coins"></i>
                        奖励: ${formatNumber(achievement.reward_merit)}功德
                    </span>` : ''
                }
            </div>
            <div class="achievement-progress">
                <div class="progress-text-small">
                    <span>🎯 目标</span>
                    <span>${formatNumber(achievement.requirement_value)}${getRequirementUnit(achievement.requirement_type)}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// 工具函数
function getRarityChineseName(rarity) {
    const mapping = {
        'common': '普通',
        'rare': '稀有', 
        'epic': '史诗',
        'legendary': '传奇'
    };
    return mapping[rarity] || rarity;
}

function getRarityIcon(rarity) {
    const mapping = {
        'common': 'fa-medal',
        'rare': 'fa-trophy',
        'epic': 'fa-crown',
        'legendary': 'fa-gem'
    };
    return mapping[rarity] || 'fa-medal';
}

function getTypeChineseName(type) {
    const mapping = {
        'milestone': '里程碑',
        'challenge': '挑战',
        'hidden': '隐藏',
        'seasonal': '季节',
        'social': '社交',
        'combo': '组合'
    };
    return mapping[type] || type;
}

function getRequirementUnit(requirementType) {
    if (requirementType.includes('merit')) return '功德';
    if (requirementType.includes('streak')) return '天';
    if (requirementType.includes('running')) return '公里';
    if (requirementType.includes('walking')) return '步';
    if (requirementType.includes('sleep')) return '小时';
    return '';
}

function darkenColor(color, percent) {
    // 简单的颜色变暗函数
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) - amt;
    const G = (num >> 8 & 0x00FF) - amt;
    const B = (num & 0x0000FF) - amt;
    return '#' + (0x1000000 + (R < 0 ? 0 : R > 255 ? 255 : R) * 0x10000 +
        (G < 0 ? 0 : G > 255 ? 255 : G) * 0x100 +
        (B < 0 ? 0 : B > 255 ? 255 : B)).toString(16).slice(1);
}

// 初始化表单计算
function initFormCalculations() {
    const form = document.getElementById('health-data-form');
    const inputs = form.querySelectorAll('input[type="number"]');
    
    // 实时计算功德
    inputs.forEach(input => {
        input.addEventListener('input', calculateMerit);
    });
    
    // 表单提交
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitHealthData();
    });
}

// 计算功德
function calculateMerit() {
    const totalMerit = calculateCurrentMerit();
    
    // 更新基础功德显示
    document.getElementById('calculated-merit').textContent = formatNumber(totalMerit);
    
    // 计算各项功德（用于明细显示）
    const running = parseFloat(document.getElementById('running').value) || 0;
    const walking = parseInt(document.getElementById('walking').value) || 0;
    const sleep = parseFloat(document.getElementById('sleep').value) || 0;
    const exercise = parseInt(document.getElementById('exercise').value) || 0;
    const standing = parseFloat(document.getElementById('standing').value) || 0;
    
    const runningMerit = Math.floor(running * 1000);
    const walkingMerit = Math.floor(walking / 100 * 10);
    const sleepMerit = Math.floor(sleep * 500);
    const exerciseMerit = Math.floor(exercise * 50);
    const standingMerit = Math.floor(standing * 300);
    
    document.getElementById('breakdown-running').textContent = formatNumber(runningMerit);
    document.getElementById('breakdown-walking').textContent = formatNumber(walkingMerit);
    document.getElementById('breakdown-sleep').textContent = formatNumber(sleepMerit);
    document.getElementById('breakdown-exercise').textContent = formatNumber(exerciseMerit);
    document.getElementById('breakdown-standing').textContent = formatNumber(standingMerit);
    
    // 更新加成显示
    updateCalculatorBoost();
}

// 提交健康数据
async function submitHealthData() {
    const form = document.getElementById('health-data-form');
    const formData = {
        running: parseFloat(document.getElementById('running').value) || 0,
        walking: parseInt(document.getElementById('walking').value) || 0,
        sleep: parseFloat(document.getElementById('sleep').value) || 0,
        exercise: parseInt(document.getElementById('exercise').value) || 0,
        standing: parseFloat(document.getElementById('standing').value) || 0
    };
    
    // 过滤掉零值
    const filteredData = {};
    Object.entries(formData).forEach(([key, value]) => {
        if (value > 0) filteredData[key] = value;
    });
    
    if (Object.keys(filteredData).length === 0) {
        alert('请至少输入一项健康数据');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/health/dict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUser,
                data: filteredData
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            let message = `✅ 提交成功！\n`;
            message += `获得功德: ${formatNumber(data.total_merit_earned)}\n`;
            
            // 显示加成信息（如果有加成）
            if (data.boost_percentage > 0) {
                message += `\n🎯 成就加成: +${data.boost_percentage.toFixed(1)}%\n`;
                message += `基础功德: ${formatNumber(data.total_merit_earned_before_boost || data.total_merit_earned)}\n`;
                message += `加成功德: +${formatNumber(data.boost_amount || 0)}\n`;
            }
            
            // 显示各项明细（如果有）
            if (data.results && data.results.length > 0) {
                message += `\n📊 明细:\n`;
                data.results.forEach(r => {
                    if (r.merit_points > 0) {
                        const boostInfo = r.boost_percentage > 0 ? 
                            ` (+${r.boost_percentage.toFixed(1)}%)` : '';
                        message += `• ${getCategoryChineseName(r.category)}: ${formatNumber(r.merit_points)}功德${boostInfo}\n`;
                    }
                });
            }
            
            alert(message);
            
            // 清空表单
            form.reset();
            calculateMerit();
            
            // 刷新数据
            loadDashboardData();
            
            // 如果正在查看排行榜，也刷新
            if (document.querySelector('#leaderboard.section.active')) {
                loadLeaderboard();
            }
            
            // 如果正在查看成就，刷新成就页面
            if (document.querySelector('#achievements.section.active')) {
                loadAchievements();
            }
        } else {
            alert('提交失败：' + (result.error || '未知错误'));
        }
    } catch (error) {
        console.error('提交数据失败:', error);
        alert('提交失败，请检查API服务是否运行');
    }
}

// 显示模拟数据模态框
function showSimulateData() {
    document.getElementById('simulate-modal').classList.add('active');
}

// 关闭模态框
function closeModal() {
    document.getElementById('simulate-modal').classList.remove('active');
}

// 模拟一天数据
function simulateDay(intensity) {
    const data = {
        light: { running: 0, walking: 3000, sleep: 6.5, exercise: 15, standing: 8 },
        moderate: { running: 3.2, walking: 8500, sleep: 7.5, exercise: 45, standing: 10 },
        intensive: { running: 8.5, walking: 15000, sleep: 8.5, exercise: 90, standing: 12 }
    };
    
    const dayData = data[intensity] || data.moderate;
    
    // 填充表单
    document.getElementById('running').value = dayData.running;
    document.getElementById('walking').value = dayData.walking;
    document.getElementById('sleep').value = dayData.sleep;
    document.getElementById('exercise').value = dayData.exercise;
    document.getElementById('standing').value = dayData.standing;
    
    // 计算功德
    calculateMerit();
    
    // 关闭模态框
    closeModal();
}

// 随机生成数据
function simulateRandom() {
    const randomData = {
        running: (Math.random() * 15).toFixed(1),
        walking: Math.floor(Math.random() * 20000),
        sleep: (4 + Math.random() * 5).toFixed(1),
        exercise: Math.floor(Math.random() * 120),
        standing: (6 + Math.random() * 8).toFixed(1)
    };
    
    // 填充表单
    document.getElementById('running').value = randomData.running;
    document.getElementById('walking').value = randomData.walking;
    document.getElementById('sleep').value = randomData.sleep;
    document.getElementById('exercise').value = randomData.exercise;
    document.getElementById('standing').value = randomData.standing;
    
    // 计算功德
    calculateMerit();
}

// 刷新数据
function refreshData() {
    const activeSection = document.querySelector('.section.active');
    if (activeSection) {
        switch(activeSection.id) {
            case 'dashboard':
                loadDashboardData();
                break;
            case 'merit':
                loadMeritHistory();
                break;
            case 'leaderboard':
                loadLeaderboard();
                break;
            case 'achievements':
                loadAchievements();
                break;
        }
    }
}

// 显示回退数据（API不可用时）
function showFallbackData() {
    // 设置一些演示数据
    document.getElementById('total-merit').textContent = '125,430';
    document.getElementById('total-level-name').textContent = '修身养性';
    document.getElementById('total-progress').style.width = '65%';
    document.getElementById('next-level-merit').textContent = '345,700';
    
    document.getElementById('today-merit').textContent = '5,280';
    document.getElementById('today-steps').textContent = '8,500';
    document.getElementById('today-running').textContent = '3.2';
    document.getElementById('today-sleep').textContent = '7.5';
    
    document.getElementById('streak-days').textContent = '7';
    
    // 显示提示
    alert('正在使用演示数据。请启动API服务获取真实数据。');
}

// 工具函数：格式化数字
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 工具函数：获取类别中文名
function getCategoryChineseName(category) {
    const mapping = {
        'running': '跑步',
        'walking': '步行',
        'standing': '站立',
        'exercise': '锻炼',
        'heart_rate': '心率',
        'sleep': '睡眠',
        'meditation': '冥想',
        'stairs': '爬楼',
        'swimming': '游泳'
    };
    return mapping[category] || category;
}

// 点击模态框外部关闭
window.addEventListener('click', function(event) {
    const modal = document.getElementById('simulate-modal');
    if (event.target === modal) {
        closeModal();
    }
});

// 更新计算器加成显示
function updateCalculatorBoost() {
    const boostElement = document.getElementById('calculator-boost');
    const boostPercentageElement = document.getElementById('boost-percentage');
    const boostedMeritElement = document.getElementById('boosted-merit');
    
    if (userBoostPercentage > 0) {
        // 显示加成提示
        boostElement.style.display = 'flex';
        boostPercentageElement.textContent = userBoostPercentage.toFixed(1);
        
        // 计算当前输入数据的加成后功德
        const currentMerit = calculateCurrentMerit();
        if (currentMerit > 0) {
            const boostedMerit = Math.floor(currentMerit * (1 + userBoostPercentage / 100));
            boostedMeritElement.textContent = formatNumber(boostedMerit);
        }
    } else {
        boostElement.style.display = 'none';
    }
}

// 计算当前输入数据的基础功德
function calculateCurrentMerit() {
    const running = parseFloat(document.getElementById('running').value) || 0;
    const walking = parseInt(document.getElementById('walking').value) || 0;
    const sleep = parseFloat(document.getElementById('sleep').value) || 0;
    const exercise = parseInt(document.getElementById('exercise').value) || 0;
    const standing = parseFloat(document.getElementById('standing').value) || 0;
    
    // 计算各项功德
    const runningMerit = Math.floor(running * 1000);
    const walkingMerit = Math.floor(walking / 100 * 10);
    const sleepMerit = Math.floor(sleep * 500);
    const exerciseMerit = Math.floor(exercise * 50);
    const standingMerit = Math.floor(standing * 300);
    
    return runningMerit + walkingMerit + sleepMerit + exerciseMerit + standingMerit;
}

// 导出到全局
window.refreshData = refreshData;
window.showSimulateData = showSimulateData;
window.closeModal = closeModal;
window.simulateDay = simulateDay;
window.simulateRandom = simulateRandom;
window.loadMeritHistory = loadMeritHistory;
window.loadLeaderboard = loadLeaderboard;