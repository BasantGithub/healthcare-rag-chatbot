# This will handle requests from React and call Azure OpenAI.

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Telemetry imports
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler

load_dotenv()

# Azure OpenAI setup
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Application Insights connection string
app_insights_conn_str = os.getenv("APPINSIGHTS_CONNECTION_STRING")

# Azure AI Search setup
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
search_index = os.getenv("AZURE_SEARCH_INDEX")

app = Flask(__name__)
CORS(app)

# Attach middleware to automatically track requests
middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(connection_string=app_insights_conn_str),
    sampler=ProbabilitySampler(1.0),
)

# Clients
openai_client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=api_key,
)

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index,
    credential=AzureKeyCredential(search_key)
)

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question")

    # Step 1: Retrieve FAQ context from Azure AI Search
    results = search_client.search(user_question, top=3)
    context = "\n".join([doc["answer"] for doc in results])

    # Step 2: Generate grounded answer using Azure OpenAI
    response = openai_client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a clinical FAQ assistant. Use the provided context to answer."},
            {"role": "user", "content": f"Question: {user_question}\nContext: {context}"}
        ],
        max_completion_tokens=1024,
        temperature=0.3
    )

    answer = response.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
