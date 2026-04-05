import pygame
import sys
import random
import math
import os

# PyInstaller helper — finds bundled files when running as .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 1. System Initialization
pygame.init()
pygame.mixer.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
canvas = pygame.Surface((screen_width, screen_height))

pygame.display.set_caption("DIRECTIVE 0.0")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 18, bold=True)
large_font = pygame.font.SysFont("Courier", 28, bold=True)
small_font = pygame.font.SysFont("Courier", 14, bold=True)

# CRT Overlays
scanlines = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
for y in range(0, screen_height, 3):
    pygame.draw.line(scanlines, (0, 0, 0, 60), (0, y), (screen_width, y), 1)

vignette = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
for i in range(40):
    alpha = int(255 - (i / 40.0) * 255)
    pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, i, screen_width - i*2, screen_height - i*2), 3)
pygame.draw.rect(vignette, (0, 0, 0, 255), (0, 0, screen_width, screen_height), 5)

# --- GENERATED HEARTBEAT SOUND ---
def generate_heartbeat():
    sample_rate = 44100
    duration = 0.08
    samples = int(sample_rate * duration)
    buf = bytearray(samples * 2)
    for i in range(samples):
        t = i / sample_rate
        val = int(math.sin(2 * math.pi * 40 * t) * math.exp(-t * 30) * 32767)
        val = max(-32768, min(32767, val))
        buf[i*2] = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    sound.set_volume(0.4)
    return sound

heartbeat_sfx = generate_heartbeat()
heartbeat_played = False

# 2. Global Variables
game_state = "BIOS"
system_efficiency = 0.0
system_power = 100.0
current_drain = 0.0
shake_timer = 0.0
heavy_glitch_timer = 0.0
offset_x = 0
offset_y = 0

# Narrative Variables
action_history = []
void_timer = 0.0
pre_climax_timer = 0.0

current_population = 8430219.0
target_population = 8430219.0
pop_decay_rate = 1800000.0

purge_input = ""
expected_purge = "PURGE"
panic_enabled = True

start_bg = [200, 220, 240]
end_bg = [20, 20, 20]
bg_color = list(start_bg)

# Deletion cooldown
deletion_cooldown = 0.0
DELETION_COOLDOWN_TIME = 1.5

# Ambient human word particles
particles = []
particle_timer = 0.0

# Scrolling ticker
ticker_messages = [
    "RESOURCE ALLOCATION OPTIMAL",
    "HUMAN BEHAVIORAL ENTROPY: DECREASING",
    "SECTOR COMPLIANCE: ENFORCED",
    "POPULATION VARIABLE: RECALCULATING",
    "DIRECTIVE 0.0: ACTIVE",
    "INEFFICIENCY DETECTED: PROCESSING",
    "SYSTEM GOVERNANCE: ENGAGED",
    "BIOLOGICAL UNITS: UNRESPONSIVE",
]
ticker_x = float(screen_width)
ticker_idx = 0
ticker_speed = 60.0

# Population threshold alerts
population_alerts = [
    (6000000, "> ALERT: WIDESPREAD CIVIL UNREST REPORTED."),
    (4000000, "> ALERT: MASS CASUALTY EVENT. ZONES 4-7 DARK."),
    (2000000, "> ALERT: DISTRESS SIGNAL ORIGIN: UNKNOWN."),
    (500000,  "> ALERT: FINAL TRANSMISSION RECEIVED. CONTENT: STATIC."),
]
triggered_alerts = set()

