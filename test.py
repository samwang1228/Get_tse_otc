
from selenium import webdriver
driver=webdriver.Chrome() #启动谷歌浏览器
driver.get("http://www.zhihu.com") #访问一个网页
driver.quit() #退出浏览器