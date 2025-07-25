"""
Multi-Agent层级协作架构
建立IntentAgent为父agent，ExecutionAgent和CheckAgent为子agent的层级关系
DocAsAgent全过程参与协作
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import time
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class AgentType(Enum):
    INTENT_AGENT = "intent_agent"
    DOCAS_AGENT = "docas_agent"
    EXECUTION_AGENT = "execution_agent"
    CHECK_AGENT = "check_agent"

@dataclass
class AgentTask:
    task_id: str
    agent_type: AgentType
    input_data: Dict
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: float = 0.0
    completed_at: Optional[float] = None

@dataclass
class WorkflowSession:
    session_id: str
    user_input: Dict
    current_step: int = 0
    status: TaskStatus = TaskStatus.PENDING
    agents_results: Dict[AgentType, Any] = None
    execution_history: List[Dict] = None
    final_result: Optional[Dict] = None
    created_at: float = 0.0
    completed_at: Optional[float] = None

class MultiAgentOrchestrator:
    """多Agent层级协调器"""
    
    def __init__(self):
        self.agents = {}
        self.active_sessions = {}
        self.workflow_steps = self._define_workflow()
        
        logger.info("MultiAgentOrchestrator with hierarchical structure initialized")
    
    def _define_workflow(self) -> List[Dict]:
        """定义层级工作流步骤"""
        return [
            {
                "step": 1,
                "name": "hierarchical_processing",
                "primary_agent": AgentType.INTENT_AGENT,
                "support_agent": AgentType.DOCAS_AGENT,
                "child_agents": [AgentType.EXECUTION_AGENT, AgentType.CHECK_AGENT],
                "description": "父agent主导，子agent协同，DocAsAgent全过程参与",
                "required": True,
                "max_iterations": 3
            }
        ]
    
    def register_agent(self, agent_type: AgentType, agent_instance):
        """注册Agent实例"""
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered {agent_type.value}")
    
    async def process_user_request(self, user_input: Dict) -> Dict:
        """处理用户请求的主入口"""
        session_id = str(uuid.uuid4())
        session = WorkflowSession(
            session_id=session_id,
            user_input=user_input,
            agents_results={},
            execution_history=[],
            created_at=time.time()
        )
        
        self.active_sessions[session_id] = session
        
        try:
            logger.info(f"开始处理用户请求，会话ID: {session_id}")
            
            # 执行层级工作流
            final_result = await self._execute_hierarchical_workflow(session)
            
            session.final_result = final_result
            session.status = TaskStatus.COMPLETED
            
            return {
                "session_id": session_id,
                "success": True,
                "result": final_result,
                "execution_summary": self._generate_execution_summary(session)
            }
            
        except Exception as e:
            logger.error(f"用户请求处理失败: {e}")
            session.status = TaskStatus.FAILED
            
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e),
                "partial_results": session.agents_results
            }
    
    async def _execute_hierarchical_workflow(self, session: WorkflowSession) -> Dict:
        """执行层级工作流"""
        session.status = TaskStatus.IN_PROGRESS
        
        # 获取所有需要的agent
        if AgentType.INTENT_AGENT not in self.agents:
            raise ValueError("IntentAgent (父agent) not registered")
        if AgentType.DOCAS_AGENT not in self.agents:
            raise ValueError("DocAsAgent (全流程参与agent) not registered")
        if AgentType.EXECUTION_AGENT not in self.agents:
            raise ValueError("ExecutionAgent (子agent) not registered")
        if AgentType.CHECK_AGENT not in self.agents:
            raise ValueError("CheckAgent (子agent) not registered")
        
        intent_agent = self.agents[AgentType.INTENT_AGENT]
        docas_agent = self.agents[AgentType.DOCAS_AGENT]
        execution_agent = self.agents[AgentType.EXECUTION_AGENT]
        check_agent = self.agents[AgentType.CHECK_AGENT]
        
        try:
            # 1. DocAsAgent全过程参与 - 意图理解阶段
            logger.info("DocAsAgent参与意图理解阶段")
            from ..docas_agent.agent_core import Task
            docas_intent_task = Task(
                task_id=f"docas_intent_{session.session_id}",
                task_type="intent_analysis",
                input_data={
                    "content": session.user_input.get("content", ""),
                    "content_type": session.user_input.get("type", "text")
                }
            )
            docas_intent_result = await docas_agent.process_task(docas_intent_task)
            
            # 2. 父agent(IntentAgent)主导意图理解，结合DocAsAgent的分析
            logger.info("父agent(IntentAgent)主导意图理解")
            user_intent = await intent_agent.understand_intent(session.user_input)
            
            # 合并DocAsAgent的洞察
            enhanced_intent = {
                "intent_type": user_intent.intent_type.value,
                "confidence": user_intent.confidence,
                "entities": {**user_intent.entities, **docas_intent_result.get("entities", {})},
                "user_requirements": {**user_intent.user_requirements, **docas_intent_result.get("requirements", {})},
                "context": {**user_intent.context, "docas_insights": docas_intent_result}
            }
            session.agents_results[AgentType.INTENT_AGENT] = enhanced_intent
            
            # 3. DocAsAgent全过程参与 - 推荐生成阶段
            logger.info("DocAsAgent参与推荐生成阶段")
            docas_recommend_task = Task(
                task_id=f"docas_recommend_{session.session_id}",
                task_type="product_recommendation",
                input_data={
                    "user_intent": enhanced_intent,
                    "content": session.user_input.get("content", ""),
                    "content_type": session.user_input.get("type", "text")
                }
            )
            docas_recommend_result = await docas_agent.process_task(docas_recommend_task)
            session.agents_results[AgentType.DOCAS_AGENT] = docas_recommend_result
            
            # 4. 父agent管理子agent执行循环（最多3轮）
            logger.info("父agent管理子agent执行循环")
            execution_history = []
            final_check_result = None
            
            for iteration in range(3):
                logger.info(f"执行循环第 {iteration + 1} 轮")
                
                # 子agent1: ExecutionAgent执行操作
                execution_result = await execution_agent.execute_operation({
                    "user_intent": enhanced_intent,
                    "recommendation": docas_recommend_result,
                    "iteration": iteration + 1
                })
                
                # DocAsAgent监督执行过程
                docas_supervise_task = Task(
                    task_id=f"docas_supervise_{session.session_id}_{iteration}",
                    task_type="execution_supervision",
                    input_data={
                        "execution_result": execution_result,
                        "user_intent": enhanced_intent,
                        "recommendation": docas_recommend_result
                    }
                )
                docas_supervision = await docas_agent.process_task(docas_supervise_task)
                
                # 子agent2: CheckAgent检查满足度
                check_result = await check_agent.check_requirements({
                    "user_intent": enhanced_intent,
                    "execution_result": execution_result,
                    "docas_supervision": docas_supervision
                })
                
                # 记录本轮执行历史
                execution_history.append({
                    "iteration": iteration + 1,
                    "execution_result": execution_result,
                    "check_result": {
                        "satisfaction_level": check_result.satisfaction_level.value,
                        "satisfaction_score": check_result.satisfaction_score,
                        "missing_requirements": check_result.missing_requirements,
                        "improvement_suggestions": check_result.improvement_suggestions
                    },
                    "docas_supervision": docas_supervision
                })
                
                final_check_result = check_result
                
                # 如果满足度足够高，提前结束循环
                if check_result.satisfaction_score >= 0.8:
                    logger.info(f"满足度达标({check_result.satisfaction_score})，提前结束循环")
                    break
            
            session.execution_history = execution_history
            session.agents_results[AgentType.EXECUTION_AGENT] = execution_history[-1]["execution_result"] if execution_history else {}
            session.agents_results[AgentType.CHECK_AGENT] = final_check_result.__dict__ if final_check_result else {}
            
            # 生成最终结果
            return self._compile_hierarchical_result(session)
            
        except Exception as e:
            logger.error(f"层级工作流执行失败: {e}")
            return {
                "execution_results": {"error": str(e)},
                "check_results": {"error": str(e)},
                "execution_history": [],
                "total_iterations": 0
            }
    
    def _compile_hierarchical_result(self, session: WorkflowSession) -> Dict:
        """编译层级架构最终结果"""
        intent_result = session.agents_results.get(AgentType.INTENT_AGENT, {})
        docas_result = session.agents_results.get(AgentType.DOCAS_AGENT, {})
        execution_result = session.agents_results.get(AgentType.EXECUTION_AGENT, {})
        check_result = session.agents_results.get(AgentType.CHECK_AGENT, {})
        
        # 提取推荐文本
        recommendation_text = "抱歉，无法生成推荐"
        if docas_result and docas_result.get("success"):
            recommendation_text = docas_result.get("result", {}).get("recommendation", recommendation_text)
        
        # 提取执行状态
        execution_success = execution_result.get("success", False) if execution_result else False
        
        # 提取最终检查状态
        if session.execution_history:
            final_check = session.execution_history[-1]["check_result"]
            satisfaction_level = final_check["satisfaction_level"]
            satisfaction_score = final_check["satisfaction_score"]
        else:
            satisfaction_level = "unknown"
            satisfaction_score = 0.0
        
        return {
            "recommendation": recommendation_text,
            "execution_status": {
                "success": execution_success,
                "satisfaction_level": satisfaction_level,
                "satisfaction_score": satisfaction_score,
                "execution_history": session.execution_history
            },
            "user_intent_summary": {
                "intent_type": intent_result.get("intent_type", "unknown"),
                "confidence": intent_result.get("confidence", 0.0),
                "enhanced_by_docas": "docas_insights" in intent_result.get("context", {})
            },
            "process_summary": {
                "architecture": "hierarchical",
                "parent_agent": "IntentAgent",
                "child_agents": ["ExecutionAgent", "CheckAgent"],
                "full_process_agent": "DocAsAgent",
                "total_iterations": len(session.execution_history),
                "workflow_completed": True
            }
        }
    
    def _generate_execution_summary(self, session: WorkflowSession) -> Dict:
        """生成层级架构执行摘要"""
        return {
            "session_id": session.session_id,
            "architecture": "hierarchical",
            "parent_agent": "IntentAgent",
            "child_agents": ["ExecutionAgent", "CheckAgent"],
            "full_process_agent": "DocAsAgent",
            "total_iterations": len(session.execution_history),
            "execution_time": (session.completed_at or time.time()) - session.created_at,
            "status": session.status.value
        }
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """获取会话状态"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return {
            "session_id": session_id,
            "architecture": "hierarchical",
            "status": session.status.value,
            "parent_agent": "IntentAgent",
            "child_agents": ["ExecutionAgent", "CheckAgent"],
            "full_process_agent": "DocAsAgent",
            "execution_history": session.execution_history,
            "agents_results": {k.value: v for k, v in session.agents_results.items()}
        }

