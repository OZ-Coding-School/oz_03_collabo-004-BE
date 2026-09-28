# SCA 의존성 보안 점검 및 업데이트 보고서

- 점검일: 2026-09-29
- 브랜치: `security/sast-remediation-20260929`
- 도구: Poetry 2.2.0, pip-audit 2.10.1
- 기준/최종 산출물: `pip-audit.before.json`, `pip-audit.after.json`

## 결과

| 구분 | 취약 패키지 | CVE/별칭 레코드 |
|---|---:|---:|
| 업데이트 전 가상환경 | 23 | 175 |
| 제약 내 일차 업데이트 | 4 | 53 |
| 제약 조정·환경 동기화 후 | 0 | 0 |

GitHub에서 표시한 83건은 기본 브랜치와 GitHub의 중복 정규화 기준이다. 로컬 175건은 현재 `.venv`에 설치된 패키지의 CVE 별칭까지 모두 세어 더 크다. 최종 로컬 실행 환경에서 `No known vulnerabilities found`를 확인했다. GitHub 숫자는 이 브랜치가 기본 브랜치에 병합된 후 재계산된다.

## 핵심 업데이트

- Django `5.1` → `5.2.17`
- Django REST Framework `3.15.2` → `3.18.1`
- SimpleJWT `5.3.1` → `5.5.1`
- Pillow `10.4.0` → `12.3.0`
- Locust `2.31.5` → `2.46.6`
- OpenAI SDK `1.43.0` → `1.109.1`
- 외 boto3, urllib3, requests, PyJWT, sqlparse, Flask/Locust 전이 의존성 등 갱신

Pillow은 기존 `^10.4.0` 제약으로 보안 수정 버전 12.x를 선택할 수 없어 `^12.3.0`으로 상향했다. 가상환경에 남은 사용하지 않는 `lxml`, BeautifulSoup 계열은 `poetry sync`로 제거했다. 프로젝트는 패키지로 배포하지 않으므로 `package-mode = false`를 추가해 Poetry 2.x의 root-package 설치 오류도 해결했다.

## AWS RDS 없이 로컬 테스트

`docker-compose.test.yml`을 추가해 운영 RDS와 완전히 분리된 PostgreSQL 16과 Redis 7을 일회성으로 실행한다. DB 데이터는 tmpfs를 사용하며, SMTP는 Django 메모리 백엔드로 바꿔 외부 메일을 보내지 않는다. PostgreSQL과 Redis 이미지는 digest로 고정했다.

```bash
docker compose -f docker-compose.test.yml up \
  --build --abort-on-container-exit --exit-code-from app-test
docker compose -f docker-compose.test.yml down --volumes --remove-orphans
```

첫 실행에서 PostgreSQL 연결과 테스트 DB 생성은 성공했지만 Redis가 없어 15건이 오류로 종료됐다. Redis 서비스와 healthcheck를 추가한 뒤 다시 실행해 `Ran 15 tests ... OK`(15/15)를 확인했다. 실패 원인은 RDS 종속이 아니라 로컬 인프라 구성의 PostgreSQL·Redis 누락이었다.

## 지속 관리

`.github/dependabot.yml`에 Poetry/pip 의존성과 GitHub Actions를 매주 월요일 09:00 KST에 검사하도록 설정했다. Dependabot은 저장소에 침입하는 봇이 아니라 GitHub가 제공하는 의존성 경고·업데이트 PR 기능이다. 생성된 PR은 CI 통과와 변경 내용을 확인한 후 병합해야 한다.
