import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import random, copy, socket, threading, json, queue, time

# ==================== 基础数据 ====================
HAND_LIMIT_BASE = 20
DODGE_SKILLS = {"瞬身闪避", "瞬闪"}
SHIELD_SKILLS = {"冰墙", "壁垒守护", "坚防"}
DEFENSE_SKILLS = DODGE_SKILLS | SHIELD_SKILLS

CHARACTERS = {
    "1": {"name": "拾荒者", "hp": 6, "atk": 1, "matk": 1, "desc": "高坦度装备拉扯坦克", "passive": "装备上限3件",
          "skills": {"1": {"name": "劫掠", "cd": 0}, "2": {"name": "废土壁垒", "cd": 5}}},
    "2": {"name": "毒猎", "hp": 5, "atk": 2, "matk": 1, "desc": "持续磨血+资源压制", "passive": "无",
          "skills": {"1": {"name": "噬血", "cd": 3}, "2": {"name": "猎击", "cd": 3}, "3": {"name": "腐毒侵蚀", "cd": 5}}},
    "3": {"name": "罗伊", "hp": 5, "atk": 1, "matk": 2, "desc": "法伤抗压坦克", "passive": "无",
          "skills": {"1": {"name": "速击", "cd": 3}, "2": {"name": "坚防", "cd": 3}, "3": {"name": "坚韧蜕变", "cd": 5}}},
    "4": {"name": "吕山", "hp": 3, "atk": 2, "matk": 1, "desc": "手牌爆发+单控收割", "passive": "无",
          "skills": {"1": {"name": "瞬身闪避", "cd": 3}, "2": {"name": "电击眩晕", "cd": 3}, "3": {"name": "狂击增幅", "cd": 5}}},
    "5": {"name": "钟离", "hp": 2, "atk": 2, "matk": 2, "desc": "高频小技能输出", "passive": "无",
          "skills": {"1": {"name": "固本", "cd": 2}, "2": {"name": "剑击", "cd": 2}, "3": {"name": "火焰灼烧", "cd": 5}}},
    "6": {"name": "利刃", "hp": 3, "atk": 2, "matk": 1, "desc": "纯粹后期成长输出", "passive": "无",
          "skills": {"1": {"name": "冰墙", "cd": 3}, "2": {"name": "突刺", "cd": 3}, "3": {"name": "寒冰增幅", "cd": 5}}},
    "7": {"name": "枪手", "hp": 4, "atk": 2, "matk": 1, "desc": "冷却压制+强控", "passive": "无",
          "skills": {"1": {"name": "迟滞弹", "cd": 3}, "2": {"name": "禁锢射击", "cd": 3}, "3": {"name": "时空回溯", "cd": 5}}},
    "8": {"name": "帝郡", "hp": 4, "atk": 1, "matk": 2, "desc": "持续减益+伤害转移", "passive": "无",
          "skills": {"1": {"name": "瞬闪", "cd": 3}, "2": {"name": "焚身灼烧", "cd": 3}, "3": {"name": "罪罚锁狱", "cd": 5}}},
    "9": {"name": "冷锋", "hp": 3, "atk": 1, "matk": 2, "desc": "防御兜底+高额法伤", "passive": "无",
          "skills": {"1": {"name": "壁垒守护", "cd": 3}, "2": {"name": "激光", "cd": 3}, "3": {"name": "浮游炮", "cd": 5}}},
    "10": {"name": "秦默", "hp": 2, "atk": 2, "matk": 2, "desc": "手牌博弈+有限复活", "passive": "无",
          "skills": {"1": {"name": "傀儡术", "cd": 3}, "2": {"name": "锐击", "cd": 3}, "3": {"name": "复生献祭", "cd": 5}}},
    "11": {"name": "玖恒", "hp": 4, "atk": 1, "matk": 1, "desc": "装备拓展+强控", "passive": "无",
          "skills": {"1": {"name": "拓械", "cd": 3}, "2": {"name": "锁滞", "cd": 3}, "3": {"name": "战威增幅", "cd": 5}}},
    "12": {"name": "多斯", "hp": 3, "atk": 1, "matk": 1, "desc": "全队持续续航核心", "passive": "每回合回血",
          "skills": {"1": {"name": "愈护", "cd": 3}, "2": {"name": "速愈调度", "cd": 3}, "3": {"name": "复生仪式", "cd": 8}}},
}

