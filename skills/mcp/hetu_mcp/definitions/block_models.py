"""
Hetu Block 数据模型和工具类
"""

from typing import Any, Dict, List, Optional, Sequence, Union
from enum import Enum
import copy

from definitions.script_definitions import load_script_block_definitions


class BlockType(Enum):
    """Block 类型枚举"""
    TRIGGER = "Trigger"  # 触发器（事件块）
    OPERATOR = "Operator"  # 运算符
    LOGICAL_OPERATOR = "LogicalOperator"  # 逻辑运算符
    STATEMENT = "Statement"  # 语句
    BRANCH_STATEMENT = "BranchStatement"  # 分支语句


class BlockCategory(Enum):
    """Block 分类枚举"""
    EVENTS = "events"  # 事件
    MOTION = "motion"  # 运动
    LOOKS = "looks"  # 外观
    SOUND = "sound"  # 声音
    CONTROL = "control"  # 控制
    SENSING = "sensing"  # 侦测
    OPERATORS = "operators"  # 运算
    VARIABLES = "variables"  # 变量
    MUSIC = "music"  # 音乐
    PHYSICS = "physics"  # 物理
    STAGE = "stage"  # 舞台
    MAGIC = "magic"  # 特殊功能
    MYBLOCKS = "myblocks"  # 自定义块
    UI = "ui"  # UI扩展
    ANIMATION = "animation"  # 动画扩展
    PATCHES = "patches"  # 补丁扩展
    EXPERIMENT = "experiment"  # 实验扩展


