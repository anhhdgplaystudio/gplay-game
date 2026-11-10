"""Build kiểm tra C# không cần mở Unity, kèm file .cs mới chưa có trong csproj.

python check_build.py <file.csproj> [file_mới.cs ...] [--out <thư mục tạm>]
Tạo bản csproj tạm (thêm <Compile Include>), build ra thư mục tạm, chỉ in dòng ' error '.
Exit 1 nếu có lỗi. Chạy song song được (mỗi lần 1 csproj tạm riêng).
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import uuid

# Console Windows mặc định cp1252: ép UTF-8 để in tiếng Việt
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csproj")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "unity_check_build"))
    a = ap.parse_args()

    proj = os.path.abspath(a.csproj)
    root = os.path.dirname(proj)
    with open(proj, encoding="utf-8-sig") as f:
        text = f.read()

    adds = []
    for p in a.files:
        rel = os.path.relpath(os.path.abspath(p), root)
        if rel.replace("/", "\\") not in text and rel.replace("\\", "/") not in text:
            adds.append(f'    <Compile Include="{rel}" />')
    tag = uuid.uuid4().hex[:8]
    out = os.path.join(a.out, tag)
    # Chỉ đổi output của project chính; project tham chiếu dùng bản đã build (BuildProjectReferences=false)
    bin_dir = os.path.join(out, "bin") + os.sep
    obj_dir = os.path.join(out, "obj") + os.sep
    text = re.sub(r"<OutputPath>[^<]*</OutputPath>",
                  lambda _: f"<OutputPath>{bin_dir}</OutputPath><IntermediateOutputPath>{obj_dir}</IntermediateOutputPath>",
                  text, count=1)
    if adds:
        block = "<ItemGroup>\n" + "\n".join(adds) + "\n  </ItemGroup>\n  "
        text = re.sub(r"(<ItemGroup>\s*<Compile )", lambda m: block + m.group(1), text, count=1)

    tmp = os.path.join(root, f"_check_{tag}.csproj")  # cùng thư mục để đường dẫn tương đối đúng
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    def run(args):
        return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=root)

    try:
        r = run(["dotnet", "build", tmp, "-nologo", "-v", "q", "-p:BuildProjectReferences=false"])
        if "CS0006" in r.stdout:
            # DLL của project tham chiếu chưa có (Temp/Bin trống): build gốc 1 lần rồi thử lại
            print("Chưa có DLL tham chiếu, build project gốc 1 lần...")
            run(["dotnet", "build", proj, "-nologo", "-v", "q"])
            r = run(["dotnet", "build", tmp, "-nologo", "-v", "q", "-p:BuildProjectReferences=false"])
    finally:
        os.remove(tmp)
    errs = sorted({l.strip() for l in (r.stdout + r.stderr).splitlines() if " error " in l})
    for e in errs:
        print(e)
    print(f"{len(errs)} lỗi" + (f" (đã thêm {len(adds)} file mới)" if adds else ""))
    sys.exit(1 if errs or r.returncode else 0)


if __name__ == "__main__":
    main()
