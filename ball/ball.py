"""
Interactive Unit Sphere – Great Circles (Dash + Plotly)
======================================================
Run:  python ball.py       →  opens at http://127.0.0.1:8050
"""

import numpy as np
import plotly.graph_objects as go
from dash import Dash, html, dcc, ctx, no_update, ALL, MATCH
from dash.dependencies import Input, Output, State
import json, uuid

# ── colour palette ──────────────────────────────────────────────────────
PALETTE = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#800000", "#aaffc3", "#808000",
    "#ffd8b1", "#000075", "#a9a9a9",
]

# ── math helpers ────────────────────────────────────────────────────────

def _random_unit() -> np.ndarray:
    v = np.random.randn(3)
    return v / np.linalg.norm(v)


def _great_circle(normal: np.ndarray, n_pts: int = 300):
    normal = normal / np.linalg.norm(normal)
    arb = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(normal, arb)) > 0.9:
        arb = np.array([0.0, 1.0, 0.0])
    u = np.cross(normal, arb);  u /= np.linalg.norm(u)
    v = np.cross(normal, u);    v /= np.linalg.norm(v)
    t = np.linspace(0, 2 * np.pi, n_pts)
    pts = np.outer(np.cos(t), u) + np.outer(np.sin(t), v)
    return pts[:, 0], pts[:, 1], pts[:, 2]


# ── base figure ─────────────────────────────────────────────────────────

def _base_traces():
    traces = []

    # Sphere surface
    nu, nv = 60, 40
    u = np.linspace(0, 2 * np.pi, nu)
    v = np.linspace(0, np.pi, nv)
    sx = np.outer(np.cos(u), np.sin(v))
    sy = np.outer(np.sin(u), np.sin(v))
    sz = np.outer(np.ones_like(u), np.cos(v))
    traces.append(go.Surface(
        x=sx, y=sy, z=sz, opacity=0.92,
        colorscale=[[0, "#4a4a6a"], [1, "#5a5a7a"]],
        showscale=False, name="_sphere",
        hovertemplate="Sphere Surface<extra></extra>",
    ))

    # Axis lines + labels
    span = 1.4
    for vec, col, lbl in [([1,0,0], "#ff4444", "X"),
                           ([0,1,0], "#44ff44", "Y"),
                           ([0,0,1], "#4488ff", "Z")]:
        d = np.array(vec, float)
        p0, p1 = -span * d, span * d
        traces.append(go.Scatter3d(
            x=[p0[0], p1[0]], y=[p0[1], p1[1]], z=[p0[2], p1[2]],
            mode="lines", line=dict(color=col, width=4),
            hoverinfo="skip", showlegend=False,
        ))
        tip = span * d * 1.12
        traces.append(go.Scatter3d(
            x=[tip[0]], y=[tip[1]], z=[tip[2]],
            mode="text", text=[lbl],
            textfont=dict(size=16, color=col, family="Arial Black"),
            hoverinfo="skip", showlegend=False,
        ))

    # Invisible clickable points on sphere
    n = 100
    u2 = np.linspace(0, 2 * np.pi, n)
    v2 = np.linspace(0.05, np.pi - 0.05, n)
    uu, vv = np.meshgrid(u2, v2)
    traces.append(go.Scatter3d(
        x=(np.cos(uu) * np.sin(vv)).ravel(),
        y=(np.sin(uu) * np.sin(vv)).ravel(),
        z=np.cos(vv).ravel(),
        mode="markers",
        marker=dict(size=1, opacity=0.05),
        hovertemplate="(%{x:.2f}, %{y:.2f}, %{z:.2f})<extra>click to place</extra>",
        showlegend=False, name="_clicksphere",
    ))

    return traces


SCENE = dict(
    xaxis=dict(range=[-1.6, 1.6], showbackground=False,
               gridcolor="#333355", color="#777799", title=""),
    yaxis=dict(range=[-1.6, 1.6], showbackground=False,
               gridcolor="#333355", color="#777799", title=""),
    zaxis=dict(range=[-1.6, 1.6], showbackground=False,
               gridcolor="#333355", color="#777799", title=""),
    aspectmode="cube",
    bgcolor="#1e1e2f",
    camera=dict(eye=dict(x=1.6, y=1.6, z=1.0)),
)


