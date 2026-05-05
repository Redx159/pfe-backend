import api from "./axios";

export const generateCheckInQR = () =>
  api.post("attendance/qr/checkin/generate/");

export const generateCheckOutQR = () =>
  api.post("attendance/qr/checkout/generate/");

export const scanQR = (token) =>
  api.post("attendance/scan/", { token });

export const fetchAllAttendance = () =>
  api.get("attendance/all/");

export const fetchMyAttendance = () =>
  api.get("attendance/my/");
