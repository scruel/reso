from agents.recorder_agent.camel_behavior_recorder import BehaviorRecorderAgent
from agents.messaging.message_broker import MessageBroker, MessageType

class IntegratedBehaviorRecording:
    """集成行为记录系统"""
    
    def __init__(self, message_broker: MessageBroker):
        self.recorder_agent = BehaviorRecorderAgent()
        self.message_broker = message_broker
        self._setup_message_listeners()
    
    def _setup_message_listeners(self):
        """设置消息监听器"""
        
        # 监听所有Agent交互消息
        self.message_broker.subscribe("behavior_recorder", MessageType.REQUEST)
        self.message_broker.subscribe("behavior_recorder", MessageType.RESPONSE)
        self.message_broker.subscribe("behavior_recorder", MessageType.NOTIFICATION)
        
        # 注册消息处理器
        self.message_broker.register_handler(
            "behavior_recorder",
            MessageType.REQUEST,
            self._handle_interaction_record
        )
    
    async def _handle_interaction_record(self, message):
        """处理交互记录消息"""
        
        interaction_data = {
            "type": message.message_type.value,
            "session_id": message.payload.get("session_id"),
            "user_id": message.payload.get("user_id"),
            "source": message.from_agent,
            "target": message.to_agent,
            "content": message.payload,
            "timestamp": message.timestamp
        }
        
        # 使用CAMEL Agent进行智能记录
        result = await self.recorder_agent.record_interaction(interaction_data)
        
        logger.info(f"行为记录完成: {result['record_id']}")
    
    async def record_purchase_completion(self, session_data: Dict[str, Any]):
        """记录购买完成"""
        
        complete_session = {
            "session_id": session_data["session_id"],
            "user_id": session_data.get("user_id", "anonymous"),
            "start_time": session_data["start_time"],
            "end_time": session_data["end_time"],
            "user_input": session_data["original_input"],
            "intent_analysis": session_data["intent_results"],
            "recommendations": session_data["recommendation_results"],
            "selected_product": session_data["final_selection"],
            "decision_process": session_data["interaction_history"],
            "purchase_result": session_data["purchase_result"]
        }
        
        # 使用CAMEL Agent记录完整购买旅程
        journey_record = await self.recorder_agent.record_purchase_journey(complete_session)
        
        # 获取行为洞察
        insights = await self.recorder_agent.get_behavior_insights(session_data["session_id"])
        
        return {
            "journey_record": journey_record,
            "insights": insights
        }