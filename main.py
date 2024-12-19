import argparse
from datetime import datetime
from extract_urls import extract_filtered_links
from captcha_handler import recognize_captcha
from extract_details import extract_target_data

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="通过关键词提取租房链接并处理详情页数据")
    parser.add_argument("-k", "--keyword", required=True, help="搜索关键词")
    args = parser.parse_args()

    search_keyword = args.keyword  # 从命令行获取搜索关键词

    # 使用关键词和当前日期生成输出文件名
    current_date = datetime.now().strftime("%Y%m%d")
    output_csv = f"{search_keyword}_{current_date}.csv"

    # 提取URL
    print("[*] 开始提取URL...")
    url_list = extract_filtered_links(search_keyword, recognize_captcha)

    if url_list:
        print(f"[+] 共提取到 {len(url_list)} 个链接，开始处理详情页...")
        extract_target_data(url_list, output_csv)
        print(f"[+] 数据已保存到 {output_csv}")
    else:
        print("[!] 未提取到任何链接，程序终止。")
