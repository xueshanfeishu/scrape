import requests
import csv
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class WebCrawlerDFS:
    def __init__(self, start_url, max_depth=3, output_file="output.csv"):
        self.start_url = start_url
        self.base_directory = start_url.rsplit("/", 1)[0] + "/"  # 计算基准目录
        self.max_depth = max_depth
        self.visited = set()
        self.output_file = output_file

        # 初始化 CSV 文件，写入表头
        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Content"])

    def normalize_url(self, url):
        """去除 URL 中的 # 及其后面的部分"""
        parsed = urlparse(url)
        return parsed.scheme + "://" + parsed.netloc + parsed.path  # 忽略 fragment（#xxx）

    def get_links_and_content(self, url):
        """提取当前页面所有符合条件的链接，并返回页面正文内容"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return set(), ""

            soup = BeautifulSoup(response.text, "html.parser")
            links = set()
            content = soup.get_text(separator="\n", strip=True)  # 提取纯文本内容

            for a_tag in soup.find_all("a", href=True):
                raw_link = a_tag["href"]
                full_link = self.normalize_url(urljoin(url, raw_link))  # 归一化去除 #

                # 只保留当前目录及其子目录的链接
                if full_link.startswith(self.base_directory):
                    links.add(full_link)

            return links, content
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            return set(), ""

    def save_to_csv(self, url, content):
        """将 URL 和内容写入 CSV"""
        try:
            with open(self.output_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([url, content])
        except Exception as e:
            print(f"写入 CSV 失败: {e}")

    def dfs_crawl(self, url, depth=0):
        """深度优先爬取"""
        url = self.normalize_url(url)  # 处理入口 URL 以去除 #
        if depth > self.max_depth or url in self.visited:
            return

        print(f"Crawling: {url} (Depth: {depth})")
        self.visited.add(url)

        links, content = self.get_links_and_content(url)

        # 存入 CSV
        self.save_to_csv(url, content)

        for link in links:  # **DFS 递归调用**
            self.dfs_crawl(link, depth + 1)

# 示例使用
if __name__ == "__main__":
    start_url = "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html"
    crawler = WebCrawlerDFS(start_url, max_depth=3)
    crawler.dfs_crawl(start_url)

    print(f"\n爬取完成，数据已存入 {crawler.output_file}")
