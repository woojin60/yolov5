#!/usr/bin/env python3
"""
분산된 데이터 통합 및 분할 도구
여러 폴더에 분산된 이미지들을 raw_images에 모으고 train/valid로 분할합니다.
"""

import os
import shutil
import random
import glob
from pathlib import Path

def consolidate_images():
    """분산된 이미지들을 raw_images 폴더에 통합합니다."""
    print("분산된 이미지 데이터를 통합합니다...")
    
    # 대상 폴더
    raw_images_dir = Path("data/raw_images")
    raw_images_dir.mkdir(parents=True, exist_ok=True)
    
    # 소스 폴더들
    source_folders = [
        "data/pinterest_waste_images",
        "data/scraped_images",
        "data/collected_images"
    ]
    
    consolidated_count = 0
    
    for source_folder in source_folders:
        source_path = Path(source_folder)
        if not source_path.exists():
            continue
            
        print(f"\n{source_folder}에서 이미지 수집 중...")
        
        # 카테고리별 폴더들 확인
        category_folders = []
        for item in source_path.iterdir():
            if item.is_dir() and any(cat in item.name.lower() for cat in ['plastic', 'paper', 'metal', 'glass', 'organic', 'food']):
                category_folders.append(item)
        
        # 직접 이미지 파일들도 확인
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(source_path.glob(ext))
        
        # 카테고리 폴더에서 이미지 수집
        for category_folder in category_folders:
            category_name = category_folder.name
            print(f"  카테고리: {category_name}")
            
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                for img_file in category_folder.glob(ext):
                    # 새 파일명 생성 (중복 방지)
                    new_name = f"{category_name}_{consolidated_count:04d}_{img_file.name}"
                    dest_path = raw_images_dir / new_name
                    
                    try:
                        shutil.copy2(img_file, dest_path)
                        consolidated_count += 1
                        if consolidated_count % 10 == 0:
                            print(f"    통합된 이미지: {consolidated_count}개")
                    except Exception as e:
                        print(f"    복사 실패: {img_file.name} - {e}")
        
        # 직접 이미지 파일들 수집
        for img_file in image_files:
            new_name = f"misc_{consolidated_count:04d}_{img_file.name}"
            dest_path = raw_images_dir / new_name
            
            try:
                shutil.copy2(img_file, dest_path)
                consolidated_count += 1
            except Exception as e:
                print(f"    복사 실패: {img_file.name} - {e}")
    
    print(f"\n총 {consolidated_count}개 이미지가 통합되었습니다.")
    return consolidated_count

def create_sample_labels():
    """샘플 라벨 파일들을 생성합니다."""
    print("\n샘플 라벨 파일을 생성합니다...")
    
    raw_images_dir = Path("data/raw_images")
    image_files = []
    
    # 이미지 파일 찾기
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(raw_images_dir.glob(ext))
    
    if not image_files:
        print("이미지 파일이 없습니다.")
        return 0
    
    label_count = 0
    
    for img_file in image_files:
        label_file = raw_images_dir / f"{img_file.stem}.txt"
        
        # 이미 라벨 파일이 있으면 스킵
        if label_file.exists():
            continue
        
        # 파일명에서 클래스 추정
        filename_lower = img_file.name.lower()
        
        if any(word in filename_lower for word in ['plastic', 'bottle', 'pet']):
            class_id = 0  # plastic
        elif any(word in filename_lower for word in ['paper', 'cardboard', 'cup']):
            class_id = 1  # paper
        elif any(word in filename_lower for word in ['metal', 'aluminum', 'can', 'tin']):
            class_id = 2  # metal
        elif any(word in filename_lower for word in ['glass', 'bottle', 'jar']):
            class_id = 3  # glass
        elif any(word in filename_lower for word in ['organic', 'food', 'waste']):
            class_id = 4  # organic
        else:
            # 랜덤하게 클래스 할당
            class_id = random.randint(0, 4)
        
        # 샘플 바운딩 박스 생성 (중앙에 적당한 크기)
        center_x = random.uniform(0.3, 0.7)
        center_y = random.uniform(0.3, 0.7)
        width = random.uniform(0.2, 0.4)
        height = random.uniform(0.2, 0.4)
        
        # 라벨 파일 생성
        with open(label_file, 'w') as f:
            f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
        
        label_count += 1
    
    print(f"총 {label_count}개 샘플 라벨이 생성되었습니다.")
    print("주의: 실제 라벨링은 LabelImg로 정확히 다시 해야 합니다!")
    return label_count

