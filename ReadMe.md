
## 프로젝트 소개

### 프로젝트 제목
**HunsuKing :: AI Question Community Platform**

<img src="https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/main_image.png" width=100%>

### 프로젝트 정보
우리 팀은 네이버의 지식인 서비스를 착안하여, <br/>
사용자가 채택한 질문에 `AI`가 추가적인 답변, 훈수를 두는 재미있는 커뮤니티를 목표로 개발하였습니다.

**개발기간:** 2024.08.06 ~ 2024.09.10 <br/>
**배포 주소:** [https://hunsuking.yoyobar.xyz/](https://hunsuking.yoyobar.xyz/)

### 팀 소개

| 이름       | 역할               | 사진                                       | GitHub                                           | Blog                                      |
|------------|--------------------|--------------------------------------------|--------------------------------------------------|-------------------------------------------|
| Kim, Min Su| 팀 & 프론트엔드 팀장 | <img src="https://github.com/yoyobar.png" width="50"/> | [GitHub](https://github.com/yoyobar)            | [Blog](https://wiki.yoyobar.xyz)            |
| Kim, Se Rim | 프론트엔드 팀원  | <img src="https://github.com/srnnnn.png" width="50"/> | [GitHub](https://github.com/srnnnn)           | [Blog]()            |
| Hwang, Seong Min | 프론트엔드 팀원  | <img src="https://github.com/akwjr963.png" width="50"/> | [GitHub](https://github.com/akwjr963)           | [Blog]()           |
| Song, Yun Ju| 백엔드 팀장       | <img src="https://github.com/yoonju977.png" width="50"/> | [GitHub](https://github.com/yoonju977)          | [Blog]()           |
| Kim, Da Yeon| 백엔드 팀원    | <img src="https://github.com/dayeonkimm.png" width="50"/> | [GitHub](https://github.com/dayeonkimm)       | [Blog]()         |

---

## 1. 개발환경

### 개발 언어 및 라이브러리
![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django Rest Framework](https://img.shields.io/badge/Django%20Rest%20Framework-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django ORM](https://img.shields.io/badge/Django%20ORM-092E20?style=for-the-badge&logo=django&logoColor=white)

### 환경 관리
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![poetry](https://img.shields.io/badge/poetry-%2360A5FA.svg?style=for-the-badge&logo=poetry&logoColor=white)

### 데이터베이스
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)

### Assistant LLM
![GPT 4o mini](https://img.shields.io/badge/GPT%204o%20mini-4285F4?style=for-the-badge&logo=openai&logoColor=white)

### CI & CD
![GitHub](https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github)
![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Jenkins](https://img.shields.io/badge/-jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)

### Cloud Service
![AWS EC2](https://img.shields.io/badge/AWS%20EC2-FF9900?style=for-the-badge&logo=amazon-ec2&logoColor=white)
![AWS RDS](https://img.shields.io/badge/AWS%20RDS-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)
![AWS S3](https://img.shields.io/badge/-AWS%20S3-569A31?style=for-the-badge&logo=amazon-s3&logoColor=white)
![AWS ELB](https://img.shields.io/badge/-AWS%20ELB-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![AWS Route 53](https://img.shields.io/badge/-AWS%20Route%2053-8C4FFF?style=for-the-badge&logo=amazonroute53&logoColor=white)
![AWS CloudFront](https://img.shields.io/badge/-AWS%20CloudFront-8C4FFF?style=for-the-badge&logo=amazonwebservices&logoColor=white)

![AWS Certificate Manager](https://img.shields.io/badge/-AWS%20Certificate%20Manager-cc4d3f?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![AWS WAF](https://img.shields.io/badge/-AWS%20WAF-8C4FFF?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![AWS CloudWatch](https://img.shields.io/badge/-AWS%20CloudWatch-8C4FFF?style=for-the-badge&logo=amazonwebservices&logoColor=white)

---

## 2. 채택한 브랜치 전략

### 브랜치 전략
- 프로젝트를 `clone`하여 각자의 리포지토리에서 개발을 진행합니다. <br/>
- 개발을 진행할 때에는 개발 유형에 맞게 개발유형/개발구역이름 형식으로 브랜치를 생성하여 작업합니다. <br/>
- 예를 들어, 새로운 기능을 추가할 때는 feat/login, 버그를 수정할 때는 hotfix/bug123과 같은 형식을 사용합니다. <br/>
- 현재 작업하고 있는 부분의 기능 구현이 완료되면 Pull Request를 생성하여 코드 검토를 진행하며, 리뷰어의 피드백을 반영하여 코드를 개선합니다. <br/>
- 코드 리뷰가 완료되고 승인이 나면, Pull Request를 통해 develop 브랜치로 변경 사항을 병합합니다. <br/>
- 병합 후에는 develop 브랜치에서 전체적인 기능 테스트를 진행합니다. dev 브랜치의 안정성이 확보되면 main 브랜치로 병합하여 배포를 준비합니다. <br/>
- 이 전략을 통해 각 개발자는 독립적으로 작업하면서도 팀과의 협업을 원활하게 진행할 수 있습니다. 코드의 품질을 유지하고 버그를 최소화할 수 있도록 지속적으로 코드 리뷰와 테스트를 강화합니다.

### Commit Convention

    
| 커밋 유형 | 의미 |
| --- | --- |
| `Feat` | 새로운 기능 추가 |
| `Fix` | 버그 수정 |
| `Docs` | 문서 수정 |
| `Style` | 코드 formatting, 세미콜론 누락, 코드 자체의 변경이 없는 경우 |
| `Refactor` | 코드 리팩토링 |
| `Test` | 테스트 코드, 리팩토링 테스트 코드 추가 |
| `Chore` | 패키지 매니저 수정, 그 외 기타 수정 ex) .gitignore |
| `Design` | CSS 등 사용자 UI 디자인 변경 |
| `Comment` | 필요한 주석 추가 및 변경 |
| `Rename` | 파일 또는 폴더 명을 수정하거나 옮기는 작업만인 경우 |
| `Remove` | 파일을 삭제하는 작업만 수행한 경우 |
| `!BREAKING CHANGE` | 커다란 API 변경의 경우 |
| `!HOTFIX` | 급하게 치명적인 버그를 고쳐야 하는 경우 |


## Pull Request(PR) Convention

PR과 관련된 템플릿은 PR을 생성할때 자동으로 생성됩니다. <br/>
해당 내용을 참고하시어 작성을 진행해주시기 바랍니다.

---


## 3. 주요 페이지

| 홈 페이지                                 | 
|--------------------------------------------|
| <img src="https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/main_page.png"/> | 
| 서비스 메인 페이지와 게시물을 볼 수 있습니다.              |

| 로그인 페이지                             | 
|--------------------------------------------|
| <img src="https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/register_page.png"/> | 
| 현대웹 구조에 맞게 로그인 페이지를 구성하고, 이메일 인증과 비밀번호 찾기가 가능합니다.         |

| 마이 페이지                             | 
|--------------------------------------------|
| <img src="https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/my_page.png"/> | 
| 사용자 정보를 확인하고 레벨, 사용자 이미지, 탈퇴처리, 작성한 게시물 등 다양한 작업이 가능합니다.|

| 어드민 페이지                             | 
|--------------------------------------------|
| <img src="https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/admin_page.png"/> | 
| 어드민 유저만 접속 가능하며 유저 신고관리, 게시물 관리, 유저 관리 등이 가능합니다.|



---

## 4. 주요 기능 로직

### 로그인/회원가입
![image](https://github.com/user-attachments/assets/5f59e81e-17b2-4dd1-8bc8-feb1dc84efde)


### 이미지 처리
- `zustand`로 동기화된 게시물 데이터
- 사용자의 게시물에 알림이 존재하여 실시간 반응 확인
- 카테고리 별 게시물, 검색 기능, 댓글, 댓글 이미지 등 여러 모던 웹 기능 지원

### AI봇 생성
![image](https://github.com/user-attachments/assets/98656fd3-3e85-454c-ad01-32a037ec608a)

### AI 프롬프트 엔지니어링


---

## 5. 아키텍처, 클라우드 아키텍처, ERD

### 아키텍처
![Architecture](https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/architecture.png)

### 클라우드 아키텍처
![CloudArchitecture](https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/cloud_architecture.png)

### ERD
![ERD](https://github.com/OZ-Coding-School/oz_03_collabo-004-FE/blob/main/src/doc/ERD.png)

---

## 6. 담당 기능

| 송윤주       | 김다연           |
| ---------       | ---------         |
| <img src="https://github.com/yoonju977.png" width="50"/>     | <img src="https://github.com/dayeonkimm.png" width="50"/>       |
| - 전체적인 프로젝트 매니징   | - Rds, CloudWatch, WAF(보안)           |
| - EC2, S3, Rds, Jenkins(CD)   | - Git Action(CI)          |
| - ELB, cloudfront, route53, certificate manager(https 배포)   | - WapTap 모니터링           |
| - Locust 성능테스트   | - Locust 성능테스트          |
| - 게시글 업로드/삭제/수정/좋아요 기능  | - 훈수봇 답변 기능          |
| - 이미지 업로드/수정/삭제 기능   |  - AI 프롬프트 엔지니어링          |
|  - 댓글 작성/도움이돼요/안돼요/채택 기능   |  - 소셜로그인 및 이메일인증, 비밀번호 재설정         |
|  - 일반로그인/ 마이페이지(프로필)       | - 어드민페이지 기능         |
| - 알림기능(채택, 좋아요, 댓글, AI알림)     | - 사용자 신고기능         |
| - 태그(카테고리)       |    - 알림기능(어드민신고처리알림)     |
| - 검색기능        |         |


---



## 7. 트러블 슈팅

- **문제:** Lorem Ipsum.
  - **해결:** Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.

- **문제:** Lorem Ipsum.
  - **해결:** Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.

- **문제:** Lorem Ipsum.
  - **해결:** Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.

- **문제:** Lorem Ipsum.
  - **해결:** Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.Lorem Ipsum.



---

## 8. 개선 방향성

- 파인튜닝을 이용한 훈수봇의 답변 미세 조정과 답변의 이미지 처리 기능 추가
- Redis를 통한 캐싱 처리
- 서비스의 확장성을 고려한 User서비스와 AI서비스의 컨테이너 분리를 통한 오케스트레이션

---

## 9. 프로젝트 후기

이번 프로젝트는 진행에 차질에 있었으나 빠르게 문제점을 파악하고 수정하고 <br/> 
최신 기술 스택을 활용하여 사용자 중심의 서비스를 제공할 수 있었습니다. <br/> 
프로젝트 기간 동안 발생한 이슈들을 해결하면서 많은 성장을 이룰 수 있었고, 앞으로의 개선 방향에 대해서도 명확한 계획을 수립할 수 있었습니다.

---

더 자세한 정보는 [Hunsuking](https://hunsuking.yoyobar.xyz/)를 방문해 주세요.
