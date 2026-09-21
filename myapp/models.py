from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_manager_task'

    def __str__(self):
        return self.title


class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_manager_subtask'

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'task_manager_category'

    def __str__(self):
        return self.name
