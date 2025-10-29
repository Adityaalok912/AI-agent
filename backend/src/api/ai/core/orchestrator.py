# # backend/app/core/orchestrator.py
# """
# Async orchestrator for AutoTeamAI.

# Responsibilities:
# - Execute agents in dependency flow (Boss -> PM <-> Architect <-> ProjectMgr -> Engineer <-> QA)
# - Persist outputs via CRUD layer
# - Publish real-time updates via MessageBus
# - Retry and error handling at agent level
# """

# from typing import List, Optional
# import asyncio
# import logging

# from api.ai.core.message_bus import MessageBus
# from api.ai.core.utils import get_logger
# from api.ai.agents.base_agent import BaseAgent, AgentResult
# from api.db import crud
# from sqlalchemy.ext.asyncio import AsyncSession 

# # agent imports
# from api.ai.agents.boss_agent import BossAgent
# from api.ai.agents.product_manager_agent import ProductManagerAgent
# from api.ai.agents.architect_agent import ArchitectAgent
# from api.ai.agents.project_manager_agent import ProjectManagerAgent
# from api.ai.agents.engineer_agent import EngineerAgent
# from api.ai.agents.qa_agent import QAAgent
# from api.ai.agents.llm_client import LLMClient
# from api.ai.schemas.agent_message import AgentMessage

# logger: logging.Logger = get_logger("orchestrator")


# class Orchestrator:
#     def __init__(self, message_bus: MessageBus, llm: Optional[LLMClient] = None):
#         self.message_bus = message_bus
#         self.boss = BossAgent(llm=llm)
#         self.pm = ProductManagerAgent(llm=llm)
#         self.arch = ArchitectAgent(llm=llm)
#         self.projmgr = ProjectManagerAgent(llm=llm)
#         self.engineer = EngineerAgent(llm=llm)
#         self.qa = QAAgent(llm=llm)

#     # --------------------- Core Flow ---------------------
#     async def run(self, prompt: str, db: AsyncSession, project_id: int, project_title: str) -> List[AgentResult]:
#         logger.info(f"Starting AutoTeamAI pipeline for project_id: {project_id}")
        
#         # Publish workflow start event
#         await self.message_bus.publish(project_id, AgentMessage(
#             project_id=project_id,
#             event_type="workflow_start",
#             content=f"Workflow started for project: '{project_title}'"
#         ).json())

#         results: List[AgentResult] = []
#         try:
#             # --------------------- Boss ---------------------
#             boss_res = await self._run_and_record("Boss", self.boss, prompt, db, project_id)
#             results.append(boss_res)

#             # --------------------- Product Manager ---------------------
#             pm_res = await self._run_and_record("Product Manager", self.pm, boss_res.content, db, project_id)
#             results.append(pm_res)

#             # --------------------- Architect ---------------------
#             arch_input = boss_res.content + "\n\n" + pm_res.content
#             arch_res = await self._run_and_record("Architect", self.arch, arch_input, db, project_id)
#             results.append(arch_res)

#             # 🔁 PM <-> Architect feedback loop
#             logger.info("Feedback loop: Product Manager ↔ Architect")
#             pm_refined_input = arch_res.content + "\n\n" + pm_res.content
#             pm_refined = await self._run_and_record("Product Manager (Refined)", self.pm, pm_refined_input, db, project_id)
#             results.append(pm_refined)

#             arch_refined_input = pm_refined.content + "\n\n" + arch_res.content
#             arch_refined = await self._run_and_record("Architect (Refined)", self.arch, arch_refined_input, db, project_id)
#             results.append(arch_refined)

#             # --------------------- Project Manager ---------------------
#             pmgr_input = pm_refined.content + "\n\n" + arch_refined.content
#             pmgr_res = await self._run_and_record("Project Manager", self.projmgr, pmgr_input, db, project_id)
#             results.append(pmgr_res)

