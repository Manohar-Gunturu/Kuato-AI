from abc import ABC, abstractmethod

class Resource(ABC):
    @abstractmethod
    def download(self, path: str) -> tuple[str, str]:
        """
        Download content from a resource.
        
        Args:
            path (str): Path to the resource (file path or URL)
        
        Returns:
            tuple[str, str]: Tuple where first element is the location and second is the content
        """
        pass