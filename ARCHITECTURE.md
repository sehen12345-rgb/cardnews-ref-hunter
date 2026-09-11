# 아키텍처 문서

## 시스템 개요

```
[GUI Layer - PyQt6]
       |
       v
[Business Logic Layer]
  ├── Crawler (Instaloader)
  ├── Analyzer (Engagement + Similarity)
  └── AI Client (Claude API)
       |
       v
[Data Layer]
  ├── SQLite DB (cardnews.db)
  └── Local Files (data/references/)
```

---

## 데이터 흐름

```
사용자가 계정 등록
       ↓
수집 실행 → Instaloader → 게시물 메타데이터 + 이미지 다운로드
       ↓
SQLite에 저장 (posts 테이블)
       ↓
참여율 계산 → 랭킹 정렬
       ↓
사용자가 게시물 선택
       ↓
Claude API → 번역 / 캡션 재작성
       ↓
유사도 체크 (코사인 유사도 < 80%)
       ↓
결과 편집 → 저장/내보내기
```

---

## DB 스키마

### accounts 테이블
```sql
CREATE TABLE accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT UNIQUE NOT NULL,
    type        TEXT NOT NULL,        -- 'overseas' | 'domestic'
    genre       TEXT,                 -- 'health' | 'lifestyle' | etc
    followers   INTEGER,
    added_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### posts 테이블
```sql
CREATE TABLE posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id      INTEGER REFERENCES accounts(id),
    shortcode       TEXT UNIQUE NOT NULL,   -- 인스타 게시물 고유ID
    post_type       TEXT,                   -- 'image' | 'carousel' | 'reel'
    thumbnail_url   TEXT,
    local_image_path TEXT,
    caption         TEXT,
    translated_caption TEXT,
    rewritten_caption  TEXT,
    likes           INTEGER DEFAULT 0,
    comments        INTEGER DEFAULT 0,
    views           INTEGER DEFAULT 0,
    engagement_rate REAL DEFAULT 0,
    similarity_score REAL,
    posted_at       DATETIME,
    collected_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_favorited    INTEGER DEFAULT 0
);
```

---

## 모듈 설명

### crawler/instagram.py
- Instaloader 래퍼
- 계정별 최근 N개 게시물 수집
- 이미지 로컬 저장
- rate limiting 적용 (요청 간 딜레이)

### analyzer/engagement.py
- Engagement Rate = (likes + comments) / followers * 100
- 랭킹 계산 및 정렬

### analyzer/similarity.py
- TF-IDF 벡터화
- 코사인 유사도 계산
- 유사도 % 반환

### analyzer/database.py
- SQLite CRUD 래퍼
- 계정/게시물 조회·저장·수정·삭제

### ai/claude_client.py
- Anthropic SDK 초기화
- API 호출 공통 메서드

### ai/caption.py
- 해외 캡션 한국어 번역
- 캡션 재작성 (유사도 80% 이하 목표)
- 썸네일 훅 카피 1줄 제안

### gui/main_window.py
- QMainWindow 기반 탭 구조
- 탭: 계정관리 / 수집 / 랭킹뷰 / 캡션재작성

---

## 외부 API

| API | 용도 | 인증 |
|-----|------|------|
| Anthropic Claude | 번역, 캡션 재작성 | API Key |
| Instagram (비공식) | 크롤링 | Instaloader (세션) |

---

## 에러 처리 전략

- Instagram 수집 실패 → 재시도 3회 후 스킵, 로그 기록
- Claude API 실패 → 에러 메시지 UI 표시
- DB 에러 → 트랜잭션 롤백
- 네트워크 없음 → 오프라인 모드 (수집된 데이터 뷰만)
