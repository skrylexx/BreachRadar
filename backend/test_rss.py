import asyncio
import httpx

urls = [
    "https://www.darkreading.com/rss.xml",
    "https://cvefeed.io/rssfeed/latest.xml",
    "https://www.cybersecuritydive.com/feeds/news/",
    "https://feeds.feedburner.com/TheHackersNews",
]

async def test():
    async with httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    ) as client:
        for u in urls:
            try:
                resp = await client.get(u)
                print(f"[{resp.status_code}] {u}")
            except Exception as e:
                print(f"[ERR] {u} : {e}")

asyncio.run(test())
