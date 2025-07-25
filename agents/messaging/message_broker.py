"""
Agent间消息传递机制
提供标准化的Agent通信协议和消息队列系统
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import time
import uuid
from collections import deque
import threading

logger = logging.getLogger(__name__)

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class AgentMessage:
    """Agent间通信消息格式"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: float = 0.0
    ttl: Optional[float] = None  # Time to live
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class MessageHandler:
    """消息处理器"""
    handler_id: str
    message_type: MessageType
    handler_func: Callable
    agent_id: str

class MessageBroker:
    """消息代理，负责Agent间消息路由和传递"""
    
    def __init__(self):
        self.message_queues = {}  # agent_id -> deque of messages
        self.handlers = {}  # agent_id -> list of handlers
        self.subscribers = {}  # message_type -> list of agent_ids
        self.message_history = deque(maxlen=1000)  # 保留最近1000条消息
        self.active_agents = set()
        self.lock = threading.Lock()
        
        logger.info("MessageBroker initialized")
    
    def register_agent(self, agent_id: str):
        """注册Agent"""
        with self.lock:
            if agent_id not in self.message_queues:
                self.message_queues[agent_id] = deque()
            if agent_id not in self.handlers:
                self.handlers[agent_id] = []
            self.active_agents.add(agent_id)
        
        logger.info(f"Agent {agent_id} registered with MessageBroker")
    
    def unregister_agent(self, agent_id: str):
        """注销Agent"""
        with self.lock:
            self.active_agents.discard(agent_id)
            if agent_id in self.message_queues:
                self.message_queues[agent_id].clear()
        
        logger.info(f"Agent {agent_id} unregistered from MessageBroker")
    
    def register_handler(self, agent_id: str, message_type: MessageType, handler_func: Callable):
        """注册消息处理器"""
        handler = MessageHandler(
            handler_id=f"{agent_id}_{message_type.value}_{int(time.time())}",
            message_type=message_type,
            handler_func=handler_func,
            agent_id=agent_id
        )
        
        with self.lock:
            if agent_id not in self.handlers:
                self.handlers[agent_id] = []
            self.handlers[agent_id].append(handler)
        
        logger.info(f"Handler registered for {agent_id}: {message_type.value}")
    
    def subscribe(self, agent_id: str, message_type: MessageType):
        """订阅特定类型的消息"""
        with self.lock:
            if message_type not in self.subscribers:
                self.subscribers[message_type] = []
            if agent_id not in self.subscribers[message_type]:
                self.subscribers[message_type].append(agent_id)
        
        logger.info(f"Agent {agent_id} subscribed to {message_type.value}")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """发送消息"""
        try:
            # 验证消息
            if not self._validate_message(message):
                logger.error(f"Invalid message: {message.message_id}")
                return False
            
            # 检查TTL
            if message.ttl and (time.time() - message.timestamp) > message.ttl:
                logger.warning(f"Message {message.message_id} expired")
                return False
            
            # 检查目标Agent是否存在
            if message.to_agent not in self.active_agents:
                logger.error(f"Target agent {message.to_agent} not found")
                return False
            
            # 添加到消息队列
            with self.lock:
                self.message_queues[message.to_agent].append(message)
                self.message_history.append(message)
            
            # 触发消息处理
            await self._process_message(message)
            
            logger.debug(f"Message {message.message_id} sent to {message.to_agent}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {e}")
            return False
    
    async def broadcast_message(self, from_agent: str, message_type: MessageType, payload: Dict) -> List[str]:
        """广播消息给所有订阅者"""
        successful_sends = []
        
        subscribers = self.subscribers.get(message_type, [])
        for subscriber in subscribers:
            if subscriber != from_agent:  # 不发送给自己
                message = AgentMessage(
                    message_id=str(uuid.uuid4()),
                    from_agent=from_agent,
                    to_agent=subscriber,
                    message_type=message_type,
                    priority=MessagePriority.NORMAL,
                    payload=payload
                )
                
                if await self.send_message(message):
                    successful_sends.append(subscriber)
        
        return successful_sends
    
    async def get_messages(self, agent_id: str, limit: Optional[int] = None) -> List[AgentMessage]:
        """获取Agent的消息"""
        if agent_id not in self.message_queues:
            return []
        
        messages = []
        with self.lock:
            queue = self.message_queues[agent_id]
            count = 0
            while queue and (limit is None or count < limit):
                messages.append(queue.popleft())
                count += 1
        
        return messages
    
    async def _process_message(self, message: AgentMessage):
        """处理消息"""
        target_agent = message.to_agent
        
        if target_agent not in self.handlers:
            logger.warning(f"No handlers found for agent {target_agent}")
            return
        
        # 查找匹配的处理器
        handlers = self.handlers[target_agent]
        for handler in handlers:
            if handler.message_type == message.message_type:
                try:
                    await handler.handler_func(message)
                except Exception as e:
                    logger.error(f"Handler error for {handler.handler_id}: {e}")
    
    def _validate_message(self, message: AgentMessage) -> bool:
        """验证消息格式"""
        if not message.message_id or not message.from_agent or not message.to_agent:
            return False
        if not isinstance(message.message_type, MessageType):
            return False
        if not isinstance(message.priority, MessagePriority):
            return False
        return True
    
    def get_queue_status(self, agent_id: str) -> Dict:
        """获取队列状态"""
        if agent_id not in self.message_queues:
            return {"error": "Agent not found"}
        
        with self.lock:
            queue = self.message_queues[agent_id]
            return {
                "agent_id": agent_id,
                "queue_length": len(queue),
                "handlers_count": len(self.handlers.get(agent_id, [])),
                "is_active": agent_id in self.active_agents
            }
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        with self.lock:
            return {
                "total_agents": len(self.active_agents),
                "active_agents": list(self.active_agents),
                "total_queues": len(self.message_queues),
                "total_handlers": sum(len(handlers) for handlers in self.handlers.values()),
                "message_history_size": len(self.message_history),
                "subscribers": {k.value: v for k, v in self.subscribers.items()}
            }

