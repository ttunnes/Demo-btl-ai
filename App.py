#Author: Bui Tran Thanh Tung with Ai
import customtkinter as ctk
import tkinter as tk
import math

# --- CẤU HÌNH GIAO DIỆN DARK MODE ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- DỮ LIỆU BẢN ĐỒ ---
nodes = {
    "Trạm Xe Buýt": (120, 250),
    "Cổng Chính": (240, 250),
    "Bãi Xe Bắc": (320, 160),
    "Bãi Xe Nam": (320, 340),
    "Siêu Thị": (460, 100),
    "Tòa A": (460, 200),
    "Tòa B": (460, 300),
    "Phòng Y Tế": (460, 400),
    "Căn Tin": (620, 150),
    "Thư Viện": (620, 250),
    "Sân Thể Thao": (620, 350),
    "Hồ Bơi": (760, 100),
    "KTX A": (760, 200),
    "KTX B": (760, 300),
    "Cổng Phụ": (860, 250)
}

# --- KHOẢNG CÁCH GIỮA CÁC NODE ---
roads = {
    "Trạm Xe Buýt": {"Cổng Chính": 200},
    "Cổng Chính": {"Trạm Xe Buýt": 200, "Bãi Xe Bắc": 360, "Bãi Xe Nam": 360, "Tòa A": 420, "Tòa B": 420},
    "Bãi Xe Bắc": {"Cổng Chính": 360, "Siêu Thị": 280, "Tòa A": 340},
    "Bãi Xe Nam": {"Cổng Chính": 360, "Tòa B": 340, "Phòng Y Tế": 280},
    "Siêu Thị": {"Bãi Xe Bắc": 280, "Căn Tin": 340},
    "Tòa A": {"Cổng Chính": 420, "Bãi Xe Bắc": 340, "Thư Viện": 340},
    "Tòa B": {"Cổng Chính": 420, "Bãi Xe Nam": 340, "Thư Viện": 340},
    "Phòng Y Tế": {"Bãi Xe Nam": 280, "Sân Thể Thao": 320},
    "Căn Tin": {"Siêu Thị": 340, "Hồ Bơi": 320, "KTX A": 360},
    "Thư Viện": {"Tòa A": 340, "Tòa B": 340, "KTX A": 320, "KTX B": 320},
    "Sân Thể Thao": {"Phòng Y Tế": 320, "KTX B": 360},
    "Hồ Bơi": {"Căn Tin": 320, "Cổng Phụ": 460},
    "KTX A": {"Căn Tin": 360, "Thư Viện": 320, "Cổng Phụ": 260},
    "KTX B": {"Thư Viện": 320, "Sân Thể Thao": 320, "Cổng Phụ": 260},
    "Cổng Phụ": {"Hồ Bơi": 460, "KTX A": 260, "KTX B": 260}
}

# --- LÕI THUẬT TOÁN A* ---
def heuristic(node1, node2):
    x1, y1 = nodes[node1]
    x2, y2 = nodes[node2]
    # Khoảng cách heuristic chính là khoảnh cách giữa 2 picxel: 
    return math.hypot(x1 - x2, y1 - y2)

def astar_generator(start, end):
    open_set = [start]
    came_from = {}
    g_score = {loc: float("inf") for loc in nodes}
    g_score[start] = 0
    f_score = {loc: float("inf") for loc in nodes}
    f_score[start] = heuristic(start, end)
    
    closed_set = set()

    while open_set:
        current = min(open_set, key=lambda loc: f_score[loc])

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            yield {"status": "success", "path": path, "dist": g_score[end]}
            return

        open_set.remove(current)
        closed_set.add(current)

        yield {"status": "running", "current": current, "open": open_set, "closed": closed_set}

        for neighbor, weight in roads[current].items():
            temp_g_score = g_score[current] + weight
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)
                if neighbor not in open_set:
                    open_set.append(neighbor)

    yield {"status": "failed"}

