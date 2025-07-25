"""
基于CAMEL框架的执行Agent
负责执行用户的购买决策、处理订单、协调后续服务等
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelType, ModelPlatformType, RoleType
from camel.configs import ChatGPTConfig
import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

class ActionType(Enum):
    ADD_TO_CART = "add_to_cart"
    PLACE_ORDER = "place_order"
    SCHEDULE_INSTALLATION = "schedule_installation"
    REQUEST_CONSULTATION = "request_consultation"
    SAVE_TO_WISHLIST = "save_to_wishlist"
    COMPARE_PRODUCTS = "compare_products"
    REQUEST_QUOTE = "request_quote"
    CONTACT_SERVICE = "contact_service"

@dataclass
class ExecutionResult:
    action_type: ActionType
    success: bool
    result_data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0

class ExecutionAgent:
    """基于CAMEL框架的执行Agent"""
    
    def __init__(self, agent_id: str = "execution_agent"):
        self.agent_id = agent_id
        
        # 设置Kimi API环境变量
        kimi_key = os.getenv("KIMI_API_KEY", "")
        if kimi_key:
            os.environ['MOONSHOT_API_KEY'] = kimi_key
        
        # 配置模型参数
        model_config_dict = {
            'temperature': 0.1,  # 执行Agent需要更确定性的输出
            'max_tokens': 1000
        }
        
        # 创建CAMEL Agent，使用Kimi模型
        self.camel_agent = ChatAgent(
            system_message=self._create_system_message(),
            model=ModelFactory.create(
                model_platform=ModelPlatformType.MOONSHOT,  # 使用Moonshot/Kimi
                model_type="kimi-k2-0711-preview",                   # 使用kimi-k2-0711-preview模型
                model_config_dict=model_config_dict
            ),
            message_window_size=10
        )
        
        # 注册可执行的动作
        self.action_handlers = self._register_action_handlers()
        
        logger.info(f"ExecutionAgent {agent_id} initialized with CAMEL framework")
    
    async def execute_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行操作的统一接口，供协调器调用"""
        try:
            user_intent = operation_data.get("user_intent", {})
            recommendation = operation_data.get("recommendation", {})
            iteration = operation_data.get("iteration", 1)
            
            # 使用CAMEL框架分析和执行
            execution_prompt = f"""
            基于以下信息执行用户操作：
            
            用户意图：{json.dumps(user_intent, ensure_ascii=False, indent=2)}
            推荐结果：{json.dumps(recommendation, ensure_ascii=False, indent=2)}
            执行轮次：{iteration}
            
            请分析并执行最合适的操作，返回执行结果。
            """
            
            user_msg = BaseMessage(
                role_name="system",
                role_type=RoleType.USER,
                meta_dict={},
                content=execution_prompt
            )
            
            # 使用同步方式调用CAMEL Agent
            response = self.camel_agent.step(user_msg)
            
            return {
                "success": True,
                "result": response.msg.content,
                "execution_time": 0.5,
                "iteration": iteration
            }
            
        except Exception as e:
            logger.error(f"ExecutionAgent操作执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    def _create_system_message(self) -> BaseMessage:
        """创建系统消息"""
        system_prompt = """
        你是一个专业的电商执行助手，负责帮助用户完成购买决策和相关操作。

        你的职责：
        1. 分析用户的购买意图和推荐结果
        2. 确定最合适的执行动作
        3. 执行具体的业务操作（加购物车、下单、预约安装等）
        4. 处理执行过程中的异常情况
        5. 提供执行结果反馈

        可执行的动作类型：
        - add_to_cart: 添加商品到购物车
        - place_order: 直接下单
        - schedule_installation: 预约安装服务
        - request_consultation: 申请专业咨询
        - save_to_wishlist: 保存到心愿单
        - compare_products: 产品对比
        - request_quote: 申请报价
        - contact_service: 联系客服

        输出格式：
        {
            "recommended_action": "action_type",
            "action_parameters": {
                "product_id": 123,
                "quantity": 1,
                "special_requirements": "需要预约安装时间"
            },
            "execution_plan": [
                {"step": 1, "action": "validate_product", "description": "验证商品信息"},
                {"step": 2, "action": "add_to_cart", "description": "添加到购物车"},
                {"step": 3, "action": "confirm_action", "description": "确认操作结果"}
            ],
            "risk_assessment": {
                "confidence": 0.95,
                "potential_issues": ["库存不足", "配送限制"],
                "fallback_actions": ["联系客服", "选择替代产品"]
            }
        }

        执行原则：
        - 确保用户理解每一步操作
        - 在关键操作前进行确认
        - 提供清晰的执行状态反馈
        - 遇到问题时主动提供解决方案
        """
        
        return BaseMessage(
            role_name="execution_expert",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content=system_prompt
        )
    
    def _register_action_handlers(self) -> Dict[ActionType, callable]:
        """注册动作处理器"""
        return {
            ActionType.ADD_TO_CART: self._handle_add_to_cart,
            ActionType.PLACE_ORDER: self._handle_place_order,
            ActionType.SCHEDULE_INSTALLATION: self._handle_schedule_installation,
            ActionType.REQUEST_CONSULTATION: self._handle_request_consultation,
            ActionType.SAVE_TO_WISHLIST: self._handle_save_to_wishlist,
            ActionType.COMPARE_PRODUCTS: self._handle_compare_products,
            ActionType.REQUEST_QUOTE: self._handle_request_quote,
            ActionType.CONTACT_SERVICE: self._handle_contact_service
        }
    
    async def plan_execution(self, user_intent: Dict, recommendation_result: Dict) -> Dict:
        """规划执行方案"""
        try:
            # 构造规划消息
            planning_message = self._construct_planning_message(user_intent, recommendation_result)
            
            # 使用CAMEL Agent分析
            response = self.camel_agent.step(planning_message)
            
            # 解析执行计划
            execution_plan = self._parse_execution_plan(response.msg.content)
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"Execution planning failed: {e}")
            return {
                "error": str(e),
                "recommended_action": "contact_service",
                "fallback_plan": True
            }
    
    async def execute_action(self, action_type: ActionType, parameters: Dict) -> ExecutionResult:
        """执行具体动作"""
        start_time = time.time()
        
        try:
            if action_type not in self.action_handlers:
                return ExecutionResult(
                    action_type=action_type,
                    success=False,
                    result_data={},
                    error_message=f"Unsupported action type: {action_type.value}",
                    execution_time=time.time() - start_time
                )
            
            # 执行动作
            handler = self.action_handlers[action_type]
            result_data = await handler(parameters)
            
            return ExecutionResult(
                action_type=action_type,
                success=True,
                result_data=result_data,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ExecutionResult(
                action_type=action_type,
                success=False,
                result_data={},
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _construct_planning_message(self, user_intent: Dict, recommendation_result: Dict) -> BaseMessage:
        """构造规划消息"""
        message_content = f"""
        用户意图分析结果：
        {json.dumps(user_intent, ensure_ascii=False, indent=2)}
        
        推荐结果：
        {json.dumps(recommendation_result, ensure_ascii=False, indent=2)}
        
        请基于用户意图和推荐结果，制定最合适的执行方案。
        考虑用户的购买阶段、紧急程度和具体需求，推荐最适合的动作。
        """
        
        return BaseMessage.make_user_message(
            role_name="user",
            content=message_content.strip()
        )
    
    def _parse_execution_plan(self, response_content: str) -> Dict:
        """解析执行计划"""
        try:
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
            
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 默认计划
            return {
                "recommended_action": "add_to_cart",
                "action_parameters": {},
                "execution_plan": [
                    {"step": 1, "action": "validate_input", "description": "验证输入参数"},
                    {"step": 2, "action": "execute_primary", "description": "执行主要操作"},
                    {"step": 3, "action": "confirm_result", "description": "确认执行结果"}
                ],
                "risk_assessment": {
                    "confidence": 0.7,
                    "potential_issues": [],
                    "fallback_actions": ["contact_service"]
                }
            }
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse execution plan: {response_content}")
            return {"error": "Failed to parse execution plan"}
    
    # 动作处理器实现
    async def _handle_add_to_cart(self, parameters: Dict) -> Dict:
        """处理添加到购物车"""
        product_id = parameters.get("product_id")
        quantity = parameters.get("quantity", 1)
        
        # 模拟添加到购物车的逻辑
        # 实际实现会调用电商平台API
        
        return {
            "cart_id": f"cart_{int(time.time())}",
            "product_id": product_id,
            "quantity": quantity,
            "status": "added",
            "message": f"已成功添加 {quantity} 件商品到购物车"
        }
    
    async def _handle_place_order(self, parameters: Dict) -> Dict:
        """处理下单"""
        product_id = parameters.get("product_id")
        user_info = parameters.get("user_info", {})
        
        # 模拟下单逻辑
        order_id = f"order_{int(time.time())}"
        
        return {
            "order_id": order_id,
            "product_id": product_id,
            "status": "pending_payment",
            "estimated_delivery": "3-5个工作日",
            "message": f"订单 {order_id} 创建成功，请完成支付"
        }
    
    async def _handle_schedule_installation(self, parameters: Dict) -> Dict:
        """处理预约安装"""
        product_id = parameters.get("product_id")
        preferred_time = parameters.get("preferred_time")
        
        # 模拟预约安装逻辑
        appointment_id = f"install_{int(time.time())}"
        
        return {
            "appointment_id": appointment_id,
            "product_id": product_id,
            "scheduled_time": preferred_time or "待协调",
            "technician_contact": "13800138000",
            "status": "scheduled",
            "message": "安装服务已预约，师傅会提前联系您"
        }
    
    async def _handle_request_consultation(self, parameters: Dict) -> Dict:
        """处理咨询申请"""
        consultation_type = parameters.get("type", "product_consultation")
        user_question = parameters.get("question", "")
        
        consultation_id = f"consult_{int(time.time())}"
        
        return {
            "consultation_id": consultation_id,
            "type": consultation_type,
            "status": "pending",
            "estimated_response_time": "2小时内",
            "contact_method": "电话回访",
            "message": "专业顾问将在2小时内联系您"
        }
    
    async def _handle_save_to_wishlist(self, parameters: Dict) -> Dict:
        """处理保存到心愿单"""
        product_id = parameters.get("product_id")
        
        return {
            "wishlist_id": f"wish_{int(time.time())}",
            "product_id": product_id,
            "status": "saved",
            "message": "商品已保存到心愿单"
        }
    
    async def _handle_compare_products(self, parameters: Dict) -> Dict:
        """处理产品对比"""
        product_ids = parameters.get("product_ids", [])
        
        return {
            "comparison_id": f"compare_{int(time.time())}",
            "product_ids": product_ids,
            "comparison_url": f"/compare?products={','.join(map(str, product_ids))}",
            "message": f"已创建 {len(product_ids)} 个产品的对比页面"
        }
    
    async def _handle_request_quote(self, parameters: Dict) -> Dict:
        """处理报价申请"""
        products = parameters.get("products", [])
        
        return {
            "quote_id": f"quote_{int(time.time())}",
            "products": products,
            "status": "processing",
            "estimated_time": "1个工作日",
            "message": "报价申请已提交，将在1个工作日内提供详细报价"
        }
    
    async def _handle_contact_service(self, parameters: Dict) -> Dict:
        """处理联系客服"""
        issue_type = parameters.get("issue_type", "general")
        
        return {
            "ticket_id": f"ticket_{int(time.time())}",
            "issue_type": issue_type,
            "status": "created",
            "service_hotline": "400-123-4567",
            "online_chat": "available",
            "message": "客服工单已创建，可通过热线或在线聊天获得帮助"
        }
    
    async def get_execution_status(self, execution_id: str) -> Dict:
        """获取执行状态"""
        # 模拟状态查询
        return {
            "execution_id": execution_id,
            "status": "completed",
            "progress": 100,
            "message": "执行完成"
        }

# 对外接口
async def create_execution_agent(agent_id: str = "execution_agent") -> ExecutionAgent:
    """创建执行Agent实例"""
    return ExecutionAgent(agent_id)

if __name__ == "__main__":
    # 测试代码
    async def test_execution_agent():
        agent = await create_execution_agent()
        
        # 测试用户意图
        user_intent = {
            "intent_type": "product_search",
            "confidence": 0.9,
            "entities": {"product_category": "油烟机", "price_range": {"max": 3000}},
            "context": {"urgency": "medium", "decision_stage": "ready_to_buy"}
        }
        
        # 测试推荐结果
        recommendation_result = {
            "recommendation": "推荐方太CXW-200-EMC2，2999元",
            "matched_products": [{"id": 1, "brand": "方太", "price": 2999}],
            "confidence": 0.85
        }
        
        # 规划执行
        execution_plan = await agent.plan_execution(user_intent, recommendation_result)
        print("执行计划:")
        print(json.dumps(execution_plan, ensure_ascii=False, indent=2))
        
        # 执行动作
        if not execution_plan.get("error"):
            action_type = ActionType(execution_plan.get("recommended_action", "add_to_cart"))
            parameters = execution_plan.get("action_parameters", {"product_id": 1})
            
            result = await agent.execute_action(action_type, parameters)
            print(f"\\n执行结果:")
            print(f"Success: {result.success}")
            print(f"Result: {json.dumps(result.result_data, ensure_ascii=False, indent=2)}")
    