class AgentCommunicator:
    """Agent通信客户端"""
    
    def __init__(self, agent_id: str, message_broker: MessageBroker):
        self.agent_id = agent_id
        self.broker = message_broker
        self.pending_requests = {}  # correlation_id -> future
        
        # 注册到broker
        self.broker.register_agent(agent_id)
        
        # 注册默认处理器
        self.broker.register_handler(
            agent_id, MessageType.RESPONSE, self._handle_response
        )
        
        logger.info(f"AgentCommunicator initialized for {agent_id}")
    
    async def send_request(self, to_agent: str, payload: Dict, timeout: float = 30.0) -> Dict:
        """发送请求并等待响应"""
        correlation_id = str(uuid.uuid4())
        
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=MessageType.REQUEST,
            priority=MessagePriority.NORMAL,
            payload=payload,
            correlation_id=correlation_id,
            ttl=timeout
        )
        
        # 创建Future等待响应
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[correlation_id] = future
        
        try:
            # 发送消息
            success = await self.broker.send_message(message)
            if not success:
                raise Exception("Failed to send message")
            
            # 等待响应
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Request to {to_agent} timed out")
            raise
        finally:
            # 清理pending request
            self.pending_requests.pop(correlation_id, None)
    
    async def send_response(self, original_message: AgentMessage, response_payload: Dict):
        """发送响应"""
        response_message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=original_message.from_agent,
            message_type=MessageType.RESPONSE,
            priority=MessagePriority.NORMAL,
            payload=response_payload,
            correlation_id=original_message.correlation_id
        )
        
        await self.broker.send_message(response_message)
    
    async def send_notification(self, to_agent: str, payload: Dict):
        """发送通知（无需响应）"""
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=MessageType.NOTIFICATION,
            priority=MessagePriority.NORMAL,
            payload=payload
        )
        
        await self.broker.send_message(message)
    
    async def broadcast(self, message_type: MessageType, payload: Dict):
        """广播消息"""
        return await self.broker.broadcast_message(self.agent_id, message_type, payload)
    
    def subscribe(self, message_type: MessageType):
        """订阅消息类型"""
        self.broker.subscribe(self.agent_id, message_type)
    
    def register_handler(self, message_type: MessageType, handler_func: Callable):
        """注册消息处理器"""
        self.broker.register_handler(self.agent_id, message_type, handler_func)
    
    async def _handle_response(self, message: AgentMessage):
        """处理响应消息"""
        if message.correlation_id in self.pending_requests:
            future = self.pending_requests[message.correlation_id]
            if not future.done():
                future.set_result(message.payload)
    
    async def get_messages(self, limit: Optional[int] = None) -> List[AgentMessage]:
        """获取待处理消息"""
        return await self.broker.get_messages(self.agent_id, limit)
    
    def cleanup(self):
        """清理资源"""
        self.broker.unregister_agent(self.agent_id)

# 全局消息代理实例
_global_message_broker = MessageBroker()

def get_message_broker() -> MessageBroker:
    """获取全局消息代理"""
    return _global_message_broker

async def create_agent_communicator(agent_id: str) -> AgentCommunicator:
    """创建Agent通信客户端"""
    return AgentCommunicator(agent_id, get_message_broker())

if __name__ == "__main__":
    # 测试代码
    async def test_message_system():
        broker = get_message_broker()
        
        # 创建两个Agent通信客户端
        agent1 = await create_agent_communicator("agent1")
        agent2 = await create_agent_communicator("agent2")
        
        # Agent2注册请求处理器
        async def handle_request(message: AgentMessage):
            print(f"Agent2 received request: {message.payload}")
            await agent2.send_response(message, {"status": "processed", "result": "success"})
        
        agent2.register_handler(MessageType.REQUEST, handle_request)
        
        # Agent1发送请求给Agent2
        try:
            response = await agent1.send_request("agent2", {"action": "test", "data": "hello"})
            print(f"Agent1 received response: {response}")
        except Exception as e:
            print(f"Request failed: {e}")
        
        # 测试广播
        agent1.subscribe(MessageType.NOTIFICATION)
        agent2.subscribe(MessageType.NOTIFICATION)
        
        broadcast_result = await agent1.broadcast(
            MessageType.NOTIFICATION, 
            {"event": "system_update", "version": "1.0"}
        )
        print(f"Broadcast sent to: {broadcast_result}")
        
        # 清理
        agent1.cleanup()
        agent2.cleanup()
    
    asyncio.run(test_message_system())