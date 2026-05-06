import httpx
from openai import OpenAI

client = OpenAI(
    api_key="dc-ai-dea9d7bf-10cf-4587-917d-343791388956",
    base_url="https://data.testing.hetao101.com/dc-route-api/route/v1",
    http_client=httpx.Client(verify=False)
)

messages = []

print("=" * 40)
print("  多轮对话（输入 exit 退出，输入 clear 清除历史）")
print("=" * 40)

while True:
    user_input = input("\n你: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("再见！")
        break
    if user_input.lower() == "clear":
        messages = []
        print("历史已清除，开始新对话。")
        continue

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-5.2-chat",
            messages=messages
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f"\nAI: {reply}")
    except Exception as e:
        print(f"\n请求失败: {e}")
        messages.pop()
