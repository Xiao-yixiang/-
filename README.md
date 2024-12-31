# 微博话题数据采集与分析系统

基于 Python 的微博话题数据采集与分析系统，以"成都女子两年被家暴16次"案为例实现数据爬取、分析和可视化。

## 功能特点

- 自动爬取微博话题数据
- 话题分类和文本分析  
- 数据可视化（饼图、词云图、柱状图）

## 环境要求

- Python 3.7+
- 依赖包：pandas, jieba, pyecharts, requests

## 使用说明

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置爬虫：
- 在`crawler.py`中替换自己的微博 cookie

3. 运行程序：
```bash 
python main.py
```

4. 选择功能：
- 1: 爬取微博数据
- 2: 分析已有数据
- 3: 完整流程(爬取+分析)
- 4: 退出程序

## 注意事项

- 确保`stopwords.txt`文件存在且正确
- 爬取时建议设置适当页数(默认50页)
- 分析结果将生成`weibo_analysis.html`

## 联系方式

[GitHub](https://github.com/Xiao-yixiang)
