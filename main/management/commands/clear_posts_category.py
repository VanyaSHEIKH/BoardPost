from django.core.management.base import BaseCommand

from News.models import PostCategory, Category, Post


class Command(BaseCommand):
    help = 'Удаляет все посты выбранной категории'
    # requires_migrations_checks = True #напоминание о выполнении миграций, если таковые есть
    post_category = ", ".join([cat.category for cat in Category.objects.all()])  # Собираем кверисет всех категорий

    def handle(self, *args, **options):
        # self.stdout.readable()#не понятно что делает, скопировал из урока
        self.stdout.write(
            f'Введите имя категории, в которой удалить все посты: {self.post_category}')  # Выводит это сообщение и добавляет все категории
        category = input()  # вводим категорию
        try:
            category = Category.objects.get(category=category)  # находим все записи с этой категорией
            self.stdout.write('Действительно хотите удалить ввсе посты? yes/no')
            answer = input()  # считываем подтверждение
            if answer != 'yes':
                self.stdout.write(self.style.ERROR('Отменено'))
                return
            else:
                Post.objects.filter(category__category=category).delete()
                self.stdout.write(self.style.SUCCESS(f'Успешно удалены все публикации из категории {category}'))
        except PostCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Не существует категории {category}'))

