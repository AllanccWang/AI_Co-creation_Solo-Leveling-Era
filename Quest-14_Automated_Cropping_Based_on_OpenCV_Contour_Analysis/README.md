## Project Title: Automated Cropping Based on OpenCV Contour Analysis

### 📋 Project Description

This project aims to develop an automated workflow to replace the repetitive task of resizing images to 1600px wide and manually cropping the main object (e.g., book covers, products).

The core challenge was to achieve **content-aware cropping** under the hardware constraint of a **standard office computer (no dedicated GPU)**, using only CPU-friendly **traditional computer vision techniques** (primarily OpenCV).

---

### 📝 Final Workflow

After multiple iterations and tests, the final output was the `Robust_Crop_Processor.py` script. Its core execution steps are as follows:

1. **Image Loading & Normalization:** Load the image and resize its width to 1600px while maintaining aspect ratio.  
2. **Preprocessing (Denoising):** Convert the image to grayscale and apply a **very large Gaussian blur kernel** (e.g., `(15, 15)`). This step intentionally **sacrifices detail** to **eliminate complex background textures** (e.g., wooden floors, fabric mats).  
3. **Edge Detection (Canny):** Run Canny edge detection on the heavily blurred image to identify regions with sharp pixel changes.  
4. **Morphological Closing:** **(Most critical step)** Apply morphological closing to forcibly connect **broken edges** (caused by low contrast or excessive blur), forming a complete closed contour.  
5. **Contour Extraction & Filtering:** Extract only the **outermost contours (`RETR_EXTERNAL`)** with area above a minimum threshold to filter out noise.  
6. **Cropping & Output:** Calculate the **bounding box** of all valid contours and crop that region (containing all detected objects) for output.  

---

### 💡 Conclusion

This project successfully demonstrated the limits of traditional computer vision (OpenCV) under CPU-only environments.

- **Achievement:** We developed an automated script (`Robust_Crop_Processor.py`) capable of handling **moderately complex backgrounds**. Experiments showed that **extreme denoising** combined with **morphological repair** is essential.  
- **Core Trade-off:** Traditional CV faces an unsolvable dilemma:  
  - **Insufficient denoising (Advanced version):** Complex background textures (e.g., fabric mats) are misidentified as edges, causing contour chaos.  
  - **Excessive denoising (Robust version):** To eliminate texture, extreme blurring also **removes weak object edges**.  
- **Critical Failure Case:** When the **internal contrast** of an object (e.g., text or color blocks on a book) is **higher** than the contrast between the object and its background, the algorithm prioritizes internal contours, resulting in incomplete cropping (as shown in the attachment).  

**Final Verdict:** For this application scenario, the project proves that CPU-only traditional CV techniques **cannot reliably** handle variable shooting backgrounds and complex objects (e.g., cover designs). This solution only works **reliably** under **standardized shooting environments** (e.g., all objects placed on solid-color, high-contrast backgrounds).
