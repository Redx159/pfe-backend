from django.urls import path

from .views import (
    GenerateCheckInQR,
    GenerateCheckOutQR,
    ScanQRView,
    MyAttendance,
    AllAttendance,
    ExportAttendanceCSV,
)

urlpatterns = [
    path("qr/checkin/generate/", GenerateCheckInQR.as_view()),
    path("qr/checkout/generate/", GenerateCheckOutQR.as_view()),
    path("scan/", ScanQRView.as_view()),

    path("my/", MyAttendance.as_view()),
    path("all/", AllAttendance.as_view()),
    path("export/", ExportAttendanceCSV.as_view()),
]
