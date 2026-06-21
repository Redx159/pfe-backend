-- ============================================================
-- SEED DATA FOR HR MANAGEMENT SYSTEM
-- ============================================================
-- Usage: sqlite3 db.sqlite3 < seed.sql
-- Then run: python manage.py seed_passwords
-- (or manually: python manage.py changepassword <user> for each)
-- ============================================================

-- 1. DEPARTMENTS
INSERT INTO employees_department (id, name, description) VALUES
(1, 'Informatique', 'Departement developpement et infrastructure IT'),
(2, 'Ressources Humaines', 'Gestion du personnel et administration'),
(3, 'Finance', 'Comptabilite et gestion financiere'),
(4, 'Marketing', 'Communication et marketing'),
(5, 'Commercial', 'Ventes et relation client');

-- 2. EMPLOYEES (single table employees_employee extends AbstractUser)
-- NOTE: passwords below are PLACEHOLDERS. Reset ALL of them after import:
--   python manage.py shell -c "
--     from django.contrib.auth import get_user_model
--     User = get_user_model()
--     for u in User.objects.all():
--         u.set_password('test123')
--         u.save()
--   "
INSERT INTO employees_employee (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, employee_id, position, hire_date, phone_number, photo_url, cp_balance, rtt_balance, role, department_id, manager_id) VALUES

-- admin (ADMIN role)
(1, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 1, 'admin', 'Admin', 'Principal', 'admin@company.ma', 1, 1, '2026-01-01 09:00:00', 'EMP-001', 'Administrateur RH', '2024-01-01', '0600000001', '', 25, 10, 'ADMIN', 2, NULL),

-- managers
(2, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'manager1', 'Karim', 'Benali', 'karim.benali@company.ma', 0, 1, '2024-02-01 09:00:00', 'EMP-002', 'Chef de projet IT', '2023-06-01', '0600000002', '', 22, 8, 'MANAGER', 1, NULL),
(3, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'manager2', 'Sara', 'El Amrani', 'sara.amrani@company.ma', 0, 1, '2024-02-15 09:00:00', 'EMP-003', 'Responsable Marketing', '2023-09-01', '0600000003', '', 20, 7, 'MANAGER', 4, NULL),
(4, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'manager3', 'Youssef', 'Idrissi', 'youssef.idrissi@company.ma', 0, 1, '2024-03-01 09:00:00', 'EMP-004', 'Chef Comptable', '2022-11-01', '0600000004', '', 18, 6, 'MANAGER', 3, NULL),

-- employees
(5, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'employee1', 'Ahmed', 'Alaoui', 'ahmed.alaoui@company.ma', 0, 1, '2024-04-01 09:00:00', 'EMP-005', 'Developpeur Full Stack', '2024-04-01', '0600000005', '', 25, 10, 'EMPLOYEE', 1, 2),
(6, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'employee2', 'Fatima', 'Zahra', 'fatima.zahra@company.ma', 0, 1, '2024-05-01 09:00:00', 'EMP-006', 'Developpeur Mobile', '2024-05-01', '0600000006', '', 24, 9, 'EMPLOYEE', 1, 2),
(7, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'employee3', 'Hassan', 'Moujtahid', 'hassan.moujtahid@company.ma', 0, 1, '2024-06-01 09:00:00', 'EMP-007', 'Data Analyst', '2024-06-01', '0600000007', '', 23, 8, 'EMPLOYEE', 1, 2),
(8, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'employee4', 'Nadia', 'Bennani', 'nadia.bennani@company.ma', 0, 1, '2024-07-01 09:00:00', 'EMP-008', 'Community Manager', '2024-07-01', '0600000008', '', 22, 7, 'EMPLOYEE', 4, 3),
(9, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'employee5', 'Omar', 'Tazi', 'omar.tazi@company.ma', 0, 1, '2024-08-01 09:00:00', 'EMP-009', 'Comptable', '2024-08-01', '0600000009', '', 21, 6, 'EMPLOYEE', 3, 4),
(10, 'pbkdf2_sha256$720000$dummy$dummyhash-CHANGE-ME', NULL, 0, 'employee6', 'Leila', 'Chraibi', 'leila.chraibi@company.ma', 0, 1, '2024-09-01 09:00:00', 'EMP-010', 'Commercial', '2024-09-01', '0600000010', '', 20, 5, 'EMPLOYEE', 5, NULL);

