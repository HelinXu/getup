import csv
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import os

# makedirs(data) 方法用于递归创建目录
os.makedirs('./docs/data', exist_ok=True)
# 数据准备
csv_file_path = './docs/data/run_times.csv'
times = []

with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过标题行
    for row in reader:
        date, time = row
        date_time_obj = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M:%S')
        times.append(date_time_obj)

latest_time = max(times).strftime('%H:%M:%S')
# today
today = datetime.now().strftime('%Y-%m-%d')
# if lastest time is today, then get today's time
today_news = ''
if max(times).strftime('%Y-%m-%d') == today:
    wakeuptime = max(times).strftime('%H:%M:%S')
    print(f"Today Helin Woke Up at {wakeuptime}.")
    today_news = f"Today Helin Woke Up at {wakeuptime}."
else:
    print(f"Last Time Helin Woke Up at {latest_time}.")
    today_news = f"Last Time Helin Woke Up at {latest_time}."

# sort times
times.sort()
# find how many times in a roll that Helin woke up before 8:00
morning_bird_count = 0
last_time = times[-1]
for i in range(len(times)):
    if times[i].hour < 8 and abs((times[i] - last_time).days) < 1.5:
        morning_bird_count += 1
    else:
        morning_bird_count = 0

today_news += f"\nHelin has been a morning bird for {morning_bird_count} days in a roll."


# 筛选本月和本年的数据
current_month = datetime.now().month
current_year = datetime.now().year
times_this_month = [time for time in times if time.month == current_month and time.year == current_year]
times_this_year = [time for time in times if time.year == current_year]

def generate_histogram_plotly_html(times, title):
    """
    使用Plotly生成直方图的HTML字符串，并将频率归一化到0-1之间。
    
    参数:
    - times: 时间数据的列表，每个元素是datetime对象。
    - title: 图表的标题。
    
    返回:
    - 一个HTML字符串，表示生成的直方图。
    """
    # 将时间转换为一天中的小时数（浮点数）
    times_in_hours = [time.hour + time.minute / 60 for time in times]
    
    # 创建直方图并设置histnorm为'probability'以归一化频率到0-1之间
    fig = go.Figure(data=[go.Histogram(
        x=times_in_hours,
        xbins=dict(start=0, end=24, size=1),  # 定义24个小时的bins
        marker_color='skyblue',  # 柱体颜色
        marker_line_color='black',  # 柱体边界颜色
        marker_line_width=1.5,  # 柱体边界宽度
        opacity=0.7,  # 柱体透明度
        histnorm='probability'  # 归一化频率到0-1之间
    )])
    
    # 更新布局设置，使图表更美观
    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Frequency',
        bargap=0.2,  # 柱体之间的间隙
        template="plotly_white",  # 使用白色背景的模板
    )
    
    # 返回HTML字符串
    return fig.to_html(full_html=False, include_plotlyjs='cdn')
# 生成本月和本年的直方图
monthly_plot_html = generate_histogram_plotly_html(times_this_month, "Monthly Wake Up Time Distribution")
yearly_plot_html = generate_histogram_plotly_html(times_this_year, "Yearly Wake Up Time Distribution")

def generate_pie_chart_html(times, title):
    times_in_half_hours = [(time.hour * 2 + (1 if time.minute >= 30 else 0)) for time in times]
    time_frequencies = Counter(times_in_half_hours)
    labels = [f"{int(hh/2)}:{'30' if hh % 2 else '00'}" for hh in sorted(time_frequencies.keys())]
    values = [time_frequencies[hh] for hh in sorted(time_frequencies.keys())]

    # 使用新的颜色集
    moderate_saturation_colors = [
        'rgba(255, 159, 128, 0.8)',  # 柔和的珊瑚
        'rgba(255, 205, 86, 0.8)',   # 柔和的黄色
        'rgba(75, 192, 192, 0.8)',   # 柔和的青色
        'rgba(153, 102, 255, 0.8)',  # 柔和的紫色
        'rgba(54, 162, 235, 0.8)',   # 柔和的蓝色
        'rgba(255, 99, 132, 0.8)',   # 柔和的红色
        'rgba(101, 143, 75, 0.8)',   # 柔和的绿色
        'rgba(255, 159, 64, 0.8)',   # 柔和的橙色
        'rgba(201, 203, 207, 0.8)',  # 柔和的灰色
    ]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=moderate_saturation_colors))])
    fig.update_layout(title_text=title)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


monthly_pie_html = generate_pie_chart_html(times_this_month, "Monthly Wake Up Time Pie Chart")
yearly_pie_html = generate_pie_chart_html(times_this_year, "Yearly Wake Up Time Pie Chart")

# 假设monthly_pie_html和yearly_pie_html已经由Plotly生成并包含圆饼图的HTML代码
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wake Up Time Statistics</title>
    <style>
        .container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
        }}
        .item {{
            flex-basis: 48%;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        .chart-container {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <center><h2>{today_news}</h2></center>
    <center><h2>Wake Up Time Statistics for {datetime.now().strftime("%B %Y")}</h2></center>
    <div class="container">
        <div class="item">
            {monthly_plot_html}
        </div>
        <div class="item chart-container">
            {monthly_pie_html}
        </div>
    </div>
</body>
<body>
    <center><h2>Wake Up Time Statistics for {datetime.now().strftime("%Y")}</h2></center>
    <div class="container">
        <div class="item">
            {yearly_plot_html}
        </div>
        <div class="item chart-container">
            {yearly_pie_html}
        </div>
    </div>
</body>
</html>
"""

with open('docs/index.md', 'w') as file:
    file.write(html_content)
    
print("plot has been generated.")
