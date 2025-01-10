from typing import List, Dict, Optional, Any, Union
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
import pandas as pd
from pydantic import BaseModel, Field
from docx import Document
import os
import yaml
import json

class TenderInfo(BaseModel):
    """招标信息模型"""
    publish_time: str = Field(..., description="挂网时间，格式：YYYY-MM-DD")
    project_name: str = Field(..., description="完整的项目名称")
    project_period: str = Field(..., description="项目预计持续时间，单位年")
    project_target: str = Field(..., description="项目的具体内容和目标")
    project_amount: str = Field(..., description="项目标的，即项目金额，单位万元")
    business_scenario: str = Field(..., description="项目应用的具体场景，包括[国际快递][日常快递][票据传递]几种类型")
    tender_unit: str = Field(..., description="招标方的完整名称")
    register_deadline: str = Field(..., description="投标报名的最后期限，格式：YYYY-MM-DD")
    submit_deadline: str = Field(..., description="标书提交的截止时间，格式：YYYY-MM-DD")
    open_time: str = Field(..., description="开标的具体时间，格式：YYYY-MM-DD")

@CrewBase
class TenderDocumentAnalyzer:
    """招标文档分析工作组"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            # model="gpt-4o",
            temperature=0.7,
            streaming=True
        )
        self.document_content = self._read_document()
        self.config_path = os.path.join(os.path.dirname(__file__), 'config')
        self.agents_config = self._load_yaml('agents.yaml')
        self.tasks_config = self._load_yaml('tasks.yaml')
        
    def _read_document(self) -> str:
        """读取文档内容"""
        if self.file_path.endswith('.docx'):
            doc = Document(self.file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()

    def _load_yaml(self, file_name: str) -> dict:
        """加载YAML配置文件"""
        file_path = os.path.join(self.config_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @agent
    def reader_agent(self) -> Agent:
        """创建文档阅读agent"""
        config = self.agents_config['reader_agent']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,
            verbose=config['verbose']
        )

    @agent
    def analyzer_agent(self) -> Agent:
        """创建信息分析agent"""
        config = self.agents_config['analyzer_agent']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,
            verbose=config['verbose']
        )

    @task
    def read_task(self) -> Task:
        """创建阅读任务"""
        config = self.tasks_config['read_task']
        return Task(
            description=f"{config['description']}\n\n文档内容：\n{self.document_content}",
            agent=self.reader_agent(),
            expected_output=config['expected_output']
        )

    @task
    def analyze_task(self) -> Task:
        """创建分析任务"""
        config = self.tasks_config['analyze_task']
        return Task(
            description=config['description'],
            agent=self.analyzer_agent(),
            expected_output=config['expected_output'],
            context=[self.read_task()],
            output_json=TenderInfo
        )

    @crew
    def tender_crew(self) -> Crew:
        """创建工作组"""
        return Crew(
            agents=[self.reader_agent(), self.analyzer_agent()],
            tasks=[self.read_task(), self.analyze_task()],
            process=Process.sequential,
            verbose=True
        )

    def analyze(self):
        """执行分析任务并返回结果"""
        result = self.tender_crew().kickoff()
        # 如果结果是JSON字符串，解析成字典
        if isinstance(result.json, str):
            return json.loads(result.json)
        return result.json

    def save_to_excel(self, info, output_file: str = 'tender_analysis.xlsx'):
        """保存结果到Excel"""
        # 定义中文表头映射
        column_mapping = {
            'publish_time': '挂网时间',
            'project_name': '项目名称',
            'project_period': '项目周期(年)',
            'project_amount': '项目标的(万元)',
            'business_scenario': '业务场景',
            'tender_unit': '招标单位',
            'register_deadline': '报名截止时间',
            'submit_deadline': '提交标书截止日期',
            'open_time': '开标截止时间'
        }
        
        # 如果info是字符串，尝试解析成字典
        if isinstance(info, str):
            info = json.loads(info)
            
        # 创建DataFrame并保存
        df = pd.DataFrame([info])
        df = df.rename(columns=column_mapping)
        df.to_excel(output_file, index=False)
        print(f"分析结果已保存到: {output_file}")

def main():
    file_path = '/Users/slg/temp/tender/tender_eg_1.docx'
    analyzer = TenderDocumentAnalyzer(file_path)
    info = analyzer.analyze()

    output_dir = os.path.dirname(file_path)
    output_file = os.path.join(output_dir, 'tender_analysis.xlsx')
    analyzer.save_to_excel(info, output_file)

if __name__ == "__main__":
    main() 