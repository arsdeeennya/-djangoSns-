from rest_framework import permissions

# ログインしている自身であればprofileの更新や削除ができる
class ProfilePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.userPro.id == request.user.id