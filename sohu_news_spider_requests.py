#coding=utf-8
"""
  Title: Sohu News Spider
  Version: V0.1
  Author: Leyi Wang
  Date: Last update 2018-05-02
  Email: leyiwang.cn@gmail.com
"""

import time
import sys
import logging
import json
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level = logging.INFO)

def load_url(file_path='sohu_military_start_url_list', mode='r'):
    """
    Load news url files
    
    :params file_path: str, save path of news url file.
    :mode: str, reading mode
    """
    for item in open(file_path, mode):
        yield item.strip()
        
def save_science_start_url(driver,
                           save_path='sohu_science_start_url_list',
                           mode='w'):
    url_start_list = ['http://it.sohu.com',
                      'http://it.sohu.com/911',
                      'http://it.sohu.com/934',
                      'http://it.sohu.com/882',
                      'http://it.sohu.com/913',
                      'http://it.sohu.com/881',
                      'http://it.sohu.com/880',
                      'http://it.sohu.com/936'
                      ]
    driver.get(url_start_list[0])
    hot = [item.get_attribute('href') 
           for item in driver.find_elements_by_xpath('//div[@data-role="left-hot-spots"]/p/a')]
    others = [item.get_attribute('href') 
              for item in driver.find_elements_by_xpath('//div[@data-role="box"]/p/a')]
    sub_link = [item.get_attribute('href') 
                for item in driver.find_elements_by_xpath('//ul[@class="con"]/li/a')]

    url_start_list.extend(hot + others + sub_link)
    with open(save_path, mode) as fout:
        for line in set(url_start_list):
            fout.write(line + '\n')

def save_finance_start_url(driver, save_path='sohu_finance_start_url_list', mode='w'):
    url_start_list = ['http://business.sohu.com',
                      'http://business.sohu.com/994',
                      'http://business.sohu.com/995',
                      'http://business.sohu.com/996',
                      'http://business.sohu.com/997',
                      'http://business.sohu.com/998'
                      ]
    driver.get(url_start_list[0])
    hot = [item.get_attribute('href') 
           for item in driver.find_elements_by_xpath('//div[@data-role="left-hot-spots"]/p/a')]
    others = [item.get_attribute('href') 
              for item in driver.find_elements_by_xpath('//div[@data-role="box"]/p/a')]
    sub_link = [item.get_attribute('href') 
                for item in driver.find_elements_by_xpath('//ul[@class="con"]/li/a')]

    url_start_list.extend(hot + others + sub_link)
    with open(save_path, mode) as fout:
        for line in set(url_start_list):
            fout.write(line + '\n')

def save_military_start_url(driver, save_path='sohu_military_start_url_list', mode='w'):
    url_start_list = ['http://mil.sohu.com',
                      'http://mil.sohu.com/1468',
                      'https://mil.sohu.com/1469',
                      'http://mil.sohu.com/1470',
                      'http://mil.sohu.com/1471',
                      'http://mil.sohu.com/1472'
                      ]
    driver.get(url_start_list[0])
    hot = [item.get_attribute('href') 
           for item in driver.find_elements_by_xpath('//div[@data-role="left-hot-spots"]/p/a')]
    sub_link = [item.get_attribute('href') 
                for item in driver.find_elements_by_xpath('//ul[@class="con"]/li/a')]
    others = [item.get_attribute('href') 
              for item in driver.find_elements_by_xpath('//div[@data-role="box"]/p/a')]
    
    url_start_list.extend(hot + sub_link + others)
    with open(save_path, mode) as fout:
        for line in set(url_start_list):
            fout.write(line + '\n')

