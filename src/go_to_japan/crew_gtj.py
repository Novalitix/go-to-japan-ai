"""
Crew definition for the Japan itinerary planning system.

This module defines a CrewAI crew that orchestrates a multi‑agent workflow
to build personalised travel itineraries for Japan.  The crew is composed
of agents and tasks defined in separate YAML files.  Agents collaborate
to parse user preferences, perform live research, sequence cities,
analyse weather, plan transport, curate lodgings and dining, design
activities, aggregate budgets, verify facts, audit quality, and finally
synthesise the complete itinerary.  The crew configuration here
relies on the YAML files generated earlier (`agents.yaml` and
`tasks.yaml`) and uses CrewAI’s decorator framework to tie everything
together.

References:
  • The CrewAI documentation on crews explains how to define a crew via
    YAML configuration and the `CrewBase` class.  A crew requires a list
    of agents and tasks, and may specify a process such as sequential
    execution【428436203923731†L236-L333】.
  • YAML configuration is the recommended method for defining crews, as
    it promotes maintainability and consistency with agent and task
    definitions【428436203923731†L245-L247】.
"""

from typing import List

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class JapanItineraryCrew:
    """Crew orchestrating the Japan itinerary planning pipeline.

    This crew brings together all of the agents and tasks needed to
    generate a comprehensive, day‑by‑day itinerary for a trip to Japan.
    Agents and tasks are loaded from external YAML configuration files
    (`agents.yaml` and `tasks.yaml`).  The crew executes the tasks
    sequentially, reflecting the logical order of the planning process.
    """

    # Lists of agents and tasks will be filled automatically by the
    # decorators below.  Type annotations are included for clarity.
    agents: List[BaseAgent]
    tasks: List[Task]

    # Paths to the YAML configuration files.  These files must exist in
    # the same directory as this crew module.  If you move the YAML
    # files into a ``config/`` subdirectory, update these paths
    # accordingly.
    agents_config = 'agents.yaml'
    tasks_config = 'tasks.yaml'

    # ----------------------------------------------------------------------
    # Agent factory methods
    # Each method decorated with ``@agent`` returns an Agent configured from
    # the corresponding entry in ``agents.yaml``.  The keys passed to
    # ``self.agents_config[...]`` must match the identifiers defined in
    # that YAML file.
    #
    # See the CrewAI documentation for details on using the ``@agent``
    # decorator【428436203923731†L268-L333】.

    @agent
    def conductor_orchestrator(self) -> Agent:
        return Agent(config=self.agents_config['conductor_orchestrator'])

    @agent
    def intent_profile_parser(self) -> Agent:
        return Agent(config=self.agents_config['intent_profile_parser'])

    @agent
    def live_research_scout(self) -> Agent:
        return Agent(config=self.agents_config['live_research_scout'])

    @agent
    def city_curator(self) -> Agent:
        return Agent(config=self.agents_config['city_curator'])

    @agent
    def weather_season_analyst(self) -> Agent:
        return Agent(config=self.agents_config['weather_season_analyst'])

    @agent
    def transport_planner(self) -> Agent:
        return Agent(config=self.agents_config['transport_planner'])

    @agent
    def stay_lodging_curator(self) -> Agent:
        return Agent(config=self.agents_config['stay_lodging_curator'])

    @agent
    def activities_experiences_designer(self) -> Agent:
        return Agent(config=self.agents_config['activities_experiences_designer'])

    @agent
    def gastro_dining_curator(self) -> Agent:
        return Agent(config=self.agents_config['gastro_dining_curator'])

    @agent
    def budget_feasibility_controller(self) -> Agent:
        return Agent(config=self.agents_config['budget_feasibility_controller'])

    @agent
    def facts_sources_verifier(self) -> Agent:
        return Agent(config=self.agents_config['facts_sources_verifier'])

    @agent
    def quality_consistency_auditor(self) -> Agent:
        return Agent(config=self.agents_config['quality_consistency_auditor'])

    @agent
    def itinerary_synthesizer(self) -> Agent:
        return Agent(config=self.agents_config['itinerary_synthesizer'])

    # ----------------------------------------------------------------------
    # Task factory methods
    # Each method decorated with ``@task`` returns a Task configured from
    # the corresponding entry in ``tasks.yaml``.  The keys passed to
    # ``self.tasks_config[...]`` must match the task identifiers defined
    # in that YAML file.

    @task
    def orchestration_boot(self) -> Task:
        return Task(config=self.tasks_config['orchestration_boot'])

    @task
    def parse_and_normalize_profile(self) -> Task:
        return Task(config=self.tasks_config['parse_and_normalize_profile'])

    @task
    def live_research_and_facts(self) -> Task:
        return Task(config=self.tasks_config['live_research_and_facts'])

    @task
    def city_sequencing_and_districts(self) -> Task:
        return Task(config=self.tasks_config['city_sequencing_and_districts'])

    @task
    def weather_windows_and_plan_b(self) -> Task:
        return Task(config=self.tasks_config['weather_windows_and_plan_b'])

    @task
    def transport_segments_and_pass(self) -> Task:
        return Task(config=self.tasks_config['transport_segments_and_pass'])

    @task
    def lodging_options_by_city(self) -> Task:
        return Task(config=self.tasks_config['lodging_options_by_city'])

    @task
    def daily_activities_sequencing(self) -> Task:
        return Task(config=self.tasks_config['daily_activities_sequencing'])

    @task
    def dining_plan_and_culinary_highlights(self) -> Task:
        return Task(config=self.tasks_config['dining_plan_and_culinary_highlights'])

    @task
    def budget_aggregation_and_variants(self) -> Task:
        return Task(config=self.tasks_config['budget_aggregation_and_variants'])

    @task
    def facts_and_sources_verification(self) -> Task:
        return Task(config=self.tasks_config['facts_and_sources_verification'])

    @task
    def quality_and_consistency_audit(self) -> Task:
        return Task(config=self.tasks_config['quality_and_consistency_audit'])

    @task
    def itinerary_synthesis_and_packaging(self) -> Task:
        return Task(config=self.tasks_config['itinerary_synthesis_and_packaging'])

    # ----------------------------------------------------------------------
    # Crew factory method
    # The ``@crew`` decorator marks the method that assembles the crew.  It
    # collects all agents and tasks defined above and specifies the
    # execution process.  Here we choose ``Process.sequential`` because the
    # itinerary planning follows a logical order from parsing the profile
    # through research, planning, verification and synthesis【428436203923731†L323-L333】.

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )