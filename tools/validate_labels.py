#!/usr/bin/env python3
"""
YOLO 라벨 검증 도구
YOLO 형식의 라벨 파일들을 검증하고 문제점을 찾습니다.
"""

import os
from pathlib import Path
import glob

def validate_yolo_label(label_path, num_classes=5):
    """YOLO 라벨 파일을 검증합니다."""
    errors = []
    
    try:
        with open(label_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # 빈 줄 무시
                continue
            
            parts = line.split()
            if len(parts) != 5:
                errors.append(f"줄 {line_num}: 5개 값이 필요하지만 {len(parts)}개 발견")
                continue
            
            try:
                class_id = int(parts[0])
                center_x = float(parts[1])
                center_y = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # 클래스 ID 검증
                if class_id < 0 or class_id >= num_classes:
                    errors.append(f"줄 {line_num}: 잘못된 클래스 ID {class_id} (0-{num_classes-1} 범위)")
                
                # 좌표 범위 검증 (0-1 사이)
                for coord_name, coord_value in [('center_x', center_x), ('center_y', center_y), 
                                              ('width', width), ('height', height)]:
                    if not 0 <= coord_value <= 1:
                        errors.append(f"줄 {line_num}: {coord_name} 값 {coord_value}가 0-1 범위를 벗어남")
                
                # 박스 크기 검증
                if width <= 0 or height <= 0:
                    errors.append(f"줄 {line_num}: 박스 크기가 0 이하 (width: {width}, height: {height})")
                
            except ValueError as e:
                errors.append(f"줄 {line_num}: 숫자 변환 오류 - {str(e)}")
    
    except Exception as e:
        errors.append(f"파일 읽기 오류: {str(e)}")
    
    return errors

def validate_dataset(data_dir="data/raw_images", num_classes=5):
    """데이터셋의 모든 라벨 파일을 검증합니다."""
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"오류: 디렉토리 {data_dir}가 존재하지 않습니다.")
        return
    
    # 라벨 파일 찾기
    label_files = list(data_path.glob("*.txt"))
    
    if not label_files:
        print(f"경고: {data_dir}에서 라벨 파일(.txt)을 찾을 수 없습니다.")
        return
    
    print(f"총 {len(label_files)}개의 라벨 파일을 검증합니다...")
    
    total_errors = 0
    problem_files = []
    
    for label_file in label_files:
        errors = validate_yolo_label(label_file, num_classes)
        
        if errors:
            total_errors += len(errors)
            problem_files.append(label_file.name)
            print(f"\n문제 발견: {label_file.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK: {label_file.name}")
    
    # 결과 요약
    print(f"\n=== 검증 결과 ===")
    print(f"전체 라벨 파일: {len(label_files)}개")
    print(f"문제 있는 파일: {len(problem_files)}개")
    print(f"총 오류 개수: {total_errors}개")
    
    if problem_files:
        print(f"\n문제 파일 목록:")
        for file_name in problem_files:
            print(f"  - {file_name}")
    else:
        print("모든 라벨 파일이 정상입니다!")

def check_image_label_pairs(data_dir="data/raw_images"):
    """이미지와 라벨 파일의 쌍을 확인합니다."""
    data_path = Path(data_dir)
    
    # 이미지 파일 찾기
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(str(data_path / ext)))
    
    # 라벨 파일 찾기
    label_files = list(data_path.glob("*.txt"))
    
    print(f"\n=== 이미지-라벨 쌍 확인 ===")
    print(f"이미지 파일: {len(image_files)}개")
    print(f"라벨 파일: {len(label_files)}개")
    
    # 이미지 파일명 (확장자 제외)
    image_stems = [Path(img).stem for img in image_files]
    label_stems = [label.stem for label in label_files]
    
    # 쌍이 맞지 않는 파일들 찾기
    missing_labels = [stem for stem in image_stems if stem not in label_stems]
    missing_images = [stem for stem in label_stems if stem not in image_stems]
    
    if missing_labels:
        print(f"\n라벨이 없는 이미지 ({len(missing_labels)}개):")
        for stem in missing_labels[:10]:  # 최대 10개만 표시
            print(f"  - {stem}")
        if len(missing_labels) > 10:
            print(f"  ... 및 {len(missing_labels) - 10}개 더")
    
    if missing_images:
        print(f"\n이미지가 없는 라벨 ({len(missing_images)}개):")
        for stem in missing_images[:10]:  # 최대 10개만 표시
            print(f"  - {stem}")
        if len(missing_images) > 10:
            print(f"  ... 및 {len(missing_images) - 10}개 더")
    
    # 완전한 쌍의 개수
    complete_pairs = len(set(image_stems) & set(label_stems))
    print(f"\n완전한 이미지-라벨 쌍: {complete_pairs}개")

def main():
    print("YOLO 라벨 검증을 시작합니다...")
    
    # 기본 설정
    data_dir = "data/raw_images"
    num_classes = 5
    
    # 사용자 입력
    custom_dir = input(f"검증할 디렉토리 (기본값: {data_dir}): ").strip()
    if custom_dir:
        data_dir = custom_dir
    
    # 라벨 검증
    validate_dataset(data_dir, num_classes)
    
    # 이미지-라벨 쌍 확인
    check_image_label_pairs(data_dir)

if __name__ == "__main__":
    main() 