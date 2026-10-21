"""Create clearly labeled synthetic bug reports for a portfolio demonstration.

All examples are invented. Do not represent them as bugs found in a real game.
"""
from pathlib import Path
import csv

BASE = Path(__file__).resolve().parent
PLATFORMS = ["Windows (keyboard/mouse)", "Windows (controller)", "Steam Deck"]
# Category, title, reproduction action, expected behavior, observed hypothetical issue, severity.
SCENARIOS = [
    ("UI", "Inventory tooltip covers item name", "Open inventory and hover over an item", "Item name and tooltip remain readable", "Tooltip overlaps the item name", "Low"),
    ("UI", "Settings text clipped at small resolution", "Set display to a low resolution and open settings", "All labels fit inside the settings panel", "Some labels are cut off", "Medium"),
    ("UI", "Health bar extends beyond screen edge", "Change interface scale and enter gameplay", "Health bar stays within the safe area", "Health bar extends past the right edge", "Medium"),
    ("UI", "Confirm button has no focus indicator", "Navigate the confirmation dialog with a controller", "Focused button is visibly highlighted", "Focused button has no visual highlight", "Low"),
    ("UI", "Quest marker remains on completed objective", "Finish a quest and open the map", "Completed quest marker disappears", "Marker remains visible", "Low"),
    ("UI", "Pause menu overlaps subtitle text", "Enable subtitles and pause during dialogue", "Pause menu and subtitles are readable", "Pause menu covers subtitles", "Medium"),
    ("UI", "Scrollbar disappears in long menu", "Open a menu with many entries and scroll down", "Scrollbar indicates list position", "Scrollbar is not rendered", "Low"),
    ("UI", "Keybinding label shows old shortcut", "Rebind an action and return to the controls menu", "Menu displays the updated shortcut", "Menu still shows the original shortcut", "Medium"),
    ("Gameplay", "Jump input ignored near ledge", "Move to a ledge and press jump", "Character jumps when input is valid", "Jump input is ignored", "High"),
    ("Gameplay", "Crafting consumes materials without item", "Gather recipe materials and craft an item", "Materials convert into the crafted item", "Materials disappear but no item appears", "High"),
    ("Gameplay", "Checkpoint does not update", "Activate a checkpoint and restart the level", "Player respawns at the latest checkpoint", "Player respawns at an older checkpoint", "High"),
    ("Gameplay", "Interaction prompt works outside range", "Stand far from an interactable object and press interact", "Interaction is unavailable outside range", "Object activates from a distant position", "Medium"),
    ("Gameplay", "Quest progress does not advance", "Defeat the required enemies and view quest progress", "Counter increases after valid defeats", "Quest counter remains unchanged", "High"),
    ("Gameplay", "Door collision remains after opening", "Unlock a door and walk through it", "Open doorway allows passage", "Invisible collision blocks movement", "Medium"),
    ("Gameplay", "Item duplicates after moving inventory slot", "Move an item between inventory slots repeatedly", "Item quantity remains unchanged", "Duplicate item appears", "High"),
    ("Gameplay", "Save load resets equipped weapon", "Equip a weapon save and reload", "Equipped weapon is restored", "Default weapon is equipped after loading", "Medium"),
    ("Performance", "Frame rate drops in crowded area", "Enter an area with many characters", "Frame rate remains reasonably stable", "Frame rate drops sharply", "Medium"),
    ("Performance", "Loading screen stalls after fast travel", "Use fast travel several times", "Destination loads within normal time", "Loading screen remains active much longer", "Medium"),
    ("Performance", "Memory usage grows after opening map", "Open and close the map repeatedly", "Memory usage stabilizes", "Memory usage grows after every opening", "Medium"),
    ("Performance", "Menu transition causes long freeze", "Switch repeatedly between inventory and settings", "Menu transitions remain responsive", "Game freezes for several seconds", "Medium"),
    ("Performance", "Texture streaming causes stutter", "Turn quickly while traversing a new area", "Movement remains smooth", "Noticeable stutter occurs while textures load", "Medium"),
    ("Performance", "Shadows setting takes unusually long to apply", "Change shadow quality while in gameplay", "Setting applies without a long pause", "Game becomes unresponsive for several seconds", "Low"),
    ("Performance", "Autosave produces repeated hitch", "Enable autosave and play until save triggers", "Autosave has minimal impact on movement", "Each autosave causes a visible hitch", "Medium"),
    ("Performance", "Long session causes rising input delay", "Play continuously and repeat a simple movement action", "Input response remains consistent", "Input response becomes progressively delayed", "High"),
    ("Network", "Lobby player count differs across clients", "Create a multiplayer lobby and invite two players", "All players see the same player count", "One client shows an incorrect player count", "Medium"),
    ("Network", "Client disconnects when host changes scene", "Join a lobby and have the host switch scenes", "Client stays connected", "Client disconnects unexpectedly", "High"),
    ("Network", "Chat messages arrive out of order", "Send several messages quickly from two clients", "Messages appear in their correct order", "Some messages appear out of order", "Low"),
    ("Network", "Reconnection does not restore session", "Disconnect briefly and reconnect to an ongoing match", "Player rejoins the active session", "Player returns to the main menu", "Medium"),
    ("Network", "Ready status fails to synchronize", "Toggle ready status in a multiplayer lobby", "All players see updated ready status", "Other clients still show not ready", "Medium"),
    ("Network", "Matchmaking remains stuck after cancellation", "Start matchmaking cancel and start again", "Second search begins normally", "Second search stays in a loading state", "Medium"),
    ("Network", "High latency warning missing", "Simulate high latency during online play", "Connection warning appears", "No warning is displayed during severe delay", "Low"),
    ("Network", "Remote player position stops updating", "Join online play and watch another player move", "Remote movement updates continuously", "Remote player freezes in place temporarily", "High"),
    ("Audio", "Background music stops after pause", "Pause and resume during gameplay", "Background music resumes", "Music remains silent", "Low"),
    ("Audio", "Dialogue audio missing in cutscene", "Start a cutscene with spoken dialogue", "Dialogue plays at the configured volume", "Characters speak without audible dialogue", "Medium"),
    ("Audio", "Sound effects play twice on interaction", "Interact with a door once", "One interaction sound plays", "Interaction sound plays twice", "Low"),
    ("Audio", "Voice volume slider has no effect", "Change voice volume and replay dialogue", "Dialogue loudness follows the slider", "Dialogue volume does not change", "Medium"),
    ("Audio", "Footstep sounds continue after stopping", "Run and release movement controls", "Footsteps stop when movement stops", "Footsteps continue briefly", "Low"),
    ("Audio", "Audio channel balance shifts unexpectedly", "Switch between menu and gameplay with headphones", "Left and right audio remain balanced", "Sound plays mostly on one side", "Medium"),
    ("Audio", "Environmental sound disappears after reload", "Save and reload near an ambient sound source", "Ambient audio resumes after loading", "Ambient sound is missing", "Low"),
    ("Audio", "Notification sound ignores mute setting", "Mute sound effects and trigger a notification", "Notification follows sound effect mute", "Notification sound still plays", "Low"),
]

