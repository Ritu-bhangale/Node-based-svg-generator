import asyncio

from services.starvector_service import starvector_service


TEST_PROMPTS = [
    "minimal icon of heart",
    "complex banking transfer symbol",
    "abstract geometric composition",
]


async def run_tests() -> None:
    starvector_service.load()

    for prompt in TEST_PROMPTS:
        print("\n==============================")
        print("PROMPT:", prompt)
        print("==============================")
        svg = await starvector_service.generate(prompt)
        print("SVG length:", len(svg))
        print("SVG preview:", svg[:200])


if __name__ == "__main__":
    asyncio.run(run_tests())

