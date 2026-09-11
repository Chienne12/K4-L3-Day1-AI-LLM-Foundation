"""Giao diện chat tối giản, chỉ sử dụng run_assistant từ template.py."""

from contextlib import redirect_stdout
from queue import Queue
import threading
import tkinter as tk

import template


BACKGROUND = "#EFECFF"
PANEL = "#FFFFFF"
CARD = "#F8F7FF"
INPUT = "#FFFFFF"
BORDER = "#E7E4F5"
ASSISTANT_BUBBLE = "#F1F2F6"
USER_BUBBLE = "#E5D9FF"
TEXT = "#29283D"
MUTED = "#9294A8"
ACCENT = "#7357F6"
ACCENT_HOVER = "#6347ED"
SOFT_ACCENT = "#EEE9FF"
SUCCESS = "#2FC48D"

PERSONA = (
    "Bạn là trợ lý thân thiện. Hãy trả lời rõ ràng, ngắn gọn bằng tiếng Việt."
)


class BubbleWriter:
    """Chuyển nội dung được run_assistant in ra sang bong bóng trong UI."""

    def __init__(self, ui: "ChatUI") -> None:
        self.ui = ui

    def write(self, content: str) -> int:
        if content == "\n":
            self.ui.root.after(0, self.ui._finish_response)
        elif content:
            self.ui.root.after(0, self.ui._append_response, content)
        return len(content)

    def flush(self) -> None:
        pass


class ChatUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.busy = False
        self.input_queue: Queue[str] = Queue()
        self.active_bubble: tk.Label | None = None
        self.current_user_message = ""
        self.reply = ""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.models = list(
            dict.fromkeys([template.OPENAI_MODEL, template.OPENAI_MINI_MODEL])
        )
        self.selected_model = self.models[0]

        root.title("AI Chat")
        root.geometry("660x800")
        root.minsize(480, 620)
        root.configure(bg=BACKGROUND)
        self._center_window(660, 800)

        self.panel = tk.Frame(
            root,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
        )
        self.panel.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(self.panel, bg=PANEL)
        header.pack(side="top", fill="x", padx=24, pady=(18, 12))

        logo = tk.Canvas(
            header,
            width=42,
            height=42,
            bg=PANEL,
            highlightthickness=0,
        )
        logo.create_oval(2, 2, 40, 40, fill=SOFT_ACCENT, outline="")
        logo.create_text(
            21,
            21,
            text="AI",
            fill=ACCENT,
            font=("Segoe UI Semibold", 11),
        )
        logo.pack(side="left")

        identity = tk.Frame(header, bg=PANEL)
        identity.pack(side="left", padx=(12, 0))
        tk.Label(
            identity,
            text="Trợ lý AI",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI Semibold", 14),
        ).pack(anchor="w")
        status_row = tk.Frame(identity, bg=PANEL)
        status_row.pack(anchor="w", pady=(2, 0))
        self.status_dot = tk.Label(
            status_row,
            text="●",
            bg=PANEL,
            fg=SUCCESS,
            font=("Segoe UI", 7),
        )
        self.status_dot.pack(side="left")
        self.status_label = tk.Label(
            status_row,
            text="Sẵn sàng",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side="left", padx=(5, 0))

        self.model_button = tk.Button(
            header,
            text=self.selected_model,
            command=self._toggle_model,
            bg=CARD,
            fg=TEXT,
            activebackground=SOFT_ACCENT,
            activeforeground=ACCENT,
            disabledforeground=MUTED,
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            font=("Segoe UI Semibold", 9),
            cursor="hand2",
        )
        self.model_button.pack(side="right")
        self.model_button.bind(
            "<Enter>", lambda _event: self._button_hover(self.model_button, True)
        )
        self.model_button.bind(
            "<Leave>", lambda _event: self._button_hover(self.model_button, False)
        )

        stats = tk.Frame(
            self.panel,
            bg=CARD,
            padx=10,
            pady=10,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        stats.pack(side="top", fill="x", padx=24, pady=(0, 10))
        for column in range(3):
            stats.grid_columnconfigure(column, weight=1)

        self.input_stat = self._create_stat(stats, "INPUT", 0, 0)
        self.output_stat = self._create_stat(stats, "OUTPUT", 0, 1)
        self.cost_stat = self._create_stat(stats, "CHI PHÍ", "$0.000000", 2)

        self.canvas = tk.Canvas(
            self.panel,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = tk.Scrollbar(
            self.panel,
            command=self.canvas.yview,
            bg="#DED9F4",
            troughcolor=PANEL,
            activebackground=ACCENT,
            highlightthickness=0,
            bd=0,
            width=7,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y", pady=6)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.messages = tk.Frame(self.canvas, bg=PANEL)
        self.messages.grid_columnconfigure(0, weight=1)
        self.messages_window = self.canvas.create_window(
            (0, 0), window=self.messages, anchor="nw"
        )
        self.messages.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_messages)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        composer = tk.Frame(
            self.panel,
            bg=INPUT,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
        )
        composer.pack(side="bottom", fill="x", padx=24, pady=(12, 20))

        self.input_box = tk.Text(
            composer,
            height=2,
            wrap="word",
            bg=INPUT,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=ACCENT,
            relief="flat",
            bd=0,
            padx=16,
            pady=14,
            font=("Segoe UI", 11),
        )
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<FocusIn>", self._remove_placeholder)
        self.input_box.bind("<FocusOut>", self._restore_placeholder)

        self.send_button = tk.Button(
            composer,
            text="↑",
            command=self.send,
            bg=ACCENT,
            fg="white",
            activebackground="#60a5fa",
            activeforeground="white",
            disabledforeground=MUTED,
            relief="flat",
            bd=0,
            padx=15,
            pady=6,
            font=("Segoe UI Semibold", 18),
            cursor="hand2",
        )
        self.send_button.pack(side="right", fill="y", padx=7, pady=7)
        self.input_box.pack(side="left", fill="both", expand=True)
        self.send_button.bind(
            "<Enter>", lambda _event: self._button_hover(self.send_button, True)
        )
        self.send_button.bind(
            "<Leave>", lambda _event: self._button_hover(self.send_button, False)
        )
        self.placeholder_active = False
        self._restore_placeholder()
        self.input_box.focus_set()

        self.root.protocol("WM_DELETE_WINDOW", self._close)
        threading.Thread(target=self._assistant_loop, daemon=True).start()

    def _center_window(self, width: int, height: int) -> None:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_stat(
        self,
        parent: tk.Frame,
        title: str,
        value: object,
        column: int,
    ) -> tk.Label:
        cell = tk.Frame(parent, bg=CARD)
        cell.grid(row=0, column=column, sticky="ew")
        tk.Label(
            cell,
            text=title,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI Semibold", 8),
        ).pack()
        value_label = tk.Label(
            cell,
            text=str(value),
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI Semibold", 12),
        )
        value_label.pack(pady=(4, 0))
        return value_label

    def _button_hover(self, button: tk.Button, hovering: bool) -> None:
        if str(button["state"]) == "disabled":
            return
        if button is self.send_button:
            button.configure(bg=ACCENT_HOVER if hovering else ACCENT)
        else:
            button.configure(
                bg=SOFT_ACCENT if hovering else CARD,
                fg=ACCENT if hovering else TEXT,
            )

    def _remove_placeholder(self, _event=None) -> None:
        if not self.placeholder_active:
            return
        self.input_box.delete("1.0", "end")
        self.input_box.configure(fg=TEXT)
        self.placeholder_active = False

    def _restore_placeholder(self, _event=None) -> None:
        if self.input_box.get("1.0", "end").strip():
            return
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", "Nhập tin nhắn...")
        self.input_box.configure(fg=MUTED)
        self.placeholder_active = True

    def _update_scroll_region(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_messages(self, event) -> None:
        self.canvas.itemconfigure(self.messages_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_enter(self, event):
        if event.state & 0x0001:
            return None
        self.send()
        return "break"

    def _toggle_model(self) -> None:
        if len(self.models) < 2:
            return
        current_index = self.models.index(self.selected_model)
        self.selected_model = self.models[(current_index + 1) % len(self.models)]
        template.OPENAI_MODEL = self.selected_model
        self.model_button.configure(text=self.selected_model)

    def _create_avatar(self, parent: tk.Frame, role: str) -> tk.Canvas:
        is_user = role == "user"
        avatar = tk.Canvas(
            parent,
            width=34,
            height=34,
            bg=PANEL,
            highlightthickness=0,
        )
        avatar.create_oval(
            1,
            1,
            33,
            33,
            fill=SOFT_ACCENT if is_user else "#E9E5FF",
            outline="",
        )
        avatar.create_text(
            17,
            17,
            text="U" if is_user else "AI",
            fill=ACCENT,
            font=("Segoe UI Semibold", 9 if is_user else 8),
        )
        return avatar

    def _add_message(self, content: str, role: str) -> tk.Label:
        row = tk.Frame(self.messages, bg=PANEL)
        row.grid(
            row=self.messages.grid_size()[1],
            column=0,
            sticky="ew",
            padx=22,
            pady=7,
        )

        is_user = role == "user"
        avatar = self._create_avatar(row, role)
        avatar.pack(
            side="right" if is_user else "left",
            padx=(9, 0) if is_user else (0, 9),
            anchor="s",
        )
        bubble_frame = tk.Frame(
            row,
            bg=USER_BUBBLE if is_user else ASSISTANT_BUBBLE,
            highlightbackground="#DCCBFF" if is_user else BORDER,
            highlightthickness=1,
            bd=0,
        )
        bubble_frame.pack(side="right" if is_user else "left")
        bubble = tk.Label(
            bubble_frame,
            text=content,
            bg=USER_BUBBLE if is_user else ASSISTANT_BUBBLE,
            fg=TEXT,
            justify="left",
            anchor="w",
            wraplength=400,
            padx=16,
            pady=12,
            font=("Segoe UI", 11),
        )
        bubble.pack()
        self._scroll_to_bottom()
        return bubble

    def _scroll_to_bottom(self) -> None:
        self.root.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def _set_busy(self, value: bool) -> None:
        self.busy = value
        state = "disabled" if value else "normal"
        self.send_button.configure(state=state)
        self.model_button.configure(state=state)
        self.input_box.configure(state=state)
        self.status_dot.configure(fg=ACCENT if value else SUCCESS)
        self.status_label.configure(text="Đang trả lời" if value else "Sẵn sàng")
        if not value:
            self._restore_placeholder()
            self.input_box.focus_set()

    def send(self) -> None:
        if self.busy:
            return

        if self.placeholder_active:
            return
        user_message = self.input_box.get("1.0", "end").strip()
        if not user_message:
            return

        self.input_box.delete("1.0", "end")
        self._add_message(user_message, "user")
        self.active_bubble = self._add_message("•••", "assistant")
        self.current_user_message = user_message
        self.reply = ""
        self._set_busy(True)
        template.OPENAI_MODEL = self.selected_model
        self.input_queue.put(user_message)

    def _assistant_loop(self) -> None:
        try:
            with redirect_stdout(BubbleWriter(self)):
                template.run_assistant(
                    persona=PERSONA,
                    get_input=self.input_queue.get,
                )
        except Exception:
            self.root.after(0, self._show_error)

    def _append_response(self, content: str) -> None:
        if self.active_bubble is None:
            return
        self.reply += content
        self._update_bubble(self.active_bubble, self.reply)

    def _finish_response(self) -> None:
        if self.active_bubble is None:
            return
        if not self.reply:
            self._update_bubble(
                self.active_bubble,
                "Không nhận được phản hồi.",
            )
        else:
            self._update_stats()
        self.active_bubble = None
        self._set_busy(False)

    def _update_stats(self) -> None:
        usage = template.estimate_cost(
            self.current_user_message,
            self.reply,
            model=self.selected_model,
        )
        self.total_input_tokens += usage["input_tokens"]
        self.total_output_tokens += usage["output_tokens"]
        self.total_cost += usage["total_cost"]

        self.input_stat.configure(text=str(self.total_input_tokens))
        self.output_stat.configure(text=str(self.total_output_tokens))
        self.cost_stat.configure(text=f"${self.total_cost:.6f}")

    def _show_error(self) -> None:
        if self.active_bubble is not None:
            self._update_bubble(
                self.active_bubble,
                "Không thể kết nối. Vui lòng thử lại.",
            )
        self.active_bubble = None
        self._set_busy(False)

    def _update_bubble(self, bubble: tk.Label, content: str) -> None:
        bubble.configure(text=content)
        self._scroll_to_bottom()

    def _close(self) -> None:
        self.input_queue.put("exit")
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    ChatUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
