#!/usr/bin/env python3
"""Draws the G1-TV2-01 mechanism diagram (a teaching diagram, not a tool screenshot)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = "Arial"
OUT = Path(__file__).resolve().parents[1] / "docs" / "tv2" / "images" / "pe-mechanism.png"
INK, MUTED = "#1F2937", "#4B5563"
BLUE, GREEN, AMBER, RED, GRAY = "#DBEAFE", "#DCFCE7", "#FEF3C7", "#FEE2E2", "#F3F4F6"

fig, ax = plt.subplots(figsize=(16, 10.6), dpi=110)
ax.set_xlim(0, 160)
ax.set_ylim(0, 106)
ax.axis("off")


def box(x, y, w, h, text, fill=GRAY, size=10.5, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.9", fc=fill, ec=MUTED, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK, weight=weight, linespacing=1.25)


def arrow(a, b, color=MUTED):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, lw=1.3, color=color, shrinkA=0, shrinkB=0))


def label(x, y, text, size=12.5, weight="bold", color=INK):
    ax.text(x, y, text, fontsize=size, weight=weight, color=color, va="center")


ax.text(3, 102.5, "PE, imports, exports và ba cách có được địa chỉ hàm", fontsize=17, weight="bold", color=INK, va="center")

label(3, 96.5, "Cấu trúc liên quan trong file PE32+")
box(3, 86, 17, 7.5, "DOS header\ne_lfanew tại +0x3C")
box(25, 86, 18, 7.5, "NT headers\nOptional header")
box(48, 86, 20, 7.5, "DataDirectory\n[0] Export, [1] Import")
arrow((20.5, 89.7), (24.6, 89.7))
arrow((43.5, 89.7), (47.6, 89.7))
box(76, 89.8, 24, 4.6, "Import Directory", BLUE, weight="bold")
box(104, 89.8, 25, 4.6, "Tên import (INT)", BLUE)
box(133, 89.8, 24, 4.6, "IAT: loader ghi địa chỉ", BLUE)
box(76, 83.6, 24, 4.6, "Export Directory (DLL)", GREEN, weight="bold")
box(104, 83.6, 25, 4.6, "AddressOfNames (+0x20)", GREEN)
box(133, 83.6, 24, 4.6, "NameOrdinals, Functions", GREEN)
arrow((68.5, 91), (75.6, 92))
arrow((68.5, 88.5), (75.6, 86))
for y in (92.1, 85.9):
    arrow((100.5, y), (103.6, y))
    arrow((129.5, y), (132.6, y))

lanes = [
    (66, BLUE, "B1 — import sẵn", "Không tìm hàm lúc chạy", [
        "Linker ghi tên API\nvào bảng import", "Loader nạp DLL,\nđiền IAT", "CALL [IAT]\nvd. B1 + 0x1048", "CreateFileW chạy"]),
    (44, AMBER, "B2 — resolve động theo tên", "Có tìm lúc chạy, không có hash", [
        "LoadLibraryW\nnạp kernel32", "Hằng chuỗi\n\"CreateFileW\"", "GetProcAddress(module, tên)\nvd. B2 + 0x1064", "CALL [RSP+0x68]\nqua con trỏ"]),
]
for y, fill, title, note, steps in lanes:
    label(3, y + 13.2, title)
    ax.text(3, y + 10.2, note, fontsize=10.5, color=MUTED, va="center")
    x, width, gap = 3, 34, 5.3
    for index, step in enumerate(steps):
        box(x, y, width, 8, step, fill)
        if index < len(steps) - 1:
            arrow((x + width + 0.5, y + 4), (x + width + gap - 0.5, y + 4))
        x += width + gap

label(3, 35.2, "P1 — API hashing: tên được chọn bằng hash của tên export (toàn bộ địa chỉ thuộc cùng một binary P1)")
ax.text(3, 32.2, "PoC vẫn gọi GetProcAddress với TÊN đã chọn. GetProcAddress không nhận giá trị hash.", fontsize=10.5, color=MUTED, va="center")
row1 = ["1. Đọc Export Directory\nP1 + 0x1196", "2. base + AddressOfNames[i]\nP1 + 0x1294, 0x129C", "3. Hash tên (h*33+byte)\nP1 + 0x12DD → 0x1000", "4. So với hash đích\nP1 + 0x12E2"]
row2 = ["5. Khớp: giữ con trỏ tên\nP1 + 0x1306, 0x130B", "6. GetProcAddress(module, tên)\nP1 + 0x13B1", "7. CALL [RSP+0x68]\nP1 + 0x15B1"]
x = 3
for index, step in enumerate(row1):
    box(x, 20.5, 34, 8.2, step, RED)
    if index < 3:
        arrow((x + 34.5, 24.6), (x + 38.8, 24.6))
    x += 39.3
x = 3
for index, step in enumerate(row2):
    box(x, 7.7, 34, 8.2, step, RED)
    if index < 2:
        arrow((x + 34.5, 11.8), (x + 38.8, 11.8))
    x += 39.3
arrow((137, 20), (20, 16.3))
ax.text(121, 11.8, "Dấu hiệu đứng riêng không đủ:\nGetProcAddress, gọi gián tiếp hay vòng hash\nphải được nối bằng luồng dữ liệu.", fontsize=10.5, color=INK, va="center")
ax.text(3, 2.5, "RVA lấy từ build 20261118-094956. Địa chỉ runtime có thể khác; forwarded export có thể trả địa chỉ ở module khác.", fontsize=9.5, color=MUTED, va="center")
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, facecolor="white", bbox_inches="tight", pad_inches=0.15)
print(OUT)
