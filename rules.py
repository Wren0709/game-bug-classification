import re

KEYWORDS = {
    'Audio': ('audio', 'sound', 'music', 'volume', '声音', '音效', '音乐', '静音'),
    'Gameplay': ('quest', 'inventory', 'save', 'item', 'collision', '任务', '背包', '存档', '道具', '碰撞', '穿模'),
    'Network': ('disconnect', 'connection', 'server', 'latency', 'multiplayer', '断线', '掉线', '服务器', '联机', '网络'),
    'Performance': ('crash', 'freeze', 'fps', 'stutter', 'memory', '崩溃', '闪退', '卡顿', '帧率', '内存'),
    'UI': ('button', 'menu', 'tooltip', 'screen', 'interface', '按钮', '菜单', '界面', '文字', '分辨率'),
}


def rule_prediction(text):
    lower = text.lower()
    hits = {label: [word for word in words if (word in lower if re.search(r'[\u4e00-\u9fff]', word) else re.search(r'\b' + re.escape(word) + r'\w*\b', lower))] for label, words in KEYWORDS.items()}
    scores = {label: len(words) for label, words in hits.items()}
    best = max(scores.values())
    winners = [label for label, score in scores.items() if score == best]
    category = winners[0] if best > 0 and len(winners) == 1 else ''
    return category, '; '.join(f'{label}: {", ".join(words)}' for label, words in hits.items() if words)
