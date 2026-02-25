import asyncio
import json
from services.llm_provider import get_llm_provider
from services.planner_service import PlannerService
from services.prompts import planner_system_prompt  # <-- import directly

TEST_PROMPTS = [
    "change circle to heart",
    "make it softer and more friendly",
    "turn this into a banking transfer icon",
]

async def main():
    llm = get_llm_provider()
    planner = PlannerService(llm)

    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" stroke="black" fill="none" id="el-1"/></svg>'

    for prompt in TEST_PROMPTS:
        print("\n==============================")
        print("PROMPT:", prompt)
        print("==============================")

        raw = await llm.generate(
            system_prompt=planner_system_prompt,
            user_prompt=json.dumps({
                "mode": "mutate",
                "userInput": prompt,
                "originalSvg": svg
            }),
            temperature=0.2
        )

        print("RAW OUTPUT:")
        print(raw)

asyncio.run(main())