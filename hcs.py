import random
import copy

# ==================== 常量 ====================
HAND_LIMIT_BASE = 20
DODGE_SKILLS = {"瞬身闪避", "瞬闪"}
SHIELD_SKILLS = {"冰墙", "壁垒守护", "坚防"}
DEFENSE_SKILLS = DODGE_SKILLS | SHIELD_SKILLS

# ==================== 装备模板 ====================
EQUIPMENT_TEMPLATES = {
    "加特林":     {"type": "weapon", "universal": True,  "desc": "解除每回合最多2张攻击手牌的限制"},
    "防弹背心":   {"type": "armor",  "universal": True,  "desc": "每回合首次物理伤害-1"},
    "能量护盾":   {"type": "armor",  "universal": True,  "desc": "获得1点护盾，破后下回合恢复"},
    "机械猎犬":   {"type": "accessory","universal": True, "desc": "攻击时1/3概率+1伤害"},
    "飞行滑板":   {"type": "accessory","universal": True, "desc": "受伤时1/3概率完全闪避"},
    "重甲犀牛":   {"type": "accessory","universal": True, "desc": "HP上限+1；未攻击则下次伤害-1"},
    "幽灵马车":   {"type": "accessory","universal": True, "desc": "每回合结束，下回合首次技能伤害-1"},
    "脉冲炮":     {"type": "weapon", "owner": "冷锋",  "desc": "冷锋：法攻+1，激光CD-1；他人：法攻+1"},
    "雷羽弓":     {"type": "weapon", "owner": "吕山",  "desc": "吕山：物攻+1、法攻+1；他人：物攻+1"},
    "火焰之刃":   {"type": "weapon", "owner": "钟离",  "desc": "钟离：物攻+1、HP上限+1；他人：物攻+1"},
    "熔岩动力戟": {"type": "weapon", "owner": "帝郡",  "desc": "帝郡：灼烧5回合；他人：法攻+1"},
    "空间之刃":   {"type": "weapon", "owner": "玖恒",  "desc": "玖恒：锁滞双目标；他人：物攻+1"},
    "寒冰之刃":   {"type": "weapon", "owner": "利刃",  "desc": "利刃：法攻+1、普攻+1、HP上限+1；他人：法攻+1"},
    "剑匣":       {"type": "weapon", "owner": "秦默",  "desc": "秦默：普攻+1、傀儡双目标；他人：普攻+1"},
    "剧毒之镰":   {"type": "weapon", "owner": "毒猎",  "desc": "毒猎：大招双目标；他人：物攻+1"},
    "双枪":       {"type": "weapon", "owner": "枪手",  "desc": "枪手：普攻+1、每回合3张攻击；他人：普攻+1"},
    "创造之墙":   {"type": "armor",  "owner": "罗伊",  "desc": "罗伊：HP上限+2；他人：HP上限+1"},
    "烟雾掩护":   {"type": "armor",  "owner": "拾荒者", "desc": "拾荒者：大招+1回合、CD-1；他人：HP上限+1"},
    "医疗包":     {"type": "accessory","owner": "多斯", "desc": "多斯：一技能CD-2；他人：获得【急救】"},
}

# ==================== 角色数据 ====================
CHARACTERS = {
    "1": {"name": "拾荒者", "hp": 6, "atk": 1, "matk": 1, "desc": "高坦度装备拉扯型坦克", "passive": "拾获：装备栏每类上限3件",
          "skills": {
              "1": {"name": "劫掠", "cd": 0, "desc": "消耗2张手牌，偷对手1件装备或1张手牌"},
              "2": {"name": "废土壁垒", "cd": 5, "desc": "1回合内免疫普通攻击和技能伤害"},
          }},
    "2": {"name": "毒猎", "hp": 5, "atk": 2, "matk": 1, "desc": "持续磨血+资源压制", "passive": "无",
          "skills": {
              "1": {"name": "噬血", "cd": 3, "desc": "窃取敌方1点血量，自身回复1点"},
              "2": {"name": "猎击", "cd": 3, "desc": "对单体造成2点技能伤害"},
              "3": {"name": "腐毒侵蚀", "cd": 5, "desc": "目标每回合掉1血，持续3回合；目标手牌上限永久-1"},
          }},
    "3": {"name": "罗伊", "hp": 5, "atk": 1, "matk": 2, "desc": "法伤抗压型坦克，自带反伤", "passive": "无",
          "skills": {
              "1": {"name": "速击", "cd": 3, "desc": "对单体造成1点技能伤害"},
              "2": {"name": "坚防", "cd": 3, "desc": "抵挡1次伤害并反弹1点（受伤时使用）"},
              "3": {"name": "坚韧蜕变", "cd": 5, "desc": "永久+1血量上限，+1物攻"},
          }},
    "4": {"name": "吕山", "hp": 3, "atk": 2, "matk": 1, "desc": "手牌爆发+单控收割核心", "passive": "无",
          "skills": {
              "1": {"name": "瞬身闪避", "cd": 3, "desc": "规避1次伤害（受伤时使用）"},
              "2": {"name": "电击眩晕", "cd": 3, "desc": "敌方跳过出牌阶段"},
              "3": {"name": "狂击增幅", "cd": 5, "desc": "下2张攻击手牌伤害翻倍"},
          }},
    "5": {"name": "钟离", "hp": 2, "atk": 2, "matk": 2, "desc": "高频小技能输出，全场AOE", "passive": "无",
          "skills": {
              "1": {"name": "固本", "cd": 2, "desc": "回复1点血量"},
              "2": {"name": "剑击", "cd": 2, "desc": "对单体造成2点技能伤害"},
              "3": {"name": "火焰灼烧", "cd": 5, "desc": "对全体敌人各造成2点伤害"},
          }},
    "6": {"name": "利刃", "hp": 3, "atk": 2, "matk": 1, "desc": "纯粹后期成长型输出", "passive": "无",
          "skills": {
              "1": {"name": "冰墙", "cd": 3, "desc": "抵挡1次伤害（受伤时使用）"},
              "2": {"name": "突刺", "cd": 3, "desc": "对单体造成1点技能伤害"},
              "3": {"name": "寒冰增幅", "cd": 5, "desc": "永久+1物攻，+1法攻"},
          }},
    "7": {"name": "枪手", "hp": 4, "atk": 2, "matk": 1, "desc": "冷却压制+回合强控", "passive": "无",
          "skills": {
              "1": {"name": "迟滞弹", "cd": 3, "desc": "敌方所有冷却中技能CD+2"},
              "2": {"name": "禁锢射击", "cd": 3, "desc": "敌方跳过出牌阶段"},
              "3": {"name": "时空回溯", "cd": 5, "desc": "血量/装备/手牌/冷却/状态回溯到上回合结束"},
          }},
    "8": {"name": "帝郡", "hp": 4, "atk": 1, "matk": 2, "desc": "持续减益+伤害转移控场", "passive": "无",
          "skills": {
              "1": {"name": "瞬闪", "cd": 3, "desc": "规避1次伤害（受伤时使用）"},
              "2": {"name": "焚身灼烧", "cd": 3, "desc": "目标每回合掉1血，持续3回合"},
              "3": {"name": "罪罚锁狱", "cd": 5, "desc": "本回合帝郡受到的伤害全部转移给指定目标"},
          }},
    "9": {"name": "冷锋", "hp": 3, "atk": 1, "matk": 2, "desc": "防御兜底+单体高额法伤", "passive": "无",
          "skills": {
              "1": {"name": "壁垒守护", "cd": 3, "desc": "抵挡1次伤害（受伤时使用）"},
              "2": {"name": "激光", "cd": 3, "desc": "对单体造成1点法术技能伤害"},
              "3": {"name": "浮游炮", "cd": 5, "desc": "对单体造成3点法术技能伤害"},
          }},
    "10": {"name": "秦默", "hp": 2, "atk": 2, "matk": 2, "desc": "手牌博弈型辅助，有限复活", "passive": "无",
          "skills": {
              "1": {"name": "傀儡术", "cd": 3, "desc": "借用敌方1张手牌使用"},
              "2": {"name": "锐击", "cd": 3, "desc": "对单体造成2点技能伤害"},
              "3": {"name": "复生献祭", "cd": 5, "desc": "阵亡时献祭手牌复活（第1次5张，第2次10张，最多2次）"},
          }},
    "11": {"name": "玖恒", "hp": 4, "atk": 1, "matk": 1, "desc": "装备拓展+强控+团队增伤", "passive": "无",
          "skills": {
              "1": {"name": "拓械", "cd": 3, "desc": "献祭2张手牌，+1额外装备槽（上限3）"},
              "2": {"name": "锁滞", "cd": 3, "desc": "敌方跳过出牌阶段"},
              "3": {"name": "战威增幅", "cd": 5, "desc": "本回合自身所有伤害翻倍（上限2倍）"},
          }},
    "12": {"name": "多斯", "hp": 3, "atk": 1, "matk": 1, "desc": "全队持续续航核心",
          "passive": "愈愈光环：存活时己方全体每回合回复1点血量",
          "skills": {
              "1": {"name": "愈护", "cd": 3, "desc": "自身回复1点血量"},
              "2": {"name": "速愈调度", "cd": 3, "desc": "自身一技能CD-2"},
              "3": {"name": "复生仪式", "cd": 8, "desc": "阵亡时自动复活（每局1次）"},
          }},
}

