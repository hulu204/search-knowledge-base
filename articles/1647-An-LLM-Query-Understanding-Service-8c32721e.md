---
title: 'An LLM Query Understanding Service'
company: softwaredoug
tag: 查询理解
date: 2025-04-08
url: https://softwaredoug.com/blog/2025/04/08/llm-query-understand
account: 
origin: harvest3-202607
---
We need to be cheating at search with LLMs. Indeed [I’m teaching a whole course on this in July](https://maven.com/softwaredoug/cheat-at-search).

With an LLM we can implement in days what previously took months. We can take apart a query like “brown leather sofa” into the important dimensions of intent — “color: brown, material: leather, category:couches” etc. With this power [all search is structured now](https://softwaredoug.com/blog/2025/04/02/all-search-structured-now).

Even better we can do this all without calling out to OpenAI/Gemini/…. We can use simple LLMs running in *our infrastructure* making it faster and cheaper.

I’m going to show you how. Let’s get started. Follow along [in this repo](https://github.com/softwaredoug/llm-query-understanding).

## The service - wrapping an open source LLM

We’ll start by deploying a FastAPI app that calls an LLM.

The code below is just a dummy “hello world” app talking to an LLM. We send a chat message over JSON, the LLM comes up with a response and we send it back.

Here’s the basic service:

```
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from llm_query_understand.llm import LargeLanguageModel
from time import perf_counter

app = FastAPI()
llm = LargeLanguageModel()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("msg")
    response = llm.generate(prompt, max_length=100)
    resp = {
        "response": response,
        "prompt": prompt
    }
    return JSONResponse(content=resp)
```

And calling a light LLM (Qwen2-7B) via pytorch:

```
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")

class LargeLanguageModel:

    def __init__(self, device=DEVICE, model="Qwen/Qwen2-7B"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            torch_dtype=torch.float16,
            device_map="auto"
        ).to(self.device)
    
    def generate(self, prompt: str, max_length: int = 100):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        outputs = self.model.generate(inputs["input_ids"], max_length=max_length)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## The Docker Image

To create a kubernetes pod, we need a Docker image with our app. One dependency is a headache with Docker - PyTorch. Luckily someone has written a great article on [shrinking pytorch images](https://mveg.es/posts/optimizing-pytorch-docker-images-cut-size-by-60percent/), which is a great starting point for [our Dockerfile](https://github.com/softwaredoug/llm-query-understanding/blob/main/Dockerfile).

OK now to build and upload to GCR - Google’s Container Registry - so our pod can pull the container. There’s a handy [scripts/publish\_gcp.sh](https://github.com/softwaredoug/llm-query-understanding/blob/main/scripts/publish_gcp.sh) script in the repo. I recommend running that script if you’re getting started, as it executes the steps in this article.

We build an amd64 image and publish it:

```
PLATFORM="linux/amd64"
GCP_PROJECT_ID=$(gcloud config get-value project)
docker buildx build --platform $PLATFORM -t "gcr.io/$GCP_PROJECT_ID/fastapi-gke:latest" .
docker push "gcr.io/$GCP_PROJECT_ID/fastapi-gke:latest"
```

## Setting up GKE autopilot mode

If you have a Google Cloud account, create a Google Kubernetes Engine cluster with default settings. Now you have an autopilot cluster! Congrats you know Kubernetes 🎉.

(If you don’t have a Google Cloud account, you can [create one and get $300 of credits](https://cloud.google.com/free/docs/free-cloud-features))

Normally with kubernetes, you’d manually allocate nodes to your cluster. GKE’s Autopilot does this for you, though may take a few minutes to spin up a VM as it finds compute for you.

With that in mind, let’s look at my kubernetes deployment ([source here](https://github.com/softwaredoug/llm-query-understanding/blob/main/k8s/deployment.yaml))

The first part here sets up a deployment of the image

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-query-understand
  namespace: softwaredoug-training
spec:
  replicas: 1
  selector:
    matchLabels:
      app: llm-query-understand
  template:
    metadata:
      labels:
        app: llm-query-understand
    spec:
      containers:
      - name: fastapi
        image: gcr.io/YOUR_PROJECT_ID/fastapi-gke:latest   # <- what we just pushed up to GCR
        ports:
        - containerPort: 80         # <- expose port 80
```

Then, adding the needed resources:

```
        resources:
          requests:
            memory: "32Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
          limits:
            memory: "32Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
```

OK good enough - we want a machine with 32 GB RAM, 2 CPUs, and a single GPU.

Finally to ensure we are scheduled correctly, we need some [node selectors specific to GKE](https://cloud.google.com/kubernetes-engine/docs/how-to/autopilot-gpus):

```
 nodeSelector:
        # Ensure your GPU quotas allow you to have a compute
        # instance with a GPU
        cloud.google.com/compute-class: "Accelerator"
        cloud.google.com/gke-accelerator-count: "1"
        cloud.google.com/gke-accelerator: "nvidia-l4"
```

If you deploy this, however, you might notice problems. If you ask kubernetes to describe your pod:

```
kubectl get pods
<your-pod-name> ... # Grab this for describe
```

And

```
kubectl describe pod <your-pod-name>
```

You may notice your pod doesn’t get allocated to the right node. You may see a message at the bottom like:

```
GCE quota exceeded. Pod is at risk of not being scheduled.
```

**You MUST ensure you have a GPU in your compute quota**.

Go to the google cloud console, make sure you’ve got a GPU allocated. [Request a GPU here](https://stackoverflow.com/questions/45227064/how-to-request-gpu-quota-increase-in-google-cloud)

![image.png](/assets/media/2025/quota.png)

### Service deployment

The [service itself](https://github.com/softwaredoug/llm-query-understanding/blob/main/k8s/service.yaml) is rather boring in kubernetes terms, ensuring we expose port 80:

```
apiVersion: v1
kind: Service
metadata:
  name: llm-query-understand
  namespace: softwaredoug-training
spec:
  type: LoadBalancer
  selector:
    app: llm-query-understand
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

### Persistent volume for model storage

If you did just the above, your service would start, but you would quickly run into an issue - storage for models would run out. So in addition to the above, I’ve added a persistent volume claim to store model data, mounted to huggingface’s cache:

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-cache-pvc
  namespace: softwaredoug-training
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 40Gi
```

You’ll notice in [the deployment](https://github.com/softwaredoug/llm-query-understanding/blob/main/k8s/deployment.yaml) the reference to these, mounted to hugging face’s directories:

```
        volumeMounts:
          - name: model-cache
            mountPath: /root/.cache/huggingface
            
      ...      
      
      volumes:
        - name: model-cache
          persistentVolumeClaim:
            claimName: model-cache-pvc
```

### Deploy!

As in [the deployment script](https://github.com/softwaredoug/llm-query-understanding/blob/main/scripts/publish_gcp.sh), all of the above will be applied to the cluster via:

```
kubectl --context="$K8S_CONTEXT" apply -f k8s/pvc.yaml
kubectl --context="$K8S_CONTEXT" apply -f k8s/.deployment.yaml
kubectl --context="$K8S_CONTEXT" apply -f k8s/service.yaml
```

### Monitor, Inspect

Check out the pods

```
kubectl get pods -n softwaredoug-training
```

See if the pod is being allocated correctly, watch kuberenetes do its thing (first time you run this with autopilot, it’ll take a while to spin up the new GPU node)

```
kubectl describe pod llm-query-understand-bac44f44c-4fzvt -n softwaredoug-training
```

```
  Normal  Scheduled               7m59s  gke.io/optimize-utilization-scheduler  Successfully assigned ...
  Normal  SuccessfulAttachVolume  7m50s  attachdetach-controller                AttachVolume.Attach succeeded for volume "..."
  Normal  Pulling                 7m47s  kubelet                                Pulling image "gcr.io/<project id>/fastapi-gke:latest"
  Normal  Pulled                  7m47s  kubelet                                Successfully pulled image "gcr.io/<project id>/fastapi-gke:latest" in 351ms (351ms including waiting). Image size: X bytes.
  Normal  Created                 7m47s  kubelet                                Created container: fastapi
  Normal  Started                 7m47s  kubelet                                Started container fastapi
```

And the application logs of course:

```
kubectl logs llm-query-understand-bac44f44c-4fzvt -n softwaredoug-training                                        llm-query-understanding$
```

## Hello agent!

Once deployed, we can chat with the model directly. It’s not a query understanding service yet. It’s just an LLM:

```
(main) $ curl -XPOST http://34.123.86.214/chat -d '{"msg": "Tell me something that happened in the 19th century in Spain"}'

{"generation_time":7.378469640010735,"response":"Tell me something that happened in the 19th century in Spain.\nOne sig
nificant event that occurred in Spain during the 19th century was the Spanish-American War. This conflict took place be
tween Spain and the United States from 1898 to 1899 and resulted in Spain's loss of its colonies in the Americas, inclu
ding Cuba, Puerto Rico, and the Philippines. The war was sparked by a series of events, including the explosion of the 
USS Maine in Havana Harbor, which led to the United States declaring war on Spain. The war had a significant impact on 
Spain's international standing and marked the end of its colonial empire in the Americas.","prompt":"Tell me something 
that happened in the 19th century in Spain"}%
```

## Add a cache - valkey

A cache is absolutely essential. We can’t be hitting the LLM every time we have a query. As long as prompt + query are the same, our results should be highly cacheable.

We’ll need to add a deployment for valkey for caching the LLM, let’s do that, [with valkey.yaml](https://github.com/softwaredoug/llm-query-understanding/blob/main/k8s/valkey.yaml). A pretty boilerplate pod / service. (Probably needs more memory).

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: val-key
  namespace: softwaredoug-training
spec:
  replicas: 1
  selector:
    matchLabels:
      app: val-key
  template:
    metadata:
      labels:
        app: val-key
    spec:
      containers:
      - name: val-key
        image: valkey/valkey:latest
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: val-key
  namespace: softwaredoug-training
spec:
  selector:
    app: val-key
  ports:
  - name: redis
    port: 6379
    targetPort: 6379
  type: ClusterIP
```

## Refactor app to a query understanding service

Let’s change the service to something less generic to something that takes a *search query* and offers a structured response (theunderstood query)

We’ll create a general prompt to use, here for furniture:

```
PROMPT = """
You are a helpful assistant. You will be given a search query and you need to parse furniture searches it into a structured format. The structured format should include the following fields:

    - item type - the core thing the user wants (sofa, table, chair, etc.)
    - material - the material of the item (wood, metal, plastic, etc.)
    - color - the color of the item (red, blue, green, etc.)

    Respond with a single line of JSON:

        {"item_type": "sofa", "material": "wood", "color": "red"}

    Omit any other information. Do not include any other text in your response. Omit a value if the user did not specify it. For example, if the user said "red sofa", you would respond with:

        {"item_type": "sofa", "color": "red"}

Here is the search query: """
```

We’ll adapt our request to use this + the query for the PROMPT, notice the interface changes to accept “query”. We take the output, try to parse it as JSON, and take a response

```
@app.post("/parse")  # CHANGED
async def q_understand(request: Request):  # RENAMED
	  print("Received request")
    body = await request.json()
    query = body.get("query")
		prompt = PROMPT + query

    response = llm.generate(prompt, max_length=100)
    generation_time = perf_counter() - start
    print(f"Generation time: {generation_time:.2f} seconds")
    parsed_query_as_json = response.split("\n")[-1]
    try:
        parsed_query_as_json = json.loads(parsed_query_as_json)
    except json.JSONDecodeError:
        return JSONResponse(status_code=500, content={"error": "Failed to parse response from LLM"})
    print(f"Parsed query: {parsed_query_as_json}")
    resp = {
        "generation_time": generation_time,
        "response": response,
        "prompt": prompt,
        "query": query,
        "parsed_query": parsed_query_as_json,
    }
    return JSONResponse(content=resp)
```

After a curl, we get the response:

```
$ curl  -XPOST http://34.42.78.184/parse   \
    -H "Content-Type: application/json" 
    -d '{"query": "red loveseat"}' | jq '.'
 {
  "generation_time": 1.0570514019927941,
  "response": "\nYou are a helpful assistant. You will be given a search query and you need to parse furniture searches it into a structured format.
 The structured format should include the following fields:\n\n    - item type - the core thing the user wants (sofa, table, chair, etc.)\n    - mat
erial - the material of the item (wood, metal, plastic, etc.)\n    - color - the color of the item (red, blue, green, etc.)\n\n    Respond with a si
ngle line of JSON:\n\n        {\"item_type\": \"sofa\", \"material\": \"wood\", \"color\": \"red\"}\n\n    Omit any other information. Do not includ
e any other text in your response. Omit a value if the user did not specify it. For example, if the user said \"red sofa\", you would respond with:\
n\n        {\"item_type\": \"sofa\", \"color\": \"red\"}\n\nHere is the search query: red loveseat\n\n{\"item_type\": \"loveseat\", \"color\": \"red
\"}",
  "prompt": "\nYou are a helpful assistant. You will be given a search query and you need to parse furniture searches it into a structured format. T
he structured format should include the following fields:\n\n    - item type - the core thing the user wants (sofa, table, chair, etc.)\n    - mater
ial - the material of the item (wood, metal, plastic, etc.)\n    - color - the color of the item (red, blue, green, etc.)\n\n    Respond with a sing
le line of JSON:\n\n        {\"item_type\": \"sofa\", \"material\": \"wood\", \"color\": \"red\"}\n\n    Omit any other information. Do not include 
any other text in your response. Omit a value if the user did not specify it. For example, if the user said \"red sofa\", you would respond with:\n\
n        {\"item_type\": \"sofa\", \"color\": \"red\"}\n\nHere is the search query: red loveseat",
  "query": "red loveseat",
  "parsed_query": {
    "item_type": "loveseat",
    "color": "red"
  }
}
```

The important part here being `parsed_query`

### Finally, use the cache!

Of course, we’ll repeat the same queries over and over, so the caching is crucial. We’ll cache based on the prompt and the query:

```
@app.post("/parse")
async def q_understand(request: Request):
    print("Received request")
    body = await request.json()
    query = body.get("query")
    
    cache_key = f"query:{PROMPT_HASH}:{query}"
    cached_response = r.get(cache_key)
    if cached_response:
        json_response = json.loads(cached_response)
        json_response["cached"] = True
        return JSONResponse(content=json_response)

    prompt = PROMPT + query

    response = llm.generate(prompt, max_length=100)
    generation_time = perf_counter() - start
    parsed_query_as_json = response.split("\n")[-1]
    try:
        parsed_query_as_json = json.loads(parsed_query_as_json)
    except json.JSONDecodeError:
        return JSONResponse(status_code=500, content={"error": "Failed to parse response from LLM"})
    print(f"Parsed query: {parsed_query_as_json}")
    resp = {
        "cached": False,
        "generation_time": generation_time,
        "response": response,
        "prompt": prompt,
        "query": query,
        "parsed_query": parsed_query_as_json,
    }
    r.set(cache_key, json.dumps(resp), ex=3600)
    return JSONResponse(content=resp)
```

### Iterate and improve

Now you’re setup to start making progress! What is next?

1. **Load testing** - how many QPS can you take? Where does this break down? How much caching do you need? Should the LLM run on its own hardware separate from the service so it doesn’t block HTTP requests?
2. **Prompt tuning -** what important attributes of your query matter? How do they map to your search system? Is there external knowledge (taxonomies, etc) we need to inject so we map into known categories?

There’s quite a lot we can do!

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---