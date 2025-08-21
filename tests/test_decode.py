from app.core import security
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU1NTMxMDg2LCJpYXQiOjE3NTU1MjkyODZ9.POKLXmJKJMdeIuo55VuqUq_KFtO9ZRcYGsAbrGTAaX0"
payload = security.decode_access_token(token)
print("before patload")
print(payload)
print("after payload")