# ==================== 卡牌类 ====================
class Card:
    def __init__(self, name, card_type, value=0, description="", effect=None):
        self.name = name
        self.card_type = card_type
        self.value = value
        self.description = description
        self.effect = effect

    def __repr__(self):
        return f"{self.name}"

# ==================== 装备类 ====================
class Equipment:
    def __init__(self, name):
        self.name = name
        tmpl = EQUIPMENT_TEMPLATES.get(name, {})
        self.equip_type = tmpl.get("type", "accessory")
        self.is_universal = tmpl.get("universal", False)
        self.owner = tmpl.get("owner", None)
        self.desc = tmpl.get("desc", "")

    def __repr__(self):
        return f"{self.name}"

# ==================== 玩家类 ====================
class Player:
    def __init__(self, name, hp, atk, matk, char_data):
        self.name = name
        self.base_atk = atk
        self.base_matk = matk
        self.base_max_hp = hp
        self.atk = atk
        self.matk = matk
        self.max_hp = hp
        self.hp = hp

        self.hand = []
        self.char_data = char_data
        self.char_name = char_data["name"]
        self.cooldowns = {sid: 0 for sid in char_data["skills"]}

        self.immune_turn = False
        self.skip_next_turn = False
        self.skip_full_turn = False
        self.poison_turns = 0
        self.burn_turns = 0
        self.double_attack_left = 0
        self.damage_double_turn = False
        self.meditate_used_this_turn = False
        self.duel_turns = 0
        self.extra_slots = 0

        self.equipment = []

        self.vest_used_this_turn = False
        self.energy_shield_hp = 0
        self.rhino_shield_available = True
        self.carriage_buff = False
        self.attacked_this_turn = False

        self.prev_state = None
        self.gunner_snapshot = None  # 枪手专用快照

        self.revive_count = 0
        self.hand_limit_reduction = 0
        self.dodge_tokens = 0
        self.extra_attack_tokens = 0
        self.cd_penalty = 0
        self.transfer_active = False
        self.transfer_target = None

    def get_hand_limit(self):
        return max(1, HAND_LIMIT_BASE - self.hand_limit_reduction)

    def get_state_snapshot(self):
        return {
            "hp": self.hp, "equipment": copy.deepcopy(self.equipment),
            "poison_turns": self.poison_turns, "burn_turns": self.burn_turns,
            "immune_turn": self.immune_turn, "skip_next_turn": self.skip_next_turn,
            "skip_full_turn": self.skip_full_turn, "damage_double_turn": self.damage_double_turn,
            "double_attack_left": self.double_attack_left, "energy_shield_hp": self.energy_shield_hp,
            "carriage_buff": self.carriage_buff, "vest_used_this_turn": self.vest_used_this_turn,
            "rhino_shield_available": self.rhino_shield_available, "attacked_this_turn": self.attacked_this_turn,
        }

    def load_state_snapshot(self, state):
        self.hp = state["hp"]
        self.equipment = copy.deepcopy(state["equipment"])
        self.poison_turns = state["poison_turns"]
        self.burn_turns = state["burn_turns"]
        self.immune_turn = state["immune_turn"]
        self.skip_next_turn = state["skip_next_turn"]
        self.skip_full_turn = state["skip_full_turn"]
        self.damage_double_turn = state["damage_double_turn"]
        self.double_attack_left = state["double_attack_left"]
        self.energy_shield_hp = state["energy_shield_hp"]
        self.carriage_buff = state["carriage_buff"]
        self.vest_used_this_turn = state["vest_used_this_turn"]
        self.rhino_shield_available = state["rhino_shield_available"]
        self.attacked_this_turn = state["attacked_this_turn"]
        self.recalc_stats()

    def save_gunner_snapshot(self):
        """枪手专用：保存完整状态快照（含手牌、冷却、buff）"""
        self.gunner_snapshot = {
            "hp": self.hp,
            "equipment": copy.deepcopy(self.equipment),
            "hand": copy.deepcopy(self.hand),
            "cooldowns": copy.deepcopy(self.cooldowns),
            "poison_turns": self.poison_turns,
            "burn_turns": self.burn_turns,
            "hand_limit_reduction": self.hand_limit_reduction,
            "immune_turn": self.immune_turn,
            "skip_next_turn": self.skip_next_turn,
            "skip_full_turn": self.skip_full_turn,
            "damage_double_turn": self.damage_double_turn,
            "double_attack_left": self.double_attack_left,
            "energy_shield_hp": self.energy_shield_hp,
            "carriage_buff": self.carriage_buff,
            "vest_used_this_turn": self.vest_used_this_turn,
            "rhino_shield_available": self.rhino_shield_available,
        }

    def recalc_stats(self):
        atk_bonus = matk_bonus = max_hp_bonus = 0
        for eq in self.equipment:
            owner_match = (eq.owner == self.char_name)
            if eq.name == "重甲犀牛": max_hp_bonus += 1
            elif eq.name == "脉冲炮": matk_bonus += 1
            elif eq.name == "雷羽弓":
                atk_bonus += 1
                if owner_match: matk_bonus += 1
            elif eq.name == "火焰之刃":
                atk_bonus += 1
                if owner_match: max_hp_bonus += 1
            elif eq.name == "熔岩动力戟":
                if not owner_match: matk_bonus += 1
            elif eq.name == "空间之刃":
                if not owner_match: atk_bonus += 1
            elif eq.name == "寒冰之刃":
                matk_bonus += 1
                if owner_match: max_hp_bonus += 1
            elif eq.name == "剧毒之镰":
                if not owner_match: atk_bonus += 1
            elif eq.name == "创造之墙":
                max_hp_bonus += 2 if owner_match else 1
            elif eq.name == "烟雾掩护":
                if not owner_match: max_hp_bonus += 1

        self.atk = self.base_atk + atk_bonus
        self.matk = self.base_matk + matk_bonus
        self.max_hp = self.base_max_hp + max_hp_bonus
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def equipment_limit(self):
        return 3 if self.char_name == "拾荒者" else 1

    def count_equipment_type(self, eq_type):
        return sum(1 for e in self.equipment if e.equip_type == eq_type)

    def can_equip(self, eq):
        limit = self.equipment_limit()
        if self.char_name == "玖恒": limit += self.extra_slots
        return self.count_equipment_type(eq.equip_type) < limit

    def equip(self, eq):
        self.equipment.append(eq)
        self.recalc_stats()
        print(f"⚙ {self.name} 装备了【{eq.name}】（{eq.equip_type}）")
        print(f"   效果：{eq.desc}")

    def unequip(self, eq):
        if eq in self.equipment:
            self.equipment.remove(eq)
            self.recalc_stats()
            print(f"🔓 {self.name} 卸下了【{eq.name}】")
            return True
        return False

    def has_equipment(self, name):
        return any(e.name == name for e in self.equipment)

    def draw_card(self, card):
        if len(self.hand) < self.get_hand_limit():
            self.hand.append(card)
            return True
        return False

    def show_hand(self):
        limit = self.get_hand_limit()
        print(f"\n{self.name} 的手牌 (HP: {self.hp}/{self.max_hp}, 手牌: {len(self.hand)}/{limit}):")
        for i, card in enumerate(self.hand):
            print(f"  [{i}] {card}")

    def show_equipment(self):
        if not self.equipment:
            print(f"  {self.name} 无装备")
            return
        print(f"  {self.name} 的装备：")
        for i, eq in enumerate(self.equipment):
            print(f"    [{i}] {eq.name}（{eq.equip_type}）")

    def is_alive(self):
        return self.hp > 0

    def show_skills(self):
        print(f"\n{self.name} 的技能:")
        for sid, sk in self.char_data["skills"].items():
            cd_left = self.cooldowns.get(sid, 0)
            status = "就绪" if cd_left == 0 else f"冷却中({cd_left})"
            tag = ""
            if sk["name"] in DODGE_SKILLS: tag = " [受伤时/挡任意伤害]"
            elif sk["name"] in SHIELD_SKILLS: tag = " [受伤时/挡普通或物理]"
            print(f"  [{sid}] {sk['name']} (CD{sk['cd']}) - {status}{tag}")
            print(f"        {sk['desc']}")
        if self.has_equipment("医疗包") and self.char_name != "多斯":
            cd = self.cooldowns.get("急救", 0)
            status = "就绪" if cd == 0 else f"冷却中({cd})"
            print(f"  [急] 【急救】(CD3) - {status}")
            print(f"        恢复自身1点血量（来自医疗包）")

    def reduce_cooldowns(self):
        for sid in self.cooldowns:
            if self.cooldowns[sid] > 0:
                self.cooldowns[sid] -= 1

    def reset_turn_flags(self):
        self.immune_turn = False
        self.damage_double_turn = False
        self.meditate_used_this_turn = False
        self.vest_used_this_turn = False
        self.attacked_this_turn = False

    def on_turn_end(self):
        self.rhino_shield_available = not self.attacked_this_turn
        if self.has_equipment("幽灵马车"):
            self.carriage_buff = True
        self.transfer_active = False
        self.transfer_target = None
        self.extra_attack_tokens = 0

