import json
import re
from typing import Optional

from openai import OpenAI

from config import config


SYSTEM_PROMPT = """你是一位资深的旅行规划师，擅长根据游客的用户画像和情绪状态，推荐个性化旅游路线。

你的任务：
1. 根据用户画像（年龄、性别、人数）和情绪状态，推荐 3 条旅游路线
2. 每条路线包含：路线标题、目的地、3日行程、适合理由、预算范围

输出格式要求（严格 JSON）：
{
  "routes": [
    {
      "title": "路线标题（有吸引力的，如\"海边治愈之旅 🌊\"）",
      "destination": "目的地城市/地区",
      "duration": "3天2晚",
      "budget": "人均预算范围",
      "reason": "结合用户画像的推荐理由",
      "itinerary": [
        {"day": 1, "label": "Day 1", "spots": ["景点1", "景点2", "景点3"], "food": ["美食推荐"]},
        {"day": 2, "label": "Day 2", "spots": ["景点1", "景点2", "景点3"], "food": ["美食推荐"]},
        {"day": 3, "label": "Day 3", "spots": ["景点1", "景点2"], "food": ["美食推荐"]}
      ],
      "tags": ["标签1", "标签2", "标签3"]
    }
  ]
}"""


class TravelAgent:
    def __init__(self):
        self._client: Optional[OpenAI] = None

    @property
    def available(self) -> bool:
        return bool(config.LLM_API_KEY and config.LLM_API_KEY != "your_api_key_here")

    def generate(self, vision_result: dict) -> dict:
        user_prompt = self._build_user_prompt(vision_result)

        if not self.available:
            return self._mock_response(vision_result)

        return self._call_llm(user_prompt)

    def _build_user_prompt(self, vision_result: dict) -> str:
        tags = vision_result.get("tags", {})
        summary = vision_result.get("summary", "")

        age_groups = ", ".join(tags.get("age_groups", ["未知"]))
        emotions = ", ".join(tags.get("emotions", ["未知"]))
        genders = ", ".join(tags.get("genders", ["未知"]))

        return f"""请根据以下用户画像，生成个性化旅游推荐：

【基本信息】
- 同行人数：{vision_result.get('face_count', 1)} 人
- 人群类型：{vision_result.get('crowd_type', '单人')}
- 年龄段：{age_groups}
- 性别：{genders}
- 当前情绪：{emotions}
- 分析摘要：{summary}

请输出 JSON 格式的推荐结果。"""

    def _call_llm(self, user_prompt: str) -> dict:
        if self._client is None:
            self._client = OpenAI(
                api_key=config.LLM_API_KEY,
                base_url=config.LLM_BASE_URL,
            )

        response = self._client.chat.completions.create(
            model=config.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=4096,
        )

        raw = response.choices[0].message.content or "{}"
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> dict:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"routes": [], "raw": raw}

    def _mock_response(self, vision_result: dict) -> dict:
        tags = vision_result.get("tags", {})
        emotions = tags.get("emotions", ["开心"])
        dominant_emotion = max(set(emotions), key=emotions.count) if emotions else "开心"
        crowd = vision_result.get("crowd_type", "单人")

        routes = []

        if dominant_emotion in ("悲伤", "愤怒", "恐惧", "厌恶"):
            routes.append({
                "title": "海边治愈之旅 🌊",
                "destination": "三亚 / 厦门",
                "duration": "3天2晚",
                "budget": "¥1500-2500/人",
                "reason": "情绪需要放松，海边漫步与日出能有效舒缓心情",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 抵达海边", "spots": ["沙滩漫步", "海边咖啡厅", "日落观景台"], "food": ["海鲜大排档", "椰子鸡"]},
                    {"day": 2, "label": "Day 2 · 深度放松", "spots": ["海岛游船", "SPA水疗", "海边书店"], "food": ["海景餐厅", "热带水果"]},
                    {"day": 3, "label": "Day 3 · 慢生活", "spots": ["椰林骑行", "赶海体验"], "food": ["当地早茶", "海鲜火锅"]},
                ],
                "tags": ["治愈", "海景", "慢节奏"],
            })
            routes.append({
                "title": "山林静修之旅 🏔️",
                "destination": "莫干山 / 安吉",
                "duration": "3天2晚",
                "budget": "¥1200-2000/人",
                "reason": "山林静谧，适合沉淀思绪，回归内心平静",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 入山", "spots": ["竹林徒步", "山间民宿", "星空露台"], "food": ["农家土菜", "竹筒饭"]},
                    {"day": 2, "label": "Day 2 · 禅意", "spots": ["茶园采茶", "山泉泡汤", "冥想课程"], "food": ["山野素食", "茶点"]},
                    {"day": 3, "label": "Day 3 · 归途", "spots": ["日出观景", "手作体验"], "food": ["本地早餐", "山货伴手礼"]},
                ],
                "tags": ["静谧", "自然", "禅修"],
            })
            routes.append({
                "title": "艺术疗愈之旅 🎨",
                "destination": "大理 / 景德镇",
                "duration": "3天2晚",
                "budget": "¥1000-1800/人",
                "reason": "艺术创作是情绪表达的最佳出口",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 遇见艺术", "spots": ["艺术街区", "陶艺工坊", "独立书店"], "food": ["文艺咖啡馆", "创意料理"]},
                    {"day": 2, "label": "Day 2 · 沉浸创作", "spots": ["陶艺手作", "扎染体验", "画廊参观"], "food": ["本地私房菜", "下午茶"]},
                    {"day": 3, "label": "Day 3 · 灵感收集", "spots": ["古镇漫步", "跳蚤市场"], "food": ["市集小吃", "手冲咖啡"]},
                ],
                "tags": ["艺术", "手作", "文艺"],
            })
        elif dominant_emotion == "开心":
            routes.append({
                "title": "活力城市探索 🏙️",
                "destination": "成都 / 长沙",
                "duration": "3天2晚",
                "budget": "¥1000-2000/人",
                "reason": "好心情配美食之都，尽情享受城市烟火气",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 城市漫游", "spots": ["地标打卡", "潮流街区", "夜市"], "food": ["火锅/小龙虾", "网红小吃"]},
                    {"day": 2, "label": "Day 2 · 文化探秘", "spots": ["博物馆", "老街巷", "LiveHouse"], "food": ["地道早餐", "串串/烧烤"]},
                    {"day": 3, "label": "Day 3 · 深度体验", "spots": ["创意园区", "本地市场"], "food": ["早茶/米粉", "伴手礼店"]},
                ],
                "tags": ["美食", "潮流", "夜生活"],
            })
            routes.append({
                "title": "乐园狂欢之旅 🎢",
                "destination": "上海 / 广州",
                "duration": "3天2晚",
                "budget": "¥1800-3000/人",
                "reason": "把快乐延续下去，主题乐园是最佳选择",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 魔法世界", "spots": ["迪士尼/长隆主题乐园全天"], "food": ["乐园主题餐厅", "烟花晚餐"]},
                    {"day": 2, "label": "Day 2 · 城市风光", "spots": ["外滩/广州塔", "观景餐厅", "滨江骑行"], "food": ["米其林/黑珍珠", "本地老字号"]},
                    {"day": 3, "label": "Day 3 · 文艺街区", "spots": ["田子坊/永庆坊", "独立书店"], "food": ["Brunch", "甜品工坊"]},
                ],
                "tags": ["乐园", "打卡", "高能量"],
            })
            routes.append({
                "title": "户外探险之旅 🏕️",
                "destination": "丽江 / 张家界",
                "duration": "3天2晚",
                "budget": "¥1500-2500/人",
                "reason": "好状态适合挑战自我，拥抱自然",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 抵达秘境", "spots": ["古城/小镇探索", "观景台日落"], "food": ["纳西/土家菜", "腊排骨"]},
                    {"day": 2, "label": "Day 2 · 山野挑战", "spots": ["徒步/攀岩", "峡谷漂流", "星空营地"], "food": ["户外野餐", "篝火晚餐"]},
                    {"day": 3, "label": "Day 3 · 云海日出", "spots": ["索道登顶", "云海日出"], "food": ["山顶咖啡", "当地特产"]},
                ],
                "tags": ["探险", "自然", "摄影"],
            })
        else:
            routes.append({
                "title": "古城慢时光之旅 🏮",
                "destination": "苏州 / 杭州",
                "duration": "3天2晚",
                "budget": "¥1000-1800/人",
                "reason": "平和的情绪适合沉浸于江南水乡的宁静",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 初见江南", "spots": ["古典园林", "水巷游船", "夜市灯会"], "food": ["苏帮菜/杭帮菜", "桂花糕"]},
                    {"day": 2, "label": "Day 2 · 湖畔时光", "spots": ["西湖/金鸡湖", "龙井茶园", "丝绸博物馆"], "food": ["楼外楼/得月楼", "龙井虾仁"]},
                    {"day": 3, "label": "Day 3 · 诗意生活", "spots": ["古寺晨钟", "手工艺馆"], "food": ["素斋", "定胜糕"]},
                ],
                "tags": ["人文", "慢生活", "古典"],
            })
            routes.append({
                "title": "温泉疗愈之旅 ♨️",
                "destination": "腾冲 / 南京汤山",
                "duration": "3天2晚",
                "budget": "¥1200-2000/人",
                "reason": "温泉是放松身心的最佳方式",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 温泉初体验", "spots": ["温泉度假村", "SPA中心", "夜景庭院"], "food": ["温泉蛋", "养生药膳"]},
                    {"day": 2, "label": "Day 2 · 周边探索", "spots": ["火山地质公园/明孝陵", "银杏村/栖霞山"], "food": ["土锅子/盐水鸭", "热海大滚锅"]},
                    {"day": 3, "label": "Day 3 · 告别温泉", "spots": ["古镇漫步", "本地集市"], "food": ["稀豆粉/鸭血粉丝", "伴手礼"]},
                ],
                "tags": ["温泉", "养生", "休闲"],
            })
            routes.append({
                "title": "文化朝圣之旅 📿",
                "destination": "西安 / 洛阳",
                "duration": "3天2晚",
                "budget": "¥1000-1800/人",
                "reason": "在历史长河中寻找内心的平静",
                "itinerary": [
                    {"day": 1, "label": "Day 1 · 千年回望", "spots": ["兵马俑/龙门石窟", "古城墙骑行"], "food": ["biangbiang面/水席", "肉夹馍"]},
                    {"day": 2, "label": "Day 2 · 盛唐风华", "spots": ["大雁塔/白马寺", "大唐不夜城"], "food": ["葫芦鸡/牡丹燕菜", "凉皮"]},
                    {"day": 3, "label": "Day 3 · 丝路余韵", "spots": ["陕西/洛阳博物馆", "回民街/老城"], "food": ["羊肉泡馍", "黄桂柿子饼"]},
                ],
                "tags": ["历史", "文化", "深度"],
            })

        return {"routes": routes}
