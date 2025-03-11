# convertable_key_model

- 이 모듈은 JSON 직렬화/역직렬화 시 모델의 필드명을 동적으로 변환할 수 있도록 지원합니다.
- **주요 클래스는 ConvertableKeyModel**이며, 이 클래스는 pydantic 모델(BaseModel) 객체를 JSON으로 serialize할 때
모델에 포함된 필드와 다른 필드명 또는 다른 케이스 컨벤션으로 변환해서 생성할 수 있도록 제작되었습니다.
- 또한 JSON으로부터 deserialize할 때에도, 입력 JSON 데이터의 키를 모델의 필드명과 매핑시켜 줍니다.
- ResponseKeyConverter 클래스는 이러한 변환 내용을 전역적으로 관리하는 보조 클래스입니다.
---
# 설치
```bash
pip install convertable-key-model
```
이 프로젝트의 전체 소스 코드를 다운 받으시려면 저장소를 클론하고 필요한 종속성을 설치하십시오:

```sh
git clone https://github.com/jogakdal/convertable-key-model.git
cd <repository-directory>
pip install -r requirements.txt
```

# class 설명
## 1. ConvertableKeyModel 클래스

### 목적
- pydantic 모델(BaseModel)을 확장하여, JSON으로 serialize할 때 모델의 필드명을 별도의 alias 또는 지정된 케이스 컨벤션으로 변환할 수 있습니다.
- 또한, deserialize할 때 객체의 필드명과 매핑된 alias를 인식하여, 케이스 컨벤션에 관계없이 데이터를 올바르게 매핑할 수 있도록 지원합니다.
  
### 핵심 기능:
1. Alias 매핑
   - 모델의 필드명과 다른 이름(alias)으로 데이터를 읽어들이거나 출력할 수 있습니다.
   - 이 동작은 deserialize 시에, **`__alias_map_reference__`** 필드를 클래스 내부에 정의하거나, 생성자 인자 또는 전역 설정을 통해 이루어집니다.
2. 케이스 컨벤션 변환
   - 필드명의 케이스 컨벤션(예: camelCase, snake_case, PascalCase)을 변환합니다.
   - alias로 매핑한 후, 지정된 케이스 컨벤션으로 다시 변환할 수 있도록 두 기능은 독립적으로 동작합니다.
3. Deserialize 시 별도의 케이스 컨벤션을 지정하지 않아도 단지 컨벤션만 다른 필드명은 자동으로 매핑됩니다. 
   - 예를 들어, 모델 필드명이 camelCase이고, JSON 데이터의 키가 snake_case인 경우에도 자동으로 매핑됩니다. 
4. 직렬화 (Serialize) 시 주의 사항
   - BaseModel의 자동 덤프 또는 model_dump() 호출 시에는 alias나 케이스 변환이 적용되지 않습니다.
   - 반드시 convert_key() 함수를 명시적으로 호출해야 alias 매핑 및 케이스 컨벤션 변환된 결과를 얻을 수 있습니다.

### 생성자 인자 (kwargs)
- **alias_map (dict[str, str])**  
모델 객체의 필드와 JSON 데이터의 키를 매핑할 때 사용할 alias 맵입니다.  
형식: { '모델의 필드명': 'JSON의 필드명' }  

- **case_converter (Callable[[str], str])**  
필드명의 케이스(대소문자) 변환에 사용할 lambda 함수를 지정입니다.  
별도로 지정하지 않으면 case_convention 인자에 정의된 기본 변환 함수가 지정됩니다.
- **case_convention (CaseConvention)**  
미리 생성한 필드명의 케이스 변환 규칙을 지정합니다.
- case_converter와 동시에 지정되면 case_converter가 우선 적용됩니다.
- case_converter와 case_convention 둘 다 지정되지 않으면 ResponseKeyConverter에 등록된 변환 함수가 적용됩니다.

## 2. ResponseKeyConverter 클래스
### 목적:
- 전역 alias 및 케이스 컨벤션 정보를 관리합니다.
- 싱글톤 패턴을 적용하여, 모듈 전체에서 동일한 설정을 공유할 수 있도록 합니다.
### 주요 기능:
- 특정 클래스에 대해 alias 및 케이스 컨벤션을 등록하거나 조회할 수 있습니다.
- 등록된 전역 설정은 ConvertableKeyModel의 동적 키 변환 과정에서 사용됩니다. 

