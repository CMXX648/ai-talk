"""
随访系统配置文件
"""
import os

# 医生信息配置
DEFAULT_DOCTOR = {
    'name': '王医生',
    'gender': '男',
    'phone': '13800000000',  # 默认医生电话号码
    'department': '内科',
    'title': '主治医师'
}

# 可以配置多个医生
DOCTORS = [
    {
        'name': '王医生',
        'gender': '男',
        'phone': '13800000000',
        'department': '内科',
        'title': '主治医师'
    },
    {
        'name': '刘医生',
        'gender': '女',
        'phone': '13900000000',
        'department': '心内科',
        'title': '副主任医师'
    }
]

# Django项目配置
DJANGO_SETTINGS_MODULE = 'medical_followup.settings'
DJANGO_PROJECT_PATH = os.path.join(os.path.dirname(__file__), 'medical_followup')

# 随访记录配置
FOLLOW_UP_OUTPUT_DIR = 'follow_up_records'
FOLLOW_UP_FILE_PREFIX = 'follow_up_'
