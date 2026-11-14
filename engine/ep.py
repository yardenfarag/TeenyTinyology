"""One command for every stage of a Short.

    python -m engine.ep status                     # every episode: stage, next step
    python -m engine.ep status e006                # one episode in detail
    python -m engine.ep new 6 slug-words           # scaffold episodes/e006_slug_words/ (idea, facts, script)
    python -m engine.ep preview e006 [--batches]   # narration + theme + SFX -> for-review/<pkg>/2_narration/eNNN_narration_vN.mp3
    python -m engine.ep captions e006              # the caption list with durations
    python -m engine.ep look e006                  # look frames -> for-review/<pkg>/3_look_frames/
    python -m engine.ep stills e006 [--times 1,2]  # storyboard stills + contact sheet in episodes/<pkg>/review/
    python -m engine.ep check e006 [--only ...]    # automatic checks (engine.checks) -> review/checks.md
    python -m engine.ep render e006                # MP4 + QA sheet from the encoded file, then all checks
    python -m engine.ep judge-kit e006             # review packet for the video-judge agent (includes checks.md)
    python -m engine.ep final e006                 # copy MP4, cover, post.md, QA sheet -> for-review/<pkg>/4_final/
    python -m engine.ep approve e006 narration "owner OK'd v3 by ear"   # record an owner approval (lessons too: l002)
    python -m engine.ep review                     # the owner's review page: http://localhost:8765 (Shorts + Lessons)
    python -m engine.ep feedback e006 [--all]      # comments left on the review page (lessons too)
    python -m engine.ep resolve e006 7 "moved the label up"   # mark comment #7 done, saying what was done

An episode is named by number (6, 006, e006) or package (e006_slug); a lesson by l2 / l002 / l002_slug (status,
approve, feedback, resolve). Every episode module provides
build(style) -> (timeline, ctx, make_audio, cues), SLUG, HERE, and optionally look_times(cues).
"""
import argparse
import datetime
import glob
import importlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPISODES = os.path.join(ROOT, "episodes")
LESSONS = os.path.join(ROOT, "lessons")
REVIEW = os.path.join(ROOT, "for-review")
GATES = {"short": ["script", "narration", "look", "final"],            # owner approval gates (new-episode skill)
         "lesson": ["plan", "script", "narration", "board", "final"]}  # (new-lesson skill)
STAGES = GATES["short"]


# ================================================================ finding episodes and lessons
def all_pkgs():
    return sorted(d for d in os.listdir(EPISODES)
                  if re.match(r"e\d{3}_", d) and os.path.isdir(os.path.join(EPISODES, d)))


def all_lessons():
    return sorted(d for d in os.listdir(LESSONS)
                  if re.match(r"l\d{3}_", d) and os.path.isdir(os.path.join(LESSONS, d)))


def kind(pkg):
    return "lesson" if pkg.startswith("l") else "short"


def project_dir(pkg):
    return os.path.join(LESSONS if kind(pkg) == "lesson" else EPISODES, pkg)


def resolve(name, lessons=False):
    """6 / 006 / e006 / e006_slug -> episode package; with lessons=True also l2 / l002 / l002_slug."""
    name = name.replace("episodes.", "").replace("lessons.", "").strip()
    pool = all_pkgs() + (all_lessons() if lessons else [])
    if name in pool:
        return name
    m = re.match(r"([el]?)(\d{1,3})$", name)
    if m:
        pre = m.group(1) or "e"
        hits = [p for p in pool if p.startswith(f"{pre}{int(m.group(2)):03d}_")]
        if hits:
            return hits[0]
    sys.exit(f"no {'episode or lesson' if lessons else 'episode'} \"{name}\" (have: {', '.join(pool)})")


def short(pkg):
    return pkg.split("_")[0]


def load(pkg):
    return importlib.import_module(f"episodes.{pkg}.episode")


def approvals(pkg):
    p = os.path.join(project_dir(pkg), "approvals.json")
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else {}


