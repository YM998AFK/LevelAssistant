"""现代简约主题 — 以 Zinc + Violet 为核心的设计语言"""

# ── 色彩系统 ─────────────────────────────────────────────────────────
C = {
    # 背景层次
    "bg":           "#FFFFFF",
    "bg_app":       "#F5F5F7",
    "bg_sidebar":   "#ECEBF3",
    "bg_hover":     "#F0EFF8",
    "bg_muted":     "#E4E4E7",

    # 边框
    "border":       "#D4D4D8",
    "border_focus": "#7C3AED",

    # 文字
    "text":         "#18181B",
    "text_muted":   "#71717A",
    "text_faint":   "#A1A1AA",
    "text_white":   "#FFFFFF",

    # 主色调（Violet）
    "indigo":       "#7C3AED",
    "indigo_dark":  "#6D28D9",
    "indigo_mid":   "#A78BFA",
    "indigo_light": "#EDE9FE",
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
    "user_bg":      "#5B21B6",
    "user_text":    "#FFFFFF",

    # AI 消息卡片
    "ai_bg":        "#F8F7FF",
    "ai_border":    "#D4D4D8",
    "ai_border_active": "#A78BFA",
}

COLORS = C  # 兼容旧引用

QSS = f"""
* {{
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {C['text']};
    outline: none;
}}

QMainWindow {{
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
    background: transparent;
    padding: 3px;
}}
QPushButton[modeTab="true"] {{
    background: transparent;
    border: none;
    padding: 5px 14px;
    color: {C['text_muted']};
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton[modeTab="true"]:hover {{
    background: {C['bg_hover']};
    color: {C['text']};
}}
QPushButton[modeTab="true"][active="true"] {{
    background: {C['indigo']};
    color: {C['text_white']};
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
    selection-background-color: #DDD6FE;
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
    background: {C['bg']};
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
    background: {C['bg']};
    border: none;
    padding: 0;
    color: {C['text']};
}}
/* 运行中：输入框边框变为主色，背景微微带色 */
#InputBox[busy="true"] {{
    border: 1.5px solid {C['indigo_mid']};
    background: {C['indigo_tint']};
}}
#InputBox[busy="true"] QTextEdit {{
    background: {C['indigo_tint']};
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

/* ── AI 消息卡片（正常） ─ */
#AICard {{
    background: {C['ai_bg']};
    border-top: 1px solid {C['ai_border']};
    border-right: 1px solid {C['ai_border']};
    border-bottom: 1px solid {C['ai_border']};
    border-left: 3px solid {C['indigo']};
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    border-top-right-radius: 16px;
    border-bottom-right-radius: 16px;
    padding: 12px 14px;
}}
#AICard QLabel {{
    background: transparent;
    color: {C['text']};
    font-size: 14px;
    line-height: 1.65;
}}
/* 运行中：左边框变亮 */
#AICard[active="true"] {{
    border-left: 3px solid {C['indigo_mid']};
    border-top: 1px solid {C['indigo_light']};
    border-right: 1px solid {C['indigo_light']};
    border-bottom: 1px solid {C['indigo_light']};
    background: {C['indigo_tint']};
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
/* AI 头像 */
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
