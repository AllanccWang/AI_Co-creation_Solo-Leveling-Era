import cv2
import numpy as np
import os
import glob
import time

# --- 【使用者可調整參數】 ---
INPUT_DIR = "./"            # 待處理圖片所在的資料夾
OUTPUT_DIR = "images_output"          # 裁切後的圖片輸出總資料夾
COMBINED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "combined") # 整體裁切輸出資料夾
# 已移除 INDIVIDUAL_OUTPUT_DIR
TARGET_WIDTH = 1600                   # 統一縮放後的目標寬度 (px)
PADDING = 20                          # 裁切時在物件邊界額外增加的像素 (可選)
BLUR_KERNEL_SIZE = (15, 15)             # 關鍵調整：用於平滑複雜背景紋理。
MIN_CONTOUR_AREA_RATIO = 0.003        # 最小輪廓面積比例：低於此比例的輪廓將被視為雜訊 (0.3%)
# ------------------------------

def find_main_contours(image):
    """
    執行圖像處理的核心步驟：灰度化、降噪、邊緣偵測、並過濾出主要輪廓。
    """
    h, w = image.shape[:2]
    image_area = h * w
    min_area_threshold = image_area * MIN_CONTOUR_AREA_RATIO
    
    # 1. 灰度化與高斯模糊 (降噪)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, BLUR_KERNEL_SIZE, 0) 

    # 2. Canny 邊緣偵測
    edges = cv2.Canny(blurred_image, 30, 150)

    # 關鍵修復步驟：形態學閉合操作 (Closing)
    # 用於連接因低對比度而斷裂的邊緣
    kernel = np.ones((7, 7), np.uint8) 
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel) 

    # 3. 輪廓提取 (使用修復後的邊緣)
    # 必須使用 cv2.RETR_EXTERNAL 只擷取最外層輪廓
    contours, _ = cv2.findContours(edges_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
    
    # 收集所有輪廓的座標點
    all_points = np.concatenate(contours)

    # 找到所有輪廓點的整體最小/最大座標
    x_min = np.min(all_points[:, :, 0])
    y_min = np.min(all_points[:, :, 1])
    x_max = np.max(all_points[:, :, 0])
    y_max = np.max(all_points[:, :, 1])

    # 應用 Padding 並確保邊界不超出圖片範圍
    x_start = max(0, x_min - padding)
    y_start = max(0, y_min - padding)
    x_end = min(w, x_max + padding)
    y_end = min(h, y_max + padding)

    return x_start, y_start, x_end, y_end

# 調整回傳值，只回傳 combined_crop 和 error_message
def process_image(image_path, target_width, padding):
    """
    主處理流程：讀取、縮放、並裁切圖片。
    回傳值：combined_crop (裁切後的圖片) 或 resized_image (找不到輪廓時的回傳圖), error_message (錯誤訊息)
    """
    try:
        # 1. 讀取圖片與縮放
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

        # 2. 尋找所有主要輪廓
        main_contours = find_main_contours(resized_image)
        
        if not main_contours:
            # 找不到輪廓時，回傳原始縮放圖作為警告，方便使用者檢查
            return resized_image, "Warning: No main object contours found." 
        
        # 3. 執行整體裁切
        x_s, y_s, x_e, y_e = get_bounding_box_coords(main_contours, resized_image.shape, padding)
        combined_crop = resized_image[y_s:y_e, x_s:x_e]
        
        # 移除個別裁切清單的準備步驟

        return combined_crop, None # 回傳 combined_crop 和 None (表示成功)
    
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
        base_name, ext = os.path.splitext(file_name)
        print(f"[{i+1}/{len(image_paths)}] 正在處理: {file_name}")
        
        # 呼叫單張圖片處理函式: 只接收 combined_crop 和 error_message
        combined_crop, error_message = process_image(image_path, TARGET_WIDTH, PADDING) 
        
        # 錯誤處理
        if isinstance(error_message, str) and error_message.startswith("Error:"):
            print(f"  [STATUS] {error_message}")
            continue
        
        # 警告/找不到輪廓處理
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