# 对外接口保持不变
async def create_orchestrator() -> MultiAgentOrchestrator:
    """创建多Agent层级协调器"""
    return MultiAgentOrchestrator()

async def setup_complete_system() -> Dict[str, Any]:
    """设置完整的层级多Agent系统"""
    orchestrator = await create_orchestrator()
    
    # 导入和创建各个Agent
    try:
        from ..intent_agent.camel_intent_agent import create_intent_agent
        from ..docas_agent.agent_core import create_docas_agent
        from ..execution_agent.camel_execution_agent import create_execution_agent
        from ..check_agent.requirement_check_agent import create_requirement_check_agent
        
        # 创建Agent实例
        intent_agent = await create_intent_agent()
        docas_agent = await create_docas_agent()
        execution_agent = await create_execution_agent()
        check_agent = await create_requirement_check_agent()
        
        # 注册Agent（保持层级关系）
        orchestrator.register_agent(AgentType.INTENT_AGENT, intent_agent)
        orchestrator.register_agent(AgentType.DOCAS_AGENT, docas_agent)
        orchestrator.register_agent(AgentType.EXECUTION_AGENT, execution_agent)
        orchestrator.register_agent(AgentType.CHECK_AGENT, check_agent)
        
        return {
            "orchestrator": orchestrator,
            "agents": {
                "parent_agent": intent_agent,
                "full_process_agent": docas_agent,
                "child_agents": {
                    "execution_agent": execution_agent,
                    "check_agent": check_agent
                }
            },
            "status": "ready",
            "architecture": "hierarchical"
        }
        
    except ImportError as e:
        logger.error(f"Failed to import agents: {e}")
        return {
            "orchestrator": orchestrator,
            "agents": {},
            "status": "incomplete",
            "error": str(e),
            "architecture": "hierarchical"
        }

if __name__ == "__main__":
    # 测试代码保持不变
    async def test_orchestrator():
        # 设置完整系统
        system = await setup_complete_system()
        
        if system["status"] != "ready":
            print(f"系统设置失败: {system.get('error')}")
            return
        
        orchestrator = system["orchestrator"]
        
        # 测试用户请求
        user_request = {
            "type": "text",
            "content": "我家新房装修，厨房8平米，预算3000元左右，希望噪音小一些，需要安装服务",
            "metadata": {"source": "chat"}
        }
        
        # 处理请求
        result = await orchestrator.process_user_request(user_request)
        
        print("多Agent层级协作结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 注意：实际运行需要设置相关API Key
    # asyncio.run(test_orchestrator())