from crewai import Agent, Crew, Process, Task
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


from typing import List
import os
from pathlib import Path


from go_to_japan.tools.activity_tool import DailyActivitiesPlan
from go_to_japan.tools.budget_management_tool import BudgetAggregationOutput
from go_to_japan.tools.itinerary_synthesis_tool import ItinerarySynthesisJSON
from go_to_japan.tools.lodging_tool import LodgingOptionsByCity
from go_to_japan.tools.news_event_tool import LiveNewsOutput
from go_to_japan.tools.orchestration_tool import OrchestrationBootReport
from go_to_japan.tools.quality_audit_tool import QualityAuditOutput
from go_to_japan.tools.restaurant_tool import DiningPlan
from go_to_japan.tools.resume_voyage_tool import ResumeVoyage
from go_to_japan.tools.transport_tool import TransportCityPlan
from go_to_japan.tools.translation_tool import MultilingualItineraryTranslations
from go_to_japan.tools.weather_tool import CityMeteoInfo



from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool 

llm = 'openai/gpt-4o-mini'

# Store in project directory
project_root = Path(__file__).parent
storage_dir = project_root / "go_to_japan_ai_storage"

os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)

#################################################
#### Fonctions condition pour chaque service ####
#################################################


def has_restaurants(output: TaskOutput) -> bool:
    # Accéder aux inputs via le crew directement
    crew = output.agent.crew if hasattr(output, 'agent') and hasattr(output.agent, 'crew') else None
    if crew and hasattr(crew, 'inputs'):
        services = crew.inputs.get('services', [])
        return 'restaurants' in services
    return False

def has_lodging(output: TaskOutput) -> bool:
    crew = output.agent.crew if hasattr(output, 'agent') and hasattr(output.agent, 'crew') else None
    if crew and hasattr(crew, 'inputs'):
        services = crew.inputs.get('services', [])
        return 'lodging' in services
    return False

def has_accommodation(output: TaskOutput) -> bool:
    crew = output.agent.crew if hasattr(output, 'agent') and hasattr(output.agent, 'crew') else None
    if crew and hasattr(crew, 'inputs'):
        services = crew.inputs.get('services', [])
        return 'accommodation' in services
    return False

def has_transport(output: TaskOutput) -> bool:
    crew = output.agent.crew if hasattr(output, 'agent') and hasattr(output.agent, 'crew') else None
    if crew and hasattr(crew, 'inputs'):
        services = crew.inputs.get('services', [])
        return 'transport' in services
    return False


