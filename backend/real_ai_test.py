#!/usr/bin/env python3
"""
AI Agents系统的交互式测试

"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agents.orchestrator.multi_agent_orchestrator import MultiAgentOrchestrator
from agents.recorder_agent.camel_behavior_recorder import BehaviorRecorderAgent

class RealAITester:
    def __init__(self):
        self.orchestrator = None
        self.behavior_recorder = None
        self.session_id = f"real_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def initialize_system(self):
        """强制初始化真实AI系统"""
        print("🚀 正在初始化真实AI Agents系统...")
        try:
            # 1. 创建协调器
            self.orchestrator = MultiAgentOrchestrator()
            
            # 2. 创建并注册所有Agent
            print("📝 正在创建Agent实例...")
            
            # IntentAgent
            from agents.intent_agent.camel_intent_agent import create_intent_agent
            from agents.orchestrator.multi_agent_orchestrator import AgentType
            intent_agent = await create_intent_agent()
            self.orchestrator.register_agent(AgentType.INTENT_AGENT, intent_agent)
            print("   ✅ IntentAgent 已注册")
            
            # DocAsAgent  
            from agents.docas_agent.agent_core import create_docas_agent
            docas_agent = await create_docas_agent()
            self.orchestrator.register_agent(AgentType.DOCAS_AGENT, docas_agent)
            print("   ✅ DocAsAgent 已注册")
            
            # ExecutionAgent
            from agents.execution_agent.camel_execution_agent import ExecutionAgent
            execution_agent = ExecutionAgent()
            self.orchestrator.register_agent(AgentType.EXECUTION_AGENT, execution_agent)
            print("   ✅ ExecutionAgent 已注册")
            
            # CheckAgent
            from agents.check_agent.requirement_check_agent import RequirementCheckAgent
            check_agent = RequirementCheckAgent()
            self.orchestrator.register_agent(AgentType.CHECK_AGENT, check_agent)
            print("   ✅ CheckAgent 已注册")
            
            # BehaviorRecorderAgent
            self.behavior_recorder = BehaviorRecorderAgent()
            print("   ✅ BehaviorRecorderAgent 已创建")
            
            print("✅ 真实AI系统初始化完成")
            print("🤖 所有Agents已激活:")
            print("   - IntentAgent: 理解用户意图")
            print("   - ExecutionAgent: 执行推荐逻辑") 
            print("   - CheckAgent: 验证推荐质量")
            print("   - DocAsAgent: 文档分析")
            print("   - BehaviorRecorderAgent: 记录用户行为")
            return True
        except Exception as e:
            print(f"❌ 真实AI系统初始化失败: {e}")
            print("💡 请检查以下配置:")
            print("   1. .env文件中是否配置了API密钥")
            print("   2. 网络连接是否正常")
            print("   3. 依赖包是否安装完整")
            import traceback
            traceback.print_exc()
            return False
    
    async def start_interactive_session(self):
        """开始强制真实AI交互"""
        print("\n" + "="*60)
        print("🎯 Reso")
        print("="*60)
        print("💡 系统特点:")
        print("   ✅ 使用真实AI模型分析")
        print("   ✅ 多Agent协作决策")
        print("   ✅ 智能语义理解")
        print("   ✅ 个性化推荐")
        print("\n📝 输入提示：")
        print("   - 详细描述您的需求")
        print("   - 输入 'exit' 退出")
        print("   - 输入 'help' 查看示例")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n👤 请输入您的需求: ").strip()
                
                if user_input.lower() == 'exit':
                    await self.show_summary()
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif not user_input:
                    continue
                
                await self.process_user_request(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用！")
                break
            except Exception as e:
                print(f"❌ 处理请求时出错: {e}")
    
    async def process_user_request(self, user_input: str):
        """使用真实AI处理用户请求"""
        print(f"\n🔍 AI正在分析您的需求: {user_input}")
        
        # 记录用户输入
        await self.record_user_input(user_input)
        
        # 强制使用真实AI处理
        user_request = {
            "content": user_input,
            "type": "text",
            "session_id": self.session_id
        }
        result = await self.orchestrator.process_user_request(user_request)
        
        if result.get("status") == "success":
            await self.display_results(result)
            await self.record_recommendations(result)
        else:
            print(f"⚠️  AI处理失败: {result.get('error', '未知错误')}")
            print("   请检查网络连接或API配置")
    
    async def record_user_input(self, user_input: str):
        """记录用户输入"""
        try:
            await self.behavior_recorder.record_interaction({
                "type": "user_input",
                "session_id": self.session_id,
                "user_id": "real_ai_user",
                "content": {"text": user_input},
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"⚠️  行为记录失败: {e}")
    
    async def record_recommendations(self, result: Dict):
        """记录AI推荐结果"""
        try:
            await self.behavior_recorder.record_purchase_journey({
                "session_id": self.session_id,
                "user_id": "real_ai_user",
                "user_input": result.get("original_input", ""),
                "recommendations": result.get("recommendations", []),
                "selected_product": result.get("selected", {}),
                "purchase_result": {"status": "ai_recommended"}
            })
        except Exception as e:
            print(f"⚠️  推荐记录失败: {e}")
    
    async def display_results(self, result: Dict):
        """显示AI分析结果"""
        print("\n" + "🤖"*20)
        print("📊 AI智能推荐结果")
        print("🤖"*20)
        
        recommendations = result.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. 🏷️  {rec.get('name', '未知产品')}")
                print(f"   💰 价格: ¥{rec.get('price', '未知')}")
                print(f"   ⭐ AI评分: {rec.get('score', 0)}/1.0")
                print(f"   🎯 AI分析: {rec.get('match_reason', 'AI推荐理由')}")
                print(f"   📊 关键特性: {', '.join(rec.get('features', []))}")
        else:
            print("⚠️  AI暂时无法提供推荐")
    
    def show_help(self):
        """显示帮助"""
        print("\n💡 AI理解示例:")
        examples = [
            "我家厨房8平米，预算3000元，想要静音效果好点的侧吸式油烟机",
            "推荐一款适合小厨房的油烟机，预算2500-3500元，噪音要小",
            "我想要一个吸力大、易清洁的油烟机，价格3000左右",
            "厨房通风不太好，需要一款吸力强劲的油烟机"
        ]
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
    
    async def show_summary(self):
        """显示会话总结"""
        print("\n" + "="*60)
        print("📊 AI会话总结")
        print("="*60)
        print(f"🆔 会话ID: {self.session_id}")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ 本次测试使用真实AI Agents")
        print("📁 行为记录已保存到: recorded_behaviors/")

async def main():
    """主函数"""
    tester = RealAITester()
    
    if await tester.initialize_system():
        await tester.start_interactive_session()
    else:
        print("\n❌ 真实AI系统无法启动")
        print("请检查配置后重试")

if __name__ == "__main__":
    asyncio.run(main())
