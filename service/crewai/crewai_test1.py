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
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
# llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

class StartupIdeationCrew:
    def __init__(self, business_direction, max_iterations=3):
        self.business_direction = business_direction
        self.max_iterations = max_iterations
        self.ideation_agent = Agent(
            role="川普的支持者",
            goal="提出支持川普的理由",
            backstory=dedent("""
                你是一个美国公民，你是川普的脑残粉，你需要提出支持川普的理由，并且否定拜登的支持者提出的支持理由
            """),
            llm=llm
        )

        self.critic_agent = Agent(
            role="拜登的支持者",
            goal="提出支持拜登的理由",
            backstory=dedent("""
                你是一位美国公民，你是拜登的脑残粉，你需要提出支持拜登的理由，并且否定川普的支持者提出的支持理由
            """),
            llm=llm
        )

    def create_trump_support_task(self, previous_arguments=None):
        context = "让我们开始新一轮的政治辩论" if not previous_arguments else f"针对拜登支持者的观点进行反驳：\n{previous_arguments}"
        return Task(
            description=dedent(f"""
                {context}
                
                请从以下几个方面支持川普：
                1. 经济政策成就
                2. 外交政策亮点
                3. 移民政策立场
                4. 对美国的贡献
                
                注意：
                - 要用充满激情的语气
                - 可以使用川普标志性的表达方式
                - 要针对性反驳拜登支持者的论点（如果有的话）
                - 最后喊出你的口号
            """),
            agent=self.ideation_agent,
            expected_output="一段充满激情的川普支持演说,不要太啰嗦，要简洁明了"
        )

    def create_biden_support_task(self, trump_arguments):
        return Task(
            description=dedent(f"""
                请反驳以下川普支持者的言论：
                {trump_arguments}
                
                从以下维度进行抨击和反驳：
                1. 驳斥川普支持者的经济观点
                2. 批评川普的外交政策
                3. 指出移民政策的问题
                4. 强调拜登的政绩
                
                注意：
                - 要用理性但不失力度的语气
                - 要具体引用数据和事实
                - 针对性反驳每个论点
                - 展现民主党的价值观
            """),
            agent=self.critic_agent,
            expected_output="一份有理有据的反驳陈述,不要太啰嗦，要简洁明了"
        )

    def run_iteration(self):
        output_content = []
        current_trump_arguments = None
        current_biden_arguments = None
        
        for iteration in range(self.max_iterations):
            output_content.append(f"\n## 辩论回合 {iteration + 1}")
            print(f"\n=== 辩论回合 {iteration + 1} ===")
            
            # 川普支持者发言
            trump_task = self.create_trump_support_task(current_biden_arguments)
            crew = Crew(agents=[self.ideation_agent], tasks=[trump_task])
            current_trump_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 川普支持者发言\n{current_trump_arguments}")
            print(f"\n川普支持者：\n{current_trump_arguments}")
            
            # 拜登支持者反驳
            biden_task = self.create_biden_support_task(current_trump_arguments)
            crew = Crew(agents=[self.critic_agent], tasks=[biden_task])
            current_biden_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 拜登支持者反驳\n{current_biden_arguments}")
            print(f"\n拜登支持者：\n{current_biden_arguments}")
        
        output_content.append("\n## 辩论结束")
        print("\n=== 辩论结束 ===")
        return {
            "final_trump": current_trump_arguments,
            "final_biden": current_biden_arguments,
            "rounds": self.max_iterations,
            "output_content": output_content
        }

def save_to_markdown(result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"political_debate_{timestamp}.md"
    
    md_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "md")
    os.makedirs(md_dir, exist_ok=True)
    
    filepath = os.path.join(md_dir, filename)
    
    content = [
        f"# 特朗普vs拜登支持者辩论\n",
        f"## 辩论回合数\n{result['rounds']}\n"
    ]
    
    content.extend(result['output_content'])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath

if __name__ == "__main__":
    crew = StartupIdeationCrew(business_direction="政治辩论", max_iterations=3)
    result = crew.run_iteration()
    
    output_file = save_to_markdown(result)
    
    print("\n=== 辩论总结 ===")
    print(f"辩论回合: {result['rounds']}")
    print(f"最后的辩论内容已保存到: {output_file}")
