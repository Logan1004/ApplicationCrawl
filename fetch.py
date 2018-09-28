from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import mailbot
import pymysql

db = pymysql.connect("localhost", "root", "1234", "CrawlProject")
cursor = db.cursor()


def open(url, keyword):
    driver = webdriver.Chrome()
    driver.implicitly_wait(20)
    driver.get(url)
    locator = (By.ID, 'queryExpr-str')
    try:
        WebDriverWait(driver, 20, 0, 5).until(EC.presence_of_all_elements_located(locator))

    except WebDriverException:
        mailbot.send_mail('1264160868@qq.com', '专利爬取出错，出错位置：#01')
        driver.close()
    finally:
        search = driver.find_element_by_id("queryExpr-str")
        search.send_keys(keyword)
        driver.find_element_by_id("btnSearchHome").click()
    locator = (By.ID, 'idpageSize')
    try:
        WebDriverWait(driver, 20, 0.5).until(EC.presence_of_all_elements_located(locator))
    except WebDriverException:
        mailbot.send_mail('1264160868@qq.com', '专利爬取出错，出错位置：#02')
        driver.close()
    finally:
        select = Select(driver.find_element_by_id('idpageSize'))
        select.select_by_value('50')


    i = 1
    while i < 3:

        locator = (By.XPATH, '//*[@id="idItem49"]/div/div[1]/h3/p[1]/span[1]')
        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_all_elements_located(locator))
        except WebDriverException:
            mailbot.send_mail('1264160868@qq.com', '专利爬取出错，出错位置：#03')
            driver.close()
        finally:
            test = driver.find_element_by_xpath('//*[@id="idItem49"]/div/div[1]/h3/p[1]/span[1]')
            print(test.text)
            while test.text != str(i*50):
                time.sleep(5)
                test = driver.find_element_by_xpath('//*[@id="idItem49"]/div/div[1]/h3/p[1]/span[1]')
            print('page-%d'%i)
            item = driver.find_element_by_id('resultContainer_ab')
            get_info(item.find_elements_by_class_name('item'),keyword)
            driver.find_element_by_id('idPageNext').click()
        i = i + 1
    driver.close()

def get_info(item_list,keyword):
    for item in item_list:
        # if item.get_attribute('id') == '':
        #     continue
        info = {}
        title = item.find_element_by_class_name('title')    #title
        info['title'] = title.text
        # print(title.text)
        info_time = item.find_element_by_class_name('infoAttributive ')
        spans = info_time.find_elements_by_tag_name('span')
        # print(spans[1].text)
        info['apply_time'] = spans[1].text
        info['announce_time'] = spans[3].text
        info_author = item.find_elements_by_class_name('infoAttributive ')[1]
        spans = info_author.find_elements_by_tag_name('span')
        # print(item.text)
        info['owner'] = spans[0].text
        # print(spans[0].text)                     #owner
        get_detail(info,keyword)




def get_detail(info,keyword):
    #在这里写数据库
    #info是一个字典，里面有如下字段'title': 专利的标题 'apply_time': 专利申请时间 'announce_time': 公示时间 'owner': 专利申请人
    sql = "INSERT INTO Application(Title,ApplyTime,AnnounceTime,Owner,Category) VALUES ('%s','%s','%s','%s','%s')" % (info["title"],info['apply_time'],info['announce_time'],info['owner'],keyword[0])
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 执行sql语句
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
        message = "专利信息插入数据库异常！出错位置：#3 出错文件：fetch.py"
        #mailbot.send_mail('1585084146@qq.com', message)
        #mailbot.send_mail('1264160868@qq.com', message)
        #mailbot.send_mail('1228974364@qq.com', message)
        print("234567876543212345678765432")
    print("%s  %s"%(info['title'], info['apply_time']))



def fetch(keyword):
    url = 'http://www.innojoy.com/search/index.html'
    open(url, keyword)

#def get_keyword():
#    key = ['医疗器械', '区块链', '人工智能']
#    return key


if __name__ == "__main__":
    sql = "SELECT Category FROM Keyword"
    try:
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            print(row)
            fetch(row)
    except:
        # 发生错误时回滚
        db.rollback()
        message = "关键词信息获取异常！出错位置：#4 出错文件：fetch.py"
        mailbot.send_mail('1585084146@qq.com', message)
        #mailbot.send_mail('1264160868@qq.com', message)
        #mailbot.send_mail('1228974364@qq.com', message)
        print("234567876543212345678765432")
