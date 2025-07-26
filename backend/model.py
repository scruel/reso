
# 请求和响应模型
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户输入消息")
    session_id: Optional[str] = Field(None, description="会话ID，可选")

class ItemInfo(BaseModel):
    title: str = Field("", description="推荐产品标题")
    pic_url: str = Field("", description="产品图片URL")

class DecisionChain(BaseModel):
    topic: str = Field("", description="决策点主题")
    content: str = Field("", description="决策内容")

class ChatResponse(BaseModel):
    items: ItemInfo = Field(default_factory=ItemInfo, description="推荐产品信息")
    dchain: List[DecisionChain] = Field(default_factory=list, description="决策链")
    message: str = Field("", description="回复消息")