def split_to_train_valid(train_ratio=0.8):
    """통합된 데이터를 train/valid로 분할합니다."""
    print(f"\n데이터를 {int(train_ratio*100)}% 학습, {int((1-train_ratio)*100)}% 검증으로 분할합니다...")
    
    raw_images_dir = Path("data/raw_images")
    labeled_data_dir = Path("data/labeled_data")
    
    # 출력 디렉토리 생성
    train_images_dir = labeled_data_dir / "train" / "images"
    train_labels_dir = labeled_data_dir / "train" / "labels"
    valid_images_dir = labeled_data_dir / "valid" / "images"
    valid_labels_dir = labeled_data_dir / "valid" / "labels"
    
    for directory in [train_images_dir, train_labels_dir, valid_images_dir, valid_labels_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        # 기존 파일들 정리
        for file in directory.glob("*"):
            file.unlink()
    
    # 이미지-라벨 쌍 찾기
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(raw_images_dir.glob(ext))
    
    valid_pairs = []
    for img_file in image_files:
        label_file = raw_images_dir / f"{img_file.stem}.txt"
        if label_file.exists():
            valid_pairs.append((img_file, label_file))
    
    if not valid_pairs:
        print("이미지-라벨 쌍이 없습니다.")
        return 0, 0
    
    print(f"총 {len(valid_pairs)}개의 이미지-라벨 쌍을 발견했습니다.")
    
    # 랜덤 섞기
    random.shuffle(valid_pairs)
    
    # 분할 지점 계산
    split_point = int(len(valid_pairs) * train_ratio)
    train_pairs = valid_pairs[:split_point]
    valid_pairs_split = valid_pairs[split_point:]
    
    # 학습 데이터 복사
    print(f"학습 데이터 복사 중... ({len(train_pairs)}개)")
    for img_file, label_file in train_pairs:
        shutil.copy2(img_file, train_images_dir / img_file.name)
        shutil.copy2(label_file, train_labels_dir / label_file.name)
    
    # 검증 데이터 복사
    print(f"검증 데이터 복사 중... ({len(valid_pairs_split)}개)")
    for img_file, label_file in valid_pairs_split:
        shutil.copy2(img_file, valid_images_dir / img_file.name)
        shutil.copy2(label_file, valid_labels_dir / label_file.name)
    
    print("데이터 분할 완료!")
    return len(train_pairs), len(valid_pairs_split)

def create_dataset_yaml():
    """YOLO 학습용 dataset.yaml 파일을 생성합니다."""
    yaml_content = """# YOLO 데이터셋 설정
path: data/labeled_data
train: train/images
val: valid/images

# 클래스 정보
nc: 5
names: ['plastic', 'paper', 'metal', 'glass', 'organic']
"""
    
    yaml_file = Path("data/labeled_data/dataset.yaml")
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"YOLO 설정 파일 생성: {yaml_file}")

def cleanup_old_folders():
    """사용하지 않는 폴더들을 정리합니다."""
    print("\n사용하지 않는 폴더를 정리합니다...")
    
    folders_to_remove = [
        "data/pinterest_waste_images",
        "data/scraped_images", 
        "data/collected_images"
    ]
    
    for folder in folders_to_remove:
        folder_path = Path(folder)
        if folder_path.exists():
            choice = input(f"{folder} 폴더를 삭제하시겠습니까? (y/N): ").strip().lower()
            if choice == 'y':
                try:
                    shutil.rmtree(folder_path)
                    print(f"삭제됨: {folder}")
                except Exception as e:
                    print(f"삭제 실패: {folder} - {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("분산된 데이터 통합 및 분할 도구")
    print("=" * 60)
    
    # 1. 이미지 통합
    total_images = consolidate_images()
    
    if total_images == 0:
        print("통합할 이미지가 없습니다.")
        return
    
    # 2. 샘플 라벨 생성 여부 확인
    choice = input("\n샘플 라벨 파일을 생성하시겠습니까? (실제 라벨링 전 테스트용) (y/N): ").strip().lower()
    if choice == 'y':
        create_sample_labels()
    
    # 3. 데이터 분할
    train_count, valid_count = split_to_train_valid()
    
    # 4. YOLO 설정 파일 생성
    create_dataset_yaml()
    
    # 5. 폴더 정리
    cleanup_old_folders()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("데이터 통합 및 분할 완료!")
    print("=" * 60)
    print(f"통합된 이미지: {total_images}개")
    print(f"학습 데이터: {train_count}개")
    print(f"검증 데이터: {valid_count}개")
    print("\n다음 단계:")
    print("1. LabelImg로 정확한 라벨링 수행")
    print("2. 라벨 검증 실행")
    print("3. YOLO 모델 학습 시작")

if __name__ == "__main__":
    main() 