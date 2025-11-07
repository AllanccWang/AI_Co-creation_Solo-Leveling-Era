import cv2
import numpy as np
import os
import glob
import time

# --- 設定參數 ---
INPUT_DIR = "./"          # 待處理圖片所在的資料夾
OUTPUT_DIR = "images_output"        # 裁切後的圖片輸出總資料夾
COMBINED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "combined_advanced") # 輸出資料夾名稱略作區分
# 已移除 INDIVIDUAL_OUTPUT_DIR
TARGET_WIDTH = 1600                 # 統一縮放後的目標寬度 (px)
PADDING = 20                        # 裁切時在物件邊界額外增加的像素 (可選)
MIN_CONTOUR_AREA_RATIO = 0.005      # 最小輪廓面積比例：小於 resized_image 面積的 0.5% 則視為雜訊
# ------------------

def find_main_contours(image):
    """
    執行圖像處理的核心步驟：灰度化、降噪、邊緣偵測、並過濾出主要輪廓。
    **使用原始的 (5, 5) 模糊核**
    """
    h, w = image.shape[:2]
    image_area = h * w
    min_area_threshold = image_area * MIN_CONTOUR_AREA_RATIO
    
    # 1. 灰度化與高斯模糊 (原始參數 (5, 5))
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # 2. Canny 邊緣偵測
    edges = cv2.Canny(blurred_image, 30, 150)

    # **未加入形態學閉合**
    
    # 3. 輪廓提取
    # 使用 cv2.RETR_EXTERNAL 只擷取最外層輪廓
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 4. 輪廓過濾：只保留大面積的輪廓 (排除小雜訊)
    main_contours = [
        c for c in contours 
        if cv2.contourArea(c) > min_area_threshold
    ]
    
    return main_contours

def get_bounding_box_coords(contours, image_shape, padding):
    """
    根據輪廓列表計算最小外接矩形 (包含所有輪廓)。
    """
    h, w = image_shape[:2]
    
    all_points = np.concatenate(contours)

    x_min = np.min(all_points[:, :, 0])
    y_min = np.min(all_points[:, :, 1])
    x_max = np.max(all_points[:, :, 0])
    y_max = np.max(all_points[:, :, 1])

    x_start = max(0, x_min - padding)
    y_start = max(0, y_min - padding)
    x_end = min(w, x_max + padding)
    y_end = min(h, y_max + padding)

    return x_start, y_start, x_end, y_end

def process_image(image_path, target_width, padding):
    """
    主處理流程：讀取、縮放、並裁切圖片。
    """
    try:
        original_image = cv2.imread(image_path)
        if original_image is None:
            return None, "Error: Unable to read image."

        h, w = original_image.shape[:2]
        if w != target_width:
            aspect_ratio = target_width / w
            new_h = int(h * aspect_ratio)
            resized_image = cv2.resize(original_image, (target_width, new_h), interpolation=cv2.INTER_AREA)
        else:
            resized_image = original_image

        main_contours = find_main_contours(resized_image)
        
        if not main_contours:
            return resized_image, "Warning: No main object contours found."
        
        # 執行整體裁切
        x_s, y_s, x_e, y_e = get_bounding_box_coords(main_contours, resized_image.shape, padding)
        combined_crop = resized_image[y_s:y_e, x_s:x_e]
        
        # **只回傳 combined_crop**
        return combined_crop, None
    
    except Exception as e:
        return None, f"Error: Unknown processing error: {e}"


def main():
    """主執行函數，用於批次處理圖片"""
    
    # 建立輸出資料夾: 僅建立 COMBINED_OUTPUT_DIR
    for d in [COMBINED_OUTPUT_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
        
    image_paths = glob.glob(os.path.join(INPUT_DIR, "*.jpg")) + \
                  glob.glob(os.path.join(INPUT_DIR, "*.jpeg")) + \
                  glob.glob(os.path.join(INPUT_DIR, "*.png"))
    
    if not image_paths:
        print(f"錯誤：在資料夾 '{INPUT_DIR}' 中找不到任何圖片。請確認路徑與圖片格式。")
        return

    print(f"--- 開始執行批次處理 ({len(image_paths)} 張圖片) ---")
    start_time = time.time()
    
    for i, image_path in enumerate(image_paths):
        file_name = os.path.basename(image_path)
        
        # 呼叫單張圖片處理函式
        combined_crop, error_message = process_image(image_path, TARGET_WIDTH, PADDING) 
        
        if isinstance(error_message, str) and error_message.startswith("Error:"):
            print(f"  [STATUS] {error_message}")
            continue
        
        warning_status = isinstance(error_message, str) and error_message.startswith("Warning:")

        # 儲存整體裁切圖
        output_combined_path = os.path.join(COMBINED_OUTPUT_DIR, file_name)
        cv2.imwrite(output_combined_path, combined_crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        if warning_status:
            print(f"  [STATUS] {error_message} (已儲存原始縮放圖至: {output_combined_path})")
        else:
            print(f"  [SUCCESS] 儲存整體裁切圖至: {output_combined_path}")

    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n--- 批次處理完成 ---")
    print(f"總耗時: {total_time:.2f} 秒")
    print(f"平均每張圖片耗時: {total_time / len(image_paths):.3f} 秒")

if __name__ == "__main__":
    main()