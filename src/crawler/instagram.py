import time
import json
import instaloader
from pathlib import Path
from datetime import datetime

from analyzer.database import upsert_post, update_account_followers
from analyzer.engagement import calc_engagement_rate

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"
REFS_DIR = Path(__file__).parent.parent.parent / "data" / "references"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_loader(username: str = "", password: str = "") -> instaloader.Instaloader:
    L = instaloader.Instaloader(
        download_pictures=True,
        download_videos=False,
        download_video_thumbnails=True,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        compress_json=False,
        quiet=True,
    )
    if username and password:
        try:
            L.login(username, password)
        except Exception as e:
            print(f"[경고] 로그인 실패: {e}")
    return L


def crawl_account(
    account_id: int,
    username: str,
    followers: int,
    post_count: int = 30,
    delay: float = 3.0,
    progress_cb=None,
    log_cb=None,
    stop_flag=None,
):
    config = load_config()
    ig_user = config.get("instagram_username", "")
    ig_pass = config.get("instagram_password", "")

    L = get_loader(ig_user, ig_pass)
    save_dir = REFS_DIR / username
    save_dir.mkdir(parents=True, exist_ok=True)

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        actual_followers = profile.followers
        update_account_followers(account_id, actual_followers)
        followers = actual_followers or followers or 1

        posts = profile.get_posts()
        collected = 0

        for post in posts:
            if stop_flag and stop_flag():
                if log_cb:
                    log_cb(f"[중단] @{username} 수집 중단됨")
                break

            if collected >= post_count:
                break

            try:
                shortcode = post.shortcode
                likes = post.likes
                comments = post.comments
                caption = post.caption or ""
                posted_at = post.date_utc.isoformat() if post.date_utc else ""
                views = post.video_view_count if post.is_video else 0
                post_type = "reel" if post.is_video else ("carousel" if post.typename == "GraphSidecar" else "image")
                er = calc_engagement_rate(likes, comments, followers)

                thumb_path = ""
                try:
                    L.dirname_pattern = str(save_dir)
                    L.filename_pattern = shortcode
                    L.download_post(post, target=str(save_dir))
                    candidates = list(save_dir.glob(f"{shortcode}*.jpg"))
                    if candidates:
                        thumb_path = str(candidates[0])
                except Exception:
                    pass

                upsert_post(account_id, shortcode, {
                    "post_type": post_type,
                    "thumbnail_path": thumb_path,
                    "caption": caption,
                    "likes": likes,
                    "comments": comments,
                    "views": views,
                    "engagement_rate": er,
                    "posted_at": posted_at,
                })

                collected += 1
                if progress_cb:
                    progress_cb(collected, post_count)
                if log_cb:
                    log_cb(f"  [{collected}/{post_count}] {shortcode} — ER {er:.2f}%")

                time.sleep(delay)

            except Exception as e:
                if log_cb:
                    log_cb(f"  [오류] {e}")
                time.sleep(delay)

        if log_cb:
            log_cb(f"✅ @{username} 완료 — {collected}개 수집")
        return collected

    except Exception as e:
        if log_cb:
            log_cb(f"❌ @{username} 실패: {e}")
        return 0
