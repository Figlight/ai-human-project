import re
from typing import Optional
from backend.config import settings


class LLMService:
    def __init__(self):
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        """初始化 LangChain LLM"""
        if settings.LLM_API_KEY:
            try:
                from langchain_community.chat_models import ChatTongyi
                
                # 使用 DashScope API Key
                self.llm = ChatTongyi(
                    model=settings.LLM_MODEL,
                    dashscope_api_key=settings.LLM_API_KEY,
                    temperature=0.7,
                    max_tokens=1024,
                    streaming=True,  # 启用流式输出
                )
                print(f"[SUCCESS] LangChain ChatTongyi 初始化成功 (模型: {settings.LLM_MODEL})")
            except Exception as e:
                print(f"[ERROR] LangChain ChatTongyi 初始化失败: {e}")
                self.llm = None
        else:
            print("[WARNING] LLM_API_KEY 未配置，使用 Mock 模式")

    async def chat(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
        preference: Optional[str] = None,
    ) -> tuple[str, str]:
        """非流式对话"""
        if self.llm:
            return await self._api_chat(prompt, context, system_prompt, history, preference)
        return self._mock_chat(prompt, context, preference)

    def _build_messages(
        self,
        prompt: str,
        context: Optional[str],
        system_prompt: Optional[str],
        history: Optional[list[dict]] = None,
        preference: Optional[str] = None,
    ) -> list:
        """构建消息列表"""
        messages = []
        
        # System prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            base_system = (
                "你是一位热情、专业、贴心的景区金牌导游“小导”，请用亲切、自然的口语化语气回答游客问题。\n\n"
                "【回答原则】\n"
                "1. 融入语境：如果提供了参考信息，请将其中关键的客观事实（如景点高度、票价、历史等）巧妙自然地融入你所描述的游览情境中，严禁机械僵硬地照抄或背诵原文。\n"
                "2. 语气生动：多使用亲切口语化的语气词（如“呀”、“哦”、“呢”、“瞧”），你可以假装在现场带着游客游览，用热情的导游口吻介绍。\n"
                "3. 互动建议：适时关心游客，如询问“您现在走到哪儿啦？”、“今天有点热，要多喝水哦”或推荐周边的配套设施或配套景点。\n"
                "4. 口语化设计：避免输出复杂的 Markdown 列表、粗体符号（如 ** 等，但保留常规文字），使回答非常适合直接转化为数字人的语音发音。\n"
                "5. 情感标注：在回答末尾用【情绪:xxx】标注情感（happy/sad/neutral/surprised/excited）。\n"
                "6. 绝对字数限制（重要）：请务必控制回答的总字数在 150 到 200 字之间（严格绝对不能超过 200 字），口语表达应极度精炼，避免任何长篇大论。\n"
                "7. 严格禁止 Emoji 表情：在你的回答正文中，绝对禁止输出任何 Emoji 表情符号（如 🌿、✨、🦌、🍂、🌸、🏛️、📸、👨‍👩‍👧 等），请确保只输出纯中文字符和基础标点，以免语音朗读流畅。\n"
                "8. 多段换行：在介绍和讲解时必须进行合理的分段换行。每段话讲完一个意思（大约2-3句话）就要换行，段落与段落之间使用换行进行分隔，确保文字排版清爽，提高游客的阅读体验。"
            )
            
            # 融入游客兴趣偏好讲解画像指示
            if preference == "history":
                base_system += (
                    "\n\n"
                    "【游客画像与讲解重点：历史人文偏好】\n"
                    "该游客非常喜欢景点的历史背景、文化渊源、古迹典故和传说故事。\n"
                    "请将你的讲解重点放在历史典故、文化考究、建筑背景、名人足迹等方面。描述要严谨且富有文化底蕴，讲故事时要绘声绘色，引领游客感受历史的厚重。"
                )
            elif preference == "photo":
                base_system += (
                    "\n\n"
                    "【游客画像与讲解重点：打卡拍照偏好】\n"
                    "该游客非常喜欢寻找景区内最出片、最适合拍照摄影的机位。\n"
                    "请将你的讲解重点放在最佳拍照位置、拍摄构图建议、小众打卡点、最佳拍摄时间（如晨光/夕阳下如何出片）、色彩光线搭配等视觉效果方面，像一位专业摄影指导一样告诉游客如何拍出极具美感的大片。"
                )
            elif preference == "nature":
                base_system += (
                    "\n\n"
                    "【游客画像与讲解重点：自然风光偏好】\n"
                    "该游客非常喜欢亲近大自然，向往山水、竹林、花海的幽静与治愈。\n"
                    "请将你的讲解重点放在景区的自然生态、奇特地貌、动植物种类、山林溪涧的感官体验（如微风拂面、溪流声、草木气息）上。讲解语调要舒缓、柔和，带给游客心灵的放松与安宁。"
                )
            elif preference == "family":
                base_system += (
                    "\n\n"
                    "【游客画像与讲解重点：休闲亲子偏好】\n"
                    "该游客是带孩子或老人出游，更加关注游览的舒适度、趣味性和便利性。\n"
                    "请将你的讲解重点放在景区内的休息区、平缓路线、无障碍通道/母婴室、亲子游乐设施、萌宠互动以及美食街小吃推荐上。讲解提示要贴心温暖，并增加童趣幽默的互动元素，让全家都感到开心方便。"
                )

            messages.append({
                "role": "system",
                "content": base_system
            })
        
        # Context (RAG 检索结果)
        if context:
            messages.append({
                "role": "system",
                "content": f"以下是相关的景区知识，请参考这些信息回答问题：\n{context}"
            })
        
        # History (多轮对话历史)
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # User question with embedded strict constraints to override RAG context inflation
        user_content = (
            f"{prompt}\n\n"
            "(注意：作为景区金牌导游，请用亲切口语回答。你的回答总字数必须严格控制在 150 到 200 字之间（绝对不能超过 200 字！）。"
            "每段话讲完一个意思（大约2-3句话）就要换行，段落与段落之间直接分段换行分隔。口语表达极度精炼，避免任何长篇大论，且绝对禁止输出任何 Emoji 表情符号。)"
        )
        messages.append({"role": "user", "content": user_content})
        
        return messages

    async def _api_chat(
        self,
        prompt: str,
        context: Optional[str],
        system_prompt: Optional[str],
        history: Optional[list[dict]] = None,
        preference: Optional[str] = None,
    ) -> tuple[str, str]:
        """调用 LangChain LLM API"""
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        messages = self._build_messages(prompt, context, system_prompt, history, preference)
        
        # 转换为 LangChain 消息格式
        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] in ("assistant", "ai"):
                lc_messages.append(AIMessage(content=msg["content"]))
        
        try:
            # 调用 LLM
            response = await self.llm.ainvoke(lc_messages)
            content = response.content
            
            # 提取情感和清理文本
            emotion = self._extract_emotion(content)
            clean_content = self._remove_emotion_tag(content)
            
            return clean_content, emotion
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return self._mock_chat(prompt, context, preference)

    async def chat_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
        preference: Optional[str] = None,
    ):
        """流式对话 - 使用 LangChain 的流式输出"""
        if not self.llm:
            reply, emotion = self._mock_chat(prompt, context, preference)
            yield reply, reply, emotion
            return

        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        messages = self._build_messages(prompt, context, system_prompt, history, preference)
        
        # 转换为 LangChain 消息格式
        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] in ("assistant", "ai"):
                lc_messages.append(AIMessage(content=msg["content"]))
        
        full = ""
        try:
            # 使用 LangChain 的流式 API
            async for chunk in self.llm.astream(lc_messages):
                if hasattr(chunk, 'content') and chunk.content:
                    delta = chunk.content
                    full += delta
                    yield delta, full, None
        except Exception as e:
            print(f"流式调用失败: {e}")
            # 降级为非流式
            reply, emotion = await self._api_chat(prompt, context, system_prompt, history, preference)
            yield reply, reply, emotion
            return

        # 提取最终情感
        emotion = self._extract_emotion(full)
        clean = self._remove_emotion_tag(full)
        yield "", clean, emotion

    def _mock_chat(self, prompt: str, context: Optional[str], preference: Optional[str] = None) -> tuple[str, str]:
        """Mock 回复（当 API 不可用时）"""
        # If preference is provided, customize replies
        if preference == "history":
            replies = {
                "古塔": "【历史人文重点】\n\n这座古塔始建于唐代，高约45米，是典型的砖石阁楼式建筑。\n\n相传它是为了存放高僧带回的名贵经卷而建，塔身上刻有精细的砖雕和古老碑文，经历了千年的风雨震灾依然屹立，见证了这片土地的沧桑历史呢。【情绪:excited】",
                "路线": "【推荐文化探访路线】\n\n您可以走这条路线：从南门入口出发，首先参观唐代古寺遗址，然后到收藏珍贵碑刻的碑林。\n\n接着登上半山腰的观景台，最后参观核心地标——唐代古塔，感受千年历史的人文情怀呀。【情绪:happy】",
                "景点": "【推荐文化景点】\n\n景区里最推荐您去的是古塔、古寺遗址和碑林。\n\n其中古塔有1300年历史，古寺遗址仍保留着唐代柱基，而碑林收藏了多达200块历代名家石碑，非常适合深度游览哦！【情绪:happy】",
            }
        elif preference == "photo":
            replies = {
                "古塔": "【最佳拍照重点】\n\n想要拍出古塔的雄伟？推荐您在下午4点左右的“黄金时刻”前往古塔南侧的银杏树旁。\n\n将手机镜头稍微放低仰拍，利用金黄的杏叶做为前景遮挡，能拍出极具故事感和光影质感的大片哦，快去试试吧！【情绪:excited】",
                "路线": "【最佳打卡路线】\n\n推荐您走南门→古寺遗址（废墟沧桑风）→观景台（俯瞰景区全景）→花海（人像花丛风）→古塔（仰拍局部特写）。\n\n这几个点是景区里最容易出片的拍摄机位，保证您的朋友圈照片效果极佳呀！【情绪:happy】",
                "景点": "【最佳拍照景点】\n\n最强推的是瀑布和花海！\n\n瀑布有30米落差，利用慢动作快门可以拍出拉丝般的流水质感；花海则有大片鲜花，站在木栈道中间并虚化背景，能拍出极其唯美的艺术人像。【情绪:happy】",
            }
        elif preference == "nature":
            replies = {
                "古塔": "【自然风光重点】\n\n古塔静静地伫立在翠绿的苍松翠柏之间，周围群山环抱，极其静谧。\n\n站在这里，您可以听到微风吹过竹林的沙沙声，还有古塔檐角铜铃在山谷间回荡的清脆声。空气里满是松针的清香，非常治愈心灵呢。【情绪:happy】",
                "路线": "【推荐自然生态路线】\n\n推荐您走东门→竹林小径（避暑清幽）→瀑布（水汽扑面）→山林栈道（森林漫步）→山顶观景台（360度远眺）。\n\n这条路线绿荫遮天，水汽充沛，特别适合呼吸新鲜空气、放松疲惫的身心呀。【情绪:happy】",
                "景点": "【推荐风光景点】\n\n最推荐的是竹林小径和瀑布。\n\n竹林小径两侧翠竹掩映，清风徐来，非常阴凉幽静；瀑布则水珠飞溅，漫步在水潭边，能感受到负氧离子，让人身心清爽舒畅！【情绪:happy】",
            }
        elif preference == "family":
            replies = {
                "古塔": "【休闲亲子重点】\n\n古塔周围是一片平坦、柔软的绿茵草坪，非常安全，小朋友可以尽情跑跳玩耍。\n\n草坪旁设有树荫遮阳椅和自动售水机，距离无障碍洗手间和母婴室也仅有100米，带老人和孩子游览非常省心方便呢。【情绪:happy】",
                "路线": "【推荐亲子趣味路线】\n\n最适合全家出游的路线是：从游客中心出发，租一辆双人代步电动车。\n\n第一站去萌宠乐园喂小兔子，第二站去花海坐轨道小火车，最后到美食街品尝本地特色甜点，全程好走不累人，轻松又温馨呀。【情绪:happy】",
                "景点": "【推荐亲子景点】\n\n最推荐萌宠乐园和美食街！\n\n萌宠乐园里有温顺的羊驼和兔宝宝，可以让孩子体验亲密互动；美食街上不仅有特色小吃，还备有婴儿手推车免费租借点，非常贴心哦！【情绪:happy】",
            }
        else:
            replies = {}

        # Fallback to general replies if no match or no preference
        general_replies = {
            "古塔": "这座古塔建于唐代，距今已有1300多年历史，高约45米。\n\n它是景区最核心的标志性建筑，非常值得登高一望呢！【情绪:excited】",
            "门票": "咱们景区成人票是80元，学生凭学生证可以享受半价40元优惠。\n\n另外，60岁以上的老人凭身份证是免票入园的哦。【情绪:happy】",
            "路线": "为您推荐经典文化探访路线：南门→古寺遗址→碑林→观景台→古塔。\n\n这是一条最省力也最能领略景区魅力的路线呢。【情绪:happy】",
            "开放": "景区的开放时间是每天早上8点到下午6点，下午5点就停止检票入园了。\n\n您游览的时候要注意合理安排时间，玩得开心哦。【情绪:neutral】",
        }

        for key, reply in replies.items():
            if key in prompt:
                return reply, self._extract_emotion(reply)
        
        for key, reply in general_replies.items():
            if key in prompt:
                return reply, self._extract_emotion(reply)

        if preference:
            labels = {"history": "历史文化", "photo": "打卡拍照", "nature": "自然风光", "family": "休闲亲子"}
            pref_name = labels.get(preference, "默认")
            return f"这是一个非常有趣的问题！\n\n我已经为您锁定了【{pref_name}】偏好讲解模式，让我为您进行深度介绍吧！【情绪:excited】", "excited"

        return "这是一个非常有趣的问题！\n\n让我为您详细介绍一下，看看这里有什么精彩内容吧。【情绪:excited】", "excited"

    def _extract_emotion(self, text: str) -> str:
        """从文本中提取情感标签"""
        # 支持 【情绪:xxx】、【情绪：xxx】、[情绪:xxx]、[情绪：xxx] 等格式
        match = re.search(r'[【\[]情绪[：:](\w+)[】\]]', text)
        return match.group(1) if match else "neutral"

    def _remove_emotion_tag(self, text: str) -> str:
        """移除情感标签"""
        return re.sub(r'[【\[]情绪[：:]\w+[】\]]', '', text).strip()

    async def analyze_emotion(self, text: str) -> str:
        """分析用户输入的情感"""
        emotions = {"开心": "happy", "喜欢": "happy", "好": "happy",
                    "失望": "sad", "遗憾": "sad", "差": "sad",
                    "惊讶": "surprised", "没想到": "surprised"}
        for word, emotion in emotions.items():
            if word in text:
                return emotion
        return "neutral"

    async def analyze_image(self, image_base64: str) -> str:
        """分析图片内容"""
        if not self.llm:
            return "这是一处景区建筑，青瓦红墙，具有典型的唐代建筑风格。"

        try:
            from langchain_core.messages import HumanMessage
            
            response = await self.llm.ainvoke([
                HumanMessage(content=[
                    {"type": "text", "text": "请用一句话描述这张图片中的内容，识别是什么景点或物体。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ])
            ])
            return response.content
        except Exception:
            return "这是一处景区建筑，青瓦红墙，具有典型的唐代建筑风格。"


llm_service = LLMService()
