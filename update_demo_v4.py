import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
demo_script = os.path.join(scratch_dir, "generate_demo.py")

with open(demo_script, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update player attack handling
old_attack_block = """                    player.attackTimer = 0.25;
                    player.attackType = 'melee';
                    const activeWeapon = player.weapons[player.currentWeaponIdx];

                    if (activeWeapon === 'pan') playSound('pan_clang');
                    else playSound('bat_hit');

                    const hitX = player.facing === 1 ? player.x + player.w : player.x - 30;
                    const hitRect = {{ x: hitX, y: player.y - 4, w: 34, h: player.h + 8 }};"""

new_attack_block = """                    const activeWeapon = player.weapons[player.currentWeaponIdx];
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
                    }}"""

assert old_attack_block in code, "old_attack_block not found!"
code = code.replace(old_attack_block, new_attack_block)
print("Replaced attack block in generate_demo.py")

# 2. Update damage
code = code.replace(
    "const dmg = (activeWeapon === 'bat') ? 30 : 20;",
    "const dmg = (activeWeapon === 'bat') ? 45 : 28;"
)
code = code.replace(
    "boss.hp -= (activeWeapon === 'bat') ? 22 : 14;",
    "boss.hp -= (activeWeapon === 'bat') ? 36 : 24;"
)

# 3. Update renderParallaxBackground
old_parallax = """        function renderParallaxBackground() {{
            const off1 = (camera.x * 0.05) % 1920;
            if (images['bg_layer1_sky']) {{
                ctx.drawImage(images['bg_layer1_sky'], -off1, 0, 1920, 270);
                if (off1 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer1_sky'], 1920 - off1, 0, 1920, 270);
            }}

            const off2 = (camera.x * 0.18) % 1920;
            if (images['bg_layer2_distant_scrap']) {{
                ctx.drawImage(images['bg_layer2_distant_scrap'], -off2, 0, 1920, 270);
                if (off2 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer2_distant_scrap'], 1920 - off2, 0, 1920, 270);
            }}

            const off3 = (camera.x * 0.45) % 1920;
            if (images['bg_layer3_midground_pipes']) {{
                ctx.drawImage(images['bg_layer3_midground_pipes'], -off3, 0, 1920, 270);
                if (off3 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer3_midground_pipes'], 1920 - off3, 0, 1920, 270);
            }}

            const off4 = (camera.x * 0.75) % 1920;
            if (images['bg_layer4_foreground_girders']) {{
                ctx.drawImage(images['bg_layer4_foreground_girders'], -off4, 0, 1920, 270);
                if (off4 > 1920 - V_WIDTH) ctx.drawImage(images['bg_layer4_foreground_girders'], 1920 - off4, 0, 1920, 270);
            }}
        }}"""

new_parallax = """        function renderParallaxBackground() {{
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
        }}"""

assert old_parallax in code, "old_parallax not found!"
code = code.replace(old_parallax, new_parallax)
print("Replaced renderParallaxBackground in generate_demo.py")

# 4. Update weapon swing in drawPlayer
old_draw_weapon = """            if (player.attackTimer > 0) {{
                const activeWeapon = player.weapons[player.currentWeaponIdx];
                let weaponSheet = null;
                let wFrames = 4;
                let wWidth = 48;

                if (activeWeapon === 'pan') weaponSheet = images['weapon_pan_swing_strip4'];
                else if (activeWeapon === 'bat') weaponSheet = images['weapon_bat_slam_strip4'];
                else if (activeWeapon === 'blaster') weaponSheet = images['weapon_blaster_shoot_strip4'];
                else if (activeWeapon === 'flamethrower') {{
                    weaponSheet = images['weapon_flamethrower_stream_strip4'];
                    wWidth = 64;
                }}

                if (weaponSheet) {{
                    const wIdx = Math.floor((1 - player.attackTimer / 0.25) * wFrames) % wFrames;
                    ctx.drawImage(weaponSheet, wIdx * wWidth, 0, wWidth, 32, 0, -16, wWidth, 32);
                }}
            }}"""

new_draw_weapon = """            if (player.attackTimer > 0) {{
                const activeWeapon = player.weapons[player.currentWeaponIdx];
                let weaponSheet = null;
                const isBat = (activeWeapon === 'bat');
                const isPan = (activeWeapon === 'pan');
                let wFrames = 4;
                let wWidth = isBat ? 56 : (activeWeapon === 'flamethrower' ? 64 : 48);
                let wHeight = isBat ? 36 : 32;

                if (isPan) weaponSheet = images['weapon_pan_swing_strip4'];
                else if (isBat) weaponSheet = images['weapon_bat_slam_strip4'];
                else if (activeWeapon === 'blaster') weaponSheet = images['weapon_blaster_shoot_strip4'];
                else if (activeWeapon === 'flamethrower') weaponSheet = images['weapon_flamethrower_stream_strip4'];

                if (weaponSheet) {{
                    const totalDur = player.attackDuration || 0.24;
                    const progress = Math.max(0, Math.min(1, 1 - (player.attackTimer / totalDur)));
                    const wIdx = Math.min(3, Math.floor(progress * wFrames));

                    const handOffX = (activeWeapon === 'flamethrower' || activeWeapon === 'blaster') ? 0 : -10;
                    const handOffY = isBat ? -18 : -16;

                    ctx.drawImage(weaponSheet, wIdx * wWidth, 0, wWidth, wHeight, handOffX, handOffY, wWidth, wHeight);

                    // Dynamic Glowing Wind Slash Arc Effect (Dara de vant ca efect in urma)
                    if ((isPan || isBat) && (wIdx === 1 || wIdx === 2)) {{
                        ctx.save();
                        ctx.beginPath();
                        const arcRadius = isBat ? 36 : 28;
                        ctx.arc(6, 0, arcRadius, -Math.PI * 0.35, Math.PI * 0.35, false);
                        ctx.strokeStyle = isBat ? 'rgba(251, 191, 36, 0.85)' : 'rgba(56, 189, 248, 0.9)';
                        ctx.lineWidth = isBat ? 4 : 3;
                        ctx.shadowColor = isBat ? '#f59e0b' : '#38bdf8';
                        ctx.shadowBlur = 6;
                        ctx.stroke();

                        // Bright sharp white core cutting edge
                        ctx.beginPath();
                        ctx.arc(6, 0, arcRadius - 2, -Math.PI * 0.28, Math.PI * 0.28, false);
                        ctx.strokeStyle = '#ffffff';
                        ctx.lineWidth = 1.5;
                        ctx.shadowBlur = 0;
                        ctx.stroke();
                        ctx.restore();
                    }}
                }}
            }}"""

assert old_draw_weapon in code, "old_draw_weapon not found!"
code = code.replace(old_draw_weapon, new_draw_weapon)
print("Replaced drawPlayer weapon code in generate_demo.py")

with open(demo_script, "w", encoding="utf-8") as f:
    f.write(code)

print("Saved generate_demo.py successfully!")
