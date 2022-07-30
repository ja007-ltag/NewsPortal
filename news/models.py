from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    # Связь «один к одному» с встроенной моделью пользователей User;
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=0)  # рейтинг пользователя

    # Суммарный рейтинг каждой статьи автора умножается на 3; (post_rating)
    # суммарный рейтинг всех комментариев автора; (comment_rating)
    # суммарный рейтинг всех комментариев к статьям автора, ИСКЛЮЧАЯ комментарии самого автора. (comment_post_rating)
    def update_rating(self):
        def check_none(var):
            return var if var is not None else 0

        post_rating = self.post_set.aggregate(sum_post=Sum('rating'))
        post_rating = check_none(post_rating.get('sum_post'))

        comment_rating = self.authorUser.comment_set.aggregate(sum_comment=Sum('rating'))
        comment_rating = check_none(comment_rating.get('sum_comment'))

        comment_post_rating = Comment.objects.filter(commentPost__postAuthor=self).\
            exclude(commentUser=self.authorUser).aggregate(sum_comment_post=Sum('rating'))
        comment_post_rating = check_none(comment_post_rating.get('sum_comment_post'))

        self.rating = post_rating * 3 + comment_rating + comment_post_rating
        self.save()

    def __str__(self):
        return f"{self.authorUser}"


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    CHOICES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    postAuthor = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=CHOICES, default=NEWS)  # поле с выбором «статья» или «новость»
    date = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:124]}...'

    def __str__(self):
        return f'{self.title}'


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
