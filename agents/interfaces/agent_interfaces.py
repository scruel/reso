"""
完善DocAsAgent与其他Agent的接口
提供标准化的接口和数据转换功能
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import time

logger = logging.getLogger(__name__)

class DataFormat(Enum):
    """数据格式枚举"""
    CAMEL_FORMAT = "camel_format"
    DOCAS_FORMAT = "docas_format"
    EXECUTION_FORMAT = "execution_format"
    CHECK_FORMAT = "check_format"
    STANDARD_FORMAT = "standard_format"

@dataclass
class StandardAgentInput:
    """标准化Agent输入格式"""
    input_id: str
    input_type: str  # "text", "voice", "document", "url"
    content: Any
    metadata: Dict[str, Any]
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class StandardAgentOutput:
    """标准化Agent输出格式"""
    output_id: str
    agent_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0.0
    confidence: float = 0.0
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

class AgentDataTransformer:
    """Agent数据转换器"""
    
    @staticmethod
    def to_standard_input(data: Any, input_type: str, metadata: Dict = None) -> StandardAgentInput:
        """转换为标准输入格式"""
        import uuid
        
        return StandardAgentInput(
            input_id=str(uuid.uuid4()),
            input_type=input_type,
            content=data,
            metadata=metadata or {}
        )
    
    @staticmethod
    def from_intent_agent_result(result: Any) -> StandardAgentOutput:
        """从意图Agent结果转换"""
        import uuid
        
        if hasattr(result, 'intent_type'):
            # 处理IntentAgent的UserIntent对象
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="intent_agent",
                success=True,
                data={
                    "intent_type": result.intent_type.value,
                    "confidence": result.confidence,
                    "entities": result.entities,
                    "user_requirements": result.user_requirements,
                    "context": result.context
                },
                confidence=result.confidence
            )
        else:
            # 处理字典格式结果
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="intent_agent",
                success=result.get("success", True),
                data=result,
                confidence=result.get("confidence", 0.0)
            )
    
    @staticmethod
    def to_docas_agent_input(intent_result: StandardAgentOutput, user_input: StandardAgentInput) -> Dict:
        """转换为DocAsAgent输入格式"""
        from ..docas_agent.agent_core import Task
        
        return Task(
            task_id=f"docas_{int(time.time())}",
            task_type="product_recommendation",
            input_data={
                "user_intent": intent_result.data,
                "content": user_input.content,
                "content_type": user_input.input_type,
                "metadata": user_input.metadata
            }
        )
    
    @staticmethod
    def from_docas_agent_result(result: Dict) -> StandardAgentOutput:
        """从DocAsAgent结果转换"""
        import uuid
        
        return StandardAgentOutput(
            output_id=str(uuid.uuid4()),
            agent_id="docas_agent",
            success=result.get("success", False),
            data=result,
            error=result.get("error"),
            confidence=result.get("result", {}).get("confidence", 0.0) if result.get("success") else 0.0
        )
    
    @staticmethod
    def to_execution_agent_input(intent_result: StandardAgentOutput, docas_result: StandardAgentOutput) -> Dict:
        """转换为执行Agent输入格式"""
        return {
            "user_intent": intent_result.data,
            "recommendation_result": docas_result.data,
            "context": {
                "intent_confidence": intent_result.confidence,
                "recommendation_confidence": docas_result.confidence
            }
        }
    
    @staticmethod
    def from_execution_agent_result(result: Any) -> StandardAgentOutput:
        """从执行Agent结果转换"""
        import uuid
        
        if hasattr(result, 'success'):
            # ExecutionResult对象
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="execution_agent",
                success=result.success,
                data={
                    "action_type": result.action_type.value,
                    "result_data": result.result_data,
                    "execution_time": result.execution_time
                },
                error=result.error_message,
                processing_time=result.execution_time
            )
        else:
            # 字典格式
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="execution_agent",
                success=result.get("success", False),
                data=result,
                error=result.get("error")
            )
    
    @staticmethod
    def to_check_agent_input(intent_result: StandardAgentOutput, execution_result: StandardAgentOutput) -> Dict:
        """转换为检查Agent输入格式"""
        return {
            "user_intent": intent_result.data,
            "execution_result": execution_result.data,
            "context": {
                "intent_confidence": intent_result.confidence,
                "execution_success": execution_result.success
            }
        }
    
    @staticmethod
    def from_check_agent_result(result: Any) -> StandardAgentOutput:
        """从检查Agent结果转换"""
        import uuid
        
        if hasattr(result, 'satisfaction_level'):
            # CheckResult对象
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="check_agent",
                success=True,
                data={
                    "satisfaction_level": result.satisfaction_level.value,
                    "satisfaction_score": result.satisfaction_score,
                    "missing_requirements": result.missing_requirements,
                    "improvement_suggestions": result.improvement_suggestions,
                    "next_action_needed": result.next_action_needed
                },
                confidence=result.confidence
            )
        else:
            # 字典格式
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="check_agent",
                success=result.get("success", True),
                data=result,
                confidence=result.get("confidence", 0.0)
            )

class DocAsAgentInterface:
    """DocAsAgent标准接口"""
    
    def __init__(self, docas_agent):
        self.docas_agent = docas_agent
        self.transformer = AgentDataTransformer()
    
    async def process_user_request(self, user_input: StandardAgentInput, intent_result: StandardAgentOutput) -> StandardAgentOutput:
        """处理用户请求的标准接口"""
        try:
            # 转换输入格式
            docas_task = self.transformer.to_docas_agent_input(intent_result, user_input)
            
            # 调用DocAsAgent
            result = await self.docas_agent.process_task(docas_task)
            
            # 转换输出格式
            return self.transformer.from_docas_agent_result(result)
            
        except Exception as e:
            logger.error(f"DocAsAgent interface error: {e}")
            import uuid
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="docas_agent",
                success=False,
                error=str(e)
            )
    
    async def get_recommendation_only(self, user_input: StandardAgentInput) -> StandardAgentOutput:
        """仅获取推荐，不进行完整流程"""
        try:
            from ..docas_agent.agent_core import Task
            
            # 创建简化任务
            task = Task(
                task_id=f"simple_rec_{int(time.time())}",
                task_type="simple_recommendation",
                input_data={
                    "content": user_input.content,
                    "content_type": user_input.input_type,
                    "metadata": user_input.metadata
                }
            )
            
            result = await self.docas_agent.process_task(task)
            return self.transformer.from_docas_agent_result(result)
            
        except Exception as e:
            logger.error(f"Simple recommendation error: {e}")
            import uuid
            return StandardAgentOutput(
                output_id=str(uuid.uuid4()),
                agent_id="docas_agent",
                success=False,
                error=str(e)
            )

class IntegratedAgentPipeline:
    """集成的Agent管道"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.docas_interface = None
        self.transformer = AgentDataTransformer()
        
        # 性能监控
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_processing_time": 0.0,
            "agent_performance": {}
        }
    
    async def initialize(self):
        """初始化管道"""
        # 创建DocAsAgent接口
        docas_agent = self.orchestrator.agents.get("docas_agent")
        if docas_agent:
            self.docas_interface = DocAsAgentInterface(docas_agent)
        
        logger.info("Integrated agent pipeline initialized")
    
    async def process_complete_workflow(self, user_input: Union[str, Dict]) -> Dict:
        """处理完整工作流"""
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1
        
        try:
            # 1. 标准化输入
            if isinstance(user_input, str):
                std_input = self.transformer.to_standard_input(user_input, "text")
            else:
                std_input = self.transformer.to_standard_input(
                    user_input.get("content", ""),
                    user_input.get("type", "text"),
                    user_input.get("metadata", {})
                )
            
            # 2. 意图理解
            intent_agent = self.orchestrator.agents.get("intent_agent")
            if not intent_agent:
                raise Exception("Intent agent not available")
            
            intent_raw_result = await intent_agent.understand_intent({
                "type": std_input.input_type,
                "content": std_input.content,
                "metadata": std_input.metadata
            })
            intent_result = self.transformer.from_intent_agent_result(intent_raw_result)
            
            # 3. 推荐生成
            if not self.docas_interface:
                raise Exception("DocAs interface not available")
            
            docas_result = await self.docas_interface.process_user_request(std_input, intent_result)
            
            # 4. 执行和检查循环
            execution_agent = self.orchestrator.agents.get("execution_agent")
            check_agent = self.orchestrator.agents.get("check_agent")
            
            if execution_agent and check_agent:
                # 使用检查Agent的迭代功能
                final_check_result, execution_history = await check_agent.iterative_check_and_guide(
                    intent_result.data, execution_agent, max_iterations=3
                )
                
                final_execution_result = self.transformer.from_execution_agent_result(
                    execution_history[-1]["execution_result"] if execution_history else {}
                )
                final_check_output = self.transformer.from_check_agent_result(final_check_result)
            else:
                final_execution_result = StandardAgentOutput(
                    output_id="no_execution",
                    agent_id="execution_agent",
                    success=False,
                    error="Execution agent not available"
                )
                final_check_output = StandardAgentOutput(
                    output_id="no_check",
                    agent_id="check_agent", 
                    success=False,
                    error="Check agent not available"
                )
            
            # 5. 编译最终结果
            processing_time = time.time() - start_time
            final_result = self._compile_final_result(
                std_input, intent_result, docas_result, 
                final_execution_result, final_check_output, processing_time
            )
            
            # 更新性能指标
            self.performance_metrics["successful_requests"] += 1
            self._update_performance_metrics(processing_time)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Complete workflow failed: {e}")
            processing_time = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "timestamp": time.time()
            }
    
    def _compile_final_result(self, user_input: StandardAgentInput,
                            intent_result: StandardAgentOutput,
                            docas_result: StandardAgentOutput,
                            execution_result: StandardAgentOutput,
                            check_result: StandardAgentOutput,
                            processing_time: float) -> Dict:
        """编译最终结果"""
        
        # 提取推荐文本
        recommendation = "暂无推荐"
        if docas_result.success and docas_result.data.get("result"):
            recommendation = docas_result.data["result"].get("recommendation", recommendation)
        
        # 提取执行信息
        execution_info = {
            "success": execution_result.success,
            "error": execution_result.error
        }
        if execution_result.success:
            execution_info.update(execution_result.data)
        
        # 提取检查信息
        satisfaction_info = {
            "level": "unknown",
            "score": 0.0,
            "next_action_needed": True
        }
        if check_result.success:
            satisfaction_info = {
                "level": check_result.data.get("satisfaction_level", "unknown"),
                "score": check_result.data.get("satisfaction_score", 0.0),
                "missing_requirements": check_result.data.get("missing_requirements", []),
                "improvement_suggestions": check_result.data.get("improvement_suggestions", []),
                "next_action_needed": check_result.data.get("next_action_needed", True)
            }
        
        return {
            "success": True,
            "user_input": {
                "type": user_input.input_type,
                "content": user_input.content
            },
            "results": {
                "recommendation": recommendation,
                "intent_understanding": {
                    "intent_type": intent_result.data.get("intent_type", "unknown"),
                    "confidence": intent_result.confidence,
                    "entities": intent_result.data.get("entities", {})
                },
                "execution": execution_info,
                "satisfaction": satisfaction_info
            },
            "performance": {
                "processing_time": processing_time,
                "agent_responses": {
                    "intent_agent": intent_result.success,
                    "docas_agent": docas_result.success,
                    "execution_agent": execution_result.success,
                    "check_agent": check_result.success
                }
            },
            "timestamp": time.time()
        }
    
    def _update_performance_metrics(self, processing_time: float):
        """更新性能指标"""
        current_avg = self.performance_metrics["average_processing_time"]
        total_requests = self.performance_metrics["total_requests"]
        
        # 计算新的平均处理时间
        new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        self.performance_metrics["average_processing_time"] = new_avg
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        total_requests = self.performance_metrics["total_requests"]
        successful_requests = self.performance_metrics["successful_requests"]
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0.0,
            "average_processing_time": self.performance_metrics["average_processing_time"],
            "agent_performance": self.performance_metrics["agent_performance"]
        }

# 对外接口
async def create_integrated_pipeline(orchestrator) -> IntegratedAgentPipeline:
    """创建集成管道"""
    pipeline = IntegratedAgentPipeline(orchestrator)
    await pipeline.initialize()
    return pipeline

if __name__ == "__main__":
    # 测试代码
    async def test_interface():
        print("Agent interface testing")
        
        # 测试数据转换器
        transformer = AgentDataTransformer()
        
        # 测试标准输入
        std_input = transformer.to_standard_input(
            "我想买个油烟机",
            "text",
            {"source": "test"}
        )
        
        print(f"Standard input: {asdict(std_input)}")
    
    asyncio.run(test_interface())