def get_news_item_url(driver, start_url_list, wait_times=15):
    """
    get news urls
    
    :params driver: webdriver, an object of webdriver
    :param start_url_list: list, list of starting urls
    :param wait_time: int, the maximum of waiting time
    :return 
    """
    last_num = 0
    curr_num = 1
    sub_list = []
    for start_url in start_url_list:
        count = 0
        driver.get(start_url)
        while True:
            last_item = curr_num
            time.sleep(0.1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            news_item = driver.find_elements_by_xpath('//div[@data-role="news-item"]/h4/a')
            curr_num = len(news_item)
            if last_item == curr_num:
                count += 1
                if count > wait_times:
                    news_url_list = [item.get_attribute('href') for item in news_item]
                    sub_list.extend(news_url_list)
                    print(start_url, len(news_url_list))
                    break
            else:
                count=0
                
    return list(set(sub_list))


def save_news_item_url_list(news_url,
                        file_path='sohu_news_url_list'):
    with open(file_path, 'w') as fout:
        for item in news_url:
            fout.write(item + '\n')

def init_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument('user-agent="Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6"')
    options.add_argument('blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(chrome_options=options)
    #driver.maximize_window()
    #current=driver.window_handles[0]
    driver.set_page_load_timeout(16)
    return driver

def perform(news_url_list,
            news_save_path='sohu_news_military_test',
            error_url_save_path='sohu_error_url',
            domain=r'军事'):
    """
    starting scrawl news by urls
    
    :param news_url_list: list, news urls
    :param news_save_path: str, file save path of news
    :param error_url_save_path: str, crawling failed news URL saved path
    :param domain: str, domain of news
    """
    error_num = 0
    req = requests.session()
    news = {'domain': domain, 'tag':""}
    news_fout = open(news_save_path, 'a')
    error_url_fout = open(error_url_save_path, 'a')
    #driver.set_script_timeout(10)
    for idx, news_url in enumerate(news_url_list):
        try:
            req_res = req.get(news_url)
            code_way = requests.utils.get_encodings_from_content(req_res.text)[0]
            req_res.encoding=code_way
            selector = etree.HTML(req_res.text)
            news['title'] = selector.xpath('//div[@class="text-title"]/h1/text()')[0]
            news['publisher'] = selector.xpath('//div[@id="user-info"]/h4/a/text()')[0]
            news['time'] = selector.xpath('//span[@id="news-time"]/text()')[0]
            text_list = selector.xpath('//article[@id="mp-editor"]/p/text()')
            tag_list = selector.xpath('//span[@class="tag"]/a/text()')
            news['content'] = "".join([item.strip().replace(" ", "") for item in text_list])
            news['tag'] = ",".join([item.strip().replace(" ", "") for item in tag_list])
            news['url'] = news_url
            logging.info('Crawling news ' + str(idx) + ' ' + news_url)
            news_json = json.dumps(news, encoding="UTF-8", ensure_ascii=False)
            news_fout.write(news_json + '\n')
            news_fout.flush()
        except TimeoutException as e:
            error_num += 1
            logging.info('Error ' + str(error_num) + " " + news_url)
            error_url_fout.write(news_url + '\n')
            error_url_fout.flush()
            logging.error(e)
        except Exception as e:
            error_num += 1
            logging.info('Error ' + str(error_num) + " " + news_url)
            error_url_fout.write(news_url + '\n')
            error_url_fout.flush()
            logging.error(e)
    error_url_fout.close()
    news_fout.close()
    
def start_sohu_military():
    """
    starting to scrawl sohu military news
    """
    driver = init_webdriver()
    save_military_start_url(driver)
    start_url_list = load_url(file_path='sohu_military_start_url_list')
    news_url = get_news_item_url(driver, start_url_list)
    save_news_item_url_list(news_url, 'sohu_military_news_url')
    #news_url_list = load_url(file_path='sohu_military_news_url')
    #perform(news_url_list, news_save_path='sohu_news_military', error_url_save_path='sohu_news_military_error')
    driver.quit()
    
def start_sohu_finance():
    """
    starting to scrawl sohu finance news
    """    
    driver = init_webdriver()
    save_finance_start_url(driver)
    start_url_list = load_url('sohu_finance_start_url_list')
    news_url = get_news_item_url(driver, start_url_list)
    save_news_item_url_list(news_url, 'sohu_finance_news_url')
    #news_url_list = load_url(file_path='sohu_finance_news_url')
    #perform(news_url_list,
            #news_save_path='sohu_news_finance',
            #error_url_save_path='sohu_news_finance_error',
            #domain=r"财经")
    driver.quit()

def start_sohu_science():
    """
    starting to scrawl sohu science news
    """    
    driver = init_webdriver()
    #save_science_start_url(driver)
    #start_url_list = load_url('sohu_science_start_url_list')
    #news_url = get_news_item_url(driver, start_url_list)
    #driver.quit()
    #save_news_item_url_list(news_url,'sohu_science_news_url')
    news_url_list = load_url(file_path='sohu_science_news_url')
    perform(news_url_list,
            news_save_path='sohu_news_science',
            error_url_save_path='sohu_news_science_error',
            domain=r"科技")
    
    
if __name__ == '__main__':
    #start_sohu_military()
    #start_sohu_science()
    start_sohu_finance()