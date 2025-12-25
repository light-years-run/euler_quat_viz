# -*- coding: utf-8 -*-
import numpy as np
import tkinter as tk
from tkinter import ttk
from math import sin, cos, atan2, asin

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# =========================
# 四元数 <-> 欧拉角 转换函数
# =========================
def euler_to_quat(roll, pitch, yaw, order="XYZ"):
    cr = cos(roll / 2); sr = sin(roll / 2)
    cp = cos(pitch / 2); sp = sin(pitch / 2)
    cy = cos(yaw / 2); sy = sin(yaw / 2)

    if order in ["XYZ", "ZYX"]:
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
    else:
        return 0, 0, 0, 1

    return x, y, z, w


def quat_to_euler(x, y, z, w):
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = max(min(t2, +1.0), -1.0)
    pitch = asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = atan2(t3, t4)

    return roll, pitch, yaw


# =========================
# 可视化坐标系
# =========================
def draw_axes(ax, R=np.eye(3)):
    scale = 1.0
    origin = np.array([0, 0, 0])

    X = R @ np.array([scale, 0, 0])
    Y = R @ np.array([0, scale, 0])
    Z = R @ np.array([0, 0, scale])

    ax.quiver(*origin, *X, color="red")
    ax.quiver(*origin, *Y, color="green")
    ax.quiver(*origin, *Z, color="blue")

    ax.text(*X, "X", color="red")
    ax.text(*Y, "Y", color="green")
    ax.text(*Z, "Z", color="blue")

    ax.view_init(elev=20, azim=170)


# =========================
# GUI 应用
# =========================
class VizApp:
    def __init__(self, root):
        self.root = root
        root.title("欧拉角 ↔ 四元数 可视化工具")

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=10, pady=10)

        right = ttk.Frame(main)
        right.pack(side="right", fill="both", expand=True)

        # ---------- 单位选择 ----------
        ttk.Label(left, text="角度单位").pack()
        self.unit = tk.StringVar(value="角度")

        ttk.Combobox(
            left,
            textvariable=self.unit,
            values=["角度", "弧度"],
            state="readonly"
        ).pack(pady=3)

        # ---------- 欧拉角 ----------
        ttk.Label(left, text="欧拉角 (Roll / Pitch / Yaw)").pack(pady=3)

        self.roll = tk.DoubleVar(value=0)
        self.pitch = tk.DoubleVar(value=0)
        self.yaw = tk.DoubleVar(value=0)

        ttk.Label(left, text="Roll (X)").pack()
        ttk.Entry(left, textvariable=self.roll).pack()

        ttk.Label(left, text="Pitch (Y)").pack()
        ttk.Entry(left, textvariable=self.pitch).pack()

        ttk.Label(left, text="Yaw (Z)").pack()
        ttk.Entry(left, textvariable=self.yaw).pack()

        # ---------- 旋转顺序 ----------
        ttk.Label(left, text="旋转顺序").pack(pady=5)
        self.order = tk.StringVar(value="XYZ")

        ttk.Combobox(
            left,
            textvariable=self.order,
            values=["XYZ", "ZYX", "YXZ", "ZXY"],
            state="readonly"
        ).pack()

        ttk.Button(left, text="欧拉角 → 四元数", command=self.update_from_euler).pack(pady=5)

        # ---------- 四元数 ----------
        ttk.Label(left, text="四元数 (x, y, z, w)").pack(pady=3)

        self.qx = tk.DoubleVar(value=0)
        self.qy = tk.DoubleVar(value=0)
        self.qz = tk.DoubleVar(value=0)
        self.qw = tk.DoubleVar(value=1)

        for name, var in zip("xyzw", (self.qx, self.qy, self.qz, self.qw)):
            ttk.Label(left, text=f"{name.upper()}").pack()
            ttk.Entry(left, textvariable=var).pack()

        ttk.Button(left, text="四元数 → 欧拉角", command=self.update_from_quat).pack(pady=5)

        # ---------- matplotlib 3D 视图 ----------
        fig = Figure(figsize=(5, 5))
        self.ax = fig.add_subplot(111, projection="3d")
        self.ax.set_box_aspect([1, 1, 1])
        self.ax.view_init(elev=20, azim=120)

        self.canvas = FigureCanvasTkAgg(fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_axes()

    # ========== 工具函数：根据单位转弧度 ==========
    def val_to_rad(self, v):
        return np.deg2rad(v) if self.unit.get() == "角度" else v

    def rad_to_val(self, v):
        return np.rad2deg(v) if self.unit.get() == "角度" else v

    # ======== 欧拉角输入 ========
    def update_from_euler(self):
        r = self.val_to_rad(self.roll.get())
        p = self.val_to_rad(self.pitch.get())
        y = self.val_to_rad(self.yaw.get())

        x, y_, z, w = euler_to_quat(r, p, y, self.order.get())

        self.qx.set(round(x, 6))
        self.qy.set(round(y_, 6))
        self.qz.set(round(z, 6))
        self.qw.set(round(w, 6))

        self.update_axes()

    # ======== 四元数输入 ========
    def update_from_quat(self):
        r, p, y = quat_to_euler(
            self.qx.get(), self.qy.get(), self.qz.get(), self.qw.get()
        )

        self.roll.set(round(self.rad_to_val(r), 6))
        self.pitch.set(round(self.rad_to_val(p), 6))
        self.yaw.set(round(self.rad_to_val(y), 6))

        self.update_axes()

    # ======== 刷新 3D 坐标轴 ========
    def update_axes(self):
        self.ax.clear()

        r = self.val_to_rad(self.roll.get())
        p = self.val_to_rad(self.pitch.get())
        y = self.val_to_rad(self.yaw.get())

        Rx = np.array([[1, 0, 0],
                       [0, cos(r), -sin(r)],
                       [0, sin(r), cos(r)]])

        Ry = np.array([[cos(p), 0, sin(p)],
                       [0, 1, 0],
                       [-sin(p), 0, cos(p)]])

        Rz = np.array([[cos(y), -sin(y), 0],
                       [sin(y), cos(y), 0],
                       [0, 0, 1]])

        order = self.order.get()
        R = np.eye(3)

        for axis in order:
            if axis == "X":
                R = R @ Rx
            elif axis == "Y":
                R = R @ Ry
            elif axis == "Z":
                R = R @ Rz

        draw_axes(self.ax, R)

        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_zlim([-1, 1])

        self.ax.set_title("旋转坐标系 (红=X  绿=Y  蓝=Z)", fontproperties="SimHei")

        self.canvas.draw()

def center_window(win):
    win.update_idletasks()   # 先更新布局，才能获取正确宽高

    w = win.winfo_width()
    h = win.winfo_height()

    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()

    x = (sw - w) // 2
    y = (sh - h) // 2

    win.geometry(f"{w}x{h}+{x}+{y}")

# ============= 启动程序 =============
if __name__ == "__main__":
    root = tk.Tk()
    VizApp(root)
    center_window(root)
    root.mainloop()
