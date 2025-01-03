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

class StartupIdeationCrew:
    def __init__(self, business_direction, max_iterations=3):
        self.business_direction = business_direction
        self.max_iterations = max_iterations
        self.ideation_agent = Agent(
            role="创业创新专家",
            goal="提出创新的创业想法",
            backstory=dedent("""
                你是一个经验丰富的创业专家，擅长发现市场机会和创新点。
                你需要提出具体可行的创业方案，包括目标市场、商业模式、核心价值主张等。
                在收到评估反馈后，你要针对评估的批评项进行更有针对性的改进。
            """),
            llm=llm
        )

        self.critic_agent = Agent(
            role="创业评估师",
            goal="严格评估创业想法的可行性，并对每一条你觉得不可行的地方提出尖锐的批评，注意一定要引用出具体的条款进行批评，不然无法定位你批评的具体内容",
            backstory=dedent("""
                你是一位资深创业评估专家，擅长从市场、财务、运营等多个维度分析创业项目。
                你需要以严谨的态度指出创业方案中的潜在问题和风险。
                评估维度包括：市场需求、竞争格局、盈利模式、运营难度、资金需求等。
            """),
            llm=llm
        )

    def create_ideation_task(self, previous_feedback=None):
        context = f"基于以下创业方向：{self.business_direction}\n" + ("提出具体的创业想法" if not previous_feedback else f"基于以下反馈改进创业方案:\n{previous_feedback}")
        return Task(
            description=dedent(f"""
                {context}
                
                请详细描述：
                1. 目标市场和痛点,不要写太多，主要针对反馈中的批评进行针对性的改进，并且注意要引用批评内容否则我怎么知道是针对哪一条款的改进
                2. 解决方案,主要针对反馈中的批评进行针对性的改进，并且注意要引用批评内容否则我怎么知道是针对哪一条款的改进
                3. 商业模式,主要针对反馈中的批评进行针对性的改进，并且注意要引用批评内容否则我怎么知道是针对哪一条款的改进
                4. 核心竞争优势,主要针对反馈中的批评进行针对性的改进，并且注意要引用批评内容否则我怎么知道是针对哪一条款的改进
            """),
            agent=self.ideation_agent,
            expected_output="一个详细的创业方案描述，包含市场分析、解决方案、商业模式和竞争优势"
        )

    def create_evaluation_task(self, idea):
        return Task(
            description=dedent(f"""
                评估以下创业想法：
                {idea}
                
                请从以下维度严格分析：
                1. 市场需求的真实性和规模
                2. 解决方案的可行性
                3. 商业模式的可持续性
                4. 竞争优势的持续性
                5. 潜在风险和挑战
                
                给出具体的改进建议，并对每一条你觉得不可行的地方提出尖锐的批评，注意一定要引用出具体的条款进行批评，不然无法定位你批评的具体内容。
                如果认为方案已经足够完善，请明确说明。
            """),
            agent=self.critic_agent,
            expected_output="一份详细的创业方案评估报告，包含多个维度的分析和具体改进建议，一定要考虑到创业者是一个自由开发者，以提高社区知名度也分享开源代码为目的，只对没有法律风险的盈利感兴趣，并且无法做问卷调查等市场调研，因为根本就找不到调研对象！"
        )

    def run_iteration(self):
        # 准备输出内容
        output_content = []
        current_idea = None
        previous_feedback = None
        
        for iteration in range(self.max_iterations):
            output_content.append(f"\n## 迭代 {iteration + 1}")
            print(f"\n=== 迭代 {iteration + 1} ===")
            
            # 创业想法生成或改进
            ideation_task = self.create_ideation_task(previous_feedback)
            crew = Crew(agents=[self.ideation_agent], tasks=[ideation_task])
            current_idea = str(crew.kickoff())
            
            output_content.append(f"\n### 创业想法\n{current_idea}")
            print(f"\n创业想法：\n{current_idea}")
            
            # 评估想法
            evaluation_task = self.create_evaluation_task(current_idea)
            crew = Crew(agents=[self.critic_agent], tasks=[evaluation_task])
            feedback = str(crew.kickoff())
            
            output_content.append(f"\n### 评估反馈\n{feedback}")
            print(f"\n评估反馈：\n{feedback}")
            
            # 检查是否达成共识
            if "足够完善" in feedback:
                output_content.append("\n## 已达成共识！")
                print("\n=== 已达成共识！===")
                return {
                    "final_idea": current_idea,
                    "final_evaluation": feedback,
                    "iterations": iteration + 1,
                    "output_content": output_content
                }
            
            previous_feedback = feedback
        
        output_content.append("\n## 达到最大迭代次数")
        print("\n=== 达到最大迭代次数 ===")
        return {
            "final_idea": current_idea,
            "final_evaluation": previous_feedback,
            "iterations": self.max_iterations,
            "output_content": output_content
        }

def save_to_markdown(business_direction, result):
    # 创建文件名（使用时间戳避免重复）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"startup_idea_{timestamp}.md"
    
    # 确保 md 目录存在
    md_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "md")
    os.makedirs(md_dir, exist_ok=True)
    
    filepath = os.path.join(md_dir, filename)
    
    # 准备文件内容
    content = [
        f"# 创业方案分析报告\n",
        f"## 创业方向\n{business_direction}\n",
        f"## 迭代次数\n{result['iterations']}\n"
    ]
    
    # 添加详细过程
    content.extend(result['output_content'])
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath

if __name__ == "__main__":
    # 指定创业方向
    # business_direction = "我想做一个统计自由职业者平台的数据,类似freelancer,upwork,fiverr之类的，然后统计数据，然后分析数据，然后给出建议或在自媒体上发布文章"
    business_direction = "我想做一个chrome插件，在浏览领英的时候，根据自身的简历情况给出对岗位的匹配建议，并且如果用户想要投递的话给出简历的改进建议。注意，我是一个自由职业者，我没有团队，我只是一个程序员，我负担不起高昂的创业成本，我只是希望提高自己在社区的名气，如果可以的话才考虑一些没有法律风险的盈利"
    crew = StartupIdeationCrew(business_direction=business_direction, max_iterations=3)
    result = crew.run_iteration()
    
    # 保存到 markdown 文件
    output_file = save_to_markdown(business_direction, result)
    
    print("\n=== 最终结果 ===")
    print(f"创业方向: {business_direction}")
    print(f"迭代次数: {result['iterations']}")
    print(f"最终创业想法:\n{result['final_idea']}")
    print(f"最终评估:\n{result['final_evaluation']}")
    print(f"\n结果已保存到: {output_file}")