-- 3. LEAVE REQUESTS
INSERT INTO leaves_leaverequest (id, employee_id, start_date, end_date, leave_type, status, reason, manager_comment, attachment, created_at, updated_at) VALUES
(1, 5, '2026-06-01', '2026-06-05', 'CP', 'APPROVED', 'Vacances en famille', 'Approuve', '', '2026-05-15 10:00:00', '2026-05-16 14:00:00'),
(2, 6, '2026-06-10', '2026-06-10', 'SICK', 'APPROVED', 'Rendez-vous medical', 'Bon retablissement', '', '2026-06-08 09:00:00', '2026-06-08 11:00:00'),
(3, 7, '2026-06-20', '2026-06-25', 'CP', 'PENDING', 'Vacances ete', '', '', '2026-06-10 15:00:00', '2026-06-10 15:00:00'),
(4, 8, '2026-05-25', '2026-05-26', 'RTT', 'REJECTED', 'Affaire personnelle', 'Refuse - conflit avec reunion client', '', '2026-05-20 08:00:00', '2026-05-21 10:00:00'),
(5, 9, '2026-07-01', '2026-07-15', 'CP', 'PENDING', 'Vacances annuelles', '', '', '2026-06-12 11:00:00', '2026-06-12 11:00:00'),
(6, 10, '2026-06-15', '2026-06-15', 'SICK', 'APPROVED', 'Maladie', 'Approuve', '', '2026-06-14 07:00:00', '2026-06-14 08:00:00'),
(7, 2, '2026-06-28', '2026-06-30', 'CP', 'PENDING', 'Conges perso', '', '', '2026-06-20 16:00:00', '2026-06-20 16:00:00'),
(8, 5, '2026-07-20', '2026-07-22', 'RTT', 'APPROVED', 'Recuperation', 'Ok', '', '2026-07-10 09:00:00', '2026-07-10 14:00:00'),
(9, 6, '2026-05-10', '2026-05-12', 'CP', 'CANCELLED', 'Annule pour raison pro', '', '', '2026-05-01 10:00:00', '2026-05-05 09:00:00'),
(10, 3, '2026-06-22', '2026-06-26', 'CP', 'PENDING', 'Vacances', '', '', '2026-06-10 12:00:00', '2026-06-10 12:00:00'),
-- Week 22-30 June
(11, 8, '2026-06-24', '2026-06-24', 'RTT', 'APPROVED', 'Demarche administrative', 'Approuve', '', '2026-06-22 09:00:00', '2026-06-22 10:00:00'),
(12, 5, '2026-06-29', '2026-06-30', 'CP', 'APPROVED', 'Fin de mois', 'Accorde', '', '2026-06-25 11:00:00', '2026-06-25 14:00:00'),
(13, 10, '2026-06-22', '2026-06-23', 'CP', 'PENDING', 'Conges perso', '', '', '2026-06-20 16:00:00', '2026-06-20 16:00:00'),
(14, 9, '2026-06-25', '2026-06-25', 'SICK', 'REJECTED', 'Maladie legere', 'Refuse - equipe reduite cette semaine', '', '2026-06-24 08:00:00', '2026-06-24 08:30:00'),
(15, 6, '2026-06-23', '2026-06-23', 'SICK', 'APPROVED', 'Visite medicale', 'OK', '', '2026-06-22 09:00:00', '2026-06-22 10:00:00');

