from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api.message_components import Node, Plain
from astrbot.api import AstrBotConfig

from playwright.async_api import async_playwright
import json
import asyncio


class MyPlugin(Star):

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        self.config = config
        self.www = self.config.get("www", "")
        self.token = self.config.get("token", "")  # 保留兼容

        if not self.www or self.www == "main":
            self.base_url = "https://huijiwiki.com"
        else:
            self.base_url = f"https://{self.www}.huijiwiki.com"

        self.playwright = None
        self.browser = None
        self.context = None


    async def initialize(self):
        """插件加载时启动浏览器"""

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=True
        )

        self.context = await self.browser.new_context()

        # 访问一次首页获取 Cloudflare cookie
        try:
            page = await self.context.new_page()
            await page.goto(self.base_url, timeout=20000)
            await page.close()
        except:
            pass


    async def _fetch_json(self, url):

        page = await self.context.new_page()

        try:

            await page.goto(url, timeout=20000)

            text = await page.text_content("body")

            if text is None:
                raise Exception("页面返回为空")

            text = text.strip()

            if text.startswith("<pre"):
                start = text.find(">") + 1
                end = text.rfind("</pre>")
                text = text[start:end]

            return json.loads(text)

        finally:
            await page.close()


    @filter.command("find", alias={"search"})
    async def find(self, event: AstrMessageEvent, thing: str):

        url = f"{self.base_url}/api.php?action=opensearch&format=json&search={thing}"

        try:
            data = await self._fetch_json(url)
        except Exception as e:
            yield event.plain_result(f"Wiki请求失败\n{str(e)}")
            return


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

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()