# Block 定义数据库 - 从文档中提取的所有 Block 定义
BASE_BLOCK_DEFINITIONS = {
    # ============= Events (事件) =============
    "WhenGameStarts": {
        "category": BlockCategory.EVENTS,
        "type": BlockType.TRIGGER,
        "description": "当游戏开始时",
        "parameters": [],
        "return_type": None
    },
    "WhenKeyPressed": {
        "category": BlockCategory.EVENTS,
        "type": BlockType.TRIGGER,
        "description": "当按下指定键时",
        "parameters": [
            {"name": "key", "type": "string", "default": "space", "options": ["space", "up arrow", "down arrow", "left arrow", "right arrow", "any"]}
        ],
        "return_type": None
    },
    "WhenClicked": {
        "category": BlockCategory.EVENTS,
        "type": BlockType.TRIGGER,
        "description": "当角色被点击时",
        "parameters": [],
        "return_type": None
    },
    "WhenReceiveMessage": {
        "category": BlockCategory.EVENTS,
        "type": BlockType.TRIGGER,
        "description": "当接收到消息时",
        "parameters": [
            {"name": "message", "type": "string", "default": "message1", "embeddable": False}
        ],
        "return_type": None
    },
    "BroadcastMessage": {
        "category": BlockCategory.EVENTS,
        "type": BlockType.STATEMENT,
        "description": "广播消息",
        "parameters": [
            {"name": "message", "type": "string", "default": "message1", "embeddable": False}
        ],
        "return_type": None
    },
    "BroadcastMessageAndWait": {
        "category": BlockCategory.EVENTS,
        "type": BlockType.STATEMENT,
        "description": "广播消息并等待",
        "parameters": [
            {"name": "message", "type": "string", "default": "message1", "embeddable": False}
        ],
        "return_type": None
    },
    
    # ============= Motion (运动) =============
    "MoveSteps": {
        "category": BlockCategory.MOTION,
        "type": BlockType.STATEMENT,
        "description": "移动指定步数",
        "parameters": [
            {"name": "steps", "type": "number", "default": "10", "embeddable": True}
        ],
        "return_type": None
    },
    "TurnRight": {
        "category": BlockCategory.MOTION,
        "type": BlockType.STATEMENT,
        "description": "向右旋转",
        "parameters": [
            {"name": "degrees", "type": "number", "default": "15", "embeddable": True}
        ],
        "return_type": None
    },
    "TurnLeft": {
        "category": BlockCategory.MOTION,
        "type": BlockType.STATEMENT,
        "description": "向左旋转",
        "parameters": [
            {"name": "degrees", "type": "number", "default": "15", "embeddable": True}
        ],
        "return_type": None
    },
    "GotoPosition3D": {
        "category": BlockCategory.MOTION,
        "type": BlockType.STATEMENT,
        "description": "移动到3D坐标",
        "parameters": [
            {"name": "x", "type": "number", "default": "0", "embeddable": True},
            {"name": "y", "type": "number", "default": "0", "embeddable": True},
            {"name": "z", "type": "number", "default": "0", "embeddable": True}
        ],
        "return_type": None
    },
    "GotoPosition2D": {
        "category": BlockCategory.MOTION,
        "type": BlockType.STATEMENT,
        "description": "移动到2D坐标",
        "parameters": [
            {"name": "x", "type": "number", "default": "0", "embeddable": True},
            {"name": "y", "type": "number", "default": "0", "embeddable": True}
        ],
        "return_type": None
    },
    "GetPosX": {
        "category": BlockCategory.MOTION,
        "type": BlockType.OPERATOR,
        "description": "获取x坐标",
        "parameters": [],
        "return_type": "float"
    },
    "GetPosY": {
        "category": BlockCategory.MOTION,
        "type": BlockType.OPERATOR,
        "description": "获取y坐标",
        "parameters": [],
        "return_type": "float"
    },
    "GetPosZ": {
        "category": BlockCategory.MOTION,
        "type": BlockType.OPERATOR,
        "description": "获取z坐标",
        "parameters": [],
        "return_type": "float"
    },
    
    # ============= Looks (外观) =============
    "Say": {
        "category": BlockCategory.LOOKS,
        "type": BlockType.STATEMENT,
        "description": "说话",
        "parameters": [
            {"name": "message", "type": "string", "default": "Hello!", "embeddable": True}
        ],
        "return_type": None
    },
    "SayForSeconds": {
        "category": BlockCategory.LOOKS,
        "type": BlockType.STATEMENT,
        "description": "说话指定秒数",
        "parameters": [
            {"name": "message", "type": "string", "default": "Hello!", "embeddable": True},
            {"name": "seconds", "type": "number", "default": "2", "embeddable": True}
        ],
        "return_type": None
    },
    "Show": {
        "category": BlockCategory.LOOKS,
        "type": BlockType.STATEMENT,
        "description": "显示",
        "parameters": [],
        "return_type": None
    },
    "Hide": {
        "category": BlockCategory.LOOKS,
        "type": BlockType.STATEMENT,
        "description": "隐藏",
        "parameters": [],
        "return_type": None
    },
    
    # ============= Sound (声音) =============
    "PlaySound": {
        "category": BlockCategory.SOUND,
        "type": BlockType.STATEMENT,
        "description": "播放音效",
        "parameters": [
            {"name": "sound", "type": "string", "default": "sound1", "embeddable": False}
        ],
        "return_type": None
    },
    "PlayBGM": {
        "category": BlockCategory.SOUND,
        "type": BlockType.STATEMENT,
        "description": "播放背景音乐",
        "parameters": [
            {"name": "music", "type": "string", "default": "music1", "embeddable": False}
        ],
        "return_type": None
    },
    
    # ============= Control (控制) =============
    "Forever": {
        "category": BlockCategory.CONTROL,
        "type": BlockType.BRANCH_STATEMENT,
        "description": "重复执行",
        "parameters": [],
        "return_type": None,
        "has_branch": True,
        "branch_count": 1
    },
    "Repeat": {
        "category": BlockCategory.CONTROL,
        "type": BlockType.BRANCH_STATEMENT,
        "description": "重复执行指定次数",
        "parameters": [
            {"name": "times", "type": "number", "default": "10", "embeddable": True}
        ],
        "return_type": None,
        "has_branch": True,
        "branch_count": 1
    },
    "If": {
        "category": BlockCategory.CONTROL,
        "type": BlockType.BRANCH_STATEMENT,
        "description": "如果...那么",
        "parameters": [
            {"name": "condition", "type": "boolean", "embeddable": True}
        ],
        "return_type": None,
        "has_branch": True,
        "branch_count": 1
    },
    "IfElse": {
        "category": BlockCategory.CONTROL,
        "type": BlockType.BRANCH_STATEMENT,
        "description": "如果...那么...否则",
        "parameters": [
            {"name": "condition", "type": "boolean", "embeddable": True}
        ],
        "return_type": None,
        "has_branch": True,
        "branch_count": 2
    },
    "WaitSeconds": {
        "category": BlockCategory.CONTROL,
        "type": BlockType.STATEMENT,
        "description": "等待指定秒数",
        "parameters": [
            {"name": "seconds", "type": "number", "default": "1", "embeddable": True}
        ],
        "return_type": None
    },
    "StopAll": {
        "category": BlockCategory.CONTROL,
        "type": BlockType.STATEMENT,
        "description": "停止所有",
        "parameters": [],
        "return_type": None
    },
    
    # ============= Sensing (侦测) =============
    "IsTouching": {
        "category": BlockCategory.SENSING,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "碰到了目标",
        "parameters": [
            {"name": "target", "type": "string", "default": "_mouse_", "embeddable": False}
        ],
        "return_type": "boolean"
    },
    "AskAndWait": {
        "category": BlockCategory.SENSING,
        "type": BlockType.STATEMENT,
        "description": "询问并等待",
        "parameters": [
            {"name": "question", "type": "string", "default": "What's your name?", "embeddable": True}
        ],
        "return_type": None
    },
    "Answer": {
        "category": BlockCategory.SENSING,
        "type": BlockType.OPERATOR,
        "description": "回答",
        "parameters": [],
        "return_type": "string"
    },
    
    # ============= Operators (运算) =============
    "Add": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.OPERATOR,
        "description": "加法",
        "parameters": [
            {"name": "num1", "type": "number", "default": "", "embeddable": True},
            {"name": "num2", "type": "number", "default": "", "embeddable": True}
        ],
        "return_type": "number"
    },
    "Subtract": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.OPERATOR,
        "description": "减法",
        "parameters": [
            {"name": "num1", "type": "number", "default": "", "embeddable": True},
            {"name": "num2", "type": "number", "default": "", "embeddable": True}
        ],
        "return_type": "number"
    },
    "Multiply": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.OPERATOR,
        "description": "乘法",
        "parameters": [
            {"name": "num1", "type": "number", "default": "", "embeddable": True},
            {"name": "num2", "type": "number", "default": "", "embeddable": True}
        ],
        "return_type": "number"
    },
    "Divide": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.OPERATOR,
        "description": "除法",
        "parameters": [
            {"name": "num1", "type": "number", "default": "", "embeddable": True},
            {"name": "num2", "type": "number", "default": "", "embeddable": True}
        ],
        "return_type": "number"
    },
    "IsGreater": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "大于",
        "parameters": [
            {"name": "val1", "type": "string", "default": "", "embeddable": True},
            {"name": "val2", "type": "string", "default": "", "embeddable": True}
        ],
        "return_type": "boolean"
    },
    "IsLess": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "小于",
        "parameters": [
            {"name": "val1", "type": "string", "default": "", "embeddable": True},
            {"name": "val2", "type": "string", "default": "", "embeddable": True}
        ],
        "return_type": "boolean"
    },
    "IsEqual": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "等于",
        "parameters": [
            {"name": "val1", "type": "string", "default": "", "embeddable": True},
            {"name": "val2", "type": "string", "default": "", "embeddable": True}
        ],
        "return_type": "boolean"
    },
    "And": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "与",
        "parameters": [
            {"name": "operand1", "type": "boolean", "embeddable": True},
            {"name": "operand2", "type": "boolean", "embeddable": True}
        ],
        "return_type": "boolean"
    },
    "Or": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "或",
        "parameters": [
            {"name": "operand1", "type": "boolean", "embeddable": True},
            {"name": "operand2", "type": "boolean", "embeddable": True}
        ],
        "return_type": "boolean"
    },
    "Not": {
        "category": BlockCategory.OPERATORS,
        "type": BlockType.LOGICAL_OPERATOR,
        "description": "非",
        "parameters": [
            {"name": "operand", "type": "boolean", "embeddable": True}
        ],
        "return_type": "boolean"
    },
    
    # ============= Variables (变量) =============
    "Variable": {
        "category": BlockCategory.VARIABLES,
        "type": BlockType.OPERATOR,
        "description": "变量",
        "parameters": [
            {"name": "varname", "type": "string", "default": "my variable", "embeddable": False}
        ],
        "return_type": "mixed"
    },
    "SetVar": {
        "category": BlockCategory.VARIABLES,
        "type": BlockType.STATEMENT,
        "description": "设置变量",
        "parameters": [
            {"name": "varname", "type": "string", "default": "my variable", "embeddable": False},
            {"name": "value", "type": "string", "default": "0", "embeddable": True}
        ],
        "return_type": None
    },
}


