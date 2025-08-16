"""
Custom tool implementations for the Japan itinerary planner.

These classes define the various tools referenced in the `agents.yaml` and
`tasks.yaml` specifications.  Each tool either subclasses `crewai.tools.BaseTool`
or uses the `@tool` decorator (where appropriate).  For environments where
`crewai` isn't available, the classes are still valid Python objects and can
easily be adapted to another agent framework.  The goal of these tools is to
encapsulate external API calls, data validation, simple computations, and
formatting logic to support the multi‑agent planning workflow.

Most tools below return simple placeholder data because this repository does
not provide API keys or network access.  Integrators should replace the
placeholder logic with real API calls (e.g. to weather services, transport
providers or booking platforms) and update the returned structures accordingly.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

try:
    # Import from crewai if available.  In development environments where
    # crewai isn't installed, the classes will still function as plain
    # Python classes.
    from crewai.tools import BaseTool, tool
    # Import built‑in tools from crewai_tools if available.  These provide
    # real web search and scraping capabilities when properly configured with
    # API keys.
    try:
        from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool  # type: ignore
    except Exception:
        # If crewai_tools is not installed, fall back to None and use
        # placeholder implementations later.
        SerperDevTool = None  # type: ignore
        ScrapeWebsiteTool = None  # type: ignore
        WebsiteSearchTool = None  # type: ignore
except ImportError:  # pragma: no cover
    BaseTool = object  # type: ignore
    def tool(name: str):  # type: ignore
        """Fallback decorator for environments without crewai.  It simply
        returns the wrapped function unchanged.  This allows the code to run
        without raising import errors while preserving the intended interface.
        """
        def decorator(func):
            func.tool_name = name
            return func
        return decorator

    # When crewai is absent, the built‑in tools from crewai_tools are also
    # unavailable.  Declare them as None to avoid NameError.
    SerperDevTool = None  # type: ignore
    ScrapeWebsiteTool = None  # type: ignore
    WebsiteSearchTool = None  # type: ignore

from pydantic import BaseModel, Field

class SchemaValidatorInput(BaseModel):
    """Input schema for the SchemaValidatorTool."""
    data: Dict[str, Any] = Field(..., description="Data to validate")
    schema: Dict[str, Any] = Field(..., description="JSON schema to validate against")


class SchemaValidatorTool(BaseTool):
    """Validate JSON data against a JSON schema.

    This tool uses the `jsonschema` library to check that a given piece of
    data conforms to a supplied JSON schema.  It returns a dictionary
    describing whether the validation passed and any associated error
    messages.
    """

    name: str = "schema_validator"
    description: str = "Validate JSON data against a JSON schema."
    args_schema = SchemaValidatorInput

    def _run(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import jsonschema  # imported here to avoid hard dependency at module import time
        except ImportError as exc:  # pragma: no cover
            return {"valid": False, "errors": f"jsonschema library not installed: {exc}"}
        try:
            jsonschema.validate(instance=data, schema=schema)
            return {"valid": True, "errors": None}
        except jsonschema.ValidationError as err:
            return {"valid": False, "errors": str(err)}


class QACheckerInput(BaseModel):
    """Input schema for QACheckerTool."""
    content: Any = Field(..., description="Data or document to quality‑check")


class QACheckerTool(BaseTool):
    """Perform quality and consistency checks on itinerary data.

    This tool implements very simple heuristic checks.  In a production
    environment you would extend this method to verify date consistency,
    budget coherence, presence of required fields, duplicate entries, etc.
    """

    name: str = "qa_checker"
    description: str = (
        "Checks the quality and consistency of data (e.g. itinerary segments) and"
        " returns a summary of issues found."
    )
    args_schema = QACheckerInput

    def _run(self, content: Any) -> Dict[str, Any]:
        issues: List[str] = []
        # Placeholder logic: in reality, inspect the content structure and
        # populate issues accordingly.
        if content is None:
            issues.append("No content provided for QA check.")
        elif isinstance(content, dict) and not content:
            issues.append("Empty dictionary provided.")
        # Return a summary of the checks.  If issues is empty, everything passed.
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "checked_fields": list(content.keys()) if isinstance(content, dict) else None,
        }


class SourceRegistryInput(BaseModel):
    """Input schema for SourceRegistryTool."""
    action: str = Field(..., description="Action to perform: 'add', 'list', or 'clear'")
    source: Optional[Dict[str, Any]] = Field(None, description="Source record to add when action is 'add'")


class SourceRegistryTool(BaseTool):
    """Maintain a registry of sources used by other tools and agents.

    This tool supports adding new sources, listing all recorded sources and
    clearing the registry.  Each source is expected to include at least a
    title, a URL, and a date.
    """

    name: str = "source_registry"
    description: str = "Manage a registry of source metadata (title, URL, date)."
    args_schema = SourceRegistryInput
    # Class‑level storage for sources.  In a real application you might
    # persist this to a database or other storage backend.
    _registry: List[Dict[str, Any]] = []

    def _run(self, action: str, source: Optional[Dict[str, Any]] = None) -> Any:
        action = action.lower()
        if action == "add":
            if not source:
                return {"error": "No source provided for addition."}
            self._registry.append(source)
            return {"status": "added", "count": len(self._registry)}
        if action == "list":
            return list(self._registry)
        if action == "clear":
            self._registry.clear()
            return {"status": "cleared"}
        return {"error": f"Unknown action '{action}'"}


class InternalKBInput(BaseModel):
    """Input schema for InternalKBTool."""
    query: str = Field(..., description="Question about Japan or internal knowledge base")


class InternalKBTool(BaseTool):
    """Simple internal knowledge base lookup tool.

    This tool demonstrates how an agent might retrieve information from a
    static dictionary.  For more sophisticated use cases, replace the
    dictionary with a retrieval‑augmented generation (RAG) system or a
    vector store.
    """

    name: str = "internal_kb"
    description: str = "Answer questions about Japan using an internal knowledge base."
    args_schema = InternalKBInput
    # Minimal internal knowledge base.  Extend this with more entries as needed.
    _knowledge_base: Dict[str, str] = {
        "japan_capital": "Tokyo is the capital city of Japan.",
        "currency": "The official currency of Japan is the Japanese Yen (JPY).",
        "language": "The primary language spoken in Japan is Japanese.",
    }

    def _run(self, query: str) -> str:
        # Normalize query key for simple lookup
        key = query.strip().lower().replace(" ", "_")
        return self._knowledge_base.get(key, "Information not found in the internal knowledge base.")


class WebSearchInput(BaseModel):
    """Input schema for WebSearchTool."""
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, description="Maximum number of search results to return")


class WebSearchTool(BaseTool):
    """Perform a simple web search.

    This tool implements a naïve HTTP GET request to the DuckDuckGo HTML endpoint
    and scrapes the titles and URLs of the top results.  Because network
    connectivity may be restricted, it gracefully falls back to returning
    example results when HTTP requests fail.
    """

    name: str = "web_search"
    description: str = "Search the web for the given query and return basic results."
    args_schema = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Execute a web search.

        This method first tries to leverage CrewAI’s `SerperDevTool` or
        `WebsiteSearchTool` if they are available and properly configured.  If
        those tools are unavailable (for example, if `crewai_tools` is not
        installed or no API keys are provided), it falls back to a simple
        DuckDuckGo HTML scrape.  When even that is not possible (e.g. due to
        network restrictions), it returns placeholder results.
        """
        # Attempt to use SerperDevTool for a real Google search
        if 'SerperDevTool' in globals() and SerperDevTool:
            try:
                search_tool = SerperDevTool()
                # SerperDevTool typically accepts a query parameter.  The
                # run method may expect a dictionary or named argument; here
                # we assume a simple call with keyword argument.
                serper_results = search_tool.run(query=query)
                # If the result is already a list of dicts, return it directly;
                # otherwise attempt to normalize into our expected format.
                if isinstance(serper_results, list):
                    # Limit the number of results
                    return serper_results[:max_results]
                elif isinstance(serper_results, dict) and 'results' in serper_results:
                    return serper_results['results'][:max_results]
            except Exception:
                # If SerperDevTool is present but misconfigured, ignore and fall
                # back to other methods.
                pass
        # Attempt to use WebsiteSearchTool for web search (within specific sites)
        if 'WebsiteSearchTool' in globals() and WebsiteSearchTool:
            try:
                website_search_tool = WebsiteSearchTool()
                site_results = website_search_tool.run(query=query)
                if isinstance(site_results, list):
                    return site_results[:max_results]
            except Exception:
                pass
        # Fallback: use HTTP scraping of DuckDuckGo if network is available
        try:
            import re
            import html as html_lib
            import requests  # runtime import to avoid dependency at import time
            url = f"https://duckduckgo.com/html/?q={query}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                pattern = re.compile(r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>')
                results = []
                for match in pattern.findall(resp.text):
                    link = html_lib.unescape(match[0])
                    title = html_lib.unescape(re.sub("<.*?>", "", match[1]))
                    results.append({"title": title, "url": link})
                    if len(results) >= max_results:
                        break
                return results
        except Exception:
            pass
        # Ultimate fallback: return fabricated example results
        return [
            {"title": f"Example result {i+1} for '{query}'", "url": "https://example.com"}
            for i in range(max_results)
        ]


