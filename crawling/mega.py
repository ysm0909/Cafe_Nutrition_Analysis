from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')

# Chrome Driver 경로 지정 및 서비스 객체 생성
s = Service(r"selenium/chromedriver.exe")

# 드라이버 초기화
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.mega-mgccoffee.com/menu/?menu_category1=1&menu_category2=1")  # Mega Coffee 메뉴 페이지 URL로 변경

# 데이터 저장 구조 초기화
data = {
    "메뉴명": [],
    "정보": [],
    "용량": [],
    "1회제공량(kcal)": [],
    "나트륨 (mg)": [],
    "포화지방 (g)": [],
    "당류 (g)": [],
    "단백질 (g)": [],
    "카페인 (mg)": [],
    "알레르기성분": []
}

# 페이지별로 메뉴 크롤링
page = 1
while True:
    items = driver.find_elements(By.XPATH, '//*[@id="menu_list"]/li')
    item_count = len(items)

    item_index = 1
    while item_index <= item_count:
        try:
            # 메뉴 이미지 클릭
            menu_xpath = f'//*[@id="menu_list"]/li[{item_index}]/a/div/div[1]/img'
            menu_element = driver.find_element(By.XPATH, menu_xpath)
            ActionChains(driver).move_to_element(menu_element).click().perform()
            time.sleep(1)

            # 각 정보 크롤링
            data["메뉴명"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[1]/div[1]/div[1]/b').text)
            data["정보"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[1]/div[3]').text)
            data["용량"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[1]/div[2]/div[1]').text)
            data["1회제공량(kcal)"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[1]/div[2]/div[2]').text)
            data["나트륨 (mg)"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[2]/ul/li[3]').text)
            data["포화지방 (g)"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[2]/ul/li[1]').text)
            data["당류 (g)"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[2]/ul/li[2]').text)
            data["단백질 (g)"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[2]/ul/li[4]').text)
            data["카페인 (mg)"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[2]/ul/li[5]').text)
            data["알레르기성분"].append(driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[1]/div[4]').text)

            # 추가 클릭
            additional_click = driver.find_element(By.XPATH, f'//*[@id="menu_list"]/li[{item_index}]/div/div[1]/div[1]/div[3]')
            additional_click.click()
            time.sleep(1)
            item_index += 1

        except NoSuchElementException:
            # 현재 페이지의 모든 메뉴 탐색 완료
            break

    # 마지막 페이지 조건: 메뉴 항목이 25개 미만이면 종료
    if item_count < 20:
        break

    # 다음 페이지로 이동
    try:
        if page == 1:
            next_page = driver.find_element(By.XPATH, '//*[@id="board_page"]/li[6]/a')
        else:
            next_page = driver.find_element(By.XPATH, '//*[@id="board_page"]/li[7]/a')
        next_page.click()
        time.sleep(1)
        page += 1
    except (NoSuchElementException, ElementClickInterceptedException):
        # 마지막 페이지에 도달하거나 클릭이 방해될 경우 종료
        break

# 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(data)
df.to_csv("csv_cafe/mega_menu.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료")

driver.quit()