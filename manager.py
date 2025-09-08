from __future__ import annotations

import asyncio
import time
import json
from collections.abc import Sequence

from rich.console import Console

# Removed old agents library imports - now using pydantic-ai directly

from agent import History, get_historical_agent
from agent import Culinary, get_culinary_agent
from agent import Culture, get_culture_agent
from agent import Architecture, get_architecture_agent
from agent import Planner, get_planner_agent
from agent import FinalTour, get_orchestrator_agent
from printer import Printer


class TourManager:
    """
    Orchestrates the full flow
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

    async def run(self, query: str, interests: list, duration: str) -> None:
        self.printer.update_item("start", "Starting tour research...", is_done=True)
        
        # Get plan based on selected interests
        planner = await self._get_plan(query, interests, duration)
        
        # Initialize research results
        research_results = {}
        
        # Calculate word limits based on duration
        # Assuming average speaking rate of 150 words per minute
        words_per_minute = 150
        total_words = int(duration) * words_per_minute
        words_per_section = total_words // len(interests)
        
        # Only research selected interests
        if "Architecture" in interests:
            research_results["architecture"] = await self._get_architecture(query, interests, words_per_section)
        
        if "History" in interests:
            research_results["history"] = await self._get_history(query, interests, words_per_section)
        
        if "Culinary" in interests:
            research_results["culinary"] = await self._get_culinary(query, interests, words_per_section)
        
        if "Culture" in interests:
            research_results["culture"] = await self._get_culture(query, interests, words_per_section)
        
        # Get final tour with only selected interests
        final_tour = await self._get_final_tour(
            query, 
            interests, 
            duration, 
            research_results
        )
        
        self.printer.update_item("final_report", "", is_done=True)
        self.printer.end()

        # Return the final tour content directly as it's now a complete string
        return final_tour
        
    async def _get_plan(self, query: str, interests: list, duration: str) -> Planner:
        self.printer.update_item("Planner", "Planning your personalized tour...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await get_planner_agent().run(
                    "Query: {} Interests: {} Duration: {}".format(query, ', '.join(interests), duration)
                )
                self.printer.update_item(
                    "Planner",
                    "Completed planning",
                    is_done=True,
                )
                return result.output
            except Exception as e:
                if attempt < max_retries - 1:
                    self.printer.update_item(
                        "Planner",
                        f"Retrying planning... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(2)
                    continue
                else:
                    self.printer.update_item(
                        "Planner",
                        "Failed to generate plan after multiple attempts",
                        is_done=True,
                    )
                    return f"Planning for {query} is currently unavailable. Please try again later."
    
    async def _get_history(self, query: str, interests: list, word_limit: int) -> History:
        self.printer.update_item("History", "Researching historical highlights...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await get_historical_agent().run(
                    "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging historical content for an audio tour. Focus on interesting stories and personal connections. Make it conversational and include specific details that would be interesting to hear while walking. Include specific locations and landmarks where possible. The content should be approximately {} words when spoken at a natural pace.".format(query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
                )
                self.printer.update_item(
                    "History",
                    "Completed history research",
                    is_done=True,
                )
                return result.output
            except Exception as e:
                if attempt < max_retries - 1:
                    self.printer.update_item(
                        "History",
                        f"Retrying history research... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(2)
                    continue
                else:
                    self.printer.update_item(
                        "History",
                        "Failed to generate history content after multiple attempts",
                        is_done=True,
                    )
                    return f"History content for {query} is currently unavailable. Please try again later."

    async def _get_architecture(self, query: str, interests: list, word_limit: int):
        self.printer.update_item("Architecture", "Exploring architectural wonders...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await get_architecture_agent().run(
                    "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging architectural content for an audio tour. Focus on visual descriptions and interesting design details. Make it conversational and include specific buildings and their unique features. Describe what visitors should look for and why it matters. The content should be approximately {} words when spoken at a natural pace.".format(query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
                )
                self.printer.update_item(
                    "Architecture",
                    "Completed architecture research",
                    is_done=True,
                )
                return result.output
            except Exception as e:
                if attempt < max_retries - 1:
                    self.printer.update_item(
                        "Architecture",
                        f"Retrying architecture research... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(2)
                    continue
                else:
                    self.printer.update_item(
                        "Architecture",
                        "Failed to generate architecture content after multiple attempts",
                        is_done=True,
                    )
                    # Return a fallback content instead of raising
                    return f"Architecture content for {query} is currently unavailable. Please try again later."
    
    async def _get_culinary(self, query: str, interests: list, word_limit: int):
        self.printer.update_item("Culinary", "Discovering local flavors...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await get_culinary_agent().run(
                    "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging culinary content for an audio tour. Focus on local specialties, food history, and interesting stories about restaurants and dishes. Make it conversational and include specific recommendations. Describe the flavors and cultural significance of the food. The content should be approximately {} words when spoken at a natural pace.".format(query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
                )
                self.printer.update_item(
                    "Culinary",
                    "Completed culinary research",
                    is_done=True,
                )
                return result.output
            except Exception as e:
                if attempt < max_retries - 1:
                    self.printer.update_item(
                        "Culinary",
                        f"Retrying culinary research... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(2)
                    continue
                else:
                    self.printer.update_item(
                        "Culinary",
                        "Failed to generate culinary content after multiple attempts",
                        is_done=True,
                    )
                    return f"Culinary content for {query} is currently unavailable. Please try again later."
    
    async def _get_culture(self, query: str, interests: list, word_limit: int):
        self.printer.update_item("Culture", "Exploring cultural highlights...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await get_culture_agent().run(
                    "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging cultural content for an audio tour. Focus on local traditions, arts, and community life. Make it conversational and include specific cultural venues and events. Describe the atmosphere and significance of cultural landmarks. The content should be approximately {} words when spoken at a natural pace.".format(query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
                )
                self.printer.update_item(
                    "Culture",
                    "Completed culture research",
                    is_done=True,
                )
                return result.output
            except Exception as e:
                if attempt < max_retries - 1:
                    self.printer.update_item(
                        "Culture",
                        f"Retrying culture research... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(2)
                    continue
                else:
                    self.printer.update_item(
                        "Culture",
                        "Failed to generate culture content after multiple attempts",
                        is_done=True,
                    )
                    return f"Culture content for {query} is currently unavailable. Please try again later."
    
    async def _get_final_tour(self, query: str, interests: list, duration: float, research_results: dict):
        self.printer.update_item("Final Tour", "Creating your personalized tour...")
        
        # Build content sections based on selected interests
        content_sections = []
        for interest in interests:
            if interest.lower() in research_results:
                result_obj = research_results[interest.lower()]
                # Extract the output string from the result object
                if hasattr(result_obj, 'output'):
                    content_sections.append(result_obj.output)
                else:
                    content_sections.append(str(result_obj))
        
        # Calculate total words based on duration
        # Assuming average speaking rate of 150 words per minute
        words_per_minute = 150
        total_words = int(duration) * words_per_minute
        
        # Create the prompt with proper string formatting
        prompt = (
            "Query: {}\n"
            "Selected Interests: {}\n"
            "Total Tour Duration (in minutes): {}\n"
            "Target Word Count: {}\n\n"
            "Content Sections:\n{}\n\n"
            "Instructions: Create a natural, conversational audio tour that focuses only on the selected interests. "
            "Make it feel like a friendly guide walking alongside the visitor, sharing interesting stories and insights. "
            "Use natural transitions between topics and maintain an engaging but relaxed pace. "
            "Include specific locations and landmarks where possible. "
            "Add natural pauses and transitions as if walking between locations. "
            "Use phrases like 'as we walk', 'look to your left', 'notice how', etc. "
            "Make it interactive and engaging, as if the guide is actually there with the visitor. "
            "Start with a warm welcome and end with a natural closing thought. "
            "The total content should be approximately {} words when spoken at a natural pace of 150 words per minute. "
            "This will ensure the tour lasts approximately {} minutes."
        ).format(
            query,
            ', '.join(interests),
            duration,
            total_words,
            '\n\n'.join(content_sections),
            total_words,
            duration
        )
        
        # Add retry logic to handle network connection issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await get_orchestrator_agent().run(
                    prompt
                )
                
                self.printer.update_item(
                    "Final Tour",
                    "Completed Final Tour Guide Creation",
                    is_done=True,
                )
                
                # Combine all sections of the FinalTour for complete audio content
                final_tour_obj = result.output
                complete_tour = f"{final_tour_obj.introduction}\n\n{final_tour_obj.architecture}\n\n{final_tour_obj.history}\n\n{final_tour_obj.culture}\n\n{final_tour_obj.culinary}\n\n{final_tour_obj.conclusion}"
                
                return complete_tour
                
            except Exception as e:
                if attempt < max_retries - 1:
                    self.printer.update_item(
                        "Final Tour",
                        f"Connection issue, retrying... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(2)  # Wait 2 seconds before retry
                    continue
                else:
                    self.printer.update_item(
                        "Final Tour",
                        "Failed to generate final tour after multiple attempts",
                        is_done=True,
                    )
                    raise e