-- 4. MEETINGS
INSERT INTO meetings_meeting (id, title, description, start_time, end_time, is_cancelled, created_at, created_by_id, is_online, location, meeting_url) VALUES
(1, 'Sprint Review', 'Revue du sprint en cours', '2026-06-22 10:00:00', '2026-06-22 11:00:00', 0, '2026-06-18 09:00:00', 2, 1, '', 'https://meet.google.com/abc-defg-hij'),
(2, 'Point hebdo equipe', 'Reunion hebdomadaire equipe IT', '2026-06-23 14:00:00', '2026-06-23 15:00:00', 0, '2026-06-16 10:00:00', 2, 0, 'Salle A-203', ''),
(3, 'Strategie marketing', 'Campagne Q3', '2026-06-24 09:00:00', '2026-06-24 11:00:00', 0, '2026-06-15 08:00:00', 3, 0, 'Salle B-101', ''),
(4, 'Entretien annuel', 'Evaluation annuelle equipe finance', '2026-06-25 15:00:00', '2026-06-25 16:30:00', 0, '2026-06-10 14:00:00', 4, 0, 'Bureau RH', ''),
(5, 'Presentation projet', 'Nouveau projet client', '2026-06-15 11:00:00', '2026-06-15 12:00:00', 0, '2026-06-08 09:00:00', 2, 1, '', 'https://zoom.us/j/123456789'),
(6, 'Formation Django', 'Workshop Django avance', '2026-06-19 09:00:00', '2026-06-19 17:00:00', 0, '2026-06-01 10:00:00', 2, 0, 'Salle formation', ''),
(7, 'Reunion annulee', 'Test annulation', '2026-06-20 10:00:00', '2026-06-20 11:00:00', 1, '2026-06-05 08:00:00', 2, 0, 'Salle C', ''),
(8, 'Brainstorming produit', 'Idees nouvelles fonctionnalites', '2026-06-26 13:00:00', '2026-06-26 14:00:00', 0, '2026-06-20 11:00:00', 5, 0, 'Salle creative', ''),
(9, 'Point direction', 'Reunion mensuelle direction', '2026-06-30 10:00:00', '2026-06-30 12:00:00', 0, '2026-06-01 09:00:00', 1, 0, 'Salle conseil', ''),
(10, 'Retrospective sprint', 'Bilan du sprint et ameliorations', '2026-06-22 11:00:00', '2026-06-22 12:00:00', 0, '2026-06-18 09:30:00', 2, 1, '', 'https://meet.google.com/abc-defg-hij'),
-- Week 22-30 June — additional meetings
(11, 'Daily standup', 'Point quotidien equipe IT', '2026-06-22 09:00:00', '2026-06-22 09:30:00', 0, '2026-06-21 17:00:00', 2, 0, 'Salle A-203', ''),
(12, 'Daily standup', 'Point quotidien equipe IT', '2026-06-23 09:00:00', '2026-06-23 09:30:00', 0, '2026-06-21 17:00:00', 2, 0, 'Salle A-203', ''),
(13, 'Daily standup', 'Point quotidien equipe IT', '2026-06-24 09:00:00', '2026-06-24 09:30:00', 0, '2026-06-21 17:00:00', 2, 0, 'Salle A-203', ''),
(14, 'Daily standup', 'Point quotidien equipe IT', '2026-06-25 09:00:00', '2026-06-25 09:30:00', 0, '2026-06-21 17:00:00', 2, 0, 'Salle A-203', ''),
(15, 'Daily standup', 'Point quotidien equipe IT', '2026-06-26 09:00:00', '2026-06-26 09:30:00', 0, '2026-06-21 17:00:00', 2, 0, 'Salle A-203', ''),
(16, 'Formation Angular', 'Workshop Angular intermediaire', '2026-06-23 10:00:00', '2026-06-23 12:00:00', 0, '2026-06-15 15:00:00', 2, 0, 'Salle formation', ''),
(17, 'Reunion fournisseur', 'Point avec prestataire', '2026-06-24 14:00:00', '2026-06-24 15:00:00', 0, '2026-06-20 08:00:00', 3, 1, '', 'https://teams.microsoft.com/meeting/456'),
(18, 'Atelier SEO', 'Strategie referencement naturel', '2026-06-25 09:00:00', '2026-06-25 11:00:00', 0, '2026-06-15 16:00:00', 3, 0, 'Salle B-101', ''),
(19, 'Point commercial', 'Bilan hebdomadaire ventes', '2026-06-26 10:00:00', '2026-06-26 11:00:00', 0, '2026-06-22 09:00:00', 10, 0, 'Salle reunion RDC', ''),
(20, 'Lancement projet', 'Kickoff nouveau projet client', '2026-06-29 09:00:00', '2026-06-29 10:30:00', 0, '2026-06-22 08:00:00', 2, 0, 'Salle conseil', ''),
(21, 'Reunion RH', 'Point recrutement et paie', '2026-06-29 14:00:00', '2026-06-29 15:00:00', 0, '2026-06-01 09:00:00', 1, 0, 'Bureau RH', ''),
(22, 'Formation Excel avance', 'Workshop tableaux croises', '2026-06-30 14:00:00', '2026-06-30 16:00:00', 0, '2026-06-15 11:00:00', 4, 0, 'Salle formation', '');

