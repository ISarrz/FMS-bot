import pytest
from modules.database_api.group.group import Group


@pytest.fixture(autouse=True)
def clear_database():
    for group in Group.all():
        group.delete()


def test_insert():
    group1 = Group.insert("11 класс")
    group2 = Group(name="11 класс")

    assert group2.id == group1.id
    assert group2.name == group1.name
    assert group2.name == "11 класс"


def test_children():
    group = Group.insert("11 класс")

    child1 = Group.insert("child 1")
    child2 = Group.insert("child 2")
    child3 = Group.insert("child 3")

    group.insert_child(child1)
    group.insert_child(child2)
    group.insert_child(child3)

    group.delete_child(child1)

    assert child2.parent.id == group.id
    assert group.parent is None

    # Проверим, что в детях остались только child2 и child3
    children_names = {child.name for child in group.children}
    assert children_names == {"child 2", "child 3"}

    group.name = "10 класс"
    assert group.name == "10 класс"


def test_relations_paths():
    root1 = Group.insert("root 1")
    root2 = Group.insert("root 2")
    root3 = Group.insert("root 3")

    roots = [r.name for r in Group.all_relations_roots()]
    assert set(roots) == {"root 1", "root 2", "root 3"}

    assert root1.relation_height == 0
    assert root1.relation_root.id == root1.id

    child1 = Group.insert("child 1")
    root1.insert_child(child1)

    assert child1.relation_height == 1
    assert child1.relation_root.id == root1.id

    child2 = Group.insert("child 2")
    child1.insert_child(child2)

    assert child2.relation_height == 2
    assert child2.relation_root.id == root1.id
    assert child2.parent.id == child1.id

    path_names = [g.name for g in child2.relation_path]
    assert path_names == ["root 1", "child 1", "child 2"]
