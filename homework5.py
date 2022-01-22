from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pymongo import MongoClient

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

driver.execute_script("window.scrollBy(0,1600)","")
wait = WebDriverWait(driver, 30)
button = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'тренде')]/../..")))
button.click()
sleep(3)
carousels = driver.find_elements(By.XPATH ,"//*[name()='mvid-carousel']")
goods = carousels[4].find_elements(By.XPATH ,"//a[@class='ng-star-inserted']/div")
v_trende = []
idf = 0
for i, g in enumerate(goods):
    this_good = {}
    if len(g.text) > 16 and i < 36:
        this_good[str(idf)] = g.text
        v_trende.append(this_good)
        idf += 1

client = MongoClient('mongodb://localhost:27017/')
db = client.goods
result = db.news.insert_many(v_trende)

# вот, как можно получить кнопку горизонтального скролла - но она не понадобилась, так как список всех товаров в тренде отдается разом, не нужно листать вправо.
# chev_right = driver.find_elements(By.XPATH ,"//div[@class='button-size--medium buttons']//*[name()='mvid-icon' and @*='chevron_right']/..")
# chev_right[4].click()