#             # 🔁 Architect <-> Project Manager feedback
#             logger.info("Feedback loop: Architect ↔ Project Manager")
#             arch_pm_input = pmgr_res.content + "\n\n" + arch_refined.content
#             arch_pm = await self._run_and_record("Architect (Final)", self.arch, arch_pm_input, db, project_id)
#             results.append(arch_pm)

#             pmgr_refined_input = arch_pm.content + "\n\n" + pmgr_res.content
#             pmgr_refined = await self._run_and_record("Project Manager (Refined)", self.projmgr, pmgr_refined_input, db, project_id)
#             results.append(pmgr_refined)

#             # --------------------- Engineer ---------------------
#             eng_input = pmgr_refined.content + "\n\n" + arch_pm.content
#             eng_res = await self._run_and_record("Engineer", self.engineer, eng_input, db, project_id)
#             results.append(eng_res)

#             # --------------------- QA ---------------------
#             qa_input = eng_res.content + "\n\n" + pmgr_refined.content
#             qa_res = await self._run_and_record("QA", self.qa, qa_input, db, project_id)
#             results.append(qa_res)

#             # 🔁 Engineer <-> QA feedback
#             logger.info("Feedback loop: Engineer ↔ QA")
#             eng_final_input = eng_res.content + "\n\n" + qa_res.content
#             eng_final = await self._run_and_record("Engineer (Final)", self.engineer, eng_final_input, db, project_id)
#             results.append(eng_final)

#         except Exception as e:
#             # Catch any exception from _run_and_record to ensure workflow_end is published
#             logger.error(f"Workflow for project_id {project_id} terminated due to an error: {e}", exc_info=True)
        
#         finally:
#             # Publish workflow end event regardless of success or failure
#             await self.message_bus.publish(project_id, AgentMessage(
#                 project_id=project_id,
#                 event_type="workflow_end",
#                 content="Workflow has completed."
#             ).json())
#             logger.info(f"✅ AutoTeamAI pipeline complete for project_id: {project_id}")
        
#         return results

#     # --------------------- Helper: run, persist, publish ---------------------
#     async def _run_and_record(self, name: str, agent: BaseAgent, input_text: str, db: AsyncSession, project_id: int) -> AgentResult:
#         # Publish agent start event
#         await self.message_bus.publish(project_id, AgentMessage(
#             project_id=project_id,
#             event_type="agent_start",
#             agent_name=name,
#             content=f"Agent '{name}' is starting its task..."
#         ).json())

#         try:
#             result = await self._run_agent_with_retries(agent, input_text, name)
#         except Exception as exc:
#             err_text = f"An error occurred in agent '{name}': {exc}"
#             logger.error(err_text, exc_info=True)
            
#             # Persist and publish error
#             await crud.add_agent_output(db, project_id, name, err_text)
#             await self.message_bus.publish(project_id, AgentMessage(
#                 project_id=project_id,
#                 event_type="error",
#                 agent_name=name,
#                 content=err_text
#             ).json())
#             raise # Re-raise the exception to stop the workflow

#         # Persist and publish successful result
#         await crud.add_agent_output(db, project_id, name, result.content)
#         await self.message_bus.publish(project_id, AgentMessage(
#             project_id=project_id,
#             event_type="agent_result",
#             agent_name=result.agent_name,
#             content=result.content
#         ).json())
        
#         return result

#     # --------------------- Helper: retry logic ---------------------
#     async def _run_agent_with_retries(
#         self, agent, input_text: str, agent_name: str, retries: int = 2, backoff: float = 1.0
#     ) -> AgentResult:
#         attempt = 0
#         last_exc = None
#         while attempt <= retries:
#             try:
#                 return await agent.run(input_text)
#             except Exception as e:
#                 last_exc = e
#                 wait = backoff * (2 ** attempt)
#                 logger.warning(
#                     "Agent %s failed on attempt %d: %s — retrying in %.1fs",
#                     agent_name,
#                     attempt,
#                     e,
#                     wait,
#                 )
#                 await asyncio.sleep(wait)
#                 attempt += 1
#         raise last_exc