def _build_figure(circles, pick_pts=None):
    traces = _base_traces()
    if pick_pts:
        traces.append(go.Scatter3d(
            x=[p[0] for p in pick_pts],
            y=[p[1] for p in pick_pts],
            z=[p[2] for p in pick_pts],
            mode="markers",
            marker=dict(size=8, color="#ffffff",
                        line=dict(width=2, color="#000")),
            showlegend=False, hoverinfo="skip",
        ))
    for c in circles:
        norm = np.array(c["normal"])
        gx, gy, gz = _great_circle(norm)
        # Great circle line
        traces.append(go.Scatter3d(
            x=gx, y=gy, z=gz, mode="lines",
            line=dict(color=c["color"], width=5),
            name=c["name"], showlegend=False,
            hovertemplate=f"{c['name']}<extra></extra>",
        ))
        # Pole points (points normal to the circle on the sphere surface)
        # These are simply +/- the unit normal vector
        pole1 = norm / np.linalg.norm(norm)
        pole2 = -pole1
        traces.append(go.Scatter3d(
            x=[pole1[0], pole2[0]],
            y=[pole1[1], pole2[1]],
            z=[pole1[2], pole2[2]],
            mode="markers",
            marker=dict(size=10, color=c["color"], symbol="diamond",
                        line=dict(width=1, color="#fff")),
            showlegend=False,
            hovertemplate=f"{c['name']} Pole<extra></extra>",
        ))
    return go.Figure(data=traces, layout=go.Layout(
        scene=SCENE, paper_bgcolor="#1e1e2f",
        margin=dict(l=0, r=0, t=0, b=0),
        uirevision="persist",
    ))


def _build_list(circles):
    if not circles:
        return html.P("(none yet)", style={"color": "#666688",
                       "textAlign": "center", "marginTop": 20})
    items = []
    for c in circles:
        items.append(html.Div(style={
            "display": "flex", "alignItems": "center", "gap": 8,
            "padding": "7px 10px", "borderRadius": 6,
            "backgroundColor": "#2e2e4a", "marginBottom": 4,
        }, children=[
            html.Span("●", style={"color": c["color"], "fontSize": 20}),
            html.Span(c["name"], style={
                "flex": "1", "fontWeight": 600, "color": c["color"], "fontSize": 14,
            }),
            html.Button("✕", id={"type": "rm", "index": c["id"]}, n_clicks=0,
                        style={
                "border": "none", "background": "#e6194b", "color": "#fff",
                "borderRadius": 4, "cursor": "pointer", "fontWeight": 700,
                "padding": "3px 9px", "fontSize": 13,
            }),
        ]))
    return html.Div(items)


# ── Dash app ────────────────────────────────────────────────────────────

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Unit Sphere – Great Circles"

BTN = {
    "padding": "10px 0", "border": "none", "borderRadius": 6,
    "color": "#fff", "fontWeight": 700, "fontSize": 14,
    "cursor": "pointer", "letterSpacing": 0.5, "width": "100%",
}

app.layout = html.Div(style={
    "display": "flex", "height": "100vh",
    "fontFamily": "'Segoe UI', sans-serif",
    "backgroundColor": "#1e1e2f", "color": "#ccc", "overflow": "hidden",
}, children=[

    # 3-D viewport
    html.Div(style={"flex": "1", "position": "relative"}, children=[
        dcc.Graph(id="graph", figure=_build_figure([]),
                  style={"height": "100%"}, config={"scrollZoom": True}),
        html.Div(id="status", style={
            "position": "absolute", "top": 10, "left": 14,
            "color": "#aab", "fontSize": 13, "pointerEvents": "none",
        }),
    ]),

    # Sidebar
    html.Div(style={
        "width": 270, "backgroundColor": "#252540", "padding": "18px 14px",
        "display": "flex", "flexDirection": "column", "gap": 10,
        "borderLeft": "1px solid #3a3a5a", "overflowY": "auto",
    }, children=[
        html.H3("Great Circles", style={
            "margin": 0, "textAlign": "center", "color": "#eee",
        }),
        html.Hr(style={"borderColor": "#3a3a5a", "margin": "4px 0"}),
        html.Button("🎲  Add Random", id="btn-rand", n_clicks=0,
                     style={**BTN, "backgroundColor": "#3cb44b"}),
        html.Button("✏️  Draw (pick 2 pts)", id="btn-draw", n_clicks=0,
                     style={**BTN, "backgroundColor": "#4363d8"}),
        html.Hr(style={"borderColor": "#3a3a5a", "margin": "4px 0"}),
        html.Div(id="clist", children=_build_list([])),
    ]),

    # Stores
    dcc.Store(id="st-circles", data=[]),
    dcc.Store(id="st-cidx",    data=0),
    dcc.Store(id="st-cnt",     data=0),
    dcc.Store(id="st-draw",    data=False),
    dcc.Store(id="st-picks",   data=[]),
])


# ── single unified callback ────────────────────────────────────────────