_BLOCK_TYPE_BY_NAME = {
    "Trigger": BlockType.TRIGGER,
    "Operator": BlockType.OPERATOR,
    "LogicalOperator": BlockType.LOGICAL_OPERATOR,
    "Statement": BlockType.STATEMENT,
    "BranchStatement": BlockType.BRANCH_STATEMENT,
}

_BLOCK_CATEGORY_BY_NAME = {
    "events": BlockCategory.EVENTS,
    "motion": BlockCategory.MOTION,
    "looks": BlockCategory.LOOKS,
    "sound": BlockCategory.SOUND,
    "control": BlockCategory.CONTROL,
    "sensing": BlockCategory.SENSING,
    "operators": BlockCategory.OPERATORS,
    "variables": BlockCategory.VARIABLES,
    "music": BlockCategory.MUSIC,
    "physics": BlockCategory.PHYSICS,
    "stage": BlockCategory.STAGE,
    "magic": BlockCategory.MAGIC,
    "myblocks": BlockCategory.MYBLOCKS,
    "ui": BlockCategory.UI,
    "animation": BlockCategory.ANIMATION,
    "patches": BlockCategory.PATCHES,
    "experiment": BlockCategory.EXPERIMENT,
}


def _coerce_script_definition(definition: Dict[str, Any]) -> Dict[str, Any]:
    coerced = copy.deepcopy(definition)

    type_name = coerced.get("type")
    if isinstance(type_name, str):
        coerced["type"] = _BLOCK_TYPE_BY_NAME.get(type_name)

    category_name = coerced.get("category")
    if isinstance(category_name, str):
        coerced["category"] = _BLOCK_CATEGORY_BY_NAME.get(category_name)

    return coerced


