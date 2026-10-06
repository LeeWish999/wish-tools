# sd_cn.py v3 —— 修复 ControlNet 未生效（enabled:true）+ 保存 info.json 供验证
# 用法: python sd_cn.py 草图.png --prompt "..." --model lineart_anime --out 输出.png
import sys, json, base64, argparse, requests

API = "http://127.0.0.1:7860"
NEG = ("lowres, blurry, watermark, text, signature, jpeg artifacts, low quality, "
       "worst quality, isometric, perspective, 3/4 view, tilted, photorealistic, "
       "people, characters, gradient background, vignette, shadow, drop shadow, "
       "cast shadow, ground shadow, contact shadow, dark floor, black shadow")

MODELS = {
    "scribble": "control_v11p_sd15_scribble_fp16 [4e6af23e]",
    "lineart": "control_v11p_sd15_lineart_fp16 [5c23b17d]",
    "lineart_anime": "control_v11p_sd15s2_lineart_anime_fp16 [c58f338b]",
    "canny": "control_v11p_sd15_canny_fp16 [b18e0966]",
    "softedge": "control_v11p_sd15_softedge_fp16 [f616a34f]",
    "mlsd": "control_v11p_sd15_mlsd_fp16 [77b5ad24]",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sketch", help="草图 PNG 路径（黑线白底）")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--model", default="lineart_anime", choices=MODELS.keys())
    ap.add_argument("--weight", type=float, default=1.0)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--checkpoint", default="sd1.5\\anything-v5.safetensors")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.sketch, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    payload = {
        "prompt": args.prompt,
        "negative_prompt": NEG,
        "steps": args.steps,
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "sampler_name": "DPM++ 2M",
        "batch_size": 1,
        "seed": args.seed,
        "override_settings": {"sd_model_checkpoint": args.checkpoint},
        "alwayson_scripts": {
            "controlnet": {
                "args": [{
                    "enabled": True,
                    "input_image": b64,
                    "module": "none",
                    "model": MODELS[args.model],
                    "weight": args.weight,
                    "guidance_start": 0.0,
                    "guidance_end": 1.0,
                    "resize_mode": "Just Resize",
                    "control_mode": "Balanced",
                    "pixel_perfect": True,
                }]
            }
        },
    }

    r = requests.post(f"{API}/sdapi/v1/txt2img", json=payload, timeout=600)
    if r.status_code != 200:
        print(f"❌ HTTP {r.status_code}: {r.text[:500]}"); sys.exit(1)
    res = r.json()
    if "images" not in res:
        print(f"❌ 失败: {res}"); sys.exit(1)

    with open(args.out, "wb") as f:
        f.write(base64.b64decode(res["images"][0]))
    print(f"✅ 已保存: {args.out}")

    info = res.get("info", "")
    with open(args.out + ".info.json", "w", encoding="utf-8") as f:
        f.write(info if isinstance(info, str) else json.dumps(info, ensure_ascii=False))
    print("info 已存:", args.out + ".info.json")

if __name__ == "__main__":
    main()