def set_approval(pkg, stage, note="", undo=False):
    if stage not in GATES[kind(pkg)]:
        raise ValueError(f"stage must be one of {', '.join(GATES[kind(pkg)])}")
    a = approvals(pkg)
    if undo:
        a.pop(stage, None)
    else:
        a[stage] = {"date": datetime.date.today().isoformat(), "note": note}
    with open(os.path.join(project_dir(pkg), "approvals.json"), "w", encoding="utf8") as f:
        json.dump(a, f, indent=1)
    return a


# ================================================================ owner feedback (written by the review page)
def feedback(pkg):
    p = os.path.join(project_dir(pkg), "feedback.json")
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else []


def save_feedback(pkg, rows):
    with open(os.path.join(project_dir(pkg), "feedback.json"), "w", encoding="utf8") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)


def open_count(pkg):
    return sum(not r.get("resolved") for r in feedback(pkg))


def fmt_t(t):
    return f"{int(t // 60)}:{t % 60:04.1f}" if t is not None else ""


def cmd_feedback(pkg, show_all=False):
    rows = [r for r in feedback(pkg) if show_all or not r.get("resolved")]
    if not rows:
        print(f"{pkg}: no open comments")
    for r in rows:
        where = " · ".join(x for x in (r["file"], fmt_t(r.get("t")), r.get("line") or "") if x)
        mark = "✔" if r.get("resolved") else "•"
        print(f"{mark} #{r['id']} [{r['date']}] {where}\n    {r['text']}" + (f"\n    → {r['reply']}" if r.get("reply") else ""))


def cmd_resolve(pkg, cid, reply=""):
    rows = feedback(pkg)
    for r in rows:
        if str(r["id"]) == str(cid):
            r["resolved"] = True
            r["reply"] = reply or r.get("reply", "")
            save_feedback(pkg, rows)
            print(f"#{cid} resolved")
            return
    sys.exit(f"no comment #{cid}")


# ================================================================ status
def _mtime(paths):
    paths = [p for p in paths if os.path.exists(p)]
    return max((os.path.getmtime(p) for p in paths), default=0)


def stages(pkg):
    """[(stage, done: bool | None, detail)] in pipeline order. None = can't tell from the files."""
    here = os.path.join(EPISODES, pkg)
    rv = os.path.join(REVIEW, pkg)
    ok = approvals(pkg)
    code_t = _mtime(glob.glob(os.path.join(here, "*.py")))
    narr = sorted(glob.glob(os.path.join(rv, "2_narration", "*.mp3")))
    looks = glob.glob(os.path.join(rv, "3_look_frames", "*.png"))
    mp4s = sorted(glob.glob(os.path.join(here, "out", "*.mp4")), key=os.path.getmtime)
    mp4_t = os.path.getmtime(mp4s[-1]) if mp4s else 0
    chk = os.path.join(here, "review", "checks.json")
    judge = sorted(glob.glob(os.path.join(here, "judge_reports", "pass*.md")),
                   key=lambda p: int(re.sub(r"\D", "", os.path.basename(p)) or 0))
    final = glob.glob(os.path.join(rv, "4_final", "*.mp4"))
    qa = os.path.join(here, "voice_cache", "qa.json")
    qa_n = len(json.load(open(qa, encoding="utf8"))) if os.path.exists(qa) else 0

    def gate(stage):
        a = ok.get(stage)
        return f"approved {a['date']}" + (f" — {a['note']}" if a.get("note") else "") if a else "owner approval not recorded"

    facts = os.path.join(here, "facts.md")
    filled = os.path.exists(facts) and "| 1 |  |  |  |" not in open(facts, encoding="utf8").read()
    out = [("idea + facts", os.path.exists(os.path.join(here, "idea.md")) and filled,
            "idea.md, facts.md" + ("" if filled else " (facts.md not filled in)"))]
    has_script = os.path.exists(os.path.join(here, "script.py"))
    out.append(("script", has_script and "script" in ok, gate("script") if has_script else "no script.py"))
    detail = (f"{os.path.basename(narr[-1])}; " if narr else "no preview yet; ") + gate("narration")
    if qa_n:
        detail += f"; {qa_n} line(s) flagged by voice QA"
    out.append(("narration", bool(narr) and "narration" in ok and not qa_n, detail))
    out.append(("look frames", bool(looks) and "look" in ok,
                (f"{len(looks)} frames; " if looks else "none yet; ") + gate("look")))
    stale = mp4s and mp4_t < code_t
    out.append(("render", bool(mp4s) and not stale,
                (os.path.basename(mp4s[-1]) + (" — OLDER than the code, re-render" if stale else "")) if mp4s else "no MP4"))
    if os.path.exists(chk):
        rows = json.load(open(chk, encoding="utf8"))
        ne, nw = sum(r["sev"] == "ERROR" for r in rows), sum(r["sev"] == "WARN" for r in rows)
        fresh = os.path.getmtime(chk) >= max(mp4_t, code_t)
        out.append(("checks", fresh and ne == 0, f"{ne} errors, {nw} warnings" + ("" if fresh else " — out of date, re-run")))
    else:
        out.append(("checks", False, "not run"))
    if judge:
        jt = os.path.getmtime(judge[-1])
        out.append(("judge", jt >= mp4_t, f"{len(judge)} pass(es), latest {os.path.basename(judge[-1])}"
                    + ("" if jt >= mp4_t else " — the MP4 is newer, judge it again")))
    else:
        out.append(("judge", False, "no judge report"))
    pack = [os.path.exists(os.path.join(here, "out", f)) for f in ("post.md", "cover.png")]
    out.append(("upload pack", all(pack), "post.md + cover.png" if all(pack) else "missing " +
                ", ".join(f for f, e in zip(("post.md", "cover.png"), pack) if not e)))
    out.append(("final", bool(final) and "final" in ok, ("in 4_final; " if final else "not in for-review yet; ") + gate("final")))
    return out


