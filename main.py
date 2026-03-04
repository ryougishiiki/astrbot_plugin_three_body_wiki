
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Node,Plain 
from astrbot.api import AstrBotConfig
import aiohttp

@register("灰机wiki查询", "J-SLY", "灰机wiki查询", "1.1.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.www = self.config.get("www","main")
        self.token = self.config.get("token","")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    @filter.command("find",alias={'search'})
    async def find(self,event:AstrMessageEvent,thing:str):
        if self.www!="main":
            url = f"https://{self.www}.huijiwiki.com/api.php?action=opensearch&format=json&search={thing}"
        else:
            url = f"https://huijiwiki.com/api.php?action=opensearch&format=json&search={thing}"
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-authkey':f"{self.token}" 
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=header) as response:
                try:
                    data = await response.json()
                except Exception as error:
                    yield event.plain_result(f"{error}")
                    return

            if not data[1] and not data[2] and not data[3]:
                yield event.plain_result("搜索目标不存在")
            else:
                if len(data[1])==1 :
                    yield event.plain_result(f"搜索到一个结果\n\n{data[1][0]}:{data[2][0]}\n\n链接：{data[3][0]}")
                else:
                    if data[1][0][-5:] == "(消歧义)":
                        return_result:str=f"该结果存在消歧义界面：{data[3][0]}\n\n"
                        for i in range(len(data[2])-1):
                            return_result+=f"{data[1][i+1]}:{data[2][i+1]}\n链接：{data[3][i]}\n\n"
                    else:
                        page_num=len(data[1])
                        return_result:str=f"查找到{page_num}个页面"
                        for i in range(len(data[2])):
                            return_result+=f"{data[1][i]}:{data[2][i]}\n链接：{data[3][i]}\n"
                    find_result=Node(
                            name="搜索结果",
                            content=[
                                Plain(return_result)
                            ]
                        )
                    yield event.chain_result([find_result])    
                   
    @filter.command("wiki-help",alias={'获取帮助'})
    async def help(self,event:AstrMessageEvent):
        from astrbot.api.message_components import Node,Plain
        help_text=Node(
            name="帮助文档",
            content=[
                Plain("灰机wiki查询插件帮助列表 \n/wiki-help /获取帮助 ：获取帮助 \n/find /search find_thing<str> ：在灰机wiki中查询 find_thing 内容 <str>类型")
            ]
        )
        yield event.chain_result([help_text])
        
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
