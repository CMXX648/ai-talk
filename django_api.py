"""
Django API接口模块
用于问卷系统与Django数据库的交互
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'medical_followup'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_followup.settings')
django.setup()

from core.models import Patient, Doctor, FollowUpRecord


def get_patient_by_phone(phone):
    """
    根据电话号码获取患者信息
    
    Args:
        phone: 患者电话号码
        
    Returns:
        Patient对象或None
    """
    try:
        patient = Patient.objects.get(phone=phone)
        return {
            'id': patient.id,
            'name': patient.name,
            'gender': patient.gender,
            'age': patient.age,
            'phone': patient.phone
        }
    except Patient.DoesNotExist:
        return None


def get_patient_by_name(name):
    """
    根据姓名获取患者信息
    
    Args:
        name: 患者姓名
        
    Returns:
        Patient对象或None
    """
    try:
        patient = Patient.objects.get(name=name)
        return {
            'id': patient.id,
            'name': patient.name,
            'gender': patient.gender,
            'age': patient.age,
            'phone': patient.phone
        }
    except Patient.DoesNotExist:
        return None


def get_all_patients():
    """
    获取所有患者信息
    
    Returns:
        患者信息列表
    """
    patients = Patient.objects.all()
    return [
        {
            'id': patient.id,
            'name': patient.name,
            'gender': patient.gender,
            'age': patient.age,
            'phone': patient.phone
        }
        for patient in patients
    ]


def get_doctor_by_phone(phone):
    """
    根据电话号码获取医生信息
    
    Args:
        phone: 医生电话号码
        
    Returns:
        Doctor对象或None
    """
    try:
        doctor = Doctor.objects.get(phone=phone)
        return {
            'id': doctor.id,
            'name': doctor.name,
            'gender': doctor.gender,
            'phone': doctor.phone,
            'department': doctor.department,
            'title': doctor.title
        }
    except Doctor.DoesNotExist:
        return None


def save_follow_up_record(patient_phone, doctor_phone, content, health_assessment=None, recommendations=None, next_follow_up=None):
    """
    保存随访记录
    
    Args:
        patient_phone: 患者电话号码
        doctor_phone: 医生电话号码
        content: 随访内容
        health_assessment: 健康评估
        recommendations: 建议措施
        next_follow_up: 下次随访时间
        
    Returns:
        FollowUpRecord对象或None
    """
    try:
        patient = Patient.objects.get(phone=patient_phone)
        doctor = Doctor.objects.get(phone=doctor_phone)
        
        record = FollowUpRecord.objects.create(
            patient=patient,
            doctor=doctor,
            content=content,
            health_assessment=health_assessment,
            recommendations=recommendations,
            next_follow_up=next_follow_up
        )
        
        return {
            'id': record.id,
            'patient': record.patient.name,
            'doctor': record.doctor.name,
            'record_date': record.record_date.strftime('%Y-%m-%d %H:%M:%S'),
            'content': record.content
        }
    except (Patient.DoesNotExist, Doctor.DoesNotExist) as e:
        print(f"保存随访记录失败: {e}")
        return None


def get_patient_records(patient_phone):
    """
    获取患者的随访记录
    
    Args:
        patient_phone: 患者电话号码
        
    Returns:
        随访记录列表
    """
    try:
        patient = Patient.objects.get(phone=patient_phone)
        records = FollowUpRecord.objects.filter(patient=patient).order_by('-record_date')
        
        return [
            {
                'id': record.id,
                'doctor': record.doctor.name,
                'record_date': record.record_date.strftime('%Y-%m-%d %H:%M:%S'),
                'content': record.content,
                'health_assessment': record.health_assessment,
                'recommendations': record.recommendations,
                'next_follow_up': record.next_follow_up.strftime('%Y-%m-%d') if record.next_follow_up else None
            }
            for record in records
        ]
    except Patient.DoesNotExist:
        return []


if __name__ == "__main__":
    # 测试代码
    print("=== 测试Django API接口 ===")
    
    # 测试获取所有患者
    patients = get_all_patients()
    print(f"所有患者数量: {len(patients)}")
    for patient in patients:
        print(f"  - {patient['name']}, {patient['gender']}, {patient['age']}岁")
    
    # 测试获取特定患者
    if patients:
        patient_info = get_patient_by_phone(patients[0]['phone'])
        print(f"\n患者详情: {patient_info}")
        
        # 测试获取患者记录
        records = get_patient_records(patients[0]['phone'])
        print(f"\n患者随访记录数量: {len(records)}")
        for record in records:
            print(f"  - {record['record_date']}: {record['content'][:50]}...")
