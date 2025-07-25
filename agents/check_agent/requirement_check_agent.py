"""
基于CAMEL框架的CheckAgent
主要任务：检查ExecutionAgent是否满足用户需求
如果不满足，指导ExecutionAgent继续执行，直到满足为止（最多3次）
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
from typing import Dict, List, Optional, Any, Tuple
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

class SatisfactionLevel(Enum):
    FULLY_SATISFIED = "fully_satisfied"
    PARTIALLY_SATISFIED = "partially_satisfied"
    NOT_SATISFIED = "not_satisfied"
    CANNOT_DETERMINE = "cannot_determine"

@dataclass
class CheckResult:
    satisfaction_level: SatisfactionLevel
    satisfaction_score: float  # 0-1之间
    missing_requirements: List[str]
    improvement_suggestions: List[str]
    next_action_needed: bool
    confidence: float

class RequirementCheckAgent:
    """基于CAMEL框架的需求检查Agent"""
    
    def __init__(self, agent_id: str = "requirement_check_agent"):
        self.agent_id = agent_id
        
        # 设置Kimi API环境变量
        kimi_key = os.getenv("KIMI_API_KEY", "")
        if kimi_key:
            os.environ['MOONSHOT_API_KEY'] = kimi_key
        
        # 配置模型参数
        model_config_dict = {
            'temperature': 0.3,  # 需要一定的客观性但保持一些灵活性
            'max_tokens': 1200
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
        
        logger.info(f"RequirementCheckAgent {agent_id} initialized with CAMEL framework")
    
    def _create_system_message(self) -> BaseMessage:
        """创建系统消息"""
        system_prompt = """
        你是一个专业的需求验证专家，负责检查ExecutionAgent的执行结果是否满足用户的真实需求。

        你的核心任务：
        1. 对比用户的原始需求和ExecutionAgent的执行结果
        2. 判断执行结果是否完全满足用户需求
        3. 识别未满足的需求点和缺失的功能
        4. 为ExecutionAgent提供具体的改进建议
        5. 决定是否需要ExecutionAgent继续执行

        评估维度：
        - 需求匹配度：执行结果是否解决了用户的核心问题
        - 完整性：是否遗漏了用户的重要需求
        - 准确性：执行的操作是否正确和精确
        - 用户体验：结果是否符合用户的期望和使用习惯

        满足度级别：
        - fully_satisfied (0.8-1.0): 完全满足用户需求，无需进一步行动
        - partially_satisfied (0.5-0.8): 部分满足，需要补充或调整
        - not_satisfied (0.0-0.5): 未满足主要需求，需要重新执行
        - cannot_determine: 信息不足，无法判断

        输出格式：
        {
            "satisfaction_level": "fully_satisfied|partially_satisfied|not_satisfied|cannot_determine",
            "satisfaction_score": 0.75,
            "missing_requirements": [
                "未提供安装预约功能",
                "缺少产品详细参数对比"
            ],
            "improvement_suggestions": [
                "添加预约安装服务",
                "提供详细的产品规格对比表",
                "增加用户评价信息"
            ],
            "next_action_needed": true,
            "confidence": 0.9,
            "detailed_analysis": {
                "satisfied_aspects": ["产品推荐合理", "价格符合预算"],
                "unsatisfied_aspects": ["未处理安装需求", "缺少售后信息"],
                "critical_gaps": ["安装服务"]
            },
            "execution_guidance": {
                "priority_actions": ["联系安装服务", "提供产品详情"],
                "optional_actions": ["收集用户反馈"]
            }
        }

        检查原则：
        - 站在用户角度思考，关注用户真正的痛点
        - 严格但合理，不过度苛求完美
        - 提供具体可执行的改进建议
        - 考虑实际的业务约束和技术限制
        """
        
        return BaseMessage(
            role_name="requirement_validation_expert",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content=system_prompt
        )
    
    async def check_requirement_satisfaction(
        self, 
        user_intent: Dict, 
        execution_result: Dict,
        execution_round: int = 1
    ) -> CheckResult:
        """检查执行结果是否满足用户需求"""
        try:
            # 构造检查消息
            check_message = self._construct_check_message(
                user_intent, execution_result, execution_round
            )
            
            # 使用CAMEL Agent进行分析
            response = self.camel_agent.step(check_message)
            
            # 解析检查结果
            check_result = self._parse_check_result(response.msg.content)
            
            return check_result
            
        except Exception as e:
            logger.error(f"Requirement satisfaction check failed: {e}")
            return CheckResult(
                satisfaction_level=SatisfactionLevel.CANNOT_DETERMINE,
                satisfaction_score=0.0,
                missing_requirements=[f"检查过程出错: {str(e)}"],
                improvement_suggestions=["重新检查系统状态"],
                next_action_needed=True,
                confidence=0.0
            )
    
    async def iterative_check_and_guide(
        self,
        user_intent: Dict,
        execution_agent,
        max_iterations: int = 3
    ) -> Tuple[CheckResult, List[Dict]]:
        """迭代检查和指导执行，直到满足需求或达到最大次数"""
        
        execution_history = []
        current_execution_result = None
        
        for iteration in range(1, max_iterations + 1):
            logger.info(f"开始第 {iteration} 轮执行检查")
            
            # 如果是第一次，需要先执行
            if iteration == 1:
                # 从用户意图构造执行计划
                execution_plan = await execution_agent.plan_execution(user_intent, {})
                action_type = execution_plan.get("recommended_action", "add_to_cart")
                action_params = execution_plan.get("action_parameters", {})
                
                # 执行动作
                from ..execution_agent.camel_execution_agent import ActionType
                current_execution_result = await execution_agent.execute_action(
                    ActionType(action_type), action_params
                )
            
            # 记录执行历史
            execution_history.append({
                "round": iteration,
                "execution_result": current_execution_result,
                "timestamp": time.time()
            })
            
            # 检查需求满足度
            check_result = await self.check_requirement_satisfaction(
                user_intent, current_execution_result.__dict__, iteration
            )
            
            logger.info(f"第 {iteration} 轮检查结果: {check_result.satisfaction_level.value}")
            
            # 如果完全满足需求，结束循环
            if check_result.satisfaction_level == SatisfactionLevel.FULLY_SATISFIED:
                logger.info("用户需求已完全满足，结束执行")
                break
            
            # 如果是最后一轮，不再继续执行
            if iteration == max_iterations:
                logger.warning(f"已达到最大执行次数 {max_iterations}，结束执行")
                break
            
            # 如果需求未满足，指导下一轮执行
            if check_result.next_action_needed:
                logger.info(f"需求未完全满足，准备第 {iteration + 1} 轮执行")
                
                # 根据改进建议生成下一轮执行计划
                next_execution_plan = await self._generate_next_execution_plan(
                    user_intent, check_result, execution_history
                )
                
                # 执行下一轮动作
                if next_execution_plan.get("action_type"):
                    from ..execution_agent.camel_execution_agent import ActionType
                    action_type = ActionType(next_execution_plan["action_type"])
                    action_params = next_execution_plan.get("parameters", {})
                    
                    current_execution_result = await execution_agent.execute_action(
                        action_type, action_params
                    )
            else:
                logger.info("当前结果已足够，无需进一步执行")
                break
        
        return check_result, execution_history
    
    def _construct_check_message(
        self, 
        user_intent: Dict, 
        execution_result: Dict, 
        execution_round: int
    ) -> BaseMessage:
        """构造检查消息"""
        
        message_content = f"""
        执行轮次: {execution_round}
        
        用户原始意图和需求:
        {json.dumps(user_intent, ensure_ascii=False, indent=2)}
        
        ExecutionAgent的执行结果:
        {json.dumps(execution_result, ensure_ascii=False, indent=2)}
        
        请仔细对比用户的原始需求和执行结果，评估是否完全满足了用户的需求。
        
        重点关注：
        1. 用户的核心问题是否得到解决
        2. 用户明确提出的需求是否都被满足
        3. 是否有遗漏的重要功能或服务
        4. 执行结果的质量是否符合用户期望
        
        如果需求未完全满足，请提供具体的改进建议。
        """
        
        return BaseMessage.make_user_message(
            role_name="user",
            content=message_content.strip()
        )
    
    def _parse_check_result(self, response_content: str) -> CheckResult:
        """解析检查结果"""
        try:
            if response_content.strip().startswith('{'):
                result_data = json.loads(response_content)
            else:
                import re
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    # 如果无法解析JSON，创建默认结果
                    result_data = {
                        "satisfaction_level": "cannot_determine",
                        "satisfaction_score": 0.5,
                        "missing_requirements": ["无法解析检查结果"],
                        "improvement_suggestions": ["重新进行检查"],
                        "next_action_needed": True,
                        "confidence": 0.3
                    }
            
            return CheckResult(
                satisfaction_level=SatisfactionLevel(result_data.get("satisfaction_level", "cannot_determine")),
                satisfaction_score=result_data.get("satisfaction_score", 0.5),
                missing_requirements=result_data.get("missing_requirements", []),
                improvement_suggestions=result_data.get("improvement_suggestions", []),
                next_action_needed=result_data.get("next_action_needed", True),
                confidence=result_data.get("confidence", 0.5)
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse check result: {e}")
            return CheckResult(
                satisfaction_level=SatisfactionLevel.CANNOT_DETERMINE,
                satisfaction_score=0.0,
                missing_requirements=[f"解析错误: {str(e)}"],
                improvement_suggestions=["检查系统状态", "重新执行检查"],
                next_action_needed=True,
                confidence=0.0
            )
    
    async def _generate_next_execution_plan(
        self, 
        user_intent: Dict, 
        check_result: CheckResult, 
        execution_history: List[Dict]
    ) -> Dict:
        """基于检查结果生成下一轮执行计划"""
        
        planning_message = BaseMessage.make_user_message(
            role_name="user",
            content=f"""
            基于检查结果，需要为ExecutionAgent生成下一轮执行计划。
            
            用户需求:
            {json.dumps(user_intent, ensure_ascii=False, indent=2)}
            
            当前检查结果:
            - 满足度: {check_result.satisfaction_level.value}
            - 缺失需求: {check_result.missing_requirements}
            - 改进建议: {check_result.improvement_suggestions}
            
            执行历史:
            {json.dumps(execution_history, ensure_ascii=False, indent=2)}
            
            请生成下一步执行计划：
            {{
                "action_type": "具体动作类型",
                "parameters": {{"参数": "值"}},
                "priority": "high|medium|low",
                "reason": "执行原因"
            }}
            """
        )
        
        try:
            response = self.camel_agent.step(planning_message)
            
            if response.msg.content.strip().startswith('{'):
                return json.loads(response.msg.content)
            else:
                import re
                json_match = re.search(r'\{.*\}', response.msg.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"Failed to generate next execution plan: {e}")
        
        # 默认计划
        return {
            "action_type": "contact_service",
            "parameters": {"issue_type": "requirement_clarification"},
            "priority": "medium",
            "reason": "无法确定下一步行动，联系客服协助"
        }

# 对外接口
async def create_requirement_check_agent(agent_id: str = "requirement_check_agent") -> RequirementCheckAgent:
    """创建需求检查Agent实例"""
    return RequirementCheckAgent(agent_id)

if __name__ == "__main__":
    # 测试代码
    async def test_requirement_check_agent():
        agent = await create_requirement_check_agent()
        
        # 模拟用户意图
        user_intent = {
            "intent_type": "product_search",
            "confidence": 0.9,
            "entities": {
                "product_category": "油烟机",
                "price_range": {"max": 3000},
                "features": ["静音", "大吸力"]
            },
            "user_requirements": {
                "priority_features": ["静音", "大吸力"],
                "must_have": ["预算3000以内", "需要安装服务"]
            },
            "context": {
                "urgency": "high",
                "decision_stage": "ready_to_buy"
            }
        }
        
        # 模拟执行结果（不完整的结果）
        incomplete_execution_result = {
            "action_type": "add_to_cart",
            "success": True,
            "result_data": {
                "cart_id": "cart_123",
                "product_id": 1,
                "quantity": 1,
                "message": "已添加到购物车"
            }
        }
        
        # 检查需求满足度
        check_result = await agent.check_requirement_satisfaction(
            user_intent, incomplete_execution_result, 1
        )
        
        print("需求满足度检查结果:")
        print(f"满足度级别: {check_result.satisfaction_level.value}")
        print(f"满足度分数: {check_result.satisfaction_score}")
        print(f"缺失需求: {check_result.missing_requirements}")
        print(f"改进建议: {check_result.improvement_suggestions}")
        print(f"需要进一步行动: {check_result.next_action_needed}")
    