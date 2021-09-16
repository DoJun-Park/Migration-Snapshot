from django.db import models

# Create your models here.

'''
디비 구조

스냅샷, 인스턴스 모두 사용자 ID를 primary key로

스냅샷
- user_id(pk)
- snap_id
- snap_name

인스턴스
- user_id(pk)
- ins_id
- ins_name
- vol_id
'''


# OpenStack 스냅샷 정보 저장 
class OpenStack_Snapshot_info(models.Model):
    objects = models.Manager()
    
    snap_id = models.TextField(primary_key=True)
    user_id = models.TextField()
    snap_name = models.TextField()
    os_name = models.TextField()
    created = models.TextField()
    


# OpenStack 인스턴스 정보 저장
class OpenStack_Instance_info(models.Model):
    objects = models.Manager()
    
    ins_id = models.TextField(primary_key=True)
    user_id = models.TextField()
    ins_name = models.TextField()
    vol_id = models.TextField()
    os_name = models.TextField()
    created = models.TextField()


# CloudStack 스냅샷 정보 저장 
class CloudStack_Snapshot_info(models.Model):
    objects = models.Manager()
    
    snap_id = models.TextField(primary_key=True)
    user_id = models.TextField()
    snap_name = models.TextField()
    os_name = models.TextField()
    created = models.TextField()


# CloudStack 인스턴스 정보 저장
class CloudStack_Instance_info(models.Model):
    objects = models.Manager()
    
    ins_id = models.TextField(primary_key=True)
    user_id = models.TextField()
    ins_name = models.TextField()
    vol_id = models.TextField()
    os_name = models.TextField()
    created = models.TextField()


