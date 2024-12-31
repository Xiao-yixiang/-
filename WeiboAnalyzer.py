"""
微博数据分析模块
~~~~~~~~~~~~~~

该模块提供了一个数据分析类，用于处理和分析微博数据。
主要功能包括数据清洗、话题分类、词频统计和可视化展示。

主要组件:
- WeiboAnalyzer: 微博数据分析类

Example:
    >>> analyzer = WeiboAnalyzer('weibo_data.csv')
    >>> analyzer.create_visualization()
"""

import pandas as pd
import jieba
import numpy as np
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, WordCloud, Page
import re


class WeiboAnalyzer:
    """
    微博数据分析器类

    该类提供了一系列方法来分析微博数据，包括话题分类、词频分析、
    数据可视化等功能。支持自定义停用词，能生成包含饼图、词云图和
    柱状图的可视化HTML页面。

    Attributes:
        df (pandas.DataFrame): 存储微博数据的数据框，包含以下列：
            - text: 微博文本内容
            - created_at: 发布时间
            - comments_count: 评论数
            - reposts_count: 转发数
            - attitudes_count: 点赞数
        stop_words (set): 停用词集合，用于文本分析
        influence_score (float): 影响力得分，由评论、转发、点赞加权计算

    Methods:
        load_stopwords(): 加载停用词表
        clean_text(): 清理文本数据
        analyze_topics(): 分析话题分布
        extract_keywords(): 提取文本关键词
        create_visualization(): 创建数据可视化

    Example:
        >>> analyzer = WeiboAnalyzer('weibo_data.csv')
        >>> analyzer.create_visualization()  # 生成可视化结果
    """
    def __init__(self, file_path, stopwords_path='stopwords.txt'):
        """初始化微博数据分析器

        Args:
            file_path (str): 微博数据CSV文件的路径
            stopwords_path (str, optional): 停用词文件路径。默认为'stopwords.txt'
        """
        self.df = pd.read_csv(file_path)
        max_comments = self.df['comments_count'].max()
        max_reposts = self.df['reposts_count'].max()
        max_attitudes = self.df['attitudes_count'].max()

        self.df['influence_score'] = (
                self.df['comments_count'] / max_comments * 0.4 +
                self.df['reposts_count'] / max_reposts * 0.35 +
                self.df['attitudes_count'] / max_attitudes * 0.25
        )
        self.stop_words = self.load_stopwords(stopwords_path)

    def load_stopwords(self, stopwords_path):
        """加载停用词表

        从文件中加载停用词，并添加额外的项目相关停用词。

        Args:
            stopwords_path (str): 停用词文件路径

        Returns:
            set: 停用词集合

        Raises:
            Exception: 当文件读取失败时抛出异常
        """
        try:
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                stop_words = set([line.strip() for line in f])
            extra_stops = {'小谢', '家暴', '微博', '转发', '评论', 'link', 'http', 'https',
                           '转发微博', '视频', '链接', '网页', '图片', '全文'}
            stop_words.update(extra_stops)
            print(f"成功加载 {len(stop_words)} 个停用词")
            return stop_words
        except Exception as e:
            print(f"加载停用词文件失败: {e}")
            return set()

    def clean_text(self, text):
        """清理文本数据

        删除HTML标签、URL链接、表情符号等干扰内容。

        Args:
            text (str): 原始文本

        Returns:
            str: 清理后的文本
        """
        text = str(text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'#.*?#', '', text)
        return text.strip()

    def get_topic_keywords(self):
        """获取话题关键词字典

        定义不同话题类别及其对应的关键词列表。

        Returns:
            dict: 话题及其关键词的字典，格式为 {话题: [关键词列表]}
        """
        return {
            '判决相关': ['判决', '判刑', '量刑', '死刑', '一审', '法院', '庭审', '刑事',
                         '起诉', '11年', '被告人', '被告', '审判', '宣判', '无期徒刑'],

            '暴力情况': ['家暴', '暴力', '殴打', '伤害', '打人', '踢', '伤势', '粪袋',
                         '住院', '伤', '16次', '打骂', '伤痕', '报警', '施暴'],

            '社会讨论': ['关注', '热议', '舆论', '网友', '声援', '支持', '谴责', '热搜',
                         '讨论', '发声', '话题', '新闻', '报道', '焦点'],

            '法律程序': ['立案', '取证', '证据', '处理', '执法', '公安', '警察', '报案',
                         '起诉', '辩护', '审理', '鉴定', '强制措施'],

            '受害者声音': ['受害者', '小谢', '发声', '控诉', '哭诉', '诉求', '无助',
                           '逃离', '报警', '求救', '遭遇', '经历']
        }

    def analyze_topics(self):
        """分析微博话题分布

        通过关键词匹配对微博内容进行分类，统计不同话题的分布情况。
        同时打印话题分布的统计信息。

        Returns:
            dict: 包含话题及其对应数量的字典
        """
        keywords = self.get_topic_keywords()
        topic_counts = {}

        for text in self.df['text']:
            text = self.clean_text(text)
            text = str(text)
            matched_topics = []

            for topic, words in keywords.items():
                if any(word in text for word in words):
                    matched_topics.append(topic)

            if not matched_topics:
                matched_topics = ['其他讨论']

            for topic in matched_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        print("\n=== 话题分布统计 ===")
        total = sum(topic_counts.values())
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total * 100
            print(f"{topic}: {count} 条 ({percentage:.1f}%)")

        return topic_counts

    def extract_keywords(self, top_n=50):
        """提取文本关键词

        对所有微博文本进行分词，统计高频词。

        Args:
            top_n (int, optional): 返回的高频词数量。默认为50

        Returns:
            list: 包含(词, 频次)元组的列表
        """
        all_text = ' '.join(self.df['text'].apply(self.clean_text))
        words = [word for word in jieba.cut(all_text)
                 if len(word) > 1 and word not in self.stop_words]

        word_counts = Counter(words)
        print(f"\n共发现 {len(word_counts)} 个不同词语")
        print(f"提取前 {top_n} 个高频词")

        return word_counts.most_common(top_n)

    def get_influential_posts(self, top_n=10):
        """获取最具影响力的微博

        基于影响力分数（评论、转发、点赞的加权和）排序。

        Args:
            top_n (int, optional): 返回的微博数量。默认为10

        Returns:
            pandas.DataFrame: 包含最具影响力微博信息的数据框
        """

        return self.df.nlargest(top_n, 'influence_score')[
            ['text', 'comments_count', 'reposts_count', 'attitudes_count', 'influence_score']
        ]

    def create_visualization(self):
        """创建数据可视化

        生成三种可视化图表：
        1. 话题分布饼图
        2. 关键词词云图
        3. 高影响力微博互动分析柱状图

        将结果保存为HTML文件，并打印统计摘要信息。
        """
        def create_topic_pie():
            topic_data = self.analyze_topics()
            pie = (
                Pie(init_opts=opts.InitOpts(width="900px", height="500px"))
                .add(
                    series_name="话题分布",
                    data_pair=[(k, v) for k, v in topic_data.items()],
                    radius=["40%", "75%"],
                    label_opts=opts.LabelOpts(formatter="{b}: {c}条 ({d}%)"),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="话题分布分析"),
                    legend_opts=opts.LegendOpts(
                        orient="vertical",
                        pos_left="85%",
                        pos_top="middle"
                    )
                )
            )
            return pie

        def create_wordcloud():
            words = self.extract_keywords(50)
            wordcloud = (
                WordCloud(init_opts=opts.InitOpts(width="900px", height="500px"))
                .add(
                    series_name="词频",
                    data_pair=words,
                    word_size_range=[20, 100]
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="热词分析"),
                    toolbox_opts=opts.ToolboxOpts()
                )
            )
            return wordcloud

        def create_interaction_bar():
            top_posts = self.get_influential_posts(10)
            bar = (
                Bar(init_opts=opts.InitOpts(width="900px", height="500px"))
                .add_xaxis([f"Top{i + 1}" for i in range(10)])
                .add_yaxis(
                    "评论数",
                    top_posts['comments_count'].tolist(),
                    label_opts=opts.LabelOpts(position="top")
                )
                .add_yaxis(
                    "转发数",
                    top_posts['reposts_count'].tolist(),
                    label_opts=opts.LabelOpts(position="top")
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="高影响力微博互动分析"),
                    xaxis_opts=opts.AxisOpts(
                        axislabel_opts=opts.LabelOpts(rotate=30)
                    ),
                    yaxis_opts=opts.AxisOpts(
                        name="数量",
                        type_="value"
                    ),
                    datazoom_opts=[opts.DataZoomOpts()],
                    toolbox_opts=opts.ToolboxOpts()
                )
            )
            return bar

        # 创建页面布局
        page = Page(layout=Page.SimplePageLayout)
        # 添加图表
        charts = [
            create_topic_pie(),
            create_wordcloud(),
            create_interaction_bar()
        ]
        page.add(*charts)

        # 生成HTML
        page.render("weibo_analysis.html")

        # 输出统计信息
        print("\n=== 数据统计摘要 ===")
        print(f"总微博数：{len(self.df)}")
        print(f"\n=== 最具影响力的微博 TOP5 ===")
        for idx, row in self.get_influential_posts(5).iterrows():
            print(f"\n{self.clean_text(row['text'])[:150]}...")
            print(f"评论数：{row['comments_count']}")
            print(f"转发数：{row['reposts_count']}")
            print(f"点赞数：{row['attitudes_count']}")
            print(f"影响力指数：{row['influence_score']:.3f}")


def main():
    """主函数

    创建WeiboAnalyzer实例，读取数据并生成可视化结果。

    Example:
        python WeiboAnalyzer.py
    """
    analyzer = WeiboAnalyzer('weibo_data_improved.csv', 'stopwords.txt')
    analyzer.create_visualization()


if __name__ == "__main__":
    main()