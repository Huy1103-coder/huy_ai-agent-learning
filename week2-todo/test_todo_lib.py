"""Todo 库的测试用例"""
import pytest
from todo_lib import (
    add_todo,
    find_todo,
    mark_done,
    mark_undone,
    delete_todo,
    clear_done,
    stats,
    save_todos,
    load_todos,
    get_next_id,
)


# ============================================
# Fixtures(共享的测试数据准备)
# ============================================

@pytest.fixture
def empty_todos():
    """提供一个空 todo 列表"""
    return []


@pytest.fixture
def sample_todos():
    """提供 3 条样本 todo(id=1,2,3)"""
    todos = []
    add_todo(todos, "学完第 2 周")
    add_todo(todos, "推到 GitHub")
    add_todo(todos, "写技术博客")
    return todos


# ============================================
# 测试 add_todo
# ============================================

def test_add_to_empty_list(empty_todos):
    """场景:向空列表加第一个 todo"""
    result = add_todo(empty_todos, "第一件事")
    
    assert len(empty_todos) == 1
    assert result["id"] == 1
    assert result["title"] == "第一件事"
    assert result["done"] is False
    assert "created_at" in result


def test_add_strips_whitespace(empty_todos):
    """场景:标题前后空格应该被自动去掉"""
    result = add_todo(empty_todos, "   有空格   ")
    assert result["title"] == "有空格"


def test_add_empty_title_raises(empty_todos):
    """场景:空标题或只有空格的标题应该报错"""
    with pytest.raises(ValueError):
        add_todo(empty_todos, "")
    
    with pytest.raises(ValueError):
        add_todo(empty_todos, "   ")


def test_add_assigns_incremental_ids(empty_todos):
    """场景:连续添加,id 应该自增"""
    a = add_todo(empty_todos, "A")
    b = add_todo(empty_todos, "B")
    c = add_todo(empty_todos, "C")
    
    assert a["id"] == 1
    assert b["id"] == 2
    assert c["id"] == 3


# ============================================
# 测试 find_todo
# ============================================

def test_find_existing(sample_todos):
    """场景:找一个存在的 todo"""
    todo = find_todo(sample_todos, 2)
    assert todo is not None
    assert todo["title"] == "推到 GitHub"


def test_find_nonexistent(sample_todos):
    """场景:找一个不存在的 todo,应该返回 None"""
    todo = find_todo(sample_todos, 999)
    assert todo is None


# ============================================
# 测试 mark_done / mark_undone
# ============================================

def test_mark_done_changes_status(sample_todos):
    """场景:标记某个 todo 为完成"""
    result = mark_done(sample_todos, 1)
    
    assert result["done"] is True
    # 验证修改是持久的(再 find 也是 True)
    assert find_todo(sample_todos, 1)["done"] is True


def test_mark_done_invalid_id_raises(sample_todos):
    """场景:标记不存在的 id,应该抛 ValueError"""
    with pytest.raises(ValueError, match="找不到"):
        mark_done(sample_todos, 999)


def test_mark_undone_reverts(sample_todos):
    """场景:把已完成的标记回未完成"""
    mark_done(sample_todos, 1)
    assert sample_todos[0]["done"] is True
    
    mark_undone(sample_todos, 1)
    assert sample_todos[0]["done"] is False


# ============================================
# 测试 delete_todo
# ============================================

def test_delete_existing(sample_todos):
    """场景:正常删除"""
    assert len(sample_todos) == 3
    deleted = delete_todo(sample_todos, 2)
    
    assert deleted["title"] == "推到 GitHub"
    assert len(sample_todos) == 2
    assert find_todo(sample_todos, 2) is None


def test_delete_nonexistent_raises(sample_todos):
    """场景:删除不存在的 id"""
    with pytest.raises(ValueError, match="找不到"):
        delete_todo(sample_todos, 999)


# ============================================
# 测试 clear_done
# ============================================

def test_clear_done_removes_only_done(sample_todos):
    """场景:清除所有已完成,保留未完成"""
    mark_done(sample_todos, 1)
    mark_done(sample_todos, 3)
    # 现在 1 和 3 是已完成,2 是未完成
    
    removed_count = clear_done(sample_todos)
    
    assert removed_count == 2
    assert len(sample_todos) == 1
    assert sample_todos[0]["id"] == 2   # 只剩没完成的


def test_clear_done_when_nothing_done(sample_todos):
    """场景:没有已完成的,清除应该返回 0"""
    removed_count = clear_done(sample_todos)
    assert removed_count == 0
    assert len(sample_todos) == 3


# ============================================
# 测试 stats
# ============================================

def test_stats_empty(empty_todos):
    """场景:空列表的统计"""
    result = stats(empty_todos)
    assert result == {"total": 0, "done": 0, "pending": 0}


def test_stats_mixed(sample_todos):
    """场景:有数据时的统计"""
    mark_done(sample_todos, 1)
    
    result = stats(sample_todos)
    assert result["total"] == 3
    assert result["done"] == 1
    assert result["pending"] == 2


# ============================================
# 测试 load_todos / save_todos(用 tmp_path)
# ============================================

def test_save_and_load_roundtrip(tmp_path):
    """场景:存进去再读出来,数据应该一致"""
    test_file = str(tmp_path / "test_todos.json")
    
    todos = []
    add_todo(todos, "A")
    add_todo(todos, "B")
    mark_done(todos, 1)
    
    save_todos(todos, test_file)
    loaded = load_todos(test_file)
    
    assert loaded == todos


def test_load_nonexistent_file(tmp_path):
    """场景:加载不存在的文件,应该返回空列表"""
    test_file = str(tmp_path / "does_not_exist.json")
    
    result = load_todos(test_file)
    assert result == []


# ============================================
# 测试 get_next_id 的边界条件
# ============================================

def test_next_id_empty():
    """场景:空列表,下一个 id 应该是 1"""
    assert get_next_id([]) == 1


def test_next_id_with_gaps():
    """场景:有删除导致 id 不连续,应该取最大 + 1"""
    todos = [
        {"id": 1, "title": "A", "done": False, "created_at": ""},
        {"id": 5, "title": "B", "done": False, "created_at": ""},
        {"id": 3, "title": "C", "done": False, "created_at": ""},
    ]
    assert get_next_id(todos) == 6   # max(1,5,3) + 1