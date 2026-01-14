import os
import pytest

from ..app.services.extract import (
    extract_action_items,
    extract_action_items_llm,
    _is_action_line,
    _looks_imperative,
)


# ==================== 规则方式测试 ====================

def test_extract_bullets_and_checkboxes():
    """测试基本的项目符号和复选框提取"""
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_with_keywords():
    """测试关键字前缀的行动项"""
    text = """
    TODO: Review pull request
    Action: Update documentation
    Next: Schedule team meeting
    """.strip()

    items = extract_action_items(text)
    assert "Review pull request" in items
    assert "Update documentation" in items
    assert "Schedule team meeting" in items


def test_extract_mixed_formats():
    """测试混合格式的行动项"""
    text = """
    Project tasks:
    - [ ] Create user authentication
    • Add logging functionality
    1. Implement caching
    2. Write unit tests
    [TODO] Deploy to staging
    Action: Review code quality
    """.strip()

    items = extract_action_items(text)
    assert len(items) == 6
    assert "Create user authentication" in items
    assert "Add logging functionality" in items
    assert "Implement caching" in items
    assert "Write unit tests" in items
    assert "Deploy to staging" in items
    assert "Review code quality" in items


def test_extract_deduplication():
    """测试去重功能"""
    text = """
    - Write tests
    - write tests
    - WRITE TESTS
    * Write tests
    """.strip()

    items = extract_action_items(text)
    assert len(items) == 1
    assert "Write tests" in items


def test_extract_empty_text():
    """测试空文本"""
    assert extract_action_items("") == []
    assert extract_action_items("   ") == []
    assert extract_action_items("\n\n\n") == []


def test_extract_no_action_items():
    """测试没有行动项的普通文本"""
    text = """
    This is a regular paragraph with no action items.
    It contains multiple sentences. None of them are tasks.
    Just some narrative content.
    """.strip()

    items = extract_action_items(text)
    # 应该尝试使用启发式方法，但可能找不到任何项
    assert isinstance(items, list)


def test_extract_imperative_sentences():
    """测试祈使句启发式提取"""
    text = """
    Add new feature to the dashboard.
    Implement user authentication.
    Fix the bug in payment processing.
    Update the API documentation.
    """.strip()

    items = extract_action_items(text)
    assert len(items) >= 4
    assert any("Add new feature" in item for item in items)
    assert any("Implement user authentication" in item for item in items)


def test_extract_with_special_characters():
    """测试包含特殊字符的行动项"""
    text = """
    - [ ] Set up PostgreSQL database (v14+)
    * Implement REST API @ /api/v1
    1. Write tests for User#create method
    - Add support for UTF-8 encoding
    """.strip()

    items = extract_action_items(text)
    assert len(items) == 4
    assert "Set up PostgreSQL database (v14+)" in items
    assert "Implement REST API @ /api/v1" in items


def test_extract_multiline_items():
    """测试多行文本中的行动项"""
    text = """
    Meeting Notes - 2024-01-15
    
    Attendees: Alice, Bob, Charlie
    
    Action Items:
    - [ ] Alice: Review the proposal
    - [ ] Bob: Update the timeline
    - [ ] Charlie: Prepare presentation
    
    Next Steps:
    1. Schedule follow-up meeting
    2. Send out meeting minutes
    
    Notes:
    The team discussed various topics.
    """.strip()

    items = extract_action_items(text)
    assert len(items) >= 5
    assert any("Review the proposal" in item for item in items)
    assert any("Schedule follow-up meeting" in item for item in items)


def test_is_action_line():
    """测试 _is_action_line 辅助函数"""
    assert _is_action_line("- Task item") is True
    assert _is_action_line("* Task item") is True
    assert _is_action_line("1. Task item") is True
    assert _is_action_line("- [ ] Task item") is True
    assert _is_action_line("TODO: Task item") is True
    assert _is_action_line("Action: Task item") is True
    assert _is_action_line("Next: Task item") is True
    assert _is_action_line("[TODO] Task item") is True
    assert _is_action_line("Regular sentence") is False
    assert _is_action_line("") is False
    assert _is_action_line("   ") is False


def test_looks_imperative():
    """测试 _looks_imperative 辅助函数"""
    assert _looks_imperative("Add new feature") is True
    assert _looks_imperative("Create database schema") is True
    assert _looks_imperative("Implement authentication") is True
    assert _looks_imperative("Fix the bug") is True
    assert _looks_imperative("Update documentation") is True
    assert _looks_imperative("Write tests") is True
    assert _looks_imperative("This is a regular sentence") is False
    assert _looks_imperative("The system works well") is False
    assert _looks_imperative("") is False


# ==================== LLM 方式测试 ====================

