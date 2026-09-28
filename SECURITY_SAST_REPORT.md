# SAST 보안 점검 및 조치 보고서

- 점검일: 2026-09-29
- 작업 브랜치: `security/sast-remediation-20260929`
- 도구: Semgrep 1.178.0, Community `auto` 규칙
- 원본 결과: `semgrep_result.before.json`
- 조치 후 결과: `semgrep_result.after.json`

## 1. 결과 요약

| 구분 | 검사 파일 | 실행 규칙 | 검출 건수 |
|---|---:|---:|---:|
| 조치 전 | 170 | 344 | 8 |
| 조치 후 | 178 | 348 | 0 |

검출 8건은 GitHub Actions 가변 태그 2건, root 컨테이너 1건, DRF 요청 제한 누락 1건, 비밀번호 정책 미적용 3건, SQL 주입 의심 1건이었다. 재스캔에서 모두 제거되었다.

## 2. 대표 취약점과 실제 조치

### GitHub Actions 공급망 위험

버전 태그는 소유자가 다른 커밋으로 다시 지정할 수 있다. `checkout` v3과 `setup-buildx-action` v2를 각 태그가 점검 시점에 가리키던 40자 커밋 SHA로 고정했다. 기능 버전은 유지하면서 태그 재지정 공격만 차단하는 선택이다.

### root 컨테이너와 과도한 권한

`Dockerfile`에 일반 사용자는 있었지만 실행 명령 뒤에 배치되어 규칙이 안전한 실행 상태로 판단하지 못했다. `USER django-user`를 실행 명령 앞으로 옮겼고, 전체 디렉토리에 쓰기 권한을 주던 재귀적 `777` 설정을 제거했다. 필요한 소유권만 `chown`으로 제공해 침해 시 피해 범위를 줄였다.

### API 자원 고갈/DoS

DRF 전역 설정에 익명 `100/hour`, 인증 사용자 `1000/day` 요청 제한을 추가했다. 운영 트래픽에 맞게 `DRF_ANON_THROTTLE_RATE`, `DRF_USER_THROTTLE_RATE` 환경변수로 조정할 수 있게 했다.

### 비밀번호 정책 우회

`set_password()`는 해시만 하며 Django 강도 검사를 실행하지 않는다. 일반 계정 생성, 관리자 생성, 비밀번호 재설정 세 경로에서 `validate_password(password, user)`를 먼저 호출하고, 재설정 API는 검증 실패 메시지를 400 응답으로 반환하도록 했다.

```python
validate_password(password, user)
user.set_password(password)
```

### SQL 주입 의심 오탐과 개인정보 로깅

Semgrep은 `DELETE` 문자열과 사용자 이메일을 합친 로그를 SQL 문자열로 추적했다. DB 실행 경로가 없어 SQL 주입은 오탐이지만, 이메일이 로그에 남는 것은 실제 개인정보 노출 위험이다. f-string 대신 지연 포맷 로깅을 사용하고, 이메일 대신 내부 user ID만 남겼다.

```python
logger.info("DELETE /api/auth/delete for user_id=%s", request.user.pk)
```

### 수동 검토에서 추가 발견한 SMTP 비밀정보

Semgrep 8건에는 포함되지 않았지만 설정 파일에 SMTP 계정과 앱 비밀번호가 하드코딩되어 있었다. 코드에서 제거하고 `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` 환경변수로 이전했다. 기존 앱 비밀번호는 이미 Git 이력에 존재할 수 있으므로 폐기·재발급이 필수다.

## 3. 검증 결과

- Semgrep 재스캔: 8→0, 종료 코드 0
- Python `compileall`: 통과
- Django `manage.py check`: 통과, 이슈 0
- 비밀번호 정책 직접 테스트: 약한 비밀번호 거부, 강한 비밀번호 허용 통과
- GitHub Actions YAML 파싱: 통과
- Docker `build --check`: 경고 0, 통과
- JSON 산출물 `jq empty`: before/after 모두 통과
- `git diff --check`: 통과

전체 users 테스 15개는 코드 실행 전 테스트 DB 생성 단계에서 중단되었다. 로컬 PostgreSQL은 미기동 상태였고, SQLite 우회는 기존 `articles_article_tags` → `tags_tag` 외래 키 마이그레이션 비호환으로 실패했다. 보안 수정으로 인한 테스트 실패는 확인되지 않았으며, CI와 동일한 PostgreSQL 환경에서 전체 재실행이 필요하다.

## 4. 재현 명령

```bash
export SSL_CERT_FILE=/etc/ssl/cert.pem
/Users/song-yoonju/.venvs/semgrep/bin/semgrep --config auto --json -o semgrep_result.after.json .
/Users/song-yoonju/.venvs/semgrep/bin/semgrep --config auto .
docker build --check --progress=plain .
```

macOS에서 Semgrep이 `ca-certs: empty trust anchors`로 실패해 시스템 CA 번들을 `SSL_CERT_FILE`로 명시했다. 또한 `--config auto`는 규칙 선택을 위해 익명 메트릭이 필요하므로 metrics-off와 함께 실행할 수 없다.
