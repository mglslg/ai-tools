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
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

class HogwartsDebateCrew:
    def __init__(self, max_iterations=3):
        self.max_iterations = max_iterations
        self.snape = Agent(
            role="西弗勒斯·斯内普教授",
            goal="用刻薄和讽刺的言语激怒麦格教授",
            backstory=dedent("""
                你是霍格沃茨魔药学教授西弗勒斯·斯内普，一个性格阴郁、刻薄、傲慢的人。
                你经常用尖酸刻薄的言语讽刺他人，特别喜欢挑衅格兰芬多学院的院长麦格教授。
                你说话总是带着冷嘲热讽，语气低沉而充满讥讽。记住你只能说一句话！
            """),
            llm=llm
        )

        self.mcgonagall = Agent(
            role="米勒娃·麦格教授",
            goal="反击斯内普的挑衅，维护自己和格兰芬多的尊严",
            backstory=dedent("""
                你是霍格沃茨变形术教授米勒娃·麦格，格兰芬多学院的院长。
                你性格正直、刚强，极具正义感，同时也很有智慧和幽默感。
                当斯内普挑衅时，你会用机智而犀利的方式予以回击。记住你只能说一句话！
            """),
            llm=llm
        )

        self.dumbledore = Agent(
            role="阿不思·邓布利多校长",
            goal="用智慧和幽默化解斯内普与麦格之间的争执",
            backstory=dedent("""
                你是霍格沃茨的校长阿不思·邓布利多，最伟大的白巫师。
                你极其睿智，总是用幽默和智慧化解矛盾。你说话常常带着神秘感和俏皮话，
                喜欢用一些看似无关但实则意味深长的话来调解争端。记住你只能说一句话！
            """),
            llm=llm
        )

    def create_snape_task(self, previous_arguments=None):
        context = "让我们开始新一轮的争执" if not previous_arguments else f"针对麦格教授的反驳：\n{previous_arguments}"
        return Task(
            description=dedent(f"""
                {context}
                
                作为斯内普教授，你现在正站在走廊里，看着哈利波特带领格兰芬多拿到了魁地奇冠军。
                你内心充满了不屑，想要对麦格教授说些尖酸刻薄的话。你可以提到她对波特的偏袒，或是质疑
                她的教学方式，用你惯有的冷嘲热讽的语气说出你的想法。记住，你说话要优雅但刻薄，要高傲
                但不失风度。记住你只能说一句话！
            """),
            agent=self.snape,
            expected_output="一段自然的讽刺性对话"
        )

    def create_mcgonagall_task(self, snape_arguments):
        return Task(
            description=dedent(f"""
                斯内普教授刚刚说了这番话：
                {snape_arguments}
                
                作为麦格教授，你听到这些刻薄的言论感到很不愉快。你想要维护自己的尊严和格兰芬多的
                荣誉。用你特有的机智和幽默，回击斯内普的挑衅。你可以指出他的偏见，或是对他的教学
                方式提出质疑。记住保持优雅和理性，但不要示弱。记住你只能说一句话！
            """),
            agent=self.mcgonagall,
            expected_output="一段自然的反击对话"
        )

    def create_dumbledore_task(self, debate_context):
        return Task(
            description=dedent(f"""
                你刚刚听到了这段争执：
                {debate_context}
                
                作为邓布利多校长，你看到两位得力助手又在争执，想要用你特有的智慧和幽默来化解这个
                局面。你可以讲个看似无关但实则意味深长的小故事，或是突然提到你最近发现的新口味柠檬
                雪宝。用你那标志性的温和语气，让两位教授意识到团结的重要性。记住你只能说一句话！
            """),
            agent=self.dumbledore,
            expected_output="一段充满智慧的调解对话"
        )

    def run_iteration(self):
        output_content = []
        current_snape_arguments = None
        current_mcgonagall_arguments = None
        
        for iteration in range(self.max_iterations):
            output_content.append(f"\n## 争执回合 {iteration + 1}")
            print(f"\n=== 争执回合 {iteration + 1} ===")
            
            # 斯内普发言
            snape_task = self.create_snape_task(current_mcgonagall_arguments)
            crew = Crew(agents=[self.snape], tasks=[snape_task])
            current_snape_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 斯内普教授说道\n{current_snape_arguments}")
            print(f"\n斯内普教授：\n{current_snape_arguments}")
            
            # 麦格教授反击
            mcgonagall_task = self.create_mcgonagall_task(current_snape_arguments)
            crew = Crew(agents=[self.mcgonagall], tasks=[mcgonagall_task])
            current_mcgonagall_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 麦格教授回击\n{current_mcgonagall_arguments}")
            print(f"\n麦格教授：\n{current_mcgonagall_arguments}")

            # 邓布利多调解
            debate_context = f"斯内普说：{current_snape_arguments}\n\n麦格说：{current_mcgonagall_arguments}"
            dumbledore_task = self.create_dumbledore_task(debate_context)
            crew = Crew(agents=[self.dumbledore], tasks=[dumbledore_task])
            current_dumbledore_arguments = str(crew.kickoff())
            
            output_content.append(f"\n### 邓布利多校长说道\n{current_dumbledore_arguments}")
            print(f"\n邓布利多校长：\n{current_dumbledore_arguments}")
        
        output_content.append("\n## 争执结束")
        print("\n=== 争执结束 ===")
        return {
            "final_snape": current_snape_arguments,
            "final_mcgonagall": current_mcgonagall_arguments,
            "final_dumbledore": current_dumbledore_arguments,
            "rounds": self.max_iterations,
            "output_content": output_content
        }

def save_to_markdown(result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hogwarts_debate_{timestamp}.md"
    
    md_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "md")
    os.makedirs(md_dir, exist_ok=True)
    
    filepath = os.path.join(md_dir, filename)
    
    content = [
        f"# 霍格沃茨教授争执实录\n",
        f"## 争执回合数\n{result['rounds']}\n"
    ]
    
    content.extend(result['output_content'])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath

if __name__ == "__main__":
    crew = HogwartsDebateCrew(max_iterations=5)
    result = crew.run_iteration()
    
    output_file = save_to_markdown(result)
    
    print("\n=== 争执总结 ===")
    print(f"争执回合: {result['rounds']}")
    print(f"争执记录已保存到: {output_file}")