@CrewBase
class GoToJapan():
    """GoToJapan crew"""
    

    agents: List[BaseAgent]
    tasks: List[Task]


    #################################################
    #################### Agents #####################
    #################################################    

    # @agent
    # def orchestration_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['orchestration_agent'],
    #         verbose=True,
    #         allow_delegation=True,
    #         llm=llm,
    #     )
    
    @agent
    def profiler_agent (self) -> Agent:
        return Agent(
            config=self.agents_config['profiler_agent'],
            verbose=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def live_news_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['live_news_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def weather_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_analyst_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def transport_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['transport_planner_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def lodging_specialist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['lodging_specialist_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def daily_activities_sequencing_designer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['daily_activities_sequencing_designer_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def dining_recommender_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['dining_recommender_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def budget_feasibility_controller_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['budget_feasibility_controller_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def quality_consistency_auditor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_consistency_auditor_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    @agent
    def itinerary_synthesizer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_synthesizer_agent'],
            verbose=True,
            allow_delegation=True,
            memory=True,
            llm=llm,
        )
    
    # @agent
    # def translation_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['translation_agent'],
    #         verbose=True,
    #         allow_delegation=True,
    #         llm=llm,
    #     )   
    
    #################################################
    ##################### Tasks #####################
    #################################################    

    # @task
    # def orchestration_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['orchestration_task'],
    #         agent=self.orchestration_agent(),
    #         output_json=OrchestrationBootReport,
    #         output_file="result/orchestration_plan.json",
        
    #     )

    
    @task
    def profiler_task(self) -> Task:
        return Task(
            config=self.tasks_config['profiler_task'],
            agent=self.profiler_agent(),
            output_json= ResumeVoyage,
            output_file="result/profile.json", 
        )
    
    @task
    def live_news_task(self) -> Task:
        return Task(
            config=self.tasks_config['live_news_task'],
            agent=self.live_news_agent(),
            contexts=['profiler_task'],
            output_json=LiveNewsOutput,
            output_file="result/live_news.json",
            tools=[SerperDevTool()],
        )

    @task
    def weather_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['weather_analyst_task'],
            agent=self.weather_analyst_agent(),
            contexts=['profiler_task', 'live_news_task'],
            output_json=CityMeteoInfo,
            output_file="result/weather_analyst.json",
            tools=[SerperDevTool()],
        )
    
    @task
    def transport_planner_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['transport_planner_task'],
            agent=self.transport_planner_agent(),
            condition=has_restaurants,
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task'],
            output_json=TransportCityPlan,
            output_file="result/transport_planner.json",
            tools=[ScrapeWebsiteTool(), WebsiteSearchTool()],
        )


    @task
    def lodging_specialist_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['lodging_specialist_task'],
            agent=self.lodging_specialist_agent(),
            condition=has_lodging or has_accommodation,
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task'],
            output_json=LodgingOptionsByCity,
            output_file="result/lodging_specialist.json",
            tools=[ScrapeWebsiteTool(), WebsiteSearchTool()], 
        )
    
    @task
    def daily_activities_sequencing_task(self) -> Task:
        return Task(
            config=self.tasks_config['daily_activities_sequencing_task'],
            agent=self.daily_activities_sequencing_designer_agent(),
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task', 'transport_planner_task', 'lodging_specialist_task'],
            output_json=DailyActivitiesPlan,
            tools=[ScrapeWebsiteTool(), WebsiteSearchTool()],
            output_file="result/daily_activities.json", 
        )
    
    @task
    def dining_recommender_task(self) -> ConditionalTask:
        return ConditionalTask(
            config=self.tasks_config['dining_recommender_task'],
            agent=self.dining_recommender_agent(),
            condition=has_restaurants,
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task', 'transport_planner_task', 'lodging_specialist_task'],
            output_json=DiningPlan,
            output_file="result/dining_recommender.json",
            tools=[ScrapeWebsiteTool(), WebsiteSearchTool()], 
        )
    
    @task
    def budget_aggregation_and_variants_task(self) -> Task:
        return Task(
            config=self.tasks_config['budget_aggregation_and_variants_task'],
            agent=self.budget_feasibility_controller_agent(),
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task', 'transport_planner_task', 'lodging_specialist_task', 'daily_activities_sequencing_task', 'dining_recommender_task'],
            output_json=BudgetAggregationOutput,
            output_file="result/budget_aggregation.json",
            tools=[ScrapeWebsiteTool(), WebsiteSearchTool()], 
        )
    
    @task
    def quality_and_consistency_audit_task(self) -> Task:
        return Task(
            config=self.tasks_config['quality_and_consistency_audit_task'],
            agent=self.quality_consistency_auditor_agent(),
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task', 'transport_planner_task', 'lodging_specialist_task', 'daily_activities_sequencing_task', 'dining_recommender_task', 'budget_aggregation_and_variants_task'],
            output_json=QualityAuditOutput,
            output_file="result/quality_consistency_audit.json", 
        )
    
    @task
    def itinerary_synthesizer_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_synthesizer_task'],
            agent=self.itinerary_synthesizer_agent(),
            contexts=['profiler_task', 'live_news_task', 'weather_analyst_task', 'transport_planner_task', 'lodging_specialist_task', 'daily_activities_sequencing_task', 'dining_recommender_task', 'budget_aggregation_and_variants_task', 'quality_and_consistency_audit_task'],
            #output_json=ItinerarySynthesisJSON,
            output_file="result/itinerary_synthesis.json",
            output_pydantic=ItinerarySynthesisJSON
        )
    
    # @task
    # def translation_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['translation_task'],
    #         agent=self.translation_agent(),
    #         contexts=['itinerary_synthesizer_task'],
    #         output_json=MultilingualItineraryTranslations,
    #         output_file="result/itinerary_translation.json", 
    #     )
    
    #################################################
    ##################### Crew ######################
    ################################################# 

    @crew
    def crew(self) -> Crew:
        """Creates the GoToJapan crew"""

        return Crew(
            agents = [
                self.profiler_agent(),
                self.live_news_agent(),
                self.weather_analyst_agent(),
                self.transport_planner_agent(),
                self.lodging_specialist_agent(),
                self.daily_activities_sequencing_designer_agent(),
                self.dining_recommender_agent(),
                self.budget_feasibility_controller_agent(),
                self.quality_consistency_auditor_agent(),
                self.itinerary_synthesizer_agent(),
                # self.translation_agent(),
            ], # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            # process=Process.hierarchical,
            # manager_agent=self.orchestration_agent(),
            process=Process.sequential,
            verbose=True,
            # memory=True,
            # long_term_memory=LongTermMemory(
            #     storage=LTMSQLiteStorage(
            #         db_path=f"{storage_dir}/long_memory.db"
            #     )
            # ),

            # short_term_memory=ShortTermMemory(
            #     storage=RAGStorage(
            #         type="short_term",
            #     )
            # ),
            # entity_memory=EntityMemory(
            #     storage=RAGStorage(
            #         type="entity_memory",
            #     )
            # ),
            output_log_file="result/crew.json"
        )
