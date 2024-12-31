import os
import time
from crawler import WeiboSpider
from WeiboAnalyzer import WeiboAnalyzer


def print_banner():
    banner = """
    ╔══════════════════════════════════════════╗
    ║        微博数据采集与分析系统            ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    menu = """
    1. 爬取微博数据
    2. 分析已有数据
    3. 完整流程(爬取+分析)
    4. 退出程序

    请选择操作 [1-4]: """
    return input(menu)


def crawl_data():
    print("\n[开始爬取数据]")
    spider = WeiboSpider()

    # 设置爬取参数
    keyword = '小谢一审'
    page_num = int(input("\n请输入要爬取的页数(建议50页): ") or "50")

    # 开始爬取
    print(f"\n正在爬取关键词 '{keyword}' 的微博数据...")
    df = spider.get_weibo_data(keyword, page_num)

    # 保存数据
    filename = 'weibo_data_improved.csv'
    spider.save_to_csv(df, filename)
    print(f"\n数据已保存至 {filename}")

    return filename


def analyze_data(filename='weibo_data_improved.csv'):
    print("\n[开始数据分析]")

    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"\n错误: 找不到数据文件 {filename}")
        return

    # 检查停用词文件
    if not os.path.exists('stopwords.txt'):
        print("\n错误: 找不到停用词文件 stopwords.txt")
        return

    # 开始分析
    analyzer = WeiboAnalyzer(filename, 'stopwords.txt')
    analyzer.create_visualization()
    print("\n分析完成! 可视化结果已保存为 weibo_analysis.html")


def main():
    print_banner()

    while True:
        choice = print_menu()

        if choice == '1':
            crawl_data()

        elif choice == '2':
            filename = input("\n请输入要分析的数据文件名(直接回车使用默认文件): ") or 'weibo_data_improved.csv'
            analyze_data(filename)

        elif choice == '3':
            print("\n[执行完整流程]")
            filename = crawl_data()
            print("\n等待3秒后开始分析...")
            time.sleep(3)
            analyze_data(filename)

        elif choice == '4':
            print("\n感谢使用! 再见!")
            break

        else:
            print("\n无效的选择，请重试")

        input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
    finally:
        print("\n程序已退出")