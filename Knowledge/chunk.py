MOCK_CHUNKS = [
    {
        "chunk_id": "chunk_006",
        "title": "用户积分规则",
        "content": "用户积分与消费金额、签到天数、观看时长关联，积分可用于兑换优惠券。",
        "knowledge_type": "relational"
    },
    {
        "chunk_id": "chunk_007",
        "title": "视频清晰度选项",
        "content": "视频支持高清、超清和4K清晰度，根据用户网络环境自动适配。",
        "knowledge_type": "declarative"
    },
    {
        "chunk_id": "chunk_008",
        "title": "订单状态流转",
        "content": "订单状态包括待支付、已支付、发货中、已完成、已取消，状态变更记录存储在order_log表。",
        "knowledge_type": "relational"
    },
    # {
    #     "chunk_id": "chunk_009",
    #     "title": "优惠券使用限制",
    #     "content": "优惠券仅限特定商品类别使用，且不可叠加，有效期自领取之日起7天。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_010",
    #     "title": "用户设备管理",
    #     "content": "用户可绑定最多5台设备，设备信息与user_id关联，用于多端同步和登录验证。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_011",
    #     "title": "会员自动续费",
    #     "content": "高级会员默认开启自动续费，可在会员中心关闭，续费前3天发送提醒通知。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_012",
    #     "title": "内容标签体系",
    #     "content": "内容标签与视频、文章等多实体关联，标签层级包括一级分类和二级标签。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_013",
    #     "title": "弹幕功能说明",
    #     "content": "弹幕支持发送、屏蔽、举报，弹幕内容需经过敏感词过滤。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_014",
    #     "title": "支付渠道配置",
    #     "content": "支付方式包括微信支付、支付宝、银行卡，各渠道对应的商户号与app_id关联。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_015",
    #     "title": "推荐算法简述",
    #     "content": "推荐基于用户历史行为、兴趣标签和热门度综合排序，每日更新一次。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_016",
    #     "title": "用户反馈工单",
    #     "content": "工单包含用户ID、问题类型、描述、附件、状态，客服处理记录关联工单ID。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_017",
    #     "title": "搜索语法规则",
    #     "content": "搜索支持关键词、引号精确匹配、减号排除、通配符*，按相关度排序。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_018",
    #     "title": "商品库存管理",
    #     "content": "库存数量与SKU_ID关联，下单时扣减库存，超时未支付则回滚。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_019",
    #     "title": "活动参与限制",
    #     "content": "每个用户每场活动仅可参与一次，活动奖品数量有限，先到先得。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_020",
    #     "title": "消息通知模板",
    #     "content": "消息模板包含模板ID、标题、内容变量，与触发事件类型关联。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_021",
    #     "title": "数据埋点规范",
    #     "content": "所有用户行为事件需上报事件名、用户ID、时间戳、扩展参数，采用批量上报方式。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_022",
    #     "title": "缓存策略",
    #     "content": "热点数据缓存于Redis，缓存key格式为业务前缀:ID，过期时间24小时。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_023",
    #     "title": "第三方登录集成",
    #     "content": "支持微信、QQ、微博第三方登录，绑定后与本地用户ID关联。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_024",
    #     "title": "安全风控规则",
    #     "content": "登录异常、短时间内大量操作等触发风控，需要验证码或冻结账号。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_025",
    #     "title": "商品评价体系",
    #     "content": "评价包含评分、内容、图片、商品ID和用户ID，审核通过后展示。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_026",
    #     "title": "分享奖励机制",
    #     "content": "用户分享内容并产生新注册，分享者获得积分奖励，被分享者获得优惠券。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_027",
    #     "title": "历史记录存储",
    #     "content": "用户观看历史、搜索历史存储于Elasticsearch，按用户ID分索引。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_028",
    #     "title": "订阅通知类型",
    #     "content": "订阅支持更新提醒、促销活动、系统公告，用户可自定义开关。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_029",
    #     "title": "权限角色设计",
    #     "content": "角色包括普通用户、会员、管理员，权限表与角色ID关联，控制接口访问。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_030",
    #     "title": "直播连麦功能",
    #     "content": "直播支持观众连麦、举手、同意，连麦时长计入主播奖励。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_031",
    #     "title": "发票申请流程",
    #     "content": "发票申请需填写抬头、税号、金额，关联订单ID，审核通过后开具。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_032",
    #     "title": "内容审核标准",
    #     "content": "视频、图文内容需经过机器+人工审核，色情、暴力等违规内容不予通过。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_033",
    #     "title": "用户等级成长",
    #     "content": "用户等级基于经验值，经验值来自登录、观看、互动，不同等级享有不同权益。",
    #     "knowledge_type": "relational"
    # },
    # {
    #     "chunk_id": "chunk_034",
    #     "title": "优惠券发放规则",
    #     "content": "优惠券可通过签到、活动、会员礼包获得，发放后记录领取时间和过期时间。",
    #     "knowledge_type": "declarative"
    # },
    # {
    #     "chunk_id": "chunk_035",
    #     "title": "数据同步策略",
    #     "content": "订单数据从主库同步到从库，延迟不超过1秒，用于报表查询。",
    #     "knowledge_type": "declarative"
    # }
]