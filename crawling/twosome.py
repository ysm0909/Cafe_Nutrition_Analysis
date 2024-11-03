from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
driver.get("https://mo.twosome.co.kr/mn/menuInfoList.do?grtCd=1&pMidCd=01")  # 투썸 메뉴 페이지 URL

# 데이터 저장 구조 초기화
data = {
    "카테고리": [],
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

# 상세 정보 크롤링 함수 정의
def collect_details(category_name, menu_name, info, allergens):
    # 상세 정보 크롤링
    volume = driver.find_element(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[1]/dd').text
    kcal = driver.find_element(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[3]/dd').text
    sodium = driver.find_element(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[7]/dd').text.split('/')[0]
    saturated_fat = driver.find_element(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[6]/dd').text.split('/')[0]
    sugars = driver.find_element(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[4]/dd').text.split('/')[0]
    protein = driver.find_element(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[5]/dd').text.split('/')[0]
    caffeine_elements = driver.find_elements(By.XPATH, '//*[@id="layer-info-popup"]/div[3]/article/div[2]/dl[8]/dd')
    caffeine = caffeine_elements[0].text if caffeine_elements else ""
    
    # 데이터 추가
    data["카테고리"].append(category_name)
    data["메뉴명"].append(menu_name)
    data["정보"].append(info)
    data["용량"].append(volume)
    data["1회제공량(kcal)"].append(kcal)
    data["나트륨 (mg)"].append(sodium)
    data["포화지방 (g)"].append(saturated_fat)
    data["당류 (g)"].append(sugars)
    data["단백질 (g)"].append(protein)
    data["카페인 (mg)"].append(caffeine)
    data["알레르기성분"].append(allergens)

# 페이지 끝까지 스크롤 후 다시 상단으로 이동
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 아래로 스크롤
time.sleep(1)  # 잠시 대기
driver.execute_script("window.scrollTo(0, 0);")  # 다시 위로 스크롤
time.sleep(1)  # 잠시 대기

# 카테고리별로 순회
for category_index in range(2, 5):  # 2, 3, 4 카테고리 인덱스
    try:
        category_xpath = f'//*[@id="midUl"]/li[{category_index}]'
        category_element = driver.find_element(By.XPATH, category_xpath)
        category_name = category_element.text  # 카테고리명 저장
        category_element.click()
        time.sleep(2)

        # 현재 카테고리의 메뉴 개수 파악
        items = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/ul/li/a/div/img')
        item_count = len(items)
        print(category_name)
        print(item_count)

        for item_index in range(1, item_count + 1):
            try:
                # 메뉴 이미지 클릭 전에 스크롤로 위치 조정
                menu_xpath = f'/html/body/div[1]/div/div/ul/li[{item_index}]/a/div/img'
                menu_element = driver.find_element(By.XPATH, menu_xpath)
                driver.execute_script("arguments[0].scrollIntoView();", menu_element)
                time.sleep(0.5)  # 스크롤 후 잠시 대기

                # 메뉴 클릭
                menu_element.click()
                time.sleep(1)

                # 페이지 끝까지 스크롤
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)  # 스크롤 후 잠시 대기
                
                # 메뉴명 및 정보 크롤링
                menu_name = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/dl/dt/strong').text
                info = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/dl/dd/p[2]').text
                # 알레르기 정보 확인 및 크롤링
                allergens_elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[2]/section[2]/p')
                allergens = allergens_elements[0].text if allergens_elements else ""
                time.sleep(1)
                
                info_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/section/div[1]/button')
                info_button.click()
                time.sleep(1)                             
                
                # '아이스' 또는 '핫' 조건에 따른 메뉴명 설정 및 정보 수집
                if driver.find_elements(By.XPATH, '//*[@id="ondo_011I"]'):
                    collect_details(category_name, f"아이스 {menu_name}", info, allergens)
                else:
                    collect_details(category_name, f"핫 {menu_name}", info, allergens)
                    # "아이스" 상태에서 다시 정보 수집
                    if driver.find_elements(By.XPATH, '//*[@id="ondo_010I"]'):
                        driver.find_element(By.XPATH, '//*[@id="ondo_010I"]').click()
                        time.sleep(1)
                        collect_details(category_name, f"아이스 {menu_name}", info, allergens)

                # 뒤로 가기 후 다음 메뉴로 이동
                driver.back()
                time.sleep(1)

            except (NoSuchElementException, ElementClickInterceptedException) as e:
                print(f"Error processing item {item_index} in {category_name}: {e}")
                driver.refresh()
                time.sleep(2)
                break  # 현재 카테고리의 다음 항목으로 이동

    except NoSuchElementException:
        # 카테고리가 없을 경우 무시하고 다음 카테고리로 이동
        continue

# 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(data)
df.to_csv("csv_cafe/twosome_menu.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료")

driver.quit()
