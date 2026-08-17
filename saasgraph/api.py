from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .engine import assess, blast_radius
from .fixtures import apps
from .report import build_report

app = FastAPI(title="SaaSGraph", version="0.1.0")


def _inventory():
    return {item.app_id: item for item in apps()}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "saasgraph"}


@app.get("/report")
def report():
    return build_report()


@app.get("/apps")
def list_apps():
    return [assess(item).to_dict() for item in apps()]


@app.get("/apps/{app_id}")
def app_assessment(app_id: str):
    item = _inventory().get(app_id)
    if item is None:
        raise HTTPException(status_code=404, detail="application not found")
    return {"assessment": assess(item).to_dict(), "blast_radius": blast_radius(item)}


@app.get("/", response_class=HTMLResponse)
def dashboard():
    report = build_report()
    summary = report["summary"]
    rows = "".join(
        f"<tr><td>{item['name']}</td><td>{item['risk_level']}</td><td>{item['risk_score']}</td><td>{item['users_exposed']}</td><td>{item['api_ratio']}x</td></tr>"
        for item in report["assessments"]
    )
    return f'''<!doctype html>
<html><head><title>SaaSGraph</title><style>
body{{font-family:Inter,system-ui;background:#07111f;color:#e5eef9;margin:0;padding:32px}}
.wrap{{max-width:1100px;margin:auto}} h1{{font-size:40px;margin-bottom:4px}}
.sub{{color:#94a3b8;margin-bottom:28px}} .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
.card{{background:#0f1c2e;border:1px solid #22344d;border-radius:14px;padding:18px}}
.k{{color:#8da2bd;font-size:13px}} .v{{font-size:30px;font-weight:700;margin-top:6px}}
table{{width:100%;border-collapse:collapse;margin-top:26px;background:#0f1c2e;border-radius:14px;overflow:hidden}}
th,td{{padding:13px;text-align:left;border-bottom:1px solid #22344d}} th{{color:#8da2bd}}
code{{color:#7dd3fc}}
</style></head><body><div class="wrap">
<h1>SaaSGraph</h1><div class="sub">OAuth & third-party SaaS exposure workbench · synthetic defensive lab</div>
<div class="grid"><div class="card"><div class="k">Applications</div><div class="v">{summary['applications']}</div></div>
<div class="card"><div class="k">Critical</div><div class="v">{summary['critical']}</div></div>
<div class="card"><div class="k">High risk</div><div class="v">{summary['high_risk']}</div></div>
<div class="card"><div class="k">Mean risk</div><div class="v">{summary['mean_risk_score']}</div></div></div>
<table><thead><tr><th>Application</th><th>Decision</th><th>Risk</th><th>Users</th><th>API vs baseline</th></tr></thead><tbody>{rows}</tbody></table>
<p class="sub">API: <code>/report</code> · <code>/apps</code> · <code>/apps/{{app_id}}</code> · <code>/docs</code></p>
</div></body></html>'''
