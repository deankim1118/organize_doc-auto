import os
import shutil
import re
from logging import root
import tkinter as tk

# 정리할 기본 폴더 (회사 내 문서 폴더 경로)
BASE_DIR = r"C:/Users/deank/Documents/test"  # 실제 경로로 수정하세요.

# 카테고리와 해당 키워드 매핑
CATEGORY_KEYWORDS = {
    "Donation_Receipt": ["Donation", "Donate"],
    "수입": ["수입"],
    "지출": ["지출"],
    "설교": ["설교", "Sermon"],
    "certificate": ["certificate", "camper"],
}

def extract_year(filename):
    """
    파일명에서 2004년 이상(2004~2099)의 연도를 추출.
    연도가 없으면 None 반환.
    """
    # 2004부터 2099까지의 연도를 매칭하는 정규식:
    # "20" + (0[4-9] 또는 [1-9]\d)
    match = re.search(r'20(?:0[4-9]|[1-9]\d)', filename)
    if match:
        return match.group(0)
    return None

def determine_category(filename):
    """
    파일명에 포함된 키워드에 따라 카테고리를 결정.
    해당 키워드가 없으면 '기타' 반환.
    """
    # 파일명을 소문자로 변환하고, 알파벳, 숫자, 공백을 제외한 모든 문자를 공백으로 치환
    normalized_filename = re.sub(r'[^A-Za-z0-9가-힣\s]', ' ', filename.lower())
    # 여러 개의 연속된 공백은 하나의 공백으로 변환
    normalized_filename = re.sub(r'\s+', ' ', normalized_filename).strip()
    
    # 예시: "donation_receipt" → "donation receipt"
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # 각 키워드도 소문자로 변환하여 normalized_filename 안에 존재하는지 비교
            if keyword.lower() in normalized_filename:
                return category
    return "기타"
def is_already_sorted(file_path):
    """
    파일이 이미 BASE_DIR 아래의 정리된 폴더 구조에 있으면 True 반환.
    정리된 폴더 구조의 기준은 BASE_DIR/<년도>/<카테고리>/... 형태여야 함.
    
    - 첫 번째 폴더는 4자리 연도여야 함 (예: "2023")
    - 두 번째 폴더는 CATEGORY_KEYWORDS의 키 중 하나여야 함 (예: "Donation_Receipt", "수입", 등)
    """
    abs_base = os.path.abspath(BASE_DIR)
    abs_file = os.path.abspath(file_path)
    rel_path = os.path.relpath(abs_file, abs_base)
    parts = rel_path.split(os.sep)

    # 정리된 파일은 최소한 년도 폴더와 카테고리 폴더, 그리고 파일명까지 포함해야 함.
    if len(parts) < 3:
        return False

    # 첫 번째 폴더가 4자리 연도인지 확인 (예: 2023)
    if not re.fullmatch(r'(19|20)\d{2}', parts[0]):
        return False

    # 두 번째 폴더가 정해진 카테고리 중 하나인지 확인
    if parts[1] not in CATEGORY_KEYWORDS:
        return False

    return True

def move_file(file_path):
    """
    파일명에서 연도와 카테고리를 추출하여, BASE_DIR/<년도>/<카테고리> 폴더로 이동.
    해당 폴더가 없으면 새로 생성함.
    """
    if not os.path.isfile(file_path):
        return

    file_name = os.path.basename(file_path)
    year = extract_year(file_name)
    if not year:
        print(f"연도 정보 없음 (정리 건너뜀): {file_name}")
        return

    # 파일명에 기반한 카테고리 결정 (예: "donation_receipt_example.pdf" → "Donation_Receipt")
    category = determine_category(file_name)
    
    # 대상 폴더: BASE_DIR/<년도>/<카테고리>
    target_dir = os.path.join(BASE_DIR, year, category)
    os.makedirs(target_dir, exist_ok=True)  # 폴더가 없으면 새로 생성

    target_path = os.path.join(target_dir, file_name)
    counter = 1
    while os.path.exists(target_path):
        name, ext = os.path.splitext(file_name)
        new_name = f"{name}_{counter}{ext}"
        target_path = os.path.join(target_dir, new_name)
        counter += 1

    try:
        shutil.move(file_path, target_path)
        print(f"파일 이동: {file_path} -> {target_path}")
    except Exception as e:
        print(f"이동 오류: {file_path} -> {target_path} : {e}")



def scan_files(base_dir):
    """
    BASE_DIR 내의 모든 파일을 재귀적으로 검색하여,
    이미 정리된 파일은 건너뛰고 정리되지 않은 파일만 move_file()로 처리.
    """
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if is_already_sorted(file_path):
                # 이미 년도 폴더 또는 카테고리 폴더 내에 있다면 건너뛰기
                print(f"이미 정리된 파일 (건너뜀): {file_path}")
                continue
            move_file(file_path)


def on_scan_button():
    """
    '정리 실행' 버튼 클릭 시 호출되는 함수.
    """
    scan_files(BASE_DIR)
    # 정리 완료 후 Tkinter 창 닫기
    root.destroy()
# Tkinter GUI 구성
root = tk.Tk()
root.title("문서 정리 프로그램")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

scan_button = tk.Button(frame, text="정리 실행", command=on_scan_button, width=20, height=2)
scan_button.pack()

root.mainloop()