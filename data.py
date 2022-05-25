import pandas as pd
import pymysql

# 把csv文件写入mysql数据库中


def get_data(file_name):
    # 用pandas读取csv
    # data = pd.read_csv(file_name,engine='python',encoding='gbk')
    pd.set_option('display.max_colwidth', None)  # 设置数据展示列宽
    pd.set_option('display.width', None)  # 设置数据展示宽度 展示所有列
    data = pd.read_csv(file_name, engine='python', encoding='utf-8-sig')
    print(data.head(5))  # 打印前5行

    # 数据库连接
    conn = pymysql.connect(
        user="root",
        port=3306,
        passwd="root",
        db="jd_project",
        host="127.0.0.1",
        charset='utf8'
    )

    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()

    # 数据过滤，替换 nan 值为 None
    data = data.astype(object).where(pd.notnull(data), None)

    for product_id, title, price, commit, shop, pic, brand, icon, good_rate, detail in zip(
            data['商品ID'], data['商品标题'], data['商品价格'], data['评论数量'], data['店铺名字'],
            data['图片链接'], data['商品品牌'], data['商品标签'], data['好评率'], data['商品详情']):

        dataList = [product_id, title, price, commit, shop, pic, brand, icon, good_rate, detail]

        print(dataList)  # 插入的值

        try:
            insertsql = "INSERT INTO jd_project_phone(product_id, title, price, commit, shop, pic, brand, icon, good_rate, detail) " \
                        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(insertsql, dataList)
            conn.commit()
        except Exception as e:
            print("Exception")
            print(e)
            conn.rollback()

    cursor.close()
    # 关闭数据库连接
    conn.close()


def main():
    # 读取数据
    get_data('jingdong.csv')


if __name__ == '__main__':
    main()
