import { createContext, useContext, useEffect, useMemo, useState } from "react";

const STORAGE_THEME_KEY = "admin_theme";
const STORAGE_LANGUAGE_KEY = "admin_language";

const translations = {
  en: {
    nav: {
      dashboard: "Dashboard",
      employees: "Employees",
      leaves: "Leaves",
      attendance: "Attendance",
      meetings: "Meetings",
      analytics: "Analytics",
      teamLeaveCalendar: "Leave Calendar",
      meetingsCalendar: "Meetings Calendar",
      language: "Language",
      theme: "Theme",
      light: "Light",
      dark: "Dark",
      auto: "Auto",
    },
    analytics: {
      title: "Analytics Dashboard",
      subtitle: "Presence statistics, trends, and PDF report export.",
      totalEmployees: "Total Employees",
      attendanceRate: "Attendance Rate",
      presentToday: "Present Today",
      lateToday: "Late Today",
      absentToday: "Absent Today",
      onLeaveToday: "On Leave Today",
      pendingLeaves: "Pending Leaves",
      monthlyTrend: "Monthly Attendance Trend",
      todayPresence: "Today's Presence",
      leaveByType: "Leave by Type",
      departmentStats: "Department Stats",
      exportPdf: "Export PDF Report",
    },
    teamLeaveCalendar: {
      title: "Team Leave Calendar",
      subtitle: "Overview of who is on leave and when.",
    },
    meetingsCalendar: {
      title: "Meetings Calendar",
      subtitle: "All non-cancelled meetings organized by date.",
    },
    login: {
      title: "Admin Login",
      username: "Username",
      password: "Password",
      submit: "Login",
      invalid: "Invalid credentials",
      subtitle: "Sign in to review workforce activity and approvals.",
    },
    common: {
      loading: "Loading...",
      unavailable: "Data is unavailable.",
      active: "Active",
      cancelled: "Cancelled",
      pending: "Pending",
      approved: "Approved",
      rejected: "Rejected",
      absent: "Absent",
      onTime: "On Time",
      late: "Late",
      noData: "No data available.",
      save: "Save",
      cancel: "Cancel",
      edit: "Edit",
      delete: "Delete",
      approve: "Approve",
      reject: "Reject",
      searchEmployee: "Search employee...",
      noDescription: "No description provided.",
      exportCsv: "Export CSV",
    },
    dashboard: {
      title: "Dashboard",
      companyScope: "Viewing company-wide activity.",
      teamScope: "Viewing team activity.",
      employees: "Employees",
      activeAccounts: "Active Accounts",
      pendingLeaves: "Pending Leaves",
      approvedLeaves: "Approved Leaves",
      meetings: "Meetings",
      presentToday: "Present Today",
      lateToday: "Late Today",
      absentToday: "Absent Today",
      attendanceTrend: "Attendance Trend",
      departmentSplit: "Department Split",
      pendingLeaveRequests: "Pending Leave Requests",
      upcomingMeetings: "Upcoming Meetings",
      upcomingLeaveCalendar: "Upcoming Leave Calendar",
      recentAttendance: "Recent Attendance",
      createdBy: "Created by",
      noPendingLeaves: "No pending leave requests.",
      noUpcomingMeetings: "No upcoming meetings.",
      noUpcomingLeaves: "No upcoming leave items.",
      noRecentAttendance: "No recent attendance records.",
      exportMonthly: "Export monthly report",
    },
    employees: {
      title: "Employees",
      totalEmployees: "Total employees",
      pendingApprovals: "Pending approvals",
      name: "Name",
      position: "Position",
      role: "Role",
      department: "Department",
      manager: "Manager",
      status: "Status",
      editEmployee: "Edit Employee",
      noManager: "---",
    },
    leaves: {
      title: "Leave Requests",
      upcomingCalendar: "Upcoming Team Leave Calendar",
      noUpcomingLeaves: "No upcoming leave requests.",
      all: "All",
      employee: "Employee",
      type: "Type",
      dates: "Dates",
      reason: "Reason",
      attachment: "Attachment",
      viewAttachment: "View",
      status: "Status",
      managerComment: "Manager Comment",
      actions: "Actions",
      managerCommentRequired: "Manager comment required",
      approveFailed: "Approve failed",
      rejectFailed: "Reject failed",
      export: "Export leave report",
    },
    attendance: {
      title: "Attendance",
      employee: "Employee",
      date: "Date",
      checkIn: "Check-in",
      status: "Status",
      checkOut: "Check-out",
      duration: "Duration",
      export: "Export attendance report",
    },
    meetings: {
      title: "Meetings",
      subtitle:
        "Meetings are created from the mobile app. This screen is for reviewing meeting activity.",
      starts: "Starts",
      ends: "Ends",
      mode: "Mode",
      online: "Online",
      inPerson: "In person",
      upcoming: "Upcoming",
      ended: "Ended",
      createdBy: "Created by",
      participants: "Participants",
      noParticipants: "No invited participants yet.",
      filterAll: "All",
      filterUpcoming: "Upcoming",
      filterActive: "Active",
      filterEnded: "Ended",
      filterCancelled: "Cancelled",
    },
  },
  fr: {
    nav: {
      dashboard: "Tableau de bord",
      employees: "Employés",
      leaves: "Congés",
      attendance: "Présence",
      meetings: "Réunions",
      analytics: "Analytique",
      teamLeaveCalendar: "Calendrier Congés",
      meetingsCalendar: "Calendrier Réunions",
      language: "Langue",
      theme: "Thème",
      light: "Clair",
      dark: "Sombre",
      auto: "Auto",
    },
    analytics: {
      title: "Tableau de bord analytique",
      subtitle: "Statistiques de présence, tendances et export PDF.",
      totalEmployees: "Total Employés",
      attendanceRate: "Taux de présence",
      presentToday: "Présents aujourd'hui",
      lateToday: "Retards aujourd'hui",
      absentToday: "Absents aujourd'hui",
      onLeaveToday: "En congé aujourd'hui",
      pendingLeaves: "Congés en attente",
      monthlyTrend: "Tendance mensuelle",
      todayPresence: "Présence du jour",
      leaveByType: "Congés par type",
      departmentStats: "Statistiques par département",
      exportPdf: "Exporter le rapport PDF",
    },
    teamLeaveCalendar: {
      title: "Calendrier des congés",
      subtitle: "Aperçu de qui est en congé et quand.",
    },
    meetingsCalendar: {
      title: "Calendrier des réunions",
      subtitle: "Toutes les réunions non annulées par date.",
    },
    login: {
      title: "Connexion Admin",
      username: "Nom d'utilisateur",
      password: "Mot de passe",
      submit: "Se connecter",
      invalid: "Identifiants invalides",
      subtitle: "Connectez-vous pour suivre l'activité, la présence et les validations.",
    },
    common: {
      loading: "Chargement...",
      unavailable: "Les données ne sont pas disponibles.",
      active: "Actif",
      cancelled: "Annulé",
      pending: "En attente",
      approved: "Approuvé",
      rejected: "Refusé",
      absent: "Absent",
      onTime: "À l'heure",
      late: "En retard",
      noData: "Aucune donnée disponible.",
      save: "Enregistrer",
      cancel: "Annuler",
      edit: "Modifier",
      delete: "Supprimer",
      approve: "Approuver",
      reject: "Refuser",
      searchEmployee: "Rechercher un employé...",
      noDescription: "Aucune description fournie.",
      exportCsv: "Exporter CSV",
    },
    dashboard: {
      title: "Tableau de bord",
      companyScope: "Vue globale de l'activité de l'entreprise.",
      teamScope: "Vue de l'activité de votre équipe.",
      employees: "Employés",
      activeAccounts: "Comptes actifs",
      pendingLeaves: "Congés en attente",
      approvedLeaves: "Congés approuvés",
      meetings: "Réunions",
      presentToday: "Présents aujourd'hui",
      lateToday: "Retards aujourd'hui",
      absentToday: "Absents aujourd'hui",
      attendanceTrend: "Tendance de présence",
      departmentSplit: "Répartition par département",
      pendingLeaveRequests: "Demandes de congé en attente",
      upcomingMeetings: "Réunions à venir",
      upcomingLeaveCalendar: "Calendrier des congés à venir",
      recentAttendance: "Présence récente",
      createdBy: "Créé par",
      noPendingLeaves: "Aucune demande de congé en attente.",
      noUpcomingMeetings: "Aucune réunion à venir.",
      noUpcomingLeaves: "Aucun congé à venir.",
      noRecentAttendance: "Aucun pointage récent.",
      exportMonthly: "Exporter le rapport mensuel",
    },
    employees: {
      title: "Employés",
      totalEmployees: "Nombre d'employés",
      pendingApprovals: "Approbations en attente",
      name: "Nom",
      position: "Poste",
      role: "Rôle",
      department: "Département",
      manager: "Manager",
      status: "Statut",
      editEmployee: "Modifier l'employé",
      noManager: "---",
    },
    leaves: {
      title: "Demandes de congé",
      upcomingCalendar: "Calendrier des congés à venir",
      noUpcomingLeaves: "Aucune demande de congé à venir.",
      all: "Tous",
      employee: "Employé",
      type: "Type",
      dates: "Dates",
      reason: "Raison",
      attachment: "Pièce jointe",
      viewAttachment: "Voir",
      status: "Statut",
      managerComment: "Commentaire du manager",
      actions: "Actions",
      managerCommentRequired: "Le commentaire du manager est obligatoire",
      approveFailed: "Échec de l'approbation",
      rejectFailed: "Échec du refus",
      export: "Exporter le rapport de congés",
    },
    attendance: {
      title: "Présence",
      employee: "Employé",
      date: "Date",
      checkIn: "Entrée",
      status: "Statut",
      checkOut: "Sortie",
      duration: "Durée",
      export: "Exporter le rapport de présence",
    },
    meetings: {
      title: "Réunions",
      subtitle:
        "Les réunions sont créées depuis l'application mobile. Cet écran sert à consulter l'activité.",
      starts: "Début",
      ends: "Fin",
      mode: "Mode",
      online: "En ligne",
      inPerson: "Présentiel",
      upcoming: "À venir",
      ended: "Terminée",
      createdBy: "Créé par",
      participants: "Participants",
      noParticipants: "Aucun participant invité pour le moment.",
      filterAll: "Toutes",
      filterUpcoming: "À venir",
      filterActive: "Actives",
      filterEnded: "Terminées",
      filterCancelled: "Annulées",
    },
  },
};

