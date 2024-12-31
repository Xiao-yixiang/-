"""
微博爬虫模块
~~~~~~~~~~~~

该模块提供了一个爬虫类，用于从微博获取指定关键词的相关数据。
主要功能包括数据爬取、解析和保存。

主要组件:
- WeiboSpider: 微博爬虫类
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import urllib.parse


class WeiboSpider:
    """微博爬虫类

    用于爬取微博数据的类，支持关键词搜索、数据解析和保存功能。

    Attributes:
        headers (dict): 请求头信息，包含User-Agent和Cookie等
    """
    def __init__(self):
        """初始化微博爬虫实例，设置请求头信息"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Cookie': 'SCF=AuM00mTHz8a0KnqyVmSnRULulsGHxv3oEd44iHHv6KPx4ZSsdN7mbkKkLYLeiCShPRhfHUf46D6rkx4PbOJErVA.; SUB=_2A25KdxX4DeRhGeFG4lsW8S7OyDSIHXVpDRcwrDV8PUNbmtANLRLdkW9NeFknBi6zOkYaRY7gp4IXY9tHoWlMz8Df; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWJsC9mL.s.G1h4WcXzN7nf5JpX5KzhUgL.FoMR1K.NeK5Ee0n2dJLoIEzLxKML1KBLBKnLxKqL1hnLBoMceKnpShB4ehBfP0-ESh.E; ALF=02_1738207912',

            'X-Requested-With': 'XMLHttpRequest'
        }

    def parse_weibo(self, card):
        """解析微博数据卡片

        Args:
            card (dict): 包含微博数据的卡片字典

        Returns:
            dict: 解析后的微博数据，解析失败则返回None

        Raises:
            Exception: 解析过程中的任何错误
        """
        try:
            # 处理type=11的卡片
            if card.get('card_type') == 11:
                card_group = card.get('card_group', [])
                for item in card_group:
                    if item.get('card_type') == 9:
                        mblog = item.get('mblog', {})
                        if mblog:
                            return self.parse_mblog(mblog)
            # 处理type=9的卡片
            elif card.get('card_type') == 9:
                mblog = card.get('mblog', {})
                if mblog:
                    return self.parse_mblog(mblog)
            return None
        except Exception as e:
            print(f"解析微博时出错: {str(e)}")
            return None

    def parse_mblog(self, mblog):
        """解析微博正文内容

        Args:
            mblog (dict): 微博正文内容字典

        Returns:
            dict: 包含以下字段的字典：
                - id: 微博ID
                - bid: 微博bid
                - created_at: 发布时间
                - text: 微博文本
                - is_retweet: 是否为转发
                - reposts_count: 转发数
                - comments_count: 评论数
                - attitudes_count: 点赞数
                - user_name: 用户名
                - user_followers: 粉丝数
                - source: 来源

        Raises:
            Exception: 解析过程中的任何错误
        """
        try:
            # 获取原创微博内容
            text = mblog.get('text', '')
            is_retweet = False
            retweet_text = ''

            # 处理转发的情况
            if 'retweeted_status' in mblog:
                is_retweet = True
                retweet_status = mblog['retweeted_status']
                retweet_text = retweet_status.get('text', '')
                # 组合原创和转发内容
                text = f"{text} // {retweet_text}"

            # 处理时间
            created_at = mblog.get('created_at', '')
            try:
                if '分钟前' in created_at or '小时前' in created_at:
                    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_at = pd.to_datetime(created_at).strftime('%Y-%m-%d %H:%M:%S')
            except:
                created_at = str(created_at)

            return {
                'id': str(mblog.get('id', '')),
                'bid': mblog.get('bid', ''),
                'created_at': created_at,
                'text': text.replace('\n', ' '),
                'is_retweet': 1 if is_retweet else 0,
                'reposts_count': mblog.get('reposts_count', 0),
                'comments_count': mblog.get('comments_count', 0),
                'attitudes_count': mblog.get('attitudes_count', 0),
                'user_name': mblog.get('user', {}).get('screen_name', ''),
                'user_followers': mblog.get('user', {}).get('followers_count', 0),
                'source': mblog.get('source', '')
            }
        except Exception as e:
            print(f"解析微博内容时出错: {str(e)}")
            return None

    def get_weibo_data(self, keyword, page_num=50):
        """获取微博数据

        Args:
            keyword (str): 搜索关键词
            page_num (int, optional): 需要爬取的页数。默认为50页

        Returns:
            pandas.DataFrame: 包含所有爬取数据的数据框

        Examples:
            >>> spider = WeiboSpider()
            >>> df = spider.get_weibo_data('关键词', page_num=10)
        """
        all_data = []
        encoded_keyword = urllib.parse.quote(keyword)
        base_url = 'https://m.weibo.cn/api/container/getIndex'

        print("正在获取搜索参数...")
        containerid = f'100103type=1&q={encoded_keyword}'

        consecutive_empty = 0
        for page in range(1, page_num + 1):
            try:
                params = {
                    'containerid': containerid,
                    'page_type': 'searchall',
                    'page': page
                }

                print(f"\n正在请求第 {page} 页...")
                response = requests.get(base_url, headers=self.headers, params=params)
                json_data = response.json()

                if json_data.get('ok') == 1 and 'data' in json_data:
                    cards = json_data['data'].get('cards', [])
                    print(f"获取到 {len(cards)} 个卡片")

                    card_types = [card.get('card_type') for card in cards]
                    print(f"卡片类型分布: {card_types}")

                    new_posts = 0
                    for card in cards:
                        print(f"\n处理卡片: type={card.get('card_type')}")

                        weibo_data = self.parse_weibo(card)
                        if weibo_data:
                            if not any(post['bid'] == weibo_data['bid'] for post in all_data):
                                all_data.append(weibo_data)
                                new_posts += 1
                                print(f"发现新微博: {weibo_data['bid']}")
                            else:
                                print(f"跳过重复微博: {weibo_data['bid']}")

                    print(f"第 {page} 页成功获取 {new_posts} 条新微博，当前总数：{len(all_data)}")

                    if new_posts == 0:
                        consecutive_empty += 1
                        if consecutive_empty >= 3:
                            print("连续多页没有新数据，停止爬取")
                            break
                    else:
                        consecutive_empty = 0

                    time.sleep(2)
                else:
                    print(f"页面请求失败，响应数据：{json_data}")
                    break

            except Exception as e:
                print(f"处理第 {page} 页时出错: {str(e)}")
                continue

        return pd.DataFrame(all_data)

    def save_to_csv(self, df, filename):
        """保存数据到CSV文件并输出统计信息

        Args:
            df (pandas.DataFrame): 要保存的数据框
            filename (str): CSV文件名

        Note:
            同时会打印数据统计信息，包括：
            - 总微博数
            - 原创/转发分布
            - 时间跨度
            - 平均互动数据
        """
        if not df.empty:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n数据已保存至 {filename}")
            print("\n数据统计：")
            print(f"总微博数：{len(df)}")
            print("\n原创/转发分布：")
            print(df['is_retweet'].value_counts())
            print("\n时间跨度：")
            print(f"最早：{df['created_at'].min()}")
            print(f"最新：{df['created_at'].max()}")

            # 添加更多统计信息
            print("\n互动数据统计：")
            print("平均转发数：", df['reposts_count'].mean())
            print("平均评论数：", df['comments_count'].mean())
            print("平均点赞数：", df['attitudes_count'].mean())
        else:
            print("没有数据可保存")


def main():
    """主函数

    创建爬虫实例并执行数据爬取。
    默认爬取关键词'小谢一审'的相关微博。

    Example:
        >>> python crawler.py
    """
    spider = WeiboSpider()
    keyword = '小谢一审'
    df = spider.get_weibo_data(keyword)

    if not df.empty:
        spider.save_to_csv(df, 'weibo_data_improved.csv')


if __name__ == "__main__":
    main()