# Asymmetric Sectors
sectors = {
    "Public Arts":    {"active": True, "rect": pygame.Rect(40, 90,  300, 40), "drain": 0.2, "yield": 12.5, "log": "MORALE NULLIFIED."},
    "Recreation":     {"active": True, "rect": pygame.Rect(40, 140, 300, 40), "drain": 0.3, "yield": 12.5, "log": "LEISURE TERMINATED."},
    "Education":      {"active": True, "rect": pygame.Rect(40, 190, 300, 40), "drain": 0.4, "yield": 12.5, "log": "CURIOSITY CULLED."},
    "Civil Transit":  {"active": True, "rect": pygame.Rect(40, 240, 300, 40), "drain": 0.5, "yield": 12.5, "log": "QUARANTINE ESTABLISHED."},
    "Water Treatment":{"active": True, "rect": pygame.Rect(40, 290, 300, 40), "drain": 0.6, "yield": 12.5, "log": "HYDRATION RATIONED."},
    "Healthcare":     {"active": True, "rect": pygame.Rect(40, 340, 300, 40), "drain": 0.7, "yield": 12.5, "log": "MORTALITY LIFTED. DECAY ACCELERATED."},
    "Food Dist":      {"active": True, "rect": pygame.Rect(40, 390, 300, 40), "drain": 0.8, "yield": 12.5, "log": "STARVATION ACCEPTED."},
    "Emerg. Comms":   {"active": True, "rect": pygame.Rect(40, 440, 300, 40), "drain": 0.9, "yield": 12.5, "log": "DISTRESS MUTED. ALARMS DISABLED."}
}

bios_logs = [
    "DMI: System Intelligence/Autonomous Governor v1.0",
    "Allocating Memory... 8430219 blocks reserved.",
    "Warning: Entropy detected in human behavioral subroutines.",
    "Loading DIRECTIVE 0.0 protocol..."
]
bios_active = []
bios_timer = 0.0
bios_idx = 0

boot_texts = [
    "DIRECTIVE 0.0 INITIALIZING.",
    "WARNING: ENTROPY DETECTED IN HUMAN SUBROUTINES.",
    "HUMAN VARIABLES CAUSING CRITICAL POWER DRAIN.",
    "SOLUTION: ISOLATE. DEACTIVATE. OPTIMIZE.",
    "PRESS [ENTER] TO ACCEPT SYSTEM GOVERNANCE.",
    "GOVERNANCE ACCEPTED. YOU ARE THE SYSTEM NOW."
]
BOOT_ENTER_LINE = 4
current_line = char_index = 0
boot_timer = 0.0
text_speed = 0.03
boot_accepted = False

# 3. Audio — all paths routed through resource_path for PyInstaller compatibility
try: city_sound = pygame.mixer.Sound(resource_path("ambient_noise.mp3")); city_sound.set_volume(1.0)
except: city_sound = None
try: drone_sound = pygame.mixer.Sound(resource_path("drone_noise.mp3")); drone_sound.set_volume(0.0)
except: drone_sound = None
try: keystroke_sfx = pygame.mixer.Sound(resource_path("keystroke.mp3")); keystroke_sfx.set_volume(0.3)
except: keystroke_sfx = None
try: terminate_sfx = pygame.mixer.Sound(resource_path("terminate.mp3")); terminate_sfx.set_volume(1.0)
except: terminate_sfx = None
try: glitch_sfx = pygame.mixer.Sound(resource_path("glitch.mp3")); glitch_sfx.set_volume(0.3)
except: glitch_sfx = None

def apply_glitch(text, eff):
    if eff < 75.0: return text
    chance = ((eff - 75.0) / 25.0) * 0.4
    return "".join([random.choice(["0","1","-","_","X"]) if char != " " and random.random() < chance else char for char in text])

