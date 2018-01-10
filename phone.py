# -*- coding:utf8 -*-
from bs4 import BeautifulSoup
import requests
import sys
import pymysql


reload(sys)
sys.setdefaultencoding('utf8')

'''
zol所有手机产品页面
'''
root_url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_613_list_1.html'
headers = {
    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'
}


class Fandb:
    '''定义pymysql类'''
    def __init__(self, host, port, user, password, db, charset='utf8mb4'):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                        password=self.password, db=self.db, charset=self.charset)
            self.cursor = self.conn.cursor()
            self.diccursor = self.conn.cursor(pymysql.cursors.DictCursor)
        except Exception, e:
            logging.error('connect error', exc_info=True)

    def dml(self, sql, val=None):
        self.cursor.execute(sql, val)

    def dql(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.diccursor.close()
        self.conn.close()


'''
返回soup.select
'''
def getSoup(url,selector,header=None):
    web_data = requests.get(url, headers=header)
    soup = BeautifulSoup(web_data.text, 'lxml')
    something = soup.select(selector)
    return something

'''
获取品牌页面,返回一个字典{品牌:url}
'''
def getBrand():
    brand_root = getSoup(root_url,'#J_ParamBrand > a',headers)
    dic_brand = {}
    for i in brand_root[1:]:
        brand_url = i.attrs['href']
        brand_name = i.get_text()
        dic_brand[brand_name] = brand_url
    return dic_brand

base_url = 'http://detail.zol.com.cn'
dic_brand = getBrand()
final_list = []
mydb = Fandb('127.0.0.1', 3306, 'root', 'fanboshi', 'fandb')
sql = 'insert into dic_brand_info(brand,model,alias,url) values(%s,%s,%s,%s)'
'''
按品牌循环,取品牌url
'''
for each_brand in dic_brand:
    sub_url = base_url + dic_brand[each_brand]
    #取每个手机url
    phone = getSoup(sub_url,'#J_PicMode > li > h3 > a',headers)
    '''
    按手机循环,取每个手机详情页url
    '''
    for each_phone in phone:
        each_phone_url = base_url + each_phone['href']
        print(each_phone_url)
        #取手机名称
        model_title = getSoup(each_phone_url,'body > div.product-model.page-title.clearfix > h1',headers)
        #取手机别名
        model_desc = getSoup(each_phone_url,'body > div.product-model.page-title.clearfix > h2',headers)
        if model_desc:
            model_desc_text = model_desc[0].get_text().split('：')[1]
        else:
            model_desc_text = ''

        if model_title:
            model_title_text = model_title[0].get_text()
        else:
            model_title_text = ''
        print(model_title_text)
        print(model_desc_text)

        for i in model_desc_text.split(','):
            #final_list.append([each_brand,model_title_text,i])
            print([each_brand,model_title_text,i,each_phone_url])
            mydb.dml(sql,[each_brand,model_title_text,i,each_phone_url])
            mydb.commit()

mydb.close()


#print(final_list)

# http://detail.zol.com.cn/cell_phone_index/subcate57_list_1.html
# http://detail.zol.com.cn/cell_phone_index/subcate57_1795_list_1.html
#
# model = soup.select('body > div.product-model.page-title.clearfix > h2')
#
# #J_PicMode > li:nth-child(1) > a
#
# print(brand)
#
# #J_ParamBrand > a:nth-child(2)
# for  in brand:
#     print(i.get_text())
# #J_ParamBrand > a:nth-child(2)
#
# >>> index[0].attrs
# {'href': '/cell_phone_index/subcate57_list_1.html', 'class': ['all']}
# >>> index[0].attrs['href']
# '/cell_phone_index/subcate57_list_1.html'