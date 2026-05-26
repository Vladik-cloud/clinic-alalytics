INSERT INTO doctors (full_name, specialty) VALUES
    ('Иванов А.С.', 'Терапия'),
    ('Петрова М.В.', 'Хирургия'),
    ('Сидоров К.Л.', 'Ортодонтия'),
    ('Козлова Е.П.', 'Гигиена'),
    ('Новиков Д.И.', 'Имплантология');

INSERT INTO patients (full_name) VALUES
    ('Пациент 01'), ('Пациент 02'), ('Пациент 03'), ('Пациент 04'),
    ('Пациент 05'), ('Пациент 06'), ('Пациент 07'), ('Пациент 08'),
    ('Пациент 09'), ('Пациент 10'), ('Пациент 11'), ('Пациент 12');

INSERT INTO visits (patient_id, doctor_id, visit_at, status) VALUES
    (1, 1, '2025-01-10 10:00+00', 'completed'),
    (1, 2, '2025-02-05 11:00+00', 'completed'),
    (2, 1, '2025-01-12 09:00+00', 'completed'),
    (2, 3, '2025-03-01 14:00+00', 'completed'),
    (3, 2, '2025-01-15 12:00+00', 'completed'),
    (3, 5, '2025-04-10 10:00+00', 'completed'),
    (4, 1, '2025-02-01 10:00+00', 'completed'),
    (5, 4, '2025-02-10 09:30+00', 'completed'),
    (5, 1, '2025-03-15 11:00+00', 'completed'),
    (6, 3, '2025-01-20 15:00+00', 'completed'),
    (7, 1, '2025-03-05 10:00+00', 'completed'),
    (8, 2, '2025-03-12 13:00+00', 'completed'),
    (8, 4, '2025-05-01 09:00+00', 'completed'),
    (9, 5, '2025-04-01 10:00+00', 'completed'),
    (10, 1, '2025-04-15 11:30+00', 'completed'),
    (11, 2, '2025-05-10 12:00+00', 'completed'),
    (12, 1, '2025-05-20 10:00+00', 'completed');

INSERT INTO services (visit_id, doctor_id, name, amount, provided_at)
SELECT v.id, v.doctor_id,
       CASE (v.id % 3) WHEN 0 THEN 'Консультация' WHEN 1 THEN 'Лечение' ELSE 'Профгигиена' END,
       (800 + (v.id * 137) % 4200)::numeric(12,2),
       v.visit_at
FROM visits v
WHERE v.status = 'completed';