EQUIPMENT_TEMPLATES = {
    "加特林": {"type": "weapon", "desc": "解除每回合攻击上限"}, "防弹背心": {"type": "armor", "desc": "首次物理伤害-1"},
    "能量护盾": {"type": "armor", "desc": "抵挡1点伤害"}, "机械猎犬": {"type": "accessory", "desc": "攻击时1/3概率+1伤害"},
    "飞行滑板": {"type": "accessory", "desc": "受伤时1/3概率闪避"}, "重甲犀牛": {"type": "accessory", "desc": "HP上限+1"},
    "幽灵马车": {"type": "accessory", "desc": "下回合首次技能伤害-1"},
    "脉冲炮": {"type": "weapon", "owner": "冷锋", "desc": "法攻+1"}, "雷羽弓": {"type": "weapon", "owner": "吕山", "desc": "物攻+1"},
    "火焰之刃": {"type": "weapon", "owner": "钟离", "desc": "物攻+1"}, "熔岩动力戟": {"type": "weapon", "owner": "帝郡", "desc": "法攻+1"},
    "空间之刃": {"type": "weapon", "owner": "玖恒", "desc": "物攻+1"}, "寒冰之刃": {"type": "weapon", "owner": "利刃", "desc": "法攻+1"},
    "剑匣": {"type": "weapon", "owner": "秦默", "desc": "普攻+1"}, "剧毒之镰": {"type": "weapon", "owner": "毒猎", "desc": "物攻+1"},
    "双枪": {"type": "weapon", "owner": "枪手", "desc": "普攻+1"}, "创造之墙": {"type": "armor", "owner": "罗伊", "desc": "HP上限+2"},
    "烟雾掩护": {"type": "armor", "owner": "拾荒者", "desc": "HP上限+1"}, "医疗包": {"type": "accessory", "owner": "多斯", "desc": "一技能CD-2"},
}

class Card:
    def __init__(self, name, card_type, value=0, effect=None):
        self.name = name; self.card_type = card_type; self.value = value; self.effect = effect
    def __repr__(self): return self.name
    def to_dict(self): return {"name": self.name, "card_type": self.card_type, "value": self.value, "effect": self.effect}
    @classmethod
    def from_dict(cls, d): return cls(d["name"], d["card_type"], d.get("value", 0), d.get("effect"))

class Equipment:
    def __init__(self, name):
        self.name = name
        tmpl = EQUIPMENT_TEMPLATES.get(name, {})
        self.equip_type = tmpl.get("type", "accessory"); self.owner = tmpl.get("owner", None); self.desc = tmpl.get("desc", "")
    def __repr__(self): return self.name

class Player:
    def __init__(self, pid, pname, char_data):
        self.pid = pid; self.name = pname; self.char_data = char_data; self.char_name = char_data["name"]
        self.base_atk = char_data["atk"]; self.base_matk = char_data["matk"]; self.base_max_hp = char_data["hp"]
        self.atk = self.base_atk; self.matk = self.base_matk; self.max_hp = self.base_max_hp; self.hp = self.base_max_hp
        self.hand = []; self.equipment = []
        self.cooldowns = {sid: 0 for sid in char_data["skills"]}
        self.extra_slots = 0; self.immune_turn = False; self.skip_next_turn = False; self.skip_full_turn = False
        self.poison_turns = 0; self.burn_turns = 0; self.double_attack_left = 0; self.damage_double_turn = False
        self.meditate_used_this_turn = False; self.duel_turns = 0
        self.vest_used_this_turn = False; self.energy_shield_hp = 0; self.rhino_shield_available = True
        self.carriage_buff = False; self.attacked_this_turn = False; self.revive_count = 0
        self.hand_limit_reduction = 0; self.dodge_tokens = 0; self.extra_attack_tokens = 0
        self.transfer_active = False; self.alive = True

    def get_hand_limit(self): return max(1, HAND_LIMIT_BASE - self.hand_limit_reduction)
    def draw_card(self, card):
        if len(self.hand) < self.get_hand_limit(): self.hand.append(card); return True
        return False
    def recalc_stats(self):
        ab = mb = hb = 0
        for eq in self.equipment:
            m = (eq.owner == self.char_name)
            if eq.name == "重甲犀牛": hb += 1
            elif eq.name == "脉冲炮": mb += 1
            elif eq.name == "雷羽弓": ab += 1; mb += 1 if m else 0
            elif eq.name == "火焰之刃": ab += 1; hb += 1 if m else 0
            elif eq.name == "熔岩动力戟": mb += 0 if m else 1
            elif eq.name == "空间之刃": ab += 0 if m else 1
            elif eq.name == "寒冰之刃": mb += 1; hb += 1 if m else 0
            elif eq.name == "剧毒之镰": ab += 0 if m else 1
            elif eq.name == "创造之墙": hb += 2 if m else 1
            elif eq.name == "烟雾掩护": hb += 0 if m else 1
        self.atk = self.base_atk + ab; self.matk = self.base_matk + mb
        self.max_hp = self.base_max_hp + hb
        if self.hp > self.max_hp: self.hp = self.max_hp
    def equipment_limit(self): return 3 if self.char_name == "拾荒者" else 1
    def count_eq(self, t): return sum(1 for e in self.equipment if e.equip_type == t)
    def can_equip(self, eq):
        limit = self.equipment_limit() + (self.extra_slots if self.char_name == "玖恒" else 0)
        return self.count_eq(eq.equip_type) < limit
    def has_equipment(self, name): return any(e.name == name for e in self.equipment)
    def to_dict(self, include_hand=False):
        d = {"pid": self.pid, "name": self.name, "char_name": self.char_name,
             "hp": self.hp, "max_hp": self.max_hp, "atk": self.atk, "matk": self.matk,
             "equipment": [e.name for e in self.equipment],
             "cooldowns": self.cooldowns, "alive": self.alive,
             "poison_turns": self.poison_turns, "burn_turns": self.burn_turns,
             "energy_shield_hp": self.energy_shield_hp}
        if include_hand: d["hand"] = [c.to_dict() for c in self.hand]
        return d

