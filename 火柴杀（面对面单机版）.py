import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import random
import copy

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

class Equipment:
    def __init__(self, name):
        self.name = name
        tmpl = EQUIPMENT_TEMPLATES.get(name, {})
        self.equip_type = tmpl.get("type", "accessory"); self.owner = tmpl.get("owner", None); self.desc = tmpl.get("desc", "")
    def __repr__(self): return self.name

class Player:
    def __init__(self, name, hp, atk, matk, char_data):
        self.name = name; self.base_atk = atk; self.base_matk = matk; self.base_max_hp = hp
        self.atk = atk; self.matk = matk; self.max_hp = hp; self.hp = hp
        self.hand = []; self.char_data = char_data; self.char_name = char_data["name"]
        self.cooldowns = {sid: 0 for sid in char_data["skills"]}
        self.equipment = []; self.extra_slots = 0
        self.immune_turn = False; self.skip_next_turn = False; self.skip_full_turn = False
        self.poison_turns = 0; self.burn_turns = 0; self.double_attack_left = 0; self.damage_double_turn = False
        self.meditate_used_this_turn = False; self.duel_turns = 0; self.last_turn_hp = None; self.last_turn_equipment = None
        self.vest_used_this_turn = False; self.energy_shield_hp = 0; self.rhino_shield_available = True
        self.carriage_buff = False; self.attacked_this_turn = False; self.revive_count = 0
        self.hand_limit_reduction = 0; self.dodge_tokens = 0; self.extra_attack_tokens = 0; self.cd_penalty = 0
        self.transfer_active = False; self.transfer_target = None

    def get_hand_limit(self): return max(1, HAND_LIMIT_BASE - self.hand_limit_reduction)
    def draw_card(self, card):
        if len(self.hand) < self.get_hand_limit(): self.hand.append(card); return True
        return False
    def recalc_stats(self):
        atk_bonus = matk_bonus = max_hp_bonus = 0
        for eq in self.equipment:
            owner_match = (eq.owner == self.char_name)
            if eq.name == "重甲犀牛": max_hp_bonus += 1
            elif eq.name == "脉冲炮": matk_bonus += 1
            elif eq.name == "雷羽弓": atk_bonus += 1; matk_bonus += 1 if owner_match else 0
            elif eq.name == "火焰之刃": atk_bonus += 1; max_hp_bonus += 1 if owner_match else 0
            elif eq.name == "熔岩动力戟": matk_bonus += 1 if not owner_match else 0
            elif eq.name == "空间之刃": atk_bonus += 1 if not owner_match else 0
            elif eq.name == "寒冰之刃": matk_bonus += 1; max_hp_bonus += 1 if owner_match else 0
            elif eq.name == "剧毒之镰": atk_bonus += 1 if not owner_match else 0
            elif eq.name == "创造之墙": max_hp_bonus += 2 if owner_match else 1
            elif eq.name == "烟雾掩护": max_hp_bonus += 1 if not owner_match else 0
        self.atk = self.base_atk + atk_bonus; self.matk = self.base_matk + matk_bonus
        self.max_hp = self.base_max_hp + max_hp_bonus
        if self.hp > self.max_hp: self.hp = self.max_hp
    def equipment_limit(self): return 3 if self.char_name == "拾荒者" else 1
    def count_equipment_type(self, eq_type): return sum(1 for e in self.equipment if e.equip_type == eq_type)
    def can_equip(self, eq):
        limit = self.equipment_limit() + (self.extra_slots if self.char_name == "玖恒" else 0)
        return self.count_equipment_type(eq.equip_type) < limit
    def has_equipment(self, name): return any(e.name == name for e in self.equipment)

