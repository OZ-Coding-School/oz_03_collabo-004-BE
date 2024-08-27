from utils import generate_ai_response, load_prompt_template

a = "하나는 모르고 둘만 아는 친구에 대해 어떻게 생각해?"
b = "잘 모르겠는뎅"

print(generate_ai_response(question=a, answer=b))


# poetry run python /Users/mac/Desktop/oz_03_collabo-004-BE/api/ai_hunsoos/ai_test.py