NEXT = {"idea + facts": "write idea.md and facts.md (new-episode skill, step 1)",
        "script": "show the owner the script, then `approve <ep> script`",
        "narration": "`preview <ep>`, send the MP3, then `approve <ep> narration`",
        "look frames": "`look <ep>`, send the frames, then `approve <ep> look`",
        "render": "`render <ep>`",
        "checks": "fix the errors in review/checks.md, then `check <ep>` (or `render` again)",
        "judge": "`judge-kit <ep>`, run the video-judge agent, save judge_reports/passN.md",
        "upload pack": "write out/post.md and out/cover.png (step 7)",
        "final": "`final <ep>`, send it, then `approve <ep> final`"}


def legacy(pkg):
    return approvals(pkg).get("legacy")


def lesson_gates(pkg):
    a = approvals(pkg)
    return [(g, g in a, f"approved {a[g]['date']}" + (f" — {a[g]['note']}" if a[g].get("note") else "")
             if g in a else "owner approval not recorded") for g in GATES["lesson"]]


def cmd_status(pkg=None):
    if pkg and legacy(pkg):
        print(f"{pkg}: {legacy(pkg)}")
    if pkg:
        n = open_count(pkg)
        if n:
            print(f"{n} open comment(s) from the review page — `python -m engine.ep feedback {short(pkg)}`")
        rows = lesson_gates(pkg) if kind(pkg) == "lesson" else stages(pkg)
        print(f"{pkg}")
        for name, done, detail in rows:
            print(f"  {'✔' if done else '·'} {name:13} {detail}")
        nxt = next((n for n, d, _ in rows if not d), None)
        if kind(pkg) == "lesson":
            print(f"\nnext gate: {nxt} (new-lesson skill)" if nxt else "\nall gates approved")
        else:
            print(f"\nnext: {NEXT[nxt].replace('<ep>', short(pkg))}" if nxt else "\nall stages done")
        return
    print(f"{'project':24} {'stage':14} next")
    for p in all_pkgs() + all_lessons():
        n = open_count(p)
        if n:
            print(f"{p:24} ** {n} open comment(s) from the review page **")
        if legacy(p):
            print(f"{p:24} finished     ({legacy(p)})")
            continue
        if kind(p) == "lesson":
            nxt = next((g for g, d, _ in lesson_gates(p) if not d), None)
            print(f"{p:24} lesson       {'next gate: ' + nxt if nxt else 'all gates approved'}")
            continue
        rows = stages(p)
        nxt = next((n for n, d, _ in rows if not d), None)
        done = sum(bool(d) for _, d, _ in rows)
        print(f"{p:24} {done}/{len(rows)} done     {nxt or 'all done'}" + (f": {dict((n, x) for n, _, x in rows)[nxt]}" if nxt else ""))


