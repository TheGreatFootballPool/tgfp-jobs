from prefect import variables

# from a synchronous context
answer = variables.set('the_answer')
print(answer)