#!/usr/bin/env python3
"""Captures evidence images from the real Ghidra CodeBrowser window.

Run this yourself through scripts/tv2-capture-gui.ps1. The window is opened on a
throw-away copy of the TV2 project with a separate Ghidra settings folder. If Ghidra
shows its user agreement, read it and decide yourself; this script never answers it.
[TV2] comments and highlights exist only in memory and are never saved. A caption
band is added above each capture and says that it was added afterwards.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = "20261118-094956"
WORK = ROOT / "artifacts" / "ghidra" / BUILD
GHIDRA = ROOT / "artifacts" / "tools" / "ghidra_12.2_PUBLIC"
SETTINGS = ROOT / "artifacts" / "ghidra" / "gui-settings"
G1_02, G1_03 = "evidence/G1/TV2/G1-TV2-02/images", "evidence/G1/TV2/G1-TV2-03/images"
G2_01, G2_02 = "evidence/G2/TV2/G2-TV2-01/images", "evidence/G2/TV2/G2-TV2-02/images"
G3_01 = "evidence/G3/TV2/G3-TV2-01/images"
COLOR = (255, 236, 150)


def view(out, rva, note, comments=None):
    return {"type": "view", "out": out, "rva": rva, "note": note, "comments": comments or {}}


SHOTS = {
    "B1.exe": [
        {"type": "imports", "out": f"{G1_02}/B1-imports.png", "note": "Symbol Tree > Imports: CreateFileW, WriteFile, CloseHandle là import sẵn"},
        {"type": "strings", "out": f"{G1_02}/B1-strings.png", "note": "Defined Strings: tên API thuộc bảng import, Ghidra không thấy mã nào tham chiếu các chuỗi này"},
        view(f"{G1_02}/B1-calls.png", 0x1048, "Lời gọi API đi qua ô IAT do loader điền",
             {0x1048: "[TV2] CALL qua IAT: CreateFileW", 0x1099: "[TV2] CALL qua IAT: WriteFile", 0x10A8: "[TV2] CALL qua IAT: CloseHandle"}),
    ],
    "B2.exe": [
        {"type": "imports", "out": f"{G1_02}/B2-imports.png", "note": "Symbol Tree > Imports: có LoadLibraryW và GetProcAddress"},
        {"type": "strings", "out": f"{G1_02}/B2-strings.png", "note": "Defined Strings: tên API xuất hiện rõ dưới dạng chuỗi"},
        view(f"{G1_02}/B2-calls.png", 0x1064, "Resolve động bằng TÊN RÕ, không có hash",
             {0x1064: "[TV2] GetProcAddress(module, \"CreateFileW\"): tên là hằng chuỗi",
              0x107B: "[TV2] GetProcAddress(module, \"WriteFile\")", 0x1092: "[TV2] GetProcAddress(module, \"CloseHandle\")",
              0x1102: "[TV2] gọi gián tiếp qua con trỏ đã resolve theo tên"}),
    ],
    "P1.exe": [
        {"type": "imports", "out": f"{G2_01}/P1-D0-C1-imports.png", "note": "D0-C1: chương trình import GetProcAddress"},
        view(f"{G1_03}/P1-1-hash-loop.png", 0x1026, "Bước hash: vòng DJB2 trên từng byte của chuỗi đầu vào",
             {0x1009: "[TV2] seed = 0x1505 (5381)", 0x1026: "[TV2] h = h * 33", 0x1032: "[TV2] h = h + byte"}),
        view(f"{G1_03}/P1-2-export-hash-compare.png", 0x12DD, "Tên export -> hash -> so sánh -> giữ tên được chọn",
             {0x1229: "[TV2][1] đọc AddressOfNames (export dir +0x20)", 0x1294: "[TV2][2] đọc RVA tên thứ i",
              0x129C: "[TV2][2] module base + RVA = con trỏ tên export", 0x12DD: "[TV2][3] hash tên export",
              0x12E2: "[TV2][4] so hash với giá trị đích (tham số)", 0x130B: "[TV2][5] khớp: ghi con trỏ tên ra tham số out"}),
        view(f"{G1_03}/P1-3-resolve.png", 0x13B1, "Tên được chọn đi vào GetProcAddress",
             {0x1391: "[TV2][5] gọi hàm tìm tên, nhận tên qua tham số out", 0x13A7: "[TV2][6] RDX = tên export đã chọn",
              0x13B1: "[TV2][6] GetProcAddress(module, tên đã chọn)"}),
        view(f"{G1_03}/P1-4-pointer-use.png", 0x15B1, "Địa chỉ đã resolve được dùng làm đích lời gọi gián tiếp",
             {0x1509: "[TV2] gọi resolver với hash đích", 0x15B1: "[TV2][7] gọi gián tiếp qua địa chỉ đã resolve"}),
        view(f"{G2_01}/P1-D0-C2-hash-loop.png", 0x1026, "D0-C2: vòng có nạp byte, trộn và kết hợp",
             {0x101F: "[TV2] D0-C2: nạp byte", 0x1026: "[TV2] D0-C2: trộn (IMUL)", 0x1032: "[TV2] D0-C2: kết hợp (ADD)", 0x1044: "[TV2] D0-C2: cạnh quay lui"}),
        view(f"{G2_01}/P1-D0-C3-indirect-call.png", 0x15B1, "D0-C3: lời gọi gián tiếp không qua ô import",
             {0x15B1: "[TV2] D0-C3: gọi gián tiếp ngoài IAT"}),
    ],
    "TV2C-B3.exe": [
        view(f"{G2_02}/B3-name-table.png", 0x1161, "B3: resolve hợp lệ theo tên lấy từ bảng chuỗi, không có hash",
             {0x1161: "[TV2] GetProcAddress với tên từ bảng chuỗi", 0x1046: "[TV2] gọi gián tiếp qua con trỏ"}),
    ],
    "TV2C-B4.exe": [
        view(f"{G2_02}/B4-data-hash.png", 0x1026, "B4: vòng DJB2 chỉ băm dữ liệu marker",
             {0x1026: "[TV2] hash dữ liệu, không liên quan API"}),
        view(f"{G2_02}/B4-static-imports.png", 0x10B9, "B4: API file được gọi qua import sẵn",
             {0x10B9: "[TV2] CreateFileW qua IAT", 0x10F3: "[TV2] WriteFile qua IAT", 0x1102: "[TV2] CloseHandle qua IAT"}),
    ],
    "TV2C-B5.exe": [
        {"type": "imports", "out": f"{G3_01}/B5-FP-D0-C1-imports.png", "note": "FP của D0: điều kiện C1 đúng vì có import GetProcAddress"},
        view(f"{G3_01}/B5-FP-D0-C2-hash-loop.png", 0x1125, "FP của D0: vòng FNV-1a chỉ kiểm tra chuỗi cấu hình",
             {0x1111: "[TV2] D0-C2: XOR byte", 0x1125: "[TV2] D0-C2: nhân FNV; không liên quan API"}),
        view(f"{G3_01}/B5-FP-D0-resolve-by-name.png", 0x119E, "FP của D0: tên API là hằng chuỗi, không lấy từ hash",
             {0x119E: "[TV2] GetProcAddress với hằng chuỗi", 0x11B5: "[TV2] hằng chuỗi", 0x11CC: "[TV2] hằng chuỗi"}),
        view(f"{G3_01}/B5-FP-D0-C3-indirect-call.png", 0x1046, "FP của D0: lời gọi gián tiếp dùng con trỏ resolve theo tên",
             {0x1046: "[TV2] D0-C3: đúng về cú pháp, nhưng không chứng minh hashing"}),
    ],
    "TV2C-B6.exe": [
        view(f"{G2_02}/B6-export-strcmp.png", 0x11CA, "B6: duyệt tên export nhưng so bằng strcmp, không hash",
             {0x11CA: "[TV2] strcmp(tên export, tên cần tìm)"}),
        view(f"{G2_02}/B6-resolve.png", 0x1224, "B6: tên export tìm được đi vào GetProcAddress",
             {0x1224: "[TV2] GetProcAddress với tên export đã khớp bằng strcmp"}),
    ],
}


def log(message):
    print(message, flush=True)


class Capture:
    def __init__(self, only, out_root):
        self.only = only
        self.out_root = Path(out_root)
        self.done = []
        self.failed = None

    # ---- Java helpers ---------------------------------------------------------------
    def bind(self):
        import jpype
        self.jpype = jpype
        for name, path in {
            "SwingUtilities": "javax.swing.SwingUtilities", "Window": "java.awt.Window", "Color": "java.awt.Color",
            "Image": "java.awt.image.BufferedImage", "ImageIO": "javax.imageio.ImageIO", "JFile": "java.io.File",
            "List": "java.util.List", "AppInfo": "ghidra.framework.main.AppInfo",
            "GTree": "docking.widgets.tree.GTree", "JTable": "javax.swing.JTable",
            "CommentType": "ghidra.program.model.listing.CommentType",
            "GoToService": "ghidra.app.services.GoToService", "ProgramManager": "ghidra.app.services.ProgramManager",
            "Colorizing": "ghidra.app.plugin.core.colorizer.ColorizingService",
        }.items():
            setattr(self, name, jpype.JClass(path))

    def edt(self, fn, timeout=60):
        done, box = threading.Event(), {}
        def task():
            try:
                box["value"] = fn()
            except BaseException as exc:  # reported on the worker thread
                box["error"] = exc
            finally:
                done.set()
        self.SwingUtilities.invokeLater(self.jpype.JProxy("java.lang.Runnable", dict={"run": task}))
        if not done.wait(timeout):
            raise TimeoutError("Swing call timed out; open windows: " + "; ".join(self.windows()))
        if "error" in box:
            raise box["error"]
        return box.get("value")

    def windows(self):
        titles = []
        for window in self.Window.getWindows():
            if window.isShowing():
                title = window.getTitle() if hasattr(window, "getTitle") else ""
                titles.append(str(title or window.getClass().getSimpleName()))
        return titles

    def walk(self, component, kind):
        if isinstance(component, kind):
            return component
        if hasattr(component, "getComponents"):
            for child in component.getComponents():
                found = self.walk(child, kind)
                if found is not None:
                    return found
        return None

    def paint(self, component, width, height):
        image = self.Image(int(width), int(height), self.Image.TYPE_INT_RGB)
        graphics = image.createGraphics()
        graphics.setColor(self.Color.WHITE)
        graphics.fillRect(0, 0, int(width), int(height))
        component.printAll(graphics)
        graphics.dispose()
        return image

    # ---- output ---------------------------------------------------------------------
    def save(self, image, shot, program):
        target = self.out_root / shot["out"]
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = target.with_suffix(".raw.png")
        self.ImageIO.write(image, "png", self.JFile(str(raw)))
        lines = [f"{program.getName()}  |  SHA-256 {str(program.getExecutableSHA256()).upper()}",
                 f"Ghidra 12.2 CodeBrowser  |  image base 0x{program.getImageBase().getOffset():X}"
                 + (f"  |  vị trí RVA 0x{shot['rva']:X}" if "rva" in shot else ""),
                 shot["note"],
                 "Dòng [TV2] và màu nền do người phân tích thêm; tên FUN_* là tên Ghidra tự đặt. Dải chú thích này được ghép sau khi chụp."]
        add_caption(raw, target, lines)
        raw.unlink()
        self.done.append(shot["out"])
        log(f"saved {shot['out']}")

    # ---- views ----------------------------------------------------------------------
    def provider(self, tool, name):
        provider = tool.getComponentProvider(name)
        if provider is None:
            raise RuntimeError(f"Ghidra window not found: {name}")
        self.edt(lambda: tool.showComponentProvider(provider, True))
        return provider

    def imports(self, tool, program, shot):
        provider = self.provider(tool, "Symbol Tree")
        time.sleep(1.5)
        def run():
            tree = self.walk(provider.getComponent(), self.GTree)
            node = tree.getModelRoot().getChild("Imports")
            tree.expandTree(node)
            return tree
        tree = self.edt(run)
        for _ in range(60):
            if not tree.isBusy():
                break
            time.sleep(0.25)
        time.sleep(1.0)
        def draw():
            view_tree = tree.getJTree()
            size = view_tree.getPreferredSize()
            width, height = max(size.width, 520), min(size.height, 2200)
            view_tree.setSize(width, height)
            view_tree.doLayout()
            return self.paint(view_tree, width, height)
        self.save(self.edt(draw), shot, program)

    def strings(self, tool, program, shot):
        provider = self.provider(tool, "Defined Strings")
        table = None
        for _ in range(80):
            table = self.edt(lambda: self.walk(provider.getComponent(), self.JTable))
            if table is not None and table.getRowCount() > 0 and not provider.getComponent().isShowing() is False:
                break
            time.sleep(0.25)
        time.sleep(1.5)
        def draw():
            header = table.getTableHeader()
            width = max(table.getWidth(), 1100)
            rows = min(table.getRowCount(), 60)
            head = max(header.getPreferredSize().height, 22)
            body = rows * table.getRowHeight()
            table.setSize(width, table.getRowCount() * table.getRowHeight())
            table.doLayout()
            header.setSize(width, head)
            header.doLayout()
            image = self.Image(int(width), int(head + body), self.Image.TYPE_INT_RGB)
            graphics = image.createGraphics()
            graphics.setColor(self.Color.WHITE)
            graphics.fillRect(0, 0, int(width), int(head + body))
            header.printAll(graphics)
            graphics.translate(0, int(head))
            graphics.setClip(0, 0, int(width), int(body))
            table.printAll(graphics)
            graphics.dispose()
            return image
        self.save(self.edt(draw), shot, program)

    def code_view(self, tool, program, shot):
        base = program.getImageBase()
        goto = tool.getService(self.GoToService.class_)
        decompiler = self.provider(tool, "Decompiler")
        self.provider(tool, "Listing")
        self.edt(lambda: tool.showComponentProvider(decompiler, True))
        address = base.add(shot["rva"])
        self.edt(lambda: goto.goTo(address))
        for _ in range(120):
            time.sleep(0.25)
            if not decompiler.isBusy():
                break
        time.sleep(1.6)
        frame = tool.getToolFrame()
        def draw():
            pane = frame.getRootPane()
            return self.paint(pane, pane.getWidth(), pane.getHeight())
        self.save(self.edt(draw), shot, program)

    def annotate(self, tool, program, shots):
        colorizer = tool.getService(self.Colorizing.class_)
        color = self.Color(*COLOR)
        listing, base = program.getListing(), program.getImageBase()
        def apply():
            tx = program.startTransaction("TV2 evidence annotations (not saved)")
            try:
                for shot in shots:
                    for rva, text in shot.get("comments", {}).items():
                        address = base.add(rva)
                        listing.setComment(address, self.CommentType.PRE, text)
                        if colorizer is not None:
                            colorizer.setBackgroundColor(address, address, color)
            finally:
                program.endTransaction(tx, True)
        self.edt(apply)

    # ---- main flow ------------------------------------------------------------------
    def run(self):
        import jpype
        for _ in range(600):
            if jpype.isJVMStarted():
                break
            time.sleep(0.25)
        self.bind()
        project = None
        notified = False
        for _ in range(2400):
            if not notified and any("Agreement" in t for t in self.windows()):
                log("Ghidra is showing its user agreement. Read it and answer it in the Ghidra window.")
                notified = True
            project = self.AppInfo.getActiveProject()
            if project is not None and self.AppInfo.getFrontEndTool() is not None:
                break
            time.sleep(0.25)
        if project is None:
            raise RuntimeError("Project did not open; windows: " + "; ".join(self.windows()))
        time.sleep(3)
        log("windows after startup: " + "; ".join(self.windows()))
        root = project.getProjectData().getRootFolder()
        names = [n for n in SHOTS if not self.only or n.replace(".exe", "") in self.only]
        first = root.getFile(names[0])
        files = self.List.of(first)
        tool = self.edt(lambda: project.getToolServices().launchTool("CodeBrowser", files), 180)
        if tool is None:
            raise RuntimeError("CodeBrowser could not be started")
        time.sleep(8)
        frame = tool.getToolFrame()
        self.edt(lambda: (frame.setBounds(0, 0, 1520, 840), frame.validate()))
        time.sleep(2)
        manager = tool.getService(self.ProgramManager.class_)
        for name in names:
            domain_file = root.getFile(name)
            if domain_file is None:
                raise RuntimeError(f"Program is not in the project: {name}")
            program = self.edt(lambda: manager.openProgram(domain_file), 120)
            time.sleep(3)
            log(f"opened {name}; windows: " + "; ".join(self.windows()))
            self.annotate(tool, program, SHOTS[name])
            time.sleep(1)
            for shot in SHOTS[name]:
                getattr(self, {"view": "code_view", "imports": "imports", "strings": "strings"}[shot["type"]])(tool, program, shot)
            self.edt(lambda: manager.closeProgram(program, True), 60)
            time.sleep(1)


def add_caption(source, target, lines):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.open(source).convert("RGB")
    regular = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 16)
    probe = ImageDraw.Draw(image)
    width = max([image.width] + [int(probe.textlength(t, font=bold if i == 2 else regular)) + 24 for i, t in enumerate(lines)])
    band = 12 + 23 * len(lines)
    canvas = Image.new("RGB", (width, image.height + band), "white")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, band - 1), fill=(32, 41, 56))
    y = 7
    for index, text in enumerate(lines):
        draw.text((12, y), text, font=bold if index == 2 else regular, fill=(255, 224, 130) if index == 2 else (235, 239, 245))
        y += 23
    canvas.paste(image, (0, band))
    canvas.save(target, optimize=True)


def prepare_project():
    target = WORK / "gui-project"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    shutil.copy2(WORK / "projects" / "TV2.gpr", target / "TV2.gpr")
    shutil.copytree(WORK / "projects" / "TV2.rep", target / "TV2.rep")
    return target / "TV2.gpr"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="", help="comma list such as P1,B1")
    parser.add_argument("--out-root", default=str(ROOT))
    args = parser.parse_args()
    only = {x for x in args.only.split(",") if x}
    os.environ["JAVA_HOME"] = str(next((ROOT / "artifacts" / "tools").glob("jdk-25*")))
    os.environ["JAVA_HOME_OVERRIDE"] = os.environ["JAVA_HOME"]
    os.environ["GHIDRA_INSTALL_DIR"] = str(GHIDRA)
    gpr = prepare_project()
    SETTINGS.mkdir(parents=True, exist_ok=True)
    from pyghidra.launcher import GuiPyGhidraLauncher
    launcher = GuiPyGhidraLauncher(install_dir=GHIDRA)
    launcher.add_vmargs(f"-Dapplication.settingsdir={SETTINGS}")
    launcher.args = [str(gpr)]
    capture = Capture(only, args.out_root)
    status = {"code": 1}

    def worker():
        try:
            capture.run()
            status["code"] = 0
        except BaseException:
            traceback.print_exc()
        finally:
            (WORK / "gui-capture-result.json").write_text(
                json.dumps({"exit": status["code"], "images": capture.done}, indent=2), encoding="utf-8")
            log(f"finished: exit={status['code']} images={len(capture.done)}")
            import jpype
            if jpype.isJVMStarted():
                jpype.JClass("java.lang.Runtime").getRuntime().halt(status["code"])
            os._exit(status["code"])

    def watchdog():
        time.sleep(2400)
        log("watchdog: time limit reached")
        os._exit(3)

    threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
    launcher.start()
    return status["code"]


if __name__ == "__main__":
    sys.exit(main())
