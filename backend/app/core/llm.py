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
                print(f"✅ LangChain ChatTongyi 初始化成功 (模型: {settings.LLM_MODEL})")
            except Exception as e:
                print(f"❌ LangChain ChatTongyi 初始化失败: {e}")
                self.llm = None
        else:
            print("⚠️ LLM_API_KEY 未配置，使用 Mock 模式")

    async def chat(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
    ) -> tuple[str, str]:
        """非流式对话"""
        if self.llm:
            return await self._api_chat(prompt, context, system_prompt, history)
        return self._mock_chat(prompt, context)

    def _build_messages(
        self,
        prompt: str,
        context: Optional[str],
        system_prompt: Optional[str],
        history: Optional[list[dict]] = None,
    ) -> list:
        """构建消息列表"""
        messages = []
        
        # System prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    "你是一个景区导游助手，请用亲切自然的语气回答游客问题。"
                    "如果提供了参考信息，请基于参考信息回答。"
                    "在回答末尾用【情绪:xxx】标注情感（happy/sad/neutral/surprised/excited）。"
                )
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
        
        # User question
        messages.append({"role": "user", "content": prompt})
        
        return messages

    async def _api_chat(
        self,
        prompt: str,
        context: Optional[str],
        system_prompt: Optional[str],
        history: Optional[list[dict]] = None,
    ) -> tuple[str, str]:
        """调用 LangChain LLM API"""
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        messages = self._build_messages(prompt, context, system_prompt, history)
        
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
            return self._mock_chat(prompt, context)

    async def chat_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
    ):
        """流式对话 - 使用 LangChain 的流式输出"""
        if not self.llm:
            reply, emotion = self._mock_chat(prompt, context)
            yield reply, reply, emotion
            return

        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        messages = self._build_messages(prompt, context, system_prompt, history)
        
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
            reply, emotion = await self._api_chat(prompt, context, system_prompt, history)
            yield reply, reply, emotion
            return

        # 提取最终情感
        emotion = self._extract_emotion(full)
        clean = self._remove_emotion_tag(full)
        yield "", clean, emotion

    def _mock_chat(self, prompt: str, context: Optional[str]) -> tuple[str, str]:
        """Mock 回复（当 API 不可用时）"""
        replies = {
            "古塔": "这座古塔建于唐代，距今已有1300多年历史，是景区的标志性建筑。【情绪:excited】",
            "门票": "成人票80元，学生票40元，60岁以上老人免票。【情绪:happy】",
            "路线": "推荐文化探访路线：南门→古寺遗址→碑林→观景台→古塔。【情绪:happy】",
            "开放": "景区开放时间 8:00-18:00，17:00停止入园。【情绪:neutral】",
        }
        for key, reply in replies.items():
            if key in prompt:
                return reply, self._extract_emotion(reply)
        return "这是一个非常有趣的问题！让我为您详细介绍一下。【情绪:excited】", "excited"

    def _extract_emotion(self, text: str) -> str:
        """从文本中提取情感标签"""
        match = re.search(r'【情绪:(\w+)】', text)
        return match.group(1) if match else "neutral"

    def _remove_emotion_tag(self, text: str) -> str:
        """移除情感标签"""
        return re.sub(r'【情绪:\w+】', '', text).strip()

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
