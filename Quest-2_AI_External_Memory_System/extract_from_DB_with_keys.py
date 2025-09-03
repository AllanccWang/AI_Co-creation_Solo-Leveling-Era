# search_vectors.py

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# --- 語意搜尋函數 (Faiss 版本) ---
def semantic_search_faiss(query, model, index_path, metadata_path, n_results=2):
    """
    執行語意搜尋，從 Faiss 索引中找出與查詢問題最相關的摘要。
    """
    try:
        index = faiss.read_index(index_path)
        summaries = np.load(metadata_path, allow_pickle=True)
    except Exception as e:
        print(f"❌ 錯誤：Faiss 索引或摘要資料載入失敗。請先執行 'generate_vectors.py' 腳本。錯誤訊息：{e}")
        return []

    print(f"✨ 正在搜尋與 '{query}' 相關的舊對話摘要...")
    query_embedding = model.encode([query]).astype('float32')
    
    D, I = index.search(query_embedding, n_results)
    
    results = [summaries[i] for i in I[0]]
    
    return results

# --- 主執行區 ---
if __name__ == "__main__":
    index_file = 'faiss_index.bin'
    metadata_file = 'faiss_metadata.npy'
    
    # 載入模型，用於將查詢問題轉換為向量
    try:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ 查詢模型載入成功。")
    except Exception as e:
        print(f"❌ 錯誤：查詢模型載入失敗。請檢查網路連線。錯誤訊息：{e}")
        exit()

    # 執行互動式搜尋
    print("\n--- 開始語意搜尋 ---")
    
    while True:
        user_query = input("\n請輸入你想查詢的舊對話主題 (輸入 'exit' 離開): ")
        if user_query.lower() == 'exit':
            break

        search_results = semantic_search_faiss(user_query, model, index_file, metadata_file)
        
        print("\n--- 最相關的舊對話摘要 ---")
        if search_results:
            for i, result in enumerate(search_results):
                print(f"    - [{i+1}] {result}")
        else:
            print("沒有找到相關的結果。")
        print("----------------------")
        print("你可以將這些摘要複製到新的 AI 對話中，接續舊的主題。")