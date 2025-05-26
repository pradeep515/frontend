import reflex as rx
import httpx
from typing import Dict, List, Any
from jose import jwt  # Added for JWT
import time  # Added for JWT
import os  # Added for environment variables
from dotenv import load_dotenv  # Already present

load_dotenv()  # Added to load environment variables

def generate_jwt():  # Added for JWT generation
    payload = {"exp": int(time.time()) + 3600, "iat": int(time.time()), "sub": "frontend"}
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not set in environment")
    return jwt.encode(payload, api_key, algorithm="HS256")

class State(rx.State):
    method: str = "GET"
    url: str = os.getenv("MIDDLE_TIER_URL", "http://localhost:8000")
    headers: List[Dict[str, str]] = [{"key": "", "value": ""}]
    response_data: Any = {}

    def add_header(self):
        self.headers.append({"key": "", "value": ""})

    def update_header(self, index: int, field: str, value: str):
        self.headers[index][field] = value

    def remove_header(self, index: int):
        if len(self.headers) > 1:
            self.headers.pop(index)

    async def get_data(self):
        headers = {h["key"]: h["value"] for h in self.headers if h["key"] and h["value"]}
        headers["X-API-Key"] = generate_jwt()  # Added to set JWT token
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    self.method, f"{self.url.rstrip('/')}/items/", headers=headers
                )
                response.raise_for_status()
                self.response_data = response.json()
            except httpx.HTTPError as e:
                self.response_data = {"error": str(e)}

def header_input(index: int, field: str):
    return rx.input(
        value=State.headers[index][field],
        on_change=lambda value: State.update_header(index, field, value),
        placeholder=field.capitalize(),
        width="100%"
    )

def index():
    return rx.vstack(
        rx.heading("API Request Demo"),
        rx.select(
            ["GET", "POST", "PUT", "DELETE"],
            value=State.method,
            on_change=State.set_method,
            placeholder="Select HTTP Method"
        ),
        rx.input(
            value=State.url,
            on_change=State.set_url,
            placeholder="Enter API URL",
            width="100%"
        ),
        rx.vstack(
            rx.foreach(
                State.headers,
                lambda h, i: rx.hstack(
                    header_input(i, "key"),
                    header_input(i, "value"),
                    rx.button("Remove", on_click=lambda: State.remove_header(i)),
                    width="100%"
                )
            ),
            rx.button("Add Header", on_click=State.add_header),
            width="100%"
        ),
        rx.button("Send Request", on_click=State.get_data),
        rx.cond(
            State.response_data,
            rx.table_container(
                rx.table(
                    rx.thead(
                        rx.tr(
                            rx.foreach(
                                lambda x: list(State.response_data[0].keys()) if State.response_data else [],
                                lambda key: rx.th(key)
                            )
                        )
                    ),
                    rx.tbody(
                        rx.foreach(
                            State.response_data,
                            lambda row: rx.tr(
                                rx.foreach(
                                    row.values(),
                                    lambda value: rx.td(str(value))
                                )
                            )
                        )
                    )
                )
            ),
            rx.text("No data to display")
        ),
        width="100%",
        padding="20px"
    )

app = rx.App()
app.add_page(index)