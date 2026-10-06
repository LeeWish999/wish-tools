# sd_img2img.py —— 以参考图锁定角色外观，重绘生成变体帧（行走帧接力）
# 用法: python sd_img2img.py 参考图.png --prompt "..." --out 输出.png [--denoise 0.5] [--seed 888]
import sys, base64, argparse, requests
from PIL import Image as PILImage

API = "http://127.0.0.1:7860"
DEFAULT_NEG = ("lowres, bad anatomy, blurry, watermark, text, signature, extra limbs, deformed, "
               "jpeg artifacts, low quality, worst quality, cropped, cut off, out of frame, "
               "partial body, head cut off, feet cut off, close-up, upper body, zoomed in, "
               "ring, circle, circular frame, ring border, halo, magic circle, emblem, badge, "
               "vignette, spotlight, circular background, medal, coin")

def main():
    ap = argparse.ArgumentParser(description="SD WebUI img2img 单张生成")
    ap.add_argument("init_image", help="参考图 PNG 路径（锁定外观）")
    ap.add_argument("--prompt", required=True, help="正向提示词（英文）")
    ap.add_argument("--negative", default=DEFAULT_NEG)
    ap.add_argument("--seed", type=int, default=888, help="固定 seed 保证系列帧一致")
    ap.add_argument("--denoise", type=float, default=0.5, help="重绘幅度 0.4~0.6")
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--cfg", type=float, default=7)
    ap.add_argument("--sampler", default="DPM++ 2M")
    ap.add_argument("--checkpoint", default=None, help="可选：覆盖底模")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    args = ap.parse_args()

    with open(args.init_image, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    w, h = PILImage.open(args.init_image).size

    payload = {
        "init_images": [b64],
        "prompt": args.prompt,
        "negative_prompt": args.negative,
        "seed": args.seed,
        "denoising_strength": args.denoise,
        "steps": args.steps,
        "cfg_scale": args.cfg,
        "sampler_name": args.sampler,
        "width": w,
        "height": h,
    }
    if args.checkpoint:
        payload["override_settings"] = {"sd_model_checkpoint": args.checkpoint}

    try:
        r = requests.post(f"{API}/sdapi/v1/img2img", json=payload, timeout=600)
    except requests.exceptions.ConnectionError:
        print("连接失败: 请确认绘世已启动且启用API")
        sys.exit(1)

    if r.status_code != 200:
        print(f"请求失败 HTTP {r.status_code}: {r.text[:500]}")
        sys.exit(1)

    res = r.json()
    if "images" not in res:
        print(f"生成失败: {res}")
        sys.exit(1)

    with open(args.out, "wb") as f:
        f.write(base64.b64decode(res["images"][0]))
    print(f"已保存: {args.out}")

if __name__ == "__main__":
    main()
