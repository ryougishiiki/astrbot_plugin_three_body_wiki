from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import aiohttp
import asyncio
import time
import json

@register("三体wiki查询", "J-SLY", "三体wiki查询", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    @filter.command_group("santi",alias={'三体'})
    def santi(self):
        pass
    @santi.command("help",alias={'帮助'})
    async def help(self,event:AstrMessageEvent):
        user_name=event.get_sender_name()
        from astrbot.api.message_components import Node,Plain
        help_text=Node(
            uin=3840638231,
            name="帮助文档",
            content=[
                Plain("灰机三体wiki查询插件帮助列表 \n/santi help /三体 帮助 ：获取帮助 \n/santi find find_thing<str> /三体 查询 find_thing<str> ：在灰机三体wiki中查询 find_thing 内容 <str>类型")
            ]
        )
        yield event.chain_result([help_text])

    @santi.command("find",alias={'查找'})
    async def find(self,event:AstrMessageEvent,find_thing:str):
        url="https://santi.huijiwiki.com/api.php?action=opensearch&format=json&search={str}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data=await response.json()
        find_result=json.loads(data)
        from astrbot.api.message_components import Node,Plain
        find_text=Node(
            uin=3840638231,
            name="搜索结果",
            content=[
                Plain(find_result[3])
            ]
        )
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
