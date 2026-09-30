from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .pipeline import compile_script


class CompilerExecuteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        command = request.data.get("command", "")
        execute = request.data.get("execute", True)
        payload = compile_script(command, execute=bool(execute))
        status_code = 200 if payload.get("success") else 400
        return Response(payload, status=status_code)
