from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api.message_components import Node, Plain
from astrbot.api import AstrBotConfig
import aiohttp


class MyPlugin(Star):

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        self.config = config
        self.www = self.config.get("www", "main")
        self.token = self.config.get("token", "")  # 保留但不使用

        if self.www != "main":
            self.base_url = f"https://{self.www}.huijiwiki.com"
        else:
            self.base_url = "https://huijiwiki.com"

    async def initialize(self):
        pass


    async def _create_session(self):
        """
        创建带浏览器特征的 session
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Referer": f"{self.base_url}/",
            "Origin": self.base_url
        }

        session = aiohttp.ClientSession(headers=headers)

        # 访问首页拿 cookie（huiji 的 cf / waf 会检查）
        try:
            async with session.get(self.base_url):
                pass
        except:
            pass

        return session


    @filter.command("find", alias={"search"})
    async def find(self, event: AstrMessageEvent, thing: str):

        url = f"{self.base_url}/api.php?action=opensearch&format=json&search={thing}"

        session = await self._create_session()

        try:

            async with session.get(url) as response:

                if response.status != 200:
                    text = await response.text()
                    yield event.plain_result(
                        f"Wiki请求失败\nHTTP:{response.status}\n{text[:200]}"
                    )
                    return

                try:
                    data = await response.json()
                except Exception:
                    text = await response.text()
                    yield event.plain_result(
                        f"返回内容不是JSON\n{text[:300]}"
                    )
                    return

        finally:
            await session.close()

        if not data[1] and not data[2] and not data[3]:
            yield event.plain_result("搜索目标不存在")
            return

        if len(data[1]) == 1:

            result = (
                f"搜索到一个结果\n\n"
                f"{data[1][0]}:{data[2][0]}\n\n"
                f"链接：{data[3][0]}"
            )

            yield event.plain_result(result)
            return

        if data[1][0].endswith("(消歧义)"):

            return_result = f"该结果存在消歧义界面：{data[3][0]}\n\n"

            for i in range(len(data[2]) - 1):
                return_result += (
                    f"{data[1][i+1]}:{data[2][i+1]}\n"
                    f"链接：{data[3][i+1]}\n\n"
                )

        else:

            page_num = len(data[1])
            return_result = f"查找到{page_num}个页面\n\n"

            for i in range(len(data[2])):
                return_result += (
                    f"{data[1][i]}:{data[2][i]}\n"
                    f"链接：{data[3][i]}\n\n"
                )

        find_result = Node(
            name="搜索结果",
            content=[Plain(return_result)]
        )

        yield event.chain_result([find_result])


    @filter.command("wiki-help", alias={"获取帮助"})
    async def help(self, event: AstrMessageEvent):

        help_text = Node(
            name="帮助文档",
            content=[
                Plain(
                    "灰机wiki查询插件帮助列表\n"
                    "/wiki-help /获取帮助 ：获取帮助\n"
                    "/find /search find_thing<str> ：在灰机wiki中查询 find_thing 内容"
                )
            ]
        )

        yield event.chain_result([help_text])


    async def terminate(self):
        pass