# ================================================================ stage commands
def cmd_new(num, slug):
    pkg = f"e{int(num):03d}_{slug.replace('-', '_')}"
    here = os.path.join(EPISODES, pkg)
    if os.path.exists(here):
        sys.exit(f"{here} exists")
    os.makedirs(os.path.join(here, "voice_cache"))
    open(os.path.join(here, "__init__.py"), "w").close()
    open(os.path.join(here, "idea.md"), "w", encoding="utf8").write(
        f"# E{int(num):03d} — idea\n\nOwner's idea, in their words:\n\n> \n\n## Beats\n1. Hook\n2. \n3. \n\n## Cast\n- \n")
    open(os.path.join(here, "facts.md"), "w", encoding="utf8").write(
        "# Facts\n\nSpecies the story follows: *...*\n\n| # | Claim (as narrated) | Source | Hedge |\n|---|---|---|---|\n| 1 |  |  |  |\n")
    open(os.path.join(here, "script.py"), "w", encoding="utf8").write(
        f'"""Episode {int(num):03d} narration. Pauses are seconds of silence after each line. "|" marks a caption break."""\n'
        "from engine.voice import Line\n\nSCRIPT = [\n    Line(\"hook\", \"...\", 0.9),\n]\n\n"
        "# (line_id, word or None, effect, gain, offset) — every sound effect, anchored to a word\nSFX = [\n]\n")
    for d in ("1_cast", "2_narration", "3_look_frames", "4_final"):
        os.makedirs(os.path.join(REVIEW, pkg, d), exist_ok=True)
    print(f"created {here} and for-review/{pkg}/. Next: idea.md + facts.md; copy the latest episode.py when the "
          f"script is approved.")


def cmd_preview(pkg, batches=False):
    out_dir = os.path.join(REVIEW, pkg, "2_narration")
    os.makedirs(out_dir, exist_ok=True)
    vs = [int(m.group(1)) for f in os.listdir(out_dir) for m in [re.search(r"_narration_v(\d+)\.mp3$", f)] if m]
    out = os.path.join(out_dir, f"{short(pkg)}_narration_v{max(vs, default=0) + 1}.mp3")
    cmd = [sys.executable, "-m", "engine.preview", f"episodes.{pkg}.script", out] + (["--batches"] if batches else [])
    subprocess.run(cmd, check=True, cwd=ROOT)
    qa = os.path.join(EPISODES, pkg, "voice_cache", "qa.json")
    flagged = json.load(open(qa, encoding="utf8")) if os.path.exists(qa) else {}
    if flagged:
        print(f"\n!! voice QA flagged {', '.join(flagged)} — bump their `take` before sending this to the owner")
    from engine import checks
    sc = importlib.import_module(f"episodes.{pkg}.script")
    from engine.voice import narrate
    _, cues, _, _ = narrate(sc.SCRIPT, os.path.join(EPISODES, pkg, "voice_cache"))
    for f in checks.check_script(sc, cues, os.path.join(EPISODES, pkg)):
        print(f"{f.sev:5} {f.when():>9}  {f.check}: {f.msg}")
    print(f"\nfor the owner: {out}")


def cmd_captions(pkg, style):
    tl, *_ = load(pkg).build(style)
    for cap in tl.captions:
        d = cap.end - cap.start
        print(f"{cap.start:6.2f}-{cap.end:6.2f} ({d:4.2f}s){' !' if d < 0.9 else '  '} {' '.join(w for w, _, _ in cap.words)}")


