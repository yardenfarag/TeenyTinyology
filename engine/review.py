"""The owner's review page: every Short and Lesson, their for-review/ files, timestamped comments and approvals.

    python -m engine.ep review            # then open http://localhost:8765

Local only (127.0.0.1), Python standard library only, nothing leaves the machine.
  - files come from for-review/<pkg>/<stage folder>/ (images, MP3, MP4, Markdown), grouped by version (_vN)
  - narration MP3s get their script lines from <mp3>.lines.json (written by engine.preview) or, for lesson batch
    MP3s, from the <stem>_batches.md beside them
  - comments go to <episodes|lessons>/<pkg>/feedback.json, approvals to approvals.json (same file `ep approve` uses)
  - the automatic checks (episodes/<pkg>/review/checks.json) show next to the final video
Claude reads comments with `python -m engine.ep feedback <pkg>` and closes them with `ep resolve`.
"""
import datetime
import json
import mimetypes
import os
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from engine import agent, ep

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_page.html")
LOCK = threading.Lock()
MEDIA = {".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image", ".gif": "image",
         ".mp3": "audio", ".wav": "audio", ".m4a": "audio", ".mp4": "video", ".webm": "video", ".md": "text",
         ".txt": "text"}


# ================================================================ data
def projects():
    out = []
    busy = agent.busy_pkgs()
    for pkg in ep.all_pkgs() + ep.all_lessons():
        a = ep.approvals(pkg)
        gates = ep.GATES[ep.kind(pkg)]
        out.append(dict(pkg=pkg, kind=ep.kind(pkg), title=title(pkg), legacy=a.get("legacy"),
                        open=ep.open_count(pkg),
                        next_gate=None if a.get("legacy") else next((g for g in gates if g not in a), None),
                        has_files=os.path.isdir(os.path.join(ep.REVIEW, pkg)), busy=pkg in busy))
    return out


def title(pkg):
    num, _, slug = pkg.partition("_")
    words = slug.replace("_", " ").title()
    if pkg.startswith("e") and len(words.split()) == 2:      # Shorts are named after their pair: "Pickle & Doodle"
        words = " & ".join(words.split())
    return f"{num.upper()} · {words}"


def version_of(name):
    m = re.search(r"_v(\d+)(?=[_.])", name)
    return int(m.group(1)) if m else 0


def batch_lines(folder):
    """{batch mp3 name: [{id, text, start}]} from every *_batches.md in a folder."""
    out = {}
    for f in os.listdir(folder):
        if not f.endswith("_batches.md"):
            continue
        cur = None
        for ln in open(os.path.join(folder, f), encoding="utf8"):
            m = re.match(r"## Batch .*?`([^`]+\.mp3)`", ln)
            if m:
                cur = out.setdefault(m.group(1), [])
                continue
            m = re.match(r"- `(\d+):([\d.]+)` \*\*([\w-]+)\*\* (.*)", ln.strip())
            if m and cur is not None:
                cur.append(dict(id=m.group(3), text=re.sub(r"\s+⚠.*$", "", m.group(4)),
                                start=int(m.group(1)) * 60 + float(m.group(2))))
    return out


def folders(pkg):
    root = os.path.join(ep.REVIEW, pkg)
    if not os.path.isdir(root):
        return []
    res = []
    for d in sorted(os.listdir(root)):
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        batches = batch_lines(full)
        files = []
        for f in sorted(os.listdir(full)):
            ext = os.path.splitext(f)[1].lower()
            if ext not in MEDIA or f.endswith("_batches.md"):
                continue
            p = os.path.join(full, f)
            item = dict(name=f, path=f"{d}/{f}", type=MEDIA[ext], version=version_of(f),
                        mtime=os.path.getmtime(p), size=os.path.getsize(p))
            side = p + ".lines.json"
            if os.path.exists(side):
                item["lines"] = json.load(open(side, encoding="utf8"))
            elif f in batches:
                item["lines"] = batches[f]
            if item["type"] == "text":
                item["body"] = open(p, encoding="utf8", errors="replace").read()
            files.append(item)
        if files:
            res.append(dict(name=d, label=re.sub(r"^\d+_", "", d).replace("_", " "), files=files))
    return res


def project(pkg):
    a = ep.approvals(pkg)
    gates = [dict(stage=g, approved=a.get(g)) for g in ep.GATES[ep.kind(pkg)]]
    status = []
    if ep.kind(pkg) == "short" and not a.get("legacy"):
        status = [dict(stage=n, done=bool(d), detail=x) for n, d, x in ep.stages(pkg)]
    checks = []
    cj = os.path.join(ep.project_dir(pkg), "review", "checks.json")
    if os.path.exists(cj):
        checks = [c for c in json.load(open(cj, encoding="utf8")) if c["sev"] in ("ERROR", "WARN")]
    return dict(pkg=pkg, kind=ep.kind(pkg), title=title(pkg), legacy=a.get("legacy"), gates=gates, status=status,
                folders=folders(pkg), feedback=ep.feedback(pkg), checks=checks, last_job=agent.last_for(pkg))


