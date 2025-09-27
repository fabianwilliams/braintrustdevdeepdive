import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import braintrust
from braintrust import init_logger, wrap_openai

load_dotenv()

def _frontier_client():
    import openai
    project = os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")
    os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{project}")
    init_logger(project=project)
    client = wrap_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")))
    model = os.getenv("FRONTIER_MODEL", "gpt-4o-mini")
    return client, model

def _local_client():
    import openai
    project = os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")
    os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{project}")
    init_logger(project=project)
    client = wrap_openai(
        openai.OpenAI(
            base_url=os.getenv("LOCAL_OPENAI_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "ollama"),
        )
    )
    model = os.getenv("LOCAL_OPENAI_MODEL", "gpt-oss:120b")
    return client, model

def _openai_client():
    return _local_client() if os.getenv("USE_LOCAL_MODEL", "false").lower() == "true" else _frontier_client()

def mock_weather_api(city: str, date: str):
    return {"forecast": random.choice(["sunny", "rainy", "cloudy"]), "date": date, "city": city}

def mock_flight_api(origin: str, dest: str):
    return {"price": random.randint(200, 800), "origin": origin, "dest": dest}

def extract_city(query: str) -> str:
    for token in query.replace("?", "").split():
        if token.istitle():
            return token
    return "Paris"

def extract_route(query: str):
    words = query.replace(",", " ").split()
    origin = words[3] if len(words) > 3 else "NYC"
    dest = words[5] if len(words) > 5 else "London"
    return origin, dest

def plan_trip(query: str) -> str:
    client, model = _openai_client()

    decision = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"User query: '{query}'. Choose one: 'weather', 'flight', or 'both'."}],
        temperature=0.0,
    ).choices[0].message.content.strip().lower()

    result = {}
    if "weather" in decision:
        city = extract_city(query)
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result["weather"] = mock_weather_api(city, date)
    if "flight" in decision:
        origin, dest = extract_route(query)
        result["flight"] = mock_flight_api(origin, dest)

    braintrust.trace({"name": "tool-results", "input": {"query": query, "decision": decision}, "output": result})

    judgment = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"Given results {result}, did I choose unnecessary actions? Reply 'yes' or 'no'."}],
        temperature=0.0,
    ).choices[0].message.content.strip().lower()

    return f"Decision: {decision}. Judgment unnecessary actions: {judgment}. Results: {result}."
