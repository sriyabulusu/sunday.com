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

        # Generate the optimized schedule
        output = self._generate(data)

        # Return the optimized schedule
        return output

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
            You are a schedule optimization assistant. Your task is to rearrange the given calendar events within their scheduled day to maximize productivity. Follow these guidelines:

            1. Keep events on their original day.
            2. Maintain the original duration of each event.
            3. Avoid overlaps in the schedule.
            4. Assume higher energy in the morning, lower after lunch, and a slight increase in late afternoon.
            5. Place high-focus tasks during high-energy periods.
            6. Group similar tasks when beneficial.
            7. Allow short breaks between intense tasks.

            Analyze the following events and provide an optimized schedule:

            {data}

            For each event in your optimized schedule, include:
            - Event ID
            - New start time
            - New end time

            
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
            temperature=0.3,
            top_p=0.9,
        )
        generated_content = output["choices"][-1]["message"]["content"]

        return self._parse_output(generated_content)

    def _parse_output(self, output):
        return output