# ==================== 角色选择 ====================
def show_character_list():
    print("\n===== 可选角色 =====")
    for key, ch in CHARACTERS.items():
        print(f"  {key}. {ch['name']}  HP={ch['hp']}  物攻={ch['atk']}  法攻={ch['matk']}")
        print(f"      {ch['desc']}")

def select_character(player_label):
    show_character_list()
    while True:
        choice = input(f"\n请 {player_label} 输入角色编号 (1-12): ").strip()
        if choice in CHARACTERS:
            ch = CHARACTERS[choice]
            print(f"✔ {player_label} 选择了【{ch['name']}】")
            print(f"  被动：{ch['passive']}")
            return Player(name=f"{player_label}-{ch['name']}", hp=ch["hp"], atk=ch["atk"], matk=ch["matk"], char_data=ch)
        else:
            print("无效编号，请重新输入。")

# ==================== 卡组 ====================
def create_deck():
    deck = []
    for _ in range(8):
        deck.append(Card("普攻·直击", "attack", value=1, description="造成1点伤害"))
    for _ in range(4):
        deck.append(Card("普攻·重击", "attack", value=2, description="造成2点伤害"))
    for _ in range(2):
        deck.append(Card("普攻·连击", "attack", value=1, description="1点伤害 + 额外普攻", effect="combo"))
    for _ in range(1):
        deck.append(Card("普攻·快刺", "attack", value=1, description="1点伤害 + 闪避1次", effect="quick"))
    for _ in range(2):
        deck.append(Card("普攻·横扫", "attack", value=1, description="对全体敌人1点", effect="sweep"))
    for _ in range(1):
        deck.append(Card("普攻·牵制", "attack", value=1, description="1点伤害 + 目标下回合CD+1", effect="bind"))
    for _ in range(1):
        deck.append(Card("普攻·破袭", "attack", value=2, description="2点伤害，无视普通护盾", effect="pierce"))
    for _ in range(1):
        deck.append(Card("普攻·浴血", "attack", value=2, description="2点伤害，自身受1点反伤", effect="blood"))

    for _ in range(5):
        deck.append(Card("物理攻击", "physical", description="造成等同物攻的物理伤害"))
    for _ in range(5):
        deck.append(Card("法术攻击", "magic", description="造成等同法攻的法术伤害"))

    for _ in range(10):
        deck.append(Card("疗伤", "heal", value=1, description="恢复1点生命"))

    for _ in range(10):
        deck.append(Card("躲闪", "dodge", description="规避单次伤害"))
    for _ in range(2):
        deck.append(Card("全能盾牌", "omnishield", description="抵挡伤害/死亡/负面效果"))

    for _ in range(3):
        deck.append(Card("狂暴剂", "rage", description="本回合所有伤害翻倍"))
    for _ in range(3):
        deck.append(Card("麻醉剂", "anesthetic", description="敌方跳过下一完整回合"))
    for _ in range(3):
        deck.append(Card("沉思", "meditate", description="立刻抽5张牌（每回合限1张）"))
    for _ in range(7):
        deck.append(Card("拆除", "dismantle", description="拆除敌方1件装备"))
    for _ in range(5):
        deck.append(Card("抢夺", "steal", description="抢夺敌方1件已装备的装备"))

    deck.append(Card("决斗", "duel", description="决斗3轮，无人阵亡则同归于尽"))

    for eq_name in EQUIPMENT_TEMPLATES:
        deck.append(Card(eq_name, "equip", description=EQUIPMENT_TEMPLATES[eq_name]["desc"]))

    random.shuffle(deck)
    return deck

# ==================== 摸牌辅助 ====================
def do_draw(player, deck, count):
    drawn = 0
    for _ in range(count):
        if deck and player.draw_card(deck.pop()):
            drawn += 1
    return drawn

