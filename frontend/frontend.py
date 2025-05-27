import os
import time
from typing import Dict, List, Any

import reflex as rx
import httpx
from jose import jwt
from dotenv import load_dotenv
from fastapi import FastAPI


# Explicitly import dashboard
from frontend.pages.dashboard import dashboard
from frontend.states.queries import QueryAPI

# Load environment variables
load_dotenv()

# --- JWT Utility --- #
def generate_jwt() -> str:
    """Generate a JWT token using API_KEY."""
    payload = {
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "sub": "frontend",
    }
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not set")
    return jwt.encode(payload, api_key, algorithm="HS256")

# --- Application State --- #
class State(rx.State):
    method: str = "GET"
    url: str = os.getenv("MIDDLE_TIER_URL", "http://localhost:8000")
    headers: List[Dict[str, str]] = [{"key": "", "value": ""}]
    response_data: List[Dict[str, Any]] = []

    def add_header(self):
        self.headers.append({"key": "", "value": ""})

    def update_header(self, index: int, field: str, value: str):
        self.headers[index][field] = value

    def remove_header(self, index: int):
        if len(self.headers) > 1:
            self.headers.pop(index)

    async def get_data(self):
        headers = {
            h["key"]: h["value"] for h in self.headers if h["key"].strip() and h["value"].strip()
        }
        headers["X-API-Key"] = generate_jwt()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    self.method,
                    f"{self.url.rstrip('/')}/items/",
                    headers=headers,
                )
                response.raise_for_status()
                self.response_data = response.json()
        except httpx.HTTPError as e:
            self.response_data = [{"error": str(e)}]

    @rx.var
    def response_headers(self) -> List[str]:
        """Compute header keys for response_data."""
        return list(self.response_data[0].keys()) if self.response_data else []

# --- UI Components --- #
def header_input(index: int, field: str):
    return rx.input(
        value=State.headers[index][field],
        on_change=lambda value: State.update_header(index, field, value),
        placeholder=field.capitalize(),
        width="100%",
    )

def index():
    """API Request Demo page."""
    return rx.vstack(
        rx.heading("API Request Demo"),
        rx.select(
            ["GET", "POST", "PUT", "DELETE"],
            value=State.method,
            on_change=State.set_method,
            placeholder="Select HTTP Method",
        ),
        rx.input(
            value=State.url,
            on_change=State.set_url,
            placeholder="Enter API URL",
            width="100%",
        ),
        rx.vstack(
            rx.foreach(
                State.headers,
                lambda h, i: rx.hstack(
                    header_input(i, "key"),
                    header_input(i, "value"),
                    rx.button("Remove", on_click=lambda: State.remove_header(i)),
                    width="100%",
                ),
            ),
            rx.button("Add Header", on_click=State.add_header),
            width="100%",
        ),
        rx.button("Send Request", on_click=State.get_data),
        rx.cond(
            State.response_data,
            rx.box(
                # Header row
                rx.hstack(
                    rx.foreach(
                        State.response_headers,
                        lambda key: rx.text(
                            str(key),
                            font_weight="bold",
                            padding="0.5em",
                            border="1px solid #ddd",
                            flex="1",
                            text_align="center",
                        ),
                    ),
                    background_color="#f0f0f0",
                    width="100%",
                ),
                # Data rows
                rx.vstack(
                    rx.foreach(
                        State.response_data,
                        lambda row: rx.hstack(
                            rx.foreach(
                                row.values(),
                                lambda value: rx.text(
                                    str(value),
                                    padding="0.5em",
                                    border="1px solid #ddd",
                                    flex="1",
                                    text_align="center",
                                ),
                            ),
                            width="100%",
                        ),
                    ),
                    width="100%",
                ),
                padding="1em",
                border="1px solid #ddd",
                border_radius="8px",
                width="100%",
            ),
            rx.text("No data to display"),
        ),
        width="100%",
        padding="20px",
    )

# --- FastAPI for Health Endpoint --- #
fastapi_app = FastAPI()

@fastapi_app.get("/health")
@fastapi_app.get("/health/")
async def health():
    print("Health check endpoint was reached")
    return {"status": "ok"}

app = rx.App(api_transformer=fastapi_app)
app.add_page(dashboard, route="/", on_load=QueryAPI.run_get_request)
app.add_page(index, route="/demo")