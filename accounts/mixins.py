from django.contrib.auth.mixins import UserPassesTestMixin

class OnlyYouMixin(UserPassesTestMixin):
    """
    リクエストされたオブジェクトの所有者、またはURLで指定されたユーザーIDが
    ログイン中のユーザー自身であることを検証するMixin
    """
    raise_exception = True

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False

        user_pk = self.kwargs.get('pk')
        if user_pk is not None and str(user_pk) == str(user.pk):
            return True

        if hasattr(self, 'get_object'):
            try:
                obj = self.get_object()
                if obj == user:
                    return True
                if hasattr(obj, 'user') and obj.user == user:
                    return True
            except Exception:
                pass

        return False
