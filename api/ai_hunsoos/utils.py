import os
from pathlib import Path

from django.conf import settings
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))


def load_prompt_template():
    """
    텍스트 파일로부터 프롬프트를 불러오는 함수.
    """
    prompt_path = os.path.join(settings.BASE_DIR, "ai_hunsoos", "prompt.txt")
    with open(prompt_path, "r") as file:
        prompt_template = file.read()
    return prompt_template


# ai_test.py 실행용

# def load_prompt_template():
#     """
#     텍스트 파일로부터 프롬프트를 불러오는 함수.
#     """
#     with open("api/ai_hunsoos/prompt.txt", "r") as file:
#         return file.read()


def generate_ai_response(question, answer):
    """
    GPT-4-mini 모델을 사용해 AI 응답을 생성하는 함수.

    :param question: 게시글의 질문 내용
    :param answer: 선택된 답변 내용
    :return: AI가 생성한 응답 텍스트
    """
    # 프롬프트 템플릿 불러오기
    prompt_template = load_prompt_template()

    # 프롬프트에 게시글과 댓글 내용 삽입
    prompt = prompt_template.format(question=question, answer=answer)

    # OpenAI API
    client = OpenAI(
        api_key=os.environ.get("api_key"),
    )

    messages = [
        {
            "role": "system",
            "content": "You are an AI that provides critical and constructive feedback.",
        },
        {"role": "user", "content": prompt},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # GPT-4-mini 모델 사용
            messages=messages,  # AI에게 주어질 프롬프트
            max_tokens=300,  # 응답의 최대 길이 설정
            n=1,  # 생성할 응답 수
            stop=None,  # 응답을 멈추는 특정 토큰 설정
            temperature=0.7,  # 생성되는 텍스트의 창의성 조절
        )
        # 응답 텍스트 반환
        return response.choices[0].message.content

    except Exception as e:
        # 오류 발생 시 기본 응답을 반환
        return f"An error occurred while generating the response: {str(e)}"
