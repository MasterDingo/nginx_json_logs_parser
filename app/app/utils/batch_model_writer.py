from typing import Generic, TypeVar

from django.db.models import Model as DjangoModel


SomeModel = TypeVar("SomeModel", bound=DjangoModel)


class BatchModelWriter(Generic[SomeModel]):
    """Collects models to store them into DB in one bulk operation.

    Args:
        model_class (type(Model)): The model class reference.
        batch_size (int): A size of one batch.
    """

    def __init__(self, model_class: type[SomeModel], batch_size: int) -> None:
        self.__model_class = model_class
        self.__batch_size = batch_size
        self.__batch_number = 0
        self.__total_models = 0
        self.__incomplete_batches: dict[int, int] = {}
        self.__new_batch()

    def __new_batch(self) -> None:
        """Initialize a new batch"""
        self.__records: list[SomeModel] = []
        self.__batch_items_count = 0
        self.__batch_number += 1

    @property
    def current_batch_number(self) -> int:
        """int: Returns a number of a current batch."""
        return self.__batch_number

    def add(self, record: SomeModel) -> int:
        """Adds a new model instance to a current batch.
        If the batch size exceeds it automatically flushes to DB and the new batch starts.

        Args:
            record (Model): model instance

        Returns:
            Stored records count if the batch flushes or 0 otherwise.
        """
        self.__records.append(record)
        self.__batch_items_count += 1
        self.__total_models += 1

        if self.__batch_items_count >= self.__batch_size:
            return self.flush()
        return 0

    def flush(self) -> int:
        """Store a rest of model instances into DB.

        Returns:
            A number of stored records.
        """
        records_count = self.__batch_items_count
        if records_count > 0:
            self.__model_class.objects.bulk_create(self.__records)  # type: ignore
            if records_count < self.__batch_size:
                self.__incomplete_batches[self.current_batch_number] = records_count
            self.__new_batch()
        # Return how many records were stored into DB
        return records_count

    @property
    def stats(self):
        """Returns a number of a current batch."""
        return {
            "total": self.__total_models,
            "incomplete_batches": self.__incomplete_batches.copy(),
        }
