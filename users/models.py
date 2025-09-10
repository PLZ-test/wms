# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

# [신규] User 모델을 별도의 users 앱으로 분리하여 관리합니다.
# AbstractUser를 상속받아 Django의 기본 인증 기능을 모두 사용하면서 필요한 필드를 추가합니다.
class User(AbstractUser):
    """
    커스텀 사용자 모델
    기본 User 모델에 역할(role), 소속 센터(center), 소속 화주사(shipper) 필드를 추가합니다.
    """
    class RoleChoices(models.TextChoices):
        # 사용자의 역할을 정의하는 선택지입니다.
        CENTER_ADMIN = 'CENTER_ADMIN', '센터 관리자'
        CENTER_MANAGER = 'CENTER_MANAGER', '센터 매니저'
        CENTER_MEMBER = 'CENTER_MEMBER', '센터 구성원'
        SHIPPER_ADMIN = 'SHIPPER_ADMIN', '화주사 관리자'
        SHIPPER_MANAGER = 'SHIPPER_MANAGER', '화주사 매니저'
        SHIPPER_MEMBER = 'SHIPPER_MEMBER', '화주사 구성원'
        UNASSIGNED = 'UNASSIGNED', '미지정'

    # 역할 필드: 사용자의 권한 그룹을 나타냅니다.
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default='UNASSIGNED', verbose_name='사용자 역할')
    
    # 소속 센터 필드: management 앱의 Center 모델과 관계를 맺습니다.
    # on_delete=models.SET_NULL: 센터가 삭제되어도 사용자는 삭제되지 않고, 이 필드값만 NULL로 변경됩니다.
    center = models.ForeignKey('management.Center', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 센터')
    
    # 소속 화주사 필드: management 앱의 Shipper 모델과 관계를 맺습니다.
    shipper = models.ForeignKey('management.Shipper', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 화주사')

    # Django의 기본 그룹, 권한 필드와의 충돌을 피하기 위해 related_name을 재정의합니다.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='users_user_groups', # related_name 변경
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='users_user_permissions', # related_name 변경
        related_query_name='user',
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'