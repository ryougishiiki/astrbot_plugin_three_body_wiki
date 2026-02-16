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
        url=f"https://santi.huijiwiki.com/api.php?action=opensearch&format=json&search={find_thing}"
        header={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-authkey':"6LOCrMadnLTXyP" 
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=header) as response:
                data=await response.json()
        if data[1]==[] and data[2]==[] and data[3]==[]:
            yield event.plain_result("搜索目标不存在")
        else:
            if len(data[1])==1 :
                yield event.plain_result(f"搜索到一个结果\n\n{data[1][0]}:{data[2][0]}\n\n链接：{data[3][0]}")
            else:
                if data[1][0][-5:] == "(消歧义)":
                    return_result:str=f"该结果存在消歧义界面：{data[3][0]}\n\n"
                    for i in range(len(data[2])-1):
                        return_result+=f"{data[1][i+1]}:{data[2][i+1]}\n链接：{data[3][i]}\n\n"
                    from astrbot.api.message_components import Node,Plain   
                    find_result=Node(
                        uin=3840638231,
                        name="搜索结果",
                        content=[
                            Plain(return_result)
                        ]
                    )
                    yield event.chain_result([find_result])
                else:
                    page_num=len(data[1])
                    return_result:str=f"查找到{page_num}个页面"
                    for i in range(len(data[2])):
                        return_result+=f"{data[1][i]}:{data[2][i]}\n链接：{data[3][i]}\n"
                    from astrbot.api.message_components import Node,Plain   
                    find_result=Node(
                        uin=3840638231,
                        name="搜索结果",
                        content=[
                            Plain(return_result)
                        ]
                    )
                    yield event.chain_result([find_result])
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
