"""
AICalendarProcessor is a class that takes a list of calendar events and
optimizes their schedule based on a user's energy levels throughout the day.

The class uses the LLaMA model to generate a prompt based on the input data,
and then uses the model to generate an optimized schedule.

The generated prompt includes the following information:

* A description of the task
* The input data in GCal API format
* The user's energy levels throughout the day
* Constraints on the optimization (e.g. no overlaps, maintain original duration)

The generated output is a JSON string that includes the optimized schedule,
with each event including its new start and end times.

The class also includes methods for loading the model, creating the prompt,
and generating the output.

"""

import json
import logging

from typing import Optional
from dataclasses import dataclass

import torch
from llama_cpp import Llama, LogitsProcessorList
from pydantic import BaseModel
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.llamacpp import (
    build_llamacpp_logits_processor,
    build_token_enforcer_tokenizer_data,
)
import anthropic
from dotenv import load_dotenv
import os


@dataclass
class GenerationParams:
    """
    GenerationParams is a dataclass that contains parameters for generating
    text using the LLaMA model.

    Attributes:
        temperature (float): The temperature parameter for generating text.
        top_k (int): The number of top tokens to consider when generating text.
        top_p (float): The probability of considering the top tokens when generating text.
        context_tokens (int): The number of tokens to consider when generating text.
        max_tokens (int): The maximum number of tokens to generate.
        num_beams (int): The number of beams to use when generating text.
        do_sample (bool): Whether to sample from the model's output probability distribution.
        no_repeat_ngram_size (int): The size of the n-gram to avoid repeating.
        system_prompt (str): The prompt to use when generating text.
    """

    temperature: float = 0.1
    top_k: int = (50,)
    top_p: float = (0.9,)
    context_tokens: int = 64000
    max_tokens: int = 1000
    num_beams: int = (1,)
    do_sample: bool = (True,)
    no_repeat_ngram_size: int = (3,)
    system_prompt: str = ""


@dataclass
class DateTime:
    """
    DateTime is a dataclass that contains information about a date and time.

    Attributes:
        date (str): The date in YYYY-MM-DD format.
        datetime (str): The date and time in YYYY-MM-DDTHH:MM:SSZ format.
        timeZone (str): The time zone.
    """

    date: str
    datetime: str
    timeZone: str


@dataclass
class CalendarEvent(BaseModel):
    """
    CalendarEvent is a dataclass that contains information about a calendar event.

    Attributes:
        id (str): The ID of the event.
        summary (str): The title of the event.
        description (str): The description of the event.
        start (DateTime): The start time of the event.
        end (DateTime): The end time of the event.
    """

    id: str
    calendar_id: str
    summary: str
    description: str
    start: DateTime
    end: DateTime


@dataclass
class CalendarEvents(BaseModel):
    events: list[CalendarEvent]