@pytest.mark.skipif(
    os.getenv("SKIP_LLM_TESTS") == "1",
    reason="跳过 LLM 测试（设置 SKIP_LLM_TESTS=1 可跳过）"
)
class TestLLMExtraction:
    """LLM 提取功能测试（需要 Ollama 服务运行）"""
    
    def test_extract_llm_basic(self):
        """测试 LLM 基本提取功能"""
        text = """
        - [ ] Set up database
        * implement API extract endpoint
        1. Write tests
        """.strip()
        
        items = extract_action_items_llm(text)
        
        # LLM 应该能提取出这些行动项
        assert len(items) >= 3
        assert any("database" in item.lower() for item in items)
        assert any("api" in item.lower() for item in items)
        assert any("test" in item.lower() for item in items)
    
    def test_extract_llm_empty_text(self):
        """测试 LLM 处理空文本"""
        assert extract_action_items_llm("") == []
        assert extract_action_items_llm("   ") == []
        assert extract_action_items_llm("\n\n") == []
    
    def test_extract_llm_no_items(self):
        """测试 LLM 没有找到行动项"""
        text = "This is just a regular paragraph with no action items. Just some narrative content."
        
        items = extract_action_items_llm(text)
        # LLM 可能返回空列表或少量误判项
        assert isinstance(items, list)
        assert len(items) <= 1  # 允许少量误判
    
    def test_extract_llm_with_keywords(self):
        """测试 LLM 提取关键字前缀的行动项"""
        text = """
        TODO: Review pull request
        Action: Update documentation
        Next: Schedule team meeting
        """.strip()
        
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        assert any("review" in item.lower() for item in items)
        assert any("documentation" in item.lower() or "update" in item.lower() for item in items)
        assert any("meeting" in item.lower() or "schedule" in item.lower() for item in items)
    
    def test_extract_llm_mixed_formats(self):
        """测试 LLM 处理混合格式"""
        text = """
        Project tasks:
        - [ ] Create user authentication
        • Add logging functionality
        1. Implement caching
        2. Write unit tests
        [TODO] Deploy to staging
        Action: Review code quality
        """.strip()
        
        items = extract_action_items_llm(text)
        
        # LLM 应该能识别多种格式
        assert len(items) >= 5
        assert any("authentication" in item.lower() for item in items)
        assert any("logging" in item.lower() for item in items)
        assert any("caching" in item.lower() for item in items)
    
    def test_extract_llm_with_custom_model(self):
        """测试使用自定义模型"""
        text = "- Task 1: Set up environment\n- Task 2: Write documentation"
        custom_model = "llama3.2:3b"
        
        try:
            items = extract_action_items_llm(text, model=custom_model)
            # 如果模型可用，应该能提取出内容
            assert isinstance(items, list)
        except Exception as e:
            # 如果模型不可用，应该优雅地处理
            pytest.skip(f"Model {custom_model} not available: {e}")
    
    def test_extract_llm_complex_text(self):
        """测试 LLM 处理复杂文本"""
        text = """
        Project Meeting Notes - Q1 2024
        
        Attendees: Alice, Bob, Charlie
        
        Discussion:
        We talked about the new features and decided on the following action items.
        
        Action Items:
        - [ ] Alice: Review the proposal by Friday
        - [ ] Bob: Update the project timeline
        * Charlie: Prepare presentation for stakeholders
        1. Schedule follow-up meeting next week
        2. Send meeting minutes to all attendees
        
        Additional Notes:
        The team is making good progress. Next meeting scheduled for next Monday.
        """.strip()
        
        items = extract_action_items_llm(text)
        
        # LLM 应该能从复杂文本中提取行动项
        assert len(items) >= 4
        assert any("review" in item.lower() or "proposal" in item.lower() for item in items)
        assert any("timeline" in item.lower() or "update" in item.lower() for item in items)
        assert any("presentation" in item.lower() or "prepare" in item.lower() for item in items)
    
    def test_extract_llm_special_characters(self):
        """测试 LLM 处理特殊字符"""
        text = """
        - Set up PostgreSQL database (v14+)
        * Implement REST API @ /api/v1
        1. Write tests for User#create method
        """.strip()
        
        items = extract_action_items_llm(text)
        
        assert len(items) >= 3
        assert any("postgresql" in item.lower() or "database" in item.lower() for item in items)
        assert any("api" in item.lower() for item in items)
        assert any("test" in item.lower() for item in items)
    
    def test_extract_llm_unicode_characters(self):
        """测试 LLM 处理 Unicode 字符"""
        text = """
        - 创建数据库架构
        - Créer l'API REST
        - Add user authentication
        """.strip()
        
        items = extract_action_items_llm(text)
        
        # LLM 应该能处理多语言文本
        assert len(items) >= 2
        assert isinstance(items, list)
        # 验证返回的都是字符串
        for item in items:
            assert isinstance(item, str)
            assert len(item) > 0


# ==================== 边界情况测试 ====================

def test_extract_very_long_text():
    """测试非常长的文本"""
    text = "\n".join([f"- Task {i}" for i in range(1000)])
    
    items = extract_action_items(text)
    assert len(items) == 1000
    assert "Task 0" in items
    assert "Task 999" in items


def test_extract_unicode_characters():
    """测试 Unicode 字符"""
    text = """
    - 创建数据库架构
    - Créer l'API REST
    - Добавить тесты
    - テストを書く
    """.strip()
    
    items = extract_action_items(text)
    assert len(items) == 4
    assert "创建数据库架构" in items


def test_extract_nested_lists():
    """测试嵌套列表"""
    text = """
    - Main task 1
      - Subtask 1.1
      - Subtask 1.2
    - Main task 2
      * Subtask 2.1
    """.strip()
    
    items = extract_action_items(text)
    # 应该提取所有层级的任务
    assert len(items) >= 3


def test_extract_with_urls():
    """测试包含 URL 的行动项"""
    text = """
    - Review PR at https://github.com/user/repo/pull/123
    - Check documentation at https://docs.example.com
    - [ ] Update API endpoint http://api.example.com/v1
    """.strip()
    
    items = extract_action_items(text)
    assert len(items) == 3
    assert any("github.com" in item for item in items)


def test_extract_with_code_snippets():
    """测试包含代码片段的行动项"""
    text = """
    - Implement `getUserById()` function
    - Add `try-catch` block to error handling
    - Update `config.json` file
    """.strip()
    
    items = extract_action_items(text)
    assert len(items) == 3
    assert any("getUserById()" in item for item in items)
