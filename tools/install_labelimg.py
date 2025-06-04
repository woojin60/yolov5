#!/usr/bin/env python3
"""
LabelImg 설치 및 설정 도구
YOLO 형식 라벨링을 위한 LabelImg를 설치합니다.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_labelimg():
    """LabelImg를 설치합니다."""
    try:
        print("LabelImg 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "labelImg"])
        print("LabelImg 설치 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"설치 실패: {e}")
        return False

def setup_directories():
    """필요한 디렉토리를 생성합니다."""
    directories = [
        "data/raw_images",
        "data/labeled_data/train/images",
        "data/labeled_data/train/labels",
        "data/labeled_data/valid/images",
        "data/labeled_data/valid/labels"
    ]
    
    print("디렉토리 생성 중...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"생성: {directory}")

def create_class_file():
    """클래스 정의 파일을 생성합니다."""
    class_names = [
        "plastic",
        "paper", 
        "metal",
        "glass",
        "organic"
    ]
    
    class_file = Path("data/class_names.txt")
    with open(class_file, 'w', encoding='utf-8') as f:
        for class_name in class_names:
            f.write(f"{class_name}\n")
    
    print(f"클래스 파일 생성: {class_file}")

def run_labelimg():
    """LabelImg를 실행합니다."""
    try:
        print("LabelImg 실행 중...")
        subprocess.run(["labelImg", "data/raw_images", "data/class_names.txt"])
    except FileNotFoundError:
        print("오류: LabelImg가 설치되지 않았거나 PATH에 없습니다.")
        print("다시 설치를 시도하거나 수동으로 실행하세요:")
        print("python -m labelImg data/raw_images data/class_names.txt")

def main():
    print("LabelImg 설치 및 설정을 시작합니다...")
    
    # 디렉토리 설정
    setup_directories()
    
    # 클래스 파일 생성
    create_class_file()
    
    # LabelImg 설치
    if install_labelimg():
        # 실행 여부 확인
        run_choice = input("LabelImg를 바로 실행하시겠습니까? (y/N): ").strip().lower()
        if run_choice == 'y':
            run_labelimg()
        else:
            print("\n수동 실행 방법:")
            print("labelImg data/raw_images data/class_names.txt")
    
    print("\n설정 완료!")
    print("다음 단계:")
    print("1. data/raw_images/ 폴더에 이미지 파일을 넣으세요")
    print("2. LabelImg로 라벨링을 진행하세요")
    print("3. YOLO 형식으로 자동 저장됩니다")

if __name__ == "__main__":
    main() 