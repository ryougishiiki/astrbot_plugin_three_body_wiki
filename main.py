from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api.message_components import Node, Plain
from astrbot.api import AstrBotConfig

from playwright.async_api import async_playwright
import json


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

        self.browser = None
        self.page = None
        self.playwright = None


    async def initialize(self):
        """启动浏览器（插件加载时只启动一次）"""

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=True
        )

        context = await self.browser.new_context()

        self.page = await context.new_page()

        # 访问首页一次，通过 Cloudflare challenge
        await self.page.goto(self.base_url)


    async def _fetch_json(self, url):

        await self.page.goto(url)

        content = await self.page.content()

        # MediaWiki API 返回 JSON 在 <pre> 标签
        if "<pre>" in content:

            start = content.find("<pre>") + 5
            end = content.find("</pre>")

            json_text = content[start:end]

        else:
            # fallback
            json_text = await self.page.text_content("body")

        return json.loads(json_text)


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
        """关闭浏览器"""

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()