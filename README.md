# 카드뉴스 레퍼런스 헌터 (CardNews Reference Hunter)

헬스/라이프스타일 인스타그램 카드뉴스 제작을 위한 레퍼런스 자동 수집·분석·캡션 재작성 도구

---

## 개요

해외/국내 인스타그램 계정에서 잘 터진 카드뉴스 게시물을 자동으로 수집하고,  
참여율 기반으로 랭킹을 매기며, Claude AI로 캡션을 재작성해주는 PyQt6 데스크탑 앱

---

## 주요 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| 계정 관리 | 해외/국내 레퍼런스 계정 등록·삭제 | 예정 |
| 게시물 수집 | Instaloader로 최근 N개 게시물 크롤링 | 예정 |
| 참여율 분석 | 좋아요+댓글 기반 Engagement Rate 자동 계산 | 예정 |
| 랭킹 뷰 | 참여율 순 정렬, 썸네일 미리보기 | 예정 |
| 캡션 번역 | 해외 캡션 → 한국어 자동 번역 (Claude API) | 예정 |
| 캡션 재작성 | 유사도 80% 이하로 재작성 (Claude API) | 예정 |
| 유사도 체크 | 코사인 유사도로 원본 대비 % 표시 | 예정 |
| 레퍼런스 저장 | 선택한 게시물 로컬 폴더로 저장 | 예정 |
| OCR 문구 추출 | 썸네일 이미지에서 텍스트 추출 | 예정 |

---

## TODO 리스트

### Phase 1 — 기반 세팅
- [ ] 프로젝트 폴더 구조 생성
- [ ] requirements.txt 작성
- [ ] PyQt6 메인 윈도우 기본 틀 구성
- [ ] 설정 파일 (config.json) 구조 설계
- [ ] Instaloader 연동 테스트

### Phase 2 — 크롤러 개발
- [ ] 계정 등록/삭제 UI
- [ ] 계정별 게시물 수집 (최근 N개 설정 가능)
- [ ] 좋아요·댓글 수 수집 및 저장
- [ ] 릴스 조회수 수집 (공개된 경우)
- [ ] 수집 진행률 표시 (Progress Bar)
- [ ] 수집 데이터 로컬 DB 저장 (SQLite)

### Phase 3 — 분석 & 뷰어
- [ ] Engagement Rate 계산 (좋아요+댓글) / 팔로워 수
- [ ] 랭킹 정렬 UI (참여율 / 좋아요 / 댓글)
- [ ] 썸네일 이미지 그리드 뷰
- [ ] 게시물 상세 보기 (원본 캡션 + 이미지)
- [ ] 필터 기능 (해외/국내, 날짜, 참여율 기준)

### Phase 4 — AI 캡션 처리
- [ ] 해외 캡션 → 한국어 번역 (Claude API)
- [ ] 캡션 재작성 (유사도 80% 이하)
- [ ] 코사인 유사도 계산 및 % 표시
- [ ] 재작성 결과 편집 가능 텍스트 박스
- [ ] 썸네일 문구 제안 (1줄 훅 카피)

### Phase 5 — 저장 & 내보내기
- [ ] 레퍼런스 즐겨찾기 기능
- [ ] 선택 게시물 폴더로 이미지 저장
- [ ] 캡션 + 재작성본 TXT/엑셀 내보내기
- [ ] 수집 이력 관리

---

## 개발 환경

| 항목 | 버전/내용 |
|------|----------|
| OS | Windows 11 |
| Python | 3.11+ |
| GUI | PyQt6 |
| DB | SQLite3 (내장) |
| AI | Claude API (claude-sonnet-4-6) |
| 크롤러 | Instaloader |
| 유사도 | scikit-learn (TF-IDF + 코사인 유사도) |
| 이미지 | Pillow |
| OCR | pytesseract (선택) |

---

## 의존성 설치

```bash
pip install -r requirements.txt
```

---

## 실행 방법

```bash
python src/main.py
```

---

## 폴더 구조

```
카드뉴스 자동화/
├── README.md               # 이 문서
├── ARCHITECTURE.md         # 아키텍처 설명
├── DESIGN_GUIDE.md         # UI/UX 디자인 가이드
├── requirements.txt        # 의존성
├── config.json             # API키, 설정값
├── src/
│   ├── main.py             # 앱 진입점
│   ├── crawler/
│   │   ├── instagram.py    # Instaloader 크롤러
│   │   └── account_manager.py
│   ├── analyzer/
│   │   ├── engagement.py   # 참여율 계산
│   │   ├── similarity.py   # 유사도 체크
│   │   └── database.py     # SQLite 관리
│   ├── ai/
│   │   ├── claude_client.py # Claude API
│   │   └── caption.py       # 번역·재작성
│   └── gui/
│       ├── main_window.py   # 메인 윈도우
│       ├── account_tab.py   # 계정 관리 탭
│       ├── crawler_tab.py   # 수집 탭
│       ├── ranking_tab.py   # 랭킹 뷰 탭
│       └── caption_tab.py   # 캡션 재작성 탭
├── data/
│   ├── references/          # 수집된 이미지 저장
│   └── cardnews.db          # SQLite DB
└── assets/
    └── 레퍼런스.png
```

---

## 주의사항

- Instagram 크롤링은 공개 계정만 가능
- 저장 수·공유 수는 Instagram에서 비공개 처리 → 수집 불가
- 과도한 크롤링 시 인스타 계정 제한 가능 → 딜레이 설정 필수
- API 키는 config.json에 저장 (절대 GitHub에 올리지 않음)
