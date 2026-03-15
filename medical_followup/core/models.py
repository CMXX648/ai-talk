from django.db import models
from django.utils import timezone

class Doctor(models.Model):
    """医生信息模型"""
    name = models.CharField(max_length=100, verbose_name="姓名")
    gender = models.CharField(max_length=10, verbose_name="性别")
    phone = models.CharField(max_length=20, unique=True, verbose_name="电话号码")
    department = models.CharField(max_length=100, blank=True, verbose_name="科室")
    title = models.CharField(max_length=100, blank=True, verbose_name="职称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "医生"
        verbose_name_plural = "医生"
    
    def __str__(self):
        return f"{self.name} - {self.department}"

class Patient(models.Model):
    """患者信息模型"""
    name = models.CharField(max_length=100, verbose_name="姓名")
    gender = models.CharField(max_length=10, verbose_name="性别")
    age = models.IntegerField(verbose_name="年龄")
    phone = models.CharField(max_length=20, unique=True, verbose_name="电话号码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "患者"
        verbose_name_plural = "患者"
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

class FollowUpRecord(models.Model):
    """随访记录模型"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="患者")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="医生")
    record_date = models.DateTimeField(default=timezone.now, verbose_name="随访日期")
    content = models.TextField(verbose_name="随访内容")
    health_assessment = models.TextField(blank=True, verbose_name="健康评估")
    recommendations = models.TextField(blank=True, verbose_name="建议措施")
    next_follow_up = models.DateTimeField(blank=True, null=True, verbose_name="下次随访时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "随访记录"
        verbose_name_plural = "随访记录"
        ordering = ["-record_date"]
    
    def __str__(self):
        return f"{self.patient.name} - {self.record_date.strftime('%Y-%m-%d')}"