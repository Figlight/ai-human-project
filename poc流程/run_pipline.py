#!/usr/bin/env python3
"""
电商AI海报生成 · 一键管线
=========================
单入口：Qwen2.5-7B 生成海报提示词 → SDXL 生成海报图片

显存管理：
  A10 (23GB) 不能同时跑 Qwen + SDXL。
  脚本自动：加载 Qwen → 生成提示词 → 释放显存 → 加载 SDXL → 出图

用法:
  python3 run_pipeline.py \\
    --name "玻尿酸精华液" \\
    --brand "Dr.G" \\
    --category "beauty" \\
    --features "三重玻尿酸" "48h锁水" \\
    --info "30ml 冬季补水" \\
    --price "129" \\
    --audience "25-35岁女性" \\
    --output ./output

  python3 run_pipeline.py --interactive   # 交互式输入
"""

import os, sys, json, time, argparse, gc, re
from pathlib import Path
from typing import List, Optional

import torch
from PIL import Image

# ─── 路径配置 ───────────────────────────────────────────────────────
QWEN_PATH = "/mnt/workspace/.cache/modelscope/models/Qwen/Qwen2.5-7B-Instruct"
SDXL_PATH = "/mnt/workspace/.cache/modelscope/models/AI-ModelScope/stable-diffusion-xl-base-1___0"
OUTPUT_DIR = Path("/mnt/workspace/output")
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# Qwen 系统提示词（用户指定的完整海报提示词生成模板）
# ═══════════════════════════════════════════════════════════════════
QWEN_SYSTEM_PROMPT = """你的任务：根据用户给到的【商品基础信息+活动信息】，自动生成一份精准的AI绘画提示词，用来让绘图AI生成竖版电商产品促销海报。

输出文案必须严格拆分5大固定模块：
1.整体基础设定：海报尺寸版式、画面风格、主色调、画面质感、使用场景（电商主图/活动海报）；
2.顶部区域：画面最上方的品牌名称、标题文案、文字排版、边框样式、色块配色；
3.画面中部（核心区）：分三块：①右侧主体产品摆放位置+产品外观细节；②左侧福利赠品框：框型、颜色、赠品实物清单、框内文案、印章图标；③中间扫码区域：标签样式、二维码、装饰小图标；
4.画面下部：横向三栏步骤活动区（分左/中/右三步，每栏标题、文案、简笔画图标、底色）+最底部通栏分区文案、色块；
5.光影画风补充：整体光影、材质表现、字体层级、商业海报画风。

要求：所有文案、数字、活动规则100%沿用用户提供的商品信息，排版布局对标飞鹤星飞帆同款经典促销版式，描述细致，可直接复制到绘图模型生成海报。"""


def build_user_message(name: str, brand: str, category: str, info: str,
                       price: str, features: List[str], audience: str,
                       instructions: str) -> str:
    """构建用户消息"""
    feat_str = "、".join(features) if features else "未提供"
    parts = [
        f"商品名称：{name}",
        f"品牌：{brand}" if brand else "",
        f"类目：{category}" if category else "",
        f"商品信息：{info}" if info else "",
        f"价格：{price}" if price else "",
        f"核心卖点：{feat_str}",
        f"目标人群：{audience}" if audience else "",
        f"附加要求：{instructions}" if instructions else "",
    ]
    return "\n".join(p for p in parts if p)


