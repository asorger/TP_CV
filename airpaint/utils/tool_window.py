import cv2
import os
import time
import numpy as np


class ToolWindow:
    def __init__(self, base_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if base_path is None:
            self.base_path = os.path.abspath(os.path.join(base_dir, "..", "assets"))
        else:
            self.base_path = os.path.abspath(base_path)

        self.animations = {}
        self.index = {}
        self.last_time = {}
        self.delay = 0.08

        self.window_w = 300
        self.window_h = 300

        self._load()

    def _load_frames(self, folder):
        frames = []

        if not os.path.exists(folder):
            print(f"[ToolWindow] Pasta não encontrada: {folder}")
            return frames

        for f in sorted(os.listdir(folder)):
            path = os.path.join(folder, f)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                frames.append(img)

        print(f"[ToolWindow] {folder}: {len(frames)} frames")
        return frames

    def _load(self):
        self.animations["brush"] = self._load_frames(os.path.join(self.base_path, "pencil"))
        self.animations["eraser"] = self._load_frames(os.path.join(self.base_path, "rubber"))
        self.animations["spray"] = self._load_frames(os.path.join(self.base_path, "can"))

        for k in self.animations:
            self.index[k] = 0
            self.last_time[k] = time.time()

    def get_frame(self, tool):
        canvas = np.zeros((self.window_h, self.window_w, 3), dtype=np.uint8)

        if tool not in self.animations or not self.animations[tool]:
            cv2.putText(
                canvas,
                "NO TOOL",
                (60, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )
            return canvas

        now = time.time()
        if now - self.last_time[tool] >= self.delay:
            self.index[tool] = (self.index[tool] + 1) % len(self.animations[tool])
            self.last_time[tool] = now

        frame = self.animations[tool][self.index[tool]]

        h, w = frame.shape[:2]
        scale = min(self.window_w / w, self.window_h / h) * 0.85
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)))

        y = (self.window_h - frame.shape[0]) // 2
        x = (self.window_w - frame.shape[1]) // 2

        if frame.shape[2] == 4:
            alpha = frame[:, :, 3] / 255.0
            for c in range(3):
                canvas[y:y+frame.shape[0], x:x+frame.shape[1], c] = (
                    canvas[y:y+frame.shape[0], x:x+frame.shape[1], c] * (1 - alpha)
                    + frame[:, :, c] * alpha
                )
        else:
            canvas[y:y+frame.shape[0], x:x+frame.shape[1]] = frame

        return canvas