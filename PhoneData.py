import json
import time
import requests
import urllib.request
from lxml import etree  # 将html转换为树形结构
from selenium import webdriver
import csv


# 模拟下拉
def drop_down():
    for x in range(1, 12, 2):
        time.sleep(1)
        j = x / 9
        js = 'document.documentElement.scrollTop = document.documentElement.scrollHeight * %f' % j
        driver.execute_script(js)


driver = webdriver.Chrome()
driver.get("https://www.jd.com")
# driver.get("https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&page=5")  # 打开京东首页
driver.find_element_by_css_selector("#key").send_keys("手机")  # 找到输入框 并输入关键字 手机
driver.find_element_by_css_selector(".button").click()  # 点击搜索按钮


def load_page():
    driver.implicitly_wait(10)  # 隐式等待
    drop_down()  # 模拟下拉
    # 获取所有标签内容
    lis = driver.find_elements_by_css_selector("#J_goodsList > ul > li")  # 获取多个标签
    for li in lis:
        title = li.find_element_by_css_selector(".p-name em").text.replace("\n", "")  # 标题
        price = li.find_element_by_css_selector(".p-price strong i").text  # 价格
        commit = li.find_element_by_css_selector(".p-commit strong a").text  # 评论量
        shop = li.find_element_by_css_selector(".J_im_icon a").text  # 店铺名字
        icons = li.find_elements_by_css_selector(".p-icons i")
        icon = ','.join([i.text for i in icons])  # 列表推导式  ','.join 以逗号把列表中元素拼接
        detail = li.find_element_by_css_selector(".p-img a").get_attribute("href")  # 详情页链接
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "cookie": "PCSYCityID=CN_110000_110100_110106; shshshfpa=ae920f6b-9354-8b14-1196-01e6ce1c63f4-1650889764; shshshfpb=mTwLmVeexJUJrRhTMOqG-VQ; areaId=1; ipLoc-djd=1-2805-55650-0; __jdu=60879375; unpl=JF8EAKtnNSttWU5RARxXHBVDTFtVW1taTUQKaG8MU1VaGVJVSVVLEER7XlVdXhRKEh9sYxRXX1NKUg4fASsSEXteXVdZDEsWC2tXVgQFDQ8VXURJQlZAFDNVCV9dSRZRZjJWBFtdT1xWSAYYRRMfDlAKDlhCR1FpMjVkXlh7VAQrBRobFkNfUlptOEwnM19hA1ZdUUtkBCsDK1BEF1pTVlwOTloEbm4DXF9eT2QEKwE; __jda=76161171.60879375.1650889684.1650893274.1650899273.3; __jdb=76161171.1.60879375|3.1650899273; __jdc=76161171; __jdv=76161171|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_04456d66b67047c7b8698693c7acfa3e|1650899272951; shshshfp=a8436d995435bbf93c1aee3d45d7dc96; shshshsID=ace279066a65297b1a994bd5baff3843_1_1650899274182; 3AB9D23F7A4B3C9B=GC42XTMIGK66ONI3H7IYEC6CHLZAXTWE4MU4HOQ2DFDLK4RNPJ7ZVCDMZS76D6T5WZCRRPTWQ7SZZOHCGFOMTNGAHQ",
            "accept": "* / *",
            "accept - encoding": "gzip, deflate, br",
            "accept - language": "zh - CN, zh;q = 0.9"
        }
        # 给请求增加请求头
        request = urllib.request.Request(detail, headers=headers)
        # 发送请求获取响应数据
        html = urllib.request.urlopen(request).read()
        content = etree.HTML(html)  # 转化为tree 使用xpath进行匹配
        # 获取商品的数据
        brand = content.xpath('//*[@id="parameter-brand"]/li/@title')[0]  # 品牌
        pic = content.xpath('//img[@id="spec-img"]/@data-origin')[0]  # 图片链接
        # 获取商品ID 在商品详情页链接中截取
        product_id = detail.split('/')[-1].split('.')[0]
        # 获取存放评论的链接
        commit_link = 'https://club.jd.com/comment/productPageComments.action?productId=' + product_id + '&score=0&sortType=5&page=1&pageSize=10'
        response = requests.get(commit_link, headers=headers)
        # 爬取到了json格式的评论
        js_data = response.json()
        # 获取其中的好评率
        good_rate = js_data['productCommentSummary'].get('goodRate')  # 好评率
        # 存到字典中
        dit = {
            '商品ID': product_id,
            '商品标题': title,
            '商品价格': price,
            '评论数量': commit,
            '店铺名字': shop,
            '图片链接': pic,
            '商品品牌': brand,
            '商品标签': icon,
            '好评率': good_rate,
            '商品详情': detail,
        }
        csv_writer.writerow([product_id, title, price, commit, shop, pic, brand, icon, good_rate, detail])  # 写入csv
        print(title, price, commit, shop, pic, brand, icon, good_rate, detail, sep=" | ")


if __name__ == '__main__':
    f = open('jingdong.csv', 'w', encoding='utf-8-sig', newline='')
    csv_writer = csv.writer(f)
    # 写入表头
    csv_writer.writerow([
        '商品ID',
        '商品标题',
        '商品价格',
        '评论数量',
        '店铺名字',
        '图片链接',
        '商品品牌',
        '商品标签',
        '好评率',
        '商品详情',
    ])
    for page in range(1, 11):
        print("正在爬取第{}页的内容".format(page))
        time.sleep(2)
        load_page()  # 进行爬取
        driver.find_element_by_css_selector(".pn-next").click()  # 点击下一页
    f.close()

driver.quit()
