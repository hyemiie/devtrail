from fastapi import FastAPI, APIRouter, Request
import httpx

router = APIRouter()

async def get_leet_questions():
     async with httpx.AsyncClient() as client:
          response = await client.get("https://alfa-leetcode-api.onrender.com/problems", 
                                      params={"difficulty" : "EASY"})
          response.raise_for_status()
          return response.json()


@router.get("/get_leetcode")
async def get_leet_questions():
     async with httpx.AsyncClient() as client:
          response = await client.get("https://alfa-leetcode-api.onrender.com/problems", 
                                      params={"difficulty" : "EASY"})
          response.raise_for_status()
          return response.json()



@router.get("/get_daily_leetcode")
async def get_daily_leet_questions():
     async with httpx.AsyncClient() as client:
          response = await client.get("https://alfa-leetcode-api.onrender.com/daily/raw")
          response.raise_for_status()
          return response.json()


async def get_solution(titleSlug: str):
    try: 
        async with httpx.AsyncClient() as client:
            response = await client.get("https://alfa-leetcode-api.onrender.com/officialSolution", 
                                        params={"titleSlug": titleSlug})
            response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")