### 주요 메서드
- **clear()**  
내부 alias 맵과 케이스 컨벤션 맵을 초기화하며, 기본 케이스 컨벤션을 SELF(변환 없음)로 설정합니다.
  

- **add_alias(cls, key_name, alias)**  
특정 클래스에 대해 하나의 alias를 등록합니다.  
예제:
```python
ResponseKeyConverter().add_alias(MyModel, “original_field”, “aliasField”)
```
- **add_aliases(cls, aliases)**  
특정 클래스에 대해 여러 alias를 한 번에 등록합니다.  
  

- **_alias_map(cls)**  
지정된 클래스에 등록된 alias 맵을 반환합니다. (등록된 alias가 없으면 빈 딕셔너리를 반환)  
  

- **_default_case_convention(case_convention)**  
전역 기본 케이스 컨벤션을 설정합니다.  
  

- **add_case_convention(cls, case_convention)**  
특정 클래스에 대해 케이스 컨벤션을 등록합니다.  
  

- **get_case_convention(cls)**  
특정 클래스에 대해 등록된 케이스 컨벤션을 반환합니다.
등록된 내용이 없으면 기본 컨벤션을 반환합니다.

---
## 3. 필드 Alias 및 케이스 컨벤션 지정 방법 
### 3.1 생성자 인자 전달
- **ConvertableKeyModel** 클래스 생성 시 다음 인자를 전달할 수 있습니다:
- **alias_map** (dict[str, str]):
  - JSON 데이터의 키를 변환할 때 사용할 alias 매핑 (예: {"original_field": "aliasField"}).
- **case_converter** (Callable[[str], str]):
  - 필드명의 케이스 변환 함수.
- **case_convention** (CaseConvention):
  - 필드명의 케이스 컨벤션을 지정 (예: CaseConvention.CAMEL).
- 주의:
  - case_converter와 case_convention이 동시에 지정되면, case_converter가 우선 적용됩니다.

### 3.2 전역 등록 (ResponseKeyConverter 활용)
- 전역 클래스인 ResponseKeyConverter에 alias 및 케이스 컨벤션을 등록할 수 있습니다.
- ResponseKeyConverter에 등록된 설정은 ConvertableKeyModel의 인스턴스 생성 시 자동으로 적용됩니다.
### 예제:
```python
ResponseKeyConverter().add_alias(MyModel, 'original_field', 'aliasField')
ResponseKeyConverter().add_case_convention(MyModel, CaseConvention.CAMEL)
```

### 3.3 클래스 내부 **`__alias_map_reference__`** 필드 사용 (Deserialize 전용)
- 모델을 deserialize할 때, 클래스 내부에 `__alias_map_reference__` 필드를 생성해 둘 수 있습니다.
- 이 필드가 존재하면 deserialize 시 alias 매핑 정보로 우선 적용됩니다.
---
## 4. Serialize/Deserialize 동작 방식
- **Deserialize (역직렬화):**
  - JSON 데이터의 키가 어떤 케이스로 들어오더라도, alias 매핑 정보를 사용하여 모델의 필드와 올바르게 매핑합니다.
  - 이 과정에서는 생성자 인자, 전역 등록, 또는 `__alias_map_reference__` 필드에 의해 alias 매핑이 적용됩니다.
- **Serialize (직렬화):**
  - 기본적으로 BaseModel의 model_dump() 호출 시에는 alias 매핑이나 케이스 컨벤션 변환이 적용되지 않습니다.
  - 반드시 convert_key() 함수를 호출하여 alias 매핑과 케이스 컨벤션 변환을 적용한 결과를 얻어야 합니다.
  - 또한, convert_key() 함수 호출 시 인자로 case_converter 또는 **case_convention**을 지정할 수 있으며, 이 경우 해당 설정이 하위 객체까지 재귀적으로 적용됩니다.
