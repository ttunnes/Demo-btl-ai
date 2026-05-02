#Author: Bui Tran Thanh Tung with Ai
import customtkinter as ctk
import tkinter as tk
import math

# --- CẤU HÌNH GIAO DIỆN  ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- DỮ LIỆU ĐỒ THỊ ---
nodes = {
    "Cổng Chính"   : (50, 350),     # ĐIỂM ĐẦU
    "Đường Hoa"    : (140, 150),      
    "Quảng Trường" : (170, 500),    
    "Vườn Lan"     : (400, 150),
    "Rừng Thông"   : (400, 50),
    "Bờ Hồ Trái"   : (400, 450),
    "Cà Phê Ven Hồ": (350, 600),
    "Đồi Cỏ"       : (600, 150),
    "Tháp Đồng Hồ" : (550, 400),
    "Đường Ven Hồ" : (550, 600),
    "Đu Quay"      : (800, 200),
    "Đảo Chim"     : (750, 400),     
    "Bờ Hồ Phải"   : (700, 550),
    "Vườn Hoa"     : (850, 600),
    "Cầu Gỗ"       : (900, 250),
    "Khu Trò Chơi" : (900, 450),    
    "Tượng Đài"    : (260, 250),
    "Thác Nước"    : (440, 270),
    "Khu Ẩm Thực"  : (1000, 350),    # ĐÍCH ĐẾN
}

# Các liên kết (Edges)
connections = [
    ("Cổng Chính", "Đường Hoa"), ("Cổng Chính", "Quảng Trường"), ("Cổng Chính", "Tượng Đài"),
    ("Đường Hoa", "Vườn Lan"), ("Đường Hoa", "Rừng Thông"), ("Đường Hoa", "Tượng Đài"),
    ("Tượng Đài", "Thác Nước"), ("Tượng Đài", "Vườn Lan"), ("Thác Nước", 'Đồi Cỏ'), ("Thác Nước", "Tháp Đồng Hồ"),
    ("Quảng Trường", "Bờ Hồ Trái"), ("Quảng Trường", "Cà Phê Ven Hồ"), ("Quảng Trường", "Tượng Đài"),
    ("Vườn Lan", "Đồi Cỏ"), ("Rừng Thông", "Đồi Cỏ"),
    ("Bờ Hồ Trái", "Tháp Đồng Hồ"), ("Cà Phê Ven Hồ", "Đường Ven Hồ"),
    ("Đồi Cỏ", "Đu Quay"), ("Tháp Đồng Hồ", "Đảo Chim"),
    ("Tháp Đồng Hồ", "Bờ Hồ Phải"), ("Đường Ven Hồ", "Bờ Hồ Phải"),
    ("Đu Quay", "Cầu Gỗ"), 
    ("Đảo Chim", "Bờ Hồ Phải"), ("Đảo Chim", 'Đu Quay'),   
    ("Bờ Hồ Phải", "Khu Trò Chơi"), ("Bờ Hồ Phải", "Vườn Hoa"),
    ("Vườn Hoa", "Khu Trò Chơi"),
    ("Cầu Gỗ", "Khu Ẩm Thực"), ("Khu Trò Chơi", "Khu Ẩm Thực"), ("Cầu Gỗ", "Khu Trò Chơi")
]

# Tự động tính trọng số thực tế (Khoảng cách Euclidean)
roads = {node: {} for node in nodes}
for u, v in connections:
    x1, y1 = nodes[u]
    x2, y2 = nodes[v]
    dist = int(math.hypot(x1 - x2, y1 - y2))
    roads[u][v] = dist
    roads[v][u] = dist

# --- LÕI THUẬT TOÁN ---
def heuristic(node1, node2):
    x1, y1 = nodes[node1]
    x2, y2 = nodes[node2]
    return int(math.hypot(x1 - x2, y1 - y2))

def search_generator(start, end, algorithm="A*"):
    open_set = [start]
    came_from = {}
    g_score = {loc: float("inf") for loc in nodes}
    g_score[start] = 0
    closed_set = set()

    def get_priority(node):
        if algorithm == "A*":
            return g_score[node] + heuristic(node, end)
        else: # Greedy
            return heuristic(node, end)

    while open_set:
        current = min(open_set, key=lambda loc: get_priority(loc))

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
                if neighbor not in open_set:
                    open_set.append(neighbor)

    yield {"status": "failed"}

