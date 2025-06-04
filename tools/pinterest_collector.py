#!/usr/bin/env python3
"""
Pinterest 쓰레기 분류 이미지 수집기
Pinterest에서 쓰레기 관련 이미지를 대량으로 수집합니다.
"""

import os
import requests
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import hashlib
import json
import random
from pathlib import Path

class PinterestWasteCrawler:
    def __init__(self, output_dir="data/raw_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.downloaded_count = 0
        self.downloaded_urls = set()
    
    def setup_driver(self):
        """Selenium 웹드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def download_image(self, img_url, filename):
        """이미지 다운로드"""
        try:
            print(f"다운로드 중: {filename}")
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(img_url, timeout=15)
            response.raise_for_status()
            
            filepath = self.output_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(filepath)
            if file_size < 15000:
                os.remove(filepath)
                print(f"파일이 너무 작음: {filename}")
                return False
            
            print(f"다운로드 완료: {filename} ({file_size} bytes)")
            return True
                
        except Exception as e:
            print(f"다운로드 실패: {filename} - {str(e)}")
            return False
    
    def get_filename_from_url(self, url, index):
        """URL에서 파일명 생성"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"waste_{index:04d}_{url_hash}.jpg"
    
    def collect_waste_images(self, max_images=100):
        """Pinterest에서 쓰레기 이미지 수집"""
        print("Pinterest에서 쓰레기 이미지 수집을 시작합니다...")
        
        # 검색어 목록
        search_terms = [
            'plastic bottle waste',
            'paper cup garbage',
            'aluminum can recycling',
            'glass bottle waste',
            'food waste organic',
            'mixed waste bin',
            'recycling center',
            'garbage sorting'
        ]
        
        driver = self.setup_driver()
        
        try:
            for search_term in search_terms:
                if self.downloaded_count >= max_images:
                    break
                
                search_url = f"https://kr.pinterest.com/search/pins/?q={search_term.replace(' ', '%20')}"
                print(f"검색 중: {search_term}")
                
                driver.get(search_url)
                time.sleep(5)
                
                # 스크롤하여 더 많은 이미지 로드
                for _ in range(5):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(2, 4))
                
                # 이미지 요소 찾기
                img_elements = driver.find_elements(By.CSS_SELECTOR, "img[src*='pinimg.com']")
                
                for i, img_element in enumerate(img_elements):
                    if self.downloaded_count >= max_images:
                        break
                    
                    try:
                        img_url = img_element.get_attribute('src')
                        
                        if img_url and img_url not in self.downloaded_urls:
                            # 고해상도 이미지 URL로 변경
                            if '/236x/' in img_url:
                                img_url = img_url.replace('/236x/', '/736x/')
                            
                            filename = self.get_filename_from_url(img_url, self.downloaded_count + 1)
                            
                            if self.download_image(img_url, filename):
                                self.downloaded_urls.add(img_url)
                                self.downloaded_count += 1
                                time.sleep(random.uniform(1, 2))
                    
                    except Exception as e:
                        continue
                
                time.sleep(random.uniform(2, 4))
        
        except Exception as e:
            print(f"수집 중 오류: {str(e)}")
        finally:
            driver.quit()
        
        print(f"총 {self.downloaded_count}개 이미지 수집 완료")
        return self.downloaded_count

def main():
    print("Pinterest 쓰레기 이미지 수집을 시작합니다...")
    print("주의: 교육/연구 목적으로만 사용하세요")
    
    try:
        max_images = int(input("수집할 이미지 수 (기본값: 50): ") or "50")
    except ValueError:
        max_images = 50
    
    crawler = PinterestWasteCrawler()
    crawler.collect_waste_images(max_images)

if __name__ == "__main__":
    main() 