def cmd_look(pkg, style):
    from engine import render
    ep = load(pkg)
    if not hasattr(ep, "look_times"):
        sys.exit(f"{pkg}/episode.py has no look_times(cues)")
    tl, ctx, _, Q = ep.build(style)
    out = os.path.join(REVIEW, pkg, "3_look_frames")
    shutil.rmtree(out, ignore_errors=True)
    lt = ep.look_times(Q)
    paths = render.stills(tl, ctx, list(lt.values()), out, prefix="look")
    named = []
    for (name, _), p in zip(lt.items(), paths):
        dst = os.path.join(out, f"{len(named) + 1:02d}_{name}.png")
        os.replace(p, dst)
        named.append(dst)
    sheet = render.contact_sheet(named, os.path.join(out, "00_overview.png"), cols=5, width=2800)
    print(f"look frames: {out}\noverview:    {sheet}")


def cmd_stills(pkg, style, times=None, copy_to=None):
    from engine import render
    ep = load(pkg)
    tl, ctx, _, Q = ep.build(style)
    review = os.path.join(ep.HERE, "review", style)
    shutil.rmtree(review, ignore_errors=True)            # stale stills look like timing bugs (judge lessons)
    if times:
        ts = [float(x) for x in times.split(",")]
    elif hasattr(ep, "key_times"):
        ts = ep.key_times(Q)
    else:
        ts = sorted({round((s.start + min(s.end, tl.duration)) / 2, 2) for s in tl.scenes})
    paths = render.stills(tl, ctx, ts, review)
    sheet = render.contact_sheet(paths, os.path.join(ep.HERE, "review", f"storyboard_{style}.png"), cols=6, width=2800)
    print("sheet", sheet)
    if copy_to:
        shutil.copy(sheet, copy_to)


def cmd_check(pkg, style, only=None, mp4=None):
    from engine import checks
    found = checks.run(pkg, mp4, style, only=only)
    for f in found:
        print(f"{f.sev:5} {f.when():>15}  {f.group}/{f.check}: {f.msg}")
    ne = sum(f.sev == "ERROR" for f in found)
    print(f"\n{ne} errors, {sum(f.sev == 'WARN' for f in found)} warnings -> "
          f"{os.path.join(EPISODES, pkg, 'review', 'checks.md')}")
    return ne


def cmd_render(pkg, style, check=True, copy_to=None):
    from engine import render
    from engine.audio import mix
    ep = load(pkg)
    tl, ctx, make_audio, Q = ep.build(style)
    outdir = os.path.join(ep.HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    wav = make_audio(os.path.join(outdir, f"audio_{style}.wav"))
    mp4 = os.path.join(outdir, f"{ep.SLUG}_{style}.mp4")
    render.video(tl, ctx, mp4, wav)
    os.remove(wav)
    print("video", mp4, "LUFS", mix.measure_lufs(mp4))
    os.makedirs(os.path.join(ep.HERE, "review"), exist_ok=True)
    qa = render.sample_frames(mp4, os.path.join(ep.HERE, "review", f"qa_{style}.png"), every=1.0, cols=10)
    print("QA sheet", qa)
    if copy_to:
        shutil.copy(mp4, copy_to)
        shutil.copy(qa, copy_to)
    if check:
        return cmd_check(pkg, style, mp4=mp4)
    return 0


def cmd_judge_kit(pkg, style):
    here = os.path.join(EPISODES, pkg)
    mp4s = sorted(glob.glob(os.path.join(here, "out", f"*_{style}.mp4")), key=os.path.getmtime)
    if not mp4s:
        sys.exit("no MP4 — render first")
    subprocess.run([sys.executable, "-m", "engine.judge_kit", f"episodes.{pkg}", mp4s[-1], "--style", style],
                   check=True, cwd=ROOT)


def cmd_final(pkg):
    here = os.path.join(EPISODES, pkg)
    dst = os.path.join(REVIEW, pkg, "4_final")
    os.makedirs(dst, exist_ok=True)
    files = sorted(glob.glob(os.path.join(here, "out", "*.mp4")), key=os.path.getmtime)[-1:]
    files += [p for p in (os.path.join(here, "out", "cover.png"), os.path.join(here, "out", "post.md"))
              if os.path.exists(p)]
    files += glob.glob(os.path.join(here, "review", "qa_*.png"))
    for f in files:
        shutil.copy(f, dst)
        print("copied", os.path.join(dst, os.path.basename(f)))


def cmd_approve(pkg, stage, note=""):
    try:
        set_approval(pkg, stage, note)
    except ValueError as e:
        sys.exit(str(e))
    print(f"{pkg}: {stage} approved")


# ================================================================ CLI
def episode_main(episode_file):
    """Back-compat entry for `python -m episodes.<pkg>.episode stills|look|render|captions|check`."""
    pkg = os.path.basename(os.path.dirname(os.path.abspath(episode_file)))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["stills", "look", "render", "captions", "check"])
    ap.add_argument("--style", default="illustrated")
    ap.add_argument("--copy-to", default=None)
    ap.add_argument("--times", default=None)
    a = ap.parse_args()
    sys.exit(dispatch(a.cmd, pkg, a))


