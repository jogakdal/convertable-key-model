from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Any

from advanced_python_singleton.singleton import Singleton
from pydantic import BaseModel, model_validator


# =============================================================================
# 문자열 케이스 판별 및 변환 함수
# =============================================================================

def is_snake_case(s: str) -> bool:
    return '_' in s and s == s.lower()

def is_camel_case(s: str) -> bool:
    return s[0].islower() and not '_' in s and not s == s.lower()

def is_pascal_case(s: str) -> bool:
    return s[0].isupper() and not '_' in s


def to_self(s: str) -> str:
    """입력값을 그대로 반환하는, 즉 변환을 하지 않는 함수"""
    return s

def to_camel(s: str) -> str:
    if is_camel_case(s):
        return s
    s = re.sub(r'_([a-zA-Z0-9])', lambda x: x.group(1).upper(), s)
    s = s[0].lower() + s[1:]
    return s

def to_snake(s: str) -> str:
    if is_snake_case(s):
        return s
    s = re.sub(r'(?<!^)(?=[A-Z0-9])', '_', s).lower()
    return s

def to_pascal(s: str) -> str:
    if is_pascal_case(s):
        return s
    s = re.sub(r'_([a-zA-Z0-9])', lambda x: x.group(1).upper(), s)
    s = s[0].upper() + s[1:]
    return ''.join(word.capitalize() for word in re.split(r'_|(?=[A-Z0-9])', s))

def null_func(x):
    """이 형태의 함수형 변수가 null인지 여부 체크 용"""
    return x


@dataclass
class CasePair:
    """
    케이스 이름과 해당 케이스로 변환하는 함수를 한 쌍으로 관리하는 데이터 클래스.

    Attributes:
        case: 케이스 이름 (예: 'snake', 'camel', 'pascal')
        converter: 문자열을 해당 케이스로 변환하는 함수
    """
    case: str
    converter: Callable[[str], str]


class CaseConvention(Enum):
    """
    문자열의 케이스 컨벤션을 정의하는 열거형.
    각 멤버는 CasePair 객체를 가지며, 비교 시 대소문자 구분 없이 수행된다.
    """

    SELF = CasePair('self', to_self) # 변환 없음
    SNAKE = CasePair('snake', to_snake)
    CAMEL = CasePair('camel', to_camel)
    PASCAL = CasePair('pascal', to_pascal)
    NULL = CasePair('null', null_func) # 컨벤션 지정되지 않음

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value.case.lower() == other.lower()

        return super().__eq__(other)

    def __str__(self):
        return self.value.case

    @staticmethod
    def from_string(text):
        for name, member in CaseConvention.__members__.items():
            if text.lower() == member.value.case.lower():
                return CaseConvention[name]

        return CaseConvention.NULL


# =============================================================================
# ConvertableKeyModel: 동적 키 변환을 지원하는 BaseModel 확장 클래스
# =============================================================================

class ResponseKeyConverter(metaclass=Singleton):
    """
    클래스 별 필드의 alias와 serialize할 케이스 컨벤션을 관리하는 싱글톤 클래스.
    """

    def __init__(self):
        self.clear()

    def clear(self) -> ResponseKeyConverter:
        self.alias_map = {}
        self.convention_map = {}
        self.default_case_convention = CaseConvention.SELF

        return self

    def add_alias(self, cls: type, key_name: str, alias: str) -> ResponseKeyConverter:
        """
        특정 클래스에 대해 하나의 alias를 추가한다.

        Args:
            cls: 대상 클래스
            key_name: 원본 키 이름
            alias: 매핑된 alias

        Returns:
            ResponseKeyConverter
        """

        self.alias_map.setdefault(cls.__name__, {})[key_name] = alias
        return self

    def add_aliases(self, cls: type, aliases: dict[str, str]) -> ResponseKeyConverter:
        self.alias_map.setdefault(cls.__name__, {}).update(aliases)
        return self

    def get_alias_map(self, cls: type) -> dict[str, str]:
        """
        특정 클래스에 등록된 alias 맵을 반환한다.

        Args:
            cls: 대상 클래스

        Returns:
            alias 매핑 딕셔너리 (없으면 빈 딕셔너리)
        """
        return self.alias_map.get(cls.__name__, {})

    def set_default_case_convention(self, case_convention: CaseConvention) -> ResponseKeyConverter:
        self.default_case_convention = case_convention
        return self

    def add_case_convention(self, cls: type, case_convention: CaseConvention) -> ResponseKeyConverter:
        self.convention_map[cls.__name__] = case_convention
        return self

    def get_case_convention(self, cls: type) -> CaseConvention:
        return self.convention_map.get(cls.__name__, self.default_case_convention)

# =============================================================================
# ConvertableKeyModel: 동적 키 변환을 지원하는 BaseModel 확장 클래스
# =============================================================================

