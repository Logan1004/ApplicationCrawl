from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import mailbot
import random
import pymysql
import xlwt

db = pymysql.connect("localhost", "root", "1234", "CrawlProject")
cursor = db.cursor()
lin_num = 0


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
        search.send_keys(keyword[0])
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
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="idItem0"]/div/div[1]/h3/p[1]/span[2]').click()
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[1])
    i = 1
    while i < 3:

        locator = (By.XPATH, '//*[@id="divPatentList"]/ul/li[50]')
        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_all_elements_located(locator))
        except WebDriverException:
            # mailbot.send_mail('1264160868@qq.com', '专利爬取出错，出错位置：#03')
            print(driver.page_source)
            print(WebDriverException.msg)
            driver.close()
        finally:
            test = driver.find_element_by_xpath('//*[@id="divPatentList"]/ul/li[50]/p[1]/span')
            print(test.text)
            while test.text != str(i*50)+'.':
                time.sleep(5)
                test = driver.find_element_by_xpath('//*[@id="divPatentList"]/ul/li[50]/p[1]/span')
            print('page-%d'%i)
            item = driver.find_element_by_class_name('bd')
            get_info(item.find_elements_by_tag_name('li'), driver,keyword)

            driver.find_element_by_xpath('//*[@id="divPatentList"]/div/a[2]').click()
        i = i + 1
    driver.close()

def get_info(item_list, driver,keyword):
    for item in item_list:
        info = {}
        item.click()
        time_sleep = random.random() + random.randint(1, 5)
        time.sleep(time_sleep)
        locator = (By.XPATH, '//*[@id="simpleDiv"]/div[4]/div[2]/div[1]/p')
        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_all_elements_located(locator))
        finally:
            table = driver.find_element_by_tag_name('tbody')
        locator = (By.XPATH, '//*[@id="simpleDiv"]/div[4]/div[2]/div[1]/p')
        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_all_elements_located(locator))
        finally:
            detail = driver.find_element_by_xpath('//*[@id="simpleDiv"]/div[4]/div[2]/div[1]/p')
        info['detail'] = detail.text
        info['title'] = driver.find_element_by_xpath('//*[@id="infoFixedTop"]/div[1]/div[1]/div[1]/span[1]').text
        info['owner'] = table.find_element_by_xpath('//*[@id="idAS"]').text
        info['apply_time'] = table.find_element_by_xpath('//*[@id="simpleDiv"]/table/tbody/tr[1]/td[2]').text
        info['announce_time'] = table.find_element_by_xpath('//*[@id="simpleDiv"]/table/tbody/tr[2]/td[2]').text
        info['link'] = driver.find_element_by_xpath('//*[@id="baidu_search_title"]/table/tbody/tr/td[3]/a').get_attribute('href')
        get_detail(info,keyword)
        # print(table.find_element_by_xpath('//*[@id="idAS"]').text)
        # print(detail.text)






def get_detail(info,keyword):
    #在这里写数据库
    #info是一个字典，里面有如下字段'title': 专利的标题 'apply_time': 专利申请时间 'announce_time': 公示时间 'owner': 专利申请人 'detail':专利的简介
    sql = "INSERT INTO Application(Title,ApplyTime,AnnounceTime,Owner,Category,Content) VALUES ('%s','%s','%s','%s','%s','%s')" % (
    info["title"], info['apply_time'], info['announce_time'], info['owner'], keyword[0],info['detail'])
    global lin_num
    lin_num = lin_num + 1
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 执行sql语句
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
        message = "专利信息插入数据库异常！出错位置：#3 出错文件：fetch_all.py"
        #mailbot.send_mail('1585084146@qq.com', message)
        #mailbot.send_mail('1264160868@qq.com', message)
        #mailbot.send_mail('1228974364@qq.com', message)
        print(message)
    sheet.write(lin_num, 0, info['title'])
    sheet.write(lin_num, 1, info['apply_time'])
    sheet.write(lin_num, 2, info['announce_time'])
    sheet.write(lin_num, 3, info['owner'])
    sheet.write(lin_num, 4, info['detail'])
    sheet.write(lin_num, 5, keyword[0])
    print("%s  %s: %s"%(info['title'], info['apply_time'], info['detail']))
    print(info['link'])


def fetch(keyword):
    url = 'http://www.innojoy.com/search/index.html'
    open(url, keyword)

#def get_keyword():
#    key = ['医疗器械', '区块链', '人工智能']
#    return key


if __name__ == "__main__":
    wb = xlwt.Workbook("data_out.xls")
    sheet = wb.add_sheet("data-out")
    sheet.write(0, 0, '标题')
    sheet.write(0, 1, '申请时间')
    sheet.write(0, 2, '发布时间')
    sheet.write(0, 3, '作者')
    sheet.write(0, 4, '摘要')
    sheet.write(0, 5, '分类')

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
        message = "关键词信息获取异常！出错位置：#4 出错文件：fetch_all.py"
        # mailbot.send_mail('1585084146@qq.com', message)
        # mailbot.send_mail('1264160868@qq.com', message)
        # mailbot.send_mail('1228974364@qq.com', message)
        print(message)
    wb.save('data_out.xls')