def calc_draw_count(player, is_skipped=False):
    if len(player.hand) == 0:
        return 3, "手牌为空，触发额外摸牌"
    if is_skipped:
        return 1, "被跳过回合，摸牌减少"
    return 2, "正常摸牌"

# ==================== 攻击上限 ====================
def get_attack_limit(player):
    if player.has_equipment("加特林"): return 999
    if player.char_name == "枪手" and player.has_equipment("双枪"): return 3
    return 2

def get_normal_attack_bonus(player):
    bonus = 0
    if player.has_equipment("剑匣"): bonus += 1
    if player.char_name == "利刃" and player.has_equipment("寒冰之刃"): bonus += 1
    if player.char_name == "枪手" and player.has_equipment("双枪"): bonus += 1
    return bonus

def equipment_attack_bonus(attacker):
    extra = 0
    for _ in range(sum(1 for e in attacker.equipment if e.name == "机械猎犬")):
        if random.random() < 1 / 3:
            print("🐕 机械猎犬触发，追加1点伤害！")
            extra += 1
    return extra

# ==================== 伤害防御响应 ====================
def apply_damage(defender, damage, attacker, damage_type="normal", ignore_normal_shield=False):
    if defender.transfer_active and damage_type in ("normal", "physical", "magic"):
        target = defender.transfer_target
        if target and target.is_alive():
            print(f"⚖ {defender.name} 的【罪罚锁狱】触发！{damage} 点伤害转移到 {target.name}！")
            target.hp -= damage
            return 0

    if defender.immune_turn and damage_type == "normal":
        print(f"🛡 {defender.name} 处于【废土壁垒】，免疫本次伤害！")
        return 0

    if damage_type in ("normal", "magic") and defender.carriage_buff:
        damage = max(0, damage - 1)
        defender.carriage_buff = False
        print(f"🐎 幽灵马车效果触发，技能伤害-1！")

    if damage_type == "physical" and defender.has_equipment("防弹背心"):
        if not defender.vest_used_this_turn:
            damage = max(0, damage - 1)
            defender.vest_used_this_turn = True
            print(f"🦺 防弹背心效果触发，物理伤害-1！")

    if defender.has_equipment("重甲犀牛") and defender.rhino_shield_available:
        damage = max(0, damage - 1)
        defender.rhino_shield_available = False
        print(f"🦏 重甲犀牛效果触发，本次伤害-1！")

    for _ in range(sum(1 for e in defender.equipment if e.name == "飞行滑板")):
        if random.random() < 1 / 3:
            print(f"🛹 飞行滑板触发，完全闪避本次伤害！")
            return 0

    if defender.energy_shield_hp > 0:
        absorbed = min(defender.energy_shield_hp, damage)
        defender.energy_shield_hp -= absorbed
        damage -= absorbed
        print(f"⚡ 能量护盾吸收了 {absorbed} 点伤害！（剩余护盾 {defender.energy_shield_hp}）")
        if damage == 0:
            return 0

    options = []

    if defender.dodge_tokens > 0:
        options.append(("token", "dodge_token", f"快刺闪避（剩余 {defender.dodge_tokens} 次）- 规避单次伤害"))

    for sid, sk in defender.char_data["skills"].items():
        name = sk["name"]
        if name in DEFENSE_SKILLS and defender.cooldowns.get(sid, 0) == 0:
            if ignore_normal_shield and name in SHIELD_SKILLS: continue
            if damage_type == "magic" and name in SHIELD_SKILLS: continue
            tag = "规避" if name in DODGE_SKILLS else "护盾"
            options.append(("skill", sid, f"技能【{name}】({tag}) - {sk['desc']}"))

    for i, card in enumerate(defender.hand):
        if card.card_type == "dodge":
            options.append(("card", i, "手牌【躲闪】- 规避单次伤害"))
        elif card.card_type == "omnishield":
            options.append(("card", i, "手牌【全能盾牌】- 抵挡全部伤害"))

    if not options:
        return damage

    print(f"\n⚠ {defender.name} 受到 {damage} 点伤害！可选择防御：")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt[2]}")
    print(f"  [0] 不防御，承受全部伤害")

    while True:
        try:
            choice = int(input("请选择防御方式: ").strip())
            if choice == 0:
                return damage
            if 1 <= choice <= len(options):
                otype, data, _ = options[choice - 1]
                if otype == "token":
                    defender.dodge_tokens -= 1
                    print(f"💨 {defender.name} 使用【快刺闪避】，规避本次伤害！")
                    return 0
                elif otype == "skill":
                    sid = data
                    sk = defender.char_data["skills"][sid]
                    name = sk["name"]
                    if name in DODGE_SKILLS:
                        print(f"💨 {defender.name} 使用【{name}】，规避本次伤害！")
                    elif name == "坚防":
                        print(f"🛡 {defender.name} 使用【{name}】，抵挡伤害并反弹1点给 {attacker.name}！")
                        attacker.hp -= 1
                    else:
                        print(f"🧊 {defender.name} 使用【{name}】，抵挡本次伤害！")
                    if sk["cd"] > 0:
                        defender.cooldowns[sid] = sk["cd"]
                    return 0
                else:
                    card = defender.hand.pop(data)
                    if card.card_type == "dodge":
                        print(f"💨 {defender.name} 使用【躲闪】，规避本次伤害！")
                    else:
                        print(f"🛡 {defender.name} 使用【全能盾牌】，抵挡本次伤害！")
                    return 0
            print("无效选择，请重新输入。")
        except ValueError:
            print("请输入数字。")

# ==================== 负面效果防御 ====================
def try_defend_debuff(defender, debuff_name):
    omni_indices = [i for i, c in enumerate(defender.hand) if c.card_type == "omnishield"]
    if not omni_indices:
        return False
    print(f"\n⚠ {defender.name} 即将被施加负面效果【{debuff_name}】！")
    print(f"  [1] 使用【全能盾牌】抵挡（你有 {len(omni_indices)} 张）")
    print(f"  [0] 不抵挡，承受效果")
    while True:
        try:
            choice = int(input("请选择: ").strip())
            if choice == 0:
                return False
            if choice == 1:
                for i, c in enumerate(defender.hand):
                    if c.card_type == "omnishield":
                        defender.hand.pop(i)
                        print(f"🛡 {defender.name} 使用【全能盾牌】抵挡了【{debuff_name}】！")
                        return True
            print("无效选择。")
        except ValueError:
            print("请输入数字。")

