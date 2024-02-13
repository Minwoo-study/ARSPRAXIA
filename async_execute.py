"""
TODO : 실 사용 전에 통제된 환경에서 테스트해야 함
"""

import asyncio, random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tool import JSONconverter

TASK_LIST = [
    # 실행할 함수, 그에 들어갈 인자를 다음과 같은 양식으로 작성
    # 실행할 함수는 () 제외. call하지 말 것
    # {"func": 함수, "parameters": [인자, 인자, ...]}
    {
        "func": JSONconverter.main, # 실행할 함수
        "parameters" : [
            Path("source/async_test_0"), Path("result_storage/async_test_0")
        ] # 실행할 함수에 들어갈 인자
    },
    {
        "func": JSONconverter.main,
        "parameters": [Path("source/async_test_1"), Path("result_storage/async_test_1")]
    },
    {
        "func": JSONconverter.main,
        "parameters": [Path("source/async_test_2"), Path("result_storage/async_test_2")]
    }
]

async def process_multithread(func, *parameters):
    
    await asyncio.sleep(random.random() * 2) # 무작위로 0~2초 가량 지연 (로그가 뒤섞이는 일을 최대한 막기 위함)
    
    loop = asyncio.get_running_loop()
    
    with ThreadPoolExecutor() as threadpool:
        
        result = await loop.run_in_executor(threadpool, func, *parameters)
        return result
    
async def main():
    
    async_tasks = [
        process_multithread(task["func"], *task["parameters"]) for task in TASK_LIST
    ]
    
    await asyncio.gather(*async_tasks)

if __name__ == "__main__":
    
    asyncio.run(main())