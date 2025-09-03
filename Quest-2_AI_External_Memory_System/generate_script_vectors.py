# generate_vectors.py

import os
import uuid
import numpy as np
import faiss
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba

# --- 輔助函數 (保持不變) ---
def split_sentences_chinese(text):
    sentences = []
    start = 0
    for i, char in enumerate(text):
        if char in '。？！':
            sentences.append(text[start:i+1].strip())
            start = i + 1
    if start < len(text):
        sentences.append(text[start:].strip())
    return [s for s in sentences if s]

def jieba_tokenizer(text):
    return jieba.lcut(text)

def summarize_text_by_keywords(text, num_sentences=3):
    sentences = split_sentences_chinese(text)
    if len(sentences) <= num_sentences:
        return text
    tfidf_vectorizer = TfidfVectorizer(tokenizer=jieba_tokenizer)
    tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    scores = np.sum(similarity_matrix, axis=1)
    ranked_sentences_indices = np.argsort(scores)[::-1]
    top_n_indices = sorted(ranked_sentences_indices[:num_sentences])
    summary_sentences = [sentences[i] for i in top_n_indices]
    return " ".join(summary_sentences)

def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# --- Faiss 版本的核心函數 ---
def create_and_store_faiss_index(documents_folder, index_path='faiss_index.bin', metadata_path='faiss_metadata.npy'):
    try:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') 
        print("✅ Sentence-Transformers 模型載入成功。")
    except Exception as e:
        print(f"❌ 錯誤：模型載入失敗。請檢查網路連線。錯誤訊息：{e}")
        return

    summaries = []
    ids = []
    
    if os.path.exists(documents_folder):
        print("\n--- 開始處理文件並生成摘要 ---")
        for filename in os.listdir(documents_folder):
            file_path = os.path.join(documents_folder, filename)
            
            try:
                full_text = ""
                if filename.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        full_text = f.read()
                elif filename.endswith(".docx"):
                    full_text = read_docx(file_path)
                else:
                    print(f"⚠️ 略過檔案 {filename}：不支援的檔案類型。")
                    continue
                
                summary = summarize_text_by_keywords(full_text)
                summaries.append(summary)
                ids.append(str(uuid.uuid4()))
                print(f"✅ 已處理並摘要：{filename}")
            except Exception as e:
                print(f"❌ 為 {filename} 產生摘要時發生錯誤：{e}")
                
    else:
        print(f"❌ 錯誤：找不到資料夾 '{documents_folder}'。請檢查路徑。")
        return

    if summaries:
        print("\n--- 開始將摘要轉換為向量並儲存至 Faiss 索引 ---")
        try:
            embeddings = model.encode(summaries).astype('float32')
            
            # 建立 Faiss 索引
            d = embeddings.shape[1] # 向量維度
            index = faiss.IndexFlatL2(d)
            index.add(embeddings)
            
            # 儲存索引和摘要
            faiss.write_index(index, index_path)
            np.save(metadata_path, np.array(summaries))
            
            print(f"✅ Faiss 索引和摘要資料已成功儲存！")
        except Exception as e:
            print(f"❌ 錯誤：Faiss 儲存失敗。錯誤訊息：{e}")
            return
    else:
        print("沒有找到可處理的文件。請檢查 'documents' 資料夾。")

    
# --- 主執行區 ---
if __name__ == "__main__":
    documents_path = r'G:\我的雲端硬碟\RPG_with_AI'
    create_and_store_faiss_index(documents_path)