# ==================== 技能执行 ====================
def use_skill(user, opponent, skill_id):
    if skill_id == "急救":
        if not (user.has_equipment("医疗包") and user.char_name != "多斯"):
            print("没有这个技能。")
            return False
        if user.cooldowns.get("急救", 0) > 0:
            print("【急救】还在冷却中！")
            return False
        user.hp = min(user.max_hp, user.hp + 1)
        user.cooldowns["急救"] = 3
        print(f"💚 {user.name} 使用【急救】，回复1点血量！")
        return True

    if skill_id not in user.char_data["skills"]:
        print("没有这个技能。")
        return False
    if user.cooldowns.get(skill_id, 0) > 0:
        print(f"【{user.char_data['skills'][skill_id]['name']}】还在冷却中！")
        return False

    sk = user.char_data["skills"][skill_id]
    name = sk["name"]

    if name in DEFENSE_SKILLS:
        print(f"⚠ 【{name}】只能在受到伤害时使用！")
        return False

    # ============ 拾荒者 ============
    if name == "劫掠":
        if len(user.hand) < 3:
            print("需要至少3张手牌才能使用【劫掠】！")
            return False
        user.hand.pop(); user.hand.pop()
        if opponent.equipment:
            stolen = opponent.equipment.pop(random.randint(0, len(opponent.equipment) - 1))
            opponent.recalc_stats()
            if user.can_equip(stolen):
                user.equip(stolen)
                print(f"🪝 {user.name} 使用【劫掠】，抢走了 {opponent.name} 的【{stolen.name}】！")
            else:
                print(f"🪝 {user.name} 使用【劫掠】，抢到【{stolen.name}】但装备栏已满，效果消散。")
        elif opponent.hand:
            stolen = opponent.hand.pop(random.randint(0, len(opponent.hand) - 1))
            user.hand.append(stolen)
            print(f"🪝 {user.name} 使用【劫掠】，偷走了 {opponent.name} 的 1 张手牌！")
        else:
            print(f"🪝 {user.name} 使用【劫掠】，但对手无手牌无装备，失败。")
    elif name == "废土壁垒":
        user.immune_turn = True
        print(f"🛡 {user.name} 开启【废土壁垒】，本回合免疫普通攻击和技能伤害！")

    # ============ 毒猎 ============
    elif name == "噬血":
        opponent.hp -= 1
        user.hp = min(user.max_hp, user.hp + 1)
        print(f"🩸 {user.name} 使用【噬血】，偷取 {opponent.name} 1点生命！")
    elif name == "猎击":
        dmg = apply_damage(opponent, 2, user, "normal")
        opponent.hp -= dmg
        print(f"🏹 {user.name} 使用【猎击】，造成 {dmg} 点技能伤害！")
    elif name == "腐毒侵蚀":
        if try_defend_debuff(opponent, "腐毒侵蚀"):
            print(f"（{user.name} 的【腐毒侵蚀】被抵消）")
        else:
            opponent.poison_turns = 3
            if opponent.hand_limit_reduction < 1:
                opponent.hand_limit_reduction = 1
                print(f"☠ {user.name} 对 {opponent.name} 施加【腐毒侵蚀】，持续3回合！")
                print(f"   {opponent.name} 手牌上限永久-1（当前上限 {opponent.get_hand_limit()}）")
            else:
                print(f"☠ {user.name} 对 {opponent.name} 施加【腐毒侵蚀】，持续3回合！")

    # ============ 罗伊 ============
    elif name == "速击":
        dmg = apply_damage(opponent, 1, user, "normal")
        opponent.hp -= dmg
        print(f"⚡ {user.name} 使用【速击】，造成 {dmg} 点技能伤害！")
    elif name == "坚韧蜕变":
        user.base_max_hp += 1
        user.base_atk += 1
        user.recalc_stats()
        print(f"💪 {user.name} 使用【坚韧蜕变】，永久+1血量上限，+1物攻！")

    # ============ 吕山 ============
    elif name == "电击眩晕":
        opponent.skip_next_turn = True
        print(f"⚡ {user.name} 使用【电击眩晕】，{opponent.name} 下回合跳过出牌阶段！")
    elif name == "狂击增幅":
        user.double_attack_left = 2
        print(f"🔥 {user.name} 使用【狂击增幅】，下2张攻击手牌伤害翻倍！")

    # ============ 钟离 ============
    elif name == "固本":
        user.hp = min(user.max_hp, user.hp + 1)
        print(f"💚 {user.name} 使用【固本】，回复1点血量！")
    elif name == "剑击":
        dmg = apply_damage(opponent, 2, user, "normal")
        opponent.hp -= dmg
        print(f"⚔ {user.name} 使用【剑击】，造成 {dmg} 点技能伤害！")
    elif name == "火焰灼烧":
        dmg = apply_damage(opponent, 2, user, "normal")
        opponent.hp -= dmg
        print(f"🔥 {user.name} 使用【火焰灼烧】，对 {opponent.name} 造成 {dmg} 点群体技能伤害！")

    # ============ 利刃 ============
    elif name == "突刺":
        dmg = apply_damage(opponent, 1, user, "normal")
        opponent.hp -= dmg
        print(f"🗡 {user.name} 使用【突刺】，造成 {dmg} 点技能伤害！")
    elif name == "寒冰增幅":
        user.base_atk += 1
        user.base_matk += 1
        user.recalc_stats()
        print(f"❄ {user.name} 使用【寒冰增幅】，永久+1物攻，+1法攻！")

    # ============ 枪手：完整回溯 ============
    elif name == "迟滞弹":
        for sid in opponent.cooldowns:
            if opponent.cooldowns[sid] > 0:
                opponent.cooldowns[sid] += 2
        print(f"🔫 {user.name} 使用【迟滞弹】，{opponent.name} 冷却中技能CD+2！")
    elif name == "禁锢射击":
        opponent.skip_next_turn = True
        print(f"🔒 {user.name} 使用【禁锢射击】，{opponent.name} 下回合跳过出牌阶段！")
    elif name == "时空回溯":
        snap = user.gunner_snapshot
        if snap is None:
            print("【时空回溯】暂时没有可回溯的状态！")
            return False
        old_hp = user.hp
        old_eq = len(user.equipment)
        old_hand = len(user.hand)
        user.hp = snap["hp"]
        user.equipment = copy.deepcopy(snap["equipment"])
        user.hand = copy.deepcopy(snap["hand"])
        user.cooldowns = copy.deepcopy(snap["cooldowns"])
        user.poison_turns = snap["poison_turns"]
        user.burn_turns = snap["burn_turns"]
        user.hand_limit_reduction = snap["hand_limit_reduction"]
        user.immune_turn = snap["immune_turn"]
        user.skip_next_turn = snap["skip_next_turn"]
        user.skip_full_turn = snap["skip_full_turn"]
        user.damage_double_turn = snap["damage_double_turn"]
        user.double_attack_left = snap["double_attack_left"]
        user.energy_shield_hp = snap["energy_shield_hp"]
        user.carriage_buff = snap["carriage_buff"]
        user.vest_used_this_turn = snap["vest_used_this_turn"]
        user.rhino_shield_available = snap["rhino_shield_available"]
        user.recalc_stats()
        print(f"⏰ {user.name} 使用【时空回溯】！完整回溯到上回合结束时的状态：")
        print(f"   血量 {old_hp} → {user.hp}")
        print(f"   装备 {old_eq} 件 → {len(user.equipment)} 件")
        print(f"   手牌 {old_hand} 张 → {len(user.hand)} 张")
        print(f"   技能冷却、中毒/灼烧等状态均已回溯")

    # ============ 帝郡 ============
    elif name == "焚身灼烧":
        if try_defend_debuff(opponent, "焚身灼烧"):
            print(f"（{user.name} 的【焚身灼烧】被抵消）")
        else:
            turns = 3
            if user.char_name == "帝郡" and user.has_equipment("熔岩动力戟"):
                turns = 5
                print("🌋 熔岩动力戟效果：灼烧时长延长至5回合！")
            opponent.burn_turns = turns
            print(f"🔥 {user.name} 对 {opponent.name} 施加【焚身灼烧】，持续{turns}回合！")
    elif name == "罪罚锁狱":
        user.transfer_active = True
        user.transfer_target = opponent
        print(f"⚖ {user.name} 使用【罪罚锁狱】，本回合受到的伤害全部转移给 {opponent.name}！")

    # ============ 冷锋 ============
    elif name == "激光":
        dmg = apply_damage(opponent, 1, user, "magic")
        opponent.hp -= dmg
        print(f"🔵 {user.name} 使用【激光】，造成 {dmg} 点法术技能伤害！")
    elif name == "浮游炮":
        dmg = apply_damage(opponent, 3, user, "magic")
        opponent.hp -= dmg
        print(f"💥 {user.name} 使用【浮游炮】，造成 {dmg} 点法术技能伤害！")

    # ============ 秦默 ============
    elif name == "傀儡术":
        if not opponent.hand:
            print("⚠ 对手没有手牌，无法使用【傀儡术】！")
            return False
        print(f"\n{opponent.name} 的手牌：")
        for i, c in enumerate(opponent.hand):
            print(f"  [{i}] {c}")
        try:
            sel = int(input("选择要借用的手牌编号（-1取消）: ").strip())
            if sel == -1:
                return False
            if 0 <= sel < len(opponent.hand):
                stolen_card = opponent.hand[sel]
                print(f"🎭 {user.name} 使用【傀儡术】，借用了【{stolen_card.name}】！")
                if stolen_card.card_type == 'attack':
                    dmg = apply_damage(opponent, stolen_card.value + get_normal_attack_bonus(user), user, "normal")
                    opponent.hp -= dmg
                    print(f"   对 {opponent.name} 造成 {dmg} 点普攻伤害！")
                elif stolen_card.card_type == 'physical':
                    dmg = apply_damage(opponent, opponent.atk, user, "physical")
                    opponent.hp -= dmg
                    print(f"   对 {opponent.name} 造成 {dmg} 点物理伤害！")
                elif stolen_card.card_type == 'magic':
                    dmg = apply_damage(opponent, opponent.matk, user, "magic")
                    opponent.hp -= dmg
                    print(f"   对 {opponent.name} 造成 {dmg} 点法术伤害！")
                elif stolen_card.card_type == 'heal':
                    user.hp = min(user.max_hp, user.hp + stolen_card.value)
                    print(f"   {user.name} 回复了 {stolen_card.value} 点生命！")
                else:
                    print("   该牌无法通过傀儡术使用。")
                    return False
                print("   （该牌仍属于对手）")
            else:
                print("无效编号。")
                return False
        except ValueError:
            print("请输入数字。")
            return False
    elif name == "锐击":
        dmg = apply_damage(opponent, 2, user, "normal")
        opponent.hp -= dmg
        print(f"⚔ {user.name} 使用【锐击】，造成 {dmg} 点技能伤害！")
    elif name == "复生献祭":
        print("【复生献祭】为阵亡时自动触发，无需主动使用！")
        return False

    # ============ 玖恒 ============
    elif name == "拓械":
        if user.extra_slots >= 3:
            print("已达到额外装备槽上限（3个）！")
            return False
        if len(user.hand) < 2:
            print("需要至少2张手牌才能使用【拓械】！")
            return False
        user.hand.pop(); user.hand.pop()
        user.extra_slots += 1
        print(f"⚙ {user.name} 使用【拓械】，获得1个额外装备槽！（当前：{user.extra_slots}/3）")
    elif name == "锁滞":
        opponent.skip_next_turn = True
        print(f"🔗 {user.name} 使用【锁滞】，{opponent.name} 下回合跳过出牌阶段！")
    elif name == "战威增幅":
        user.damage_double_turn = True
        print(f"⚡ {user.name} 使用【战威增幅】，本回合自身所有伤害翻倍（上限2倍）！")

    # ============ 多斯 ============
    elif name == "愈护":
        user.hp = min(user.max_hp, user.hp + 1)
        print(f"💚 {user.name} 使用【愈护】，回复1点血量！")
    elif name == "速愈调度":
        if "1" in user.cooldowns:
            user.cooldowns["1"] = max(0, user.cooldowns["1"] - 2)
        print(f"⏩ {user.name} 使用【速愈调度】，一技能CD-2！")
    elif name == "复生仪式":
        print("【复生仪式】为阵亡时自动触发，无需主动使用！")
        return False

    else:
        print(f"技能【{name}】暂未实现。")
        return False

    cd = sk["cd"]
    if name == "激光" and user.char_name == "冷锋" and user.has_equipment("脉冲炮"):
        cd = max(0, cd - 1)
        print("🔫 脉冲炮效果：激光CD-1！")
    if name == "愈护" and user.char_name == "多斯" and user.has_equipment("医疗包"):
        cd = max(0, cd - 2)
        print("💊 医疗包效果：愈护CD-2！")
    if name == "废土壁垒" and user.char_name == "拾荒者" and user.has_equipment("烟雾掩护"):
        cd = max(0, cd - 1)
        print("💨 烟雾掩护效果：废土壁垒CD-1！")

    if cd > 0:
        user.cooldowns[skill_id] = cd
    return True