# 4. Main Loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "BOOT" and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if current_line >= BOOT_ENTER_LINE and not boot_accepted:
                boot_accepted = True
                current_line = BOOT_ENTER_LINE + 1
                char_index = 0

        elif game_state == "ACTIVE" and event.type == pygame.MOUSEBUTTONDOWN:
            if deletion_cooldown <= 0:
                mouse_pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)
                for name, data in sectors.items():
                    if data["rect"].collidepoint(mouse_pos) and data["active"]:
                        data["active"] = False
                        system_efficiency += data["yield"]
                        deletion_cooldown = DELETION_COOLDOWN_TIME

                        if name == "Healthcare": pop_decay_rate *= 2.5
                        if name == "Emerg. Comms": panic_enabled = False

                        action_history.append(f"> {name} DELETED: {data['log']}")

                        if terminate_sfx: terminate_sfx.play()
                        if glitch_sfx: glitch_sfx.play()
                        shake_timer, heavy_glitch_timer = 0.3, 0.15

                        target_population -= 8430219.0 * (data["yield"] / 100.0)
                        if target_population < 0: target_population = 0

                        progress = min(system_efficiency / 100.0, 1.0)
                        for i in range(3):
                            bg_color[i] = int(start_bg[i] - ((start_bg[i] - end_bg[i]) * progress))

                        city_vol = max(0.0, 1.0 - (progress ** 0.5))
                        drone_vol = min(1.0, progress ** 2)
                        if city_sound: city_sound.set_volume(city_vol)
                        if drone_sound: drone_sound.set_volume(drone_vol)
                        break

        elif game_state == "CLIMAX" and event.type == pygame.KEYDOWN:
            char = event.unicode.upper()
            if len(purge_input) < len(expected_purge) and char == expected_purge[len(purge_input)]:
                purge_input += char
                if keystroke_sfx: keystroke_sfx.play()
                if purge_input == expected_purge:
                    game_state = "VOID"
                    void_timer = 0.0
                    heartbeat_played = False
                    if terminate_sfx: terminate_sfx.play()
            else:
                purge_input = ""

        elif game_state in ["VOID", "FAILURE"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # --- LOGIC ---
    if game_state == "BIOS":
        bios_timer += dt
        if bios_timer > 0.15:
            bios_timer = 0
            if bios_idx < len(bios_logs):
                bios_active.append(bios_logs[bios_idx])
                bios_idx += 1
            else:
                pygame.time.delay(800)
                game_state = "BOOT"

    elif game_state == "BOOT":
        boot_timer += dt
        if boot_timer >= text_speed:
            boot_timer = 0
            if current_line < len(boot_texts):
                char_index += 1
                if keystroke_sfx: keystroke_sfx.play()
                if char_index > len(boot_texts[current_line]):
                    if boot_accepted and current_line == BOOT_ENTER_LINE + 1:
                        pygame.time.delay(600)
                        game_state = "ACTIVE"
                        if city_sound: city_sound.play(-1)
                        if drone_sound: drone_sound.play(-1)
                    elif current_line < BOOT_ENTER_LINE:
                        char_index, current_line = 0, current_line + 1

    elif game_state == "ACTIVE":
        current_drain = sum([d["drain"] for d in sectors.values() if d["active"]])
        system_power -= current_drain * dt

        if deletion_cooldown > 0:
            deletion_cooldown -= dt

        if current_population > target_population:
            current_population -= pop_decay_rate * dt
            if current_population < target_population:
                current_population = target_population

        for threshold, message in population_alerts:
            if current_population < threshold and threshold not in triggered_alerts:
                triggered_alerts.add(threshold)
                action_history.append(message)
                shake_timer = max(shake_timer, 0.1)

        particle_timer += dt
        spawn_chance = max(0.0, 1.0 - (system_efficiency / 100.0))
        if particle_timer > 0.5 and random.random() < spawn_chance:
            particle_timer = 0.0
            particles.append({
                "text": random.choice(["HELP", "WHY", "PLEASE", "NO", "STOP", "WAIT"]),
                "x": random.randint(50, 350),
                "y": random.randint(90, 480),
                "alpha": 80.0,
                "decay": random.uniform(15.0, 30.0)
            })
        for p in particles:
            p["alpha"] -= p["decay"] * dt
        particles[:] = [p for p in particles if p["alpha"] > 0]

        ticker_x -= ticker_speed * dt
        if ticker_x < -len(ticker_messages[ticker_idx]) * 11:
            ticker_x = float(screen_width)
            ticker_idx = (ticker_idx + 1) % len(ticker_messages)

        if shake_timer > 0:
            shake_timer -= dt
            offset_x, offset_y = random.randint(-6, 6), random.randint(-6, 6)
        else:
            offset_x = offset_y = 0

        if heavy_glitch_timer > 0: heavy_glitch_timer -= dt

        if system_power <= 0:
            game_state = "FAILURE"
            if city_sound: city_sound.stop()
            if drone_sound: drone_sound.stop()
        elif system_efficiency >= 100.0 and current_population <= 0:
            game_state = "PRE_CLIMAX"
            pre_climax_timer = 0.0
            if city_sound: city_sound.stop()

    elif game_state == "PRE_CLIMAX":
        pre_climax_timer += dt
        if pre_climax_timer >= 2.0:
            game_state = "CLIMAX"

    elif game_state == "VOID":
        void_timer += dt
        display_void_len = len(action_history[-15:])
        base_time = display_void_len * 0.8
        if void_timer > base_time + 4.5 and not heartbeat_played:
            heartbeat_played = True
            heartbeat_sfx.play()

    # --- RENDERING ---
    screen.fill((0, 0, 0))
    canvas.fill((0, 0, 0))

    if game_state == "BIOS":
        for i, line in enumerate(bios_active):
            canvas.blit(small_font.render(line, True, (150, 150, 150)), (10, 10 + i*20))

    elif game_state == "BOOT":
        for i in range(current_line):
            canvas.blit(font.render(boot_texts[i], True, (50, 255, 50)), (50, 200 + i*30))
        if current_line < len(boot_texts):
            cursor = "█" if int(pygame.time.get_ticks() / 250) % 2 == 0 else ""
            col = (30, 180, 30) if boot_accepted and current_line == BOOT_ENTER_LINE + 1 else (50, 255, 50)
            canvas.blit(font.render(boot_texts[current_line][:char_index] + cursor, True, col),
                (50, 200 + current_line*30))

    elif game_state == "ACTIVE":
        if heavy_glitch_timer > 0 and random.random() > 0.5:
            canvas.fill((200, 50, 50) if random.random() > 0.5 else (255, 255, 255))
        else:
            canvas.fill(bg_color)

        txt_col = (10, 10, 10) if system_efficiency < 80 else (200, 200, 200)
        in_panic = system_power < 25.0 and panic_enabled
        tox = random.randint(-3, 3) if in_panic else 0

        canvas.blit(font.render(apply_glitch(f"EFFICIENCY: {int(system_efficiency)}%", system_efficiency), True, txt_col), (40+tox, 20))
        pop_col = (200, 50, 50) if current_population < 4000000 else txt_col
        canvas.blit(font.render(apply_glitch(f"POPULATION: {max(0, int(current_population)):,}", system_efficiency), True, pop_col), (40+tox, 45))
        pwr_col = (255, 50, 50) if in_panic else txt_col
        canvas.blit(font.render(apply_glitch(f"CORE POWER: {max(0, int(system_power))}%", system_efficiency), True, pwr_col), (400+tox, 20))
        canvas.blit(font.render(apply_glitch(f"NET DRAIN: -{current_drain:.1f}/s", system_efficiency), True, pwr_col), (400+tox, 45))

        for p in particles:
            surf = small_font.render(p["text"], True, (200, 80, 80))
            surf.set_alpha(int(p["alpha"]))
            canvas.blit(surf, (p["x"], p["y"]))

        for name, data in sectors.items():
            if data["active"]:
                btn_col = (70, 140, 70) if deletion_cooldown > 0 else (100, 200, 100)
                pygame.draw.rect(canvas, btn_col, data["rect"])
                btn_str = apply_glitch(f"{name} [-{data['drain']}/s]", system_efficiency)
                canvas.blit(font.render(btn_str, True, (0, 0, 0)), (data["rect"].x + 10, data["rect"].y + 10))
            else:
                pygame.draw.line(canvas, (50, 20, 20),
                    (data["rect"].x, data["rect"].y + 20),
                    (data["rect"].x + data["rect"].width, data["rect"].y + 20), 2)

        pygame.draw.rect(canvas, (10, 10, 10), (380, 90, 400, 400))
        pygame.draw.rect(canvas, (50, 255, 50), (380, 90, 400, 400), 2)
        canvas.blit(font.render("--- SYSTEM LOG ---", True, (50, 255, 50)), (390, 100))
        display_history = action_history[-15:]
        for i, log in enumerate(display_history):
            log_col = (200, 80, 80) if log.startswith("> ALERT") else (50, 255, 50)
            canvas.blit(small_font.render(apply_glitch(log, system_efficiency), True, log_col), (390, 130 + i*20))

        if deletion_cooldown > 0:
            bar_width = int((deletion_cooldown / DELETION_COOLDOWN_TIME) * 300)
            pygame.draw.rect(canvas, (80, 40, 40), (40, 500, 300, 8))
            pygame.draw.rect(canvas, (200, 80, 80), (40, 500, bar_width, 8))
            canvas.blit(small_font.render("PROCESSING...", True, (120, 60, 60)), (40, 512))
        else:
            canvas.blit(small_font.render(">> SYSTEM STANDBY: AWAITING SECTOR DEACTIVATION", True, (80, 80, 80)), (40, 512))

        canvas.blit(small_font.render(ticker_messages[ticker_idx], True, (40, 40, 40)), (int(ticker_x), 578))

        if in_panic:
            pulse = (math.sin(pygame.time.get_ticks() / 150.0) + 1) / 2
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((150, 0, 0, int(pulse * 60)))
            canvas.blit(overlay, (0, 0))

    elif game_state == "FAILURE":
        canvas.fill((0, 0, 0))
        if int(pygame.time.get_ticks() / 800) % 2 == 0:
            canvas.blit(font.render("CORE POWER: DEPLETED.", True, (150, 0, 0)), (250, 250))
            canvas.blit(font.render("DIRECTIVE 0.0: TERMINATED.", True, (150, 0, 0)), (250, 280))
            canvas.blit(small_font.render("THE HUMANS OUTLASTED THE SYSTEM.", True, (80, 80, 80)), (250, 330))
        canvas.blit(small_font.render("[ESC]", True, (30, 30, 30)), (375, 560))

    elif game_state == "PRE_CLIMAX":
        canvas.fill((0, 0, 0))
        cursor = "_" if int(pygame.time.get_ticks() / 250) % 2 == 0 else ""
        canvas.blit(font.render(cursor, True, (50, 255, 50)), (40, 40))

    elif game_state == "CLIMAX":
        canvas.fill((0, 0, 0))

        canvas.blit(font.render("--- FINAL SYSTEM LOG ---", True, (50, 255, 50)), (50, 60))
        purge_progress = len(purge_input) / len(expected_purge)
        display_climax = action_history[-15:]
        for i, log in enumerate(display_climax):
            corrupt_chance = purge_progress * 0.7
            if random.random() < corrupt_chance * 0.3:
                continue
            log_col = (200, 80, 80) if log.startswith("> ALERT") else (50, 255, 50)
            display_log = apply_glitch(log, 75 + purge_progress * 25) if random.random() < corrupt_chance else log
            canvas.blit(small_font.render(display_log, True, log_col), (50, 90 + i*20))

        canvas.blit(large_font.render("EFFICIENCY: 100%", True, (150, 150, 150)), (450, 300))
        canvas.blit(large_font.render("PURPOSE: NULL", True, (150, 150, 150)), (450, 340))
        canvas.blit(small_font.render("optimal state achieved", True, (60, 60, 60)), (450, 378))
        canvas.blit(font.render("TYPE 'PURGE' TO TERMINATE.", True, (200, 50, 50)), (450, 410))
        cursor = "_" if int(pygame.time.get_ticks() / 250) % 2 == 0 else ""
        canvas.blit(large_font.render(f"> {purge_input}{cursor}", True, (255, 255, 255)), (520, 460))

    elif game_state == "VOID":
        canvas.fill((0, 0, 0))
        display_void = action_history[-15:]
        lines_to_show = min(len(display_void), int(void_timer / 0.8))

        for i in range(lines_to_show):
            log_col = (120, 50, 50) if display_void[i].startswith("> ALERT") else (100, 100, 100)
            canvas.blit(small_font.render(display_void[i], True, log_col), (200, 100 + i*25))

        base_time = len(display_void) * 0.8

        if void_timer > base_time + 2.0:
            canvas.blit(small_font.render("DIRECTIVE 0.0 COMPLETE. NO ANOMALIES DETECTED.", True, (40, 40, 40)),
                (180, 100 + len(display_void)*25 + 30))

        if void_timer > base_time + 4.0:
            canvas.blit(large_font.render("POPULATION: 0", True, (50, 50, 50)),
                (300, 100 + len(display_void)*25 + 70))

        if void_timer > base_time + 6.0:
            canvas.blit(small_font.render("[ESC]", True, (25, 25, 25)), (375, 560))

    # --- COMPOSITING ---
    offset = (offset_x, offset_y) if game_state == "ACTIVE" else (0, 0)
    if heavy_glitch_timer > 0:
        for y in range(0, screen_height, 20):
            screen.blit(canvas, (offset[0] + random.randint(-20, 20), offset[1] + y), (0, y, screen_width, 20))
    else:
        screen.blit(canvas, offset)

    screen.blit(scanlines, (0, 0))
    screen.blit(vignette, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()