-- 5. MEETING PARTICIPANTS
INSERT INTO meetings_meetingparticipant (id, meeting_id, employee_id, status, responded_at, decline_reason) VALUES
(1, 1, 5, 'ACCEPTED', '2026-06-19 10:00:00', ''),
(2, 1, 6, 'ACCEPTED', '2026-06-19 11:00:00', ''),
(3, 1, 7, 'DECLINED', '2026-06-19 08:00:00', 'En conges'),
(4, 2, 5, 'ACCEPTED', '2026-06-17 09:00:00', ''),
(5, 2, 6, 'ACCEPTED', '2026-06-17 09:30:00', ''),
(6, 2, 7, 'INVITED', NULL, ''),
(7, 3, 8, 'ACCEPTED', '2026-06-16 10:00:00', ''),
(8, 3, 3, 'ACCEPTED', '2026-06-16 10:00:00', ''),
(9, 4, 9, 'INVITED', NULL, ''),
(10, 8, 6, 'ACCEPTED', '2026-06-21 09:00:00', ''),
(11, 8, 7, 'ACCEPTED', '2026-06-21 10:00:00', ''),
(12, 8, 5, 'INVITED', NULL, ''),
(13, 9, 2, 'ACCEPTED', '2026-06-02 08:00:00', ''),
(14, 9, 3, 'ACCEPTED', '2026-06-02 08:30:00', ''),
(15, 9, 4, 'ACCEPTED', '2026-06-02 09:00:00', ''),
-- Week 22-30 June participants
(16, 11, 5, 'ACCEPTED', '2026-06-21 17:30:00', ''),
(17, 11, 6, 'ACCEPTED', '2026-06-21 17:30:00', ''),
(18, 11, 7, 'ACCEPTED', '2026-06-21 17:30:00', ''),
(19, 12, 5, 'ACCEPTED', '2026-06-22 08:00:00', ''),
(20, 12, 6, 'INVITED', NULL, ''),
(21, 12, 7, 'ACCEPTED', '2026-06-22 08:00:00', ''),
(22, 13, 5, 'ACCEPTED', '2026-06-23 08:00:00', ''),
(23, 13, 6, 'ACCEPTED', '2026-06-23 08:00:00', ''),
(24, 13, 7, 'ACCEPTED', '2026-06-23 08:00:00', ''),
(25, 14, 5, 'INVITED', NULL, ''),
(26, 14, 6, 'ACCEPTED', '2026-06-24 08:00:00', ''),
(27, 14, 7, 'ACCEPTED', '2026-06-24 08:00:00', ''),
(28, 15, 5, 'ACCEPTED', '2026-06-25 17:00:00', ''),
(29, 15, 6, 'ACCEPTED', '2026-06-25 17:00:00', ''),
(30, 15, 7, 'ACCEPTED', '2026-06-25 17:00:00', ''),
(31, 16, 5, 'ACCEPTED', '2026-06-22 14:00:00', ''),
(32, 16, 6, 'ACCEPTED', '2026-06-22 14:00:00', ''),
(33, 17, 8, 'INVITED', NULL, ''),
(34, 17, 3, 'ACCEPTED', '2026-06-22 09:00:00', ''),
(35, 18, 8, 'ACCEPTED', '2026-06-23 15:00:00', ''),
(36, 18, 3, 'ACCEPTED', '2026-06-23 15:00:00', ''),
(37, 19, 10, 'ACCEPTED', '2026-06-24 09:00:00', ''),
(38, 20, 5, 'INVITED', NULL, ''),
(39, 20, 6, 'INVITED', NULL, ''),
(40, 20, 7, 'INVITED', NULL, ''),
(41, 20, 2, 'ACCEPTED', '2026-06-25 09:00:00', ''),
(42, 21, 1, 'ACCEPTED', '2026-06-22 09:00:00', ''),
(43, 21, 2, 'INVITED', NULL, ''),
(44, 22, 9, 'ACCEPTED', '2026-06-28 10:00:00', ''),
(45, 22, 4, 'ACCEPTED', '2026-06-28 10:00:00', '');

