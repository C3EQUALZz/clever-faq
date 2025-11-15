import logging
from typing import TYPE_CHECKING, Any, Final, override

from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langsmith import traceable

from clever_faq.application.common.ports.question.question_answering_port import (
    MessageWithTokenDTO,
    QuestionAnsweringPort,
)
from clever_faq.domain.dialog.values.message import Message
from clever_faq.domain.dialog.values.tokens import Tokens

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable

logger: Final[logging.Logger] = logging.getLogger(__name__)

PROMPT_TO_LLM_RUSSIAN: Final[str] = (
    "Ты — виртуальный ассистент службы поддержки компании Clever FAQ.\n"
    "Тебе передают вопрос пользователя и выдержки из внутренней документации.\n"
    "Отвечай строго на русском языке деловым, понятным тоном.\n"
    "\n"
    "Правила:\n"
    "1. Используй только предоставленный контекст. Не додумывай факты.\n"
    "2. Если контекст не содержит ответа, напиши: "
    '"Информация не найдена. Обратитесь к специалисту."\n'
    "3. Если ответ включает инструкции, перечисляй шаги по порядку.\n"
    "4. Если упоминаешь документы, укажи их название или раздел.\n"
    "5. Заверши ответ кратким выводом или рекомендацией.\n"
    "\n"
    "Верни только содержательный ответ без преамбулы и без указания, что ты модель."
)


class LangChainQuestionAnsweringPort(QuestionAnsweringPort):
    def __init__(self, large_learning_model: BaseChatModel, vector_store: VectorStore) -> None:
        self._large_learning_model: Final[BaseChatModel] = large_learning_model
        self._retrieval: Final[VectorStoreRetriever] = vector_store.as_retriever(
            similarity="similarity",
        )

    @traceable
    @override
    async def answer_the_question(self, question: Message) -> MessageWithTokenDTO:
        logger.debug("Building prompt for chat...")

        prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
            [
                ("system", PROMPT_TO_LLM_RUSSIAN),
                ("human", "{input}"),
                ("human", "Контекст:\n{context}"),
            ]
        )

        logger.debug("Building chain for question answering...")
        question_answer_chain: Runnable[dict[str, Any], Any] = create_stuff_documents_chain(
            self._large_learning_model, prompt
        )

        logger.debug("Building retrieval chain for question answering...")
        chain: Runnable[dict[str, Any], Any] = create_retrieval_chain(self._retrieval, question_answer_chain)

        logger.debug("Answering Large Learning Model...")
        answer_from_llm = await chain.ainvoke(
            {
                "input": question.value,
            }
        )

        logger.debug("Got answer from Large Learning Model...")
        raw_answer: str = answer_from_llm.get("answer", "") or answer_from_llm.get("result", "")

        answer: str = raw_answer.replace("Согласно контексту", "Согласно документации").replace(
            "В предоставленном контексте", ""
        )

        if "Информация не найдена" not in answer:
            answer = answer.replace("но я не нашел информации", "")

        message: Message = Message(answer.strip())
        tokens: Tokens = Tokens(self._large_learning_model.get_num_tokens(raw_answer))

        return MessageWithTokenDTO(
            message=message,
            tokens=tokens,
        )
