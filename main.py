from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("santi-help",alias={'三体-帮助'})
    async def help(self,event:AstrMessageEvent):
        user_name=event.get_sender_name()
        from astrbot.api.message_components import Node,Plain
        help_text=Node(
            uin=3840638231,
            name="帮助文档",
            content=[
                Plain("灰机三体wiki查询插件帮助列表 \n/santi-help /三体-帮助 ：获取帮助 \n/santi find_thing<str> /三体-查询 find_thing<str> ：在灰机三体wiki中查询 find_thing 内容 <str>类型")
            ]
        )
        yield event.chain_result([help_text])
    #async def find(self,event:AstrMessageEvent,find_thing:str):
        
    #asyncdef helloworld(self, event: AstrMessageEvent):
    #这是一个 hello world 指令 # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
    #user_name = event.get_sender_name()
    #message_str = event.message_str # 用户发的纯文本消息字符串
    #message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
    #logger.info(message_chain)
    #yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息
    
        async def terminate(self):
            """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