# ==================== 回合开始处理 ====================
def on_turn_start(player):
    if player.cd_penalty > 0:
        for sid in player.cooldowns:
            if player.cooldowns[sid] > 0:
                player.cooldowns[sid] += player.cd_penalty
        print(f"⏱ {player.name} 受到【牵制】影响，冷却中技能 CD+{player.cd_penalty}！")
        player.cd_penalty = 0

    if player.char_name == "多斯":
        player.hp = min(player.max_hp, player.hp + 1)
        print(f"✨ 多斯被动【愈愈光环】触发，{player.name} 回复1点血量！")

    if player.poison_turns > 0:
        player.hp -= 1
        player.poison_turns -= 1
        print(f"☠ {player.name} 受到毒素伤害，掉1点血！（剩余{player.poison_turns}回合）")

    if player.burn_turns > 0:
        player.hp -= 1
        player.burn_turns -= 1
        print(f"🔥 {player.name} 受到灼烧伤害，掉1点血！（剩余{player.burn_turns}回合）")

    if player.has_equipment("能量护盾") and player.energy_shield_hp == 0:
        player.energy_shield_hp = 1
        print(f"⚡ 能量护盾恢复1点护盾！")

# ==================== 复活检查 ====================
def try_revive(player):
    if player.hp > 0:
        return True

    if player.char_name == "秦默":
        if player.revive_count >= 2:
            print(f"💀 {player.name} 的【复生献祭】次数已用尽（最多 2 次）！")
            return False
        cost = 5 if player.revive_count == 0 else 10
        if len(player.hand) < cost:
            print(f"💀 {player.name} 的【复生献祭】需要 {cost} 张手牌，手牌不足！")
            return False
        for _ in range(cost):
            player.hand.pop()
        player.hp = player.max_hp
        player.revive_count += 1
        print(f"✨ {player.name} 使用【复生献祭】复活！消耗 {cost} 张手牌，恢复满血！")
        print(f"   （已复活 {player.revive_count}/2 次）")
        return True

    if player.char_name == "多斯":
        cd = player.cooldowns.get("3", 0)
        if cd == 0 and player.revive_count < 1:
            player.hp = player.max_hp
            player.revive_count += 1
            player.cooldowns["3"] = 8
            print(f"✨ {player.name} 使用【复生仪式】自动复活！恢复满血！")
            return True
        else:
            print(f"💀 {player.name} 的【复生仪式】已用过或还在冷却中！")
            return False

    return False