-- 6. ATTENDANCE
INSERT INTO attendance_attendance (id, employee_id, date, check_in, check_out, work_duration, overtime_minutes, location, status, created_at) VALUES
-- Weekend 20-21 June
(1, 5, '2026-06-20', '2026-06-20 08:45:00', '2026-06-20 17:15:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-20 08:45:00'),
(2, 6, '2026-06-20', '2026-06-20 09:05:00', '2026-06-20 18:00:00', '32100', 60, 'Bureau', 'LATE', '2026-06-20 09:05:00'),
(3, 7, '2026-06-20', NULL, NULL, NULL, 0, '', 'ABSENT', '2026-06-20 00:00:00'),
(4, 5, '2026-06-21', '2026-06-21 08:30:00', '2026-06-21 17:00:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-21 08:30:00'),
(5, 6, '2026-06-21', '2026-06-21 08:50:00', '2026-06-21 17:10:00', '30000', 0, 'Bureau', 'ON_TIME', '2026-06-21 08:50:00'),
(6, 7, '2026-06-21', '2026-06-21 09:15:00', '2026-06-21 18:30:00', '33300', 90, 'Bureau', 'LATE', '2026-06-21 09:15:00'),
(7, 8, '2026-06-20', '2026-06-20 08:00:00', '2026-06-20 16:30:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-20 08:00:00'),
(8, 9, '2026-06-20', '2026-06-20 08:55:00', '2026-06-20 17:00:00', '29100', 0, 'Bureau', 'ON_TIME', '2026-06-20 08:55:00'),
(9, 10, '2026-06-20', '2026-06-20 09:30:00', '2026-06-20 17:30:00', '28800', 0, 'Client externe', 'LATE', '2026-06-20 09:30:00'),
-- Mon 22 June
(10, 5, '2026-06-22', '2026-06-22 08:40:00', '2026-06-22 17:00:00', '30000', 0, 'Bureau', 'ON_TIME', '2026-06-22 08:40:00'),
(11, 6, '2026-06-22', '2026-06-22 08:55:00', '2026-06-22 17:15:00', '30800', 0, 'Bureau', 'ON_TIME', '2026-06-22 08:55:00'),
(12, 7, '2026-06-22', '2026-06-22 09:10:00', '2026-06-22 17:30:00', '30000', 0, 'Bureau', 'LATE', '2026-06-22 09:10:00'),
(13, 8, '2026-06-22', '2026-06-22 08:15:00', '2026-06-22 16:45:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-22 08:15:00'),
(14, 9, '2026-06-22', '2026-06-22 08:50:00', '2026-06-22 17:00:00', '29400', 0, 'Bureau', 'ON_TIME', '2026-06-22 08:50:00'),
(15, 10, '2026-06-22', NULL, NULL, NULL, 0, '', 'ABSENT', '2026-06-22 00:00:00'),
-- Tue 23 June
(16, 5, '2026-06-23', '2026-06-23 08:30:00', '2026-06-23 16:30:00', '28800', 0, 'Bureau', 'ON_TIME', '2026-06-23 08:30:00'),
(17, 6, '2026-06-23', NULL, NULL, NULL, 0, '', 'ABSENT', '2026-06-23 00:00:00'),
(18, 7, '2026-06-23', '2026-06-23 08:45:00', '2026-06-23 17:00:00', '29700', 0, 'Bureau', 'ON_TIME', '2026-06-23 08:45:00'),
(19, 8, '2026-06-23', '2026-06-23 08:30:00', '2026-06-23 17:00:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-23 08:30:00'),
(20, 9, '2026-06-23', '2026-06-23 08:55:00', '2026-06-23 17:10:00', '29700', 0, 'Bureau', 'ON_TIME', '2026-06-23 08:55:00'),
(21, 10, '2026-06-23', '2026-06-23 09:00:00', '2026-06-23 17:00:00', '28800', 0, 'Bureau', 'ON_TIME', '2026-06-23 09:00:00'),
-- Wed 24 June
(22, 5, '2026-06-24', '2026-06-24 08:45:00', '2026-06-24 17:15:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-24 08:45:00'),
(23, 6, '2026-06-24', '2026-06-24 09:00:00', '2026-06-24 18:00:00', '32400', 60, 'Bureau', 'ON_TIME', '2026-06-24 09:00:00'),
(24, 7, '2026-06-24', '2026-06-24 08:30:00', '2026-06-24 17:00:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-24 08:30:00'),
(25, 8, '2026-06-24', NULL, NULL, NULL, 0, '', 'ABSENT', '2026-06-24 00:00:00'),
(26, 9, '2026-06-24', '2026-06-24 09:05:00', '2026-06-24 17:00:00', '28500', 0, 'Bureau', 'LATE', '2026-06-24 09:05:00'),
(27, 10, '2026-06-24', '2026-06-24 08:50:00', '2026-06-24 17:10:00', '29600', 0, 'Bureau', 'ON_TIME', '2026-06-24 08:50:00'),
-- Thu 25 June
(28, 5, '2026-06-25', '2026-06-25 08:40:00', '2026-06-25 17:30:00', '31800', 30, 'Bureau', 'ON_TIME', '2026-06-25 08:40:00'),
(29, 6, '2026-06-25', '2026-06-25 08:55:00', '2026-06-25 17:00:00', '29100', 0, 'Bureau', 'ON_TIME', '2026-06-25 08:55:00'),
(30, 7, '2026-06-25', '2026-06-25 09:00:00', '2026-06-25 17:15:00', '29700', 0, 'Bureau', 'ON_TIME', '2026-06-25 09:00:00'),
(31, 8, '2026-06-25', '2026-06-25 08:00:00', '2026-06-25 16:30:00', '30600', 0, 'Bureau', 'ON_TIME', '2026-06-25 08:00:00'),
(32, 10, '2026-06-25', '2026-06-25 09:30:00', '2026-06-25 17:30:00', '28800', 0, 'Client', 'LATE', '2026-06-25 09:30:00'),
-- Fri 26 June
(33, 5, '2026-06-26', '2026-06-26 08:45:00', '2026-06-26 16:45:00', '28800', 0, 'Bureau', 'ON_TIME', '2026-06-26 08:45:00'),
(34, 6, '2026-06-26', '2026-06-26 08:50:00', '2026-06-26 17:00:00', '29400', 0, 'Bureau', 'ON_TIME', '2026-06-26 08:50:00'),
(35, 7, '2026-06-26', '2026-06-26 09:15:00', '2026-06-26 17:30:00', '29700', 0, 'Bureau', 'LATE', '2026-06-26 09:15:00'),
(36, 8, '2026-06-26', '2026-06-26 08:10:00', '2026-06-26 16:00:00', '28200', 0, 'Bureau', 'ON_TIME', '2026-06-26 08:10:00'),
(37, 9, '2026-06-26', '2026-06-26 08:50:00', '2026-06-26 17:00:00', '29400', 0, 'Bureau', 'ON_TIME', '2026-06-26 08:50:00'),
(38, 10, '2026-06-26', '2026-06-26 09:00:00', '2026-06-26 17:00:00', '28800', 0, 'Bureau', 'ON_TIME', '2026-06-26 09:00:00');