# ==================== 游戏主界面 ====================
class MatchstickKillApp:
    def __init__(self, root):
        self.root = root
        self.root.title("火柴杀 - 单机UI版")
        self.root.geometry("900x750")
        self.root.configure(bg="#f0f0f0")
        
        self.deck = []
        self.p1 = None; self.p2 = None
        self.current_player = None; self.opponent = None
        self.turn = 1; self.duel_active = False
        self.attack_cards_used = 0

        self.init_game_data()
        self.setup_ui()
        self.select_characters()

    def init_game_data(self):
        self.deck = []
        for _ in range(8): self.deck.append(Card("普攻·直击", "attack", 1))
        for _ in range(4): self.deck.append(Card("普攻·重击", "attack", 2))
        for _ in range(5): self.deck.append(Card("物理攻击", "physical"))
        for _ in range(5): self.deck.append(Card("法术攻击", "magic"))
        for _ in range(10): self.deck.append(Card("疗伤", "heal", 1))
        for _ in range(10): self.deck.append(Card("躲闪", "dodge"))
        for _ in range(2): self.deck.append(Card("全能盾牌", "omnishield"))
        for _ in range(3): self.deck.append(Card("狂暴剂", "rage"))
        for _ in range(3): self.deck.append(Card("麻醉剂", "anesthetic"))
        for _ in range(3): self.deck.append(Card("沉思", "meditate"))
        for _ in range(7): self.deck.append(Card("拆除", "dismantle"))
        for _ in range(5): self.deck.append(Card("抢夺", "steal"))
        self.deck.append(Card("决斗", "duel"))
        for eq in EQUIPMENT_TEMPLATES: self.deck.append(Card(eq, "equip"))
        random.shuffle(self.deck)

    def setup_ui(self):
        self.frame_top = tk.Frame(self.root, bg="#e74c3c", pady=10)
        self.frame_top.pack(fill="x")
        self.label_opponent = tk.Label(self.frame_top, text="对手: 等待选择...", font=("微软雅黑", 14, "bold"), bg="#e74c3c", fg="white")
        self.label_opponent.pack()
        
        self.frame_center = tk.LabelFrame(self.root, text=" 战斗日志 ", font=("微软雅黑", 12), padx=10, pady=10, bg="#f0f0f0")
        self.frame_center.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_text = scrolledtext.ScrolledText(self.frame_center, height=18, width=80, font=("微软雅黑", 11), state='disabled')
        self.log_text.pack(fill="both", expand=True)

        self.frame_bottom = tk.Frame(self.root, bg="#3498db", pady=10)
        self.frame_bottom.pack(fill="x", side="bottom")
        self.label_player = tk.Label(self.frame_bottom, text="你: 等待选择...", font=("微软雅黑", 14, "bold"), bg="#3498db", fg="white")
        self.label_player.pack()

        self.frame_hand = tk.LabelFrame(self.root, text=" 你的手牌 ", font=("微软雅黑", 12), padx=10, pady=10, bg="#f0f0f0")
        self.frame_hand.pack(fill="x", padx=20, pady=5)
        self.card_buttons = []

        self.frame_actions = tk.Frame(self.root, bg="#f0f0f0")
        self.frame_actions.pack(pady=10)
        
        self.btn_skill = tk.Button(self.frame_actions, text="查看技能", font=("微软雅黑", 12), width=10, command=self.action_skill)
        self.btn_skill.grid(row=0, column=0, padx=5)
        
        self.btn_view_equip = tk.Button(self.frame_actions, text="查看装备", font=("微软雅黑", 12), width=10, command=self.action_view_equipment)
        self.btn_view_equip.grid(row=0, column=1, padx=5)
        
        self.btn_unequip = tk.Button(self.frame_actions, text="卸下装备", font=("微软雅黑", 12), width=10, command=self.action_unequip)
        self.btn_unequip.grid(row=0, column=2, padx=5)
        
        self.btn_end_turn = tk.Button(self.frame_actions, text="结束回合", font=("微软雅黑", 12, "bold"), width=12, bg="#2ecc71", fg="white", command=self.action_end_turn)
        self.btn_end_turn.grid(row=0, column=3, padx=20)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def select_characters(self):
        self.log("=== 欢迎来到火柴杀 ===")
        char_info = "编号 | 名称   | HP | 物攻 | 法攻 | 定位\n"
        char_info += "------------------------------------------------------\n"
        for key, ch in CHARACTERS.items():
            char_info += f" {key:>2}  | {ch['name']} |  {ch['hp']:>2}  |  {ch['atk']:>2}  |  {ch['matk']:>2}  | {ch['desc']}\n"
        
        self.log("可用角色列表：")
        self.log(char_info)
        
        prompt_text = "玩家1选择角色 (输入编号 1-12):\n\n" + char_info
        c1 = simpledialog.askinteger("选择角色 - 玩家1", prompt_text, minvalue=1, maxvalue=12)
        if not c1: c1 = 1
        self.log(f"玩家1 选择了【{CHARACTERS[str(c1)]['name']}】")
        
        prompt_text2 = "玩家2选择角色 (输入编号 1-12):\n\n" + char_info
        c2 = simpledialog.askinteger("选择角色 - 玩家2", prompt_text2, minvalue=1, maxvalue=12)
        if not c2: c2 = 2
        self.log(f"玩家2 选择了【{CHARACTERS[str(c2)]['name']}】")

        ch1 = CHARACTERS[str(c1)]; ch2 = CHARACTERS[str(c2)]
        self.p1 = Player("玩家1", ch1["hp"], ch1["atk"], ch1["matk"], ch1)
        self.p2 = Player("玩家2", ch2["hp"], ch2["atk"], ch2["matk"], ch2)

        for _ in range(3):
            self.p1.draw_card(self.deck.pop())
            self.p2.draw_card(self.deck.pop())

        self.current_player = self.p1
        self.opponent = self.p2
        self.start_turn()

    def update_ui(self):
        p = self.current_player; o = self.opponent
        self.label_player.config(text=f"【{p.name}】 血量: {p.hp}/{p.max_hp}  物攻:{p.atk} 法攻:{p.matk} 装备:{len(p.equipment)}")
        self.label_opponent.config(text=f"【{o.name}】 血量: {o.hp}/{o.max_hp}  物攻:{o.atk} 法攻:{o.matk} 装备:{len(o.equipment)}")
        
        for btn in self.card_buttons: btn.destroy()
        self.card_buttons = []
        for i, card in enumerate(p.hand):
            display_name = card.name
            if card.card_type == 'equip':
                display_name += "（装备）"
            btn = tk.Button(self.frame_hand, text=display_name, font=("微软雅黑", 11), width=12, command=lambda c=card, idx=i: self.play_card(c, idx))
            btn.grid(row=i // 6, column=i % 6, padx=5, pady=5)
            self.card_buttons.append(btn)

    def start_turn(self):
        p = self.current_player; o = self.opponent
        self.attack_cards_used = 0
        if p.skip_full_turn:
            self.log(f"💉 {p.name} 被【麻醉剂】跳过整个回合！")
            p.skip_full_turn = False
            self.draw_phase(is_skipped=True)
            self.end_turn_logic()
            return

        p.immune_turn = False; p.damage_double_turn = False; p.meditate_used_this_turn = False
        p.vest_used_this_turn = False; p.attacked_this_turn = False

        if p.char_name == "多斯": p.hp = min(p.max_hp, p.hp + 1); self.log(f"✨ 多斯被动回血！")
        if p.poison_turns > 0: p.hp -= 1; p.poison_turns -= 1; self.log(f"☠ {p.name} 中毒掉血！")
        if p.burn_turns > 0: p.hp -= 1; p.burn_turns -= 1; self.log(f"🔥 {p.name} 灼烧掉血！")
        if p.has_equipment("能量护盾") and p.energy_shield_hp == 0: p.energy_shield_hp = 1

        if p.hp <= 0:
            if self.check_death(p): return

        self.draw_phase(is_skipped=p.skip_next_turn)
        if p.skip_next_turn:
            self.log(f"⛔ {p.name} 跳过出牌阶段！")
            p.skip_next_turn = False
            self.end_turn_logic()
            return
        self.update_ui()

    def draw_phase(self, is_skipped=False):
        p = self.current_player
        count = 3 if len(p.hand) == 0 else (1 if is_skipped else 2)
        drawn = 0
        for _ in range(count):
            if self.deck and p.draw_card(self.deck.pop()): drawn += 1
        self.log(f"💫 {p.name} 摸了 {drawn} 张牌。")

    def play_card(self, card, idx):
        p = self.current_player; o = self.opponent
        if card.card_type in ('attack', 'physical', 'magic'):
            limit = 999 if p.has_equipment("加特林") else (3 if p.char_name == "枪手" and p.has_equipment("双枪") else 2)
            if self.attack_cards_used >= limit and p.extra_attack_tokens == 0:
                self.log("⚠ 攻击手牌已达上限！"); return
            if p.extra_attack_tokens > 0: p.extra_attack_tokens -= 1
            self.attack_cards_used += 1
            p.attacked_this_turn = True
            
            dmg = card.value if card.card_type == 'attack' else (p.atk if card.card_type == 'physical' else p.matk)
            if card.card_type == 'attack':
                if p.has_equipment("剑匣") or (p.char_name == "枪手" and p.has_equipment("双枪")): dmg += 1
            if p.double_attack_left > 0: dmg *= 2; p.double_attack_left -= 1; self.log("🔥 狂击增幅翻倍！")
            if p.damage_double_turn: dmg *= 2; self.log("⚡ 战威增幅/狂暴剂翻倍！")
            if sum(1 for e in p.equipment if e.name == "机械猎犬") and random.random() < 1/3: dmg += 1; self.log("🐕 机械猎犬追伤！")
            
            self.log(f"⚔ {p.name} 对 {o.name} 造成 {dmg} 点伤害！")
            o.hp -= dmg
            p.hand.pop(idx)
        elif card.card_type == 'heal':
            p.hp = min(p.max_hp, p.hp + card.value); self.log(f"💚 {p.name} 回复 1 点生命。"); p.hand.pop(idx)
        elif card.card_type == 'rage':
            p.damage_double_turn = True; self.log("🔥 使用狂暴剂！"); p.hand.pop(idx)
        elif card.card_type == 'anesthetic':
            if o.skip_full_turn: self.log("⚠ 目标已被麻醉！"); return
            o.skip_full_turn = True; self.log("💉 使用麻醉剂！"); p.hand.pop(idx)
        elif card.card_type == 'meditate':
            if p.meditate_used_this_turn: self.log("⚠ 已经用过沉思！"); return
            p.meditate_used_this_turn = True; p.hand.pop(idx)
            drawn = 0
            for _ in range(5):
                if self.deck and p.draw_card(self.deck.pop()): drawn += 1
            self.log(f"📖 使用沉思，抽了 {drawn} 张牌！")
        elif card.card_type == 'dismantle':
            if not o.equipment: self.log("⚠ 对方没有装备！"); return
            removed = o.equipment.pop(random.randint(0, len(o.equipment)-1)); o.recalc_stats()
            self.log(f"🔨 拆除了 {o.name} 的【{removed.name}】！"); p.hand.pop(idx)
        elif card.card_type == 'steal':
            if not o.equipment: self.log("⚠ 对方没有装备！"); return
            for eq in o.equipment:
                if p.can_equip(eq):
                    o.equipment.remove(eq); o.recalc_stats(); p.equipment.append(eq); p.recalc_stats()
                    self.log(f"🎯 抢走了 {o.name} 的【{eq.name}】！"); p.hand.pop(idx); break
            else: self.log("⚠ 装备栏已满，无法抢夺！"); return
        elif card.card_type == 'equip':
            eq = Equipment(card.name)
            if not p.can_equip(eq): self.log(f"⚠ {eq.equip_type} 装备栏已满！"); return
            p.hand.pop(idx); p.equipment.append(eq); p.recalc_stats()
            self.log(f"⚙ 装备了【{eq.name}】！")
        else:
            self.log("这张牌暂时无法使用。")
        
        if o.hp <= 0: 
            if self.check_death(o): return
        self.update_ui()

    def action_skill(self):
        p = self.current_player; o = self.opponent
        skills = []
        for sid, sk in p.char_data["skills"].items():
            if p.cooldowns.get(sid, 0) == 0: skills.append((sid, sk["name"]))
        if not skills: self.log("⚠ 没有就绪的技能！"); return
        
        skill_list = "\n".join([f"{sid}. {name}" for sid, name in skills])
        choice = simpledialog.askinteger("使用技能", f"可用技能：\n{skill_list}\n\n请输入编号：", minvalue=1, maxvalue=3)
        if not choice: return
        sid = str(choice)
        if sid not in p.char_data["skills"] or p.cooldowns.get(sid,0) > 0: self.log("无效技能！"); return
        
        name = p.char_data["skills"][sid]["name"]
        if name in DEFENSE_SKILLS: self.log("⚠ 防御技能只能在受伤时使用！"); return
        cd = p.char_data["skills"][sid]["cd"]
        
        if name == "噬血": o.hp -= 1; p.hp = min(p.max_hp, p.hp+1); self.log("🩸 偷取1点生命！")
        elif name == "猎击": o.hp -= 2; self.log("🏹 造成2点伤害！")
        elif name == "腐毒侵蚀": o.poison_turns = 3; self.log("☠ 施加剧毒！")
        elif name == "速击": o.hp -= 1; self.log("⚡ 造成1点伤害！")
        elif name == "坚韧蜕变": p.base_max_hp += 1; p.base_atk += 1; p.recalc_stats(); self.log("💪 永久提升属性！")
        elif name == "电击眩晕": o.skip_next_turn = True; self.log("⚡ 敌方跳过出牌！")
        elif name == "狂击增幅": p.double_attack_left = 2; self.log("🔥 下2张攻击翻倍！")
        elif name == "固本": p.hp = min(p.max_hp, p.hp+1); self.log("💚 回复1点！")
        elif name == "剑击": o.hp -= 2; self.log("⚔ 造成2点伤害！")
        elif name == "火焰灼烧": o.hp -= 2; self.log("🔥 造成2点群体伤害！")
        elif name == "突刺": o.hp -= 1; self.log("🗡 造成1点伤害！")
        elif name == "寒冰增幅": p.base_atk += 1; p.base_matk += 1; p.recalc_stats(); self.log("❄ 永久提升法攻！")
        elif name == "迟滞弹": 
            for s in o.cooldowns:
                if o.cooldowns[s] > 0: o.cooldowns[s] += 2
            self.log("🔫 敌方冷却中技能CD+2！")
        elif name == "禁锢射击": o.skip_next_turn = True; self.log("🔒 敌方跳过出牌！")
        elif name == "时空回溯": p.hp = p.last_turn_hp or p.hp; self.log("⏰ 回溯血量！")
        elif name == "瞬闪": p.dodge_tokens += 1; self.log("💨 获得闪避！")
        elif name == "焚身灼烧": o.burn_turns = 3; self.log("🔥 施加灼烧！")
        elif name == "罪罚锁狱": p.transfer_active = True; p.transfer_target = o; self.log("⚖ 伤害转移！")
        elif name == "壁垒守护": p.dodge_tokens += 1; self.log("🛡 获得护盾！")
        elif name == "激光": o.hp -= 1; self.log("🔵 造成1点法术伤害！")
        elif name == "浮游炮": o.hp -= 2; self.log("💥 造成2点法术伤害（无视防御）！") # <--- 修改在这里
        elif name == "锐击": o.hp -= 2; self.log("⚔ 造成2点伤害！")
        elif name == "锁滞": o.skip_next_turn = True; self.log("🔗 敌方跳过出牌！")
        elif name == "战威增幅": p.damage_double_turn = True; self.log("⚡ 本回合伤害翻倍！")
        elif name == "愈护": p.hp = min(p.max_hp, p.hp+1); self.log("💚 回复1点！")
        elif name == "速愈调度": 
            if "1" in p.cooldowns: p.cooldowns["1"] = max(0, p.cooldowns["1"]-2)
            self.log("⏩ 一技能CD-2！")
        else: self.log(f"技能【{name}】暂未实现。"); return

        p.cooldowns[sid] = cd
        if o.hp <= 0: 
            if self.check_death(o): return
        self.update_ui()

    # ==================== 查看装备 ====================
    def action_view_equipment(self):
        p = self.current_player
        info = f"【{p.name}】的装备信息：\n\n"
        has_content = False
        if p.equipment:
            info += "=== 已装备 ===\n"
            for i, eq in enumerate(p.equipment):
                type_name = {"weapon": "武器", "armor": "防具", "accessory": "辅助"}.get(eq.equip_type, "未知")
                info += f"{i+1}. {eq.name}（{type_name}）\n   效果：{eq.desc}\n"
            has_content = True
        hand_equips = [c for c in p.hand if c.card_type == 'equip']
        if hand_equips:
            if has_content: info += "\n"
            info += "=== 手牌中的装备（未装备） ===\n"
            for i, card in enumerate(hand_equips):
                eq_name = card.name
                tmpl = EQUIPMENT_TEMPLATES.get(eq_name, {})
                type_name = {"weapon": "武器", "armor": "防具", "accessory": "辅助"}.get(tmpl.get("type"), "未知")
                desc = tmpl.get("desc", "无描述")
                info += f"{i+1}. {eq_name}（{type_name}）\n   效果：{desc}\n"
            has_content = True
        if not has_content: info += "你目前没有任何装备，手牌中也没有装备牌。"
        self.log(f"🔍 {p.name} 查看了装备信息。")
        messagebox.showinfo("查看装备", info)

    def action_unequip(self):
        p = self.current_player
        if not p.equipment: self.log("⚠ 你没有装备！"); return
        eq_names = [e.name for e in p.equipment]
        choice = simpledialog.askinteger("卸下装备", f"你的装备：\n" + "\n".join(f"{i+1}. {n}" for i,n in enumerate(eq_names)) + "\n\n输入编号卸下：", minvalue=1, maxvalue=len(p.equipment))
        if not choice: return
        eq = p.equipment.pop(choice-1); p.recalc_stats(); self.log(f"🔓 卸下了【{eq.name}】"); self.update_ui()

    def action_end_turn(self):
        p = self.current_player
        p.reduce_cooldowns()
        if p.char_name == "枪手": p.last_turn_hp = p.hp; p.last_turn_equipment = copy.deepcopy(p.equipment)
        p.transfer_active = False; p.transfer_target = None; p.extra_attack_tokens = 0
        p.rhino_shield_available = not p.attacked_this_turn
        if p.has_equipment("幽灵马车"): p.carriage_buff = True
        self.end_turn_logic()

    def end_turn_logic(self):
        self.current_player, self.opponent = self.opponent, self.current_player
        self.turn += 1
        self.start_turn()

    def check_death(self, player):
        if player.hp <= 0:
            if player.char_name == "多斯" and player.revive_count < 1:
                player.hp = player.max_hp; player.revive_count += 1; self.log(f"✨ {player.name} 触发【复生仪式】复活！"); self.update_ui(); return False
            if player.char_name == "秦默" and player.revive_count < 2:
                cost = 5 if player.revive_count == 0 else 10
                if len(player.hand) >= cost:
                    for _ in range(cost): player.hand.pop()
                    player.hp = player.max_hp; player.revive_count += 1; self.log(f"✨ {player.name} 触发【复生献祭】复活！"); self.update_ui(); return False
            self.log(f"💀 {player.name} 阵亡！游戏结束！")
            messagebox.showinfo("游戏结束", f"{player.name} 阵亡！")
            self.root.destroy()
            return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = MatchstickKillApp(root)
    root.mainloop()
