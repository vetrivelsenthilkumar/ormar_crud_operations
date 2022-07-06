import typing

from fastapi import FastAPI, BackgroundTasks


class BackgroundTask(BackgroundTasks):
    def __init__(self, tasks: typing.Sequence[BackgroundTasks] = []):
        self.tasks = list(tasks)

    def add_task(self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any) -> None:
        task = BackgroundTasks(func, *args, **kwargs)
        self.tasks.append(task)

    async def __call__(self) -> None:
        for task in self.tasks:
            await task()
