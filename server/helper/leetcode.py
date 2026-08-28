from fastapi import FastAPI, APIRouter, Request
import httpx

router = APIRouter()

async def get_leet_questions(number: int):
     print('number', number)
     async with httpx.AsyncClient() as client:
          response = await client.get("https://alfa-leetcode-api.onrender.com/problems?limit=number", 
                                      params={"limit" : number})
          response.raise_for_status()
          return response.json()

async def get_question_from_slug(titleSlug: str):
    try:
        print("slug", titleSlug)
        async with httpx.AsyncClient() as client:
            response = await client.get("https://alfa-leetcode-api.onrender.com/select/raw?titleSlug=selected-question",
                                        params={"titleSlug" : titleSlug}
                                        )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        print(f'Error {e}')
    

@router.get("/get_leetcode_difficulty")
async def get_leet_questions_difficulty():
     async with httpx.AsyncClient() as client:
          response = await client.get("https://alfa-leetcode-api.onrender.com/problems", 
                                      params={"difficulty" : "EASY"})
          response.raise_for_status()
          return response.json()

@router.get('/get_question_details/{number}')
async def get_question_details(number:int):
    try:
        print("title_slug", number)
        raw_question =  await get_leet_questions(number=number)
        slug_array = []
        for question in raw_question.get("problemsetQuestionList"):
            slug_array.append(question.get("titleSlug"))

        questions_array = []

        for title in slug_array:
            print(title)
            questions = await get_question_from_slug(titleSlug= str(title))
            print("questions", questions)
            questions_array.append(questions.get("question", {}).get("content"))

        return questions_array
    
    except Exception as e:
        print(f'Error {e}')




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


