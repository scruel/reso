"""
DocAsAgent
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import time

logger = logging.getLogger(__name__)

class AgentState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    REASONING = "reasoning"
    FINISHED = "finished"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Agent间通信消息格式"""
    agent_id: str
    message_type: str
    content: Dict
    timestamp: float
    correlation_id: str

@dataclass
class Task:
    """Agent任务定义"""
    task_id: str
    task_type: str
    input_data: Dict
    priority: int = 1
    max_steps: int = 10
    timeout: float = 300.0

@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    parameters: Dict
    result: Any
    success: bool
    timestamp: float

@dataclass
class ReasoningStep:
    """推理步骤记录"""
    step_id: int
    observation: str
    thought: str
    action: str
    action_input: Dict
    result: Any
    timestamp: float

class AgentMemory:
    """Agent记忆系统"""
    
    def __init__(self):
        self.short_term = []  # 对话历史
        self.long_term = {}   # 持久化知识
        self.working_memory = {}  # 当前任务的工作记忆
        self.tool_calls = []  # 工具调用历史
        self.reasoning_chain = []  # 推理链
    
    def add_reasoning_step(self, step: ReasoningStep):
        """添加推理步骤"""
        self.reasoning_chain.append(step)
        # 保持推理链长度限制
        if len(self.reasoning_chain) > 20:
            self.reasoning_chain = self.reasoning_chain[-15:]
    
    def update_working_memory(self, key: str, value: Any):
        """更新工作记忆"""
        self.working_memory[key] = value
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        context = []
        
        # 当前任务状态
        if self.working_memory:
            context.append(f"当前任务状态: {json.dumps(self.working_memory, ensure_ascii=False)}")
        
        # 最近的推理链
        if self.reasoning_chain:
            recent_steps = self.reasoning_chain[-3:]
            context.append("最近推理步骤:")
            for step in recent_steps:
                context.append(f"  - {step.thought} -> {step.action}")
        
        return "\n".join(context)

class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name: str, tool_func, description: str):
        """注册工具"""
        self.tools[name] = {
            "function": tool_func,
            "description": description
        }
    
    async def call_tool(self, name: str, parameters: Dict) -> ToolCall:
        """调用工具"""
        if name not in self.tools:
            return ToolCall(
                tool_name=name,
                parameters=parameters,
                result=None,
                success=False,
                timestamp=time.time()
            )
        
        try:
            tool_func = self.tools[name]["function"]
            result = await tool_func(**parameters)
            return ToolCall(
                tool_name=name,
                parameters=parameters,
                result=result,
                success=True,
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}")
            return ToolCall(
                tool_name=name,
                parameters=parameters,
                result=str(e),
                success=False,
                timestamp=time.time()
            )

