from playwright.sync_api import sync_playwright
import csv
import time
import re
from datetime import datetime

def extract_target_data(url_list, output_csv):
    """
    处理详情页数据并保存到CSV，将 test1 中的多个属性提取为独立字段，值作为条目。
    :param url_list: 需要处理的URL列表
    :param output_csv: 保存数据的CSV文件路径
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            extra_http_headers={"Referer": "https://example.com"}
        )
        page = context.new_page()

        # 初始化CSV字段
        base_fields = ["url", "price", "lease_type", "tags", "keywords", "building_name", "layout", "scraped_time"]
        dynamic_fields = set()  # 存储 test1 动态生成的键

        # 第二次遍历URL，提取数据并写入CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = None

            for url in url_list:
                print(f"[*] 正在处理 URL: {url}")
                try:
                    page.goto(url, timeout=60000)
                    time.sleep(2)

                    # 提取页面标题作为楼盘名称和户型信息
                    title = page.title()
                    match_dot = re.search(r"·(\S+)", title)
                    extracted_title = match_dot.group(1) if match_dot else ""
                    match_space = re.search(r"\s(\S+)\s", title)
                    extracted_subtitle = match_space.group(1) if match_space else ""
                    print(f"[+] 提取到的楼盘名称: {extracted_title}")
                    print(f"[+] 提取到的户型信息: {extracted_subtitle}")

                    # 提取价格和租赁方式
                    price_elements = page.locator("//*[@id='aside']/div[1]/span").all()
                    lease_type_elements = page.locator("//*[@id='aside']/ul/li[1]").all()
                    tags_elements = page.locator("//*[@id='aside']/p").all()
                    test1_elements = page.locator("//li[@class='fl oneline']").all()

                    price_list = [price.text_content().strip() for price in price_elements]
                    lease_type_list = []
                    for lease in lease_type_elements:
                        lease_text = lease.text_content().replace("租赁方式：", "").strip()
                        if "整租" in lease_text or "合租" in lease_text:
                            lease_text = "整租" if "整租" in lease_text else "合租"
                        else:
                            lease_text = ""  # 清空无关内容
                        print(f"[DEBUG] 租赁方式提取: {lease_text}")
                        lease_type_list.append(lease_text)

                    # 提取标签数据并清洗
                    tags_list = [tag.text_content().strip().replace("\n", ", ").replace("权属核验", "").strip(', ').replace(" ", "") for tag in tags_elements]
                    cleaned_tags = ", ".join(tags_list)

                    # 提取 test1 数据
                    test1_data = {}
                    for item in test1_elements:
                        ts = item.text_content().strip()
                        ts = re.sub(r"\s+", " ", ts)
                        match = re.search(r"([^：]+)：\s*(.*)", ts)
                        if match:
                            key = match.group(1).strip()
                            value = match.group(2).strip()
                            test1_data[key] = value

                    # 提取关键词
                    html_content = page.content()
                    keywords = ["洗衣机", "空调", "衣柜", "电视", "冰箱", "热水器", "床", "暖气", "宽带", "天然气"]
                    pattern = r'<li[^>]*class=["\']([^"\']*?\bfl oneline\b[^"\']*)["\'][^>]*>.*?(' + '|'.join(keywords) + r').*?</li>'
                    matches = re.findall(pattern, html_content, re.S)
                    matched_keywords = [kw for cls, kw in matches if "facility_no" not in cls]

                    # 确保字段名包含 test1 数据中的键
                    if not writer:
                        fieldnames = base_fields + list(test1_data.keys())
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()

                    # 构建行数据
                    scraped_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row_data = {
                        "url": url,
                        "price": ", ".join(price_list),
                        "lease_type": ", ".join(lease_type_list),
                        "tags": cleaned_tags,
                        "keywords": ", ".join(set(matched_keywords)),
                        "building_name": extracted_title,
                        "layout": extracted_subtitle,
                        "scraped_time": scraped_time
                    }
                    row_data.update(test1_data)  # 添加动态字段数据

                    # 写入CSV文件并输出写入内容
                    writer.writerow(row_data)
                    print(f"[+] 完成数据提取: {url}")
                    print(f"[DEBUG] 写入数据: {row_data}")

                except Exception as e:
                    print(f"[!] 处理失败: {e}")

        browser.close()
        print(f"[+] 数据已全部写入 {output_csv}")
