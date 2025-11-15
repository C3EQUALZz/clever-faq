from dataclasses import FrozenInstanceError, dataclass, field, fields
from typing import ClassVar

import pytest

from clever_faq.domain.common.errors import DomainError, DomainFieldError
from clever_faq.domain.common.values.base import BaseValueObject
from tests.unit.factories.named_entity import (
    create_named_entity,
    create_named_entity_id,
    create_named_entity_subclass,
)
from tests.unit.factories.tagged_entity import create_tagged_entity
from tests.unit.factories.value_objects import (
    create_multi_field_vo,
    create_single_field_vo,
)


@pytest.mark.parametrize(
    "new_id",
    [
        pytest.param(1, id="same_id"),
        pytest.param(999, id="different_id"),
    ],
)
def test_entity_id_cannot_be_changed(new_id: int) -> None:
    sut = create_named_entity(id_=1)

    with pytest.raises(DomainError):
        sut.id = create_named_entity_id(new_id)


def test_entity_is_mutable_except_id() -> None:
    sut = create_named_entity(name="Alice")
    new_name = "Bob"

    sut.name = new_name

    assert sut.name == new_name


@pytest.mark.parametrize(
    ("name1", "name2"),
    [
        pytest.param("Alice", "Alice", id="same_name"),
        pytest.param("Alice", "Bob", id="different_name"),
    ],
)
def test_same_type_entities_with_same_id_are_equal(
    name1: str,
    name2: str,
) -> None:
    e1 = create_named_entity(name=name1)
    e2 = create_named_entity(name=name2)

    assert e1 == e2


def test_same_type_entities_with_different_id_are_not_equal() -> None:
    e1 = create_named_entity(id_=1)
    e2 = create_named_entity(id_=2)

    assert e1 != e2


def test_entities_of_different_types_are_not_equal() -> None:
    sut_id = 1
    e1 = create_named_entity(id_=sut_id)
    e2 = create_tagged_entity(id_=sut_id)

    assert e1 != e2


def test_entity_is_not_equal_to_subclass_with_same_id() -> None:
    parent = create_named_entity()
    child = create_named_entity_subclass(
        id_=parent.id.value,
        name=parent.name,
        value=1,
    )

    assert parent.__eq__(child) is False
    assert child.__eq__(parent) is False


def test_equal_entities_have_equal_hash() -> None:
    sut_id = 1
    e1 = create_named_entity(id_=sut_id, name="Alice")
    e2 = create_named_entity(id_=sut_id, name="Bob")

    assert e1 == e2
    assert hash(e1) == hash(e2)


def test_entity_can_be_used_in_set() -> None:
    e1 = create_named_entity(id_=1, name="Alice")
    e2 = create_named_entity(id_=1, name="Bob")
    e3 = create_named_entity(id_=2)
    e4 = create_tagged_entity(id_=1)

    entity_set = {e1, e2, e3, e4}

    assert len(entity_set) == 3


def test_child_cannot_init_with_no_instance_fields() -> None:
    # Arrange
    @dataclass(frozen=True)
    class EmptyVO(BaseValueObject):
        def _validate(self) -> None: ...

        def __str__(self) -> str:
            return ""

    # Act & Assert
    with pytest.raises(DomainFieldError):
        EmptyVO()


def test_child_cannot_init_with_only_class_fields() -> None:
    # Arrange
    @dataclass(frozen=True)
    class ClassFieldsVO(BaseValueObject):
        foo: ClassVar[int] = 0
        bar: ClassVar[str] = "baz"

        def _validate(self) -> None: ...

        def __str__(self) -> str:
            return ""

    # Act & Assert
    with pytest.raises(DomainFieldError):
        ClassFieldsVO()


def test_class_field_not_in_dataclass_fields() -> None:
    # Arrange
    @dataclass(frozen=True)
    class MixedFieldsVO(BaseValueObject):
        foo: ClassVar[int] = 0
        bar: str

        def _validate(self) -> None: ...

        def __str__(self) -> str: ...

    sut = MixedFieldsVO(bar="baz")

    # Act
    sut_fields = fields(sut)

    # Assert
    assert len(sut_fields) == 1
    assert sut_fields[0].name == "bar"
    assert sut_fields[0].type is str
    assert getattr(sut, sut_fields[0].name) == "baz"


def test_class_field_not_broken_by_slots() -> None:
    # Arrange
    @dataclass(frozen=True, slots=True)
    class MixedFieldsVO(BaseValueObject):
        foo: ClassVar[int] = 0
        bar: str

        def _validate(self) -> None: ...

        def __str__(self) -> str:
            return ""

    # Assert
    assert MixedFieldsVO.foo == 0


def test_class_field_final_equivalence() -> None:
    # Arrange
    @dataclass(frozen=True)
    class MixedFieldsVO:
        a: ClassVar[int] = 1
        b: ClassVar[str] = "bar"
        c: str = "baz"

    # Act
    sut_field_names = [f.name for f in fields(MixedFieldsVO)]

    # Assert
    assert sut_field_names == ["c"]


def test_is_immutable() -> None:
    # Arrange
    vo_value = 123
    sut = create_single_field_vo(vo_value)

    # Act & Assert
    with pytest.raises(FrozenInstanceError):
        # noinspection PyDataclass
        sut.value = vo_value + 1  # type: ignore[misc]


def test_equality() -> None:
    # Arrange
    vo1 = create_multi_field_vo()
    vo2 = create_multi_field_vo()

    # Assert
    assert vo1 == vo2


def test_inequality() -> None:
    # Arrange
    vo1 = create_multi_field_vo(value2="one")
    vo2 = create_multi_field_vo(value2="two")

    # Assert
    assert vo1 != vo2


def test_class_field_not_in_repr() -> None:
    # Arrange
    @dataclass(frozen=True, repr=False)
    class MixedFieldsVO(BaseValueObject):
        baz: int
        foo: ClassVar[int] = 0
        bar: ClassVar[str] = "baz"

        def _validate(self) -> None: ...

        def __str__(self) -> str:
            return "baz"

    sut = MixedFieldsVO(baz=1)
    sut2 = MixedFieldsVO(baz=1)

    # Act
    result = repr(sut)
    result2 = repr(sut2)

    # Assert
    assert result == result2


def test_hidden_field_not_in_repr() -> None:
    # Arrange
    @dataclass(frozen=True, repr=False)
    class HiddenFieldVO(BaseValueObject):
        visible: int
        hidden: int = field(repr=False)

        def _validate(self) -> None: ...

        def __str__(self) -> str:
            return str(self.hidden)

    sut = HiddenFieldVO(123, 456)
    sut2 = HiddenFieldVO(123, 123123)

    # Act
    result = repr(sut)
    result2 = repr(sut2)

    # Assert
    assert result == result2


def test_all_fields_hidden_repr() -> None:
    # Arrange
    @dataclass(frozen=True, repr=False)
    class HiddenFieldVO(BaseValueObject):
        hidden_1: int = field(repr=False)
        hidden_2: int = field(repr=False)

        def _validate(self) -> None: ...

        def __str__(self) -> str:
            return str(self.hidden_1) + str(self.hidden_2)

    sut = HiddenFieldVO(123, 456)
    an_sut = HiddenFieldVO(256, 123)

    # Act
    result = repr(sut)
    result2 = repr(an_sut)

    # Assert
    assert result == result2