@app.callback(
    Output("graph",    "figure"),
    Output("clist",    "children"),
    Output("status",   "children"),
    Output("btn-draw", "style"),
    Output("st-circles", "data"),
    Output("st-cidx",    "data"),
    Output("st-cnt",     "data"),
    Output("st-draw",    "data"),
    Output("st-picks",   "data"),

    Input("btn-rand",  "n_clicks"),
    Input("btn-draw",  "n_clicks"),
    Input("graph",     "clickData"),
    Input({"type": "rm", "index": ALL}, "n_clicks"),

    State("st-circles", "data"),
    State("st-cidx",    "data"),
    State("st-cnt",     "data"),
    State("st-draw",    "data"),
    State("st-picks",   "data"),
    prevent_initial_call=True,
)
def update(n_rand, n_draw, click_data, rm_clicks,
           circles, cidx, cnt, draw_mode, picks):

    trigger = ctx.triggered_id
    status = ""

    # ── Remove button ───────────────────────────────────────────────
    if isinstance(trigger, dict) and trigger.get("type") == "rm":
        rid = trigger["index"]
        removed_name = next((c["name"] for c in circles if c["id"] == rid), "?")
        circles = [c for c in circles if c["id"] != rid]
        status = f"Removed {removed_name}"

    # ── Add Random ──────────────────────────────────────────────────
    elif trigger == "btn-rand":
        draw_mode = False; picks = []
        normal = _random_unit().tolist()
        color = PALETTE[cidx % len(PALETTE)]; cidx += 1; cnt += 1
        circles.append(dict(id=str(uuid.uuid4()), name=f"GC-{cnt}",
                            normal=normal, color=color))
        status = f"Added GC-{cnt}  (random)"

    # ── Draw toggle ─────────────────────────────────────────────────
    elif trigger == "btn-draw":
        draw_mode = not draw_mode; picks = []
        status = "DRAW MODE — click two points on the sphere" if draw_mode else ""

    # ── Click on sphere ─────────────────────────────────────────────
    elif trigger == "graph" and draw_mode and click_data:
        pt = click_data.get("points", [{}])[0]
        x, y, z = pt.get("x"), pt.get("y"), pt.get("z")
        if x is not None:
            v_orig = np.array([x, y, z], float)
            n_orig = np.linalg.norm(v_orig)
            if n_orig > 0.01:
                v_unit = v_orig / n_orig
                # Snap to grid defined by n=200
                n_grid = 200
                phi = np.arctan2(v_unit[1], v_unit[0])
                theta = np.arccos(np.clip(v_unit[2], -1, 1))
                
                u2 = np.linspace(0, 2 * np.pi, n_grid)
                v2 = np.linspace(0.05, np.pi - 0.05, n_grid)
                
                # Nearest phi (u2)
                # Note: u2 is [0, 2pi]. phi is [-pi, pi].
                phi_mod = phi % (2 * np.pi)
                phi_idx = np.argmin(np.abs(u2 - phi_mod))
                phi_snapped = u2[phi_idx]
                
                # Nearest theta (v2)
                theta_idx = np.argmin(np.abs(v2 - theta))
                theta_snapped = v2[theta_idx]
                
                # Convert back to Cartesian
                x_s = np.cos(phi_snapped) * np.sin(theta_snapped)
                y_s = np.sin(phi_snapped) * np.sin(theta_snapped)
                z_s = np.cos(theta_snapped)
                v = [float(x_s), float(y_s), float(z_s)]
                
                picks.append(v)
                status = f"DRAW MODE — {len(picks)}/2 points selected"
                if len(picks) == 2:
                    p1, p2 = np.array(picks[0]), np.array(picks[1])
                    cross = np.cross(p1, p2)
                    cn = np.linalg.norm(cross)
                    if cn < 1e-8:
                        status = "Points too close / antipodal — pick again"
                        picks.pop()
                    else:
                        normal = (cross / cn).tolist()
                        color = PALETTE[cidx % len(PALETTE)]; cidx += 1; cnt += 1
                        circles.append(dict(id=str(uuid.uuid4()),
                                            name=f"GC-{cnt}",
                                            normal=normal, color=color))
                        status = f"Added GC-{cnt}  (drawn)"
                        draw_mode = False; picks = []

    # ── Build outputs ───────────────────────────────────────────────
    fig = _build_figure(circles, picks if draw_mode else None)
    draw_style = {**BTN, "backgroundColor": "#f0a030" if draw_mode else "#4363d8"}

    return (fig, _build_list(circles), status, draw_style,
            circles, cidx, cnt, draw_mode, picks)


if __name__ == "__main__":
    app.run(debug=True, port=8050)