def _merge_block_definition(
    base_definition: Optional[Dict[str, Any]],
    script_definition: Dict[str, Any],
) -> Dict[str, Any]:
    if not base_definition:
        return copy.deepcopy(script_definition)

    merged = copy.deepcopy(base_definition)

    for key in ("category", "type", "has_branch", "branch_count", "object_types"):
        if key in script_definition:
            merged[key] = script_definition[key]

    script_parameters = script_definition.get("parameters", [])
    base_parameters = merged.get("parameters", [])
    if script_parameters and (not base_parameters or len(base_parameters) != len(script_parameters)):
        merged["parameters"] = copy.deepcopy(script_parameters)

    if merged.get("return_type") in (None, "mixed") and script_definition.get("return_type"):
        merged["return_type"] = script_definition["return_type"]

    if not merged.get("description") and script_definition.get("description"):
        merged["description"] = script_definition["description"]

    return merged


def _build_block_definitions() -> Dict[str, Dict[str, Any]]:
    merged = copy.deepcopy(BASE_BLOCK_DEFINITIONS)

    try:
        script_definitions = load_script_block_definitions()
    except Exception:
        script_definitions = {}

    for define, raw_definition in script_definitions.items():
        definition = _coerce_script_definition(raw_definition)
        merged[define] = _merge_block_definition(merged.get(define), definition)

    return merged


BLOCK_DEFINITIONS = _build_block_definitions()