# ═══════════════════════════════════════════════════════════════════
# Step 1: Qwen2.5-7B → 生成 AI 绘画提示词
# ═══════════════════════════════════════════════════════════════════
def step1_generate_prompt(name: str, brand: str = "", category: str = "",
                          info: str = "", price: str = "",
                          features: List[str] = None,
                          audience: str = "", instructions: str = "",
                          max_tokens: int = 2048) -> str:
    """加载 Qwen2.5-7B，用系统提示词生成 AI 绘画提示词"""
    print("\n" + "=" * 60)
    print("  Step 1/2: Qwen2.5-7B 生成海报提示词")
    print("=" * 60)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    print(f"  📦 加载 Qwen 模型... ({QWEN_PATH})")
    tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        QWEN_PATH,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    model.eval()
    print(f"  ✅ Qwen 加载完成 ({time.time()-t0:.1f}s)")

    # 构建消息
    user_msg = build_user_message(name, brand, category, info, price,
                                  features or [], audience, instructions)

    messages = [
        {"role": "system", "content": QWEN_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    print(f"  🧠 Qwen 生成中...")
    gen_t0 = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )
    prompt = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    print(f"  ✅ Qwen 生成完成 ({time.time()-gen_t0:.1f}s)")

    # 清理显存
    print("  🧹 释放 Qwen 显存...")
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    print(f"  当前显存: {torch.cuda.memory_allocated()/1024**3:.1f}GB / {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")

    return prompt


# ═══════════════════════════════════════════════════════════════════
# Step 2: SDXL → 根据提示词生成海报图片
# ═══════════════════════════════════════════════════════════════════
def step2_generate_image(prompt: str, output_path: str,
                         width: int = 768, height: int = 1024,
                         num_steps: int = 30,
                         guidance_scale: float = 7.0):
    """加载 SDXL，根据提示词生成海报图片"""
    print("\n" + "=" * 60)
    print("  Step 2/2: SDXL 生成海报图片")
    print("=" * 60)

    from diffusers import StableDiffusionXLPipeline, EulerDiscreteScheduler

    t0 = time.time()
    print(f"  📦 加载 SDXL 模型... ({SDXL_PATH})")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        SDXL_PATH,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    )
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to("cuda")

    # 内存优化
    pipe.enable_xformers_memory_efficient_attention()
    pipe.enable_vae_tiling()
    print(f"  ✅ SDXL 加载完成 ({time.time()-t0:.1f}s)")

    negative_prompt = (
        "NSFW, low quality, blurry, distorted, ugly, bad anatomy, "
        "watermark, signature, text, words, letters, low resolution, "
        "worst quality, monochrome, grayscale, bad composition"
    )

    print(f"  🎨 SDXL 生成中... ({width}x{height}, {num_steps}步)")

    # SDXL 有两个文本编码器：
    #   - CLIP ViT-L:  77 tokens（固定）
    #   - OpenCLIP G:  支持更长，通过 max_embedding_size 控制
    # 默认 77 会截断长提示词，这里设为 256 保留更多细节
    gen_t0 = time.time()
    with torch.no_grad():
        # 使用 encode_prompt 手动编码，支持更长的提示词
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds = (
            pipe.encode_prompt(
                prompt=prompt,
                negative_prompt=negative_prompt,
                max_embedding_size=256,  # OpenCLIP 支持更长序列
                device="cuda",
            )
        )
        image = pipe(
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_prompt_embeds,
            pooled_prompt_embeds=pooled_prompt_embeds,
            negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
            width=width,
            height=height,
            num_inference_steps=num_steps,
            guidance_scale=guidance_scale,
        ).images[0]
    print(f"  ✅ SDXL 生成完成 ({time.time()-gen_t0:.1f}s)")

    # 清理显存
    print("  🧹 释放 SDXL 显存...")
    del pipe
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    # 保存
    image.save(output_path)
    print(f"  💾 图片已保存: {output_path}")
    print(f"  📐 尺寸: {width}x{height}")

    return image


