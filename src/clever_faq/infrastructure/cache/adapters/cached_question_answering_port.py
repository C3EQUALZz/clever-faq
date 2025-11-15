import hashlib
import json
import logging
from typing import Final, TypedDict, override

from clever_faq.application.common.ports.cache_store import CacheStore
from clever_faq.application.common.ports.question.question_answering_port import (
    MessageWithTokenDTO,
    QuestionAnsweringPort,
)
from clever_faq.domain.dialog.values.message import Message
from clever_faq.domain.dialog.values.tokens import Tokens
from clever_faq.infrastructure.errors.cache import CacheError

logger: Final[logging.Logger] = logging.getLogger(__name__)


class AnswerWithTokenInCache(TypedDict):
    question: str
    answer: str
    tokens: int


class CachedQuestionAnsweringPort(QuestionAnsweringPort):
    def __init__(
        self,
        question_answering_port: QuestionAnsweringPort,
        cache: CacheStore,
    ) -> None:
        self._question_answering_port: Final[QuestionAnsweringPort] = question_answering_port
        self._cache: Final[CacheStore] = cache
        self._default_ttl_seconds: Final[int] = 3600

    @override
    async def answer_the_question(self, question: Message) -> MessageWithTokenDTO:
        cache_key = self._build_cache_key(question)

        try:
            cached_bytes = await self._cache.get(cache_key)
        except CacheError:
            logger.exception("Cache get failed for question: %s", question.value)
            return await self._question_answering_port.answer_the_question(question)

        if cached_bytes:
            cached_payload = self._decode_cached_answer(cached_bytes)
            if cached_payload:
                logger.info("Cache hit for question: %s", question.value)
                return self._build_dto_from_cache(cached_payload)

        logger.info("Cache miss for question: %s", question.value)
        answer_dto = await self._question_answering_port.answer_the_question(question)

        await self._store_in_cache(cache_key, question, answer_dto)

        return answer_dto

    @staticmethod
    def _build_cache_key(question: Message) -> str:
        key_json: str = json.dumps(
            {
                "question_for_llm": question.value,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(key_json.encode("utf-8")).hexdigest()

    async def _store_in_cache(
        self,
        cache_key: str,
        question: Message,
        answer_dto: MessageWithTokenDTO,
    ) -> None:
        payload: AnswerWithTokenInCache = {
            "question": question.value,
            "answer": answer_dto.message.value,
            "tokens": answer_dto.tokens.value,
        }
        encoded_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        try:
            await self._cache.set(cache_key, encoded_payload, ttl=self._default_ttl_seconds)
        except CacheError:
            logger.exception("Failed to cache answer for question: %s", question.value)
        else:
            logger.info(
                "Cached answer for question: %s with TTL: %s",
                question.value,
                self._default_ttl_seconds,
            )

    @staticmethod
    def _decode_cached_answer(cached_bytes: bytes) -> AnswerWithTokenInCache | None:
        try:
            payload = json.loads(cached_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("Failed to decode cached answer")
            return None

        if not isinstance(payload, dict):
            logger.warning("Cached answer has invalid format")
            return None

        if not {"question", "answer", "tokens"} <= payload.keys():
            logger.warning("Cached answer missing required fields")
            return None

        try:
            payload["tokens"] = int(payload["tokens"])
        except (TypeError, ValueError):
            logger.warning("Cached answer has invalid token count")
            return None

        return payload  # type: ignore[return-value]

    @staticmethod
    def _build_dto_from_cache(payload: AnswerWithTokenInCache) -> MessageWithTokenDTO:
        return MessageWithTokenDTO(
            message=Message(payload["answer"]),
            tokens=Tokens(payload["tokens"]),
        )
