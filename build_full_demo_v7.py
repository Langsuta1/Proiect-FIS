import json
import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
with open(os.path.join(scratch_dir, "assets_bundle.json"), "r", encoding="utf-8") as f:
    assets = json.load(f)

print(f"Loaded {len(assets)} assets for V7 Demo Generator.")

html_content = f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCRAPBORN — Playable Metroidvania Demo (The Heap V7)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }}
        body {{
            background: #090b10;
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
        }}
        #game-container {{
            position: relative;
            width: 1060px;
            height: 600px;
            background: #05070a;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(56, 189, 248, 0.2);
            border: 2px solid #1e293b;
            border-radius: 6px;
            overflow: hidden;
        }}
        canvas {{
            display: block;
            width: 100%;
            height: 100%;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }}
        #ui-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }}
        .hud-bar {{
            position: absolute;
            top: 14px;
            left: 16px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .bar-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(15, 23, 42, 0.9);
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid #334155;
            backdrop-filter: blur(4px);
        }}
        .bar-label {{
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
            width: 95px;
        }}
        .bar-track {{
            width: 160px;
            height: 10px;
            background: #1e293b;
            border-radius: 2px;
            overflow: hidden;
            border: 1px solid #475569;
        }}
        .bar-fill-hp {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #f87171);
            transition: width 0.15s ease-out;
        }}
        .bar-fill-ep {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            transition: width 0.15s ease-out;
        }}
        .bar-fill-shield {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #06b6d4, #22d3ee);
            transition: width 0.15s ease-out;
        }}
        .equipped-panel {{
            position: absolute;
            bottom: 16px;
            left: 16px;
            background: rgba(15, 23, 42, 0.92);
            padding: 8px 14px;
            border-radius: 6px;
            border: 1px solid #38bdf8;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .slot-box {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }}
        .slot-title {{
            font-size: 9px;
            color: #94a3b8;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .slot-name {{
            font-size: 13px;
            font-weight: bold;
            color: #38bdf8;
        }}
        .slot-name-sec {{
            font-size: 13px;
            font-weight: bold;
            color: #94a3b8;
        }}
        .swap-hint {{
            font-size: 10px;
            color: #f59e0b;
            background: rgba(245, 158, 11, 0.15);
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }}
        #boss-hud {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 520px;
            background: rgba(15, 23, 42, 0.92);
            padding: 8px 16px;
            border-radius: 6px;
            border: 2px solid #ef4444;
            display: none;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.4);
        }}
        .boss-title-row {{
            display: flex;
            justify-content: space-between;
            width: 100%;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .boss-name {{
            color: #f87171;
        }}
        .boss-phase {{
            color: #f59e0b;
        }}
        .boss-track {{
            width: 100%;
            height: 14px;
            background: #1e293b;
            border-radius: 3px;
            overflow: hidden;
            border: 1px solid #7f1d1d;
        }}
        .boss-fill {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #b91c1c, #ef4444);
            transition: width 0.1s;
        }}
        #inventory-modal {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 440px;
            background: rgba(15, 23, 42, 0.96);
            border: 2px solid #38bdf8;
            border-radius: 8px;
            padding: 16px;
            display: none;
            flex-direction: column;
            gap: 12px;
            box-shadow: 0 0 35px rgba(0, 0, 0, 0.9), 0 0 20px rgba(56, 189, 248, 0.25);
            pointer-events: auto;
        }}
        .inv-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 8px;
        }}
        .inv-title {{
            font-size: 14px;
            font-weight: bold;
            color: #38bdf8;
            letter-spacing: 1px;
        }}
        .matrix-3x3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 6px;
        }}
        .matrix-slot {{
            height: 64px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #475569;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.15s;
            position: relative;
        }}
        .matrix-slot:hover {{
            border-color: #38bdf8;
            background: rgba(56, 189, 248, 0.15);
        }}
        .matrix-slot.active {{
            border-color: #f59e0b;
            background: rgba(245, 158, 11, 0.2);
        }}
        .matrix-slot-num {{
            position: absolute;
            top: 2px;
            left: 4px;
            font-size: 9px;
            color: #64748b;
        }}
        .matrix-slot-title {{
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            padding: 0 4px;
        }}
        .matrix-slot-count {{
            position: absolute;
            bottom: 2px;
            right: 4px;
            font-size: 10px;
            color: #38bdf8;
            font-weight: bold;
        }}
        #tutorial-toast {{
            position: absolute;
            top: 140px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid #38bdf8;
            border-radius: 6px;
            padding: 10px 20px;
            display: none;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
            animation: fadeIn 0.3s ease-out;
        }}
        .tut-title {{
            font-size: 14px;
            font-weight: bold;
            color: #38bdf8;
            letter-spacing: 1px;
        }}
        .tut-desc {{
            font-size: 12px;
            color: #cbd5e1;
            text-align: center;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translate(-50%, -10px); }}
            to {{ opacity: 1; transform: translate(-50%, 0); }}
        }}
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="game-canvas" width="1060" height="600"></canvas>

        <div id="ui-overlay">
            <!-- Top Left: Player Status Bars (Armor, Stamina, Energy Shield) -->
            <div class="hud-bar">
                <div class="bar-container">
                    <span class="bar-label" style="color: #f87171;">ARMOR HP</span>
                    <div class="bar-track">
                        <div id="bar-hp" class="bar-fill-hp"></div>
                    </div>
                    <span id="txt-hp" style="font-size: 10px; color: #cbd5e1; width: 50px;">100 / 100</span>
                </div>
                <div class="bar-container">
                    <span class="bar-label" style="color: #38bdf8;">CORE ENERGY</span>
                    <div class="bar-track">
                        <div id="bar-ep" class="bar-fill-ep"></div>
                    </div>
                    <span id="txt-ep" style="font-size: 10px; color: #cbd5e1; width: 50px;">100 / 100</span>
                </div>
                <div class="bar-container">
                    <span class="bar-label" style="color: #22d3ee;">SHIELD (15%/s)</span>
                    <div class="bar-track">
                        <div id="bar-shield" class="bar-fill-shield"></div>
                    </div>
                    <span id="txt-shield" style="font-size: 10px; color: #cbd5e1; width: 50px;">50 / 50</span>
                </div>
            </div>

            <!-- Top Center: Boss Health Bar -->
            <div id="boss-hud">
                <div class="boss-title-row">
                    <span class="boss-name">THE CRUSHER TITAN</span>
                    <span id="boss-phase-txt" class="boss-phase">PHASE 1 - COMPACTOR OVERLOAD</span>
                </div>
                <div class="boss-track">
                    <div id="boss-fill" class="boss-fill"></div>
                </div>
            </div>

            <!-- Bottom Left: Equipped Arsenal & Quick-Swap [Q] -->
            <div class="equipped-panel">
                <div class="slot-box">
                    <span class="slot-title">PRIMARY [CLICK / X]</span>
                    <span id="lbl-primary" class="slot-name">CYBER FRYING PAN</span>
                </div>
                <div class="swap-hint">[Q] SWAP</div>
                <div class="slot-box">
                    <span class="slot-title">SECONDARY [Z]</span>
                    <span id="lbl-secondary" class="slot-name-sec">LASER BLASTER</span>
                </div>
                <div class="slot-box" style="margin-left: 10px;">
                    <span class="slot-title">GRENADE [G]</span>
                    <span id="lbl-grenade" style="font-size: 12px; color: #f59e0b; font-weight: bold;">FRAG (x3)</span>
                </div>
                <div class="swap-hint" style="color: #38bdf8; border-color: #38bdf8; background: rgba(56,189,248,0.15);">[I] INVENTORY</div>
            </div>

            <!-- Tutorial Toast Notification -->
            <div id="tutorial-toast">
                <span id="tut-title" class="tut-title">A / D MOVE CHASSIS</span>
                <span id="tut-desc" class="tut-desc">Hold [SHIFT] to sprint</span>
            </div>

            <!-- 3x3 Backpack Inventory Screen [I] -->
            <div id="inventory-modal">
                <div class="inv-header">
                    <span class="inv-title">SCRAP INVENTORY MATRIX (3x3)</span>
                    <span style="font-size: 11px; color: #94a3b8;">Press [I] to Close</span>
                </div>
                <div class="matrix-3x3" id="matrix-container">
                    <!-- 9 slots dynamically injected -->
                </div>
                <div style="font-size: 11px; color: #64748b; text-align: center; margin-top: 4px;">
                    Click slot to equip to Primary or switch active Grenade module
                </div>
            </div>
        </div>
    </div>

    <script>
        // -------------------------------------------------------------
        // SCRAPBORN METROIDVANIA V7 ENGINE - ALL 8 USER REQUIREMENTS
        // -------------------------------------------------------------
        const ASSETS = {json.dumps(assets)};
        const canvas = document.getElementById("game-canvas");
        const ctx = canvas.getContext("2d");

        // Load Images
        const imgMap = {{}};
        let loadedImgs = 0;
        const totalImgs = Object.keys(ASSETS).length;

        for (const [k, v] of Object.entries(ASSETS)) {{
            const img = new Image();
            img.src = v;
            img.onload = () => {{
                loadedImgs++;
                if (loadedImgs >= totalImgs) init();
            }};
            imgMap[k] = img;
        }}

        // Game Constants
        const WORLD_W = 5200;
        const WORLD_H = 900;
        const FLOOR_Y = 780;
        const CHASM_START = 2800;
        const CHASM_END = 3600;

        // Player State
        const player = {{
            x: 80,
            y: 750,
            vx: 0,
            vy: 0,
            w: 18,
            h: 28,
            facing: 1,
            hp: 100,
            maxHp: 100,
            ep: 100,
            maxEp: 100,
            shield: 50,
            maxShield: 50,
            shieldRegenTimer: 0,
            isGrounded: false,
            isCrouching: false,
            isSprinting: false,
            isDashing: false,
            dashTimer: 0,
            dashCooldown: 0,
            isShieldRaised: false,
            isGrappling: false,
            grappleAnchor: {{x: 0, y: 0}},
            grappleLen: 0,
            grappleAngle: 0,
            grappleAngVel: 0,
            canDoubleJump: true,
            hasDoubleJumped: false,
            attackTimer: 0,
            attackDuration: 0.22,
            iFrameTimer: 0,
            primary: "pan",
            secondary: "blaster",
            activeGrenade: "frag",
            animTimer: 0
        }};

        // 3x3 Backpack Matrix (9 slots)
        const backpack = [
            {{ id: "pan", name: "Cyber Pan", type: "weapon", icon: "cyber_pan_32x32", count: 1 }},
            {{ id: "bat", name: "Metal Bat", type: "weapon", icon: "metal_bat_32x32", count: 1 }},
            {{ id: "blaster", name: "Blaster Arm", type: "weapon", icon: "laser_blaster_arm_32x32", count: 1 }},
            {{ id: "flamethrower", name: "Flamethrower", type: "weapon", icon: "flamethrower_32x32", count: 1 }},
            {{ id: "frag", name: "Frag Grenade", type: "grenade", icon: "grenade_frag_32x32", count: 4 }},
            {{ id: "emp", name: "EMP Grenade", type: "grenade", icon: "grenade_emp_32x32", count: 3 }},
            {{ id: "cryo", name: "Cryo Grenade", type: "grenade", icon: "grenade_cryo_32x32", count: 3 }},
            {{ id: "fire", name: "Fire Grenade", type: "grenade", icon: "grenade_fire_32x32", count: 3 }},
            {{ id: "chip", name: "Overclock Chip", type: "upgrade", icon: "chip_nano_repair_32x32", count: 1 }}
        ];

        let isInventoryOpen = false;

        // Camera
        const camera = {{ x: 0, y: 0, targetX: 0, targetY: 0 }};

        // Input
        const keys = {{}};
        let mouseX = 0, mouseY = 0;
        let isMouseDown = false, isRightMouseDown = false;

        window.addEventListener("keydown", e => {{
            keys[e.code] = true;
            if (e.code === "KeyI") {{
                toggleInventory();
            }}
            if (e.code === "KeyQ") {{
                swapWeapons();
            }}
            if (e.code === "KeyG") {{
                throwGrenade();
            }}
            if (e.code === "KeyE") {{
                tryGrapple();
            }}
            if (e.code === "KeyC") {{
                tryDash();
            }}
        }});
        window.addEventListener("keyup", e => {{ keys[e.code] = false; }});
        window.addEventListener("mousedown", e => {{
            if (e.button === 0) isMouseDown = true;
            if (e.button === 2) isRightMouseDown = true;
        }});
        window.addEventListener("mouseup", e => {{
            if (e.button === 0) isMouseDown = false;
            if (e.button === 2) isRightMouseDown = false;
        }});
        window.addEventListener("contextmenu", e => e.preventDefault());

        // Level Obstacles & Gates
        const obstacles = [
            {{ type: "car", x: 320, y: 756, w: 56, h: 24, pass: false }},
            {{ type: "conduit_roof", x: 800, y: 730, w: 220, h: 20 }}, // clearance 24px (must crouch!)
            {{ type: "barricade", x: 1380, y: 700, w: 24, h: 80, hp: 50, broken: false }},
            {{ type: "arena_gate_left", x: 1620, y: 640, w: 20, h: 140, locked: false }},
            {{ type: "arena_gate_right", x: 2280, y: 640, w: 20, h: 140, locked: true }},
            {{ type: "laser_turret", x: 2550, y: 550, active: true }},
            {{ type: "blast_bulkhead", x: 3800, y: 640, w: 24, h: 140, hp: 100, broken: false }},
            {{ type: "boss_gate", x: 4080, y: 620, w: 24, h: 160, locked: false }}
        ];

        // 3 Grapple Rings across Chasm (Ori / Prince of Persia style)
        const grappleRings = [
            {{ x: 3000, y: 560 }},
            {{ x: 3200, y: 540 }},
            {{ x: 3400, y: 560 }}
        ];

        // Safe Combat Arena Enemies
        const enemies = [
            {{ id: "crawler1", type: "crawler", x: 1850, y: 768, hp: 60, maxHp: 60, speed: 70, dir: -1, frozen: 0, stun: 0 }},
            {{ id: "drone1", type: "drone", x: 2100, y: 580, hp: 50, maxHp: 50, speed: 85, dir: -1, frozen: 0, stun: 0 }}
        ];

        // The Crusher Titan Boss
        const boss = {{
            x: 4650,
            y: 740,
            hp: 1500,
            maxHp: 1500,
            phase: 1,
            state: "dormant", // dormant, drop_in, idle, telegraph, slam, charge, stunned
            timer: 0,
            facing: -1,
            telegraphX: 0,
            telegraphW: 120,
            pistonActive: false,
            pistonX: 0,
            pistonY: 0
        }};

        // Projectiles & Grenades & Particles
        const projectiles = [];
        const grenades = [];
        const particles = [];

        function toggleInventory() {{
            isInventoryOpen = !isInventoryOpen;
            const modal = document.getElementById("inventory-modal");
            modal.style.display = isInventoryOpen ? "flex" : "none";
            if (isInventoryOpen) renderInventory();
        }}

        function renderInventory() {{
            const c = document.getElementById("matrix-container");
            c.innerHTML = "";
            backpack.forEach((item, idx) => {{
                const div = document.createElement("div");
                div.className = "matrix-slot" + (item.id === player.primary ? " active" : "");
                div.innerHTML = `
                    <span class="matrix-slot-num">#${{idx + 1}}</span>
                    <span class="matrix-slot-title">${{item.name}}</span>
                    ${{item.count > 1 ? `<span class="matrix-slot-count">x${{item.count}}</span>` : ''}}
                `;
                div.onclick = () => {{
                    if (item.type === "weapon") {{
                        player.primary = item.id;
                        updateUI();
                        renderInventory();
                    }} else if (item.type === "grenade") {{
                        player.activeGrenade = item.id;
                        updateUI();
                        renderInventory();
                    }}
                }};
                c.appendChild(div);
            }});
        }}

        function swapWeapons() {{
            const temp = player.primary;
            player.primary = player.secondary;
            player.secondary = temp;
            updateUI();
        }}

        function tryDash() {{
            if (player.dashCooldown <= 0 && !player.isDashing && player.ep >= 15) {{
                player.isDashing = true;
                player.dashTimer = 0.22;
                player.ep -= 15;
            }}
        }}

        function throwGrenade() {{
            const item = backpack.find(i => i.id === player.activeGrenade);
            if (item && item.count > 0) {{
                item.count--;
                grenades.push({{
                    x: player.x + player.facing * 16,
                    y: player.y + (player.isCrouching ? 6 : 0),
                    vx: player.facing * 340,
                    vy: -260,
                    type: player.activeGrenade,
                    timer: 1.4
                }});
                updateUI();
            }}
        }}

        function tryGrapple() {{
            if (player.isGrappling) {{
                player.isGrappling = false;
                player.vy = -380;
                player.vx += player.facing * 180;
                return;
            }}
            // Find closest ring
            for (const r of grappleRings) {{
                const d = Math.hypot(player.x - r.x, player.y - r.y);
                if (d < 240 && r.y < player.y) {{
                    player.isGrappling = true;
                    player.grappleAnchor = {{ x: r.x, y: r.y }};
                    player.grappleLen = d;
                    player.grappleAngle = Math.atan2(player.y - r.y, player.x - r.x);
                    player.grappleAngVel = (player.vx / d) * 0.8;
                    return;
                }}
            }}
        }}

        function updateUI() {{
            document.getElementById("bar-hp").style.width = Math.max(0, (player.hp / player.maxHp) * 100) + "%";
            document.getElementById("txt-hp").innerText = `${{Math.round(player.hp)}} / ${{player.maxHp}}`;
            document.getElementById("bar-ep").style.width = Math.max(0, (player.ep / player.maxEp) * 100) + "%";
            document.getElementById("txt-ep").innerText = `${{Math.round(player.ep)}} / ${{player.maxEp}}`;
            document.getElementById("bar-shield").style.width = Math.max(0, (player.shield / player.maxShield) * 100) + "%";
            document.getElementById("txt-shield").innerText = `${{Math.round(player.shield)}} / ${{player.maxShield}}`;

            const names = {{
                pan: "CYBER FRYING PAN",
                bat: "REINFORCED BAT",
                blaster: "LASER BLASTER",
                flamethrower: "FLAMETHROWER"
            }};
            document.getElementById("lbl-primary").innerText = names[player.primary] || player.primary.toUpperCase();
            document.getElementById("lbl-secondary").innerText = names[player.secondary] || player.secondary.toUpperCase();

            const gItem = backpack.find(i => i.id === player.activeGrenade);
            document.getElementById("lbl-grenade").innerText = `${{player.activeGrenade.toUpperCase()}} (x${{gItem ? gItem.count : 0}})`;

            // Boss HUD
            const bossHud = document.getElementById("boss-hud");
            if (boss.state !== "dormant" && boss.hp > 0) {{
                bossHud.style.display = "flex";
                document.getElementById("boss-fill").style.width = Math.max(0, (boss.hp / boss.maxHp) * 100) + "%";
                document.getElementById("boss-phase-txt").innerText = boss.phase === 2 ? "PHASE 2 - ENRAGED CRUSHER (ROCKET RAM)" : "PHASE 1 - HYDRAULIC COMPACTOR SLAM";
            }} else {{
                bossHud.style.display = "none";
            }}
        }}

        function showTutorial(title, desc) {{
            const toast = document.getElementById("tutorial-toast");
            document.getElementById("tut-title").innerText = title;
            document.getElementById("tut-desc").innerText = desc;
            toast.style.display = "flex";
        }}
        function hideTutorial() {{
            document.getElementById("tutorial-toast").style.display = "none";
        }}

        // -------------------------------------------------------------
        // MAIN GAME LOOP
        // -------------------------------------------------------------
        let lastTime = performance.now();

        function init() {{
            requestAnimationFrame(gameLoop);
        }}

        function gameLoop(now) {{
            const dt = Math.min((now - lastTime) / 1000, 0.1);
            lastTime = now;

            update(dt);
            render();

            requestAnimationFrame(gameLoop);
        }}

        function update(dt) {{
            player.animTimer += dt;

            // Shield Regeneration (15% per second after 3 seconds non-use)
            if (player.shieldRegenTimer > 0) {{
                player.shieldRegenTimer -= dt;
            }} else if (player.shield < player.maxShield) {{
                player.shield = Math.min(player.maxShield, player.shield + (player.maxShield * 0.15 * dt));
            }}

            // Shield Deployment [F] or [Right Click]
            player.isShieldRaised = (keys["KeyF"] || isRightMouseDown) && player.shield > 0;

            // I-Frames
            if (player.iFrameTimer > 0) player.iFrameTimer -= dt;

            // Dashing
            if (player.dashCooldown > 0) player.dashCooldown -= dt;
            if (player.isDashing) {{
                player.dashTimer -= dt;
                player.vy = 0;
                player.vx = player.facing * 440;
                if (player.dashTimer <= 0) {{
                    player.isDashing = false;
                    player.dashCooldown = 0.45;
                }}
            }} else if (player.isGrappling) {{
                // Grapple Pendulum Physics
                const g = 980;
                const angularAccel = (-g / player.grappleLen) * Math.cos(player.grappleAngle);
                player.grappleAngVel += angularAccel * dt;
                player.grappleAngVel *= 0.996;
                player.grappleAngle += player.grappleAngVel * dt;

                player.x = player.grappleAnchor.x + Math.cos(player.grappleAngle) * player.grappleLen;
                player.y = player.grappleAnchor.y + Math.sin(player.grappleAngle) * player.grappleLen;
                player.vx = -Math.sin(player.grappleAngle) * player.grappleAngVel * player.grappleLen;
                player.vy = Math.cos(player.grappleAngle) * player.grappleAngVel * player.grappleLen;

                if (keys["Space"]) {{
                    tryGrapple();
                }}
            }} else {{
                // Normal Movement Physics
                player.isCrouching = (keys["KeyS"] || keys["ArrowDown"]) && player.isGrounded;
                player.isSprinting = (keys["ShiftLeft"] || keys["ShiftRight"]) && !player.isCrouching;

                let moveDir = 0;
                if (keys["KeyA"] || keys["ArrowLeft"]) moveDir -= 1;
                if (keys["KeyD"] || keys["ArrowRight"]) moveDir += 1;

                const speed = player.isCrouching ? 60 : (player.isSprinting ? 230 : 145);
                player.vx = moveDir * speed;
                if (moveDir !== 0) player.facing = moveDir;

                // Gravity
                player.vy += 980 * dt;

                // Jump
                if (keys["Space"] || keys["KeyW"]) {{
                    if (player.isGrounded) {{
                        player.vy = -380;
                        player.isGrounded = false;
                    }} else if (player.canDoubleJump && !player.hasDoubleJumped && player.ep >= 10) {{
                        player.vy = -330;
                        player.hasDoubleJumped = true;
                        player.ep -= 10;
                    }}
                    keys["Space"] = false;
                    keys["KeyW"] = false;
                }}

                player.x += player.vx * dt;
                player.y += player.vy * dt;

                // Floor Collision (Respecting the Colossal Chasm!)
                const inChasm = (player.x > CHASM_START && player.x < CHASM_END);
                if (!inChasm) {{
                    if (player.y >= FLOOR_Y - (player.isCrouching ? 16 : 28)) {{
                        player.y = FLOOR_Y - (player.isCrouching ? 16 : 28);
                        player.vy = 0;
                        player.isGrounded = true;
                        player.canDoubleJump = true;
                        player.hasDoubleJumped = false;
                    }}
                }} else {{
                    player.isGrounded = false;
                    // Fell into bottomless scrap chasm: Instant Death!
                    if (player.y > FLOOR_Y + 140) {{
                        player.x = 2740;
                        player.y = 740;
                        player.vx = 0;
                        player.vy = 0;
                        player.hp = Math.max(10, player.hp - 40);
                    }}
                }}
            }}

            // Low Scrap Conduit collision (Clearance 24px)
            if (player.x > 800 && player.x < 1020) {{
                if (!player.isCrouching && player.y < 755) {{
                    // Head hits ceiling! Must stay crouched
                    player.y = 756;
                }}
            }}

            // Barricade collision
            const barricade = obstacles.find(o => o.type === "barricade");
            if (barricade && !barricade.broken) {{
                if (player.x > barricade.x - 16 && player.x < barricade.x + 24) {{
                    player.x = barricade.x - 16;
                }}
            }}

            // Blast Bulkhead collision
            const bulkhead = obstacles.find(o => o.type === "blast_bulkhead");
            if (bulkhead && !bulkhead.broken) {{
                if (player.x > bulkhead.x - 16 && player.x < bulkhead.x + 24) {{
                    player.x = bulkhead.x - 16;
                }}
            }}

            // Car obstacle collision
            const car = obstacles.find(o => o.type === "car");
            if (car && player.y > car.y - 20) {{
                if (player.x > car.x - 16 && player.x < car.x + car.w) {{
                    if (player.vy > 0 && player.y < car.y + 10) {{
                        player.y = car.y - (player.isCrouching ? 16 : 28);
                        player.vy = 0;
                        player.isGrounded = true;
                    }} else if (player.facing === 1) {{
                        player.x = car.x - 16;
                    }}
                }}
            }}

            // Attacks
            if (player.attackTimer > 0) {{
                player.attackTimer -= dt;
            }} else if (isMouseDown || keys["KeyX"]) {{
                // Primary Melee Attack
                player.attackTimer = 0.24;
                // Melee hit check
                const hitX = player.x + player.facing * 34;
                const hitY = player.y + (player.isCrouching ? 6 : 0);

                // Hit barricade
                if (barricade && !barricade.broken && Math.abs(hitX - barricade.x) < 40) {{
                    barricade.hp -= 25;
                    if (barricade.hp <= 0) barricade.broken = true;
                }}

                // Hit enemies
                enemies.forEach(e => {{
                    if (e.hp > 0 && Math.hypot(hitX - e.x, hitY - e.y) < 45) {{
                        e.hp -= (player.primary === "bat" ? 35 : 25);
                    }}
                }});

                // Hit boss
                if (boss.state !== "dormant" && Math.abs(hitX - boss.x) < 80) {{
                    const mult = (boss.state === "stunned" ? 2.0 : 1.0);
                    boss.hp -= (player.primary === "bat" ? 35 : 25) * mult;
                    if (boss.hp <= boss.maxHp * 0.5 && boss.phase === 1) boss.phase = 2;
                }}
            }} else if (keys["KeyZ"]) {{
                // Secondary Ranged Blaster
                if (player.secondary === "blaster" && player.ep >= 12) {{
                    player.ep -= 12;
                    player.attackTimer = 0.18;
                    projectiles.push({{
                        x: player.x + player.facing * 24,
                        y: player.y + (player.isCrouching ? 6 : 0),
                        vx: player.facing * 600,
                        timer: 1.5
                    }});
                    keys["KeyZ"] = false;
                }}
            }}

            // Update Projectiles
            for (let i = projectiles.length - 1; i >= 0; i--) {{
                const p = projectiles[i];
                p.x += p.vx * dt;
                p.timer -= dt;

                // Hit enemies
                enemies.forEach(e => {{
                    if (e.hp > 0 && Math.hypot(p.x - e.x, p.y - e.y) < 30) {{
                        e.hp -= 30;
                        p.timer = 0;
                    }}
                }});

                // Hit boss
                if (boss.state !== "dormant" && Math.abs(p.x - boss.x) < 60 && Math.abs(p.y - boss.y) < 70) {{
                    boss.hp -= 30;
                    p.timer = 0;
                    if (boss.hp <= boss.maxHp * 0.5 && boss.phase === 1) boss.phase = 2;
                }}

                if (p.timer <= 0) projectiles.splice(i, 1);
            }}

            // Update Grenades
            for (let i = grenades.length - 1; i >= 0; i--) {{
                const g = grenades[i];
                g.vy += 650 * dt;
                g.x += g.vx * dt;
                g.y += g.vy * dt;
                if (g.y >= FLOOR_Y - 8) {{
                    g.y = FLOOR_Y - 8;
                    g.vx *= 0.6;
                    g.vy = -g.vy * 0.4;
                }}
                g.timer -= dt;
                if (g.timer <= 0) {{
                    // Explode!
                    if (g.type === "frag") {{
                        // Breaks blast bulkhead!
                        if (bulkhead && !bulkhead.broken && Math.abs(g.x - bulkhead.x) < 80) {{
                            bulkhead.broken = true;
                        }}
                        // Dmg enemies & boss
                        enemies.forEach(e => {{ if (Math.hypot(g.x - e.x, g.y - e.y) < 80) e.hp -= 80; }});
                        if (boss.state !== "dormant" && Math.abs(g.x - boss.x) < 100) boss.hp -= 80;
                    }} else if (g.type === "emp") {{
                        enemies.forEach(e => {{ if (Math.hypot(g.x - e.x, g.y - e.y) < 100) e.stun = 4.0; }});
                    }} else if (g.type === "cryo") {{
                        enemies.forEach(e => {{ if (Math.hypot(g.x - e.x, g.y - e.y) < 100) e.frozen = 3.5; }});
                    }}
                    grenades.splice(i, 1);
                }}
            }}

            // Update Enemies in Safe Combat Arena
            let allDead = true;
            enemies.forEach(e => {{
                if (e.hp > 0) {{
                    allDead = false;
                    if (e.frozen > 0) {{
                        e.frozen -= dt;
                    }} else if (e.stun > 0) {{
                        e.stun -= dt;
                    }} else {{
                        // Patrol
                        e.x += e.dir * e.speed * dt;
                        if (e.x < 1700 || e.x > 2200) e.dir *= -1;

                        // Contact damage with player
                        if (Math.hypot(player.x - e.x, player.y - e.y) < 30) {{
                            damagePlayer(15);
                        }}
                    }}
                }}
            }});
            if (allDead) {{
                const gateR = obstacles.find(o => o.type === "arena_gate_right");
                if (gateR) gateR.locked = false;
            }}

            // Security Laser Turret
            const turret = obstacles.find(o => o.type === "laser_turret");
            if (turret && turret.active) {{
                if (player.x > 2500 && player.x < 2600 && player.y > 600) {{
                    if (player.isShieldRaised) {{
                        // Shield absorbs laser beam!
                        damagePlayer(5);
                    }} else {{
                        // Direct continuous laser melt!
                        damagePlayer(25);
                    }}
                }}
                // Terminal deactivates turret
                if (player.x > 2630) turret.active = false;
            }}

            // Boss Crusher Titan Logic (Tuned for ~5 minutes)
            if (player.x > 4150 && boss.state === "dormant") {{
                boss.state = "drop_in";
                boss.timer = 2.0;
            }}

            if (boss.state !== "dormant" && boss.hp > 0) {{
                boss.timer -= dt;

                if (boss.state === "drop_in") {{
                    if (boss.timer <= 0) {{
                        boss.state = "idle";
                        boss.timer = 2.0;
                    }}
                }} else if (boss.state === "idle") {{
                    boss.facing = (player.x < boss.x ? -1 : 1);
                    if (boss.timer <= 0) {{
                        // Choose attack
                        if (boss.phase === 2 && Math.random() < 0.5) {{
                            boss.state = "charge";
                            boss.timer = 2.5;
                        }} else {{
                            // Ceiling Compactor Slam! (2.0s Red Floor Indicator)
                            boss.state = "telegraph";
                            boss.timer = 2.0;
                            boss.telegraphX = player.x - 50;
                        }}
                    }}
                }} else if (boss.state === "telegraph") {{
                    if (boss.timer <= 0) {{
                        boss.state = "slam";
                        boss.timer = 0.6;
                        boss.pistonActive = true;
                        boss.pistonX = boss.telegraphX + 50;
                        boss.pistonY = 700;

                        // Check if player caught in 50% HP SLAM!
                        if (player.x >= boss.telegraphX && player.x <= boss.telegraphX + 100) {{
                            damagePlayer(50); // 50% HP Crusher Slam!
                        }}
                    }}
                }} else if (boss.state === "slam") {{
                    if (boss.timer <= 0) {{
                        boss.pistonActive = false;
                        boss.state = "idle";
                        boss.timer = boss.phase === 2 ? 1.4 : 2.2;
                    }}
                }} else if (boss.state === "charge") {{
                    boss.x += boss.facing * 440 * dt;
                    if (Math.abs(player.x - boss.x) < 50) damagePlayer(35);
                    if (boss.x < 4180 || boss.x > 5120 || boss.timer <= 0) {{
                        boss.state = "stunned";
                        boss.timer = 4.5; // 4.5s STUNNED OPENING!
                    }}
                }} else if (boss.state === "stunned") {{
                    if (boss.timer <= 0) {{
                        boss.state = "idle";
                        boss.timer = 1.8;
                    }}
                }}
            }}

            // Tutorial Prompts Trigger Check
            checkTutorialTriggers();

            // Camera Tracking
            camera.targetX = player.x - canvas.width / 2;
            camera.targetY = 0;
            camera.x += (camera.targetX - camera.x) * 0.12;
            camera.x = Math.max(0, Math.min(WORLD_W - canvas.width, camera.x));

            updateUI();
        }}

        function damagePlayer(amt) {{
            if (player.iFrameTimer > 0) return;

            if (player.isShieldRaised) {{
                player.shieldRegenTimer = 3.0; // 3s delay before regen!
                if (player.shield >= amt) {{
                    player.shield -= amt;
                    return;
                }} else {{
                    const leftover = amt - player.shield;
                    player.shield = 0;
                    amt = leftover;
                }}
            }}

            player.iFrameTimer = 1.2;
            player.hp = Math.max(0, player.hp - amt);
            if (player.hp <= 0) {{
                player.x = 80;
                player.y = 750;
                player.hp = player.maxHp;
            }}
        }}

        function checkTutorialTriggers() {{
            const px = player.x;
            if (px < 220) {{
                showTutorial("A / D MOVE CHASSIS", "Hold [SHIFT] to sprint | Press [C] to dash");
            }} else if (px >= 220 && px < 460) {{
                showTutorial("[SPACE] TO JUMP", "Leap over the crushed car obstacle");
            }} else if (px >= 700 && px < 1000) {{
                showTutorial("[S] / [DOWN] CROUCH CRAWL", "Clearance is only 22px! Crawl through low scrap conduit");
            }} else if (px >= 1250 && px < 1450) {{
                showTutorial("[CLICK] / [X] MELEE ATTACK", "Swing Cyber Frying Pan to smash scrap barricade");
            }} else if (px >= 1650 && px < 2150) {{
                showTutorial("SAFE COMBAT ARENA", "Neutralize Scrap Crawler & Junk Drone in safe quarantine");
            }} else if (px >= 2350 && px < 2650) {{
                showTutorial("HOLD [F] / [RIGHT CLICK] SHIELD", "Raise Energy Shield to deflect automated turret beam");
            }} else if (px >= 2700 && px < 3550) {{
                showTutorial("[E] GRAPPLING HOOK", "Aim at overhead anchor rings & swing across colossal death chasm!");
            }} else if (px >= 3650 && px < 3850) {{
                showTutorial("[G] FRAG GRENADE", "Blow open reinforced steel bulkhead with high-explosive charge");
            }} else if (px >= 3900 && px < 4150) {{
                showTutorial("[I] INVENTORY & [Q] WEAPON SWAP", "Configure 3x3 Arsenal Matrix before facing The Crusher Titan!");
            }} else {{
                hideTutorial();
            }}
        }}

        // -------------------------------------------------------------
        // RENDER PIPELINE
        // -------------------------------------------------------------
        function render() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            ctx.translate(-camera.x, -camera.y);

            // 1. Draw 5200x900 Static Apocalyptic Backdrop
            const bgImg = imgMap["level_heap_backdrop_5200x900"];
            if (bgImg) {{
                ctx.drawImage(bgImg, 0, 0);
            }}

            // 2. Draw Obstacles
            // Crushed Car
            const carImg = imgMap["crushed_car_obstacle"];
            if (carImg) ctx.drawImage(carImg, 320, 756);

            // Barricade
            const barricade = obstacles.find(o => o.type === "barricade");
            if (barricade && !barricade.broken) {{
                ctx.fillStyle = "#78350f";
                ctx.fillRect(barricade.x, barricade.y, barricade.w, barricade.h);
                ctx.strokeStyle = "#f59e0b";
                ctx.strokeRect(barricade.x, barricade.y, barricade.w, barricade.h);
            }}

            // Blast Bulkhead
            const bulkhead = obstacles.find(o => o.type === "blast_bulkhead");
            if (bulkhead && !bulkhead.broken) {{
                ctx.fillStyle = "#334155";
                ctx.fillRect(bulkhead.x, bulkhead.y, bulkhead.w, bulkhead.h);
                ctx.strokeStyle = "#ef4444";
                ctx.strokeRect(bulkhead.x, bulkhead.y, bulkhead.w, bulkhead.h);
            }}

            // 3. Draw Grapple Anchor Rings
            const ringImg = imgMap["grapple_ring_32x32"];
            grappleRings.forEach(r => {{
                if (ringImg) ctx.drawImage(ringImg, r.x - 16, r.y - 16);
            }});

            // Draw Grapple Cable if active
            if (player.isGrappling) {{
                ctx.beginPath();
                ctx.moveTo(player.grappleAnchor.x, player.grappleAnchor.y);
                ctx.lineTo(player.x, player.y);
                ctx.strokeStyle = "#00f5ff";
                ctx.lineWidth = 2;
                ctx.stroke();
            }}

            // 4. Draw Enemies
            enemies.forEach(e => {{
                if (e.hp > 0) {{
                    const eImg = imgMap[e.type === "crawler" ? "enemy_crawler_strip4" : "enemy_drone_strip4"];
                    if (eImg) {{
                        ctx.drawImage(eImg, 0, 0, 32, 32, e.x - 16, e.y - 16, 32, 32);
                    }}
                    // Frozen ice block
                    if (e.frozen > 0) {{
                        ctx.fillStyle = "rgba(56, 189, 248, 0.4)";
                        ctx.fillRect(e.x - 18, e.y - 18, 36, 36);
                    }}
                }}
            }});

            // 5. Draw The Crusher Titan Boss
            if (boss.state !== "dormant" && boss.hp > 0) {{
                const bossImg = imgMap["boss_crusher_titan_strip4"];
                let f = 0;
                if (boss.state === "telegraph") f = 1;
                else if (boss.state === "charge") f = 2;
                else if (boss.state === "stunned") f = 3;

                if (bossImg) {{
                    ctx.save();
                    ctx.translate(boss.x, boss.y);
                    ctx.scale(-boss.facing, 1);
                    ctx.drawImage(bossImg, f * 128, 0, 128, 128, -64, -64, 128, 128);
                    ctx.restore();
                }}

                // Red Floor Telegraph Warning Indicator (2.0s duration)
                if (boss.state === "telegraph") {{
                    ctx.fillStyle = `rgba(239, 68, 68, ${{0.4 + 0.3 * Math.sin(Date.now() / 80)}})`;
                    ctx.fillRect(boss.telegraphX, 770, 100, 20);
                    ctx.strokeStyle = "#ef4444";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(boss.telegraphX, 770, 100, 20);
                }}

                // Ceiling Compactor Slam Piston
                if (boss.pistonActive) {{
                    const pistonImg = imgMap["boss_compactor_piston_80x160"];
                    if (pistonImg) ctx.drawImage(pistonImg, boss.pistonX - 40, boss.pistonY - 80);
                }}
            }}

            // 6. Draw Player (Humanoid Bipedal Locomotion & Fixed Hands)
            ctx.save();
            ctx.translate(player.x, player.y);
            ctx.scale(player.facing, 1);

            let pImg = imgMap["robot_standard_idle_strip4"];
            let hframes = 4;
            let fIdx = 0;

            if (player.attackTimer > 0) {{
                const prog = 1.0 - (player.attackTimer / player.attackDuration);
                fIdx = Math.min(3, Math.floor(prog * 4));
                if (player.primary === "pan") {{
                    pImg = imgMap["robot_standard_attack_pan_strip4"];
                    hframes = 4;
                }} else if (player.primary === "bat") {{
                    pImg = imgMap["robot_standard_attack_bat_strip4"];
                    hframes = 4;
                }}
            }} else if (player.isCrouching) {{
                pImg = imgMap["robot_standard_crouch_strip2"];
                hframes = 2;
                fIdx = Math.floor(player.animTimer * 4) % 2;
            }} else if (!player.isGrounded) {{
                pImg = imgMap["robot_standard_walk_strip8"];
                hframes = 8;
                fIdx = 3; // High leap frame
            }} else if (player.vx !== 0) {{
                pImg = imgMap["robot_standard_walk_strip8"];
                hframes = 8;
                const spd = player.isSprinting ? 12 : 8;
                fIdx = Math.floor(player.animTimer * spd) % 8;
            }}

            if (pImg) {{
                const frameW = pImg.width / hframes;
                const frameH = pImg.height;
                const yOff = player.isCrouching ? 6 : 0;
                ctx.drawImage(pImg, fIdx * frameW, 0, frameW, frameH, -frameW / 2, -frameH / 2 + yOff, frameW, frameH);
            }}

            // Draw Energy Shield in front of player
            if (player.isShieldRaised) {{
                const shieldImg = imgMap["shield_energy_barrier_64x64"];
                if (shieldImg) {{
                    ctx.drawImage(shieldImg, 0, -32, 64, 64);
                }}
            }}

            ctx.restore();

            // 7. Draw Projectiles
            ctx.fillStyle = "#38bdf8";
            projectiles.forEach(p => {{
                ctx.fillRect(p.x - 4, p.y - 2, 8, 4);
            }});

            // 8. Draw Grenades
            grenades.forEach(g => {{
                const gImg = imgMap[`grenade_${{g.type}}_32x32`];
                if (gImg) ctx.drawImage(gImg, g.x - 16, g.y - 16);
            }});

            ctx.restore();
        }}
    </script>
</body>
</html>
"""

demo_path = os.path.join(scratch_dir, "scrapborn_demo.html")
with open(demo_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("scrapborn_demo.html V7 updated successfully!")
