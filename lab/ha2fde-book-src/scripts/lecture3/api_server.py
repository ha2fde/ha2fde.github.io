# -*- coding: utf-8 -*-
"""
第 9 章: 怎么让别的程序用上它? —— 本地 Chat Completions 兼容服务
输入: HTTP POST /v1/chat/completions  JSON: {model, messages, stream}
输出: 非流式 -> choices JSON; 流式 -> SSE 逐 token 推送(delta) + data: [DONE]
运行: pip install torch transformers fastapi uvicorn
      python api_server.py   (默认 http://127.0.0.1:8000)

curl 示例(非流式):
  curl http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"qwen\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}"

curl 示例(流式, 逐字返回):
  curl http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"qwen\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}],\"stream\":true}"

说明: 字段与 OpenAI 契约对齐; 现有 OpenAI 客户端只需把 base_url 指向本服务
"""
import json
import time
import uuid
from threading import Thread

# import os; os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

print(f"加载模型 {MODEL} ...")
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL)
app = FastAPI(title="Local Chat Completions")


class ChatRequest(BaseModel):
    model: str = "qwen"
    messages: list
    stream: bool = False
    max_tokens: int = 512
    temperature: float = 0.7


def build_inputs(messages):
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return tok(text, return_tensors="pt")


def sse_chunk(content, model_name, finish=False):
    """按 OpenAI 流式格式组装一条 SSE 事件"""
    payload = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{
            "index": 0,
            "delta": {} if finish else {"content": content},
            "finish_reason": "stop" if finish else None,
        }],
    }
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    ids = build_inputs(req.messages)
    do_sample = req.temperature > 0
    gen_kwargs = dict(max_new_tokens=req.max_tokens,
                      do_sample=do_sample,
                      temperature=req.temperature if do_sample else None,
                      top_p=0.9 if do_sample else None)

    if not req.stream:
        out = model.generate(**ids, **gen_kwargs)
        answer = tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": answer},
                "finish_reason": "stop",
            }],
        }

    def stream():
        streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)
        kwargs = {**ids, **gen_kwargs, "streamer": streamer}
        Thread(target=model.generate, kwargs=kwargs, daemon=True).start()
        for piece in streamer:                       # 模型每出一个 token
            yield sse_chunk(piece, req.model)        # 就推一条 SSE 事件
        yield sse_chunk("", req.model, finish=True)
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/v1/models")
def models():
    return {"object": "list", "data": [
        {"id": req_model, "object": "model", "created": int(time.time()), "owned_by": "local"}
        for req_model in [MODEL, "qwen"]
    ]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
