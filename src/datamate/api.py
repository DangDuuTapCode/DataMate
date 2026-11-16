"""Stable in-process API for a local SLM or a host application; no HTTP/network."""
from .metrics import Executor
from .types import Question
from .understanding import RulePlanner
from .verify import verify


def answer_question(question: Question, tables, planner=None):
    planner = planner or RulePlanner()
    plan = planner.plan(question.question, question.as_of_date)
    if plan is None:
        return {"id": question.id, "type": "abstain"}
    candidate = Executor(tables).execute(plan, question.question)
    return verify(question.id, candidate, plan)