# ==================== 网络层 ====================
class NetworkManager:
    def __init__(self):
        self.mode = None; self.sock = None
        self.clients = []  # [(sock, name)]
        self.msg_queue = queue.Queue()
        self.running = False

    def start_server(self, port=5000):
        self.mode = "host"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(4); self.running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]; s.close(); return ip
        except: return "127.0.0.1"

    def _accept_loop(self):
        while self.running and len(self.clients) < 3:
            try:
                self.sock.settimeout(1.0)
                conn, addr = self.sock.accept()
                self.clients.append((conn, "等待..."))
                threading.Thread(target=self._recv_loop, args=(conn,), daemon=True).start()
                self.msg_queue.put({"type": "_new_client", "conn": conn})
            except socket.timeout: continue
            except: break

    def connect_to_server(self, host, port=5000):
        self.mode = "client"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port)); self.running = True
        threading.Thread(target=self._recv_loop, args=(self.sock,), daemon=True).start()
        return True

    def _recv_loop(self, conn):
        buf = b""
        while self.running:
            try:
                data = conn.recv(65536)
                if not data: break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try: msg = json.loads(line.decode("utf-8"))
                    except: continue
                    msg["_from_conn"] = conn
                    self.msg_queue.put(msg)
            except: break

    def send(self, conn, msg):
        try: conn.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        except: pass

    def send_to_player(self, pid, msg):
        if pid == 0: return
        if pid - 1 < len(self.clients): self.send(self.clients[pid-1][0], msg)

    def broadcast_all(self, msg):
        for c, n in self.clients: self.send(c, msg)

