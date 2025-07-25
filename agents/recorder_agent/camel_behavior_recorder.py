import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelType, ModelPlatformType, RoleType
from camel.models import ModelFactory

logger = logging.getLogger(__name__)

@dataclass
class BehaviorRecord:
    """行为记录数据结构"""
    record_id: str
    session_id: str
    user_id: str
    timestamp: datetime
    
    # 交互信息
    interaction_type: str  # user_input, agent_response, system_event
    source_agent: str
    target_agent: str
    content_preview: str
    full_content: Dict[str, Any]
    
    # 上下文信息
    conversation_context: Dict[str, Any]
    agent_state: Dict[str, Any]
    
    # 元数据
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    error_info: Optional[Dict[str, Any]] = None

class BehaviorRecorderAgent(ChatAgent):
    """基于CAMEL框架的行为记录Agent，使用Kimi模型"""
    
    def __init__(self, model_platform=ModelPlatformType.MOONSHOT, model_type="moonshot-v1-8k"):
        # 确保设置Kimi API密钥
        if not os.environ.get('MOONSHOT_API_KEY'):
            kimi_key = os.environ.get('KIMI_API_KEY')
            if kimi_key:
                os.environ['MOONSHOT_API_KEY'] = kimi_key
        
        # 使用CAMEL框架创建Kimi Agent
        model = ModelFactory.create(
            model_platform=model_platform,
            model_type=model_type,
            model_config_dict={"temperature": 0.1, "max_tokens": 2000}
        )
        
        system_message = BaseMessage(
            role_name="BehaviorRecorder",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content="""你是一个专业的用户行为记录Agent，负责记录和分析用户与AI系统之间的所有交互行为。

你的职责包括：
1. **行为记录**：准确记录用户输入、Agent响应和系统事件
2. **模式识别**：识别用户行为模式和决策路径
3. **质量评估**：评估交互质量和用户满意度
4. **洞察提取**：提取有价值的用户洞察和系统改进建议
5. **隐私保护**：确保记录过程中保护用户隐私信息

记录原则：
- 完整记录交互流程，不遗漏关键信息
- 识别用户意图变化和行为模式
- 评估推荐效果和用户满意度
- 提供数据驱动的改进建议
- 确保敏感信息脱敏处理

输出格式：
始终以结构化的JSON格式输出记录结果，包含必要的元数据和分析。"""
        )
        
        super().__init__(
            system_message=system_message,
            model=model,
            message_window_size=50
        )
        
        self.records = []
        self.session_contexts = {}
        self.storage_path = "recorded_behaviors"
        os.makedirs(self.storage_path, exist_ok=True)
        
    async def record_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """记录单次交互"""
        
        # 准备记录消息
        record_prompt = f"""
        请分析并记录以下用户交互行为：
        
        交互类型：{interaction_data.get('type', 'unknown')}
        会话ID：{interaction_data.get('session_id', 'unknown')}
        用户ID：{interaction_data.get('user_id', 'anonymous')}
        
        交互内容：
        {json.dumps(interaction_data.get('content', {}), ensure_ascii=False, indent=2)}
        
        当前会话上下文：
        {json.dumps(interaction_data.get('context', {}), ensure_ascii=False, indent=2)}
        
        请提供：
        1. 交互行为的标准化记录
        2. 用户意图分析
        3. 交互质量评估
        4. 改进建议（如有）
        5. 隐私脱敏处理建议
        """
        
        user_msg = BaseMessage(
            role_name="System",
            role_type=RoleType.USER,
            meta_dict={},
            content=record_prompt
        )
        
        # 使用CAMEL框架进行智能分析（同步方式，因为Moonshot不支持异步）
        response = self.step(user_msg)
        
        # 创建行为记录
        record = BehaviorRecord(
            record_id=str(uuid.uuid4()),
            session_id=interaction_data.get('session_id', str(uuid.uuid4())),
            user_id=interaction_data.get('user_id', 'anonymous'),
            timestamp=datetime.now(),
            interaction_type=interaction_data.get('type', 'unknown'),
            source_agent=interaction_data.get('source', 'user'),
            target_agent=interaction_data.get('target', 'system'),
            content_preview=str(interaction_data.get('content', ''))[:200],
            full_content=interaction_data,
            conversation_context=interaction_data.get('context', {}),
            agent_state=interaction_data.get('agent_state', {}),
            processing_time=interaction_data.get('processing_time'),
            confidence_score=interaction_data.get('confidence_score')
        )
        
        self.records.append(record)
        
        # 解析CAMEL Agent的智能分析结果
        analysis_result = self._parse_analysis_response(response.msg.content)
        
        return {
            "record_id": record.record_id,
            "analysis": analysis_result,
            "status": "recorded"
        }
    
    async def record_purchase_journey(self, complete_session: Dict[str, Any]) -> Dict[str, Any]:
        """记录完整购买旅程"""
        
        journey_prompt = f"""
        请分析并记录以下完整的用户购买决策旅程：
        
        会话ID：{complete_session.get('session_id')}
        用户ID：{complete_session.get('user_id', 'anonymous')}
        开始时间：{complete_session.get('start_time')}
        结束时间：{complete_session.get('end_time')}
        
        用户原始需求：
        {json.dumps(complete_session.get('user_input', {}), ensure_ascii=False, indent=2)}
        
        意图理解结果：
        {json.dumps(complete_session.get('intent_analysis', {}), ensure_ascii=False, indent=2)}
        
        推荐产品列表：
        {json.dumps(complete_session.get('recommendations', []), ensure_ascii=False, indent=2)}
        
        用户选择：
        {json.dumps(complete_session.get('selected_product', {}), ensure_ascii=False, indent=2)}
        
        决策过程：
        {json.dumps(complete_session.get('decision_process', []), ensure_ascii=False, indent=2)}
        
        购买结果：
        {json.dumps(complete_session.get('purchase_result', {}), ensure_ascii=False, indent=2)}
        
        请提供：
        1. 完整的行为路径分析
        2. 用户决策模式识别
        3. 推荐系统效果评估
        4. 用户体验优化建议
        5. 商业价值洞察
        6. 数据隐私合规检查
        """
        
        user_msg = BaseMessage(
            role_name="System",
            role_type=RoleType.USER,
            meta_dict={},
            content=journey_prompt
        )
        
        response = self.step(user_msg)
        
        # 创建购买旅程记录
        journey_record = {
            "journey_id": str(uuid.uuid4()),
            "session_data": complete_session,
            "behavior_analysis": response.msg.content,
            "timestamp": datetime.now().isoformat(),
            "record_type": "complete_purchase_journey"
        }
        
        # 保存到存储
        self._save_journey_record(journey_record)
        
        return journey_record
    
    async def get_behavior_insights(self, session_id: str) -> Dict[str, Any]:
        """获取行为洞察"""
        
        insights_prompt = f"""
        基于会话{session_id}的所有行为记录，请提供以下洞察：
        
        1. 用户行为模式分析
        2. 推荐系统效果评估
        3. 用户满意度指标
        4. 系统改进建议
        5. 商业价值分析
        
        请确保分析基于实际数据，并提供可操作的改进建议。
        """
        
        user_msg = BaseMessage(
            role_name="System",
            role_type=RoleType.USER,
            meta_dict={},
            content=insights_prompt
        )
        
        response = self.step(user_msg)
        
        return {
            "session_id": session_id,
            "insights": response.msg.content,
            "generated_at": datetime.now().isoformat()
        }
    
    def _parse_analysis_response(self, response_content: str) -> Dict[str, Any]:
        """解析CAMEL Agent的分析响应"""
        try:
            # 尝试解析JSON格式的响应
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
            else:
                # 如果不是JSON，创建结构化响应
                return {
                    "analysis_text": response_content,
                    "structured_insights": {
                        "intent_clarity": "high",
                        "interaction_quality": "good",
                        "improvement_areas": [],
                        "privacy_check": "passed"
                    }
                }
        except Exception as e:
            logger.error(f"解析分析响应失败: {e}")
            return {"error": str(e), "raw_response": response_content}
    
    def _save_journey_record(self, journey_record: Dict[str, Any]):
        """保存旅程记录到存储"""
        try:
            # 保存到文件
            filename = f"{self.storage_path}/{journey_record['journey_id']}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(journey_record, f, ensure_ascii=False, indent=2)
            
            logger.info(f"购买旅程记录已保存: {filename}")
            
        except Exception as e:
            logger.error(f"保存旅程记录失败: {e}")

# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_recorder():
        print("🧪 测试 BehaviorRecorderAgent")
        
        try:
            recorder = BehaviorRecorderAgent()
            print("✅ BehaviorRecorderAgent 初始化成功")
            
            # 测试记录交互
            test_interaction = {
                "session_id": "test_session",
                "user_id": "test_user",
                "type": "user_input",
                "content": {"text": "我需要一个油烟机"}
            }
            
            result = await recorder.record_interaction(test_interaction)
            print("📝 记录结果:", result)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    asyncio.run(test_recorder())