# ================================================================ HTTP
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):          # quiet: only errors
        if args and str(args[1])[0] in "45":
            super().log_message(fmt, *args)

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _err(self, code, msg):
        self._json({"error": msg}, code)

    def _pkg(self, name):
        pool = ep.all_pkgs() + ep.all_lessons()
        if name not in pool:
            raise KeyError(name)
        return name

    def do_GET(self):
        url = urlparse(self.path)
        parts = [unquote(p) for p in url.path.strip("/").split("/") if p]
        try:
            if not parts:
                body = open(PAGE, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif parts == ["api", "projects"]:
                self._json(projects())
            elif parts == ["api", "ideas"]:
                self._json(agent.load_ideas())
            elif parts == ["api", "jobs"]:
                self._json({"running": agent.running(), "recent": agent.recent()})
            elif len(parts) == 3 and parts[:2] == ["api", "jobs"]:
                self._json(agent.get_job(parts[2]))
            elif len(parts) == 3 and parts[:2] == ["api", "project"]:
                self._json(project(self._pkg(parts[2])))
            elif parts[0] == "files" and len(parts) >= 4:
                self._file(self._pkg(parts[1]), parts[2:])
            elif parts[0] == "thumbs" and len(parts) >= 4:
                self._thumb(self._pkg(parts[1]), parts[2:])
            else:
                self._err(404, "not found")
        except KeyError as e:
            self._err(404, f"unknown project {e}")
        except (ConnectionError, BrokenPipeError):
            pass

    def _safe(self, pkg, rel):
        base = os.path.realpath(os.path.join(ep.REVIEW, pkg))
        path = os.path.realpath(os.path.join(base, *rel))
        if os.path.commonpath([base, path]) != base or not os.path.isfile(path):
            return None
        return path

    def _thumb(self, pkg, rel):
        """A 480 px wide JPEG of a review image, cached in .cache/review_thumbs/ (the grid would otherwise load
        twenty full 1080x1920 PNGs)."""
        path = self._safe(pkg, rel)
        if not path:
            return self._err(404, "no such file")
        import hashlib
        key = hashlib.sha1(f"{path}|{os.path.getmtime(path)}".encode()).hexdigest()[:20]
        cache = os.path.join(ep.ROOT, ".cache", "review_thumbs")
        out = os.path.join(cache, key + ".jpg")
        if not os.path.exists(out):
            from PIL import Image
            os.makedirs(cache, exist_ok=True)
            im = Image.open(path).convert("RGB")
            im.thumbnail((480, 480 * 4))
            im.save(out, "JPEG", quality=84)
        body = open(out, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, pkg, rel):
        path = self._safe(pkg, rel)
        if not path:
            return self._err(404, "no such file")
        size = os.path.getsize(path)
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if path.endswith(".md"):
            ctype = "text/markdown; charset=utf-8"
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        m = re.match(r"bytes=(\d*)-(\d*)", rng or "")
        if m and (m.group(1) or m.group(2)):        # media seeking needs byte ranges
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def do_POST(self):
        parts = [unquote(p) for p in urlparse(self.path).path.strip("/").split("/") if p]
        try:
            n = int(self.headers.get("Content-Length") or 0)
            data = json.loads(self.rfile.read(n) or b"{}")
            # ---- Claude at work: ideas, jobs, continue
            if parts == ["api", "ideas"]:
                idea = agent.add_idea(data.get("kind", "short"), data.get("text", ""))
                job = agent.start_idea(idea["id"]) if data.get("start") else None
                return self._json({"ideas": agent.load_ideas(), "job": job})
            if len(parts) == 4 and parts[:2] == ["api", "ideas"]:
                iid = int(parts[2])
                if parts[3] == "start":
                    job = agent.start_idea(iid)
                    return self._json({"ideas": agent.load_ideas(), "job": job})
                if parts[3] == "delete":
                    return self._json({"ideas": agent.delete_idea(iid)})
                return self._err(404, "not found")
            if len(parts) == 4 and parts[:2] == ["api", "jobs"] and parts[3] == "cancel":
                return self._json(agent.cancel(parts[2]))
            if len(parts) < 4 or parts[:2] != ["api", "project"]:
                return self._err(404, "not found")
            pkg = self._pkg(parts[2])
            if parts[3] == "continue":
                if agent.running():
                    raise agent.Busy(f"Claude is already working on {agent.running()['title']}")
                if data.get("approve"):
                    with LOCK:
                        ep.set_approval(pkg, data["approve"], "approved with Continue")
                return self._json({"job": agent.start_continue(pkg, data.get("note", ""))})
            with LOCK:
                if parts[3] == "approve":
                    ep.set_approval(pkg, data["stage"], data.get("note", ""), undo=bool(data.get("undo")))
                elif parts[3] == "comment":
                    text = (data.get("text") or "").strip()
                    if not text:
                        return self._err(400, "empty comment")
                    rows = ep.feedback(pkg)
                    rows.append(dict(id=max((r["id"] for r in rows), default=0) + 1,
                                     date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                     file=data.get("file", ""), t=data.get("t"), line=data.get("line"),
                                     text=text, resolved=False, reply=""))
                    ep.save_feedback(pkg, rows)
                elif parts[3] == "comment-state" and len(parts) == 5:
                    rows = ep.feedback(pkg)
                    for r in rows:
                        if str(r["id"]) == parts[4]:
                            if "resolved" in data:
                                r["resolved"] = bool(data["resolved"])
                            if data.get("delete"):
                                rows.remove(r)
                            break
                    ep.save_feedback(pkg, rows)
                else:
                    return self._err(404, "not found")
            self._json(project(pkg))
        except agent.Busy as e:
            self._err(409, str(e))
        except KeyError as e:
            self._err(404, f"unknown {e}")
        except (ValueError, json.JSONDecodeError) as e:
            self._err(400, str(e))
        except RuntimeError as e:
            self._err(500, str(e))


def serve(port=8765, open_browser=True):
    agent.recover()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"TeenyTinyology review page: {url}   (Ctrl+C to stop)")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        srv.server_close()


if __name__ == "__main__":
    serve()