# --- GIAO DIỆN CHÍNH ---
class SmartWayUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tìm 2 khoảng cách ngắn nhất giữa 2 điểm trên bản đồ")
        self.geometry("1200x600")
        self.configure(fg_color="#0f172a") 

        # Zoom & Pan
        self.scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_data = {"x": 0, "y": 0}

        # Trạng thái
        self.animation_generator = None
        self.is_running = False
        self.current_path = []
        self.current_eval = None
        self.open_nodes = set()
        self.closed_nodes = set()

        self.setup_ui()
        self.draw_graph()

    def setup_ui(self):
        # --- SIDEBAR ---
        sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#1e293b")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False) 

        # Khung chứa các nút điều khiển 
        # (Điều chỉnh pady=(25, 5) để nó cách mép trên cửa sổ một khoảng vừa đẹp)
        control_frame = ctk.CTkFrame(sidebar, fg_color="#0f172a", corner_radius=10)
        control_frame.pack(fill="x", padx=15, pady=(25, 5))
        box_height = 28 

        # 1. Dòng chọn Thuật toán
        ctk.CTkLabel(control_frame, text="Thuật toán:", text_color="#cbd5e1", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(12, 2))
        self.cbo_algo = ctk.CTkComboBox(control_frame, values=["A* sreach", "Greedy search"], fg_color="#1e293b", border_color="#334155", height=box_height)
        self.cbo_algo.set("A* search")
        self.cbo_algo.pack(fill="x", padx=20, pady=(0, 10))

        # 2. Dòng chọn Xuất phát
        ctk.CTkLabel(control_frame, text="Điểm xuất phát", text_color="#cbd5e1", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(0, 2))
        self.cbo_start = ctk.CTkComboBox(control_frame, values=list(nodes.keys()), fg_color="#1e293b", border_color="#334155", height=box_height)
        self.cbo_start.set("Cổng Chính")
        self.cbo_start.pack(fill="x", padx=20, pady=(0, 10))

        # 3. Dòng chọn Đích đến
        ctk.CTkLabel(control_frame, text="Điểm đến", text_color="#cbd5e1", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(0, 2))
        self.cbo_end = ctk.CTkComboBox(control_frame, values=list(nodes.keys()), fg_color="#1e293b", border_color="#334155", height=box_height)
        self.cbo_end.set("Khu Ẩm Thực")
        self.cbo_end.pack(fill="x", padx=20, pady=(0, 15))

        # Khung chứa 2 Nút bấm 
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.btn_start = ctk.CTkButton(btn_frame, text="Tìm đường", command=self.start_algorithm, fg_color="#2563eb", hover_color="#1d4ed8", height=32)
        self.btn_start.pack(side="left", expand=True, padx=(0, 4))
        self.btn_reset = ctk.CTkButton(btn_frame, text="Làm mới", command=self.reset_ui, fg_color="#475569", hover_color="#334155", height=32)
        self.btn_reset.pack(side="right", expand=True, padx=(4, 0))

        # --- LỘ TRÌNH  ---
        route_frame = ctk.CTkFrame(sidebar, fg_color="#0f172a", corner_radius=10)
        route_frame.pack(fill="both", expand=True, padx=15, pady=(10, 20))
        
        ctk.CTkLabel(route_frame, text="Lộ trình:", font=("Arial", 15, "bold"), text_color="white").pack(anchor="w", padx=15, pady=(15, 5))
        self.lbl_total_dist = ctk.CTkLabel(route_frame, text="Tổng chiều dài: --", font=("Arial", 12), text_color="#94a3b8")
        self.lbl_total_dist.pack(anchor="w", padx=15)

        self.txt_route = ctk.CTkTextbox(route_frame, fg_color="transparent", text_color="#e2e8f0", font=("Arial", 13), wrap="word")
        self.txt_route.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_route.insert("1.0", "Chưa có lộ trình.")
        self.txt_route.configure(state="disabled")

        # --- CANVAS  ---
        canvas_container = ctk.CTkFrame(self, fg_color="#0f172a")
        canvas_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_container, bg="#0f172a", highlightthickness=0, cursor="hand2")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
    # --- ZOOM & PAN LOGIC ---
    def on_pan_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_pan_move(self, event):
        self.pan_x += event.x - self.drag_data["x"]
        self.pan_y += event.y - self.drag_data["y"]
        self.drag_data["x"], self.drag_data["y"] = event.x, event.y
        self.draw_graph()

    def on_zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.pan_x = x - (x - self.pan_x) * factor
        self.pan_y = y - (y - self.pan_y) * factor
        self.scale *= factor
        self.draw_graph()

    def transform(self, x, y):
        return x * self.scale + self.pan_x, y * self.scale + self.pan_y

    # --- VẼ ĐỒ THỊ VÀ TRỌNG SỐ ---
    def draw_graph(self):
        self.canvas.delete("all")
        drawn_edges = set() # Tránh vẽ đè 2 lần do đồ thị vô hướng

        # Vẽ cạnh và khoảng cách
        for u in roads:
            for v in roads[u]:
                edge_id = tuple(sorted((u, v)))
                if edge_id in drawn_edges: continue
                drawn_edges.add(edge_id)

                x1, y1 = self.transform(nodes[u][0], nodes[u][1])
                x2, y2 = self.transform(nodes[v][0], nodes[v][1])
                
                line_color = "#334155" 
                line_width = max(2, int(2 * self.scale))
                
                if self.current_path and ((u in self.current_path and v in self.current_path and abs(self.current_path.index(u) - self.current_path.index(v)) == 1)):
                    line_color = "#f97316" # Màu Cam
                    line_width = max(4, int(4 * self.scale))

                self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)

                # Vẽ text hiển thị khoảng cách
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                self.canvas.create_rectangle(mx-15, my-9, mx+15, my+9, fill="#1e293b", outline="", tags="weight")
                self.canvas.create_text(mx, my, text=f"{roads[u][v]}", fill="#94a3b8", font=("Arial", 9, "bold"), tags="weight")

        # Vẽ Node
        for loc, (orig_x, orig_y) in nodes.items():
            x, y = self.transform(orig_x, orig_y)
            fill_color = "#0ea5e9"
            
            if self.current_path:
                if loc == self.current_path[0]: fill_color = "#22c55e"
                elif loc == self.current_path[-1]: fill_color = "#ef4444"
                elif loc in self.current_path: fill_color = "#f97316"
            elif loc == self.current_eval: fill_color = "#facc15"
            elif loc in self.closed_nodes: fill_color = "#6366f1"
            elif loc in self.open_nodes: fill_color = "#14b8a6"

            r = max(8, int(10 * self.scale))
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline="#cbd5e1", width=1)
            self.canvas.create_text(x, y - r - 12, text=loc, fill="#f8fafc", font=("Arial", 10, "bold"))

    def update_route_panel(self, path=None, dist=0):
        self.txt_route.configure(state="normal")
        self.txt_route.delete("1.0", tk.END)
        
        if not path:
            self.lbl_total_dist.configure(text="Đang tìm kiếm...")
        else:
            self.lbl_total_dist.configure(text=f"Tổng chiều dài: {dist} m • {len(path)-1} chặng")
            route_text = ""
            for i, node in enumerate(path):
                if i == 0: route_text += f"{i+1}. {node} (Xuất phát)\n\n"
                else: route_text += f"{i+1}. {node} • {roads[path[i-1]][node]} m\n\n"
            self.txt_route.insert("1.0", route_text)
            
        self.txt_route.configure(state="disabled")

    def start_algorithm(self):
        if self.is_running: return
        start_node = self.cbo_start.get()
        end_node = self.cbo_end.get()

        # --- XỬ LÝ TRƯỜNG HỢP GỐC VÀ ĐÍCH TRÙNG NHAU ---
        if start_node == end_node:
            self.current_path = [start_node]
            self.draw_graph()
            
            # Cập nhật ngay Text Lộ trình và Label Quãng đường
            self.lbl_total_dist.configure(text="Tổng chiều dài: 0 m • 0 chặng")
            self.txt_route.configure(state="normal")
            self.txt_route.delete("1.0", tk.END)
            self.txt_route.insert("1.0", f"1. {start_node} (Bạn đã ở ngay tại đích!)")
            self.txt_route.configure(state="disabled")
            return
        # -----------------------------------------------

        self.is_running = True
        self.update_route_panel(None)
        
        alg_choice = "A*" if "A*" in self.cbo_algo.get() else "Greedy"
        self.animation_generator = search_generator(start_node, end_node, algorithm=alg_choice)
        self.animate_step()

    def animate_step(self):
        try:
            state = next(self.animation_generator)
            if state["status"] == "running":
                self.current_eval = state["current"]
                self.open_nodes = state["open"]
                self.closed_nodes = state["closed"]
                self.draw_graph()
                self.after(50, self.animate_step) 

            elif state["status"] == "success":
                self.current_path = state["path"]
                self.current_eval = None
                self.draw_graph()
                self.update_route_panel(path=state["path"], dist=state["dist"])
                self.is_running = False

            elif state["status"] == "failed":
                self.lbl_total_dist.configure(text="Không tìm thấy đường!")
                self.is_running = False

        except StopIteration:
            pass

    def reset_ui(self):
        self.is_running = False
        self.animation_generator = None
        self.current_path = []
        self.current_eval = None
        self.open_nodes = set()
        self.closed_nodes = set()
        self.lbl_total_dist.configure(text="Tổng chiều dài: --")
        self.txt_route.configure(state="normal")
        self.txt_route.delete("1.0", tk.END)
        self.txt_route.insert("1.0", "Chưa có lộ trình.")
        self.txt_route.configure(state="disabled")
        self.draw_graph()

if __name__ == "__main__":
    app = SmartWayUI()
    app.mainloop()
