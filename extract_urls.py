from playwright.sync_api import sync_playwright
import re
import time
import os

def extract_filtered_links(search_keyword, captcha_handler):
    """
    提取搜索关键词对应的所有URL列表。
    :param search_keyword: 搜索关键词
    :param captcha_handler: 验证码处理函数
    :return: 符合条件的URL列表
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 打开搜索页面
        print("[*] 正在访问主页...")
        page.goto("https://cd.ke.com/")
        page.get_by_text("找租房").click()
        page.wait_for_timeout(2000)
        page.locator('//*[@id="keyword-box"]').fill(search_keyword)
        page.locator('//*[@id="findHouse"]').click()
        page.wait_for_timeout(5000)

        # 检查反爬机制
        if "CAPTCHA" in page.title():
            print("[!] 检测到反爬虫机制，截取验证码...")
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = "screenshots/captcha_detected.png"
            page.screenshot(path=screenshot_path)
            captcha_handler(screenshot_path)
            browser.close()
            return []

        # 提取总页数
        total_pages = int(page.locator("div.content__pg").get_attribute("data-totalpage"))
        print(f"[+] 总页数: {total_pages}")

        # 遍历每一页提取URL
        total_links = []
        current_page = 1
        base_url = page.url.split("rs")[0] + "rs"

        while current_page <= total_pages:
            print(f"[*] 提取第 {current_page} 页链接...")
            links = page.locator("a").all()
            page_links = []
            for link in links:
                href = link.get_attribute("href")
                if href and re.match(r"^/zufang/CD\d+\.html$", href):
                    full_link = "https://cd.zu.ke.com" + href
                    if full_link not in total_links:
                        total_links.append(full_link)
                        page_links.append(full_link)

            print(f"[+] 第 {current_page} 页新提取链接数量: {len(page_links)}")
            current_page += 1

            # 跳转到下一页
            if current_page <= total_pages:
                next_page_url = f"{base_url}pg{current_page}"
                time.sleep(2)
                page.goto(next_page_url)
                page.wait_for_timeout(2000)
            else:
                print("[*] 已到达最后一页")

        print(f"[+] 提取到的所有链接总数: {len(total_links)}")
        browser.close()
        return total_links
