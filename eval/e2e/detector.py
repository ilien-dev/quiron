#!/usr/bin/env python3
"""Local AI-text detectors for evaluation (not part of the skill).

  detector.py FILES...   -> TSV: file, binoculars, desklib_p_ai   (cached by text hash)

Binoculars (Hans et al., ICML 2024): log-perplexity of the text under a performer model
divided by the cross-perplexity between observer and performer. Lower = more AI-like.
desklib/ai-text-detector-v1.01: DeBERTa-v3-large classifier; P(AI).
"""
import hashlib, json, os, re, sys
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, AutoModel, PreTrainedModel

H = os.environ.get("QUIRON_E2E", os.path.expanduser("~/.cache/quiron-e2e"))
CACHE = os.path.join(H, "detector-cache.jsonl")
OBS = os.environ.get("BINO_OBS", "Qwen/Qwen2.5-3B")
PERF = os.environ.get("BINO_PERF", "Qwen/Qwen2.5-3B-Instruct")
DEV = "cuda"


def strip(text):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # code is not prose
    return text.strip()


class DesklibModel(nn.Module):
    def __init__(self, name):
        super().__init__()
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        cfg = AutoConfig.from_pretrained(name)
        self.model = AutoModel.from_config(cfg)
        self.classifier = nn.Linear(cfg.hidden_size, 1)
        sd = load_file(hf_hub_download(name, "model.safetensors"))
        missing, unexpected = self.load_state_dict(sd, strict=False)
        assert not [m for m in missing if "classifier" in m], missing

    def forward(self, input_ids, attention_mask=None):
        out = self.model(input_ids, attention_mask=attention_mask)[0]
        m = attention_mask.unsqueeze(-1).expand(out.size()).float()
        pooled = (out * m).sum(1) / m.sum(1).clamp(min=1e-9)
        return self.classifier(pooled)


def load_cache():
    c = {}
    if os.path.exists(CACHE):
        for l in open(CACHE):
            d = json.loads(l)
            c[d["h"]] = d
    return c


@torch.inference_mode()
def binoculars(texts):
    tok = AutoTokenizer.from_pretrained(OBS)
    obs = AutoModelForCausalLM.from_pretrained(OBS, torch_dtype=torch.bfloat16).to(DEV).eval()
    perf = AutoModelForCausalLM.from_pretrained(PERF, torch_dtype=torch.bfloat16).to(DEV).eval()
    out = []
    for t in texts:
        ids = tok(t, return_tensors="pt", truncation=True, max_length=1024).input_ids.to(DEV)
        lo = obs(ids).logits[0, :-1].float()
        lp = perf(ids).logits[0, :-1].float()
        tgt = ids[0, 1:]
        ppl = nn.functional.cross_entropy(lp, tgt)  # log-ppl under performer
        xppl = (torch.softmax(lo, -1) * -torch.log_softmax(lp, -1)).sum(-1).mean()
        out.append(float(ppl / xppl))
    del obs, perf
    torch.cuda.empty_cache()
    return out


@torch.inference_mode()
def desklib(texts):
    name = "desklib/ai-text-detector-v1.01"
    tok = AutoTokenizer.from_pretrained(name)
    m = DesklibModel(name).to(DEV).eval()
    out = []
    for t in texts:
        enc = tok(t, return_tensors="pt", truncation=True, max_length=768, padding="max_length").to(DEV)
        out.append(float(torch.sigmoid(m(enc.input_ids, enc.attention_mask)).item()))
    del m
    torch.cuda.empty_cache()
    return out


def main(files):
    cache = load_cache()
    texts = {f: strip(open(f).read()) for f in files}
    hs = {f: hashlib.sha256((OBS + texts[f]).encode()).hexdigest()[:16] for f in files}
    todo = [f for f in files if hs[f] not in cache]
    if todo:
        b = binoculars([texts[f] for f in todo])
        d = desklib([texts[f] for f in todo])
        with open(CACHE, "a") as fh:
            for f, bb, dd in zip(todo, b, d):
                rec = {"h": hs[f], "bino": bb, "desklib": dd}
                cache[hs[f]] = rec
                fh.write(json.dumps(rec) + "\n")
    for f in files:
        r = cache[hs[f]]
        print(f"{f}\t{r['bino']:.4f}\t{r['desklib']:.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
