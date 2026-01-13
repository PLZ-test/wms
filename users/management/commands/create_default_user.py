"""
Django Management Command: 공용 계정 자동 생성

사용법:
    python manage.py create_default_user

설명:
    깃허브에서 코드를 클론 받은 팀원들이 동일한 계정으로 로그인할 수 있도록
    공용 계정을 자동으로 생성합니다.
    
    계정 정보:
    - 아이디: PLZM
    - 비밀번호: 16449051*
    - 권한: 슈퍼유저 (관리자 권한)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '팀 공용 계정을 생성합니다 (아이디: PLZM)'

    def handle(self, *args, **options):
        # 공용 계정 정보
        USERNAME = 'PLZM'
        PASSWORD = '16449051*'
        EMAIL = 'team@wms.local'  # 이메일은 선택사항

        # 이미 계정이 존재하는지 확인
        if User.objects.filter(username=USERNAME).exists():
            self.stdout.write(
                self.style.WARNING(f'✋ 계정 "{USERNAME}"이 이미 존재합니다. 건너뜁니다.')
            )
            return

        # 슈퍼유저 계정 생성
        user = User.objects.create_superuser(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD
        )

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ 공용 계정이 성공적으로 생성되었습니다!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'아이디: {USERNAME}')
        self.stdout.write(f'비밀번호: {PASSWORD}')
        self.stdout.write(f'권한: 슈퍼유저 (관리자)')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('이제 로그인 페이지에서 위 계정 정보로 접속하세요.')
        self.stdout.write(f'URL: http://localhost:8000/users/login/')
