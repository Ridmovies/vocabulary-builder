from app.crud.base import CRUDBase
from app.models.word import Word
from app.schemas.words import WordCreate, WordUpdate


class CRUDWord(CRUDBase[Word, WordCreate, WordUpdate]):
    """
    CRUD операции для модели Word.
    Наследуемся от базового класса и добавляем специфичные методы.
    """


word_crud = CRUDWord(Word)