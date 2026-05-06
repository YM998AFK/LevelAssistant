"""现代简约主题 — 以 Slate + Indigo 为核心的设计语言"""

# ── 色彩系统 ─────────────────────────────────────────────────────────
C = {
    # 背景层次
    "bg":           "#FFFFFF",
    "bg_app":       "#F8FAFC",
    "bg_sidebar":   "#F1F5F9",
    "bg_hover":     "#F1F5F9",
    "bg_muted":     "#E2E8F0",

    # 边框
    "border":       "#E2E8F0",
    "border_focus": "#6366F1",

    # 文字
    "text":         "#1E293B",
    "text_muted":   "#64748B",
    "text_faint":   "#94A3B8",
    "text_white":   "#FFFFFF",

    # 主色调（Indigo）
    "indigo":       "#6366F1",
    "indigo_dark":  "#4F46E5",
    "indigo_mid":   "#818CF8",
    "indigo_light": "#EEF2FF",
    "indigo_tint":  "#F5F3FF",

    # 成功 / 警告 / 错误
    "success":      "#059669",
    "success_bg":   "#ECFDF5",
    "success_bdr":  "#6EE7B7",
    "warn":         "#D97706",
    "warn_bg":      "#FFFBEB",
    "warn_bdr":     "#FDE68A",
    "error":        "#DC2626",
    "error_bg":     "#FEF2F2",
    "error_bdr":    "#FECACA",

    # 用户消息气泡
    "user_bg":      "#6366F1",
    "user_text":    "#FFFFFF",

    # AI 消息卡片
    "ai_bg":        "#FFFFFF",
    "ai_border":    "#E2E8F0",
    "ai_border_active": "#A5B4FC",
}

COLORS = C