# --- GIAO DIỆN CHÍNH ---
class ModernAStarUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nhóm 4")
        self.geometry("900x600")
        self.configure(fg_color="#18181b")

        self.animation_generator = None
        self.is_running = False

        self.setup_ui()
        self.draw_graph()

    def setup_ui(self):
        # 1. HEADER
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=35, pady=(25, 10))

        ctk.CTkLabel(header_frame, text="Bản đồ:", font=("Arial", 20, "bold"), text_color="white").pack(side="left")

        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right")
        self.lbl_dist_title = ctk.CTkLabel(stats_frame, text="TỔNG QUÃNG ĐƯỜNG\n---", font=("Arial", 12, "bold"), text_color="#a1a1aa", justify="right")
        self.lbl_dist_title.pack(side="right", padx=5)

        # 2. CANVAS
        canvas_container = ctk.CTkFrame(self, fg_color="#1e1e24", corner_radius=15)
        canvas_container.pack(fill="both", expand=True, padx=35, pady=10)
        
        self.canvas = tk.Canvas(canvas_container, bg="#1e1e24", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # 3. CONTROL PANEL
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", padx=35, pady=(10, 25))

        # Dòng 1: 2 Dropdown chia đều 2 bên
        row1 = ctk.CTkFrame(control_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 15))
        
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        # Cụm Trái (Điểm Xuất Phát)
        left_combo_frame = ctk.CTkFrame(row1, fg_color="transparent")
        left_combo_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(left_combo_frame, text="Điểm Xuất Phát", text_color="white", font=("Arial", 13)).pack(side="left", padx=(0, 15))
        self.cbo_start = ctk.CTkComboBox(left_combo_frame, values=list(nodes.keys()), fg_color="#18181b", border_color="#52525b")
        self.cbo_start.set("Trạm Xe Buýt")
        self.cbo_start.pack(side="left", fill="x", expand=True)

        # Cụm Phải (Điểm Đích)
        right_combo_frame = ctk.CTkFrame(row1, fg_color="transparent")
        right_combo_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(right_combo_frame, text="Điểm Đích", text_color="white", font=("Arial", 13)).pack(side="left", padx=(0, 15))
        self.cbo_end = ctk.CTkComboBox(right_combo_frame, values=list(nodes.keys()), fg_color="#18181b", border_color="#52525b")
        self.cbo_end.set("Hồ Bơi")
        self.cbo_end.pack(side="left", fill="x", expand=True)

        # Dòng 2: 2 Nút bấm chia đều 2 bên
        row2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        row2.pack(fill="x")
        
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        self.btn_start = ctk.CTkButton(row2, text="Tìm đường", command=self.start_algorithm, fg_color="#2f3342", hover_color="#3f4455", height=40, font=("Arial", 14))
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.btn_reset = ctk.CTkButton(row2, text="Làm mới", command=self.reset_ui, fg_color="#2f3342", hover_color="#3f4455", height=40, font=("Arial", 14))
        self.btn_reset.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def create_rounded_pill(self, x, y, text):
        padding_x = 12
        padding_y = 6
        text_id = self.canvas.create_text(x, y, text=text, fill="white", font=("Arial", 9, "bold"))
        bbox = self.canvas.bbox(text_id)
        
        x1, y1, x2, y2 = bbox[0]-padding_x, bbox[1]-padding_y, bbox[2]+padding_x, bbox[3]+padding_y
        r = (y2 - y1) / 2
        
        self.canvas.delete(text_id)
        
        # Vẽ background màu đen xám, viền xám sáng giống hình
        self.canvas.create_polygon(
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1,
            smooth=True, fill="#18181b", outline="#a1a1aa", width=1.2
        )
        self.canvas.create_text(x, y, text=text, fill="white", font=("Arial", 9, "bold"))

    def draw_graph(self, path=[]):
        self.canvas.delete("all")

        # 1. Vẽ các cạnh (Đường nối)
        for u in roads:
            for v in roads[u]:
                x1, y1 = nodes[u]
                x2, y2 = nodes[v]
                
                line_color = "#3f3f46" # Xám tối
                line_width = 2
                
                # Highlight đường đi bằng màu Xanh Ngọc
                if path and ((u in path and v in path and abs(path.index(u) - path.index(v)) == 1)):
                    line_color = "#86efac" # Xanh ngọc (Light Green)
                    line_width = 4

                self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)

                # Vẽ trọng số
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                self.canvas.create_rectangle(mx-12, my-8, mx+12, my+8, fill="#1e1e24", outline="")
                self.canvas.create_text(mx, my, text=str(roads[u][v]), fill="#a1a1aa", font=("Arial", 10))

        # 2. Vẽ các Node
        for loc, (x, y) in nodes.items():
            fill_color = "#3f3f46" # Trạng thái mặc định: Xám
            
            # Tô màu theo hình ảnh thiết kế
            if path:
                if loc == path[0]:
                    fill_color = "#a5b4fc" # Điểm bắt đầu: Xanh lam nhạt
                elif loc == path[-1]:
                    fill_color = "#fecaca" # Điểm đích: Hồng nhạt
                elif loc in path:
                    fill_color = "#86efac" # Các điểm trung gian: Xanh ngọc

            # Vẽ điểm tròn (Node)
            r = 12
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline="#52525b", width=1)
            
            # Vẽ Label (Viên thuốc) đè nhẹ lên node
            self.create_rounded_pill(x, y+15, loc)

    def update_stats(self, dist="---"):
        # Hiển thị số to, chữ "đơn vị" nhỏ lại
        self.lbl_dist_title.configure(text=f"TỔNG QUÃNG ĐƯỜNG\n{dist} mét")

    def start_algorithm(self):
        if self.is_running: return
        
        start_node = self.cbo_start.get()
        end_node = self.cbo_end.get()
        if start_node == end_node: return

        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.cbo_start.configure(state="disabled")
        self.cbo_end.configure(state="disabled")

        self.animation_generator = astar_generator(start_node, end_node)
        self.animate_step()

    def animate_step(self):
        try:
            state = next(self.animation_generator)
            
            if state["status"] == "running":
                # Tốc độ hoạt ảnh nhanh (50ms) vì đã bỏ thanh trượt
                self.after(50, self.animate_step)

            elif state["status"] == "success":
                self.draw_graph(path=state["path"])
                self.update_stats(dist=str(state["dist"]))
                self.is_running = False
                self.btn_start.configure(state="normal")

            elif state["status"] == "failed":
                self.update_stats(dist="Không có đường")
                self.is_running = False
                self.btn_start.configure(state="normal")

        except StopIteration:
            self.is_running = False
            self.btn_start.configure(state="normal")

    def reset_ui(self):
        self.is_running = False
        self.animation_generator = None
        self.cbo_start.configure(state="normal")
        self.cbo_end.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.update_stats()
        self.draw_graph()

if __name__ == "__main__":
    app = ModernAStarUI()
    app.mainloop()