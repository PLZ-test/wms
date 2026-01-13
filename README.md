# WMS (Warehouse Management System)

물류센터 재고 관리 시스템

## 🚀 초기 설정 가이드

### 1. 필수 요구사항
- Python 3.8 이상
- Git

### 2. 프로젝트 클론

```bash
git clone https://github.com/PLZ-test/wms.git
cd wms
```

### 3. 가상환경 생성 및 활성화

**Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

만약 `requirements.txt`가 없다면:
```bash
pip install django pillow
```

### 5. 데이터베이스 초기화

```bash
python manage.py migrate
```

### 6. 공용 계정 생성 ⭐

**중요**: 팀 전체가 사용할 공용 계정을 자동으로 생성합니다.

```bash
python manage.py create_default_user
```

**계정 정보** (자동 생성됨):
- 아이디: `PLZM`
- 비밀번호: `16449051*`
- 권한: 관리자 (슈퍼유저)

### 7. 서버 실행

**로컬 컴퓨터에서만 접속:**
```bash
python manage.py runserver
```

**같은 와이파이 사용자들과 공유:**
```bash
python run_wifi.py
```

### 8. 접속

브라우저에서 접속:
- 로컬: `http://localhost:8000`
- 같은 WiFi: `http://192.168.X.X:8000` (터미널에 표시된 주소)

로그인 페이지에서 위 계정 정보로 로그인하세요!

---

## 📂 주요 기능

- **대시보드**: 주문 및 재고 현황 한눈에 확인
- **주문 관리**: 여러 쇼핑몰에서 자동 주문 수집
- **재고 관리**: 입출고 처리 및 위치 추적
- **화주사 관리**: 화주사별 상품 및 재고 관리
- **정산 관리**: 월별 정산 내역

---

## 🛠️ 문제 해결

### 포트 충돌 오류
```bash
# 8000번 포트가 이미 사용 중이면 다른 포트 사용
python manage.py runserver 8001
```

### Migration 오류
```bash
# 데이터베이스 초기화
python manage.py migrate --run-syncdb
```

### 공용 계정이 이미 존재한다는 메시지
- 정상입니다! 계정이 이미 생성되어 있으므로 바로 로그인하면 됩니다.

---

## 📝 개발 정보

- Django 기반 웹 애플리케이션
- SQLite 데이터베이스 (개발용)
- Chart.js를 사용한 데이터 시각화

---

## 🔐 보안 주의사항

- 실제 배포 시에는 `settings.py`의 `SECRET_KEY`를 변경하세요.
- `DEBUG = False`로 설정하고 `ALLOWED_HOSTS`를 적절히 설정하세요.
- 실서비스에서는 개별 계정을 사용하세요 (공용 계정은 개발/테스트 용도).