class BlockModel:
    """Block 数据模型"""
    
    def __init__(self, define: str, sections: Optional[List[Dict]] = None):
        """
        初始化 Block
        
        Args:
            define: Block 定义名称
            sections: Section 列表（可选）
        """
        self.define = define
        self.sections = sections or []
        
        # 从定义数据库获取 Block 信息
        self.definition = BLOCK_DEFINITIONS.get(define, {})
        self.category = self.definition.get("category")
        self.type = self.definition.get("type")
        self.parameters = self.definition.get("parameters", [])
        self.return_type = self.definition.get("return_type")
    
    def to_dict(self, include_next: bool = True) -> Dict[str, Any]:
        """
        转换为 JSON 字典
        
        Args:
            include_next: 是否包含 next 字段
        
        Returns:
            Block 的 JSON 字典
        """
        data = {
            "define": self.define
        }
        
        if self.sections:
            data["sections"] = self.sections
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockModel":
        """
        从 JSON 字典创建 Block
        
        Args:
            data: Block 的 JSON 数据
        
        Returns:
            BlockModel 实例
        """
        define = data.get("define", "")
        sections = data.get("sections", [])
        
        return cls(define, sections)
    
    def get_parameter_count(self) -> int:
        """获取参数数量"""
        if not self.sections:
            return 0
        
        # 参数在第一个 section 的 columns 中
        first_section = self.sections[0] if self.sections else {}
        columns = first_section.get("columns", [])
        
        # 过滤掉标签类型的列
        param_columns = [col for col in columns if col.get("type") != "label"]
        return len(param_columns)
    
    def set_parameter(self, index: int, value: Union[str, Dict]) -> None:
        """
        设置参数值
        
        Args:
            index: 参数索引
            value: 参数值（字符串或嵌套 Block）
        """
        if isinstance(value, list):
            raise ValueError(
                "Block parameters do not support JSON array values; write arrays through "
                "typed workspace fields such as props2 SimpleList.value or res."
            )

        if not self.sections:
            self.sections.append({"columns": []})
        
        first_section = self.sections[0]
        if "columns" not in first_section:
            first_section["columns"] = []
        
        columns = first_section["columns"]
        
        # 找到第 index 个非标签列
        param_index = 0
        for i, col in enumerate(columns):
            if col.get("type") != "label":
                if param_index == index:
                    if isinstance(value, str):
                        col["value"] = value
                    elif isinstance(value, dict):
                        col["value"] = value
                    return
                param_index += 1
        
        # 如果没找到，创建新的列
        new_column = {
            "type": "value" if isinstance(value, str) else "block"
        }
        if isinstance(value, str):
            new_column["value"] = value
        else:
            new_column["value"] = value
        
        columns.append(new_column)


def _is_custom_myblock_define(define: Any) -> bool:
    return isinstance(define, str) and define.endswith("/myblockdefine")


def _validate_block_value_entry(entry: Dict[str, Any], path: str, value_key: str) -> Optional[str]:
    if "name" in entry and not isinstance(entry["name"], str):
        return f"{path}.name must be a string"
    if "customPopup" in entry and not (
        isinstance(entry["customPopup"], int) and not isinstance(entry["customPopup"], bool)
    ):
        return f"{path}.customPopup must be an integer"

    if "type" not in entry:
        return None

    entry_type = entry["type"]
    if not isinstance(entry_type, str):
        return f"{path}.type must be a string"

    if entry_type == "var":
        if value_key not in entry:
            return f"{path} missing required field: {value_key}"
        if not isinstance(entry[value_key], str):
            return f"{path}.{value_key} must be a string for var entries"
    elif entry_type == "block":
        if value_key not in entry:
            return f"{path} missing required field: {value_key}"
        if not isinstance(entry[value_key], dict):
            return f"{path}.{value_key} must be a dictionary for block entries"

    return None


def validate_block_value_entry(entry: Dict[str, Any], path: str, value_key: str) -> Optional[str]:
    return _validate_block_value_entry(entry, path, value_key)