-- 7. NOTIFICATIONS
INSERT INTO notifications_notification (id, recipient_id, title, body, type, is_read, related_link, created_at) VALUES
(1, 5, 'Conges approuves', 'Votre demande de conges du 01/06 au 05/06 a ete approuvee', 'LEAVE_APPROVED', 1, '/leaves/1', '2026-05-16 14:00:00'),
(2, 6, 'Conges approuves', 'Votre conge maladie du 10/06 a ete approuve', 'LEAVE_APPROVED', 1, '/leaves/2', '2026-06-08 11:00:00'),
(3, 8, 'Conges refuses', 'Votre demande RTT du 25/05 au 26/05 a ete refusee', 'LEAVE_REJECTED', 0, '/leaves/4', '2026-05-21 10:00:00'),
(4, 5, 'Invitation reunion', 'Vous etes invite a Sprint Review le 22/06 a 10h00', 'MEETING_INVITE', 1, '/meetings/1', '2026-06-18 09:00:00'),
(5, 6, 'Invitation reunion', 'Vous etes invite a Sprint Review le 22/06 a 10h00', 'MEETING_INVITE', 0, '/meetings/1', '2026-06-18 09:00:00'),
(6, 5, 'Invitation reunion', 'Point hebdo equipe le 23/06 a 14h00', 'MEETING_INVITE', 1, '/meetings/2', '2026-06-16 10:00:00'),
(7, 6, 'Invitation reunion', 'Point hebdo equipe le 23/06 a 14h00', 'MEETING_INVITE', 0, '/meetings/2', '2026-06-16 10:00:00'),
(8, 10, 'Conges approuves', 'Votre conge maladie du 15/06 a ete approuve', 'LEAVE_APPROVED', 0, '/leaves/6', '2026-06-14 08:00:00'),
(9, 5, 'Invitation brainstorming', 'Brainstorming produit le 26/06 a 13h00', 'MEETING_INVITE', 1, '/meetings/8', '2026-06-20 11:00:00'),
(10, 6, 'Reunion annulee', 'La reunion Test annulation a ete annulee', 'MEETING_CANCELLED', 0, '/meetings/7', '2026-06-05 08:00:00'),
-- Week 22-30 June
(11, 8, 'RTT approuve', 'Votre jour RTT du 24/06 a ete approuve', 'LEAVE_APPROVED', 1, '/leaves/11', '2026-06-22 10:00:00'),
(12, 5, 'Conges approuves', 'Vos conges des 29-30/06 ont ete approuves', 'LEAVE_APPROVED', 1, '/leaves/12', '2026-06-25 14:00:00'),
(13, 6, 'Invitation reunion', 'Formation Angular le 23/06 a 10h00', 'MEETING_INVITE', 1, '/meetings/16', '2026-06-22 14:00:00'),
(14, 5, 'Invitation reunion', 'Daily standup 22/06 a 09h00', 'MEETING_INVITE', 1, '/meetings/11', '2026-06-21 17:30:00'),
(15, 7, 'Invitation reunion', 'Daily standup 22/06 a 09h00', 'MEETING_INVITE', 1, '/meetings/11', '2026-06-21 17:30:00'),
(16, 6, 'Invitation reunion', 'Daily standup 22/06 a 09h00', 'MEETING_INVITE', 1, '/meetings/11', '2026-06-21 17:30:00'),
(17, 5, 'Rappel', 'Sprint Review demain a 10h00', 'MEETING_INVITE', 0, '/meetings/1', '2026-06-21 18:00:00'),
(18, 10, 'Rappel', 'Point commercial vendredi 26/06 a 10h00', 'MEETING_INVITE', 0, '/meetings/19', '2026-06-24 09:00:00'),
(19, 5, 'Invitation reunion', 'Kickoff projet lundi 29/06 a 09h00', 'MEETING_INVITE', 0, '/meetings/20', '2026-06-25 09:00:00'),
(20, 9, 'Conge refuse', 'Votre conge maladie du 25/06 a ete refuse', 'LEAVE_REJECTED', 0, '/leaves/14', '2026-06-24 08:30:00');