# ==================== 决斗死亡处理 ====================
def trigger_duel_death(player):
    for i, c in enumerate(player.hand):
        if c.card_type == "omnishield":
            print(f"\n⚠ {player.name} 即将因决斗阵亡！你有【全能盾牌】可以抵消。")
            try:
                choice = input(f"是否使用【全能盾牌】抵消死亡？(y/n): ").strip().lower()
            except Exception:
                choice = 'n'
            if choice == 'y':
                player.hand.pop(i)
                print(f"🛡 {player.name} 使用【全能盾牌】抵消了决斗死亡！")
                return False
    player.hp = 0
    print(f"💀 {player.name} 因决斗阵亡！")
    return True

# ==================== 出牌处理 ====================
def play_attack_card(current_player, opponent, card, damage_type, base_damage, ignore_normal_shield=False):
    damage = base_damage
    if card.card_type == 'attack':
        damage += get_normal_attack_bonus(current_player)

    if current_player.double_attack_left > 0:
        damage *= 2
        current_player.double_attack_left -= 1
        print("🔥 狂击增幅触发，伤害翻倍！")
    if current_player.damage_double_turn:
        damage *= 2
        print("⚡ 战威增幅/狂暴剂触发，伤害翻倍！")

    damage += equipment_attack_bonus(current_player)

    actual = apply_damage(opponent, damage, current_player, damage_type, ignore_normal_shield=ignore_normal_shield)
    opponent.hp -= actual
    if actual > 0:
        type_name = {"normal": "", "physical": "物理", "magic": "法术"}[damage_type]
        print(f"{current_player.name} 对 {opponent.name} 造成 {actual} 点{type_name}伤害！")
    return actual

def do_steal(current_player, opponent):
    if not opponent.equipment:
        print("⚠ 对方没有装备！")
        return False
    print(f"\n对方的装备：")
    for i, eq in enumerate(opponent.equipment):
        print(f"  [{i}] {eq.name}（{eq.equip_type}）- {eq.desc}")
    while True:
        try:
            choice = int(input("请选择要抢夺的装备编号（-1取消）: ").strip())
            if choice == -1:
                return False
            if 0 <= choice < len(opponent.equipment):
                eq = opponent.equipment[choice]
                if not current_player.can_equip(eq):
                    limit = current_player.equipment_limit() + (current_player.extra_slots if current_player.char_name == "玖恒" else 0)
                    print(f"⚠ 你的 {eq.equip_type} 装备栏已满（上限{limit}件），无法抢夺！")
                    return False
                opponent.equipment.remove(eq)
                opponent.recalc_stats()
                current_player.equip(eq)
                print(f"🎯 {current_player.name} 使用【抢夺】，抢走了 {opponent.name} 的【{eq.name}】！")
                if eq.name == "能量护盾":
                    current_player.energy_shield_hp = 1
                    print("  ⚡ 能量护盾：立即获得1点护盾！")
                return True
            print("无效编号。")
        except ValueError:
            print("请输入数字。")

def do_unequip(current_player):
    if not current_player.equipment:
        print("⚠ 你没有任何装备！")
        return False
    print(f"\n你的装备：")
    for i, eq in enumerate(current_player.equipment):
        print(f"  [{i}] {eq.name}（{eq.equip_type}）- {eq.desc}")
    while True:
        try:
            choice = int(input("请选择要卸下的装备编号（-1取消）: ").strip())
            if choice == -1:
                return False
            if 0 <= choice < len(current_player.equipment):
                eq = current_player.equipment[choice]
                current_player.unequip(eq)
                return True
            print("无效编号。")
        except ValueError:
            print("请输入数字。")

