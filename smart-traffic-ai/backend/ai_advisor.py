"""
AI 出行顾问
============
两层设计：
1. 检索层（始终可用）：从本地知识库 knowledge.json 按关键词检索，离线可跑。
2. 大模型层（可插拔）：配置了环境变量则调用 OpenAI 兼容接口增强回答；
   未配置时自动降级为检索结果，保证 Demo 永不失败。

配置方式（写在 .env / 环境变量，切勿把 key 提交到 git）：
  LLM_API_KEY=sk-xxxx
  LLM_BASE_URL=https://api.openai.com/v1   # 或任意兼容网关
  LLM_MODEL=gpt-4o-mini
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge.json"

_STOPWORDS = {"的", "了", "吗", "呢", "怎么", "如何", "什么", "请问", "我想", "一下", "去", "到", "在"}


def _tokenize(text: str) -> set[str]:
    """简易中文检索：2-gram 切片 + 关键词命中，不依赖分词库。"""
    grams = set()
    for i in range(len(text) - 1):
        grams.add(text[i:i + 2])
    grams |= {w for w in _STOPWORDS if w in text}
    return grams


def retrieve(question: str, knowledge: list[dict], top_k: int = 2) -> list[dict]:
    q_grams = _tokenize(question)
    scored = []
    for item in knowledge:
        score = sum(1 for kw in item.get("keywords", []) if kw in question)
        score += len(q_grams & _tokenize(item.get("answer", ""))) * 0.15
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: -x[0])
    return [it for _, it in scored[:top_k]]


def _llm_enabled() -> bool:
    return bool(os.environ.get("LLM_API_KEY"))


def _call_llm(system: str, user: str, timeout: int = 12) -> str | None:
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
        "max_tokens": 512,
    }).encode("utf-8")
    req = urllib.request.Request(
        base + "/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['LLM_API_KEY']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
        return None


SYSTEM_PROMPT = (
    "你是重庆智慧交通出行助手，服务来渝游客。回答要具体、口语化、给出可执行建议，"
    "涉及拥堵、路线时以系统提供的路况数据为准，不要编造数据。150 字以内。"
)


def answer(question: str, knowledge: list[dict], context: str = "") -> dict:
    """返回 {answer, source, hits}。source: 'llm' | 'retrieval'"""
    hits = retrieve(question, knowledge)
    context_text = "\n".join(f"- {h['answer']}" for h in hits) or "- 暂无相关知识条目"

    if _llm_enabled():
        user_msg = (
            f"参考资料（据此回答，勿编造）：\n{context_text}\n\n"
            f"实时路况摘要：\n{context or '暂无'}\n\n用户问题：{question}"
        )
        llm_out = _call_llm(SYSTEM_PROMPT, user_msg)
        if llm_out:
            return {"answer": llm_out, "source": "llm", "hits": [h["id"] for h in hits]}

    # 降级：检索式回答
    if hits:
        body = "\n\n".join(h["answer"] for h in hits)
    else:
        body = ("这个问题我暂时没有把握，可以换个说法，比如问「洪崖洞什么时候去不堵」"
                "或「从北站去磁器口怎么走」。也可以直接用右侧的 AI 路线规划。")
    return {"answer": body, "source": "retrieval", "hits": [h["id"] for h in hits]}