class DocAsAgent:
    """文档理解和商品推荐Agent"""
    
    def __init__(self, agent_id: str = "docas_agent"):
        self.agent_id = agent_id
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.tools = ToolRegistry()
        self.minimax_client = None
        
        # 注册可用工具
        self._register_tools()
        
        logger.info(f"DocAsAgent {agent_id} initialized")
    
    def _register_tools(self):
        """注册Agent可用的工具"""
        self.tools.register_tool(
            "parse_content",
            self._tool_parse_content,
            "解析文档、链接或文本内容"
        )
        
        self.tools.register_tool(
            "search_products",
            self._tool_search_products,
            "在商品数据库中搜索匹配的产品"
        )
        
        self.tools.register_tool(
            "calculate_similarity",
            self._tool_calculate_similarity,
            "计算产品与用户需求的相似度"
        )
        
        self.tools.register_tool(
            "generate_recommendation_text",
            self._tool_generate_recommendation,
            "生成个性化推荐语"
        )
    
    async def process_task(self, task: Task) -> Dict:
        """处理任务的主入口 - ReAct循环"""
        self.state = AgentState.PLANNING
        self.memory.update_working_memory("current_task", task.task_id)
        self.memory.update_working_memory("task_type", task.task_type)
        
        try:
            # Phase 1: Planning - 制定执行计划
            plan = await self._planning_phase(task)
            self.memory.update_working_memory("execution_plan", plan)
            
            # Phase 2: ReAct执行循环
            result = await self._react_execution_loop(task, plan)
            
            self.state = AgentState.FINISHED
            return {
                "success": True,
                "result": result,
                "reasoning_chain": [asdict(step) for step in self.memory.reasoning_chain],
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            self.state = AgentState.ERROR
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _planning_phase(self, task: Task) -> List[Dict]:
        """规划阶段 - 制定执行计划"""
        self.state = AgentState.PLANNING
        
        planning_prompt = f"""
        你是DocAsAgent，专门处理文档理解和商品推荐任务。
        
        任务类型: {task.task_type}
        输入数据: {json.dumps(task.input_data, ensure_ascii=False)}
        
        请制定执行计划，分解为具体步骤。可用工具:
        - parse_content: 解析内容
        - search_products: 搜索商品
        - calculate_similarity: 计算相似度
        - generate_recommendation_text: 生成推荐语
        
        返回JSON格式的执行计划:
        [
            {{"step": 1, "action": "parse_content", "goal": "解析用户输入内容"}},
            {{"step": 2, "action": "search_products", "goal": "搜索匹配商品"}},
            ...
        ]
        """
        
        if self.minimax_client:
            response = await self.minimax_client.generate_plan(planning_prompt)
            return response.get("plan", [])
        else:
            # Fallback计划
            return [
                {"step": 1, "action": "parse_content", "goal": "解析用户输入内容"},
                {"step": 2, "action": "search_products", "goal": "搜索匹配商品"},
                {"step": 3, "action": "calculate_similarity", "goal": "计算产品匹配度"},
                {"step": 4, "action": "generate_recommendation_text", "goal": "生成推荐语"}
            ]
    
    async def _react_execution_loop(self, task: Task, plan: List[Dict]) -> Dict:
        """ReAct执行循环：Reasoning + Acting"""
        self.state = AgentState.EXECUTING
        
        for step_num in range(1, task.max_steps + 1):
            # Observation: 观察当前状态
            observation = self._get_current_observation()
            
            # Reasoning: 推理下一步行动
            thought, action, action_input = await self._reasoning_step(
                step_num, observation, plan
            )
            
            # Acting: 执行行动
            action_result = await self._execute_action(action, action_input)
            
            # 记录推理步骤
            reasoning_step = ReasoningStep(
                step_id=step_num,
                observation=observation,
                thought=thought,
                action=action,
                action_input=action_input,
                result=action_result,
                timestamp=time.time()
            )
            self.memory.add_reasoning_step(reasoning_step)
            
            # 判断是否完成任务
            if self._is_task_complete(action_result):
                return action_result
        
        # 如果达到最大步数仍未完成
        return {"error": "Task execution exceeded maximum steps"}
    
    async def _reasoning_step(self, step_num: int, observation: str, plan: List[Dict]) -> tuple:
        """推理步骤"""
        self.state = AgentState.REASONING
        
        context = self.memory.get_context_summary()
        
        reasoning_prompt = f"""
        你是DocAsAgent，正在执行第{step_num}步。
        
        当前观察: {observation}
        
        执行计划: {json.dumps(plan, ensure_ascii=False)}
        
        上下文: {context}
        
        请推理下一步应该执行什么行动。
        
        返回JSON格式:
        {{
            "thought": "推理过程",
            "action": "工具名称", 
            "action_input": {{"参数": "值"}}
        }}
        """
        
        if self.minimax_client:
            response = await self.minimax_client.reasoning(reasoning_prompt)
            return (
                response.get("thought", ""),
                response.get("action", ""),
                response.get("action_input", {})
            )
        else:
            # Fallback推理逻辑
            return self._fallback_reasoning(step_num, plan)
    
    async def _execute_action(self, action: str, action_input: Dict) -> Any:
        """执行行动"""
        tool_call = await self.tools.call_tool(action, action_input)
        self.memory.tool_calls.append(tool_call)
        
        if tool_call.success:
            return tool_call.result
        else:
            return {"error": f"Tool execution failed: {tool_call.result}"}
    
    def _get_current_observation(self) -> str:
        """获取当前观察状态"""
        observations = []
        
        # 工作记忆状态
        if self.memory.working_memory:
            observations.append(f"工作记忆: {json.dumps(self.memory.working_memory, ensure_ascii=False)}")
        
        # 最近的工具调用结果
        if self.memory.tool_calls:
            recent_call = self.memory.tool_calls[-1]
            observations.append(f"上次工具调用: {recent_call.tool_name} -> {'成功' if recent_call.success else '失败'}")
        
        return "; ".join(observations) if observations else "开始执行任务"
    
    def _is_task_complete(self, result: Any) -> bool:
        """判断任务是否完成"""
        if isinstance(result, dict):
            # 如果结果包含推荐文本，认为任务完成
            return "recommendation" in result or "text" in result
        return False
    
    def _fallback_reasoning(self, step_num: int, plan: List[Dict]) -> tuple:
        """Fallback推理逻辑"""
        if step_num <= len(plan):
            current_step = plan[step_num - 1]
            return (
                f"执行计划第{step_num}步: {current_step['goal']}",
                current_step["action"],
                {}
            )
        else:
            return ("任务完成", "finish", {})
    
    # 工具实现
    async def _tool_parse_content(self, content: str, content_type: str = "text") -> Dict:
        """解析内容工具"""
        from .content_parser import ContentParser
        parser = ContentParser()
        
        if content_type == "text":
            parsed = parser._parse_text_content(content)
        elif content_type == "url":
            parsed = await parser.parse_url(content)
        else:
            parsed = await parser.parse_document(content)
        
        # 提取需求信息
        requirements = parser.extract_keywords(parsed)
        
        self.memory.update_working_memory("parsed_content", parsed)
        self.memory.update_working_memory("requirements", requirements)
        
        return {"parsed_content": parsed, "requirements": requirements}
    
    async def _tool_search_products(self, requirements: Dict = None) -> Dict:
        """搜索商品工具"""
        from .mock_database import MockProductDatabase
        
        if not requirements:
            requirements = self.memory.working_memory.get("requirements", {})
        
        db = MockProductDatabase()
        all_products = db.get_all_products()
        
        # 简单过滤逻辑
        filtered_products = all_products[:5]  # 返回前5个产品
        
        self.memory.update_working_memory("candidate_products", filtered_products)
        
        return {"products": [
            {
                "id": p.id, "brand": p.brand, "model": p.model,
                "price": p.price, "features": p.features
            } for p in filtered_products
        ]}
    
    async def _tool_calculate_similarity(self, products: List = None, requirements: Dict = None) -> Dict:
        """计算相似度工具"""
        if not products:
            products = self.memory.working_memory.get("candidate_products", [])
        if not requirements:
            requirements = self.memory.working_memory.get("requirements", {})
        
        # 简化的相似度计算
        scored_products = []
        for i, product in enumerate(products[:3]):
            score = 0.8 - i * 0.1  # 简单的递减分数
            scored_products.append({
                "product": product,
                "similarity_score": score,
                "match_reasons": ["价格匹配", "功能匹配"]
            })
        
        self.memory.update_working_memory("matched_products", scored_products)
        
        return {"matched_products": scored_products}
    
    async def _tool_generate_recommendation(self, matched_products: List = None, requirements: Dict = None) -> Dict:
        """生成推荐语工具"""
        if not matched_products:
            matched_products = self.memory.working_memory.get("matched_products", [])
        if not requirements:
            requirements = self.memory.working_memory.get("requirements", {})
        
        if matched_products:
            top_product = matched_products[0]["product"]
            recommendation = f"为您推荐{top_product.brand} {top_product.model}，价格{top_product.price}元，{', '.join(top_product.features[:2])}！"
        else:
            recommendation = "抱歉，暂未找到合适的商品推荐。"
        
        # 序列化产品对象为字典，解决JSON序列化问题
        serialized_products = []
        for match in matched_products:
            product_dict = {
                "brand": match["product"].brand,
                "model": match["product"].model,
                "price": match["product"].price,
                "features": match["product"].features,
                "kitchen_size": match["product"].kitchen_size,
                "score": match["score"]
            }
            serialized_products.append(product_dict)
        
        result = {
            "recommendation": recommendation,
            "confidence": 0.85,
            "matched_products": serialized_products,
            "reasoning": "基于需求匹配度生成推荐"
        }
        
        self.memory.update_working_memory("final_result", result)
        
        return result
    
    def set_minimax_client(self, client):
        """设置MiniMax客户端"""
        self.minimax_client = client
    
    async def generate_product_highlight(self, product: Dict, user_requirements: Dict = None) -> str:
        """
        DocAsAgent核心功能1: 生成产品亮点总结
        用一句话总结产品的核心亮点，突出与用户需求的匹配点
        """
        try:
            # 提取产品信息
            brand = product.get('brand', '')
            model = product.get('model', '')
            price = product.get('price', 0)
            features = product.get('features', [])
            kitchen_size = product.get('kitchen_size', '')
            
            # 分析用户需求重点
            highlight_points = []
            
            if user_requirements:
                # 根据用户需求突出相应特点
                required_features = user_requirements.get('priority_features', [])
                budget = user_requirements.get('budget', 0)
                
                # 功能匹配亮点
                for feature in required_features:
                    if feature in features:
                        highlight_points.append(f"✨{feature}")
                
                # 价格优势
                if budget and price <= budget:
                    if price <= budget * 0.8:
                        highlight_points.append("💰超值价格")
                    else:
                        highlight_points.append("💰价格合适")
            
            # 产品独特亮点
            premium_features = ['智能控制', '自清洁', '变频', '免拆洗']
            for feature in premium_features:
                if feature in features:
                    highlight_points.append(f"🚀{feature}")
            
            # 生成亮点总结
            if highlight_points:
                highlight_text = " ".join(highlight_points[:3])  # 最多3个亮点
                return f"💫 {brand} {model} - {highlight_text}，{price}元超值之选！"
            else:
                return f"💫 {brand} {model} - 品质可靠，{price}元性价比之选！"
                
        except Exception as e:
            logger.error(f"Product highlight generation error: {e}")
            return f"💫 推荐产品 - 品质优选！"
    
    async def parse_user_content(self, content: str, content_type: str = "text") -> Dict:
        """
        DocAsAgent核心功能2: 解析用户上传的文档/链接内容
        提取关键信息供主AI agent进行意图分析
        """
        try:
            result = {
                "content_type": content_type,
                "extracted_info": {},
                "user_intent_hints": [],
                "processing_status": "success"
            }
            
            if content_type == "url":
                # 处理链接内容
                from .content_parser import ContentParser
                parser = ContentParser()
                parsed_result = await parser.parse_url(content)
                
                if parsed_result.get("type") == "product":
                    result["extracted_info"] = {
                        "mentioned_products": parsed_result.get("product_info", []),
                        "price_mentions": parsed_result.get("prices", []),
                        "features_mentioned": parsed_result.get("features", [])
                    }
                    result["user_intent_hints"] = ["product_research", "price_comparison"]
                
            elif content_type == "document":
                # 处理文档内容
                from .content_parser import ContentParser
                parser = ContentParser()
                parsed_result = await parser.parse_document(content)
                
                # 提取装修/家居相关信息
                keywords = self._extract_home_keywords(content)
                result["extracted_info"] = {
                    "home_context": keywords,
                    "requirements_mentioned": self._extract_requirements(content),
                    "budget_hints": self._extract_budget_info(content)
                }
                result["user_intent_hints"] = ["home_renovation", "product_planning"]
                
            else:
                # 处理普通文本
                result["extracted_info"] = {
                    "key_phrases": self._extract_key_phrases(content),
                    "intent_keywords": self._extract_intent_keywords(content)
                }
                result["user_intent_hints"] = ["text_inquiry"]
            
            return result
            
        except Exception as e:
            logger.error(f"Content parsing error: {e}")
            return {
                "content_type": content_type,
                "extracted_info": {},
                "user_intent_hints": ["parsing_error"],
                "processing_status": "failed",
                "error": str(e)
            }
    
    def _extract_home_keywords(self, text: str) -> List[str]:
        """提取家居/装修相关关键词"""
        home_keywords = [
            "厨房", "客厅", "卧室", "装修", "新房", "老房", "改造",
            "平米", "户型", "风格", "现代", "简约", "中式", "欧式"
        ]
        found_keywords = []
        for keyword in home_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        return found_keywords
    
    def _extract_requirements(self, text: str) -> List[str]:
        """提取需求相关信息"""
        requirement_patterns = [
            r"(需要|要求|希望)([^，。！？]*)",
            r"(预算|价格).*?(\d+)",
            r"(静音|大吸力|易清洁|智能|自清洁)"
        ]
        requirements = []
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text)
            requirements.extend([match[0] if isinstance(match, tuple) else match for match in matches])
        return requirements
    
    def _extract_budget_info(self, text: str) -> List[int]:
        """提取预算信息"""
        budget_pattern = r"(\d+)\s*元?"
        matches = re.findall(budget_pattern, text)
        return [int(match) for match in matches if int(match) > 100]  # 过滤掉太小的数字
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键短语"""
        # 简单的关键词提取
        keywords = ["油烟机", "抽油烟机", "方太", "老板", "华帝", "美的", "西门子"]
        found_phrases = []
        for keyword in keywords:
            if keyword in text:
                found_phrases.append(keyword)
        return found_phrases
    
    def _extract_intent_keywords(self, text: str) -> List[str]:
        """提取意图关键词"""
        intent_words = {
            "购买": ["买", "购买", "下单", "要"],
            "咨询": ["咨询", "问", "了解", "知道"],
            "比较": ["对比", "比较", "哪个好", "区别"],
            "投诉": ["投诉", "问题", "故障", "坏了"]
        }
        found_intents = []
        for intent, words in intent_words.items():
            for word in words:
                if word in text:
                    found_intents.append(intent)
                    break
        return found_intents

# 对外接口
async def create_docas_agent(agent_id: str = "docas_agent") -> DocAsAgent:
    """创建DocAsAgent实例"""
    return DocAsAgent(agent_id)

if __name__ == "__main__":
    # 测试代码
    async def test_docas_agent():
        agent = await create_docas_agent()
        
        task = Task(
            task_id="test_001",
            task_type="product_recommendation",
            input_data={
                "content": "我家新房装修，厨房8平米，预算3000元左右，希望噪音小一些",
                "content_type": "text"
            }
        )
        
        result = await agent.process_task(task)
        print("Agent执行结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    asyncio.run(test_docas_agent())