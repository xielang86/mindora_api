from abc import ABC, abstractmethod
from typing import Dict, Any

class Document(ABC):
    @abstractmethod
    def get_mapping(self) -> Dict[str, Any]:
        raise NotImplementedError