def _validate_block_structure(
    block: Dict[str, Any],
    path: str,
    allowed_custom_defines: Optional[set[str]] = None,
    allow_unsupported_defines: bool = False,
) -> tuple[bool, Optional[str]]:
    if not isinstance(block, dict):
        return False, f"{path} must be a dictionary"

    if "define" not in block:
        return False, f"{path} missing required field: define"

    define = block["define"]
    if not isinstance(define, str) or not define:
        return False, f"{path}.define must be a non-empty string"

    block_info = BLOCK_DEFINITIONS.get(define)
    unsupported_message: Optional[str] = None
    if not block_info:
        if _is_custom_myblock_define(define):
            if allowed_custom_defines is not None and define not in allowed_custom_defines:
                unsupported_message = f"{path} references undefined myblock: {define}"
        else:
            unsupported_message = f"{path} uses unsupported block define: {define}"

    sections = block.get("sections", [])

    if "sections" in block and not isinstance(sections, list):
        return False, f"{path}.sections must be a list"

    for i, section in enumerate(sections):
        section_path = f"{path}.sections[{i}]"
        if not isinstance(section, dict):
            return False, f"{section_path} must be a dictionary"

        if "params" in section:
            params = section["params"]
            if not isinstance(params, list):
                return False, f"{section_path}.params must be a list"
            for j, entry in enumerate(params):
                entry_path = f"{section_path}.params[{j}]"
                if not isinstance(entry, dict):
                    return False, f"{entry_path} must be a dictionary"
                entry_error = _validate_block_value_entry(entry, entry_path, "val")
                if entry_error:
                    return False, entry_error
                nested = entry.get("val")
                if isinstance(nested, dict):
                    is_valid, error = _validate_block_structure(
                        nested,
                        f"{entry_path}.val",
                        allowed_custom_defines,
                        allow_unsupported_defines,
                    )
                    if not is_valid:
                        return is_valid, error

        if "columns" in section:
            columns = section["columns"]
            if not isinstance(columns, list):
                return False, f"{section_path}.columns must be a list"
            for j, entry in enumerate(columns):
                entry_path = f"{section_path}.columns[{j}]"
                if not isinstance(entry, dict):
                    return False, f"{entry_path} must be a dictionary"
                entry_error = _validate_block_value_entry(entry, entry_path, "value")
                if entry_error:
                    return False, entry_error
                nested = entry.get("value")
                if isinstance(nested, dict):
                    is_valid, error = _validate_block_structure(
                        nested,
                        f"{entry_path}.value",
                        allowed_custom_defines,
                        allow_unsupported_defines,
                    )
                    if not is_valid:
                        return is_valid, error

        if "children" in section:
            children = section["children"]
            if not isinstance(children, list):
                return False, f"{section_path}.children must be a list"
            for j, child in enumerate(children):
                is_valid, error = _validate_block_structure(
                    child,
                    f"{section_path}.children[{j}]",
                    allowed_custom_defines,
                    allow_unsupported_defines,
                )
                if not is_valid:
                    return is_valid, error

        if "child" in section and section["child"] is not None:
            child = section["child"]
            if not isinstance(child, dict):
                return False, f"{section_path}.child must be a dictionary"
            is_valid, error = _validate_block_structure(
                child,
                f"{section_path}.child",
                allowed_custom_defines,
                allow_unsupported_defines,
            )
            if not is_valid:
                return is_valid, error

    if "next" in block and block["next"] is not None:
        if not isinstance(block["next"], dict):
            return False, f"{path}.next must be a dictionary"
        is_valid, error = _validate_block_structure(
            block["next"],
            f"{path}.next",
            allowed_custom_defines,
            allow_unsupported_defines,
        )
        if not is_valid:
            return is_valid, error

    if unsupported_message and not allow_unsupported_defines:
        return False, unsupported_message

    if block_info:
        block_type = block_info.get("type")
        has_branch = bool(block_info.get("has_branch"))
        allows_children = has_branch or block_type == BlockType.TRIGGER

        if block_type == BlockType.TRIGGER:
            if len(sections) != 1:
                return False, f"{path} trigger blocks must use exactly 1 section"
            if block.get("next"):
                return False, f"{path} trigger blocks must attach statements via section children, not next"

        if has_branch:
            expected_sections = block_info.get("branch_count", 1)
            if not sections:
                return False, f"{path} branch blocks must define at least 1 section"
            if len(sections) > expected_sections:
                return False, f"{path} branch blocks may only use {expected_sections} section(s)"

        if not allows_children:
            for i, section in enumerate(sections):
                if "children" in section or "child" in section:
                    return False, f"{path}.sections[{i}] cannot contain child blocks for {define}"

    return True, None


