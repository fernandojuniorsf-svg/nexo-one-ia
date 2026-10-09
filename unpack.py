"""Build-only loader. Application source is supplied as PRIVATE Render env vars.
The public repository contains NO NEXO Commerce AI application source.
"""
import base64, io, lzma, os, tarfile
from pathlib import Path

chunks = []
for index in range(1, 10):
    chunk = os.getenv(f"NEXO_SOURCE_B64_{index}", "")
    if not chunk:
        break
    chunks.append(chunk)
if not chunks:
    raise SystemExit("NEXO_SOURCE_B64_1 environment secret is missing")
payload = base64.b64decode("".join(chunks), validate=True)
bundle = lzma.decompress(payload)
with tarfile.open(fileobj=io.BytesIO(bundle)) as archive:
    for member in archive.getmembers():
        target = Path(member.name)
        if target.is_absolute() or ".." in target.parts:
            raise SystemExit("Unsafe path in release archive")
        if not member.isfile() and not member.isdir():
            raise SystemExit("Unexpected item type in release archive")
    archive.extractall(".", filter="data")
if not Path("app.py").is_file() or not Path("requirements.txt").is_file():
    raise SystemExit("Release archive is incomplete")
print("Release archive unpacked; preparing Python dependencies")
