# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
from weather_service import WeatherService
from config import Config
import json
import os
import asyncio

HISTORY_FILE = "search_history.json"
MAX_HISTORY = 8 # max search history

class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history = self.load_history()
        self.setup_page()
        self.build_ui()
        self.current_unit = "metric"        # default to metric (°C, m/s)
        self.current_temp = 0               # current temperature in the active unit
        self.current_feels_like = 0
        self.current_wind_speed = 0
        self.current_data = None            # store full weather data for reuse
    
    # json file functions
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self, hist):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, ensure_ascii=False)

    def add_to_history(self, city: str):
        city = city.strip().title()
        if not city or city in self.history:
            return
        self.history.insert(0, city)          # newest on top
        self.history = self.history[:10]      # keep only last 10
        self.save_history(self.history)                 

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )

        # Custom theme Colors
        self.page.padding = 20
            
        # Window properties are accessed via page.window object in Flet 0.28.3
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False

        # Center the window on desktop
        self.page.window.center()
    
    def select_city(self, city: str):
        city = city.strip().title()
        if not city:
            return

        # Set the search bar value and close dropdown
        self.city_input.value = city
        self.city_input.close_view(city)

        if city in self.history:
            self.history.remove(city)
        self.history.insert(0, city)
        self.history = self.history[:MAX_HISTORY]
        self.save_history(self.history)
        self.refresh_history()

        self.page.run_task(self.get_weather)  

    def refresh_history(self):
        self.history_column.controls = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.HISTORY),
                title=ft.Text(city),
                on_click=lambda e, c=city: self.select_city(c),

            )
            for city in self.history[:MAX_HISTORY]
        ]
        
        self.history_column.update()

    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        search_view_constraints = ft.BoxConstraints(
            max_height=164,
        )
        self.history_column = ft.Column()
        
        # City input field
        self.city_input = ft.SearchBar(
            view_elevation=8,
            bar_hint_text="Enter city name",
            view_hint_text="Your recent searches",
            on_tap=lambda e: self.city_input.open_view(),
            on_submit=self.on_search_async,
            
            view_size_constraints=search_view_constraints, 
            
            controls=[
                ft.Column(
                    controls=[self.history_column],
                    scroll=ft.ScrollMode.ADAPTIVE 
                )
            ]
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search_async,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            self.title,
                            self.theme_button
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    self.search_button,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

        self.refresh_history() # populate the listTile
        
    async def on_search_async(self, e):
        """Async event handler."""
        await self.get_weather()
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()

        # add city to json file
        self.add_to_history(city)
        self.refresh_history() # refresh listTile when new city is added
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Display weather
            await self.display_weather(weather_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()

    # Toggle theme
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    # temp toggle
    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit + update display."""
        if not self.current_data:
            return  # no data yet

        # Toggle unit
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"

        # Re-display weather with new units
        self.page.run_task(self.display_weather, self.current_data)

    async def display_weather(self, data: dict):
        """Display weather information and store data for unit conversion."""
        # Store the raw data and values
        self.current_data = data
        
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_c = data.get("main", {}).get("temp", 0)
        feels_like_c = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed_ms = data.get("wind", {}).get("speed", 0)

        # Convert wind speed: m/s → mph when imperial
        wind_speed = wind_speed_ms * 3.6 if self.current_unit == "imperial" else wind_speed_ms
        wind_unit = "km/h" if self.current_unit == "imperial" else "m/s"

        # Set temperature based on current unit
        if self.current_unit == "metric":
            temp = temp_c
            feels_like = feels_like_c
            temp_unit = "C"
        else:
            temp = (temp_c * 9/5) + 32
            feels_like = (feels_like_c * 9/5) + 32
            temp_unit = "F"

        # Store current displayed values
        self.current_temp = temp
        self.current_feels_like = feels_like
        self.current_wind_speed = wind_speed

        # Build UI
        self.weather_container.content = ft.Column(
            [
                # Location + Unit Toggle Button
                ft.Row(
                    [
                        ft.Text(
                            f"{city_name}, {country}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.THERMOSTAT,
                            tooltip="Toggle °C / °F",
                            on_click=self.toggle_units,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_100,
                                shape=ft.RoundedRectangleBorder(radius=20),
                            )
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Column(
                            [
                                ft.Text(description, size=20, italic=True),
                                # Big temperature + toggle button side by side
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"{temp:.1f}°",
                                            size=48,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_900,
                                        ),
                                        ft.TextButton(
                                            text="C" if self.current_unit == "metric" else "F",
                                            on_click=self.toggle_units,
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.BLUE_200,
                                                color=ft.Colors.BLUE_900,
                                                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                                shape=ft.RoundedRectangleBorder(radius=20),
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=0,
                                ),
                                ft.Text(f"Feels like {feels_like:.1f}°{temp_unit}", size=16, color=ft.Colors.GREY_700),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed:.1f} {wind_unit}"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        # Show with fade-in
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()    

    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"{message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)