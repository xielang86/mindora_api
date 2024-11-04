import socket
import requests
from datetime import datetime
from zoneinfo import ZoneInfo  
from aivc.config.config import settings

def is_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False
    
def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=5) 
        return response.status_code in range(200, 300)
    except requests.RequestException:
        return False
    
def is_reachable(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)  
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"error: {e}")
        return False
    finally:
        sock.close()

def remove_outside_brackets(s):
    first_bracket_pos = s.find('[')
    last_bracket_pos = s.rfind(']')
    
    if first_bracket_pos != -1 and last_bracket_pos != -1:
        s = s[first_bracket_pos:last_bracket_pos+1]
    return repair_json_str(s)

def remove_outside_curly_brackets(s):
    first_bracket_pos = s.find('{')
    last_bracket_pos = s.rfind('}')
    
    if first_bracket_pos != -1 and last_bracket_pos != -1:
        s = s[first_bracket_pos:last_bracket_pos+1]
    return repair_json_str(s)

def repair_json_str(s):
    s = s.replace('\'', '\"')
    return s

def get_time_str():
    tz = ZoneInfo(settings.TZ)
    return datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S%z")