-- 8. NOTIFICATION PREFERENCES
INSERT INTO notifications_notificationpreference (id, employee_id, meeting_invites, leave_status, reminders, vacation_mode, vacation_until) VALUES
(1, 1, 1, 1, 1, 0, NULL),
(2, 2, 1, 1, 1, 0, NULL),
(3, 3, 1, 1, 0, 0, NULL),
(4, 4, 1, 1, 1, 0, NULL),
(5, 5, 1, 1, 1, 0, NULL),
(6, 6, 1, 1, 1, 0, NULL),
(7, 7, 1, 1, 0, 0, NULL),
(8, 8, 1, 1, 1, 0, NULL),
(9, 9, 1, 1, 1, 0, NULL),
(10, 10, 0, 1, 1, 0, NULL);

-- 9. ASSISTANT CONVERSATIONS
INSERT INTO assistantbot_assistantconversation (id, user_id, title, created_at, updated_at) VALUES
(1, 5, 'HR Assistant', '2026-06-20 09:00:00', '2026-06-20 09:05:00'),
(2, 6, 'HR Assistant', '2026-06-21 14:00:00', '2026-06-21 14:03:00');

INSERT INTO assistantbot_assistantmessage (id, conversation_id, role, content, metadata, created_at) VALUES
(1, 1, 'user', 'Combien de conges il me reste ?', '{}', '2026-06-20 09:00:00'),
(2, 1, 'assistant', 'Il vous reste 25 jours de conges payes et 10 jours de RTT.', '{}', '2026-06-20 09:00:01'),
(3, 1, 'user', 'Comment faire une demande de conges ?', '{}', '2026-06-20 09:02:00'),
(4, 1, 'assistant', 'Allez dans longlet Conges, cliquez sur +, remplissez le formulaire et soumettez.', '{}', '2026-06-20 09:02:01'),
(5, 1, 'user', 'Merci', '{}', '2026-06-20 09:05:00'),
(6, 2, 'user', 'Quelles sont mes reunions aujourd hui ?', '{}', '2026-06-21 14:00:00'),
(7, 2, 'assistant', 'Vous avez une reunion : Sprint Review a 10h00.', '{}', '2026-06-21 14:00:02'),
(8, 2, 'user', 'Je peux la reporter ?', '{}', '2026-06-21 14:03:00'),
(9, 2, 'assistant', 'Contactez votre manager pour modifier la reunion.', '{}', '2026-06-21 14:03:01');

-- ============================================================
-- AFTER IMPORT: reset passwords for all users
-- ============================================================
-- python manage.py shell -c "
-- from django.contrib.auth import get_user_model
-- U = get_user_model()
-- for u in U.objects.all():
--     u.set_password('test123')
--     u.save()
-- print('All passwords set to test123')
-- "
