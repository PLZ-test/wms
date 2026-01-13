# 백업 복구 방법 (Backup Restoration Guide)

## 📌 백업 정보
- **백업 일시**: 2026년 1월 7일 09:59
- **백업 브랜치**: `backup-original-2026-01-07`
- **복구 태그**: `backup-restore-point`
- **현재 커밋**: 1fb2b50 (입출고 간단버전)

## 🔄 원상태로 복구하는 방법

### 방법 1: Git 태그를 사용한 복구 (권장)
```bash
# 현재 작업을 임시 저장 (필요한 경우)
git stash

# 백업 지점으로 복구
git reset --hard backup-restore-point

# 작업 내역 확인
git log --oneline -5
```

### 방법 2: 백업 브랜치로 전환
```bash
# 백업 브랜치로 전환
git checkout backup-original-2026-01-07

# 또는 main 브랜치에서 백업 내용을 가져오기
git checkout main
git reset --hard backup-original-2026-01-07
```

### 방법 3: 특정 파일만 복구
```bash
# 특정 파일만 백업 지점에서 복구
git checkout backup-restore-point -- <파일경로>
```

## ⚠️ 주의사항
1. 복구 전에 현재 작업 중인 내용을 저장하세요
2. `git reset --hard`는 현재 변경사항을 모두 삭제하므로 신중히 사용하세요
3. 복구 후에는 `git status`로 상태를 확인하세요

## 📝 백업된 코드 구조
- Django WMS 프로젝트
- 주요 앱: core, management, orders, settlement, stock, users
- 데이터베이스: db.sqlite3 (백업 시점의 상태)
- 정적 파일 및 템플릿 포함

## 🛡️ 개발 중 안전 수칙
1. **코드 변경 전**: AI가 변경 사항을 먼저 알려드립니다
2. **구조 유지**: 현재 코드의 기본 틀은 유지됩니다
3. **복구 가능**: 언제든지 "원상태로 복구해줘"라고 요청하시면 됩니다
