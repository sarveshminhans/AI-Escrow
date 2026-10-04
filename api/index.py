import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient
app=Flask(__name__)
CORS(app)
usage_count=0
HOURLY_LIMIT=75
@app.route("/api/chat",methods=["POST"])
def chat():
 global usage_count
 try:
  data=request.get_json(silent=True) or {}
  user_message=data.get("message","").strip()
  if not user_message:return jsonify({"error":"No message provided","status":0}),400
  token=os.environ.get("HF_TOKEN")
  if not token:return jsonify({"error":"HF_TOKEN is not configured in Vercel.","status":0}),500
  if usage_count>=HOURLY_LIMIT:return jsonify({"error":"Rate limit reached. Please try again later.","status":0}),429
  usage_count+=1
  client=InferenceClient(api_key=token)
  full_response=""
  for message in client.chat_completion(model="openai/gpt-oss-20b",messages=[{"role":"user","content":user_message}],max_tokens=500,stream=True):
   delta=getattr(message.choices[0].delta,"content",None)
   if delta:full_response+=delta
  return jsonify({"status":1,"response":full_response})
 except Exception as e:return jsonify({"status":0,"error":str(e)}),500
