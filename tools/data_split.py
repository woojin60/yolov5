#!/usr/bin/env python3
"""
YOLO 데이터셋 분할 도구
라벨링된 이미지와 라벨을 학습용(80%)과 검증용(20%)으로 분할합니다.
"""

import os
import shutil
import random
from pathlib import Path
import glob

def split_dataset(raw_images_dir="data/raw_images", 
                 train_ratio=0.8,
                 output_dir="data/labeled_data"):
    """데이터셋을 학습용과 검증용으로 분할"""
    
    raw_path = Path(raw_images_dir)
    output_path = Path(output_dir)
    
    # 출력 디렉토리 생성
    train_images_dir = output_path / "train" / "images"
    train_labels_dir = output_path / "train" / "labels"
    valid_images_dir = output_path / "valid" / "images"
    valid_labels_dir = output_path / "valid" / "labels"
    
    for directory in [train_images_dir, train_labels_dir, valid_images_dir, valid_labels_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # 이미지 파일 찾기
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(str(raw_path / ext)))
    
    if not image_files:
        print("오류: 이미지 파일을 찾을 수 없습니다.")
        return
    
    # 라벨 파일이 있는 이미지만 필터링
    valid_pairs = []
    for img_path in image_files:
        img_name = Path(img_path).stem
        label_path = raw_path / f"{img_name}.txt"
        
        if label_path.exists():
            valid_pairs.append((img_path, str(label_path)))
    
    if not valid_pairs:
        print("오류: 라벨 파일이 있는 이미지를 찾을 수 없습니다.")
        return
    
    print(f"총 {len(valid_pairs)}개의 이미지-라벨 쌍을 발견했습니다.")
    
    # 랜덤 섞기
    random.shuffle(valid_pairs)
    
    # 분할 지점 계산
    split_point = int(len(valid_pairs) * train_ratio)
    train_pairs = valid_pairs[:split_point]
    valid_pairs = valid_pairs[split_point:]
    
    print(f"학습용: {len(train_pairs)}개")
    print(f"검증용: {len(valid_pairs)}개")
    
    # 파일 복사
    def copy_files(pairs, img_dir, label_dir, dataset_type):
        print(f"{dataset_type} 데이터 복사 중...")
        for img_path, label_path in pairs:
            img_name = Path(img_path).name
            label_name = Path(label_path).name
            
            # 이미지 복사
            shutil.copy2(img_path, img_dir / img_name)
            # 라벨 복사
            shutil.copy2(label_path, label_dir / label_name)
    
    copy_files(train_pairs, train_images_dir, train_labels_dir, "학습용")
    copy_files(valid_pairs, valid_images_dir, valid_labels_dir, "검증용")
    
    print("데이터 분할 완료!")
    print(f"출력 경로: {output_path.absolute()}")

def main():
    print("YOLO 데이터셋 분할을 시작합니다...")
    
    # 기본 설정
    raw_dir = "data/raw_images"
    train_ratio = 0.8
    
    # 사용자 입력
    custom_ratio = input(f"학습 데이터 비율 (기본값: {train_ratio}): ").strip()
    if custom_ratio:
        try:
            train_ratio = float(custom_ratio)
            if not 0.1 <= train_ratio <= 0.9:
                print("경고: 비율은 0.1~0.9 사이여야 합니다. 기본값 사용.")
                train_ratio = 0.8
        except ValueError:
            print("경고: 잘못된 입력입니다. 기본값 사용.")
    
    split_dataset(raw_dir, train_ratio)

if __name__ == "__main__":
    main() 