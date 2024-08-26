from utils import generate_ai_response, load_prompt_template

a = "정해인같은 남자친구를 만드려면 어디로 가야돼?"
b = "방송국에 가봐"

print(generate_ai_response(question=a, answer=b))


# poetry run python /Users/mac/Desktop/oz_03_collabo-004-BE/api/ai_hunsoos/ai_test.py
