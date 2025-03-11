from pydantic import BaseModel

from convertable_key_model.convertable_key_model import ConvertableKeyModel, CaseConvention
from standard_api_response.standard_response import PageableList, IncrementalList, OrderInfo, \
    OrderBy, OrderDirection, CursorInfo, Items


class SamplePayload(ConvertableKeyModel):
    value_1: str
    value_2: int


class SampleItem(BaseModel):
    key: str
    value: int


class SamplePageListPayload(ConvertableKeyModel):
    value_1: str
    value_2: int
    pageable: PageableList[SampleItem]


class SampleIncrementalListPayload(ConvertableKeyModel):
    value_1: str
    value_2: int
    incremental: IncrementalList[SampleItem]


class SampleService:
    def __init__(self):
        self.item_list = []
        for i in range(100):
            self.item_list.append(SampleItem(key=f'key_{i}', value=i))

    def get_item(self):
        # return SamplePayload(value_1='sample', value_2=0, case_convention=CaseConvention.SNAKE)
        return SamplePayload(value_1='sample', value_2=0, case_convention=CaseConvention.CAMEL)

    def get_pageable_list(self, page: int, page_size: int):
        # page == 0 이면 모든 데이터 반환
        if page <= 0:
            page = 1
            page_size = len(self.item_list)

        page_list = PageableList[SampleItem].build(
            items=self.item_list[(page - 1) * page_size : page * page_size],
            total_items=len(self.item_list),
            page_size=page_size,
            current_page=page,
            order_info=OrderInfo(sorted=True, by=[OrderBy(field='key', direction=OrderDirection.ASC)]),
        )

        payload = SamplePageListPayload(
            value_1='page_list_sample',
            value_2=0,
            pageable=page_list.convert_key(),  # Pydantic에서 custom model에 대한 직렬화를 수행할 때 dict를 사용하므로 dict로 변환
        )
        return payload

    def get_pageable_only(self, page: int, page_size: int):
        # page == 0 이면 모든 데이터 반환
        if page <= 0:
            page = 1
            page_size = len(self.item_list)

        page_list = PageableList[SampleItem].build(
            items=self.item_list[(page - 1) * page_size : page * page_size],
            total_items=len(self.item_list),
            page_size=page_size,
            current_page=page,
            order_info=OrderInfo(sorted=True, by=[OrderBy(field='key', direction=OrderDirection.ASC)]),
        )

        return page_list

    def get_incremental_list(self, start_index: int, how_many: int):
        item_count = len(self.item_list)

        if start_index >= item_count:
            return SampleIncrementalListPayload(
                value_1='no more item',
                value_2=0,
                incremental=IncrementalList[SampleItem](
                    cursor=CursorInfo(field='sequence', start=start_index, end=None, expandable=False),
                    order=OrderInfo(sorted=True, by=[OrderBy(field='key', direction=OrderDirection.ASC)]).model_dump(),
                    items=Items[SampleItem](total=item_count, current=0, list=[]).model_dump()
                ).model_dump()
            )

        real_fetch_size = min(how_many, item_count - start_index)

        order = OrderInfo(
            sorted=True,
            by=[
                OrderBy(field='key', direction=OrderDirection.ASC),
                OrderBy(field='value', direction=OrderDirection.ASC)
            ]
        )

        items = Items.build(item_count, self.item_list[start_index: start_index + real_fetch_size])

        cursor = CursorInfo.build_from_total(
            start_index=start_index,
            how_many=how_many,
            total_items=item_count,
            field='sequence'
        )

        incremental = IncrementalList[SampleItem](
            cursor=cursor,
            order=order.model_dump(),
            items=items.model_dump()
        )

        return SampleIncrementalListPayload(
            value_1='expandable_list_sample',
            value_2=0,
            incremental=incremental.model_dump()
        )

    def get_incremental_list_by_key(self, start_key, how_many: int):
        def find_node_index(item_list, key):
            for index, item in enumerate(item_list):
                if (item.key == key):
                    return index
            return -1

        item_count = len(self.item_list)
        start_index = find_node_index(self.item_list, start_key)
        if start_index == -1:
            return SampleIncrementalListPayload(
                value_1='no more item',
                value_2=0,
                incremental=IncrementalList[SampleItem](
                    cursor=CursorInfo(field='key', start=start_key, end=None, expandable=False),
                    order=OrderInfo(sorted=True, by=[OrderBy(field='key', direction=OrderDirection.ASC)]),
                    items=Items(total=item_count, current=0, list=[]).model_dump()
                ).model_dump()
            )

        real_fetch_size = min(how_many, item_count - start_index)

        return SampleIncrementalListPayload(
            value_1='expandable_list_sample',
            value_2=0,
            incremental=IncrementalList.build(
                items=self.item_list[start_index: start_index + real_fetch_size],
                start_index=start_index,
                how_many=how_many,
                total_items=item_count,
                cursor_field='key',
                order_info=OrderInfo(sorted=True, by=[OrderBy(field='key', direction=OrderDirection.ASC)]),
                convert_index=lambda field_name, index: self.item_list[index].key
            ).model_dump()
        )
