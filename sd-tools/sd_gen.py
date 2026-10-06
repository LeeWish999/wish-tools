# sd_gen.py v2 —— 文生图 + 保存防呆（重试3次 + 原子写，治 Errno 22 文件占用）
import json, base64, sys, os, time, argparse
import requests

DEFAULT_API = "http://127.0.0.1:7860"

def save_bytes(path, data, retries=3):
    tmp = path + ".tmp"
    for attempt in range(1, retries + 1):
        try:
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)   # 原子改名：成功前不会留下半截文件
            return True
        except OSError as e:
            if attempt < retries:
                time.sleep(1.5)     # 等占用的进程松手
            else:
                raise

def main():
    parser = argparse.ArgumentParser(description="调用 SD WebUI txt2img API")
    parser.add_argument("task", help="任务 JSON 文件路径")
    parser.add_argument("--out", default="output", help="图片输出目录")
    parser.add_argument("--api", default=DEFAULT_API)
    args = parser.parse_args()

    with open(args.task, "r", encoding="utf-8") as f:
        payload = json.load(f)
    prefix = payload.pop("save_prefix", None) or time.strftime("sd_%Y%m%d_%H%M%S")
    payload.setdefault("negative_prompt", "")
    payload.setdefault("seed", -1)
    payload.setdefault("batch_size", 1)
    payload.setdefault("n_iter", 1)

    os.makedirs(args.out, exist_ok=True)
    print(f"→ 调用 {args.api}/sdapi/v1/txt2img ...")
    try:
        r = requests.post(f"{args.api}/sdapi/v1/txt2img", json=payload, timeout=600)
    except requests.exceptions.ConnectionError:
        print("❌ 连不上绘世 API。请确认绘世已启动且「启用 API」开启。")
        sys.exit(1)
    if r.status_code != 200:
        print(f"❌ 请求失败 HTTP {r.status_code}: {r.text[:500]}")
        sys.exit(1)

    res = r.json()
    if "images" not in res:
        print(f"❌ 生成失败: {res}")
        sys.exit(1)

    saved = []
    for i, b64 in enumerate(res["images"]):
        path = os.path.join(args.out, f"{prefix}_{i:02d}.png")
        save_bytes(path, base64.b64decode(b64))
        saved.append(path)

    try:
        info = json.loads(res.get("info", "{}"))
        with open(os.path.join(args.out, f"{prefix}_info.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        seeds = info.get("all_seeds", [info.get("seed", "?")])
    except Exception:
        seeds = ["?"]

    print(f"✅ 完成：{len(saved)} 张，seed = {seeds}")
    for p in saved:
        print(p)

if __name__ == "__main__":
    main()