class ConvertableKeyModel(BaseModel):
    """
    JSON 직렬화/역직렬화 시 필드명과 케이스를 동적으로 변환하는 기능을 제공하는 BaseModel 확장 클래스.

    생성자 kwargs:
        - alias_map: dict[str, str]
            -> 키 필드명을 변환할 때 사용할 alias 맵.
        - case_converter: Callable[[str], str]
            -> 키 필드명의 케이스 변환 함수.
        - case_convention: CaseConvention
            -> 키 필드명의 케이스 컨벤션 변환 규칙.

    주의:
        case_converter와 case_convention이 동시에 지정되면, case_converter가 우선 적용된다.
    """

    def __init__(self, **kwargs):
        alias_map = kwargs.get('alias_map', None)
        case_converter: Callable[[str], str] = kwargs.pop('case_converter', null_func)
        case_convention = kwargs.pop('case_convention', CaseConvention.NULL)
        if case_converter == null_func:
            case_converter = case_convention.value.converter

        super().__init__(**kwargs)

        self._alias_map = alias_map if alias_map is not None else {}
        self._case_converter = case_converter


    @model_validator(mode='before')
    @classmethod
    def normalize_keys(cls, data):
        """
        JSON 키가 어떤 case convention으로 들어와도 클래스의 필드명과 매핑될 수 있도록 변환
        alias map이 정의되어 있으면 맵의 alias로 필드명 매핑
        """
        if not isinstance(data, dict):
            return data

        alias_map = data.pop('alias_map', None) or ResponseKeyConverter().alias_map.get(cls.__name__, {})
        reverse_alias_map = { to_snake(v): k for k, v in getattr(cls, '__alias_map_reference__', alias_map).items() }

        field_names = cls.model_fields.keys()
        converted_data = {}

        for key, value in data.items():
            normalized_key = to_snake(key)
            if normalized_key in reverse_alias_map:
                matching_key = reverse_alias_map[normalized_key]
            else:
                matching_key = next((f for f in field_names if to_snake(f) == normalized_key), key)

            converted_data[matching_key] = value

        return converted_data

    @staticmethod
    def _convert_keys_in_dict(cls, base: dict[str, Any], converter=None, alias_map=None, **kwargs) -> dict[str, Any]:
        def serialize_value(value):
            if isinstance(value, ConvertableKeyModel):
                return value.convert_key(**kwargs)
            elif isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, BaseModel):
                return ConvertableKeyModel._convert_keys_in_dict(
                    value,
                    value.model_dump(**kwargs_copy),
                    ResponseKeyConverter().get_case_convention(value.__class__).value.converter,
                    ResponseKeyConverter().get_alias_map(value.__class__),
                    **kwargs
                )
            elif isinstance(value, Enum):
                return value.value
            else:
                return value

        if not converter:
            converter = cls._case_converter
        if not alias_map:
            alias_map = {}

        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('case_converter', null_func)
        kwargs_copy.pop('case_convention', CaseConvention.NULL)

        new_dict = {}
        for key, value in base.items():
            orig_value = getattr(cls, key, None)
            new_key = alias_map.get(key, key)
            if converter:
                new_key = converter(new_key)

            if isinstance(orig_value, list):
                new_list = []
                for item in orig_value:
                    new_list.append(serialize_value(item))
                new_dict[new_key] = new_list
            else:
                new_dict[new_key] = serialize_value(orig_value)

        return new_dict

    def convert_key(self, **kwargs) -> dict[str, Any]:
        """
        BaseModel의 model_dump() 결과에 대해 키 변환을 수행하고 json으로 serialize 한다.
        변환 함수 선택 우선 순위는 다음과 같다:
          1. convert_key() 인자: case_converter, case_convention
          2. 인스턴스 변수 _case_converter
          3. ResponseKeyConverter에 등록된 케이스 컨벤션
          4. ResponseKeyConverter에 등록된 기본 변환 함수

        인자에 case_converter나 case_convention이 지정되면 하위 객체에도 동일하게 적용된다.

        Args:
            case_converter: Callable[[str], str]
                : 필드명의 케이스 컨벤션 변환 시 사용할 변환 함수
            case_convention: CaseConvention
                : 키 필드명의 케이스 컨벤션 변환 시 사용할 변환 규칙
            kwargs: model_dump()에 전달할 옵션 및 변환 관련 인자

        Returns:
            키가 변환된 딕셔너리
        """

        kwargs_copy = kwargs.copy()

        converter: Callable[[str], str] = kwargs_copy.pop('case_converter', null_func)
        case_convention: CaseConvention = kwargs_copy.pop('case_convention', CaseConvention.NULL)

        if converter == null_func:
            if case_convention != CaseConvention.NULL:
                converter = case_convention.value.converter
            else:
                if hasattr(self, '_case_converter') and self._case_converter != null_func:
                    converter = self._case_converter
                else:
                    converter = ResponseKeyConverter().get_case_convention(self.__class__).value.converter

        return ConvertableKeyModel._convert_keys_in_dict(
            self,
            super().model_dump(**kwargs_copy),
            converter,
            self._alias_map if hasattr(self, '_alias_map') and self._alias_map else ResponseKeyConverter().get_alias_map(self.__class__),
            **kwargs
        )