# Each description is written as an individual fictional report, rather than
# being assembled by repeating the title and the expected result.
DESCRIPTIONS = [
    "When I hover over an inventory item, the tooltip opens on top of its name. I have to move the cursor away to read the label.",
    "Several options at the bottom of the settings panel are cut off when I switch to a smaller display resolution.",
    "Increasing the interface scale pushes the health bar beyond the right edge of the screen during gameplay.",
    "I can move between the confirmation buttons using a controller, but neither button shows which one currently has focus.",
    "The objective is marked as complete in the quest log, but its marker is still on the map afterward.",
    "If I pause while subtitles are visible, the pause panel covers part of the dialogue text.",
    "The menu list scrolls normally, although its scrollbar disappears once the number of entries gets large.",
    "After I change an action's key binding, the controls page still displays the previous shortcut.",
    "Jump sometimes fails to register when the character is standing close to the edge of a platform.",
    "The crafting action removes the required materials from the inventory, but the finished item never appears.",
    "I activate the newest checkpoint and restart the level, yet the character respawns at the earlier checkpoint.",
    "An interactable object can still be triggered when the player is well beyond the distance where its prompt disappears.",
    "The quest asks me to defeat several enemies. The counter stays unchanged even after the required targets are defeated.",
    "The door opens visually after being unlocked, but the character hits an invisible barrier when trying to walk through.",
    "Moving the same item back and forth between inventory slots occasionally creates an additional copy.",
    "After saving with a different weapon equipped, reloading restores the default weapon instead of the selected one.",
    "The game runs smoothly in quieter areas, then suffers a noticeable frame rate drop when many characters enter view.",
    "After several fast travel attempts, the loading screen stays visible much longer than it did at the start of the session.",
    "Memory use keeps increasing whenever I open and close the map, and it does not return to its earlier level.",
    "Switching rapidly between inventory and settings sometimes leaves the game unresponsive for a few seconds.",
    "Quick camera turns in a newly entered area cause brief pauses while the environment textures appear.",
    "Changing shadow quality during gameplay makes the application freeze momentarily before the new setting takes effect.",
    "Every time autosave starts, movement briefly stutters even though the player is not entering a new area.",
    "After a long session, movement begins responding later than usual to the same keyboard inputs.",
    "One player's lobby screen shows a different number of connected players from the count shown by the host.",
    "A joined player is unexpectedly disconnected when the host moves the group to another scene.",
    "Messages sent in quick succession by two players occasionally appear in a different order on their chat panels.",
    "After a short connection loss, reconnecting sends the player to the main menu rather than the active match.",
    "The local ready indicator changes correctly, but another player's lobby screen continues to show the old status.",
    "Cancelling a matchmaking search and starting another leaves the second search spinning without progressing.",
    "During severe simulated latency, the game continues without displaying any connection quality warning.",
    "A remote character stops moving on screen for several seconds and then suddenly jumps to a new position.",
    "The background track falls silent after I open the pause menu and resume the game.",
    "The cutscene advances and subtitles appear, but the characters' spoken dialogue cannot be heard.",
    "Interacting with the door once triggers the same sound effect twice in immediate succession.",
    "Changing the voice volume slider does not seem to affect the loudness of dialogue playback.",
    "Footstep sounds continue for a short time after the character has stopped and movement input has been released.",
    "After moving from the menu into gameplay, most sound seems to come from one headphone channel.",
    "An ambient sound source is audible before saving, but its audio disappears after loading that save.",
    "The notification tone still plays even after sound effects have been muted in the audio settings.",
]


def main():
    if len(DESCRIPTIONS) != len(SCENARIOS):
        raise ValueError("Descriptions and scenarios must have the same number of entries.")
    rows = []
    # Keep one distinct scenario per row. Repeating an identical defect across
    # multiple platforms would inflate the apparent dataset size and test score.
    for index, (category, title, steps, expected, actual, severity) in enumerate(SCENARIOS, 1):
        platform = PLATFORMS[(index - 1) % len(PLATFORMS)]
        rows.append({
            "report_id": f"SYN-{index:03d}",
            "title": title,
            "category": category,
            "severity": severity,
            "platform": platform,
            "steps_to_reproduce": steps,
            "expected_result": expected,
            "actual_result": actual,
            "description": DESCRIPTIONS[index - 1],
            "data_source": "Fictional example; not observed in a released game",
        })
    output = BASE / "data" / "demo_bug_reports.csv"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} synthetic, structured bug reports: {output}")


if __name__ == "__main__":
    main()
