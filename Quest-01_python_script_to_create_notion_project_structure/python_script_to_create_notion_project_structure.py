import requests
import os

# ==== define API KEY ====
NOTION_API_KEY = "********************************"
PARENT_PAGE_ID = "********************************"  # 專案總章父頁面
WORKSPACE_PAGE_ID = "********************************"  # 頂層頁面 ID
# =========================

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# === 建立頂層頁面（雙語內容） ===
def create_top_level_page(title, eng_intro, chi_intro, content_blocks):
    blocks = [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": title}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": eng_intro}}]}
        },
        {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "💬 中文簡介"}}],
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text", "text": {"content": chi_intro}}]}
                    }
                ]
            }
        }
    ] + content_blocks

    payload = {
        "parent": {"page_id": WORKSPACE_PAGE_ID},
        "properties": {
            "title": [{"type": "text", "text": {"content": title}}]
        },
        "children": blocks
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code == 200:
        print(f"✅ 頂層頁面建立成功: {title}")
    else:
        print(f"❌ 頂層頁面建立失敗: {title}", res.text)


# === 專案總章（資料庫） ===
def create_database():
    payload = {
        "parent": {"page_id": WORKSPACE_PAGE_ID},
        "title": [{"type": "text", "text": {"content": "專案總章"}}],
        "properties": {
            "專案名稱": {"title": {}},
            "專案描述": {"rich_text": {}},
            "專案類型": {"select": {"options": []}},
            "技術 / 工具": {"multi_select": {"options": []}},
            "GitHub 連結": {"url": {}},
            "狀態": {
                "select": {
                    "options": [
                        {"name": "進行中", "color": "blue"},
                        {"name": "已完成", "color": "green"},
                        {"name": "待開始", "color": "yellow"}
                    ]
                }
            },
            "開始日期": {"date": {}},
            "截止日期": {"date": {}}
        }
    }
    res = requests.post("https://api.notion.com/v1/databases", headers=headers, json=payload)
    if res.status_code == 200:
        db_id = res.json()["id"]
        print(f"✅ 專案總章建立成功，資料庫 ID: {db_id}")
        return db_id
    else:
        print("❌ 建立資料庫失敗:", res.text)
        return None


# === 專案子頁模板 ===
def create_template_page(database_id):
    content_blocks = [
        {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": "📌 專案名稱與背景"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "專案背景、動機與問題來源"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎯 目標與 KPI"}}]}},
        {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "- 預期成果"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "⚙ 技術細節 / GitHub"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "技術文件請放在 GitHub，這裡可放連結與摘要"}}]}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📷 未來可加圖片與示意圖"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "此區塊預留未來添加圖片或示意圖"}}]}}
    ]
    payload = {
        "parent": {"database_id": database_id},
        "properties": {"專案名稱": {"title": [{"text": {"content": "專案子頁模板"}}]}, "狀態": {"select": {"name": "待開始"}}},
        "children": content_blocks
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code == 200:
        print("✅ 專案子頁模板建立成功")
    else:
        print("❌ 建立模板頁失敗:", res.text)


# === 主流程 ===
if __name__ == "__main__":
    # 1. 遊戲化提示指南（完整內容）
    guide_eng_intro = "This is a practical guide that transforms your interactions with AI into a role-playing game."
    guide_chi_intro = "《如何撰寫遊戲化提示》是一份將你與 AI 的互動轉換為角色扮演遊戲的實用指南。"
    guide_content_blocks = [
        # Step 1
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Step 1: Start a Quest"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Begin by defining your quest with clear objectives and constraints."}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "中文翻譯"}}], "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "首先，用清晰的目標和限制來定義你的任務。"}}]}}]}},
        # Step 2
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Step 2: Report Progress"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Periodically update on your progress and obstacles encountered."}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "中文翻譯"}}], "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "定期更新你的進度以及遇到的障礙。"}}]}}]}},
        # Step 3
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Step 3: Solve Challenges"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Work through problems with the AI, iterating solutions."}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "中文翻譯"}}], "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "與 AI 一起解決問題，不斷迭代方案。"}}]}}]}},
        # Step 4
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Step 4: Seek Feedback"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Ask for feedback from AI as different roles to refine the output."}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "中文翻譯"}}], "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "請 AI 以不同角色提供反饋，以優化成果。"}}]}}]}},
    ]
    create_top_level_page("How to Write Prompts for Playing Games", guide_eng_intro, guide_chi_intro, guide_content_blocks)

    # 2. 上傳文件全文（範例內容，請替換成解析後的完整英文）
    doc_eng_intro = "This document provides best practices and examples for writing prompts for games."
    doc_chi_intro = "本文件提供撰寫遊戲提示的最佳實踐與範例。"
    doc_content_blocks = [
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Full English content from your uploaded document here..."}}]}},
        {"object": "block", "type": "toggle", "toggle": {"rich_text": [{"type": "text", "text": {"content": "中文翻譯"}}], "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "對應的中文翻譯內容放在這裡..."}}]}}]}}
    ]
    create_top_level_page("Reference Document", doc_eng_intro, doc_chi_intro, doc_content_blocks)

    # 3 & 4. 專案總章 + 子頁模板
    db_id = create_database()
    if db_id:
        create_template_page(db_id)
