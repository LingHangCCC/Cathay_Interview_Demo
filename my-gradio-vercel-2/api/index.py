import pathlib, requests, markdown, nbformat
from fastapi import FastAPI
import gradio as gr
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter

# ——— 個人設定 ———
PROFILE_IMG = "/profile.png"               # 放 public/ 底下
PROJECT_IMAGES = ["/proj1.png", "/proj2.png"]

SELF_INTRO_MD = """## 關於我
您好，我是 **趙駖翰**，目前就讀 **國立政治大學**，主修 **地政學系**，雙主修經濟、副修統計，並完成 **FinTech 專業學程**。

* GPA：3.93 / 4.3（已獲國立政治大學統計所錄取）
* 語言：TOEIC 800
* 技能：R / Python / SAS Viya，熟悉 Word、Excel、PowerPoint

### 實習 / 工作經驗
* *Elegant Real Estate* — 文件歸檔、租售表單與官網維護
* *政大教務處綜合業務組* — 行政助理，協助招生活動與資料彙整
* *可口可樂公司* — 補貨員，物流陳列與庫存巡查
* *水處理公司* — 膜管清洗員，系統薄膜管清洗

### 專案 / 競賽成果
* **SAS Campus Hackathon** 銀牌：動態保費定價模型
* **資科期末專案**：R 語言股票交易預測模型
* 三校聯合街舞大賽總召：協調 50 人團隊，節省 NT$6,000 預算
"""

RAW_IPYNB = "https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/gpt4-1_prompting_guide.ipynb"
RAW_MD    = "https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/gpt4-1_prompting_guide.md"
WEBPAGE   = "https://cookbook.openai.com/examples/gpt4-1_prompting_guide"

# ——— 抓取指南 ———
def fetch_guide() -> str:
    try:
        nb = requests.get(RAW_IPYNB, timeout=30).text
        html, _ = HTMLExporter(template_name="lab").from_notebook_node(
            nbformat.reads(nb, 4)
        )
        return html
    except Exception:
        try:
            md = requests.get(RAW_MD, timeout=30).text
            return markdown.markdown(md, extensions=["fenced_code", "tables"])
        except Exception:
            art = BeautifulSoup(requests.get(WEBPAGE, timeout=30).text,
                                "html.parser").find("article")
            md_txt = "\n\n".join(t.get_text(" ", strip=True) for t in art.find_all(True))
            return markdown.markdown(md_txt)

guide_html = fetch_guide()

# ——— Gradio 介面 ———
with gr.Blocks(title="國泰金控實習展示") as demo:
    with gr.Tab("自我介紹"):
        gr.Markdown(SELF_INTRO_MD)
        gr.Image(value=PROFILE_IMG, show_download_button=False, height=160)
        if PROJECT_IMAGES:
            gr.Gallery(PROJECT_IMAGES, show_download_button=False)

    with gr.Tab("Prompting Guide"):
        gr.HTML(f"<div style='padding:1rem 1.2rem'>{guide_html}</div>")

# ——— FastAPI + Vercel ———
app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")