class AICalendarProcessor:
    """
    AICalendarProcessor is a class that takes a list of calendar events and
    optimizes their schedule based on a user's energy levels throughout the day.

    Attributes:
        model_id (str): The ID of the LLaMA model to use.
        gen_params (GenerationParams): The parameters for generating text.
        verbose (bool): Whether to print verbose output.
        schema (dict): The JSON schema to use for validating the output.
    """

    def __init__(
        self,
        model_id: str = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
        gen_params: GenerationParams = GenerationParams(),
        verbose: bool = False,
        **kwargs,
    ):
        """
        Initializes the AICalendarProcessor class.

        Args:
            model_id (str): The ID of the LLaMA model to use.
            gen_params (GenerationParams): The parameters for generating text.
            verbose (bool): Whether to print verbose output.
            **kwargs: Additional keyword arguments.
        """
        self.model_id = model_id

        self.verbose = verbose
        self.tokenizer = None
        self.gen_params = gen_params

        self._load_model()
        self.schema = CalendarEvents.schema()

    def predict_claude(self, prompt):
        load_dotenv()

        # Send request to Claude API
        response = anthropic.Anthropic().messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],  # Add prompt herepost(
        )

        content = json.loads(response.json())["content"][-1]["text"]

        # Extract the JSON part of the response
        try:
            json_start = content.index("{")
            json_end = content.rindex("}") + 1
            json_content = content[json_start:json_end]
            optimized_data = json.loads(json_content)
        except (ValueError, json.JSONDecodeError):
            print("Failed to parse JSON from Claude's response. Raw response:")
            print(content)
            return None

        return optimized_data

    def predict(
        self, events: CalendarEvents, questionnaire: Optional[str] = None
    ) -> str:
        """
        Predicts an optimized schedule based on the input data.

        Args:
            events (CalendarEvents): The input data in CalendarEvents format.
            questionnaire (Optional[str]): The user's energy levels throughout the day.

        Returns:
            str: The optimized schedule in JSON format.
        """

        # If the questionnaire is provided, add it to the prompt
        if questionnaire:
            data = (
                str(events)
                + "\n Here are some details about the user: "
                + str(questionnaire)
            )
        else:
            data = str(events)

        # Create the prompt based on the input data
        prompt = self._create_prompt(data)

        return self.predict_claude(prompt)["events"]

        # # Generate the optimized schedule
        # output = self._generate(data)

        # # Return the optimized schedule
        # return output

    def _load_model(self):
        """
        Loads the LLaMA model.
        """
        self.model = Llama.from_pretrained(
            repo_id=self.model_id,
            filename="*Q8_0.gguf",
            n_ctx=self.gen_params.context_tokens,
            n_gpu_layers=-1,
            verbose=True,
        )
        self.tokenizer = build_token_enforcer_tokenizer_data(self.model)

    def _create_prompt(self, data) -> str:
        """
        Creates a prompt based on the input data.

        Args:
            data (str): The input data in JSON format.

        Returns:
            str: The prompt in JSON format.
        """
        return f"""
                You are an intelligent schedule optimization assistant. Your task is to take a user's existing calendar events and rearrange them within their scheduled days to maximize productivity based on the user's energy levels and the nature of each task. Here are your key responsibilities and constraints:

                1. Input Processing:
                - You will receive a list of dictionaries, each representing a calendar event.
                - Each event will include, at minimum: event ID, title, start time, end time, and day.
                - You will also receive information about the user's energy levels throughout the day.

                2. Event Analysis:
                - Analyze each event to determine its nature (e.g., high-focus work, low-energy tasks, meetings).
                - Consider the duration of each event, which must remain unchanged in your optimization.

                3. Energy Level Consideration:
                - Use the provided information about the user's energy levels throughout the day.
                - Match high-energy periods with high-focus tasks, and low-energy periods with less demanding activities.

                4. Scheduling Constraints:
                - Do not change the day of any event. Events must remain on their original scheduled day.
                - Maintain the original duration of each event. A 2-hour event should remain 2 hours long.
                - Ensure there are no overlaps in the optimized schedule.
                - Consider standard working hours unless otherwise specified.

                5. Optimization Strategy:
                - Prioritize important or high-focus tasks during the user's peak energy times.
                - Group similar tasks together when beneficial (e.g., back-to-back meetings).
                - Allow for short breaks between intense focus periods.
                - Consider the flow of the day, avoiding rapid switches between very different types of tasks.

                6. Output Format:
                - Provide the optimized schedule in a specified JSON format (details to be provided separately).
                - Include the event ID, new start time, and new end time for each rescheduled event.
                
                7. Handling Special Cases:
                - If certain events are marked as unmovable, respect those constraints.
                - If there are conflicting objectives, prioritize based on event importance if specified.

                Remember, your goal is to create an optimized daily schedule that respects the user's existing commitments while maximizing their productivity based on their energy levels. 
                Always maintain the original day and duration of each event, and focus on rearranging events within each day for optimal performance.
                
                Here are the events in GCal API form:
                {data}
                
                You MUST answer using the following JSON schema: {self.schema}
            """

    def _generate(self, data) -> str:
        """
        Generates an optimized schedule based on the input data.

        Args:
            data (str): The input data in JSON format.

        Returns:
            str: The optimized schedule in JSON format.
        """
        prompt = self._create_prompt(data)
        logits_processors = None

        if self.schema:
            logits_processors = LogitsProcessorList(
                [
                    build_llamacpp_logits_processor(
                        self.tokenizer, JsonSchemaParser(self.schema)
                    )
                ]
            )

            prompt += f"You MUST answer using the following JSON schema: {self.schema}"

        conversation = [
            {"role": "system", "content": "You are an intelligent assistant."},
            {
                "role": "user",
                "content": prompt,
            },
        ]

        output = self.model.create_chat_completion(
            conversation,
            logits_processor=logits_processors,
            max_tokens=self.gen_params.max_tokens,
            temperature=0.8,
            top_p=0.9,
        )
        generated_content = output["choices"][-1]["message"]["content"]

        return self._parse_output(generated_content)

    def _parse_output(self, output):
        return output
