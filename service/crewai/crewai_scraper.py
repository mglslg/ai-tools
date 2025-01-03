from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from langchain.tools import BaseTool, Tool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from typing import Any, Dict, Optional

URL = 'https://zb.yfb.qianlima.com/yfbsemsite/mesinfo/zbpglist?source=baidu3&e_matchtype=1&e_creative=92587742638&e_keywordid=783565769311&bd_vid=12232570759345726931'

def selenium_scraper(url: str) -> str:
    """使用 Selenium 抓取网页内容"""
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        page_content = driver.page_source
        return page_content
    except Exception as e:
        return f"抓取出错: {str(e)}"
    finally:
        driver.quit()

@CrewBase
class QianLimaScraper:
    """千里马招标信息抓取 Crew"""
    
    @agent
    def scraper_agent(self) -> Agent:
        """创建网页抓取代理"""
        return Agent(
            role="Web Scraper",
            goal="准确抓取全国招标采购信息平台信息",
            backstory="我是一个专业的网页数据抓取专家，擅长解析和提取网页信息",
            tools=[Tool(
                name="selenium_scraper",
                func=lambda x: selenium_scraper(URL),
                description="使用 Selenium 抓取网页内容的工具"
            )],
            verbose=True
        )
    
    @task
    def scrape_task(self) -> Task:
        """创建抓取任务"""
        return Task(
            description="""
            1. 访问千里马招标网页
            2. 等待页面加载完成
            3. 获取页面内容
            4. 返回完整的HTML内容
            """,
            agent=self.scraper_agent(),
            expected_output="页面的HTML内容"
        )
    
    @crew
    def crew(self) -> Crew:
        """创建抓取 Crew"""
        return Crew(
            agents=[self.scraper_agent()],
            tasks=[self.scrape_task()],
            process=Process.sequential,
            verbose=True
        )

    def scrape(self):
        """执行抓取任务"""
        try:
            html_content = selenium_scraper(URL)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            items = soup.select('.bid-item') or \
                   soup.select('.list-item') or \
                   soup.select('.announcement-item') or \
                   [div for div in soup.find_all('div') if div.get('class') and \
                    any('item' in c.lower() or 'list' in c.lower() for c in div.get('class', []))]
            
            if items:
                data = []
                for item in items:
                    date = item.select_one('.date, .time, [class*="date"], [class*="time"]')
                    region = item.select_one('.region, .area, [class*="region"], [class*="area"]')
                    proj_type = item.select_one('.type, [class*="type"]')
                    title = item.select_one('.title, h3, h4, a, [class*="title"]')
                    
                    data.append({
                        '日期': date.text.strip() if date else '',
                        '地区': region.text.strip() if region else '',
                        '项目类型': proj_type.text.strip() if proj_type else '',
                        '招标采购标题': title.text.strip() if title else ''
                    })
                
                df = pd.DataFrame(data)
                df.to_csv('qianlima_bids.csv', index=False, encoding='utf-8-sig')
                print("数据已保存到 qianlima_bids.csv")
                return df
            else:
                print("未找到招标信息条目")
                with open('debug.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("已将页面HTML保存到debug.html以供分析")
                return None
        except Exception as e:
            print(f"解析数据时出错: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = QianLimaScraper()
    result = scraper.crew().kickoff()
