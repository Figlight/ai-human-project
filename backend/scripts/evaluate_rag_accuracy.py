"""
RAG 事实性问答准确率自动化测评脚本
"""
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目根目录到系统路径以导入 backend 包
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.chat_service import chat_service
from backend.app.core.llm import llm_service
from backend.app.db.database import engine


async def judge_answer(
    reply: str,
    expected_keywords: list[str],
    use_llm_judge: bool = True
) -> tuple[bool, str]:
    """
    评判数字人回复是否正确：先进行关键字硬匹配，如果失败再转由大模型裁判进行语义判定。
    """
    # 1. 关键字匹配（忽略大小写，去除空格）
    matched_keywords = [kw for kw in expected_keywords if kw.strip().lower() in reply.lower()]
    is_correct = len(matched_keywords) > 0
    reason = f"匹配关键字: {matched_keywords}" if is_correct else f"未匹配任何关键字 {expected_keywords}"

    # 2. 大模型裁判判定
    if use_llm_judge and not is_correct and llm_service.llm:
        try:
            judge_prompt = f"""请扮演评委，判断AI数字人对景区问题的回答是否符合事实且回答正确。
预期正确内容应包含或暗示这些关键信息：{expected_keywords}

AI数字人的回答：{reply}

如果回答正确，在第一行只输出：正确。
如果回答错误或答非所问，在第一行只输出：错误。
随后可以在新的一行给出你的评判理由。"""
            
            judge_res, _ = await llm_service.chat(
                prompt=judge_prompt,
                system_prompt="你是一个严谨的景区导游评判裁判。"
            )
            judge_res_clean = judge_res.strip()
            print(f"   🤖 大模型裁判判定详情: {judge_res_clean}")
            # 仅提取第一行进行判定，防止后续解释文本中包含“正确”二字造成误判
            first_line = judge_res_clean.split("\n")[0].strip()
            if "正确" in first_line:
                is_correct = True
                reason = f"通过大模型裁判语义判定（正确）。裁判反馈: {judge_res_clean}"
            else:
                reason = f"大模型裁判判定（错误）。裁判反馈: {judge_res_clean}"
        except Exception as e:
            print(f"   ⚠️ 大模型裁判判定发生异常: {e}")
            reason = f"未匹配任何关键字且大模型裁判发生异常: {e}"
            
    return is_correct, reason



async def evaluate(report_name: str = "rag_eval_report.md"):
    print("=" * 80)
    print("🧪 开始运行：RAG 事实问答准确率自动化测试与评估")
    print("=" * 80)

    # 1. 加载测试集
    test_set_path = project_root / "backend/data/rag_test_set.json"
    if not test_set_path.exists():
        print(f"❌ 测试集文件不存在: {test_set_path}")
        return

    with open(test_set_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"📊 已加载 {len(test_cases)} 个测试用例。正在发起问答与相关度评测...")
    print("-" * 80)

    results = []
    correct_count = 0
    session_id = "eval_session_tmp"

    try:
        # 清除该临时会话的历史记录，防止上下文干扰评测
        try:
            await chat_service.delete_conversation_session(session_id)
        except Exception:
            pass

        for i, case in enumerate(test_cases, 1):
            question = case["question"]
            expected_keywords = case["expected_keywords"]
            category = case["category"]

            print(f"▶️ [{i}/{len(test_cases)}] 【{category}】问题: {question}")
            
            # 2. 调用 RAG 问答链获取回答
            try:
                res = await chat_service.process_text_message(
                    session_id=session_id,
                    message=question,
                    use_rag=True
                )
                reply = res["reply"]
                emotion = res["emotion"]
            except Exception as e:
                print(f"   ❌ 调用失败: {e}")
                results.append({
                    "question": question,
                    "reply": f"ERROR: {e}",
                    "status": "FAIL",
                    "reason": "接口调用异常",
                    "category": category
                })
                continue

            print(f"   🤖 回复 (情绪: {emotion}): {reply[:120]}...")

            # 3. 评判逻辑 (封装了关键字硬匹配与 LLM 裁判双核判定)
            is_correct, reason = await judge_answer(reply, expected_keywords, use_llm_judge=True)

            if is_correct:
                correct_count += 1
                status = "PASS"
                print(f"   ✅ 评测通过 ({reason})")
            else:
                status = "FAIL"
                print(f"   ❌ 评测失败 ({reason})")
            print("-" * 80)

            results.append({
                "question": question,
                "reply": reply,
                "status": status,
                "reason": reason,
                "category": category
            })

        # 4. 计算并输出报告
        accuracy = (correct_count / len(test_cases)) * 100
        report_markdown = f"""# 📊 RAG 事实性问答准确率评测报告

* **评测时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (本地运行)
* **测试用例总数**: {len(test_cases)} 个
* **通过用例数**: {correct_count} 个
* **准确率（Accuracy）**: **{accuracy:.1f}%**
* **达标要求**: 不低于 **90%** (赛题硬性指标)
* **结论**: {"✨ 达标 (PASS)" if accuracy >= 90 else "⚠️ 未达标，需继续调优 RAG (FAIL)"}

---

## 📋 详细测评结果明细

| 编号 | 类别 | 评估问题 | 数字人回复 | 评测状态 | 判定理由 |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""

        for i, res in enumerate(results, 1):
            reply_esc = res["reply"].replace("\n", " ").replace("|", "\\|")
            reason_esc = res["reason"].replace("\n", "<br>").replace("|", "\\|")
            report_markdown += f"| {i} | {res['category']} | {res['question']} | {reply_esc[:80]}... | {res['status'] == 'PASS' and '✅ PASS' or '❌ FAIL'} | {reason_esc} |\n"

        # 保存报告至 data 目录
        report_path = project_root / f"backend/data/{report_name}"
        report_path.write_text(report_markdown, encoding="utf-8")

        print("\n" + "=" * 80)
        print(f"✨ 评测完成！总准确率: {accuracy:.1f}%")
        print(f"💾 详细报告已保存至: {report_path}")
        print("=" * 80)

    finally:
        # 确保评测结束后自动清理数据库测试数据与连接引擎
        print("\n🧹 正在清理数据库测试数据...")
        try:
            await chat_service.delete_conversation_session(session_id)
            print("✅ 数据库测试数据清理完毕")
        except Exception as e:
            print(f"⚠️ 清理数据库测试数据失败: {e}")

        try:
            await engine.dispose()
        except Exception as e:
            print(f"⚠️ 清理数据库引擎失败: {e}")


if __name__ == "__main__":
    asyncio.run(evaluate())
