from ai.claude_client import ask
from analyzer.similarity import calc_similarity


TRANSLATE_SYSTEM = """당신은 인스타그램 헬스/라이프스타일 콘텐츠 전문 번역가입니다.
영어 캡션을 자연스러운 한국어 인스타그램 캡션으로 번역하세요.
해시태그는 한국어로 변환하되 #기호는 유지하세요.
이모지는 그대로 유지하세요."""

REWRITE_SYSTEM = """당신은 인스타그램 헬스/라이프스타일 콘텐츠 크리에이터입니다.
주어진 캡션을 참고해서, 원본과 유사도 75% 이하가 되도록 새로운 캡션을 작성하세요.
핵심 메시지와 주제는 유지하되, 문장 구조·표현·순서를 완전히 바꾸세요.
한국 인스타그램 감성에 맞게 자연스럽고 공감 가는 문체로 작성하세요.
해시태그 10~15개를 포함하세요."""

HOOK_SYSTEM = """당신은 인스타그램 카드뉴스 썸네일 카피라이터입니다.
주어진 캡션 내용을 바탕으로 클릭을 유도하는 강렬한 썸네일 문구 3가지를 제안하세요.
각각 15자 이내로, 호기심·공감·놀라움 중 하나를 자극해야 합니다.
번호 목록으로만 출력하세요."""


def translate_caption(caption: str) -> str:
    if not caption:
        return ""
    return ask(TRANSLATE_SYSTEM, f"다음 캡션을 번역해주세요:\n\n{caption}")


def rewrite_caption(caption: str, max_attempts: int = 3) -> tuple[str, float]:
    if not caption:
        return "", 0.0

    for attempt in range(max_attempts):
        rewritten = ask(
            REWRITE_SYSTEM,
            f"다음 캡션을 재작성해주세요 (시도 {attempt+1}/{max_attempts}):\n\n{caption}"
        )
        similarity = calc_similarity(caption, rewritten)
        if similarity <= 75.0:
            return rewritten, similarity

    return rewritten, similarity


def suggest_hooks(caption: str) -> list[str]:
    if not caption:
        return []
    result = ask(HOOK_SYSTEM, f"캡션 내용:\n\n{caption}")
    lines = [l.strip() for l in result.strip().splitlines() if l.strip()]
    return lines[:3]