const AppShellContext = createContext(null);

function getInitialThemePreference() {
  return localStorage.getItem(STORAGE_THEME_KEY) || "auto";
}

function getInitialLanguage() {
  return localStorage.getItem(STORAGE_LANGUAGE_KEY) || "en";
}

function resolveTheme(themePreference) {
  if (themePreference !== "auto") return themePreference;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function lookup(dictionary, key) {
  return key.split(".").reduce((value, segment) => value?.[segment], dictionary);
}

export function AppShellProvider({ children }) {
  const [themePreference, setThemePreference] = useState(getInitialThemePreference);
  const [language, setLanguage] = useState(getInitialLanguage);
  const [resolvedTheme, setResolvedTheme] = useState(() => resolveTheme(getInitialThemePreference()));

  useEffect(() => {
    localStorage.setItem(STORAGE_THEME_KEY, themePreference);

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const applyTheme = () => setResolvedTheme(resolveTheme(themePreference));

    applyTheme();

    if (themePreference === "auto") {
      media.addEventListener("change", applyTheme);
      return () => media.removeEventListener("change", applyTheme);
    }
  }, [themePreference]);

  useEffect(() => {
    localStorage.setItem(STORAGE_LANGUAGE_KEY, language);
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme;
  }, [resolvedTheme]);

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      themePreference,
      setThemePreference,
      resolvedTheme,
      t: (key) => lookup(translations[language], key) ?? lookup(translations.en, key) ?? key,
    }),
    [language, themePreference, resolvedTheme]
  );

  return (
    <AppShellContext.Provider value={value}>
      {children}
    </AppShellContext.Provider>
  );
}

export function useAppShell() {
  const context = useContext(AppShellContext);

  if (!context) {
    throw new Error("useAppShell must be used inside AppShellProvider");
  }

  return context;
}
