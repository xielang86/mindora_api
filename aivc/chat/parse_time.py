import re
import datetime
from typing import Optional, Dict, Any

def parse_date(question_orig: str, question_lower: str, today_date: datetime.date) -> str:
    """
    从问题文本中解析日期信息
    
    Args:
        question_orig: 原始问题文本
        question_lower: 小写的问题文本
        today_date: 今天的日期
        
    Returns:
        格式为 "YYYY-MM-DD" 的日期字符串
    """
    ts_fmt = "%Y-%m-%d"
    
    # 相对日期
    if "明天" in question_orig or "tomorrow" in question_lower:
        return (today_date + datetime.timedelta(days=1)).strftime(ts_fmt)
    if "后天" in question_orig or "day after tomorrow" in question_lower:
        return (today_date + datetime.timedelta(days=2)).strftime(ts_fmt)
    if "大后天" in question_orig:
        return (today_date + datetime.timedelta(days=3)).strftime(ts_fmt)
    if "今天" in question_orig or "today" in question_lower:
        return today_date.strftime(ts_fmt)

    # 周相关日期
    weekday_map_cn = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
    weekday_map_en = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    current_weekday = today_date.weekday()  # Monday is 0 and Sunday is 6

    # 检查周相关表达
    week_offset_patterns = [
        (r"下下周(?:周|星期)([一二三四五六日天])", 14),  # 下下周X
        (r"下周(?:周|星期)([一二三四五六日天])", 7),    # 下周X
        (r"(?:周|星期)([一二三四五六日天])", 0)         # 周X（当前周）
    ]
    
    for pattern, offset in week_offset_patterns:
        match = re.search(pattern, question_orig)
        if match:
            day_char = match.group(1)
            target_day = weekday_map_cn.get(day_char, 0)
            days_to_add = (target_day - current_weekday) % 7
            if days_to_add == 0 and offset == 0:  # 如果是今天的星期几但没有"今天"关键词
                days_to_add = 7  # 假设是下周的同一天
            return (today_date + datetime.timedelta(days=offset + days_to_add)).strftime(ts_fmt)
    
    # 英文星期表达
    for day_name, day_value in weekday_map_en.items():
        if day_name in question_lower:
            if "next" in question_lower and day_name in question_lower:
                days_to_add = (day_value - current_weekday) % 7
                if days_to_add <= 0:
                    days_to_add += 7  # 确保是下周
                return (today_date + datetime.timedelta(days=days_to_add)).strftime(ts_fmt)
            else:
                days_to_add = (day_value - current_weekday) % 7
                if days_to_add == 0:  # 今天
                    if "today" not in question_lower:
                        days_to_add = 7  # 下周同一天
                return (today_date + datetime.timedelta(days=days_to_add)).strftime(ts_fmt)

    # 默认为今天
    return today_date.strftime(ts_fmt)

def apply_time_period(hour: int, minute: int, question_orig: str, question_lower: str) -> str:
    """
    根据时间段调整小时值
    
    Args:
        hour: 小时
        minute: 分钟
        question_orig: 原始问题文本
        question_lower: 小写的问题文本
        
    Returns:
        格式为 "HH:MM" 的时间字符串
    """
    if "下午" in question_orig or "afternoon" in question_lower:
        if 1 <= hour <= 11:
            hour += 12
    elif "晚上" in question_orig or "evening" in question_lower or "night" in question_lower:
        if 1 <= hour <= 11:
            hour += 12
    elif "上午" in question_orig or "morning" in question_lower:
        if hour == 12:
            hour = 0
    return f"{hour:02d}:{minute:02d}"

def parse_time(question_orig: str, question_lower: str) -> Optional[str]:
    """
    从问题文本中解析时间信息
    
    Args:
        question_orig: 原始问题文本
        question_lower: 小写的问题文本
        
    Returns:
        格式为 "HH:MM" 的时间字符串或 None
    """
    hour = None
    minute = 0

    # 特殊口语化表达
    # 1. "差X分Y点" -> Y-1:60-X
    match = re.search(r"差(\d{1,2})分(\d{1,2})点", question_orig)
    if match:
        mins = int(match.group(1))
        target_hour = int(match.group(2))
        hour = (target_hour - 1) if mins < 60 else target_hour
        minute = 60 - mins if mins < 60 else 0
        return apply_time_period(hour, minute, question_orig, question_lower)

    # 2. "X点过Y分"、"X点Y分"
    match = re.search(r"(\d{1,2})点(?:过)?(\d{1,2})(?:分)?", question_orig)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return apply_time_period(hour, minute, question_orig, question_lower)

    # 3. "X点半"、"X点一刻"、"X点三刻"
    match = re.search(r"(\d{1,2})点(半|一刻|三刻)", question_orig)
    if match:
        hour = int(match.group(1))
        period = match.group(2)
        if period == "半":
            minute = 30
        elif period == "一刻":
            minute = 15
        elif period == "三刻":
            minute = 45
        return apply_time_period(hour, minute, question_orig, question_lower)

    # 标准时间格式
    # 中文: "X点"
    match = re.search(r"(\d{1,2})点", question_orig)
    if match:
        hour = int(match.group(1))
        minute = 0
        return apply_time_period(hour, minute, question_orig, question_lower)

    # 英文: "X:Y", "X.Y", "X o'clock"
    match = re.search(r"(\d{1,2})(?::|\.)(\d{1,2})|(\d{1,2})\s*o'clock", question_lower)
    if match:
        if match.group(3):  # X o'clock
            hour = int(match.group(3))
            minute = 0
        else:  # X:Y or X.Y
            hour = int(match.group(1))
            minute = int(match.group(2))
        
        # 处理AM/PM
        if " pm" in question_lower and 1 <= hour <= 11:
            hour += 12
        elif " am" in question_lower and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute:02d}"

    return None

def extract_time_params(question: str) -> Dict[str, Any]:
    """
    从问题中提取日期和时间参数
    
    Args:
        question: 原始问题文本
        
    Returns:
        包含日期和时间的参数字典
    """
    question_lower = question.lower()
    today = datetime.datetime.now().date()
    
    date_str = parse_date(question, question_lower, today)
    time_str = parse_time(question, question_lower)
    
    result = {}
    if date_str:
        result["date"] = date_str
    if time_str:
        result["time"] = time_str
        
    return result