"""
Async orchestrator for AutoTeamAI.

Responsibilities:
- Execute agents in dependency flow (Boss -> PM <-> Architect <-> ProjectMgr -> Engineer <-> QA)
- Persist outputs via CRUD layer
- Publish real-time updates via MessageBus
- Retry and error handling at agent level
"""

from typing import List, Optional, Callable
import asyncio
import logging
import json

from api.ai.core.message_bus import MessageBus
from api.ai.core.utils import get_logger
from api.ai.agents.base_agent import BaseAgent, AgentResult
from api.db import crud
from sqlalchemy.ext.asyncio import AsyncSession

# agent imports
from api.ai.agents.boss_agent import BossAgent
from api.ai.agents.product_manager_agent import ProductManagerAgent
from api.ai.agents.architect_agent import ArchitectAgent
from api.ai.agents.project_manager_agent import ProjectManagerAgent
from api.ai.agents.engineer_agent import EngineerAgent
from api.ai.agents.qa_agent import QAAgent
from api.ai.agents.llm_client import LLMClient

logger: logging.Logger = get_logger("orchestrator")


class Orchestrator:
    def __init__(self, message_bus: MessageBus, llm: Optional[LLMClient] = None):
        self.message_bus = message_bus
        self.boss = BossAgent(llm=llm)
        self.pm = ProductManagerAgent(llm=llm)
        self.arch = ArchitectAgent(llm=llm)
        self.projmgr = ProjectManagerAgent(llm=llm)
        self.engineer = EngineerAgent(llm=llm)
        self.qa = QAAgent(llm=llm)

    # --------------------- Helper to create structured JSON messages ---------------------
    def _create_message(self, event_type: str, project_id: int, agent_name: Optional[str] = None, content: Optional[str] = None) -> str:
        message = {
            "event_type": event_type,
            "project_id": project_id,
            "agent_name": agent_name,
            "content": content
        }
        return json.dumps(message)

    # --------------------- Core Flow ---------------------
    async def run(self, prompt: str, db_session_factory: Callable[[], AsyncSession], project_id: int, project_title: str) -> List[AgentResult]:
        logger.info(f"Starting AutoTeamAI pipeline for project_id: {project_id}")
        
        # Create a new session specifically for this background task.
        db: AsyncSession = db_session_factory()
        
        results: List[AgentResult] = []
        try:
            # Publish workflow start event
            start_message = self._create_message(
                "workflow_start",
                project_id,
                "Orchestrator",
                f"Workflow started for project: '{project_title}'"
            )
            await self.message_bus.publish(project_id, "Orchestrator", start_message)

            # --------------------- Boss ---------------------
            boss_res = await self._run_and_record("Boss", self.boss, prompt, db, project_id)
            results.append(boss_res)

            # --------------------- Product Manager ---------------------
            pm_res = await self._run_and_record("Product Manager", self.pm, boss_res.content, db, project_id)
            results.append(pm_res)

            # --------------------- Architect ---------------------
            arch_input = boss_res.content + "\n\n" + pm_res.content
            arch_res = await self._run_and_record("Architect", self.arch, arch_input, db, project_id)
            results.append(arch_res)

            # 🔁 PM <-> Architect feedback loop
            logger.info("Feedback loop: Product Manager ↔ Architect")
            pm_refined_input = arch_res.content + "\n\n" + pm_res.content
            pm_refined = await self._run_and_record("Product Manager (Refined)", self.pm, pm_refined_input, db, project_id)
            results.append(pm_refined)

            arch_refined_input = pm_refined.content + "\n\n" + arch_res.content
            arch_refined = await self._run_and_record("Architect (Refined)", self.arch, arch_refined_input, db, project_id)
            results.append(arch_refined)

            # --------------------- Project Manager ---------------------
            pmgr_input = pm_refined.content + "\n\n" + arch_refined.content
            pmgr_res = await self._run_and_record("Project Manager", self.projmgr, pmgr_input, db, project_id)
            results.append(pmgr_res)

            # 🔁 Architect <-> Project Manager feedback
            logger.info("Feedback loop: Architect ↔ Project Manager")
            arch_pm_input = pmgr_res.content + "\n\n" + arch_refined.content
            arch_pm = await self._run_and_record("Architect (Final)", self.arch, arch_pm_input, db, project_id)
            results.append(arch_pm)

            pmgr_refined_input = arch_pm.content + "\n\n" + pmgr_res.content
            pmgr_refined = await self._run_and_record("Project Manager (Refined)", self.projmgr, pmgr_refined_input, db, project_id)
            results.append(pmgr_refined)

            # --------------------- Engineer ---------------------
            eng_input = pmgr_refined.content + "\n\n" + arch_pm.content
            eng_res = await self._run_and_record("Engineer", self.engineer, eng_input, db, project_id)
            results.append(eng_res)

            # --------------------- QA ---------------------
            qa_input = eng_res.content + "\n\n" + pmgr_refined.content
            qa_res = await self._run_and_record("QA", self.qa, qa_input, db, project_id)
            results.append(qa_res)

            # 🔁 Engineer <-> QA feedback
            logger.info("Feedback loop: Engineer ↔ QA")
            eng_final_input = qa_res.content + "\n\n" + eng_res.content
            eng_final = await self._run_and_record("Engineer (Final)", self.engineer, eng_final_input, db, project_id)
            results.append(eng_final)

        except Exception as e:
            logger.error(f"Workflow for project_id {project_id} terminated due to an error: {e}", exc_info=True)
        
        finally:
            # IMPORTANT: Close the session created within this task.
            await db.close()

            # Publish workflow end event
            end_message = self._create_message(
                "workflow_end",
                project_id,
                "Orchestrator",
                "Workflow has completed."
            )
            await self.message_bus.publish(project_id, "Orchestrator", end_message)
            logger.info(f"✅ AutoTeamAI pipeline complete for project_id: {project_id}")
        
        return results

    # --------------------- Helper: run, persist, publish ---------------------
    async def _run_and_record(self, name: str, agent: BaseAgent, input_text: str, db: AsyncSession, project_id: int) -> AgentResult:
        # Publish agent start event
        start_message = self._create_message("agent_start", project_id, name, f"Agent '{name}' is starting its task...")
        await self.message_bus.publish(project_id, name, start_message)

        try:
            result = await self._run_agent_with_retries(agent, input_text, name)
        except Exception as exc:
            err_text = f"An error occurred in agent '{name}': {exc}"
            logger.error(err_text, exc_info=True)
            
            # Persist and publish error
            await crud.add_agent_output(db, project_id, name, err_text)
            error_message = self._create_message("error", project_id, name, err_text)
            await self.message_bus.publish(project_id, name, error_message)
            raise # Re-raise the exception to stop the workflow

        # Persist and publish successful result
        await crud.add_agent_output(db, project_id, name, result.content)
        result_message = self._create_message("agent_result", project_id, name, result.content)
        await self.message_bus.publish(project_id, name, result_message)
        
        return result

    # --------------------- Helper: retry logic ---------------------
    async def _run_agent_with_retries(
        self, agent, input_text: str, agent_name: str, retries: int = 2, backoff: float = 1.0
    ) -> AgentResult:
        attempt = 0
        last_exc = None
        while attempt <= retries:
            try:
                return await agent.run(input_text)
            except Exception as e:
                last_exc = e
                wait = backoff * (2 ** attempt)
                logger.warning(
                    "Agent %s failed on attempt %d: %s — retrying in %.1fs",
                    agent_name,
                    attempt,
                    e,
                    wait,
                )
                await asyncio.sleep(wait)
                attempt += 1
        raise last_exc