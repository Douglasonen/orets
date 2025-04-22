from openai import OpenAI
def create_rep(prompt):
      try:
        ### new openreutor API key = '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'
        client = OpenAI(
          base_url="https://openrouter.ai/api/v1",
          api_key='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',
        )

        completion = client.chat.completions.create(
          extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
          },
          extra_body={},
          model="deepseek/deepseek-chat-v3-0324:free",
          messages=[
            {
              "role": "user",
              "content": prompt
            }
          ]
        )
        print(completion.choices[0].message.content)
      except Exception as e:
        print('An error occured: ', e)
        return 'I beg your pardon'
create_rep('who is the president of USA?')