# ==================== 游戏主程序 ====================
class LanGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("火柴杀 - 局域网联机版")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")
        self.net = NetworkManager()
        self.my_id = 0; self.my_name = "玩家"
        self.role = None; self.game_started = False
        self.players = []; self.deck = []; self.turn_player_id = 0; self.turn = 1
        self.attack_cards_used = 0
        self.pending_ask = None
        self.teams = {} # 阵营系统
        self.setup_ui()
        self.root.after(100, self.process_network)
        self.root.after(200, self.ask_mode)

    def setup_ui(self):
        f = tk.Frame(self.root, bg="#e74c3c", pady=8); f.pack(fill="x")
        self.label_players = tk.Label(f, text="等待玩家...", font=("微软雅黑", 11, "bold"),
                                       bg="#e74c3c", fg="white", justify="left", anchor="w")
        self.label_players.pack(fill="x", padx=10)

        cf = tk.LabelFrame(self.root, text=" 战斗日志 ", font=("微软雅黑", 11), padx=5, pady=5, bg="#f0f0f0")
        cf.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(cf, height=16, font=("微软雅黑", 10), state='disabled')
        self.log_text.pack(fill="both", expand=True)

        bf = tk.Frame(self.root, bg="#3498db", pady=8); bf.pack(fill="x")
        self.label_me = tk.Label(bf, text="你: 等待...", font=("微软雅黑", 12, "bold"), bg="#3498db", fg="white")
        self.label_me.pack()

        hf = tk.LabelFrame(self.root, text=" 手牌 ", font=("微软雅黑", 11), padx=5, pady=5, bg="#f0f0f0")
        hf.pack(fill="x", padx=10, pady=3)
        self.frame_hand = hf; self.card_buttons = []

        af = tk.Frame(self.root, bg="#f0f0f0"); af.pack(pady=5)
        self.btn_start = tk.Button(af, text="开始游戏", font=("微软雅黑", 11, "bold"), width=10, bg="#f39c12", fg="white", command=self.start_game_click, state="disabled")
        self.btn_start.grid(row=0, column=0, padx=3)
        tk.Button(af, text="技能", font=("微软雅黑", 11), width=8, command=self.action_skill).grid(row=0, column=1, padx=3)
        tk.Button(af, text="装备", font=("微软雅黑", 11), width=8, command=self.action_view_equip).grid(row=0, column=2, padx=3)
        tk.Button(af, text="结束回合", font=("微软雅黑", 11, "bold"), width=10, bg="#2ecc71", fg="white", command=self.action_end_turn).grid(row=0, column=3, padx=10)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def ask_mode(self):
        c = messagebox.askyesnocancel("火柴杀联机", "创建房间？\n\n是=主机  否=加入")
        if c is None: self.root.destroy(); return
        if c:
            self.role = "host"; self.my_id = 0
            ip = self.net.start_server(5000)
            self.my_name = simpledialog.askstring("昵称", "你的昵称：") or "主机"
            self.log(f"🏠 房间已创建！IP: {ip}:5000")
            self.log(f"👤 {self.my_name} (玩家1)")
            messagebox.showinfo("房间已创建", f"IP: {ip}\n请告诉其他玩家！")
            self.btn_start.config(state="normal") # 主机初始就可点按钮
        else:
            self.role = "client"
            ip = simpledialog.askstring("加入", "主机 IP：")
            if not ip: self.root.destroy(); return
            self.my_name = simpledialog.askstring("昵称", "你的昵称：") or "玩家"
            try:
                self.net.connect_to_server(ip, 5000)
                self.net.send(self.net.sock, {"type": "join", "name": self.my_name})
                self.log(f"🔗 已连接 {ip}")
            except Exception as e:
                messagebox.showerror("失败", str(e)); self.root.destroy(); return
        self.root.after(300, self.check_lobby)

    def check_lobby(self):
        if self.role == "host":
            total = 1 + len(self.net.clients)
            names = [self.my_name] + [n for c, n in self.net.clients]
            self.label_players.config(text="玩家列表 (" + str(total) + "/4):\n" + "\n".join(f"  {i+1}. {n}" for i, n in enumerate(names)))
            # 动态更新按钮状态
            if total >= 2 and not self.game_started:
                self.btn_start.config(state="normal")
            else:
                self.btn_start.config(state="disabled")
            self.net.broadcast_all({"type": "lobby_update", "names": names})
        self.root.after(500, self.check_lobby)

    def start_game_click(self):
        if self.role != "host": return
        total = 1 + len(self.net.clients)
        if total < 2 or total > 4:
            messagebox.showwarning("提示", "人数必须在 2 到 4 人之间！")
            return
        self.start_char_select()

    def process_network(self):
        try:
            while True:
                msg = self.net.msg_queue.get_nowait()
                self.handle_msg(msg)
        except queue.Empty: pass
        self.root.after(100, self.process_network)

    def handle_msg(self, msg):
        t = msg.get("type")
        if t == "_new_client":
            self.net.send(msg["conn"], {"type": "welcome", "id": len(self.net.clients)})
        elif t == "join":
            name = msg.get("name", "玩家")
            conn = msg["_from_conn"]
            for i, (c, n) in enumerate(self.net.clients):
                if c == conn: self.net.clients[i] = (c, name); break
            self.log(f"👋 {name} 加入")
        elif t == "lobby_update":
            names = msg["names"]
            self.label_players.config(text="玩家列表:\n" + "\n".join(f"  {i+1}. {n}" for i, n in enumerate(names)))
        elif t == "start_select":
            self.select_order = msg["order"]; self.cur_select_idx = 0
            self.available_chars = list(CHARACTERS.keys()); self.picks = {}
            self.show_select()
        elif t == "pick_done":
            self.available_chars = msg["available"]; self.cur_select_idx = msg["idx"]
            self.log(f"✅ {msg['name']} 选了【{CHARACTERS[msg['cid']]['name']}】")
            if self.cur_select_idx >= len(self.select_order):
                self.net.broadcast_all({"type": "game_begin", "picks": self.picks})
                self.begin_game(self.picks)
            else:
                self.show_select()
        elif t == "game_begin":
            self.picks = msg["picks"]; self.begin_game(self.picks)
        elif t == "ask":
            self.show_ask_dialog(msg["prompt"], msg["options"])
        elif t == "answer":
            if self.pending_ask:
                self.pending_ask["answer"] = msg["index"]; self.pending_ask["event"].set()
        elif t == "state":
            self.sync_state(msg["state"])
        elif t == "log":
            self.log(msg["text"])
        elif t == "game_over":
            messagebox.showinfo("游戏结束", msg["text"])
            self.root.destroy()

    def start_char_select(self):
        if self.role != "host": return
        num_players = 1 + len(self.net.clients)
        order = list(range(num_players)); random.shuffle(order)
        self.select_order = order; self.cur_select_idx = 0
        self.available_chars = list(CHARACTERS.keys()); self.picks = {}
        self.log(f"🎲 选人顺序: {[o+1 for o in order]}")
        self.net.broadcast_all({"type": "start_select", "order": order})
        self.show_select()

    def show_select(self):
        num_players = len(self.select_order)
        if self.cur_select_idx >= num_players: return
        if self.select_order[self.cur_select_idx] != self.my_id: return
        text = "\n".join([f"{k}. {CHARACTERS[k]['name']} HP{CHARACTERS[k]['hp']} 物攻{CHARACTERS[k]['atk']} 法攻{CHARACTERS[k]['matk']}"
                          for k in self.available_chars])
        c = simpledialog.askinteger("选择角色", f"轮到你！可选:\n{text}\n编号:", minvalue=1, maxvalue=12)
        if not c or str(c) not in self.available_chars:
            self.show_select(); return
        cid = str(c)
        self.available_chars.remove(cid); self.picks[self.my_id] = cid
        self.log(f"✅ 你选了【{CHARACTERS[cid]['name']}】")
        self.cur_select_idx += 1
        if self.role == "host":
            self.net.broadcast_all({"type": "pick_done", "available": self.available_chars,
                                    "idx": self.cur_select_idx, "name": self.my_name, "cid": cid})
            if self.cur_select_idx >= num_players:
                self.net.broadcast_all({"type": "game_begin", "picks": self.picks})
                self.begin_game(self.picks)
            else:
                self.show_select()
        else:
            self.net.send(self.net.sock, {"type": "pick_done", "available": self.available_chars,
                                          "idx": self.cur_select_idx, "name": self.my_name, "cid": cid})

    def begin_game(self, picks):
        if self.game_started: return
        self.game_started = True
        num_players = len(picks)
        self.players = []
        for i in range(num_players):
            cid = picks.get(str(i)) or picks.get(i)
            cd = CHARACTERS[cid]
            p = Player(i, f"P{i+1}-{cd['name']}", cd)
            self.players.append(p)
            
        # 阵营分配
        self.teams = {}
        if num_players == 2:
            self.teams = {0: 1, 1: 2} # 1v1
        elif num_players == 3:
            self.teams = {0: 1, 1: 2, 2: 3} # 三方混战
        elif num_players == 4:
            self.teams = {0: 1, 1: 1, 2: 2, 3: 2} # 2v2 组队
            
        self.deck = self.make_deck()
        for _ in range(3):
            for p in self.players:
                if self.deck: p.draw_card(self.deck.pop())
        self.turn_player_id = random.randint(0, num_players-1)
        self.turn = 1
        self.log(f"🎮 游戏开始！先手：玩家{self.turn_player_id+1}")
        if num_players == 4:
            self.log(f"👥 阵营分配：玩家1&2 为一队，玩家3&4 为一队")
        self.refresh_ui()
        self.broadcast_state()

    def make_deck(self):
        d = []
        for _ in range(8): d.append(Card("普攻·直击", "attack", 1))
        for _ in range(4): d.append(Card("普攻·重击", "attack", 2))
        for _ in range(5): d.append(Card("物理攻击", "physical"))
        for _ in range(5): d.append(Card("法术攻击", "magic"))
        for _ in range(10): d.append(Card("疗伤", "heal", 1))
        for _ in range(10): d.append(Card("躲闪", "dodge"))
        for _ in range(2): d.append(Card("全能盾牌", "omnishield"))
        for _ in range(3): d.append(Card("狂暴剂", "rage"))
        for _ in range(3): d.append(Card("麻醉剂", "anesthetic"))
        for _ in range(3): d.append(Card("沉思", "meditate"))
        for _ in range(7): d.append(Card("拆除", "dismantle"))
        for _ in range(5): d.append(Card("抢夺", "steal"))
        d.append(Card("决斗", "duel"))
        for eq in EQUIPMENT_TEMPLATES: d.append(Card(eq, "equip"))
        random.shuffle(d); return d

    def refresh_ui(self):
        lines = []
        for p in self.players:
            if p.pid == self.my_id: continue
            status = "☠" if not p.alive else f"HP {p.hp}/{p.max_hp}"
            team_tag = "🟢" if self.teams.get(p.pid) == self.teams.get(self.my_id) else "🔴"
            lines.append(f"{team_tag} P{p.pid+1}-{p.char_name}: {status} 装备{len(p.equipment)}")
        self.label_players.config(text="\n".join(lines))
        if self.my_id < len(self.players):
            me = self.players[self.my_id]
            self.label_me.config(text=f"【{me.name}】HP:{me.hp}/{me.max_hp} 物攻:{me.atk} 法攻:{me.matk} 装备:{len(me.equipment)}")
            for b in self.card_buttons: b.destroy()
            self.card_buttons = []
            for i, c in enumerate(me.hand):
                nm = c.name + ("（装备）" if c.card_type == "equip" else "")
                b = tk.Button(self.frame_hand, text=nm, font=("微软雅黑", 10), width=11,
                              command=lambda cc=c, ii=i: self.play_card(cc, ii))
                b.grid(row=i//7, column=i%7, padx=3, pady=3)
                self.card_buttons.append(b)

    def broadcast_state(self):
        if self.role != "host": return
        for p in self.players:
            own = p.pid == self.my_id
            self.net.send_to_player(p.pid, {"type": "state",
                "state": [pp.to_dict(include_hand=(pp.pid == p.pid)) for pp in self.players],
                "turn_player": self.turn_player_id, "turn": self.turn})

    def sync_state(self, state):
        for i, pd in enumerate(state):
            if i >= len(self.players): break
            p = self.players[i]
            p.hp = pd["hp"]; p.max_hp = pd["max_hp"]; p.atk = pd["atk"]; p.matk = pd["matk"]
            p.alive = pd["alive"]; p.poison_turns = pd["poison_turns"]; p.burn_turns = pd["burn_turns"]
            p.equipment = [Equipment(n) for n in pd["equipment"]]
            if "hand" in pd: p.hand = [Card.from_dict(c) for c in pd["hand"]]
        self.refresh_ui()

    def ask_player(self, target_id, prompt, options):
        if target_id == self.my_id:
            text = prompt + "\n\n" + "\n".join(f"{i+1}. {o}" for i, o in enumerate(options))
            c = simpledialog.askinteger("选择", text, minvalue=1, maxvalue=len(options))
            return (c - 1) if c else 0
        self.pending_ask = {"answer": None, "event": threading.Event()}
        self.net.send_to_player(target_id, {"type": "ask", "prompt": prompt, "options": options})
        deadline = time.time() + 60
        while time.time() < deadline and not self.pending_ask["event"].is_set():
            self.root.update(); time.sleep(0.05)
        ans = self.pending_ask["answer"]
        self.pending_ask = None
        return ans if ans is not None else 0

    def show_ask_dialog(self, prompt, options):
        text = prompt + "\n\n" + "\n".join(f"{i+1}. {o}" for i, o in enumerate(options))
        c = simpledialog.askinteger("请选择", text, minvalue=1, maxvalue=len(options))
        idx = (c - 1) if c else 0
        self.net.send(self.net.sock, {"type": "answer", "index": idx})

    # ---------- 游戏动作 ----------
    def play_card(self, card, idx):
        if not self.game_started: return
        if self.turn_player_id != self.my_id:
            self.log("⚠ 不是你的回合"); return
        if self.role == "client":
            self.net.send(self.net.sock, {"type": "play", "card": card.to_dict(), "idx": idx})
            return
        self.host_play(self.my_id, card, idx)

    def host_play(self, pid, card, idx):
        p = self.players[pid]
        # 筛选敌人
        enemies = [q for q in self.players if q.alive and self.teams[q.pid] != self.teams[pid]]
        if card.card_type in ("attack", "physical", "magic"):
            if not enemies: return
            options = [f"P{q.pid+1}-{q.char_name}" for q in enemies]
            t_idx = self.ask_player(pid, "选择目标:", options)
            target = enemies[t_idx]
            dmg = card.value if card.card_type == "attack" else (p.atk if card.card_type == "physical" else p.matk)
            if card.card_type == "attack":
                if p.has_equipment("剑匣") or (p.char_name == "枪手" and p.has_equipment("双枪")): dmg += 1
            if p.double_attack_left > 0: dmg *= 2; p.double_attack_left -= 1
            if p.damage_double_turn: dmg *= 2
            if sum(1 for e in p.equipment if e.name == "机械猎犬") and random.random() < 1/3: dmg += 1
            t_dmg = self.apply_damage(target, dmg, p, card.card_type)
            self.broadcast_log(f"⚔ {p.name} 对 {target.name} 造成 {t_dmg} 伤害")
            p.hand.pop(idx)
        elif card.card_type == "heal":
            p.hp = min(p.max_hp, p.hp + card.value); p.hand.pop(idx)
            self.broadcast_log(f"💚 {p.name} 回复 {card.value} 血")
        elif card.card_type == "rage":
            p.damage_double_turn = True; p.hand.pop(idx); self.broadcast_log(f"🔥 {p.name} 狂暴剂")
        elif card.card_type == "anesthetic":
            if not enemies: return
            t_idx = self.ask_player(pid, "麻醉谁?", [f"P{q.pid+1}-{q.char_name}" for q in enemies])
            enemies[t_idx].skip_full_turn = True; p.hand.pop(idx)
            self.broadcast_log(f"💉 {p.name} 麻醉 {enemies[t_idx].name}")
        elif card.card_type == "meditate":
            p.hand.pop(idx)
            cnt = 0
            for _ in range(5):
                if self.deck and p.draw_card(self.deck.pop()): cnt += 1
            self.broadcast_log(f"📖 {p.name} 沉思摸 {cnt} 张")
        elif card.card_type == "dismantle":
            targets = [q for q in enemies if q.equipment]
            if not targets: self.broadcast_log("⚠ 无目标"); return
            t_idx = self.ask_player(pid, "拆谁的装备?", [f"P{q.pid+1}-{q.char_name}" for q in targets])
            target = targets[t_idx]
            eq_options = [f"{e.name}" for e in target.equipment]
            eq_idx = self.ask_player(pid, "拆哪件?", eq_options)
            target.equipment.pop(eq_idx); target.recalc_stats(); p.hand.pop(idx)
            self.broadcast_log(f"🔨 {p.name} 拆除 {target.name} 的装备")
        elif card.card_type == "steal":
            targets = [q for q in enemies if q.equipment]
            if not targets: self.broadcast_log("⚠ 无目标"); return
            t_idx = self.ask_player(pid, "抢谁的装备?", [f"P{q.pid+1}-{q.char_name}" for q in targets])
            target = targets[t_idx]
            eq_idx = self.ask_player(pid, "抢哪件?", [e.name for e in target.equipment])
            eq = target.equipment[eq_idx]
            if p.can_equip(eq):
                target.equipment.pop(eq_idx); target.recalc_stats()
                p.equipment.append(eq); p.recalc_stats(); p.hand.pop(idx)
                self.broadcast_log(f"🎯 {p.name} 抢走 {target.name} 的 {eq.name}")
            else:
                self.broadcast_log("⚠ 装备栏满，抢夺失败")
        elif card.card_type == "equip":
            eq = Equipment(card.name)
            if p.can_equip(eq):
                p.equipment.append(eq); p.recalc_stats(); p.hand.pop(idx)
                self.broadcast_log(f"⚙ {p.name} 装备 {eq.name}")
            else: self.broadcast_log("⚠ 装备栏满")
        elif card.card_type == "duel":
            if not enemies: return
            t_idx = self.ask_player(pid, "决斗谁?", [f"P{q.pid+1}-{q.char_name}" for q in enemies])
            t = enemies[t_idx]; p.duel_turns = 3; t.duel_turns = 3
            p.hand.pop(idx)
            self.broadcast_log(f"⚔ {p.name} 与 {t.name} 决斗！")
        self.broadcast_state()
        self.check_end()

    def apply_damage(self, target, dmg, attacker, damage_type):
        if target.transfer_active:
            for q in self.players:
                if q.alive and self.teams[q.pid] != self.teams[target.pid]:
                    q.hp -= dmg
                    self.broadcast_log(f"⚖ 伤害转移到 {q.name}")
                    return 0
        if damage_type in ("attack", "magic") and target.carriage_buff:
            dmg = max(0, dmg - 1); target.carriage_buff = False
        if damage_type == "physical" and target.has_equipment("防弹背心") and not target.vest_used_this_turn:
            dmg = max(0, dmg - 1); target.vest_used_this_turn = True
        if target.has_equipment("重甲犀牛") and target.rhino_shield_available:
            dmg = max(0, dmg - 1); target.rhino_shield_available = False
        if sum(1 for e in target.equipment if e.name == "飞行滑板") and random.random() < 1/3:
            self.broadcast_log(f"🛹 {target.name} 滑板闪避"); return 0
        if target.energy_shield_hp > 0:
            absorb = min(target.energy_shield_hp, dmg)
            target.energy_shield_hp -= absorb; dmg -= absorb
        if dmg <= 0: return 0
        options = []
        if target.dodge_tokens > 0: options.append(("token", "快刺闪避"))
        for sid, sk in target.char_data["skills"].items():
            nm = sk["name"]
            if nm in DEFENSE_SKILLS and target.cooldowns.get(sid, 0) == 0:
                if damage_type == "magic" and nm in SHIELD_SKILLS: continue
                options.append(("skill", sid, nm))
        for i, c in enumerate(target.hand):
            if c.card_type == "dodge": options.append(("dodge", i, "躲闪"))
            elif c.card_type == "omnishield": options.append(("omni", i, "全能盾牌"))
        options.append(("none", 0, "不防御"))
        if len(options) == 1:
            target.hp -= dmg
            return dmg
        ans = self.ask_player(target.pid, f"你受到 {dmg} 伤害，防御?", [o[2] for o in options])
        choice = options[ans]
        if choice[0] == "token":
            target.dodge_tokens -= 1; self.broadcast_log(f"💨 {target.name} 闪避"); return 0
        elif choice[0] == "skill":
            sk = target.char_data["skills"][choice[1]]
            target.cooldowns[choice[1]] = sk["cd"]
            self.broadcast_log(f"🛡 {target.name} 使用 {choice[2]}"); return 0
        elif choice[0] == "dodge":
            target.hand.pop(choice[1]); self.broadcast_log(f"💨 {target.name} 躲闪"); return 0
        elif choice[0] == "omni":
            target.hand.pop(choice[1]); self.broadcast_log(f"🛡 {target.name} 全能盾牌"); return 0
        target.hp -= dmg
        return dmg

    def broadcast_log(self, text):
        self.log(text)
        if self.role == "host": self.net.broadcast_all({"type": "log", "text": text})

    def check_end(self):
        alive_teams = set(self.teams[p.pid] for p in self.players if p.alive)
        if len(alive_teams) <= 1:
            winner_team = list(alive_teams)[0] if alive_teams else None
            winners = [p.name for p in self.players if p.alive and self.teams[p.pid] == winner_team]
            txt = f"🏆 阵营 {winner_team} 获胜！({', '.join(winners)})" if winners else "平局！"
            self.log(txt)
            if self.role == "host": self.net.broadcast_all({"type": "game_over", "text": txt})
            messagebox.showinfo("游戏结束", txt)
            self.root.destroy()

    def action_skill(self):
        if self.turn_player_id != self.my_id: self.log("⚠ 不是你的回合"); return
        me = self.players[self.my_id]
        avail = [(sid, sk["name"]) for sid, sk in me.char_data["skills"].items() if me.cooldowns.get(sid, 0) == 0]
        if not avail: self.log("⚠ 无可用技能"); return
        text = "可用:\n" + "\n".join(f"{i+1}. {n}" for i, (s, n) in enumerate(avail))
        c = simpledialog.askinteger("技能", text, minvalue=1, maxvalue=len(avail))
        if not c: return
        sid, name = avail[c-1]
        if self.role == "client":
            self.net.send(self.net.sock, {"type": "skill", "sid": sid})
        else:
            self.host_skill(self.my_id, sid)

    def host_skill(self, pid, sid):
        p = self.players[pid]
        name = p.char_data["skills"][sid]["name"]
        cd = p.char_data["skills"][sid]["cd"]
        enemies = [q for q in self.players if q.alive and self.teams[q.pid] != self.teams[pid]]
        
        # ---- 冷锋大招特殊处理：浮游炮 2点法术伤害，无视防御 ----
        if name == "浮游炮":
            if enemies:
                t_idx = self.ask_player(pid, "浮游炮打谁?", [f"P{q.pid+1}-{q.char_name}" for q in enemies])
                target = enemies[t_idx]
                target.hp -= 2
                self.broadcast_log(f"💥 {p.name} 使用【浮游炮】，对 {target.name} 造成 2 点法术伤害（无视防御）！")
            p.cooldowns[sid] = cd
            self.broadcast_state(); self.check_end(); return
        # ---------------------------------------------------
        
        if name == "噬血":
            if enemies: enemies[0].hp -= 1; p.hp = min(p.max_hp, p.hp+1)
        elif name in ("猎击", "剑击", "火焰灼烧", "锐击"):
            for q in enemies: q.hp -= 2
        elif name in ("速击", "突刺", "激光"):
            if enemies: enemies[0].hp -= 1
        elif name in ("固本", "愈护", "急救"):
            p.hp = min(p.max_hp, p.hp+1)
        elif name == "坚韧蜕变": p.base_max_hp += 1; p.base_atk += 1; p.recalc_stats()
        elif name == "寒冰增幅": p.base_atk += 1; p.base_matk += 1; p.recalc_stats()
        elif name == "狂击增幅": p.double_attack_left = 2
        elif name == "战威增幅": p.damage_double_turn = True
        elif name in ("电击眩晕", "禁锢射击", "锁滞"):
            if enemies: enemies[0].skip_next_turn = True
        elif name == "腐毒侵蚀":
            if enemies: enemies[0].poison_turns = 3
        elif name == "焚身灼烧":
            if enemies: enemies[0].burn_turns = 3
        elif name == "迟滞弹":
            for q in self.players:
                if self.teams[q.pid] != self.teams[pid]:
                    for k in q.cooldowns:
                        if q.cooldowns[k] > 0: q.cooldowns[k] += 2
        elif name == "速愈调度":
            if "1" in p.cooldowns: p.cooldowns["1"] = max(0, p.cooldowns["1"]-2)
        elif name == "拓械":
            if p.extra_slots < 3 and len(p.hand) >= 2:
                p.hand.pop(); p.hand.pop(); p.extra_slots += 1
        p.cooldowns[sid] = cd
        self.broadcast_log(f"✨ {p.name} 使用 {name}")
        self.broadcast_state()
        self.check_end()

    def action_view_equip(self):
        me = self.players[self.my_id]
        info = f"装备：\n"
        for e in me.equipment: info += f"  {e.name}（{e.desc}）\n"
        hand_eq = [c for c in me.hand if c.card_type == "equip"]
        if hand_eq:
            info += "\n手牌中的装备：\n"
            for c in hand_eq: info += f"  {c.name}（{EQUIPMENT_TEMPLATES.get(c.name,{}).get('desc','')}）\n"
        messagebox.showinfo("装备信息", info)

    def action_end_turn(self):
        if self.turn_player_id != self.my_id: self.log("⚠ 不是你的回合"); return
        if self.role == "client":
            self.net.send(self.net.sock, {"type": "end_turn"})
            return
        self.host_end_turn()

    def host_end_turn(self):
        p = self.players[self.turn_player_id]
        for k in p.cooldowns:
            if p.cooldowns[k] > 0: p.cooldowns[k] -= 1
        p.rhino_shield_available = not p.attacked_this_turn
        if p.has_equipment("幽灵马车"): p.carriage_buff = True
        p.transfer_active = False; p.extra_attack_tokens = 0
        p.immune_turn = False; p.damage_double_turn = False; p.meditate_used_this_turn = False
        p.vest_used_this_turn = False; p.attacked_this_turn = False
        
        num_players = len(self.players)
        self.turn_player_id = (self.turn_player_id + 1) % num_players
        while not self.players[self.turn_player_id].alive:
            self.turn_player_id = (self.turn_player_id + 1) % num_players
        self.turn += 1
        
        p = self.players[self.turn_player_id]
        cnt = 3 if len(p.hand) == 0 else (1 if p.skip_next_turn or p.skip_full_turn else 2)
        if p.skip_full_turn:
            self.broadcast_log(f"💉 {p.name} 跳过整个回合")
            p.skip_full_turn = False
        elif p.skip_next_turn:
            self.broadcast_log(f"⛔ {p.name} 跳过出牌")
            p.skip_next_turn = False
        drawn = 0
        for _ in range(cnt):
            if self.deck and p.draw_card(self.deck.pop()): drawn += 1
        if p.poison_turns > 0: p.hp -= 1; p.poison_turns -= 1
        if p.burn_turns > 0: p.hp -= 1; p.burn_turns -= 1
        if p.has_equipment("能量护盾") and p.energy_shield_hp == 0: p.energy_shield_hp = 1
        self.broadcast_log(f"--- 第{self.turn}回合：{p.name} 摸 {drawn} 张 ---")
        self.broadcast_state()
        self.check_end()
        if self.turn_player_id == self.my_id: self.refresh_ui()

    def _handle_client_actions(self, msg):
        t = msg.get("type")
        if self.role != "host": return
        if t == "play":
            card = Card.from_dict(msg["card"]); idx = msg["idx"]
            self.host_play(self._client_pid(msg["_from_conn"]), card, idx)
        elif t == "skill":
            pid = self._client_pid(msg["_from_conn"])
            self.host_skill(pid, msg["sid"])
        elif t == "end_turn":
            pid = self._client_pid(msg["_from_conn"])
            if self.turn_player_id == pid: self.host_end_turn()
        elif t == "answer":
            if self.pending_ask:
                self.pending_ask["answer"] = msg["index"]; self.pending_ask["event"].set()

    def _client_pid(self, conn):
        for i, (c, n) in enumerate(self.net.clients):
            if c == conn: return i + 1
        return 0

    def run(self):
        orig = self.handle_msg
        def new_handle(msg):
            if msg.get("type") in ("play", "skill", "end_turn", "answer") and self.role == "host":
                self._handle_client_actions(msg); return
            orig(msg)
        self.handle_msg = new_handle
        self.root.mainloop()

if __name__ == "__main__":
    LanGame().run()
    
