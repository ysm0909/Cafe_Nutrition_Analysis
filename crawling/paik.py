from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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
driver.get("https://paikdabang.com/menu/menu_new/")  # 빽다방 메뉴 페이지 URL

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
    "카페인 (mg)": []
}

# 카테고리 번호 리스트
category_indices = [2, 3, 5]

# 카테고리별로 순회
for category_index in category_indices:
    try:
        # 카테고리 클릭
        category_xpath = f'//*[@id="content-wrap"]/div[1]/ul/li[{category_index}]'
        category_element = driver.find_element(By.XPATH, category_xpath)
        category_name = category_element.text  # 카테고리명 저장
        category_element.click()
        time.sleep(2)

        # 현재 카테고리의 메뉴 개수 파악
        items = driver.find_elements(By.XPATH, '//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li')
        item_count = len(items)
        print(f"{category_name} 카테고리의 메뉴 수: {item_count}")

        # 페이지 끝까지 스크롤 후 다시 상단으로 이동
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 아래로 스크롤
        time.sleep(1)  # 잠시 대기
        driver.execute_script("window.scrollTo(0, 0);")  # 다시 위로 스크롤
        time.sleep(1)  # 잠시 대기

        for item_index in range(1, item_count + 1):
            try:

                # 메뉴 이미지 클릭 전에 스크롤로 위치 조정
                menu_xpath = f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[1]/img'
                menu_element = driver.find_element(By.XPATH, menu_xpath)
                driver.execute_script("arguments[0].scrollIntoView();", menu_element)
                time.sleep(0.5)  # 스크롤 후 잠시 대기

                # 메뉴 클릭
                menu_element.click()
                time.sleep(1)

                # 메뉴명 및 정보 크롤링
                menu_name = driver.find_element(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/h3').text
                info_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/p[1]')
                info = info_elements[0].text if info_elements else ""  # 정보가 없으면 빈 문자열 저장

                # 용량 크롤링
                volume_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/p')
                volume = volume_elements[0].text if volume_elements else ""  # 용량이 없으면 빈 문자열 저장

                # 영양 성분 크롤링
                kcal_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/ul/li[2]/div[2]')
                kcal = kcal_elements[0].text.split(": ")[-1] if kcal_elements else ""  # kcal이 없으면 빈 문자열 저장

                sodium_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/ul/li[3]/div[2]')
                sodium = sodium_elements[0].text if sodium_elements else ""  # 나트륨이 없으면 빈 문자열 저장

                saturated_fat_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/ul/li[5]/div[2]')
                saturated_fat = saturated_fat_elements[0].text if saturated_fat_elements else ""  # 포화지방이 없으면 빈 문자열 저장

                sugars_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/ul/li[4]/div[2]')
                sugars = sugars_elements[0].text if sugars_elements else ""  # 당류가 없으면 빈 문자열 저장

                protein_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/ul/li[6]/div[2]')
                protein = protein_elements[0].text if protein_elements else ""  # 단백질이 없으면 빈 문자열 저장

                caffeine_elements = driver.find_elements(By.XPATH, f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{item_index}]/div[2]/div[2]/ul/li[1]/div[2]')
                caffeine = caffeine_elements[0].text if caffeine_elements else ""  # 카페인이 없으면 빈 문자열 저장

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

                time.sleep(1)

            except NoSuchElementException as e:
                print(f"Error processing item {item_index} in {category_name}: {e}")
                time.sleep(1)
                continue
            
        # 모든 메뉴를 수집한 후 카테고리 목록으로 돌아가기
        driver.back()
        time.sleep(2)

    except NoSuchElementException as e:
        print(f"Error processing category {category_index}: {e}")
        continue

# 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(data)
df.to_csv("csv_cafe/paik_menu.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료")

driver.quit()