QSS = f"""
* {{
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {C['text']};
    outline: none;
}}

QMainWindow, QWidget {{
    background-color: {C['bg_app']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   顶部导航栏
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#TopBar {{
    background-color: {C['bg']};
    border-bottom: 1px solid {C['border']};
}}

#AppTitle {{
    font-size: 15px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: {C['text']};
}}

#IconButton {{
    background: transparent;
    border: none;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 13px;
    color: {C['text_muted']};
}}
#IconButton:hover {{
    background-color: {C['bg_hover']};
    color: {C['text']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   模式选项卡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#ModeBar {{
    background: {C['bg_muted']};
    border-radius: 10px;
    padding: 3px;
}}
QPushButton[modeTab="true"] {{
    background: transparent;
    border: none;
    padding: 5px 14px;
    color: {C['text_muted']};
    border-radius: 7px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton[modeTab="true"]:hover {{
    color: {C['text']};
}}
QPushButton[modeTab="true"][active="true"] {{
    background: {C['bg']};
    color: {C['indigo']};
    font-weight: 600;
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   左侧边栏
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#Sidebar {{
    background: {C['bg_sidebar']};
    border-right: 1px solid {C['border']};
}}

QLabel[sectionLabel="true"] {{
    color: {C['text_faint']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}

QLabel[linkText="true"] {{
    color: {C['indigo']};
    font-size: 12px;
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   拖放区 & 文件 Chip
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#DropZone {{
    background: {C['bg']};
    border: 1.5px dashed {C['border']};
    border-radius: 10px;
    color: {C['text_faint']};
}}
#DropZone:hover {{
    border-color: {C['indigo']};
    background: {C['indigo_light']};
}}
#DropZone[dragging="true"] {{
    border-color: {C['indigo']};
    background: {C['indigo_light']};
}}

#FileChip {{
    background: {C['bg']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 6px 10px;
}}

QPushButton#RemoveBtn {{
    background: transparent;
    border: none;
    color: {C['text_faint']};
    font-size: 14px;
    padding: 0px 4px;
    border-radius: 4px;
}}
QPushButton#RemoveBtn:hover {{
    color: {C['error']};
    background: {C['error_bg']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   通用输入框
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
QTextEdit, QLineEdit {{
    background: {C['bg']};
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #C7D2FE;
    color: {C['text']};
}}
QTextEdit:focus, QLineEdit:focus {{
    border-color: {C['indigo']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   按钮
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
QPushButton#PrimaryButton {{
    background: {C['indigo']};
    color: {C['text_white']};
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{
    background: {C['indigo_dark']};
}}
QPushButton#PrimaryButton:disabled {{
    background: {C['bg_muted']};
    color: {C['text_faint']};
}}

QPushButton#SecondaryButton {{
    background: {C['bg']};
    color: {C['text']};
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 500;
}}
QPushButton#SecondaryButton:hover {{
    border-color: {C['indigo']};
    color: {C['indigo']};
}}

QPushButton#AddLinkBtn {{
    background: transparent;
    border: none;
    color: {C['indigo']};
    font-size: 12px;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 4px;
}}
QPushButton#AddLinkBtn:hover {{
    background: {C['indigo_light']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   聊天区域
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#ChatArea {{
    background: {C['bg_app']};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C['text_faint']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── 聊天输入框 ─ */
#InputBox {{
    background: {C['bg']};
    border: 1.5px solid {C['border']};
    border-radius: 16px;
}}
#InputBox QTextEdit {{
    background: transparent;
    border: none;
    padding: 0;
    color: {C['text']};
}}
/* 运行中：输入框边框变为 Indigo，背景微微带色 */
#InputBox[busy="true"] {{
    border: 1.5px solid {C['indigo_mid']};
    background: {C['indigo_tint']};
}}

QPushButton#SendBtn {{
    background: {C['indigo']};
    color: white;
    border: none;
    border-radius: 18px;
    font-size: 18px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
}}
QPushButton#SendBtn:hover {{
    background: {C['indigo_dark']};
}}
QPushButton#SendBtn:disabled {{
    background: {C['bg_muted']};
    color: {C['text_faint']};
}}

/* ── 用户消息气泡 ─ */
#UserBubble {{
    background: {C['user_bg']};
    border-radius: 18px;
    border-bottom-right-radius: 5px;
    padding: 10px 14px;
}}
#UserBubble QLabel {{
    color: {C['text_white']};
    font-size: 14px;
    background: transparent;
    line-height: 1.6;
}}

/* ── AI 消息卡片（正常） ─ */
#AICard {{
    background: {C['ai_bg']};
    border: 1px solid {C['ai_border']};
    border-radius: 18px;
    border-top-left-radius: 5px;
    padding: 12px 14px;
}}
#AICard QLabel {{
    background: transparent;
    color: {C['text']};
    font-size: 14px;
    line-height: 1.65;
}}
/* 运行中：AI 卡片左侧亮 Indigo 边框 */
#AICard[active="true"] {{
    border: 1px solid {C['ai_border']};
    border-left: 3px solid {C['indigo']};
}}

/* ── 头像 ─ */
#UserAvatar {{
    background: {C['indigo']};
    color: white;
    border-radius: 14px;
    font-weight: 700;
    font-size: 11px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
}}
/* Sonnet 头像 */
#AIAvatar {{
    background: {C['indigo_light']};
    color: {C['indigo_dark']};
    border-radius: 14px;
    font-size: 13px;
    font-weight: 700;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
    border: 1.5px solid {C['indigo_mid']};
}}

/* ── 工具 Chip（三种状态） ─ */
#ToolChip {{
    background: {C['bg_hover']};
    color: {C['text_muted']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    border: 1px solid {C['border']};
}}
#ToolChip[status="running"] {{
    background: {C['warn_bg']};
    color: {C['warn']};
    border-color: {C['warn_bdr']};
}}
#ToolChip[status="done"] {{
    background: {C['success_bg']};
    color: {C['success']};
    border-color: {C['success_bdr']};
}}
#ToolChip[status="error"] {{
    background: {C['error_bg']};
    color: {C['error']};
    border-color: {C['error_bdr']};
}}

/* ── 角色名 ─ */
#RoleLabel {{
    color: {C['indigo']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}

/* ── 消息正文 ─ */
#MessageText {{
    font-size: 14px;
    color: {C['text']};
}}

/* ── 下载卡片 ─ */
#DownloadCard {{
    background: {C['success_bg']};
    border: 1px solid {C['success_bdr']};
    border-radius: 12px;
    padding: 12px 14px;
}}

#HintLabel {{
    color: {C['text_faint']};
    font-size: 12px;
}}

/* ── ComboBox ─ */
QComboBox {{
    background: {C['bg']};
    border: 1.5px solid {C['border']};
    border-radius: 7px;
    padding: 4px 10px;
    min-height: 26px;
    color: {C['text']};
}}
QComboBox:hover {{
    border-color: {C['text_muted']};
}}
QComboBox:focus {{
    border-color: {C['indigo']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background: {C['bg']};
    border: 1px solid {C['border']};
    border-radius: 7px;
    selection-background-color: {C['indigo_light']};
    selection-color: {C['text']};
}}
"""


COLORS = C  # 兼容旧引用