def dispatch(cmd, pkg, a):
    style = getattr(a, "style", "illustrated")
    if cmd == "captions":
        cmd_captions(pkg, style)
    elif cmd == "look":
        cmd_look(pkg, style)
    elif cmd == "stills":
        cmd_stills(pkg, style, getattr(a, "times", None), getattr(a, "copy_to", None))
    elif cmd == "check":
        only = getattr(a, "only", None)
        return 1 if cmd_check(pkg, style, only.split(",") if only else None, getattr(a, "mp4", None)) else 0
    elif cmd == "render":
        return 1 if cmd_render(pkg, style, not getattr(a, "no_check", False), getattr(a, "copy_to", None)) else 0
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["status", "new", "preview", "captions", "look", "stills", "check", "render",
                                    "judge-kit", "final", "approve", "feedback", "resolve", "review"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--style", default="illustrated")
    ap.add_argument("--times")
    ap.add_argument("--only", help="check: comma list of script,timeline,layout,mp4")
    ap.add_argument("--mp4")
    ap.add_argument("--batches", action="store_true")
    ap.add_argument("--no-check", action="store_true", help="render: skip the automatic checks")
    ap.add_argument("--copy-to")
    ap.add_argument("--all", action="store_true", help="feedback: include resolved comments")
    ap.add_argument("--port", type=int, default=8765, help="review: local port")
    a = ap.parse_args()
    if a.cmd == "review":
        from engine import review
        return review.serve(a.port)
    if a.cmd == "status":
        return cmd_status(resolve(a.args[0], lessons=True) if a.args else None)
    if a.cmd in ("feedback", "resolve", "approve"):
        if not a.args:
            sys.exit(f"usage: {a.cmd} <episode|lesson> ...")
        pkg = resolve(a.args[0], lessons=True)
        if a.cmd == "feedback":
            return cmd_feedback(pkg, a.all)
        if a.cmd == "resolve":
            if len(a.args) < 2:
                sys.exit("usage: resolve <episode|lesson> <comment id> [what was done]")
            return cmd_resolve(pkg, a.args[1], " ".join(a.args[2:]))
        if len(a.args) < 2:
            sys.exit(f"usage: approve <episode|lesson> <{'|'.join(GATES[kind(pkg)])}> [note]")
        return cmd_approve(pkg, a.args[1], " ".join(a.args[2:]))
    if a.cmd == "new":
        if len(a.args) != 2:
            sys.exit("usage: new <number> <slug>")
        return cmd_new(*a.args)
    if not a.args:
        sys.exit(f"usage: {a.cmd} <episode>")
    pkg = resolve(a.args[0])
    if a.cmd == "preview":
        return cmd_preview(pkg, a.batches)
    if a.cmd == "judge-kit":
        return cmd_judge_kit(pkg, a.style)
    if a.cmd == "final":
        return cmd_final(pkg)
    sys.exit(dispatch(a.cmd, pkg, a))


if __name__ == "__main__":
    main()
