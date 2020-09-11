from django.db import models

class Book(models.Model):
    name = models.CharField(
        max_length=40
    )
    icon = models.ImageField(
        upload_to="icons"  # 指定文件保存的路径名 系统自动创建
    )