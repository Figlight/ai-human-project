from fastapi import APIRouter
from backend.app.models.schemas import ApiResponse, RouteRecommendRequest

router = APIRouter()

ATTRACTIONS = [
    {"name": "古塔", "icon": "🗼", "description": "唐代七层八角古塔，景区标志性建筑", "color": "linear-gradient(135deg, #667eea, #764ba2)", "tags": ["历史文化", "拍照打卡"]},
    {"name": "古寺遗址", "icon": "⛩️", "description": "唐代寺院遗址，感受千年历史沧桑", "color": "linear-gradient(135deg, #f093fb, #f5576c)", "tags": ["历史文化"]},
    {"name": "碑林", "icon": "📜", "description": "200余块珍贵石碑，唐宋至明清", "color": "linear-gradient(135deg, #4facfe, #00f2fe)", "tags": ["历史文化", "休闲散步"]},
    {"name": "瀑布", "icon": "🌊", "description": "30米落差瀑布，雨季尤为壮观", "color": "linear-gradient(135deg, #43e97b, #38f9d7)", "tags": ["自然风光", "拍照打卡"]},
    {"name": "花海", "icon": "🌸", "description": "四季花海，春季樱花秋季菊花", "color": "linear-gradient(135deg, #fa709a, #fee140)", "tags": ["自然风光", "亲子游", "拍照打卡"]},
    {"name": "竹林小径", "icon": "🎋", "description": "翠竹掩映的石板小路，清幽雅致", "color": "linear-gradient(135deg, #a8edea, #fed6e3)", "tags": ["自然风光", "休闲散步"]},
    {"name": "美食街", "icon": "🍜", "description": "汇集当地特色小吃和饮品", "color": "linear-gradient(135deg, #ffecd2, #fcb69f)", "tags": ["美食小吃", "亲子游"]},
    {"name": "萌宠乐园", "icon": "🐰", "description": "近距离接触小动物，亲子互动", "color": "linear-gradient(135deg, #a1c4fd, #c2e9fb)", "tags": ["亲子游", "休闲散步"]},
]

ROUTES = [
    {
        "id": 1, "name": "文化探访精华路线", "duration": "半日游", "color": "#4F6CF7",
        "description": "覆盖景区最核心的历史人文景点，适合对历史文化感兴趣的游客。",
        "spots": ["南门入口", "古寺遗址", "碑林", "观景台", "古塔"],
        "distance": "2.5km", "time": "2小时", "tag": "🔥 热门", "tags": ["history", "photo"],
    },
    {
        "id": 2, "name": "自然生态徒步路线", "duration": "一日游", "color": "#10B981",
        "description": "穿越山林溪涧，感受自然之美，适合户外运动爱好者。",
        "spots": ["东门", "竹林小径", "瀑布", "山林栈道", "山顶观景台"],
        "distance": "5km", "time": "3.5小时", "tag": "🌿 自然", "tags": ["nature", "leisure"],
    },
    {
        "id": 3, "name": "亲子趣味路线", "duration": "半日游", "color": "#F59E0B",
        "description": "轻松有趣的路程，适合带小朋友的家庭出游。",
        "spots": ["游客中心", "萌宠乐园", "花海", "游乐场", "美食街"],
        "distance": "1.8km", "time": "2.5小时", "tag": "👨‍👩‍👧 亲子", "tags": ["family", "food"],
    },
]

SPOT_DESCRIPTIONS = {
    "南门入口": "景区正门，汉白玉牌坊上刻有'山水胜境'四个大字。",
    "古寺遗址": "始建于唐代的著名寺院遗址，现仅存地基和部分石柱。",
    "碑林": "收藏了从唐宋到明清的200多块珍贵石碑。",
    "观景台": "位于半山腰，可以俯瞰整个景区的美景。",
    "古塔": "七层八角，始建于唐代，高约45米，景区标志性建筑。",
    "东门": "景区东侧入口，周围古木参天，环境清幽。",
    "竹林小径": "蜿蜒在竹林中的石板小路，两侧翠竹掩映。",
    "瀑布": "落差约30米的瀑布，雨季时水量充沛。",
    "山林栈道": "依山而建的木质栈道，全长约1.2公里。",
    "山顶观景台": "景区最高点，海拔约200米，可360度俯瞰全景。",
    "游客中心": "提供咨询、寄存、母婴室等综合服务。",
    "萌宠乐园": "小朋友可以近距离接触小动物。",
    "花海": "四季都有不同的花卉盛开。",
    "游乐场": "有旋转木马、小火车等适合儿童的游乐设施。",
    "美食街": "汇集了当地各种特色小吃和饮品。",
}

INTEREST_TAGS = [
    {"key": "history", "icon": "🏛️", "label": "历史文化"},
    {"key": "nature", "icon": "🌿", "label": "自然风光"},
    {"key": "food", "icon": "🍜", "label": "美食小吃"},
    {"key": "photo", "icon": "📸", "label": "拍照打卡"},
    {"key": "family", "icon": "👨‍👩‍👧", "label": "亲子游"},
    {"key": "leisure", "icon": "🚶", "label": "休闲散步"},
]

TAG_TO_ROUTE = {
    "history": [1],
    "nature": [2],
    "food": [3],
    "photo": [1, 2],
    "family": [3],
    "leisure": [2],
}


@router.get("", response_model=ApiResponse)
async def list_attractions():
    return ApiResponse(data=ATTRACTIONS)


@router.get("/tags", response_model=ApiResponse)
async def list_tags():
    return ApiResponse(data=INTEREST_TAGS)


@router.get("/routes", response_model=ApiResponse)
async def list_routes():
    return ApiResponse(data=ROUTES)


@router.post("/routes/recommend", response_model=ApiResponse)
async def recommend_routes(req: RouteRecommendRequest):
    if not req.tags:
        return ApiResponse(data=ROUTES)

    route_ids = set()
    for tag in req.tags:
        for rid in TAG_TO_ROUTE.get(tag, []):
            route_ids.add(rid)

    filtered = [r for r in ROUTES if r["id"] in route_ids]
    return ApiResponse(data=filtered)


@router.get("/spot-description/{spot_name}", response_model=ApiResponse)
async def get_spot_description(spot_name: str):
    desc = SPOT_DESCRIPTIONS.get(spot_name, "暂无该景点的详细介绍。")
    return ApiResponse(data={"name": spot_name, "description": desc})