# ==================== 游戏主循环 ====================
def game_loop():
    print("====== 火柴杀 ======")
    print("开始选择角色：")

    p1 = select_character("玩家1")
    p2 = select_character("玩家2")

    deck = create_deck()
    for _ in range(3):
        p1.draw_card(deck.pop())
        p2.draw_card(deck.pop())

    current_player = p1
    opponent = p2
    turn = 1
    duel_active = False

    while True:
        if not p1.is_alive() or not p2.is_alive():
            break

        print(f"\n--- 第{turn}回合 ---")
        print(f"{current_player.name} 的回合 (HP: {current_player.hp}/{current_player.max_hp})")
        print(f"  物攻: {current_player.atk}  法攻: {current_player.matk}  装备数: {len(current_player.equipment)}")

        if turn > 1:
            p1.prev_state = p1.get_state_snapshot()
            p2.prev_state = p2.get_state_snapshot()

        # 跳过整回合
        if current_player.skip_full_turn:
            print(f"💉 {current_player.name} 被【麻醉剂】麻醉，跳过整个回合！")
            current_player.skip_full_turn = False
            count, reason = calc_draw_count(current_player, is_skipped=True)
            if deck:
                drawn = do_draw(current_player, deck, count)
                print(f"💫 {current_player.name} 摸了 {drawn} 张牌。")
            current_player.reduce_cooldowns()
            current_player.on_turn_end()
            # 枪手保存快照
            if current_player.char_name == "枪手":
                current_player.save_gunner_snapshot()
            current_player, opponent = opponent, current_player
            turn += 1
            continue

        # 回合开始
        current_player.reset_turn_flags()
        on_turn_start(current_player)
        if not current_player.is_alive():
            if try_revive(current_player):
                pass
            else:
                print(f"\n💀 {current_player.name} 阵亡！{opponent.name} 获胜！")
                return

        # 摸牌
        is_skipped = current_player.skip_next_turn
        count, reason = calc_draw_count(current_player, is_skipped=is_skipped)
        if reason != "正常摸牌":
            print(f"💫 {current_player.name} {reason}！")
        if deck:
            drawn = do_draw(current_player, deck, count)
            print(f"{current_player.name} 摸了 {drawn} 张牌。")
        else:
            print("牌堆已空。")

        # 跳过出牌阶段
        if current_player.skip_next_turn:
            print(f"⛔ {current_player.name} 跳过本回合出牌阶段！")
            current_player.skip_next_turn = False
            current_player.reduce_cooldowns()
            current_player.on_turn_end()
            if current_player.char_name == "枪手":
                current_player.save_gunner_snapshot()
            current_player, opponent = opponent, current_player
            turn += 1
            continue

        # 出牌阶段
        attack_limit = get_attack_limit(current_player)
        attack_cards_used = 0
        if attack_limit < 999:
            print(f"（本回合攻击手牌上限：{attack_limit} 张）")

        while True:
            current_player.show_hand()
            current_player.show_equipment()
            print("提示：输入 u 可卸下自己的装备")
            action = input("请选择: 牌序号出牌 | 's'技能 | 'u'卸装备 | 'end'结束回合: ").strip()

            if action.lower() == 'end':
                break

            if action.lower() == 'u':
                do_unequip(current_player)
                continue

            if action.lower() == 's':
                current_player.show_skills()
                sk_choice = input("输入技能编号使用（或'急'用急救），'back'返回: ").strip()
                if sk_choice == 'back':
                    continue
                if sk_choice == '急' or sk_choice == "急救":
                    use_skill(current_player, opponent, "急救")
                    continue
                if sk_choice in current_player.char_data["skills"]:
                    use_skill(current_player, opponent, sk_choice)
                    if not opponent.is_alive():
                        if try_revive(opponent):
                            pass
                        else:
                            print(f"\n💀 {opponent.name} 阵亡！{current_player.name} 获胜！")
                            return
                else:
                    print("无效技能编号。")
                continue

            try:
                idx = int(action)
                if 0 <= idx < len(current_player.hand):
                    card = current_player.hand[idx]

                    if card.card_type in ('attack', 'physical', 'magic'):
                        is_extra_attack = False
                        if current_player.extra_attack_tokens > 0 and card.card_type == 'attack' and attack_cards_used >= attack_limit:
                            is_extra_attack = True
                            current_player.extra_attack_tokens -= 1
                            print("🔄 使用【连击】的额外普攻机会！")

                        if not is_extra_attack and attack_cards_used >= attack_limit:
                            print(f"本回合最多只能使用{attack_limit}张攻击手牌！")
                            continue

                        ignore_shield = (card.effect == "pierce")

                        if card.card_type == 'attack':
                            actual = play_attack_card(current_player, opponent, card, "normal", card.value, ignore_normal_shield=ignore_shield)
                        elif card.card_type == 'physical':
                            actual = play_attack_card(current_player, opponent, card, "physical", current_player.atk)
                        elif card.card_type == 'magic':
                            actual = play_attack_card(current_player, opponent, card, "magic", current_player.matk)

                        if card.effect == "combo":
                            current_player.extra_attack_tokens += 1
                            print("🔄 【连击】：获得 1 次额外普攻机会！")
                        elif card.effect == "quick":
                            current_player.dodge_tokens += 1
                            print("💨 【快刺】：获得 1 次闪避！")
                        elif card.effect == "sweep":
                            print("🌪 【横扫】：对全体敌人造成伤害（1v1 已对对手造成）")
                        elif card.effect == "bind":
                            opponent.cd_penalty += 1
                            print("⏱ 【牵制】：对手下回合冷却中的技能 CD+1！")
                        elif card.effect == "blood":
                            current_player.hp -= 1
                            print("🩸 【浴血】：自身受到 1 点反伤！")

                        current_player.hand.pop(idx)
                        attack_cards_used += 1
                        current_player.attacked_this_turn = True

                    elif card.card_type == 'heal':
                        heal_amount = card.value
                        current_player.hp = min(current_player.max_hp, current_player.hp + heal_amount)
                        print(f"{current_player.name} 恢复了 {heal_amount} 点生命。")
                        current_player.hand.pop(idx)

                    elif card.card_type == 'rage':
                        current_player.damage_double_turn = True
                        print(f"🔥 {current_player.name} 使用【狂暴剂】，本回合所有伤害翻倍！")
                        current_player.hand.pop(idx)

                    elif card.card_type == 'anesthetic':
                        if opponent.skip_full_turn:
                            print("⚠ 目标已被麻醉，不能连续使用！")
                            continue
                        opponent.skip_full_turn = True
                        print(f"💉 {current_player.name} 对 {opponent.name} 使用【麻醉剂】！")
                        current_player.hand.pop(idx)

                    elif card.card_type == 'meditate':
                        if current_player.meditate_used_this_turn:
                            print("⚠ 本回合已经使用过【沉思】了！")
                            continue
                        current_player.meditate_used_this_turn = True
                        current_player.hand.pop(idx)
                        drawn = do_draw(current_player, deck, 5)
                        print(f"📖 {current_player.name} 使用【沉思】，抽取了 {drawn} 张牌！")

                    elif card.card_type == 'dismantle':
                        if not opponent.equipment:
                            print("⚠ 对方没有装备！")
                            continue
                        print(f"\n对方的装备：")
                        for i, eq in enumerate(opponent.equipment):
                            print(f"  [{i}] {eq.name}（{eq.equip_type}）")
                        try:
                            sel = int(input("选择要拆除的装备编号（-1取消）: ").strip())
                            if sel == -1:
                                continue
                            if 0 <= sel < len(opponent.equipment):
                                removed = opponent.equipment.pop(sel)
                                opponent.recalc_stats()
                                print(f"🔨 {current_player.name} 使用【拆除】，拆除了 {opponent.name} 的【{removed.name}】！")
                                current_player.hand.pop(idx)
                            else:
                                print("无效编号。")
                        except ValueError:
                            print("请输入数字。")

                    elif card.card_type == 'steal':
                        if not opponent.equipment:
                            print("⚠ 对方没有装备，无法使用【抢夺】！")
                            continue
                        success = do_steal(current_player, opponent)
                        if success:
                            current_player.hand.pop(idx)

                    elif card.card_type == 'duel':
                        if duel_active:
                            print("⚠ 已经有决斗在进行中！")
                            continue
                        current_player.duel_turns = 3
                        opponent.duel_turns = 3
                        duel_active = True
                        print(f"⚔ {current_player.name} 对 {opponent.name} 发起【决斗】！")
                        current_player.hand.pop(idx)

                    elif card.card_type == 'equip':
                        eq_name = card.name
                        eq = Equipment(eq_name)
                        if not current_player.can_equip(eq):
                            limit = current_player.equipment_limit() + (current_player.extra_slots if current_player.char_name == "玖恒" else 0)
                            print(f"⚠ {eq.equip_type} 装备栏已满（上限{limit}件）！")
                            print(f"   提示：可输入 u 卸下旧装备，或使用【拆除】/【抢夺】处理")
                            continue
                        current_player.hand.pop(idx)
                        current_player.equip(eq)
                        if eq.name == "能量护盾":
                            current_player.energy_shield_hp = 1
                            print("  ⚡ 能量护盾：立即获得1点护盾！")

                    elif card.card_type in ('dodge', 'omnishield'):
                        print(f"⚠ 【{card.name}】只能在受到伤害/负面效果时使用！")
                    else:
                        print("这张牌暂时无法使用。")
                else:
                    print("无效的牌序号。")
            except ValueError:
                print("请输入数字、's'、'u'或'end'。")

            if not opponent.is_alive():
                if try_revive(opponent):
                    pass
                else:
                    print(f"\n💀 {opponent.name} 阵亡！{current_player.name} 获胜！")
                    return

        # 回合结束
        current_player.reduce_cooldowns()
        current_player.on_turn_end()

        # 枪手：回合结束时保存完整快照
        if current_player.char_name == "枪手":
            current_player.save_gunner_snapshot()
            print(f"📸 {current_player.name} 保存回合快照（用于下次【时空回溯】）")

        if duel_active and current_player.duel_turns > 0:
            current_player.duel_turns -= 1
            print(f"⚔ 决斗计数器（{current_player.name}）：剩余 {current_player.duel_turns} 轮")

        if duel_active and p1.duel_turns == 0 and p2.duel_turns == 0:
            print("\n⚔⚔⚔ 决斗3轮已到，无人阵亡，双方同归于尽！")
            duel_active = False
            p1_dead = trigger_duel_death(p1)
            p2_dead = trigger_duel_death(p2)
            if p1_dead and p2_dead:
                print("\n💀💀 双方同时阵亡！平局！")
                return
            elif p1_dead:
                print(f"\n💀 {p1.name} 阵亡！{p2.name} 获胜！")
                return
            elif p2_dead:
                print(f"\n💀 {p2.name} 阵亡！{p1.name} 获胜！")
                return
            else:
                print("\n⚔ 双方都用【全能盾牌】抵消了决斗死亡，游戏继续！")

        current_player, opponent = opponent, current_player
        turn += 1

if __name__ == "__main__":
    game_loop()
