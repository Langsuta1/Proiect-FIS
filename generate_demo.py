import json
import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
with open(os.path.join(scratch_dir, "assets_bundle.json"), "r", encoding="utf-8") as f:
    assets = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCRAPBORN — Playable Metroidvania Demo (The Heap)</title>
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
            width: 960px;
            height: 540px;
            background: #05070a;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.15);
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
            gap: 6px;
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
            width: 100px;
        }}
        .bar-track {{
            width: 160px;
            height: 12px;
            background: #1e293b;
            border-radius: 2px;
            overflow: hidden;
            border: 1px solid #475569;
        }}
        .bar-fill-hp {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #dc2626, #ef4444);
            transition: width 0.15s ease-out;
        }}
        .bar-fill-ep {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            transition: width 0.15s ease-out;
        }}
        .weapon-card {{
            position: absolute;
            bottom: 14px;
            left: 16px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid #38bdf8;
            padding: 8px 12px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .weapon-slot {{
            width: 38px;
            height: 38px;
            background: #0f172a;
            border: 1px solid #64748b;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .weapon-slot img {{
            width: 32px;
            height: 32px;
            image-rendering: pixelated;
        }}
        .weapon-info {{
            display: flex;
            flex-direction: column;
        }}
        .weapon-name {{
            font-size: 13px;
            font-weight: bold;
            color: #38bdf8;
        }}
        .weapon-sub {{
            font-size: 10px;
            color: #94a3b8;
        }}
        #minimap-box {{
            position: absolute;
            top: 14px;
            right: 16px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid #475569;
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 11px;
            color: #94a3b8;
            text-align: right;
        }}
        #boss-hud {{
            position: absolute;
            top: 50px;
            left: 50%;
            transform: translateX(-50%);
            display: none;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            background: rgba(15, 23, 42, 0.9);
            padding: 8px 16px;
            border: 1px solid #ef4444;
            border-radius: 6px;
        }}
        #boss-bar-track {{
            width: 280px;
            height: 12px;
            background: #1e293b;
            border: 1px solid #ef4444;
            border-radius: 2px;
            overflow: hidden;
        }}
        #boss-bar-fill {{
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #dc2626, #ef4444);
            transition: width 0.1s ease;
        }}
        #dialogue-box {{
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 14, 26, 0.95);
            border: 2px solid #38bdf8;
            border-radius: 6px;
            padding: 12px 20px;
            width: 600px;
            max-width: 90%;
            display: none;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
            pointer-events: auto;
        }}
        #dialogue-title {{
            font-size: 13px;
            font-weight: bold;
            color: #38bdf8;
            margin-bottom: 4px;
        }}
        #dialogue-text {{
            font-size: 13px;
            line-height: 1.4;
            color: #e2e8f0;
        }}
        #controls-hint {{
            margin-top: 12px;
            font-size: 12px;
            color: #64748b;
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .key-badge {{
            background: #1e293b;
            color: #38bdf8;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
            border: 1px solid #334155;
        }}
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="480" height="270"></canvas>

        <div id="ui-overlay">
            <div class="hud-bar">
                <div class="bar-container">
                    <span class="bar-label" style="color: #ef4444;">ARMOR HP</span>
                    <div class="bar-track"><div id="hp-bar" class="bar-fill-hp"></div></div>
                    <span id="hp-text" style="font-size: 10px; font-weight: bold; width: 45px; text-align: right;">100 / 100</span>
                </div>
                <div class="bar-container">
                    <span class="bar-label" style="color: #38bdf8;">CORE STAMINA</span>
                    <div class="bar-track"><div id="ep-bar" class="bar-fill-ep"></div></div>
                    <span id="ep-text" style="font-size: 10px; font-weight: bold; width: 45px; text-align: right;">100 / 100</span>
                </div>
            </div>

            <div class="weapon-card">
                <div class="weapon-slot"><img id="weapon-icon" src="" alt="weapon"></div>
                <div class="weapon-info">
                    <span id="weapon-name" class="weapon-name">Cyber Frying Pan</span>
                    <span id="weapon-sub" class="weapon-sub">[X] Primary Melee · Deflect & Clang</span>
                </div>
            </div>

            <div id="minimap-box">
                <div style="font-weight: bold; color: #f59e0b;" id="zone-label">THE HEAP // ZONE 1</div>
                <div id="sub-zone-label" style="font-size: 10px;">Compactor Pit [Start]</div>
            </div>

            <div id="boss-hud">
                <div style="font-size: 11px; font-weight: bold; color: #ef4444; letter-spacing: 1.5px;">THE CRUSHER — COMPACTOR TITAN</div>
                <div id="boss-bar-track"><div id="boss-bar-fill"></div></div>
            </div>

            <div id="dialogue-box">
                <div id="dialogue-title">SYSTEM PROTOCOL</div>
                <div id="dialogue-text">Scraps re-activated. Chassis damaged. Right arm missing. Escape the compactor immediately!</div>
            </div>
        </div>
    </div>

    <div id="controls-hint">
        <span><span class="key-badge">A / D</span> Mers</span>
        <span><span class="key-badge">SHIFT</span> Sprint</span>
        <span><span class="key-badge">SPACE / W</span> Salt + Double Jump</span>
        <span><span class="key-badge">C</span> Dash</span>
        <span><span class="key-badge">X</span> Melee (Tigaie/Bâtă)</span>
        <span><span class="key-badge">Z</span> Blaster / Flamethrower</span>
        <span><span class="key-badge">G</span> Grenadă</span>
        <span><span class="key-badge">E</span> Grapple Hook</span>
        <span><span class="key-badge">1 - 4 / Q</span> Schimbă Armă</span>
        <span><span class="key-badge">F</span> Toggle Chassis</span>
        <span><span class="key-badge">M</span> Mute Sunet</span>
    </div>

    <script>
        const ASSETS = {json.dumps(assets)};

        const images = {{}};
        let loadedCount = 0;
        const assetKeys = Object.keys(ASSETS);

        assetKeys.forEach(k => {{
            const img = new Image();
            img.onload = () => {{
                loadedCount++;
                if (loadedCount === assetKeys.length) {{
                    initGame();
                }}
            }};
            img.src = ASSETS[k];
            images[k] = img;
        }});

        let audioCtx = null;
        let soundEnabled = true;

        function getAudioContext() {{
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();
            return audioCtx;
        }}

        function playSound(type) {{
            if (!soundEnabled) return;
            try {{
                const ctx = getAudioContext();
                const now = ctx.currentTime;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);

                if (type === 'jump') {{
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(140, now);
                    osc.frequency.exponentialRampToValueAtTime(380, now + 0.12);
                    gain.gain.setValueAtTime(0.15, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.12);
                    osc.start(now);
                    osc.stop(now + 0.12);
                }} else if (type === 'dash') {{
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(320, now);
                    osc.frequency.exponentialRampToValueAtTime(110, now + 0.18);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.18);
                    osc.start(now);
                    osc.stop(now + 0.18);
                }} else if (type === 'pan_clang') {{
                    osc.type = 'square';
                    osc.frequency.setValueAtTime(840, now);
                    osc.frequency.exponentialRampToValueAtTime(260, now + 0.22);
                    gain.gain.setValueAtTime(0.25, now);
                    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
                    osc.start(now);
                    osc.stop(now + 0.22);
                }} else if (type === 'bat_hit') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(160, now);
                    osc.frequency.linearRampToValueAtTime(60, now + 0.15);
                    gain.gain.setValueAtTime(0.3, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.15);
                    osc.start(now);
                    osc.stop(now + 0.15);
                }} else if (type === 'blaster') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(880, now);
                    osc.frequency.exponentialRampToValueAtTime(180, now + 0.14);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.14);
                    osc.start(now);
                    osc.stop(now + 0.14);
                }} else if (type === 'flame') {{
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(90, now);
                    osc.frequency.linearRampToValueAtTime(180, now + 0.08);
                    gain.gain.setValueAtTime(0.08, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.08);
                    osc.start(now);
                    osc.stop(now + 0.08);
                }} else if (type === 'explosion') {{
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(120, now);
                    osc.frequency.exponentialRampToValueAtTime(30, now + 0.35);
                    gain.gain.setValueAtTime(0.35, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.35);
                    osc.start(now);
                    osc.stop(now + 0.35);
                }} else if (type === 'hurt') {{
                    osc.type = 'square';
                    osc.frequency.setValueAtTime(220, now);
                    osc.frequency.exponentialRampToValueAtTime(70, now + 0.2);
                    gain.gain.setValueAtTime(0.25, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
                    osc.start(now);
                    osc.stop(now + 0.2);
                }} else if (type === 'pickup') {{
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(340, now);
                    osc.frequency.setValueAtTime(440, now + 0.07);
                    osc.frequency.setValueAtTime(660, now + 0.14);
                    gain.gain.setValueAtTime(0.2, now);
                    gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
                    osc.start(now);
                    osc.stop(now + 0.25);
                }}
            }} catch(e) {{}}
        }}

        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false;

        const V_WIDTH = 480;
        const V_HEIGHT = 270;
        const GRAVITY = 820;
        const LEVEL_WIDTH = 3200;
        const LEVEL_HEIGHT = 900;

        const keys = {{}};
        window.addEventListener('keydown', e => {{
            keys[e.code] = true;
            getAudioContext();

            if (e.code === 'Digit1') switchWeapon(0);
            if (e.code === 'Digit2') switchWeapon(1);
            if (e.code === 'Digit3') switchWeapon(2);
            if (e.code === 'Digit4') switchWeapon(3);
            if (e.code === 'KeyQ') nextWeapon();
            if (e.code === 'KeyF') toggleChassis();
            if (e.code === 'KeyM') {{
                soundEnabled = !soundEnabled;
                showNotification("Audio: " + (soundEnabled ? "ON" : "MUTED"));
            }}
        }});
        window.addEventListener('keyup', e => {{ keys[e.code] = false; }});

        // Player with 1.2s strict I-Frames & Humanoid Gait
        const player = {{
            x: 80,
            y: 720,
            vx: 0,
            vy: 0,
            w: 20,
            h: 28,
            facing: 1,
            isGrounded: false,
            hp: 100,
            maxHp: 100,
            ep: 100,
            maxEp: 100,
            iFrameTimer: 0, // Strict I-Frame immunity
            chassis: 'damaged',
            canDoubleJump: true,
            hasDoubleJumped: false,
            dashCooldown: 0,
            isDashing: false,
            dashTime: 0,
            isSprinting: false,
            isCrouching: false,
            weapons: ['pan', 'bat', 'blaster', 'flamethrower'],
            currentWeaponIdx: 0,
            attackTimer: 0,
            attackType: null,
            animTimer: 0,
            leanAngle: 0,
            grappleActive: false,
            grappleTarget: null
        }};

        function toggleChassis() {{
            player.chassis = (player.chassis === 'damaged') ? 'standard' : 'damaged';
            playSound('pickup');
            showNotification("Chassis Mode: " + (player.chassis === 'damaged' ? "DAMAGED (Loose Copper Wires)" : "STANDARD (Titanium Refit)"));
        }}

        function switchWeapon(idx) {{
            if (idx >= 0 && idx < player.weapons.length) {{
                player.currentWeaponIdx = idx;
                updateWeaponUI();
                playSound('pickup');
            }}
        }}

        function nextWeapon() {{
            player.currentWeaponIdx = (player.currentWeaponIdx + 1) % player.weapons.length;
            updateWeaponUI();
            playSound('pickup');
        }}

        function updateWeaponUI() {{
            const wName = player.weapons[player.currentWeaponIdx];
            const iconEl = document.getElementById('weapon-icon');
            const nameEl = document.getElementById('weapon-name');
            const subEl = document.getElementById('weapon-sub');

            if (wName === 'pan') {{
                iconEl.src = ASSETS['cyber_pan_32x32'];
                nameEl.textContent = "Cyber Frying Pan";
                nameEl.style.color = "#f59e0b";
                subEl.textContent = "[X] Melee Blunt · Deflect & Heavy Knockback";
            }} else if (wName === 'bat') {{
                iconEl.src = ASSETS['metal_bat_32x32'];
                nameEl.textContent = "Reinforced Metal Bat";
                nameEl.style.color = "#38bdf8";
                subEl.textContent = "[X] Melee Slam · High Damage & Break Walls";
            }} else if (wName === 'blaster') {{
                iconEl.src = ASSETS['laser_blaster_arm_32x32'];
                nameEl.textContent = "Laser Blaster Arm";
                nameEl.style.color = "#06b6d4";
                subEl.textContent = "[Z] Ranged Plasma Beam · 12 Core Energy";
            }} else if (wName === 'flamethrower') {{
                iconEl.src = ASSETS['flamethrower_32x32'];
                nameEl.textContent = "Plasma Flamethrower";
                nameEl.style.color = "#ef4444";
                subEl.textContent = "[Z] Continuous Thermal Jet · Burns Bio-Obstacles";
            }}
        }}

        // Platforms & Level Layout with Interactive Crushed Car Obstacle
        const platforms = [
            {{ x: 0, y: 780, w: 600, h: 120, type: 'scrap_ground' }},
            {{ x: 0, y: 350, w: 40, h: 430, type: 'wall' }},

            // CRUSHED CAR OBSTACLE IN TUTORIAL ZONE (x: 260, y: 752)
            {{ x: 260, y: 752, w: 56, h: 28, type: 'crushed_car' }},

            {{ x: 420, y: 680, w: 120, h: 18, type: 'girder' }},
            {{ x: 560, y: 600, w: 130, h: 18, type: 'girder' }},

            {{ x: 160, y: 360, w: 260, h: 40, type: 'hazard_piston', timer: 0 }},

            {{ x: 550, y: 780, w: 600, h: 120, type: 'scrap_ground' }},
            {{ x: 740, y: 520, w: 130, h: 18, type: 'girder' }},
            {{ x: 920, y: 440, w: 140, h: 18, type: 'girder' }},

            {{ x: 760, y: 330, w: 280, h: 20, type: 'girder' }},
            {{ x: 760, y: 230, w: 20, h: 100, type: 'breakable_wall', hp: 3 }},
            {{ x: 600, y: 230, w: 160, h: 20, type: 'secret_ground' }},
            {{ x: 600, y: 130, w: 20, h: 100, type: 'wall' }},
            {{ x: 600, y: 130, w: 200, h: 20, type: 'wall' }},

            {{ x: 1150, y: 820, w: 900, h: 80, type: 'toxic_sludge' }},
            {{ x: 1200, y: 700, w: 120, h: 18, type: 'girder' }},
            {{ x: 1380, y: 630, w: 140, h: 18, type: 'girder' }},
            {{ x: 1580, y: 560, w: 130, h: 18, type: 'girder' }},
            {{ x: 1770, y: 640, w: 140, h: 18, type: 'girder' }},
            {{ x: 1950, y: 720, w: 150, h: 18, type: 'girder' }},

            {{ x: 1320, y: 420, w: 240, h: 20, type: 'crane_girder' }},
            {{ x: 1680, y: 360, w: 220, h: 20, type: 'crane_girder' }},
            {{ x: 1500, y: 220, w: 20, h: 20, type: 'grapple_ring' }},
            {{ x: 1780, y: 180, w: 20, h: 20, type: 'grapple_ring' }},

            {{ x: 2100, y: 760, w: 1000, h: 140, type: 'boss_floor' }},
            {{ x: 2100, y: 400, w: 30, h: 360, type: 'boss_gate_left' }},
            {{ x: 3080, y: 400, w: 30, h: 360, type: 'boss_gate_right' }},
            {{ x: 2100, y: 400, w: 1000, h: 30, type: 'ceiling' }},

            {{ x: 2250, y: 640, w: 140, h: 18, type: 'girder' }},
            {{ x: 2790, y: 640, w: 140, h: 18, type: 'girder' }},
            {{ x: 2520, y: 550, w: 140, h: 18, type: 'girder' }},
            {{ x: 3110, y: 760, w: 90, h: 140, type: 'exit_shaft' }}
        ];

        // In-Game Holographic Tutorial Triggers (Including Crushed Car Jump Prompt)
        const tutorials = [
            {{ x: 100, y: 710, key: "A / D", title: "MOVE CHASSIS", sub: "Hold [SHIFT] to Sprint" }},
            {{ x: 285, y: 690, key: "[SPACE] OR [W]", title: "JUMP OVER THE CRUSHED CAR", sub: "Tap in mid-air to Double Jump" }},
            {{ x: 480, y: 620, key: "[C]", title: "DASH THROUGH HAZARDS", sub: "Phases through enemy shots & traps" }},
            {{ x: 740, y: 470, key: "[X] / CLICK", title: "MELEE COMBAT", sub: "Cyber Pan clangs & deflects enemy shots" }},
            {{ x: 1040, y: 410, key: "[Z] / CLICK", title: "LASER BLASTER ARM", sub: "High velocity cyan plasma pulses" }},
            {{ x: 1380, y: 710, key: "[Q] OR [1-4]", title: "WEAPONS ARSENAL", sub: "[G] Grenade · [E] Grappling Hook" }}
        ];

        const particles = [];
        const projectiles = [];
        const pickups = [
            {{ x: 670, y: 195, w: 24, h: 24, type: 'pan_pickup', name: 'Cyber Frying Pan + Easter Egg Spoon', collected: false }}
        ];

        function createSparks(x, y, count = 6, color = '#38bdf8') {{
            for (let i = 0; i < count; i++) {{
                particles.push({{
                    x: x, y: y,
                    vx: (Math.random() - 0.5) * 220,
                    vy: (Math.random() - 0.8) * 180,
                    life: 0.3 + Math.random() * 0.3,
                    maxLife: 0.5,
                    color: color,
                    size: 1 + Math.random() * 2
                }});
            }}
        }}

        function createExplosion(x, y) {{
            playSound('explosion');
            for (let i = 0; i < 24; i++) {{
                particles.push({{
                    x: x, y: y,
                    vx: (Math.random() - 0.5) * 320,
                    vy: (Math.random() - 0.5) * 320,
                    life: 0.4 + Math.random() * 0.3,
                    maxLife: 0.7,
                    color: ['#f97316', '#ef4444', '#facc15', '#94a3b8'][Math.floor(Math.random() * 4)],
                    size: 2 + Math.random() * 4
                }});
            }}
        }}

        // Enemies
        const enemies = [
            {{ id: 1, type: 'drone', x: 740, y: 550, startX: 620, endX: 860, vx: 50, vy: 0, hp: 20, maxHp: 20, shootTimer: 2.0, animTimer: 0 }},
            {{ id: 2, type: 'drone', x: 1300, y: 520, startX: 1200, endX: 1450, vx: 60, vy: 0, hp: 20, maxHp: 20, shootTimer: 1.5, animTimer: 0 }},
            {{ id: 3, type: 'drone', x: 1720, y: 480, startX: 1600, endX: 1850, vx: 55, vy: 0, hp: 20, maxHp: 20, shootTimer: 2.2, animTimer: 0 }},
            {{ id: 4, type: 'crawler', x: 420, y: 755, startX: 340, endX: 520, vx: 40, vy: 0, hp: 35, maxHp: 35, w: 26, h: 18, animTimer: 0 }},
            {{ id: 5, type: 'crawler', x: 800, y: 755, startX: 650, endX: 950, vx: 45, vy: 0, hp: 35, maxHp: 35, w: 26, h: 18, animTimer: 0 }}
        ];

        // Boss
        const boss = {{
            active: false,
            dead: false,
            x: 2750,
            y: 640,
            vx: 0,
            vy: 0,
            w: 48,
            h: 56,
            hp: 200,
            maxHp: 200,
            state: 'idle',
            timer: 2.0,
            facing: -1,
            animTimer: 0
        }};

        const camera = {{
            x: 0,
            y: 0,
            targetX: 0,
            targetY: 0
        }};

        function showNotification(text, title = "SYSTEM MESSAGE") {{
            const box = document.getElementById('dialogue-box');
            document.getElementById('dialogue-title').textContent = title;
            document.getElementById('dialogue-text').textContent = text;
            box.style.display = 'block';
            clearTimeout(box.timer);
            box.timer = setTimeout(() => {{ box.style.display = 'none'; }}, 4000);
        }}

        let lastTime = 0;
        function initGame() {{
            updateWeaponUI();
            showNotification("SCRAPBORN // Zone 1: The Heap. Jump over the crushed car to begin!", "SYSTEM READY");
            requestAnimationFrame(gameLoop);
        }}

        function gameLoop(time) {{
            if (!lastTime) lastTime = time;
            const dt = Math.min((time - lastTime) / 1000, 0.05);
            lastTime = time;

            update(dt);
            render();

            requestAnimationFrame(gameLoop);
        }}

        // Strict damage with I-Frames & Knockback (NO HP MELT!)
        function damagePlayer(amount, knockbackDir = 0) {{
            if (player.iFrameTimer > 0) return; // Strict immunity!
            player.iFrameTimer = 1.2; // 1.2 seconds of i-frames
            player.hp = Math.max(0, player.hp - amount);

            // Knockback separates player from enemy
            player.vx = knockbackDir * 280;
            player.vy = -180;
            playSound('hurt');
            createSparks(player.x + 10, player.y + 10, 8, '#ef4444');

            if (player.hp <= 0) {{
                player.hp = player.maxHp;
                player.x = 80;
                player.y = 720;
                player.iFrameTimer = 1.5;
                showNotification("CRITICAL SHUTDOWN // Rebooting at Compactor Pit...");
            }}
        }}

        function update(dt) {{
            if (player.iFrameTimer > 0) player.iFrameTimer -= dt;
            player.ep = Math.min(player.maxEp, player.ep + dt * 14);

            document.getElementById('hp-bar').style.width = (player.hp / player.maxHp * 100) + '%';
            document.getElementById('ep-bar').style.width = (player.ep / player.maxEp * 100) + '%';
            document.getElementById('hp-text').textContent = Math.ceil(player.hp) + ' / ' + player.maxHp;
            document.getElementById('ep-text').textContent = Math.ceil(player.ep) + ' / ' + player.maxEp;

            if (player.dashCooldown > 0) player.dashCooldown -= dt;
            if (player.isDashing) {{
                player.dashTime -= dt;
                createSparks(player.x + 10, player.y + 14, 2, '#38bdf8');
                if (player.dashTime <= 0) player.isDashing = false;
            }}

            if (!player.isDashing) {{
                player.isCrouching = player.isGrounded && (keys['KeyS'] || keys['ArrowDown']);
                player.h = player.isCrouching ? 16 : 28;
                player.isSprinting = (keys['ShiftLeft'] || keys['ShiftRight']) && !player.isCrouching;
                const speed = player.isCrouching ? 55 : (player.isSprinting ? 230 : 145);

                let moveX = 0;
                if (keys['ArrowLeft'] || keys['KeyA']) {{
                    moveX -= 1;
                    player.facing = -1;
                }}
                if (keys['ArrowRight'] || keys['KeyD']) {{
                    moveX += 1;
                    player.facing = 1;
                }}

                player.vx = moveX * speed;
                player.leanAngle = moveX * (player.isSprinting ? 0.08 : 0.02);

                if ((keys['KeyC'] || keys['KeyK']) && player.dashCooldown <= 0 && player.ep >= 15) {{
                    player.isDashing = true;
                    player.dashTime = 0.22;
                    player.dashCooldown = 0.65;
                    player.ep -= 15;
                    player.vx = player.facing * 420;
                    player.vy = 0;
                    playSound('dash');
                }}

                if ((keys['Space'] || keys['KeyW'] || keys['ArrowUp']) && !player.isCrouching) {{
                    if (player.isGrounded) {{
                        player.vy = -385;
                        player.isGrounded = false;
                        player.hasDoubleJumped = false;
                        playSound('jump');
                        createSparks(player.x + 10, player.y + 26, 4, '#e2e8f0');
                        keys['Space'] = false;
                        keys['KeyW'] = false;
                        keys['ArrowUp'] = false;
                    }} else if (player.canDoubleJump && !player.hasDoubleJumped && player.ep >= 10) {{
                        player.vy = -340;
                        player.hasDoubleJumped = true;
                        player.ep -= 10;
                        playSound('jump');
                        createSparks(player.x + 10, player.y + 26, 6, '#38bdf8');
                        keys['Space'] = false;
                        keys['KeyW'] = false;
                        keys['ArrowUp'] = false;
                    }}
                }}
            }}

            // Attacks
            if (player.attackTimer > 0) {{
                player.attackTimer -= dt;
            }} else {{
                if (keys['KeyX'] || keys['KeyJ']) {{
                    const activeWeapon = player.weapons[player.currentWeaponIdx];
                    const isBat = (activeWeapon === 'bat');
                    player.attackDuration = isBat ? 0.30 : 0.22;
                    player.attackTimer = player.attackDuration;
                    player.attackType = 'melee';

                    if (isBat) playSound('bat_hit');
                    else playSound('pan_clang');

                    const reach = isBat ? 64 : 50;
                    const hitX = player.facing === 1 ? player.x + player.w - 4 : player.x - reach + 4;
                    const hitH = isBat ? (player.h + 20) : (player.h + 12);
                    const hitRect = {{ x: hitX, y: player.y - (isBat ? 10 : 6), w: reach, h: hitH }};

                    // Spawn dynamic wind slash particles in facing direction
                    for (let i = 0; i < 6; i++) {{
                        particles.push({{
                            x: player.x + 10 + player.facing * (14 + i * (reach / 6)),
                            y: player.y + 6 + (Math.random() - 0.5) * 16,
                            vx: player.facing * (160 + Math.random() * 80),
                            vy: (Math.random() - 0.5) * 50,
                            color: isBat ? '#fbbf24' : '#38bdf8',
                            size: Math.random() * 2.5 + 2,
                            life: 0.18,
                            maxLife: 0.18
                        }});
                    }}

                    platforms.forEach(p => {{
                        if (p.type === 'breakable_wall' && checkOverlap(hitRect, p)) {{
                            p.hp -= 1;
                            createSparks(hitRect.x + 15, hitRect.y + 15, 8, '#f59e0b');
                            if (p.hp <= 0) {{
                                createExplosion(p.x + 10, p.y + 50);
                                p.destroyed = true;
                                showNotification("Secret passageway revealed! Cyber Frying Pan discovered inside!");
                            }}
                        }}
                    }});

                    enemies.forEach(e => {{
                        if (e.hp > 0 && checkOverlap(hitRect, {{ x: e.x, y: e.y, w: 26, h: 26 }})) {{
                            const dmg = (activeWeapon === 'bat') ? 45 : 28;
                            e.hp -= dmg;
                            createSparks(e.x + 10, e.y + 10, 8, '#ef4444');
                            e.vx = player.facing * 160;
                            if (e.hp <= 0) createExplosion(e.x + 12, e.y + 12);
                        }}
                    }});

                    if (boss.active && !boss.dead && checkOverlap(hitRect, {{ x: boss.x, y: boss.y, w: boss.w, h: boss.h }})) {{
                        boss.hp -= (activeWeapon === 'bat') ? 36 : 24;
                        createSparks(boss.x + 20, boss.y + 20, 10, '#ef4444');
                        if (boss.hp <= 0) {{
                            boss.dead = true;
                            createExplosion(boss.x + 24, boss.y + 28);
                            document.getElementById('boss-hud').style.display = 'none';
                            showNotification("THE CRUSHER DEFEATED! Laser Blaster Arm permanently acquired!", "VICTORY");
                        }}
                    }}
                }}

                if (keys['KeyZ'] || keys['KeyL']) {{
                    const activeWeapon = player.weapons[player.currentWeaponIdx];
                    if (activeWeapon === 'blaster' && player.ep >= 12) {{
                        player.attackTimer = 0.2;
                        player.attackType = 'shoot';
                        player.ep -= 12;
                        playSound('blaster');
                        projectiles.push({{
                            x: player.facing === 1 ? player.x + player.w + 4 : player.x - 12,
                            y: player.y + 10,
                            vx: player.facing * 480,
                            vy: 0,
                            w: 12,
                            h: 6,
                            color: '#38bdf8',
                            life: 1.2
                        }});
                    }} else if (activeWeapon === 'flamethrower' && player.ep >= 1.5) {{
                        player.attackTimer = 0.12;
                        player.attackDuration = 0.12;
                        player.attackType = 'flame';
                        player.ep -= 18 * dt;
                        playSound('flame');
                        const handY = player.isCrouching ? player.y + 14 : player.y + 8;
                        for (let i = 0; i < 2; i++) {{
                            projectiles.push({{
                                x: player.facing === 1 ? player.x + player.w + 2 : player.x - 10,
                                y: handY + (Math.random() - 0.5) * 6,
                                vx: player.facing * (240 + Math.random() * 80),
                                vy: (Math.random() - 0.5) * 40,
                                w: 8 + Math.random() * 4,
                                h: 8 + Math.random() * 4,
                                color: Math.random() > 0.4 ? '#f97316' : '#ef4444',
                                life: 0.32,
                                isFlame: true
                            }});
                        }}
                    }}
                }}
            }}

            if (!player.isDashing && !player.grappleActive) {{
                player.vy += GRAVITY * dt;
            }}

            player.x += player.vx * dt;
            handleHorizontalCollisions();

            player.y += player.vy * dt;
            player.isGrounded = false;
            handleVerticalCollisions();

            if (player.x < 40) player.x = 40;
            if (player.x > LEVEL_WIDTH - 60) player.x = LEVEL_WIDTH - 60;
            if (player.y > LEVEL_HEIGHT - 60) {{
                damagePlayer(25, 0);
                player.y = 700;
                player.vy = 0;
            }}

            // Hazard cycle
            platforms.forEach(p => {{
                if (p.type === 'hazard_piston') {{
                    p.timer = (p.timer || 0) + dt;
                    const cycle = p.timer % 3.5;
                    if (cycle > 2.5) {{
                        p.h = 40 + (cycle - 2.5) * 220;
                        if (checkOverlap(player, p)) {{
                            damagePlayer(30, 0);
                        }}
                    }} else {{
                        p.h = 40;
                    }}
                }}
                if (p.type === 'toxic_sludge' && checkOverlap(player, p)) {{
                    damagePlayer(20, 0);
                    player.vy = -140;
                }}
            }});

            pickups.forEach(pu => {{
                if (!pu.collected && checkOverlap(player, pu)) {{
                    pu.collected = true;
                    playSound('pickup');
                    createSparks(pu.x + 12, pu.y + 12, 16, '#facc15');
                    showNotification("DISCOVERED: " + pu.name + "! Press [1] to equip pan!");
                }}
            }});

            // Projectiles
            for (let i = projectiles.length - 1; i >= 0; i--) {{
                const pr = projectiles[i];
                pr.life -= dt;
                pr.x += pr.vx * dt;
                pr.y += pr.vy * dt;

                let hit = false;
                enemies.forEach(e => {{
                    if (e.hp > 0 && checkOverlap(pr, {{ x: e.x, y: e.y, w: 26, h: 26 }})) {{
                        e.hp -= pr.isFlame ? 14 : 24;
                        createSparks(pr.x, pr.y, 4, pr.color);
                        hit = true;
                    }}
                }});

                if (boss.active && !boss.dead && checkOverlap(pr, {{ x: boss.x, y: boss.y, w: boss.w, h: boss.h }})) {{
                    boss.hp -= pr.isFlame ? 12 : 20;
                    createSparks(pr.x, pr.y, 6, pr.color);
                    hit = true;
                }}

                if (hit || pr.life <= 0) projectiles.splice(i, 1);
            }}

            // Enemies Update with Safe Hitbox & I-Frames Check
            enemies.forEach(e => {{
                if (e.hp <= 0) return;
                e.animTimer = (e.animTimer || 0) + dt;
                if (e.type === 'drone') {{
                    e.x += e.vx * dt;
                    if (e.x > e.endX) e.vx = -Math.abs(e.vx);
                    if (e.x < e.startX) e.vx = Math.abs(e.vx);
                }} else if (e.type === 'crawler') {{
                    e.x += e.vx * dt;
                    if (e.x > e.endX) e.vx = -Math.abs(e.vx);
                    if (e.x < e.startX) e.vx = Math.abs(e.vx);
                }}

                // Check collision with player -> Call damagePlayer (triggers 1.2s i-frame!)
                if (checkOverlap(player, {{ x: e.x, y: e.y, w: 24, h: 24 }})) {{
                    const kbDir = player.x > e.x ? 1 : -1;
                    damagePlayer(18, kbDir);
                }}
            }});

            // Boss AI & Safe Damage
            if (player.x > 2180 && !boss.active && !boss.dead) {{
                boss.active = true;
                document.getElementById('boss-hud').style.display = 'flex';
                showNotification("WARNING: THE CRUSHER COMPACTOR TITAN AWAKENED!", "BOSS ALERT");
            }}

            if (boss.active && !boss.dead) {{
                boss.animTimer += dt;
                document.getElementById('boss-bar-fill').style.width = (boss.hp / boss.maxHp * 100) + '%';
                boss.facing = player.x < boss.x ? -1 : 1;
                boss.timer -= dt;

                if (boss.timer <= 0) {{
                    boss.timer = 2.8;
                    if (Math.random() < 0.5) {{
                        boss.state = 'charge';
                        boss.vx = boss.facing * 240;
                    }} else {{
                        boss.state = 'slam';
                        boss.vy = -340;
                    }}
                }}

                boss.vy += GRAVITY * dt;
                boss.x += boss.vx * dt;
                boss.y += boss.vy * dt;

                if (boss.y + boss.h > 760) {{
                    boss.y = 760 - boss.h;
                    boss.vy = 0;
                    if (boss.state === 'slam') {{
                        playSound('explosion');
                        createExplosion(boss.x + 24, boss.y + 50);
                        boss.state = 'idle';
                        boss.vx = 0;
                    }}
                }}

                if (boss.x < 2140) {{ boss.x = 2140; boss.vx = 0; }}
                if (boss.x > 3020) {{ boss.x = 3020; boss.vx = 0; }}

                if (checkOverlap(player, {{ x: boss.x, y: boss.y, w: boss.w, h: boss.h }})) {{
                    const kbDir = player.x > boss.x ? 1 : -1;
                    damagePlayer(28, kbDir);
                }}
            }}

            camera.targetX = player.x + player.w / 2 - V_WIDTH / 2;
            camera.targetY = player.y + player.h / 2 - V_HEIGHT / 2;
            camera.targetX = Math.max(0, Math.min(camera.targetX, LEVEL_WIDTH - V_WIDTH));
            camera.targetY = Math.max(0, Math.min(camera.targetY, LEVEL_HEIGHT - V_HEIGHT));
            camera.x += (camera.targetX - camera.x) * 0.12;
            camera.y += (camera.targetY - camera.y) * 0.12;
        }}

        function handleHorizontalCollisions() {{
            platforms.forEach(p => {{
                if (p.destroyed || p.type === 'hazard_piston' || p.type === 'toxic_sludge' || p.type === 'grapple_ring') return;
                if (checkOverlap(player, p)) {{
                    if (player.vx > 0) player.x = p.x - player.w;
                    else if (player.vx < 0) player.x = p.x + p.w;
                    player.vx = 0;
                }}
            }});
        }}

        function handleVerticalCollisions() {{
            platforms.forEach(p => {{
                if (p.destroyed || p.type === 'hazard_piston' || p.type === 'toxic_sludge' || p.type === 'grapple_ring') return;
                if (checkOverlap(player, p)) {{
                    if (player.vy > 0 && (player.y + player.h - player.vy * 0.05) <= p.y + 12) {{
                        player.y = p.y - player.h;
                        player.vy = 0;
                        player.isGrounded = true;
                    }} else if (player.vy < 0) {{
                        player.y = p.y + p.h;
                        player.vy = 0;
                    }}
                }}
            }});
        }}

        function checkOverlap(a, b) {{
            return a.x < b.x + b.w &&
                   a.x + (a.w || 20) > b.x &&
                   a.y < b.y + b.h &&
                   a.y + (a.h || 28) > b.y;
        }}

        function render() {{
            ctx.clearRect(0, 0, V_WIDTH, V_HEIGHT);

            ctx.save();
            ctx.translate(-Math.floor(camera.x), -Math.floor(camera.y));

            // 100% STATIC LEVEL BACKDROP (Aligned to floor line y = 780, never shifts or floats!)
            if (images['level_heap_backdrop_3200x900']) {{
                ctx.drawImage(images['level_heap_backdrop_3200x900'], 0, 0);
            }}

            drawPlatforms();
            drawTutorials();
            drawPickups();
            drawEnemies();
            drawPlayer();
            drawProjectiles();
            drawParticles();

            ctx.restore();
        }}

        function renderParallaxBackground() {{
            // Layer 1: Distant Sky stays at horizon
            const off1 = (camera.x * 0.05) % 1920;
            const y1 = Math.floor((camera.y - 630) * 0.03);
            if (images['bg_layer1_sky']) {{
                ctx.drawImage(images['bg_layer1_sky'], -off1, y1 - 40, 1920, 360);
                if (off1 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer1_sky'], 1920 - off1, y1 - 40, 1920, 360);
            }}

            // Layer 2: Distant scrap silhouette
            const off2 = (camera.x * 0.18) % 1920;
            const y2 = Math.floor((camera.y - 630) * 0.10);
            if (images['bg_layer2_distant_scrap']) {{
                ctx.drawImage(images['bg_layer2_distant_scrap'], -off2, y2 - 20, 1920, 320);
                if (off2 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer2_distant_scrap'], 1920 - off2, y2 - 20, 1920, 320);
            }}

            // Layer 3: Midground Towering Cranes & Pipes (Locked Vertically to the Ground Level!)
            const off3 = (camera.x * 0.45) % 1920;
            const y3 = Math.floor((780 - 540) - camera.y);
            if (images['bg_layer3_midground_pipes']) {{
                ctx.drawImage(images['bg_layer3_midground_pipes'], -off3, y3, 1920, 540);
                if (off3 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer3_midground_pipes'], 1920 - off3, y3, 1920, 540);
            }}

            // Layer 4: Foreground Chainlink Fences, Tire Piles & Hazard Signs (100% Fixed to Ground Floor!)
            const off4 = (camera.x * 0.75) % 1920;
            const y4 = Math.floor((780 - 540) - camera.y);
            if (images['bg_layer4_foreground_girders']) {{
                ctx.drawImage(images['bg_layer4_foreground_girders'], -off4, y4, 1920, 540);
                if (off4 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer4_foreground_girders'], 1920 - off4, y4, 1920, 540);
            }}
        }}

        function drawTutorials() {{
            tutorials.forEach(t => {{
                const dist = Math.hypot(player.x - t.x, player.y - t.y);
                if (dist < 180) {{
                    const alpha = Math.max(0, 1 - dist / 180);
                    ctx.save();
                    ctx.globalAlpha = alpha;

                    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(t.x - 75, t.y - 48, 150, 38);
                    ctx.fillRect(t.x - 75, t.y - 48, 150, 38);

                    ctx.fillStyle = '#06b6d4';
                    ctx.fillRect(t.x - 75, t.y - 48, 4, 4);
                    ctx.fillRect(t.x + 71, t.y - 48, 4, 4);

                    ctx.font = 'bold 9px monospace';
                    ctx.fillStyle = '#38bdf8';
                    ctx.textAlign = 'center';
                    ctx.fillText(t.key, t.x, t.y - 34);

                    ctx.font = '8px sans-serif';
                    ctx.fillStyle = '#f8fafc';
                    ctx.fillText(t.title, t.x, t.y - 22);

                    ctx.font = '7px sans-serif';
                    ctx.fillStyle = '#94a3b8';
                    ctx.fillText(t.sub, t.x, t.y - 12);

                    ctx.restore();
                }}
            }});
        }}

        function drawPlatforms() {{
            platforms.forEach(p => {{
                if (p.destroyed) return;
                if (p.type === 'crushed_car') {{
                    if (images['crushed_car_obstacle']) {{
                        ctx.drawImage(images['crushed_car_obstacle'], p.x - 4, p.y - 4, 64, 32);
                    }}
                }} else if (p.type === 'scrap_ground' || p.type === 'boss_floor') {{
                    ctx.fillStyle = '#261b14';
                    ctx.fillRect(p.x, p.y, p.w, p.h);
                    ctx.fillStyle = '#b45309';
                    ctx.fillRect(p.x, p.y, p.w, 4);
                }} else if (p.type === 'girder' || p.type === 'crane_girder') {{
                    ctx.fillStyle = '#334155';
                    ctx.fillRect(p.x, p.y, p.w, p.h);
                    ctx.fillStyle = '#64748b';
                    ctx.fillRect(p.x, p.y, p.w, 3);
                }} else if (p.type === 'hazard_piston') {{
                    ctx.fillStyle = '#dc2626';
                    ctx.fillRect(p.x, p.y, p.w, p.h);
                    ctx.fillStyle = '#facc15';
                    ctx.fillRect(p.x, p.y + p.h - 8, p.w, 8);
                }} else if (p.type === 'toxic_sludge') {{
                    ctx.fillStyle = '#14532d';
                    ctx.fillRect(p.x, p.y, p.w, p.h);
                    ctx.fillStyle = '#22c55e';
                    ctx.fillRect(p.x, p.y, p.w, 6);
                }} else if (p.type === 'breakable_wall') {{
                    ctx.fillStyle = '#78350f';
                    ctx.fillRect(p.x, p.y, p.w, p.h);
                    ctx.strokeStyle = '#f59e0b';
                    ctx.strokeRect(p.x, p.y, p.w, p.h);
                }} else {{
                    ctx.fillStyle = '#1e293b';
                    ctx.fillRect(p.x, p.y, p.w, p.h);
                }}
            }});
        }}

        function drawPickups() {{
            pickups.forEach(pu => {{
                if (pu.collected) return;
                const bob = Math.sin(Date.now() / 250) * 4;
                if (images['cyber_pan_32x32']) {{
                    ctx.drawImage(images['cyber_pan_32x32'], pu.x - 4, pu.y - 4 + bob, 32, 32);
                }}
            }});
        }}

        function drawEnemies() {{
            enemies.forEach(e => {{
                if (e.hp <= 0) return;
                ctx.save();
                ctx.translate(e.x + 16, e.y + 16);
                ctx.scale(e.vx > 0 ? 1 : -1, 1);

                if (e.type === 'drone') {{
                    const frame = Math.floor(Date.now() / 90) % 4;
                    if (images['enemy_junk_drone_strip4']) {{
                        ctx.drawImage(images['enemy_junk_drone_strip4'], frame * 32, 0, 32, 32, -16, -16, 32, 32);
                    }}
                }} else if (e.type === 'crawler') {{
                    const frame = Math.floor(Date.now() / 110) % 4;
                    if (images['enemy_scrap_crawler_strip4']) {{
                        ctx.drawImage(images['enemy_scrap_crawler_strip4'], frame * 32, 0, 32, 32, -16, -16, 32, 32);
                    }}
                }}
                ctx.restore();
            }});

            if (boss.active && !boss.dead) {{
                ctx.save();
                ctx.translate(boss.x + boss.w / 2, boss.y + boss.h / 2);
                ctx.scale(boss.facing === 1 ? -1 : 1, 1);

                const frame = Math.floor(Date.now() / 140) % 4;
                if (images['boss_crusher_strip4']) {{
                    ctx.drawImage(images['boss_crusher_strip4'], frame * 64, 0, 64, 64, -32, -32, 64, 64);
                }}
                ctx.restore();
            }}
        }}

        function drawPlayer() {{
            ctx.save();
            ctx.translate(Math.floor(player.x + 10), Math.floor(player.y + (player.isCrouching ? 8 : 14)));
            ctx.scale(player.facing, 1);
            ctx.rotate(player.leanAngle);

            // Strict I-Frames Flashing
            if (player.iFrameTimer > 0 && Math.floor(Date.now() / 70) % 2 === 0) {{
                ctx.globalAlpha = 0.35;
            }}

            const isDmg = (player.chassis === 'damaged');
            const prefix = isDmg ? 'robot_damaged_' : 'robot_standard_';

            // 1. UNIFIED ATTACK ANIMATION (Character visibly swings arm holding weapon from hand level!)
            if (player.attackTimer > 0) {{
                const activeWeapon = player.weapons[player.currentWeaponIdx];
                const totalDur = player.attackDuration || 0.24;
                const progress = Math.max(0, Math.min(1, 1 - (player.attackTimer / totalDur)));
                const fIdx = Math.min(3, Math.floor(progress * 4));

                if (activeWeapon === 'pan') {{
                    const sheet = images[prefix + 'attack_pan_strip4'];
                    if (sheet) ctx.drawImage(sheet, fIdx * 48, 0, 48, 32, -16, -16, 48, 32);
                }} else if (activeWeapon === 'bat') {{
                    const sheet = images[prefix + 'attack_bat_strip4'];
                    if (sheet) ctx.drawImage(sheet, fIdx * 56, 0, 56, 36, -16, -18, 56, 36);
                }} else if (activeWeapon === 'blaster') {{
                    const sheet = images[prefix + 'shoot_strip4'];
                    if (sheet) ctx.drawImage(sheet, fIdx * 40, 0, 40, 32, -16, -16, 40, 32);
                }} else if (activeWeapon === 'flamethrower') {{
                    const sheet = images[prefix + 'shoot_strip4'] || images[prefix + 'idle_strip4'];
                    if (sheet) ctx.drawImage(sheet, 0, 0, 32, 32, -16, -16, 32, 32);
                    const flameSheet = images['weapon_flamethrower_stream_strip4'];
                    if (flameSheet) ctx.drawImage(flameSheet, fIdx * 64, 0, 64, 32, 4, -16, 64, 32);
                }}
                ctx.restore();
                return;
            }}

            // 2. CROUCH ANIMATION
            if (player.isCrouching) {{
                const sheet = images[prefix + 'crouch_strip2'];
                const fIdx = Math.abs(player.vx) > 5 ? (Math.floor(Date.now() / 120) % 2) : 0;
                if (sheet) ctx.drawImage(sheet, fIdx * 32, 0, 32, 32, -16, -16, 32, 32);
                ctx.restore();
                return;
            }}

            // 3. DASH, JUMP, WALK, IDLE
            let sheet = null;
            let frameCount = 4;
            let frameSpeed = 120;

            if (player.isDashing) {{
                sheet = images['robot_dash_strip2'];
                frameCount = 2;
                frameSpeed = 80;
            }} else if (!player.isGrounded) {{
                sheet = images['robot_jump_strip3'];
                frameCount = 3;
                frameSpeed = 150;
            }} else if (Math.abs(player.vx) > 10) {{
                sheet = images[prefix + 'walk_strip8'];
                frameCount = 8;
                frameSpeed = player.isSprinting ? 75 : 110;
            }} else {{
                sheet = images[prefix + 'idle_strip4'];
                frameCount = 4;
                frameSpeed = 140;
            }}

            const frameIdx = Math.floor(Date.now() / frameSpeed) % frameCount;
            if (sheet) {{
                ctx.drawImage(sheet, frameIdx * 32, 0, 32, 32, -16, -16, 32, 32);
            }}

            ctx.restore();
            return;
        }}

        function drawProjectiles() {{
            projectiles.forEach(pr => {{
                ctx.fillStyle = pr.color;
                ctx.fillRect(pr.x, pr.y, pr.w, pr.h);
            }});
        }}

        function drawParticles() {{
            particles.forEach(p => {{
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.life / p.maxLife;
                ctx.fillRect(p.x, p.y, p.size, p.size);
            }});
            ctx.globalAlpha = 1.0;
        }}
    </script>
</body>
</html>
"""

demo_path = os.path.join(scratch_dir, "scrapborn_demo.html")
with open(demo_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated scrapborn_demo.html successfully with crushed car and clean humanoid walk!")