QSS = f"""
* {{
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {C['text']};
    outline: none;
}}

QMainWindow, QWidget {{
    background-color: {C['bg_app']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   顶部导航栏
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#TopBar {{
    background-color: {C['bg']};
    border-bottom: 1px solid {C['border']};
}}

#AppTitle {{
    font-size: 15px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: {C['text']};
}}

#IconButton {{
    background: transparent;
    border: none;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 13px;
    color: {C['text_muted']};
}}
#IconButton:hover {{
    background-color: {C['bg_hover']};
    color: {C['text']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   模式选项卡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#ModeBar {{
    background: {C['bg_muted']};
    border-radius: 10px;
    padding: 3px;
}}
QPushButton[modeTab="true"] {{
    background: transparent;
    border: none;
    padding: 5px 14px;
    color: {C['text_muted']};
    border-radius: 7px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton[modeTab="true"]:hover {{
    color: {C['text']};
}}
QPushButton[modeTab="true"][active="true"] {{
    background: {C['bg']};
    color: {C['text']};
    font-weight: 600;
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   左侧边栏
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#Sidebar {{
    background: {C['bg_sidebar']};
    border-right: 1px solid {C['border']};
}}

QLabel[sectionLabel="true"] {{
    color: {C['text_faint']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.6px;
}}

QLabel[linkText="true"] {{
    color: {C['indigo']};
    font-size: 12px;
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   拖放区 & 文件 Chip
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#DropZone {{
    background: {C['bg']};
    border: 1.5px dashed {C['border']};
    border-radius: 10px;
    color: {C['text_faint']};
}}
#DropZone:hover {{
    border-color: {C['indigo']};
    background: {C['indigo_light']};
}}
#DropZone[dragging="true"] {{
    border-color: {C['indigo']};
    background: {C['indigo_light']};
}}

#FileChip {{
    background: {C['bg']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 6px 10px;
}}

QPushButton#RemoveBtn {{
    background: transparent;
    border: none;
    color: {C['text_faint']};
    font-size: 14px;
    padding: 0px 4px;
    border-radius: 4px;
}}
QPushButton#RemoveBtn:hover {{
    color: {C['error']};
    background: #FEE2E2;
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   通用输入框
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
QTextEdit, QLineEdit {{
    background: {C['bg']};
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #C7D2FE;
    color: {C['text']};
}}
QTextEdit:focus, QLineEdit:focus {{
    border-color: {C['indigo']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   按钮
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
QPushButton#PrimaryButton {{
    background: {C['indigo']};
    color: {C['text_white']};
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{
    background: {C['indigo_dark']};
}}
QPushButton#PrimaryButton:disabled {{
    background: {C['bg_muted']};
    color: {C['text_faint']};
}}

QPushButton#SecondaryButton {{
    background: {C['bg']};
    color: {C['text']};
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 500;
}}
QPushButton#SecondaryButton:hover {{
    border-color: {C['indigo']};
    color: {C['indigo']};
}}

QPushButton#AddLinkBtn {{
    background: transparent;
    border: none;
    color: {C['indigo']};
    font-size: 12px;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 4px;
}}
QPushButton#AddLinkBtn:hover {{
    background: {C['indigo_light']};
}}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   聊天区域
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#ChatArea {{
    background: {C['bg_app']};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C['text_faint']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── 聊天输入框 ─ */
#InputBox {{
    background: {C['bg']};
    border: 1.5px solid {C['border']};
    border-radius: 16px;
}}
#InputBox QTextEdit {{
    background: transparent;
    border: none;
    padding: 0;
    color: {C['text']};
}}

QPushButton#SendBtn {{
    background: {C['indigo']};
    color: white;
    border: none;
    border-radius: 18px;
    font-size: 18px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
}}
QPushButton#SendBtn:hover {{
    background: {C['indigo_dark']};
}}
QPushButton#SendBtn:disabled {{
    background: {C['bg_muted']};
    color: {C['text_faint']};
}}

/* ── 用户消息气泡 ─ */
#UserBubble {{
    background: {C['user_bg']};
    border-radius: 18px;
    border-bottom-right-radius: 5px;
    padding: 10px 14px;
}}
#UserBubble QLabel {{
    color: {C['text_white']};
    font-size: 14px;
    background: transparent;
    line-height: 1.6;
}}

/* ── AI 消息卡片 ─ */
#AICard {{
    background: {C['bg']};
    border: 1px solid {C['ai_border']};
    border-radius: 18px;
    border-top-left-radius: 5px;
    padding: 12px 14px;
}}
#AICard QLabel {{
    background: transparent;
    color: {C['text']};
    font-size: 14px;
    line-height: 1.65;
}}

/* ── 头像 ─ */
#UserAvatar {{
    background: {C['indigo']};
    color: white;
    border-radius: 14px;
    font-weight: 700;
    font-size: 11px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
}}
#AIAvatar {{
    background: {C['success_bg']};
    color: {C['success']};
    border-radius: 14px;
    font-size: 14px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
}}

/* ── 工具 Chip ─ */
#ToolChip {{
    background: {C['bg_hover']};
    color: {C['text_muted']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    border: 1px solid {C['border']};
}}

/* ── 角色名 ─ */
#RoleLabel {{
    color: {C['text_faint']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}

/* ── 消息正文 ─ */
#MessageText {{
    font-size: 14px;
    color: {C['text']};
}}

/* ── 下载卡片 ─ */
#DownloadCard {{
    background: {C['success_bg']};
    border: 1px solid {C['success_bdr']};
    border-radius: 12px;
    padding: 12px 14px;
}}

#HintLabel {{
    color: {C['text_faint']};
    font-size: 12px;
}}

/* ── ComboBox ─ */
QComboBox {{
    background: {C['bg']};
    border: 1.5px solid {C['border']};
    border-radius: 7px;
    padding: 4px 10px;
    min-height: 26px;
    color: {C['text']};
}}
QComboBox:hover {{
    border-color: {C['text_muted']};
}}
QComboBox:focus {{
    border-color: {C['indigo']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background: {C['bg']};
    border: 1px solid {C['border']};
    border-radius: 7px;
    selection-background-color: {C['indigo_light']};
    selection-color: {C['text']};
}}
"""