def validate_block_structure(
    block: Dict[str, Any],
    allowed_custom_defines: Optional[set[str]] = None,
    allow_unsupported_defines: bool = False,
) -> tuple[bool, Optional[str]]:
    """
    验证 Block JSON 结构的完整性
    
    Args:
        block: Block JSON 数据
    
    Returns:
        (is_valid, error_message) 元组
    """
    return _validate_block_structure(
        block,
        "block",
        allowed_custom_defines,
        allow_unsupported_defines,
    )


def get_block_type_info(define: str) -> Optional[Dict[str, Any]]:
    """
    获取 Block 类型信息
    
    Args:
        define: Block 定义名称
    
    Returns:
        Block 定义信息，如果不存在则返回 None
    """
    return BLOCK_DEFINITIONS.get(define)


def _collect_block_object_type_errors(
    block: Dict[str, Any],
    object_types: Sequence[str],
    owner_label: str,
    path: str,
    errors: List[str],
) -> None:
    if not isinstance(block, dict):
        return

    define = block.get("define")
    block_info = BLOCK_DEFINITIONS.get(define) if isinstance(define, str) else None
    allowed_types = block_info.get("object_types") if block_info else None
    if allowed_types and not set(object_types).intersection(allowed_types):
        effective = ", ".join(object_types)
        owner_description = owner_label
        if owner_label and len(object_types) > 1:
            owner_description = f"{owner_label} (effective: {effective})"
        elif not owner_description:
            owner_description = effective
        errors.append(
            f"{path} uses {define}, which is not allowed for owner type {owner_description} "
            f"(allowed: {', '.join(allowed_types)})"
        )

    sections = block.get("sections", [])
    if isinstance(sections, list):
        for section_index, section in enumerate(sections):
            if not isinstance(section, dict):
                continue

            params = section.get("params", [])
            if isinstance(params, list):
                for param_index, entry in enumerate(params):
                    if not isinstance(entry, dict):
                        continue
                    nested = entry.get("val")
                    if isinstance(nested, dict):
                        _collect_block_object_type_errors(
                            nested,
                            object_types,
                            owner_label,
                            f"{path}.sections[{section_index}].params[{param_index}].val",
                            errors,
                        )

            columns = section.get("columns", [])
            if isinstance(columns, list):
                for column_index, entry in enumerate(columns):
                    if not isinstance(entry, dict):
                        continue
                    nested = entry.get("value")
                    if isinstance(nested, dict):
                        _collect_block_object_type_errors(
                            nested,
                            object_types,
                            owner_label,
                            f"{path}.sections[{section_index}].columns[{column_index}].value",
                            errors,
                        )

            children = section.get("children", [])
            if isinstance(children, list):
                for child_index, child in enumerate(children):
                    _collect_block_object_type_errors(
                        child,
                        object_types,
                        owner_label,
                        f"{path}.sections[{section_index}].children[{child_index}]",
                        errors,
                    )

            child = section.get("child")
            if isinstance(child, dict):
                _collect_block_object_type_errors(
                    child,
                    object_types,
                    owner_label,
                    f"{path}.sections[{section_index}].child",
                    errors,
                )

    next_block = block.get("next")
    if isinstance(next_block, dict):
        _collect_block_object_type_errors(
            next_block,
            object_types,
            owner_label,
            f"{path}.next",
            errors,
        )


def collect_block_object_type_errors(
    block: Dict[str, Any],
    object_type: Optional[Union[str, Sequence[str]]],
    path: str = "block",
    owner_label: Optional[str] = None,
) -> List[str]:
    if isinstance(object_type, str):
        object_types = [object_type] if object_type else []
    else:
        object_types = [value for value in (object_type or []) if isinstance(value, str) and value]

    if not object_types:
        return []

    errors: List[str] = []
    _collect_block_object_type_errors(
        block,
        object_types,
        owner_label if isinstance(owner_label, str) and owner_label else object_types[0],
        path,
        errors,
    )
    return errors