# ═══════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="电商AI海报生成 · 一键管线 (Qwen→SDXL)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 run_pipeline.py --name "玻尿酸精华液" --brand "Dr.G" --features "补水" "锁水"
  python3 run_pipeline.py --interactive
        """,
    )
    parser.add_argument("--name", help="商品名称")
    parser.add_argument("--brand", default="", help="品牌")
    parser.add_argument("--category", default="general", help="类目 (beauty/food/digital/home/general)")
    parser.add_argument("--info", default="", help="商品详细信息")
    parser.add_argument("--price", default="", help="价格")
    parser.add_argument("--features", nargs="*", default=[], help="核心卖点列表")
    parser.add_argument("--audience", default="", help="目标人群")
    parser.add_argument("--instructions", default="", help="附加要求")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--width", type=int, default=768, help="图片宽度")
    parser.add_argument("--height", type=int, default=1024, help="图片高度")
    parser.add_argument("--steps", type=int, default=30, help="SDXL 推理步数")
    parser.add_argument("--guidance", type=float, default=7.0, help="引导尺度")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Qwen 最大生成 token 数")
    parser.add_argument("--interactive", action="store_true", help="交互式输入模式")
    parser.add_argument("--save-prompt", default="", help="保存提示词到文件（调试用）")
    args = parser.parse_args()

    # 交互模式
    if args.interactive or not args.name:
        if not args.name:
            print("=" * 50)
            print("  交互式输入")
            print("=" * 50)
            args.name = input("商品名称: ").strip()
            args.brand = input("品牌: ").strip()
            args.category = input("类目 (beauty/food/digital/home/general): ").strip() or "general"
            args.info = input("商品信息: ").strip()
            args.price = input("价格: ").strip()
            feats = input("核心卖点（逗号分隔）: ").strip()
            args.features = [f.strip() for f in feats.split("，") if f.strip()] if feats else []
            args.audience = input("目标人群: ").strip()
            instr = input("附加要求: ").strip()
            args.instructions = instr

    if not args.name:
        print("❌ 错误：必须提供商品名称（--name 或 --interactive 模式）")
        sys.exit(1)

    # 输出目录
    output_dir = Path(args.output)
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    prompt_file = output_dir / f"prompt_{timestamp}.txt"
    image_file = output_dir / f"poster_{timestamp}.png"

    # 检查显存
    if torch.cuda.is_available():
        total_vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        free_vram = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1024**3
        print(f"\n  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  显存: 已用 {torch.cuda.memory_allocated()/1024**3:.1f}GB / 空闲 {free_vram:.1f}GB / 总计 {total_vram:.1f}GB")
        if free_vram < 18:
            print("  ⚠️  可用显存不足 18GB，建议先关闭其他 GPU 进程")
    else:
        print("❌ 未检测到 GPU，无法运行 SDXL")
        sys.exit(1)

    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  电商 AI 海报生成管线 ".center(48) + "║")
    print("║" + f"  商品: {args.name}".ljust(56) + "║")
    print("║" + f"  品牌: {args.brand or '无'}  类目: {args.category}".ljust(56) + "║")
    print("╚" + "═" * 58 + "╝")

    # ═══ Step 1: Qwen 生成提示词 ═══
    prompt = step1_generate_prompt(
        name=args.name,
        brand=args.brand,
        category=args.category,
        info=args.info,
        price=args.price,
        features=args.features,
        audience=args.audience,
        instructions=args.instructions,
        max_tokens=args.max_tokens,
    )

    # 保存提示词
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    if args.save_prompt:
        with open(args.save_prompt, "w", encoding="utf-8") as f:
            f.write(prompt)

    print("\n" + "─" * 60)
    print("  📝 Qwen 生成的 AI 绘画提示词:")
    print("─" * 60)
    # 截取前 500 字预览
    preview = prompt[:500] + ("..." if len(prompt) > 500 else "")
    print(preview)
    print("─" * 60)
    print(f"  完整提示词已保存: {prompt_file}")
    print(f"  提示词长度: {len(prompt)} 字符")

    # ═══ Step 2: SDXL 生成图片 ═══
    image = step2_generate_image(
        prompt=prompt,
        output_path=str(image_file),
        width=args.width,
        height=args.height,
        num_steps=args.steps,
        guidance_scale=args.guidance,
    )

    # ═══ 完成 ═══
    print("\n" + "=" * 60)
    print("  🎉 管线完成！")
    print("=" * 60)
    print(f"  📄 提示词: {prompt_file}")
    print(f"  🖼️  海报:   {image_file}")
    print(f"  📐 尺寸:   {args.width}x{args.height}")
    print("=" * 60)


if __name__ == "__main__":
    main()
