"""
Enhanced Multi-Agent Orchestrator
增强版多代理协调器

集成新设计的AI agents：
1. EnhancedIntentRefiner - 意图精化代理
2. AdvancedWeaviateAgent - 商品获取代理

支持两种集成模式：
- 扩展模式：新agent作为现有流程的增强
- 独立模式：新agent作为独立服务使用
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import time
import uuid

# 导入现有orchestrator
from .multi_agent_orchestrator import (
    MultiAgentOrchestrator, AgentType, TaskStatus, 
    WorkflowSession, AgentTask
)

# 导入新设计的agents
try:
    from ..intent_refine_agent.enhanced_intent_refiner import EnhancedIntentRefiner
    from ..get_goods_agent.advanced_weaviate_agent import AdvancedWeaviateAgent
    NEW_AGENTS_AVAILABLE = True
except ImportError:
    NEW_AGENTS_AVAILABLE = False
    print("New agents not available")

logger = logging.getLogger(__name__)

# 扩展AgentType枚举
class ExtendedAgentType(Enum):
    """扩展的Agent类型"""
    # 原有agents
    INTENT_AGENT = "intent_agent"
    DOCAS_AGENT = "docas_agent" 
    EXECUTION_AGENT = "execution_agent"
    CHECK_AGENT = "check_agent"
    
    # 新增agents
    INTENT_REFINER = "intent_refiner"  # 意图精化代理
    GOODS_RETRIEVER = "goods_retriever"  # 商品获取代理

@dataclass
class EnhancedWorkflowSession:
    """增强版工作流会话"""
    session_id: str
    user_input: Dict
    current_step: int = 0
    status: TaskStatus = TaskStatus.PENDING
    agents_results: Dict[ExtendedAgentType, Any] = None
    execution_history: List[Dict] = None
    final_result: Optional[Dict] = None
    created_at: float = 0.0
    completed_at: Optional[float] = None
    
    # 新增字段
    conversation_history: List[Dict[str, str]] = None
    intent_evolution: List[Dict] = None  # 意图演化历史
    mode: str = "enhanced"  # enhanced, legacy, hybrid
    
    def __post_init__(self):
        if self.agents_results is None:
            self.agents_results = {}
        if self.execution_history is None:
            self.execution_history = []
        if self.conversation_history is None:
            self.conversation_history = []
        if self.intent_evolution is None:
            self.intent_evolution = []

class EnhancedMultiAgentOrchestrator(MultiAgentOrchestrator):
    """增强版多代理协调器"""
    
    def __init__(self, mode: str = "enhanced"):
        """
        初始化增强版协调器
        
        Args:
            mode: 运行模式
                - enhanced: 使用新agents增强现有流程
                - legacy: 只使用原有agents
                - hybrid: 动态选择使用方式
        """
        super().__init__()
        self.mode = mode
        self.new_agents = {}
        self.enhanced_workflow_steps = self._define_enhanced_workflow()
        
        logger.info(f"EnhancedMultiAgentOrchestrator initialized in {mode} mode")
    
    def _define_enhanced_workflow(self) -> List[Dict]:
        """定义增强版工作流"""
        return [
            {
                "step": 1,
                "name": "intent_understanding_and_refinement",
                "primary_agent": ExtendedAgentType.INTENT_AGENT,
                "enhancement_agent": ExtendedAgentType.INTENT_REFINER,
                "description": "意图理解 + 增量精化",
                "required": True
            },
            {
                "step": 2, 
                "name": "product_retrieval_and_recommendation",
                "primary_agent": ExtendedAgentType.DOCAS_AGENT,
                "enhancement_agent": ExtendedAgentType.GOODS_RETRIEVER,
                "description": "商品检索 + 专业推荐",
                "required": True
            },
            {
                "step": 3,
                "name": "execution_and_verification",
                "child_agents": [ExtendedAgentType.EXECUTION_AGENT, ExtendedAgentType.CHECK_AGENT],
                "description": "执行操作 + 质量验证",
                "required": True
            }
        ]
    
    def register_new_agent(self, agent_type: ExtendedAgentType, agent_instance):
        """注册新的Agent实例"""
        if agent_type in [ExtendedAgentType.INTENT_REFINER, ExtendedAgentType.GOODS_RETRIEVER]:
            self.new_agents[agent_type] = agent_instance
            logger.info(f"Registered new agent: {agent_type.value}")
        else:
            # 使用父类方法注册原有agents
            super().register_agent(AgentType(agent_type.value), agent_instance)
    
    async def process_enhanced_request(
        self, 
        user_input: Dict,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        existing_intent: Optional[Dict] = None
    ) -> Dict:
        """
        处理增强版用户请求
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            existing_intent: 现有意图（用于增量更新）
            
        Returns:
            Dict: 处理结果
        """
        session_id = str(uuid.uuid4())
        session = EnhancedWorkflowSession(
            session_id=session_id,
            user_input=user_input,
            conversation_history=conversation_history or [],
            agents_results={},
            execution_history=[],
            created_at=time.time(),
            mode=self.mode
        )
        
        self.active_sessions[session_id] = session
        
        try:
            logger.info(f"开始增强版处理，会话ID: {session_id}, 模式: {self.mode}")
            
            if self.mode == "enhanced":
                final_result = await self._execute_enhanced_workflow(session, existing_intent)
            elif self.mode == "hybrid":
                final_result = await self._execute_hybrid_workflow(session, existing_intent)
            else:  # legacy
                final_result = await self._execute_hierarchical_workflow(session)
            
            session.final_result = final_result
            session.status = TaskStatus.COMPLETED
            
            return {
                "session_id": session_id,
                "success": True,
                "result": final_result,
                "mode": self.mode,
                "intent_evolution": session.intent_evolution,
                "execution_summary": self._generate_enhanced_summary(session)
            }
            
        except Exception as e:
            logger.error(f"增强版请求处理失败: {e}")
            session.status = TaskStatus.FAILED
            
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e),
                "mode": self.mode,
                "partial_results": session.agents_results
            }
    
    async def _execute_enhanced_workflow(
        self, 
        session: EnhancedWorkflowSession,
        existing_intent: Optional[Dict] = None
    ) -> Dict:
        """执行增强版工作流"""
        
        session.status = TaskStatus.IN_PROGRESS
        
        # Step 1: 意图理解 + 增量精化
        enhanced_intent = await self._step1_enhanced_intent_processing(
            session, existing_intent
        )
        
        # Step 2: 商品检索 + 专业推荐  
        enhanced_products = await self._step2_enhanced_product_retrieval(
            session, enhanced_intent
        )
        
        # Step 3: 执行操作 + 质量验证
        final_result = await self._step3_execution_and_verification(
            session, enhanced_intent, enhanced_products
        )
        
        return final_result
    
    async def _step1_enhanced_intent_processing(
        self,
        session: EnhancedWorkflowSession,
        existing_intent: Optional[Dict] = None
    ) -> Dict:
        """Step 1: 增强版意图处理"""
        
        logger.info("Step 1: 增强版意图理解 + 精化")
        
        # 1.1 原有IntentAgent处理
        if ExtendedAgentType.INTENT_AGENT in self.agents:
            intent_agent = self.agents[ExtendedAgentType.INTENT_AGENT]
            base_intent = await intent_agent.understand_intent(session.user_input)
            
            session.agents_results[ExtendedAgentType.INTENT_AGENT] = {
                "intent_type": base_intent.intent_type.value,
                "confidence": base_intent.confidence,
                "entities": base_intent.entities,
                "user_requirements": base_intent.user_requirements
            }
        
        # 1.2 新增IntentRefiner增强处理
        enhanced_intent = None
        if ExtendedAgentType.INTENT_REFINER in self.new_agents and existing_intent:
            refiner = self.new_agents[ExtendedAgentType.INTENT_REFINER]
            
            refine_result = await refiner.refine_intent_incremental(
                session_id=session.session_id,
                existing_intent=existing_intent,
                conversation_history=session.conversation_history
            )
            
            enhanced_intent = refine_result.intent
            session.agents_results[ExtendedAgentType.INTENT_REFINER] = {
                "refined_intent": enhanced_intent,
                "analysis": refine_result.analysis,
                "message": refine_result.message
            }
            
            # 记录意图演化
            session.intent_evolution.append({
                "step": "intent_refinement",
                "original": existing_intent,
                "refined": enhanced_intent,
                "changes": {
                    "new_positive": refine_result.analysis.new_positive_attrs,
                    "new_negative": refine_result.analysis.new_negative_attrs
                }
            })
        
        # 合并意图信息
        if enhanced_intent:
            final_intent = enhanced_intent
        else:
            # 如果没有existing_intent，使用base_intent生成初始意图
            base_result = session.agents_results.get(ExtendedAgentType.INTENT_AGENT, {})
            final_intent = {
                "title": "商品查询",  # 默认标题
                "attrs": list(base_result.get("entities", {}).keys())
            }
        
        logger.info(f"Step 1 完成，最终意图: {final_intent}")
        return final_intent
    
    async def _step2_enhanced_product_retrieval(
        self,
        session: EnhancedWorkflowSession,
        enhanced_intent: Dict
    ) -> Dict:
        """Step 2: 增强版商品检索"""
        
        logger.info("Step 2: 增强版商品检索 + 推荐")
        
        # 2.1 原有DocAsAgent处理
        docas_result = None
        if ExtendedAgentType.DOCAS_AGENT in self.agents:
            docas_agent = self.agents[ExtendedAgentType.DOCAS_AGENT]
            
            # 构建DocAsAgent的任务
            from ..docas_agent.agent_core import Task
            docas_task = Task(
                task_id=f"docas_recommend_{session.session_id}",
                task_type="product_recommendation",
                input_data={
                    "user_intent": enhanced_intent,
                    "conversation_history": session.conversation_history
                }
            )
            
            docas_result = await docas_agent.process_task(docas_task)
            session.agents_results[ExtendedAgentType.DOCAS_AGENT] = docas_result
        
        # 2.2 新增GoodsRetriever专业处理
        goods_result = None
        if ExtendedAgentType.GOODS_RETRIEVER in self.new_agents:
            retriever = self.new_agents[ExtendedAgentType.GOODS_RETRIEVER]
            
            # 提取subcategory
            subcategory = self._extract_subcategory(enhanced_intent)
            
            goods_result = await retriever.process_complete_workflow(
                conversation_history=session.conversation_history,
                current_category=subcategory,
                limit=20
            )
            
            session.agents_results[ExtendedAgentType.GOODS_RETRIEVER] = {
                "intent": goods_result.intent,
                "message": goods_result.message,
                "debug_info": goods_result.debug_info
            }
        
        # 合并检索结果
        combined_result = {
            "enhanced_intent": enhanced_intent,
            "docas_recommendations": docas_result,
            "goods_retrieval": goods_result,
            "retrieval_strategy": "hybrid" if (docas_result and goods_result) else "single"
        }
        
        logger.info(f"Step 2 完成，检索策略: {combined_result['retrieval_strategy']}")
        return combined_result
    
    async def _step3_execution_and_verification(
        self,
        session: EnhancedWorkflowSession,
        enhanced_intent: Dict,
        enhanced_products: Dict
    ) -> Dict:
        """Step 3: 执行操作 + 质量验证"""
        
        logger.info("Step 3: 执行操作 + 质量验证")
        
        # 使用原有的execution和check流程
        execution_result = None
        check_result = None
        
        if ExtendedAgentType.EXECUTION_AGENT in self.agents:
            execution_agent = self.agents[ExtendedAgentType.EXECUTION_AGENT]
            execution_result = await execution_agent.execute_operation({
                "user_intent": enhanced_intent,
                "recommendations": enhanced_products,
                "session_id": session.session_id
            })
            session.agents_results[ExtendedAgentType.EXECUTION_AGENT] = execution_result
        
        if ExtendedAgentType.CHECK_AGENT in self.agents:
            check_agent = self.agents[ExtendedAgentType.CHECK_AGENT]
            check_result = await check_agent.check_requirements({
                "user_intent": enhanced_intent,
                "execution_result": execution_result,
                "products": enhanced_products
            })
            session.agents_results[ExtendedAgentType.CHECK_AGENT] = {
                "satisfaction_level": check_result.satisfaction_level.value,
                "satisfaction_score": check_result.satisfaction_score,
                "missing_requirements": check_result.missing_requirements
            }
        
        # 编译最终结果
        final_result = {
            "status": "success",
            "enhanced_intent": enhanced_intent,
            "products": enhanced_products,
            "execution": execution_result,
            "verification": session.agents_results.get(ExtendedAgentType.CHECK_AGENT, {}),
            "workflow_mode": "enhanced",
            "agents_used": list(session.agents_results.keys())
        }
        
        logger.info("Step 3 完成，增强版工作流执行成功")
        return final_result
    
    async def _execute_hybrid_workflow(
        self, 
        session: EnhancedWorkflowSession,
        existing_intent: Optional[Dict] = None
    ) -> Dict:
        """执行混合工作流（智能选择使用新旧agents）"""
        
        # 简单策略：如果有existing_intent就使用enhanced模式，否则使用legacy模式
        if existing_intent and session.conversation_history:
            logger.info("Hybrid模式：选择enhanced workflow")
            return await self._execute_enhanced_workflow(session, existing_intent)
        else:
            logger.info("Hybrid模式：选择legacy workflow")
            return await self._execute_hierarchical_workflow(session)
    
    def _extract_subcategory(self, intent: Dict) -> Optional[str]:
        """从意图中提取子类目"""
        title = intent.get("title", "")
        attrs = intent.get("attrs", [])
        
        # 简单的类目映射
        category_mapping = {
            "笔记本": "笔记本电脑",
            "电脑": "笔记本电脑", 
            "手机": "智能手机",
            "洗衣机": "家用洗衣机"
        }
        
        for keyword, category in category_mapping.items():
            if keyword in title or any(keyword in attr for attr in attrs):
                return category
        
        return None
    
    def _generate_enhanced_summary(self, session: EnhancedWorkflowSession) -> Dict:
        """生成增强版执行摘要"""
        
        summary = {
            "session_id": session.session_id,
            "mode": session.mode,
            "total_steps": len(session.execution_history),
            "agents_involved": list(session.agents_results.keys()),
            "intent_evolution_count": len(session.intent_evolution),
            "processing_time": session.completed_at - session.created_at if session.completed_at else None,
            "status": session.status.value
        }
        
        # 新agents的使用情况
        new_agents_used = []
        if ExtendedAgentType.INTENT_REFINER in session.agents_results:
            new_agents_used.append("IntentRefiner")
        if ExtendedAgentType.GOODS_RETRIEVER in session.agents_results:
            new_agents_used.append("GoodsRetriever")
        
        summary["new_agents_used"] = new_agents_used
        summary["enhancement_level"] = len(new_agents_used)
        
        return summary

# 便捷函数
async def create_enhanced_orchestrator(mode: str = "enhanced") -> EnhancedMultiAgentOrchestrator:
    """创建增强版协调器"""
    
    orchestrator = EnhancedMultiAgentOrchestrator(mode=mode)
    
    # 注册原有agents（如果可用）
    try:
        from ..intent_agent.camel_intent_agent import create_intent_agent
        from ..docas_agent.agent_core import create_docas_agent
        from ..execution_agent.camel_execution_agent import create_execution_agent
        from ..check_agent.requirement_check_agent import create_requirement_check_agent
        
        intent_agent = await create_intent_agent()
        docas_agent = await create_docas_agent() 
        execution_agent = await create_execution_agent()
        check_agent = await create_requirement_check_agent()
        
        orchestrator.register_new_agent(ExtendedAgentType.INTENT_AGENT, intent_agent)
        orchestrator.register_new_agent(ExtendedAgentType.DOCAS_AGENT, docas_agent)
        orchestrator.register_new_agent(ExtendedAgentType.EXECUTION_AGENT, execution_agent)
        orchestrator.register_new_agent(ExtendedAgentType.CHECK_AGENT, check_agent)
        
        logger.info("原有agents注册成功")
        
    except ImportError as e:
        logger.warning(f"部分原有agents注册失败: {e}")
    
    # 注册新agents（如果可用）
    if NEW_AGENTS_AVAILABLE:
        try:
            intent_refiner = EnhancedIntentRefiner(use_ai=True)
            goods_retriever = AdvancedWeaviateAgent(use_ai=True)
            
            orchestrator.register_new_agent(ExtendedAgentType.INTENT_REFINER, intent_refiner)
            orchestrator.register_new_agent(ExtendedAgentType.GOODS_RETRIEVER, goods_retriever)
            
            logger.info("新agents注册成功")
            
        except Exception as e:
            logger.warning(f"新agents注册失败: {e}")
    
    return orchestrator

async def process_with_new_agents(
    user_input: Dict,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    existing_intent: Optional[Dict] = None,
    mode: str = "enhanced"
) -> Dict:
    """
    使用新agents处理请求的便捷函数
    
    Args:
        user_input: 用户输入
        conversation_history: 对话历史
        existing_intent: 现有意图
        mode: 处理模式
        
    Returns:
        Dict: 处理结果
    """
    orchestrator = await create_enhanced_orchestrator(mode)
    
    return await orchestrator.process_enhanced_request(
        user_input, conversation_history, existing_intent
    ) 