from rest_framework import permissions


class IsOtpAllowed(permissions.BasePermission):
    message = ''

    def has_permission(self, request, view):
        # if authenticated and not verified
        if request.user.is_authenticated and not request.user.user_profile.verified:
            return True
        if request.user.user_profile.password_reset:
            return True
        self.message = 'User already verified'
        return False


class IsVerified(permissions.BasePermission):
    message = 'User not verified'

    def has_permission(self, request, view):
        try:
            if request.user.user_profile.verified:
                return True
            return False
        except:
            self.message = "Some error occured"
            return False
