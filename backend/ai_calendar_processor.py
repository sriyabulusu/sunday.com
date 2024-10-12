import json
import logging
import math

from typing import Optional
from dataclasses import dataclass

import torch
from llama_cpp import Llama, LogitsProcessorList
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.llamacpp import (
    build_llamacpp_logits_processor,
    build_token_enforcer_tokenizer_data,
)


@dataclass
class GenerationParams:
    temperature: float = 0.1
    top_k: int = (50,)
    top_p: float = (0.9,)
    context_tokens: int = 64000
    max_tokens: int = 100
    num_beams: int = (1,)
    do_sample: bool = (True,)
    no_repeat_ngram_size: int = (3,)
    system_prompt: str = ""


class AICalendarProcessor:

    def __init__(
        self,
        model_id: str,
        gen_params: GenerationParams = GenerationParams(),
        verbose: bool = False,
        **kwargs,
    ):
        self.model_id = model_id

        self.verbose = verbose
        self.tokenizer = None
        self.gen_params = gen_params

    def predict(self, data):
        pass

    def predict_batch(self, data):
        pass

    def _load_model(self):
        self.model = Llama.from_pretrained(
            repo_id=self.model_id,
            filename="*Q6_K.gguf",
            n_ctx=self.gen_params.context_tokens,
            n_gpu_layers=-1,
            verbose=self.verbose,
        )
        self.tokenizer = build_token_enforcer_tokenizer_data(self.model)

    def _create_prompt(self, data) -> str:
        return "hi"

    def _generate(self, data, json_schema: Optional[dict] = None) -> str:
        prompt = self._create_prompt(data)

        try:
            logits_processors = None

            if json_schema:
                logits_processors = LogitsProcessorList(
                    [
                        build_llamacpp_logits_processor(
                            self.tokenizer, JsonSchemaParser(json_schema)
                        )
                    ]
                )

                prompt += (
                    f"You MUST answer using the following JSON schema: {json_schema}"
                )

            conversation = [
                {
                    "role": "system",
                    "content": self.gen_params.system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]

            output = self.model.create_chat_completion(
                conversation,
                logits_processor=logits_processors,
                max_tokens=self.gen_params.max_tokens,
                temperature=self.gen_params.temperature,
                top_p=self.gen_params.top_p,
                logprobs=True,
            )

            generated_content = output["choices"][-1]["message"]["content"]
            logprobs = output["choices"][-1]["logprobs"]

            confidence = math.exp(sum(logprobs) / len(logprobs)) if logprobs else None

            if json_schema and "properties" in json_schema:
                if "confidence" in json_schema["properties"]:
                    content_json = json.loads(generated_content)
                    content_json["confidence"] = (
                        confidence
                        if confidence is not None
                        else content_json["confidence"]
                    )

            return self._parse_output(generated_content)

        except Exception as exp:
            logging.error(f"Error generating output: {exp}")
            return None

    def _parse_output(self, output):
        return output
