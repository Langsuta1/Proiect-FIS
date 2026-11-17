import os
import re

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
demo_script = os.path.join(scratch_dir, "generate_demo.py")

with open(demo_script, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add isCrouching to player definition
if "isCrouching: false," not in code:
    code = code.replace(
        "isSprinting: false,",
        "isSprinting: false,\n            isCrouching: false,"
    )

# 2. Add crouch handling in player movement update
old_move_physics = """            // Movement & Sprint
            player.isSprinting = keys['ShiftLeft'] || keys['ShiftRight'];
            const moveSpeed = player.isSprinting ? player.sprintSpeed : player.speed;

            if (keys['KeyA'] || keys['ArrowLeft']) {
                player.vx = -moveSpeed;
                player.facing = -1;
            } else if (keys['KeyD'] || keys['ArrowRight']) {
                player.vx = moveSpeed;
                player.facing = 1;
            } else {
                player.vx = 0;
            }"""

# In the f-string in generate_demo.py, braces are doubled {{ }}
old_move_physics_fstring = """            // Movement & Sprint
            player.isSprinting = keys['ShiftLeft'] || keys['ShiftRight'];
            const moveSpeed = player.isSprinting ? player.sprintSpeed : player.speed;

            if (keys['KeyA'] || keys['ArrowLeft']) {{
                player.vx = -moveSpeed;
                player.facing = -1;
            }} else if (keys['KeyD'] || keys['ArrowRight']) {{
                player.vx = moveSpeed;
                player.facing = 1;
            }} else {{
                player.vx = 0;
            }}"""

new_move_physics = """            // Crouch Handling [S] / [ArrowDown]
            player.isCrouching = player.isGrounded && (keys['KeyS'] || keys['ArrowDown']) && !player.isDashing;
            if (player.isCrouching) {{
                player.h = 16;
            }} else {{
                player.h = 28;
            }}

            // Movement & Sprint
            player.isSprinting = (keys['ShiftLeft'] || keys['ShiftRight']) && !player.isCrouching;
            const currentSpeed = player.isCrouching ? 55 : (player.isSprinting ? player.sprintSpeed : player.speed);

            if (keys['KeyA'] || keys['ArrowLeft']) {{
                player.vx = -currentSpeed;
                player.facing = -1;
            }} else if (keys['KeyD'] || keys['ArrowRight']) {{
                player.vx = currentSpeed;
                player.facing = 1;
            }} else {{
                player.vx = 0;
            }}"""

if old_move_physics_fstring in code:
    code = code.replace(old_move_physics_fstring, new_move_physics)
    print("Replaced movement physics with crouch support.")
else:
    print("WARNING: old_move_physics_fstring not found!")

# 3. Disallow jump while crouching
code = code.replace(
    "if ((keys['Space'] || keys['KeyW'] || keys['ArrowUp'])) {{",
    "if ((keys['Space'] || keys['KeyW'] || keys['ArrowUp']) && !player.isCrouching) {{"
)

# 4. Make background 100% STATIC and aligned to floor in render()
old_render_block = """        function render() {{
            ctx.clearRect(0, 0, V_WIDTH, V_HEIGHT);

            renderParallaxBackground();

            ctx.save();
            ctx.translate(-Math.floor(camera.x), -Math.floor(camera.y));

            drawPlatforms();"""

new_render_block = """        function render() {{
            ctx.clearRect(0, 0, V_WIDTH, V_HEIGHT);

            ctx.save();
            ctx.translate(-Math.floor(camera.x), -Math.floor(camera.y));

            // 100% STATIC LEVEL BACKDROP (Aligned to floor line y = 780, never shifts or floats!)
            if (images['level_heap_backdrop_3200x900']) {{
                ctx.drawImage(images['level_heap_backdrop_3200x900'], 0, 0);
            }}

            drawPlatforms();"""

if old_render_block in code:
    code = code.replace(old_render_block, new_render_block)
    print("Replaced render with 100% static backdrop.")
else:
    print("WARNING: old_render_block not found!")

# 5. Update drawPlayer() to use unified attack strips with arm swing from hand level & crouch strip
old_draw_player = """        function drawPlayer() {{
            ctx.save();
            ctx.translate(Math.floor(player.x + 10), Math.floor(player.y + 14));
            ctx.scale(player.facing, 1);
            ctx.rotate(player.leanAngle);

            // Strict I-Frames Flashing
            if (player.iFrameTimer > 0 && Math.floor(Date.now() / 70) % 2 === 0) {{
                ctx.globalAlpha = 0.35;
            }}

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
                // 8-Frame Humanoid Clean Walk Cycle
                sheet = (player.chassis === 'damaged') ? images['robot_damaged_walk_strip8'] : images['robot_standard_walk_strip8'];
                frameCount = 8;
                frameSpeed = player.isSprinting ? 75 : 110;
            }} else {{
                sheet = (player.chassis === 'damaged') ? images['robot_damaged_idle_strip4'] : images['robot_standard_idle_strip4'];
                frameCount = 4;
                frameSpeed = 140;
            }}

            const frameIdx = Math.floor(Date.now() / frameSpeed) % frameCount;

            if (sheet) {{
                ctx.drawImage(sheet, frameIdx * 32, 0, 32, 32, -16, -16, 32, 32);
            }}

            if (player.attackTimer > 0) {{"""

new_draw_player = """        function drawPlayer() {{
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

        function dummyOldWeaponCode() {{
            if (false) {{"""

# Replace the start of drawPlayer up to if (player.attackTimer > 0)
if old_draw_player in code:
    # Find the closing brace of the old weapon block in drawPlayer
    idx_start = code.find(old_draw_player)
    idx_end = code.find("ctx.restore();\n        }", idx_start)
    if idx_end != -1:
        old_full_block = code[idx_start:idx_end + len("ctx.restore();\n        }")]
        code = code.replace(old_full_block, new_draw_player)
        print("Replaced drawPlayer with unified attack and crouch.")
    else:
        print("WARNING: idx_end of drawPlayer not found!")
else:
    print("WARNING: old_draw_player header not found!")

# 6. Update Blaster shooting position so projectile fires from hand level (y = player.y + 12)
code = code.replace(
    "const py = player.y + 6;",
    "const py = player.y + 12;"
)

with open(demo_script, "w", encoding="utf-8") as f:
    f.write(code)

print("Saved updated generate_demo.py successfully!")
