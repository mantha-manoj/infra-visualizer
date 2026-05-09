from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import hcl2
import yaml
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Infra Visualizer Running"}


# -----------------------------------
# Terraform Upload
# -----------------------------------
@app.post("/upload")
async def upload_tf(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8").replace("\r\n", "\n")

    parsed = hcl2.loads(text)

    nodes = []
    edges = []
    resource_map = {}

    node_id = 1
    compute_y = 80
    db_y = 80

    # AWS Cloud container
    nodes.append({
        "id": "aws-cloud",
        "data": {"label": "AWS Cloud"},
        "position": {"x": 200, "y": 50},
        "style": {
            "width": 1000,
            "height": 700,
            "background": "#dbeafe",
            "border": "3px solid #0284c7",
            "borderRadius": 12
        }
    })

    # Compute group
    nodes.append({
        "id": "compute-group",
        "data": {"label": "Compute Layer"},
        "position": {"x": 50, "y": 80},
        "parentNode": "aws-cloud",
        "extent": "parent",
        "style": {
            "width": 420,
            "height": 550,
            "background": "#dcfce7",
            "border": "2px solid #16a34a",
            "borderRadius": 10
        }
    })

    # Database group
    nodes.append({
        "id": "database-group",
        "data": {"label": "Database Layer"},
        "position": {"x": 520, "y": 80},
        "parentNode": "aws-cloud",
        "extent": "parent",
        "style": {
            "width": 420,
            "height": 550,
            "background": "#fee2e2",
            "border": "2px solid #dc2626",
            "borderRadius": 10
        }
    })

    for resource in parsed.get("resource", []):
        for resource_type, instances in resource.items():
            for resource_name, resource_values in instances.items():

                nid = str(node_id)
                full_name = f"{resource_type}.{resource_name}"
                resource_map[full_name] = nid

                parent = "compute-group"
                x = 100
                y = compute_y

                if "db" in resource_type or "rds" in resource_type:
                    parent = "database-group"
                    y = db_y
                    db_y += 140
                else:
                    y = compute_y
                    compute_y += 140

                nodes.append({
                    "id": nid,
                    "data": {"label": resource_type},
                    "position": {"x": x, "y": y},
                    "parentNode": parent,
                    "extent": "parent"
                })

                node_id += 1

    # Dependency edges
    for resource in parsed.get("resource", []):
        for resource_type, instances in resource.items():
            for resource_name, resource_values in instances.items():

                current = f"{resource_type}.{resource_name}"
                current_id = resource_map[current]

                refs = re.findall(
                    r"(aws_[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)",
                    str(resource_values),
                )

                for ref in refs:
                    if ref in resource_map:
                        edges.append({
                            "id": f"{resource_map[ref]}-{current_id}",
                            "source": resource_map[ref],
                            "target": current_id,
                        })

    return {"nodes": nodes, "edges": edges}


# -----------------------------------
# Kubernetes Upload
# -----------------------------------
@app.post("/upload-k8s")
async def upload_k8s(file: UploadFile = File(...)):
    content = await file.read()
    data = yaml.safe_load_all(content.decode())

    nodes = []
    edges = []

    prev = None
    node_id = 1
    y = 100

    for item in data:
        if not item:
            continue

        kind = item.get("kind", "Unknown")
        nid = str(node_id)

        nodes.append({
            "id": nid,
            "data": {"label": kind},
            "position": {"x": 200, "y": y},
        })

        if prev:
            edges.append({
                "id": f"{prev}-{nid}",
                "source": prev,
                "target": nid,
            })

        prev = nid
        y += 150
        node_id += 1

    return {"nodes": nodes, "edges": edges}


# -----------------------------------
# Explain Architecture
# -----------------------------------
@app.post("/explain")
async def explain_architecture(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    explanation = ""

    if file.filename.endswith(".tf"):
        parsed = hcl2.loads(text)

        resources = []

        for resource in parsed.get("resource", []):
            for resource_type, instances in resource.items():
                for _ in instances.keys():
                    resources.append(resource_type)

        explanation = (
            f"This Terraform architecture contains: "
            f"{', '.join(resources)}. "
            f"It provisions AWS resources automatically."
        )

    else:
        docs = list(yaml.safe_load_all(text))

        resources = []

        for doc in docs:
            if doc:
                resources.append(doc.get("kind", "Unknown"))

        explanation = (
            f"This Kubernetes manifest contains: "
            f"{', '.join(resources)}. "
            f"It defines Kubernetes resources for deployment."
        )

    return {"explanation": explanation}