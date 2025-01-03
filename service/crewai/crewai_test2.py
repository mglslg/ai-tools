import warnings
import logging
import os
from datetime import datetime

# 禁用 OpenTelemetry 警告
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)

from crewai import Agent, Task, Crew
from textwrap import dedent
from langchain_openai import ChatOpenAI

# 配置 LLM
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

class InvestmentStrategyCrew:
    def __init__(self, business_direction, max_iterations=3):
        self.business_direction = business_direction
        self.max_iterations = max_iterations
        self.hs300_agent = Agent(
            role="沪深300支持者",
            goal="提出支持定投沪深300的理由",
            backstory=dedent("""
                你是一位专业的投资顾问，坚定支持定投沪深300指数。你认为沪深300是追踪中国大盘股最好的指数，
                具有优秀的流动性和较好的代表性。你需要用专业的视角来分析沪深300的优势。
            """),
            llm=llm
        )

        self.a50_agent = Agent(
            role="上证A50支持者",
            goal="提出支持定投上证A50的理由",
            backstory=dedent("""
                你是一位资深的基金经理，坚定支持定投上证A50指数。你认为上证A50代表了中国最优质的蓝筹股，
                是分享中国经济增长的最佳选择。你需要用专业的视角来分析上证A50的优势。
            """),
            llm=llm
        )

    def create_hs300_task(self, previous_arguments=None):
        context = "让我们开始新一轮的投资策略辩论" if not previous_arguments else f"针对上证A50支持者的观点进行反驳：\n{previous_arguments}"
        return Task(
            description=dedent(f"""
                {context}
                
                请从以下几个方面支持沪深300：
                1. 指数特点和优势
                2. 历史表现分析
                3. 估值水平
                4. 风险收益特征
                
                注意：
                - 要用专业的语气
                - 要使用具体的数据支持
                - 要针对性反驳A50支持者的论点（如果有的话）
                - 说明为什么沪深300更适合定投
            """),
            agent=self.hs300_agent,
            expected_output="一段专业的沪深300投资分析,不要太啰嗦，要简洁明了"
        )

    def create_a50_task(self, hs300_arguments):
        return Task(
            description=dedent(f"""
                请反驳以下沪深300支持者的言论：
                {hs300_arguments}
                
                从以下维度进行分析和反驳：
                1. A50指数的特色和优势
                2. A50的历史业绩表现
                3. 当前投资价值
                4. 相比沪深300的独特优势
                
                注意：
                - 要用专业严谨的语气
                - 要具体引用数据和事实
                - 针对性反驳每个论点
                - 强调A50适合定投的原因
            """),
            agent=self.a50_agent,
            expected_output="一份专业的上证A50投资分析,不要太啰嗦，要简洁明了"
        )

    def run_iteration(self):
        output_content = []
        current_hs300_arguments = None
        current_a50_arguments = None
        
        for iteration in range(self.max_iterations):
            output_content.append(f"\n## 辩论回合 {iteration + 1}")
            print(f"\n=== 辩论回合 {iteration + 1} ===")
            
            # 沪深300支持者发言
            hs300_task = self.create_hs300_task(current_a50_arguments)
            crew = Crew(agents=[self.hs300_agent], tasks=[hs300_task])
            current_hs300_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 沪深300支持者发言\n{current_hs300_arguments}")
            print(f"\n沪深300支持者：\n{current_hs300_arguments}")
            
            # 上证A50支持者反驳
            a50_task = self.create_a50_task(current_hs300_arguments)
            crew = Crew(agents=[self.a50_agent], tasks=[a50_task])
            current_a50_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 上证A50支持者反驳\n{current_a50_arguments}")
            print(f"\n上证A50支持者：\n{current_a50_arguments}")
        
        output_content.append("\n## 辩论结束")
        print("\n=== 辩论结束 ===")
        return {
            "final_hs300": current_hs300_arguments,
            "final_a50": current_a50_arguments,
            "rounds": self.max_iterations,
            "output_content": output_content
        }

def save_to_markdown(result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"investment_debate_{timestamp}.md"
    
    md_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "md")
    os.makedirs(md_dir, exist_ok=True)
    
    filepath = os.path.join(md_dir, filename)
    
    content = [
        f"# 沪深300 vs 上证A50 定投策略辩论\n",
        f"## 辩论回合数\n{result['rounds']}\n"
    ]
    
    content.extend(result['output_content'])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath

if __name__ == "__main__":
    crew = InvestmentStrategyCrew(business_direction="投资策略辩论", max_iterations=3)
    result = crew.run_iteration()
    
    output_file = save_to_markdown(result)
    
    print("\n=== 辩论总结 ===")
    print(f"辩论回合: {result['rounds']}")
    print(f"最后的辩论内容已保存到: {output_file}")