class WeatherAPIInput(BaseModel):
    """Input schema for WeatherAPITool."""
    location: str = Field(..., description="City or location name")
    date: Optional[str] = Field(None, description="Date in ISO format (YYYY‑MM‑DD)")


class WeatherAPITool(BaseTool):
    """Retrieve basic weather information for a location and date.

    This implementation returns a mock forecast.  Integrators should replace
    the placeholder logic with calls to a real weather service such as
    OpenWeatherMap or JMA.
    """

    name: str = "weather_api"
    description: str = "Get weather data (forecast and historical) for a location and date."
    args_schema = WeatherAPIInput

    def _run(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        # Placeholder: produce some made‑up weather metrics
        return {
            "location": location,
            "date": date or "today",
            "temperature_c": 20,
            "precipitation_mm": 1.2,
            "condition": "Partly cloudy",
        }


class TransportAPIInput(BaseModel):
    """Input schema for TransportAPITool."""
    from_city: str = Field(..., description="Origin city")
    to_city: str = Field(..., description="Destination city")
    departure_date: Optional[str] = Field(None, description="Date of departure (ISO format)")


class TransportAPITool(BaseTool):
    """Compute transport options between two cities.

    In a full implementation this tool would query a transportation API for
    schedules, prices and travel times (e.g. JR East, Hyperdia).  Here it
    returns illustrative data only.
    """

    name: str = "transport_api"
    description: str = "Retrieve transport options and cost estimates between cities."
    args_schema = TransportAPIInput

    def _run(self, from_city: str, to_city: str, departure_date: Optional[str] = None) -> Dict[str, Any]:
        # Placeholder for demonstration purposes
        sample_duration = 120  # minutes
        sample_cost = 8000     # yen
        return {
            "from_city": from_city,
            "to_city": to_city,
            "departure_date": departure_date,
            "options": [
                {
                    "mode": "train",
                    "duration_minutes": sample_duration,
                    "cost_yen": sample_cost,
                    "notes": "Shinkansen with reserved seat",
                }
            ],
        }


class MapsRoutingInput(BaseModel):
    """Input schema for MapsRoutingTool."""
    start: str = Field(..., description="Starting point (address or coordinates)")
    end: str = Field(..., description="Ending point (address or coordinates)")


class MapsRoutingTool(BaseTool):
    """Calculate the route and distance between two locations.

    This stub returns an estimated distance and duration.  Real implementations
    can use services like Google Maps or Mapbox.
    """

    name: str = "maps_routing"
    description: str = "Compute driving/walking routes and distances between locations."
    args_schema = MapsRoutingInput

    def _run(self, start: str, end: str) -> Dict[str, Any]:
        # Placeholder values
        return {
            "start": start,
            "end": end,
            "distance_km": 5.0,
            "duration_minutes": 15,
            "route": [start, "Midpoint", end],
        }


class LodgingAPIInput(BaseModel):
    """Input schema for LodgingAPITool."""
    city: str = Field(..., description="City for which to find lodging")
    check_in: Optional[str] = Field(None, description="Check‑in date (ISO format)")
    check_out: Optional[str] = Field(None, description="Check‑out date (ISO format)")
    budget_yen: Optional[int] = Field(None, description="Maximum budget in yen per night")


class LodgingAPITool(BaseTool):
    """Retrieve lodging options for a city and date range.

    This stub returns two example accommodations per city.  Replace with calls
    to a booking API (e.g. Hotels.com, Booking.com, Rakuten Travel) to get
    real availability and prices.
    """

    name: str = "lodging_api"
    description: str = "Find lodging options based on city, dates and budget."
    args_schema = LodgingAPIInput

    def _run(
        self,
        city: str,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        budget_yen: Optional[int] = None,
    ) -> Dict[str, Any]:
        # Return two example lodging options
        options = []
        options.append({
            "name": f"{city} Central Hotel",
            "type": "hotel",
            "price_per_night_yen": 10000,
            "total_estimate_yen": 10000 * ((1 if not check_in or not check_out else 1)),
            "pros": ["Central location", "Free breakfast"],
            "cons": ["Small rooms"],
            "link": "https://example.com/hotel",
            "source_date": "2025-01-01",
        })
        options.append({
            "name": f"{city} Traditional Ryokan",
            "type": "ryokan",
            "price_per_night_yen": 15000,
            "total_estimate_yen": 15000 * ((1 if not check_in or not check_out else 1)),
            "pros": ["Tatami rooms", "Onsen access"],
            "cons": ["Curfew at 22h"],
            "link": "https://example.com/ryokan",
            "source_date": "2025-01-01",
        })
        return {"city": city, "options": options}


class RestaurantsAPIInput(BaseModel):
    """Input schema for RestaurantsAPITool."""
    city: str = Field(..., description="City in which to search for restaurants")
    meal_type: Optional[str] = Field(None, description="Meal type: breakfast, lunch, dinner")
    budget_yen: Optional[int] = Field(None, description="Approximate budget in yen per person")


class RestaurantsAPITool(BaseTool):
    """Retrieve restaurant recommendations for a city and meal type.

    This stub returns example restaurants.  Integrators should replace this
    logic with calls to real services such as Yelp, Tabelog or Google Maps.
    """

    name: str = "restaurants_api"
    description: str = "Get restaurants and culinary experiences for a given city and meal type."
    args_schema = RestaurantsAPIInput

    def _run(self, city: str, meal_type: Optional[str] = None, budget_yen: Optional[int] = None) -> Dict[str, Any]:
        # Provide a list of example restaurants
        restaurants = []
        restaurants.append({
            "name": f"Sushi Place in {city}",
            "cuisine": "Sushi",
            "price_range_yen": [2000, 5000],
            "recommended_dish": "Omakase",
            "address": f"123 Fish St, {city}",
            "reservation_needed": True,
            "source": "https://example.com/sushi",
        })
        restaurants.append({
            "name": f"Ramen Shop in {city}",
            "cuisine": "Ramen",
            "price_range_yen": [800, 1200],
            "recommended_dish": "Miso Ramen",
            "address": f"456 Noodle Ave, {city}",
            "reservation_needed": False,
            "source": "https://example.com/ramen",
        })
        return {"city": city, "meal_type": meal_type, "restaurants": restaurants}


class BudgetCalcInput(BaseModel):
    """Input schema for BudgetCalcTool."""
    breakdown: Dict[str, float] = Field(..., description="Breakdown of costs by category (in yen)")
    budget_yen: Optional[float] = Field(None, description="User's budget in yen")


class BudgetCalcTool(BaseTool):
    """Aggregate costs and produce budget scenarios.

    This tool sums costs across categories and compares against a user budget if
    provided.  It also generates simple alternative scenarios for saving or
    exceeding the budget.
    """

    name: str = "budget_calc"
    description: str = "Calculate total costs and budget scenarios based on cost breakdowns."
    args_schema = BudgetCalcInput

    def _run(self, breakdown: Dict[str, float], budget_yen: Optional[float] = None) -> Dict[str, Any]:
        total = sum(breakdown.values())
        result = {
            "breakdown": breakdown,
            "total": total,
        }
        if budget_yen is not None:
            result["difference_from_budget"] = total - budget_yen
            # Suggest one cheaper and one more expensive scenario for illustration
            result["scenarios"] = [
                {
                    "name": "Economy",
                    "modifier": -0.1,
                    "estimated_total": total * 0.9,
                    "description": "Reduce costs by 10% across all categories",
                },
                {
                    "name": "Premium",
                    "modifier": 0.2,
                    "estimated_total": total * 1.2,
                    "description": "Increase budget by 20% for upgrades",
                },
            ]
        return result


class DocWriterInput(BaseModel):
    """Input schema for DocWriterTool."""
    itinerary: Dict[str, Any] = Field(..., description="Detailed itinerary data structure")
    output_path: Optional[str] = Field(None, description="Optional path to save the generated document")


class DocWriterTool(BaseTool):
    """Generate a Markdown document from itinerary data.

    This tool composes a human‑readable markdown report from a structured
    itinerary.  It can optionally write the result to a file on disk.
    """

    name: str = "doc_writer"
    description: str = "Compose and optionally save a Markdown document summarizing the itinerary."
    args_schema = DocWriterInput

    def _run(self, itinerary: Dict[str, Any], output_path: Optional[str] = None) -> str:
        # Build a simple Markdown string.  A real implementation would be more
        # sophisticated, handling formatting and edge cases.
        lines: List[str] = []
        lines.append(f"# Itinéraire pour {itinerary.get('trip_name', 'voyage au Japon')}")
        lines.append("")
        days = itinerary.get("days", [])
        for day in days:
            lines.append(f"## {day.get('date', 'Jour')}: {day.get('city', '')}")
            for act in day.get("activities", []):
                lines.append(f"- **{act.get('name')}**: {act.get('description')} (\u3011 {act.get('duration')} min, {act.get('cost')} ¥)")
            lines.append("")
        lines.append(f"\n**Coût total estimé:** {itinerary.get('total_cost', 'N/A')} ¥")
        lines.append("\nSources:\n")
        for source in itinerary.get("sources", []):
            lines.append(f"- {source.get('title')} ({source.get('date')}): {source.get('url')}")
        markdown_content = "\n".join(lines)
        # Optionally write to file
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
        return markdown_content


# -----------------------------------------------------------------------------
# Optional wrappers for built‑in CrewAI tools
class ScrapeWebsiteInput(BaseModel):
    """Input schema for ScrapeWebsiteToolWrapper."""
    website_url: str = Field(..., description="URL of the website to scrape")


class ScrapeWebsiteToolWrapper(BaseTool):
    """Wrapper around CrewAI’s ScrapeWebsiteTool.

    This class exposes the functionality of ScrapeWebsiteTool via the same
    BaseTool interface used elsewhere in this module.  If the underlying tool
    is available (via crewai_tools) it will be used; otherwise it falls back
    to a simple HTTP GET and returns the raw text content of the page.
    """

    name: str = "scrape_website_tool"
    description: str = "Extract and return the text content of a website."
    args_schema = ScrapeWebsiteInput

    def _run(self, website_url: str) -> str:
        # Use built‑in ScrapeWebsiteTool if available
        if 'ScrapeWebsiteTool' in globals() and ScrapeWebsiteTool:
            try:
                scraper = ScrapeWebsiteTool(website_url=website_url)
                return scraper.run()
            except Exception:
                pass
        # Fallback: perform a simple HTTP GET and return the raw text
        try:
            import requests
            response = requests.get(website_url, timeout=10)
            return response.text
        except Exception as exc:
            return f"Failed to fetch content from {website_url}: {exc}"


class WebsiteSearchInput(BaseModel):
    """Input schema for WebsiteSearchToolWrapper."""
    query: str = Field(..., description="Search query")
    site: str = Field(..., description="Website to search within (e.g. example.com)")
    max_results: int = Field(5, description="Number of results to return")


class WebsiteSearchToolWrapper(BaseTool):
    """Wrapper around CrewAI’s WebsiteSearchTool.

    Searches within a specific website for the given query.  If the underlying
    tool is unavailable, this class performs a very naive keyword search by
    requesting the homepage and scanning for the query string.  For real
    use cases, replace the fallback with a proper on‑site search engine or
    internal indexing.
    """

    name: str = "website_search_tool"
    description: str = "Search within a specific website for a given query."
    args_schema = WebsiteSearchInput

    def _run(self, query: str, site: str, max_results: int = 5) -> List[Dict[str, Any]]:
        # Use built‑in WebsiteSearchTool if available
        if 'WebsiteSearchTool' in globals() and WebsiteSearchTool:
            try:
                searcher = WebsiteSearchTool(
                    websites=[site] if hasattr(WebsiteSearchTool, 'websites') else None
                )
                results = searcher.run(query=query)
                if isinstance(results, list):
                    return results[:max_results]
            except Exception:
                pass
        # Fallback: naive search on the site's home page
        try:
            import requests
            response = requests.get(f"https://{site}", timeout=10)
            text = response.text.lower()
            matches = []
            if query.lower() in text:
                matches.append({
                    "title": f"Result on {site}",
                    "snippet": "Query term found on homepage",
                    "url": f"https://{site}",
                })
            return matches[:max_results]
        except Exception:
            return []
