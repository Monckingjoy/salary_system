from flask import Flask, render_template, request, jsonify
from datetime import datetime, time, timedelta
import chinese_calendar as chn_calendar  # 保持这个导入方式

app = Flask(__name__)

def calculate_work_days(year, month):
    # 获取当月第一天和最后一天
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year+1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month+1, 1) - timedelta(days=1)
    
    # 计算所有工作日
    work_days = 0
    current_day = first_day
    while current_day <= last_day:
        # 检查是否是周末或法定节假日
        if current_day.weekday() < 5 and not chn_calendar.is_holiday(current_day):  # 使用chn_calendar
            work_days += 1
        current_day += timedelta(days=1)
    
    return work_days

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    monthly_salary = float(data['salary'])
    daily_hours = float(data['hours'])
    start_time = data['startTime']
    break_duration = float(data['breakDuration'])
    
    now = datetime.now()
    year = now.year
    month = now.month
    today = now.date()
    
    # 计算当月工作天数
    work_days = calculate_work_days(year, month)
    
    # 计算当月已工作天数
    worked_days = 0
    current_day = datetime(year, month, 1).date()
    while current_day <= today:
        if current_day.weekday() < 5 and not chn_calendar.is_holiday(current_day):  # 使用chn_calendar
            worked_days += 1
        current_day += timedelta(days=1)
    
    # 计算时薪
    hourly_rate = monthly_salary / (work_days * (daily_hours - break_duration))
    
    # 计算本月已赚金额
    monthly_earned = hourly_rate * (daily_hours - break_duration) * worked_days
    
    # 计算年度已赚金额
    yearly_earned = 0
    for m in range(1, month):
        m_days = calculate_work_days(year, m)
        yearly_earned += monthly_salary * m_days / work_days
    
    yearly_earned += monthly_earned
    
    return jsonify({
        'hourly_rate': round(hourly_rate, 2),
        'monthly_earned': round(monthly_earned, 2),
        'yearly_earned': round(yearly_earned, 2),
        'worked_days': worked_days,
        'work_days': work_days,
        'current_month': month
    })

if __name__ == '__main__':
    app.run(debug=True)