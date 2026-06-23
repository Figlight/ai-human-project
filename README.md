# 🏔️ 景区导览服务 AI 数字人 (AI Digital Human Tour Guide)

> **国家文旅产业数字化转型先锋项目** —— 基于开源大模型与 RAG 检索增强技术，构建集**游客多模态交互**与**景区智慧运营大屏**于一体的智能文旅导览平台。

---

## ✨ 核心亮点与特色功能

### 1. 🎨 千人千面个性化定制游览 (Personalized Guide)
* **游览偏好卡片**：游客首次进入系统时，可自主选择 **打卡拍照**、**历史人文**、**自然风光** 或 **休闲亲子** 等偏好。
* **讲解重点动态微调**：大模型（Qwen）根据游客画像自适应调整景点讲解词的侧重点（如：拍照偏好多讲最佳拍摄机位，历史偏好多讲朝代传说）。
* **专属路线高亮**：在景点与路线页面，系统将智能渲染 `✨ 偏好首选` 标签并突出显示匹配度最高的推荐路线。

### 2. 🎙️ 多模态音画同步交互 (Multimodal Interaction)
* **语音与文本输入**：基于 **OpenAI Whisper 模型** 实现精准的 ASR 语音输入识别。
* **音量振幅驱动口型同步**：利用前端 `Web Audio API` 实时提取播放音频的**振幅分贝（Volume）**，动态驱动数字人卡通嘴部按声音大小进行物理收缩，告别机械循环动画。
* **情感表情联动**：大模型在流式回复中进行多维度情感标注，数字人自动感知并切换喜怒哀乐等表情，同时飘出个性化情绪特效。
* **温柔 neural 音色**：搭载升级版 **Edge-TTS** 服务，支持 5 种温柔男女声、知性女声与清亮童声的切换与语速控制。

### 3. 📚 事实性问答准确率 $\ge 90\%$ (RAG Architecture)
* **本地 RAG 向量检索**：基于 **BGE 向量检索模型** 加载本地景区知识库，在无网或弱网下自动降级为高并发 TF-IDF 精准匹配。
* **大模型检索重排 (Rerank)**：大模型对 RAG 检索结果进行二次重排与相关性过滤，确保生成回答的高度事实性，准确度不低于 90%。
* **自动化测评套件**：内置了完整的 `evaluate_rag_accuracy.py` 自动化事实问答评测脚本和大模型裁判（LLM-as-a-Judge）逻辑，支持一键出具准确率分析报告。

### 4. 📊 数字化智慧运营大屏与真实反馈闭环 (Smart Admin Dashboard)
* **实时监控数据大屏**：展示今日服务人次、对话总数、近 7 日满意度趋势（SVG 折线图折线图）以及热点问答 TOP10。
* **游客意见提炼与建议闭环**：后台对游客提交的评星与文本建议进行**实时聚类分词与大模型摘要提炼**，自动在看板上生成具体的服务改进建议（如：“有多位游客提到景区没有遮阳伞租赁，建议补充”），打破传统 Mock 数据，打通业务数据链。
* **安全防护机制**：后端对知识库 QA 维护、文档上传、形象配置等所有敏感写操作接口注入了严密的 **JWT 拦截鉴权依赖**，安全防范非授权访问。

---

## 🛠️ 快速部署与运行

更详细的数据库环境设置与数据导入步骤，请参阅 📖 **[操作与部署手册](file:///d:/vibe-coding-project/ai-human-project/OPERATION_MANUAL.md)**。

### 1. 环境准备
* 确保安装了 **Python 3.12**、**Node.js 18+** 和 **MySQL 8.x**。

### 2. 依赖安装
```bash
# 后端依赖安装
cd backend
pip install -r requirements.txt

# 前端依赖安装
cd ..
npm install
```

### 3. 数据初始化
修改 [backend/.env](file:///d:/vibe-coding-project/ai-human-project/backend/.env) 中的数据库连接和通义千问 `LLM_API_KEY`，然后在根目录下依次执行初始化脚本：
```bash
# 创建数据库表结构
py backend/scripts/create_db.py

# 导入示范景区14万条行为数据及景点详情
py database/import_data.py

# 批量分块并计算本地知识库 RAG 向量索引
py backend/scripts/build_rag_database.py
```

### 4. 一键服务启动
* **启动后端**：双击运行根目录下的 `start_backend.bat`。
* **启动前端**：双击运行根目录下的 `start_frontend.bat`，浏览器打开 `http://localhost:3000`。

---

## 🧪 自动化事实问答测评执行

我们在根目录下提供了可供答辩和评审展示的 RAG 准确率自动化测评方法：

```powershell
# 在 PowerShell 中一键运行评测
$env:PYTHONIOENCODING="utf-8"; py backend/scripts/evaluate_rag_accuracy.py
```
运行完成后，控制台将输出总体准确率，并在 `backend/data/` 目录下生成可视化评估报告 [rag_eval_report.md](file:///d:/vibe-coding-project/ai-human-project/backend/data/rag_eval_report.md)。您可以使用 Markdown 预览功能将其网页化投屏展示给评委。
