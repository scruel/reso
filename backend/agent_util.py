
# async def initialize_agents():
#     """初始化所有AI Agents"""
#     global orchestrator, behavior_recorder
    
#     try:
#         logger.info("正在初始化AI Agents系统...")
        
#         # 创建协调器
#         orchestrator = MultiAgentOrchestrator()
        
#         # 创建并注册所有Agent
#         from agents.intent_agent.camel_intent_agent import create_intent_agent
#         from agents.orchestrator.multi_agent_orchestrator import AgentType
#         from agents.docas_agent.agent_core import create_docas_agent
#         from agents.execution_agent.camel_execution_agent import ExecutionAgent
#         from agents.check_agent.requirement_check_agent import RequirementCheckAgent
        
#         # 注册各个Agent
#         intent_agent = await create_intent_agent()
#         orchestrator.register_agent(AgentType.INTENT_AGENT, intent_agent)
        
#         docas_agent = await create_docas_agent()
#         orchestrator.register_agent(AgentType.DOCAS_AGENT, docas_agent)
        
#         execution_agent = ExecutionAgent()
#         orchestrator.register_agent(AgentType.EXECUTION_AGENT, execution_agent)
        
#         check_agent = RequirementCheckAgent()
#         orchestrator.register_agent(AgentType.CHECK_AGENT, check_agent)
        
#         # 创建行为记录器
#         behavior_recorder = BehaviorRecorderAgent()
        
#         logger.info("AI Agents系统初始化完成")
#         return True
        
#     except Exception as e:
#         logger.error(f"AI Agents系统初始化失败: {e}")
#         return False

# def format_response_for_frontend(ai_result: Dict, user_input: str) -> ChatResponse:
#     """将AI结果格式化为前端需要的格式"""
#     try:
#         # 如果AI处理成功，使用AI结果
#         if ai_result.get("success"):
#             result_data = ai_result.get("result", {})
#             recommendation = result_data.get("recommendation", "")
#             execution_status = result_data.get("execution_status", {})
#             execution_history = execution_status.get("execution_history", [])
#             user_intent = result_data.get("user_intent_summary", {})
            
#             # 构建items（从AI结果或mock数据）
#             items = ItemInfo()
            
#             # 尝试从execution_history中提取产品信息
#             selected_product = None
#             if execution_history:
#                 last_execution = execution_history[-1].get("execution_result", {})
#                 if last_execution.get("success") and "recommendations" in last_execution:
#                     recommendations = last_execution["recommendations"]
#                     if recommendations:
#                         selected_product = recommendations[0]
            
#             # 如果AI没有返回具体产品，使用mock数据
#             if not selected_product:
#                 selected_product = get_mock_recommendation(user_input)
            
#             items.title = selected_product.get("name", "智能推荐油烟机")
#             items.pic_url = selected_product.get("image_url", "")
            
#             # 构建dchain（决策链）
#             dchain = []
            
#             # 添加需求理解
#             if user_intent.get("intent_type"):
#                 dchain.append(DecisionChain(
#                     topic="需求分析",
#                     content=f"识别您的{user_intent['intent_type']}需求，AI理解置信度{user_intent.get('confidence', 0.8):.1f}"
#                 ))
            
#             # 添加产品匹配分析
#             price = selected_product.get("price", 0)
#             features = selected_product.get("features", [])
#             dchain.append(DecisionChain(
#                 topic="产品匹配",
#                 content=f"价格{price}元，主要特点：{', '.join(features[:3])}"
#             ))
            
#             # 添加执行历史中的关键决策点
#             for i, history in enumerate(execution_history, 1):
#                 check_result = history.get("check_result", {})
#                 satisfaction_score = check_result.get("satisfaction_score", 0.8)
                
#                 dchain.append(DecisionChain(
#                     topic=f"AI评估{i}",
#                     content=f"满足度评分: {satisfaction_score:.1f}/1.0"
#                 ))
                
#                 # 添加改进建议
#                 suggestions = check_result.get("improvement_suggestions", [])
#                 if suggestions:
#                     dchain.append(DecisionChain(
#                         topic="优化建议", 
#                         content="; ".join(suggestions[:2])
#                     ))
#                     break  # 只显示第一轮建议
            
#             # 添加最终推荐理由
#             suitable_for = selected_product.get("suitable_for", [])
#             if suitable_for:
#                 dchain.append(DecisionChain(
#                     topic="推荐理由",
#                     content=f"适合：{', '.join(suitable_for)}"
#                 ))
            
#             # 构建message
#             if recommendation:
#                 message = recommendation
#             else:
#                 message = f"基于您的需求分析，我推荐{selected_product['name']}。这款产品{', '.join(features[:2])}，售价{price}元，性价比很高。"
        
#         else:
#             # AI处理失败，使用fallback逻辑
#             logger.warning("AI处理失败，使用fallback逻辑")
#             selected_product = get_mock_recommendation(user_input)
            
#             items = ItemInfo(
#                 title=selected_product["name"],
#                 pic_url=selected_product["image_url"]
#             )
            
#             dchain = [
#                 DecisionChain(topic="快速匹配", content="基于关键词快速匹配"),
#                 DecisionChain(topic="产品特点", content=f"主要特点：{', '.join(selected_product['features'][:2])}"),
#                 DecisionChain(topic="价格区间", content=f"售价{selected_product['price']}元")
#             ]
            
#             message = f"为您推荐{selected_product['name']}，售价{selected_product['price']}元。主要特点：{', '.join(selected_product['features'][:3])}。"
        
#         # 确保dchain不为空
#         if not dchain:
#             dchain = [
#                 DecisionChain(topic="AI分析", content="正在智能分析您的需求"),
#                 DecisionChain(topic="产品匹配", content="基于多维度算法推荐最适合的产品")
#             ]
        
#         return ChatResponse(
#             items=items,
#             dchain=dchain,
#             message=message
#         )
        
#     except Exception as e:
#         logger.error(f"格式化响应失败: {e}")
#         # 返回默认响应
#         default_product = MOCK_PRODUCTS[0]
#         return ChatResponse(
#             items=ItemInfo(
#                 title=default_product["name"],
#                 pic_url=default_product["image_url"]
#             ),
#             dchain=[
#                 DecisionChain(topic="系统提示", content="使用默认推荐算法"),
#                 DecisionChain(topic="产品信息", content=f"推荐{default_product['name']}")
#             ],
#             message=f"系统为您推荐{default_product['name']}，这是一款性能稳定的产品。"
#         )
