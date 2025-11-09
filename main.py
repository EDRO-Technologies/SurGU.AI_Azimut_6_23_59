from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
import asyncio
from models import llm
import logging
import re
from prompts import chat_prompt, quiz_prompt, scenario_prompt

from rag import get_context
from questions import generate_quiz_questions, get_context_quiz, generate_scenario_questions
from speech import get_text_from_speech


app = FastAPI(title="beZbot API", version="1.0.0")


class SpeechResponse(BaseModel):
    text: str


class QuestionRequest(BaseModel):
    question: str

class QuizRequest(BaseModel):
    id: str

class ScenarioRequest(BaseModel):
    id: str

class AnswerResponse(BaseModel):
    answer: str

class QuizResponse(BaseModel):
    quiz: list

class ScenarioResponse(BaseModel):
    scenario: list


@app.post("/get_answer", response_model=AnswerResponse)
async def get_answer(request: QuestionRequest):
    """Отвечает на вопрос: сначала проверяет FAQ, потом использует RAG + LLM."""
    try:
        context = get_context()
        # Строим промпт с учётом историизкщьзе = context
        prompt = chat_prompt.format(context=context, question=request.question)
        answer = llm.predict(prompt)
            
        answer = answer.strip()
        
        return AnswerResponse(
            answer=answer,
        )
        
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")


@app.post("/get_quiz", response_model=QuizResponse)
async def get_quiz(request: QuizRequest):
    """Генерирует проверочную викторину на основе контекста."""
    try:
        context = get_context_quiz(request.id)
        response = generate_quiz_questions(context)
        return QuizResponse(quiz=response)
    except Exception as e:
        logging.error(f"Ошибка при генерации викторины: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации викторины: {str(e)}")
    
    
@app.post("/get_scenario", response_model=ScenarioResponse)
async def get_scenario(request: ScenarioRequest):
    try:
        response = generate_scenario_questions()
        return ScenarioResponse(scenario=response)
    except Exception as e:
        logging.error(f"Ошибка при генерации ситуационной задачи: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ситуационной задачи: {str(e)}")


@app.post('/speech_to_text', response_model=SpeechResponse)
async def speech_to_text(file: UploadFile):
  try:
    # Читаем содержимое файла
    file_content = await file.read()

    text = get_text_from_speech(file_content)

    return {'text': text}

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)