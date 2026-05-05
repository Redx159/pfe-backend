import axios from "axios";

const BASE = "http://192.168.11.112:8000/api/attendance/";

const auth = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access")}`,
  },
});

export const generateCheckInQR = () =>
  axios.post(BASE + "qr/checkin/generate/", {}, auth());

export const generateCheckOutQR = () =>
  axios.post(BASE + "qr/checkout/generate/", {}, auth());

export const scanQR = (token) =>
  axios.post(BASE + "scan/", { token }, auth());

export const myAttendance = () =>
  axios.get(BASE + "all/", auth());