---
## 5. 사용 예제
```python
def print_pretty_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


class SampleClass(ConvertableKeyModel):
    some_value_1: str
    someValue2: int

class SampleHaveConvertableKeyModel(ConvertableKeyModel):
    field_one: str
    ckm_field: SampleClass


class SampleClass2(ConvertableKeyModel):
    valueOne: str  # camelCase 필드
    ValueTwo: int  # PascalCase 필드
    value_three: bool  # snake_case 필드


def test_nested_convertable_mapping():
    class SampleAliasClass(ConvertableKeyModel):
        some_field_1: str
        someValue2: int

    class SampleClassWithReverseAliasMap(SampleClass):
        __alias_map_reference__ = {"some_value_1": "some_field_1"}

    class SampleHaveAliasConvertableKeyModel(ConvertableKeyModel):
        field_one: str
        ckm_field: SampleAliasClass

    class SampleHaveReverseAlistMapKeyModel(ConvertableKeyModel):
        field_one: str
        ckm_field: SampleClassWithReverseAliasMap

    def __lambda():
        payload = SampleHaveConvertableKeyModel(
            field_one='sample_field_1',
            ckm_field=SampleClassWithReverseAliasMap(
                some_value_1='sample',
                someValue2=0,
                alias_map={"some_value_1": "some_field_1"},
                case_convention=CaseConvention.CAMEL
            )
        )
        return payload, None, None

    json = StandardResponse.build(callback=__lambda).convert_key()
    print_pretty_json(json)

    # nested model에서 내부 필드 객체 생성자에 alias_map을 지정한 경우 바깥 쪽 객체 매핑이 불가능하다
    # 이런 경우 매핑된 필드로 구성된 클래스를 정의하고 해당 클래스를 내부 필드 객체를 가지는 별도의 클래스를 정의하여 매핑시켜야 한다.
    mapper = StdResponseMapper(json, SampleHaveAliasConvertableKeyModel)
    assert isinstance(mapper.response.payload, SampleHaveAliasConvertableKeyModel)
    assert mapper.response.payload.ckm_field.some_field_1 == 'sample'

    # 또는 원 클래스에 __alias_map_reference__를 정의해 줄 수 있다.
    json = StandardResponse.build(callback=lambda: (
        SampleHaveReverseAlistMapKeyModel(
            field_one='sample_field_1',
            ckm_field=SampleClassWithReverseAliasMap(
                some_value_1='sample',
                someValue2=0,
                alias_map={"some_value_1": "some_field_1"},
                case_convention=CaseConvention.CAMEL
            )
        ), None, None
    )).convert_key()
    mapper = StdResponseMapper(json, SampleHaveReverseAlistMapKeyModel)

    assert isinstance(mapper.response.payload, SampleHaveReverseAlistMapKeyModel)
    assert mapper.response.payload.ckm_field.some_value_1 == 'sample'


def test_convert_key_map():
    def __lambda():
        payload = SampleHaveConvertableKeyModel(
            field_one='sample_field_1',
            ckm_field=SampleClass(
                some_value_1='sample_value_1',
                someValue2=0
            )
        )
        return payload, None, None

    # SampleClass의 some_value_1 필드를 some_value_1_alias로 매핑
    # ResponseKeyConverter를 사용하면 지정된 클래스가 모델의 어떤 레벨에 있든 매핑된 필드명으로 serialize/deserialize가 가능하다.
    ResponseKeyConverter().add_alias(SampleClass, "some_value_1", "some_value_1_alias")

    response_object = StandardResponse.build(callback=__lambda)
    json = response_object.convert_key()
    print_pretty_json(json)

    mapper = StdResponseMapper(json, SampleHaveConvertableKeyModel)

    assert isinstance(mapper.response.payload, SampleHaveConvertableKeyModel)
    assert mapper.response.payload.ckm_field.some_value_1 == 'sample_value_1'


def test_case_convention_mapping():
    alias_map = {
        "valueOne": "value_one_alias",
        "ValueTwo": "value_two_alias",
    }

    original_data = {
        "value_one": "값1",  # alias_map을 통해 매핑되어야 함
        "valueTwo": 999,  # alias_map과 case 변환 적용
        "ValueThree": True,  # snake_case로 변환하여 매핑
    }

    converted_data = {
        "value_one_alias": "값2",  # alias_map을 통해 매핑되어야 함
        "valueTwoAlias": 999,  # alias_map과 case 변환 적용
        "ValueThree": True,  # snake_case로 변환하여 매핑
    }

    sample = SampleClass2(case_convention=CaseConvention.CAMEL, **original_data)
    print()
    print(f'sample object: {sample}')

    assert sample.valueOne == '값1'  # 객체는 camelCase이고 json 데이터는 snake_case이어도 매핑이 잘 되어야 함
    assert sample.ValueTwo == 999  # 객체는 PascalCase이고 json 데이터는 camelCase이어도 매핑이 잘 되어야 함
    assert sample.value_three  # 객체는 snake_case이고 json 데이터는 PascalCase이어도 매핑이 잘 되어야 함

    dump_data = sample.convert_key()
    print_pretty_json(dump_data)
    assert dump_data['valueTwo'] == 999  # convert_key()에 아무런 인자가 없으면 객체의 case_convention에 따라 변환
    assert dump_data['valueThree']  # convert_key()에 아무런 인자가 없으면 객체의 case_convention에 따라 변환

    dump_data = sample.convert_key(case_convention=CaseConvention.CAMEL)
    print_pretty_json(dump_data)
    assert dump_data['valueTwo'] == 999  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['valueThree']  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환

    dump_data = sample.convert_key(case_convention=CaseConvention.SNAKE)
    print_pretty_json(dump_data)
    assert dump_data['value_one'] == '값1'  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['value_two'] == 999  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환

    dump_data = sample.convert_key(case_convention=CaseConvention.PASCAL)
    print_pretty_json(dump_data)
    assert dump_data['ValueOne'] == '값1'  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['ValueThree']  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환

    # alias_map을 적용하여 매핑될 필드명이 변경되어도 지정된 case convention으로 serialize/deserialize가 가능해야 한다.
    sample2 = SampleClass2(alias_map=alias_map, case_convention=CaseConvention.CAMEL, **converted_data)
    print(f'sample2: {sample2}')
    assert sample2.valueOne == '값2'  # 객체는 camelCase이고 json 데이터는 snake_case이어도 매핑이 잘 되어야 함
    assert sample2.ValueTwo == 999  # 객체는 PascalCase이고 json 데이터는 camelCase이어도 매핑이 잘 되어야 함
    assert sample2.value_three  # 객체는 snake_case이고 json 데이터는 PascalCase이어도 매핑이 잘 되어야 함

    dump_data = sample2.convert_key()
    print('sample2 dump_data with class parameter: ')
    print_pretty_json(dump_data)
    assert dump_data['valueOneAlias'] == '값2'  # convert_key()에 아무런 인자가 없으면 객체의 case_convention에 따라 변환
    assert dump_data['valueTwoAlias'] == 999  # convert_key()에 아무런 인자가 없으면 객체의 case_convention에 따라 변환
    assert dump_data['valueThree']  # convert_key()에 아무런 인자가 없으면 객체의 case_convention에 따라 변환, alias_map에 없는 키는 원 필드명이 변환되어야 함

    dump_data = sample2.convert_key(case_convention=CaseConvention.CAMEL)
    print('sample2 dump_data with convert_key function parameter: ')
    print_pretty_json(dump_data)
    assert dump_data['valueOneAlias'] == '값2'  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['valueTwoAlias'] == 999  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['valueThree']  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환

    dump_data = sample2.convert_key(case_convention=CaseConvention.SNAKE)
    print_pretty_json(dump_data)
    assert dump_data['value_one_alias'] == '값2'  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['value_two_alias'] == 999  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['value_three']  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환

    dump_data = sample2.convert_key(case_convention=CaseConvention.PASCAL)
    print_pretty_json(dump_data)
    assert dump_data['ValueOneAlias'] == '값2'  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['ValueTwoAlias'] == 999  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환
    assert dump_data['ValueThree']  # convert_key()에 case_convention 인자가 있으면 해당 case로 변환


def test_with_StandardResponse_and_StdResponseMapper():
    def __lambda():
        payload = SampleClass(
            some_value_1='sample',
            someValue2=0,
            case_convention=CaseConvention.CAMEL
        )
        return payload, None, None

    json = StandardResponse.build(callback=__lambda).convert_key()
    print_pretty_json(json)

    mapper = StdResponseMapper(json, SampleClass)

    assert isinstance(mapper.response.payload, SampleClass)
    assert mapper.response.payload.some_value_1 == 'sample'
```
