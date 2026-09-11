def calc_engagement_rate(likes: int, comments: int, followers: int) -> float:
    if followers <= 0:
        return 0.0
    return round((likes + comments) / followers * 100, 4)


def er_label(er: float) -> str:
    if er >= 5.0:
        return "최상위"
    elif er >= 3.0:
        return "상위"
    elif er >= 1.0:
        return "보통"
    else:
        return "낮음"


def er_color(er: float) -> str:
    if er >= 5.0:
        return "#00C896"
    elif er >= 3.0:
        return "#FFA500"
    elif er >= 1.0:
        return "#AAAAAA"
    else:
        return "#FF4444"
